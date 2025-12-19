#!/usr/bin/env python


import os

import numpy
import pytest

import diffpy.morph.morphpy as morphpy
from diffpy.morph.morphapp import create_option_parser, single_morph
from diffpy.morph.morphs.morphstretch import MorphStretch
from tests.helper import create_morph_data_file

# useful variables
thisfile = locals().get("__file__", "file.py")
tests_dir = os.path.dirname(os.path.abspath(thisfile))
# testdata_dir = os.path.join(tests_dir, 'testdata')


class TestMorphStretch:
    @pytest.fixture
    def setup(self):
        self.x_morph = numpy.arange(0.01, 5, 0.01)
        # A step function between 2 and 3
        self.y_morph = heaviside(self.x_morph, 1, 2)
        self.x_target = self.x_morph.copy()
        self.y_target = self.x_target.copy()
        return

    def test_morph(self, setup):
        """Check MorphStretch.morph()"""
        morph = MorphStretch()

        # Stretch by 50%
        morph.stretch = 0.5
        x_morph, y_morph, x_target, y_target = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        # Target should be unchanged
        assert numpy.allclose(self.y_target, y_target)

        # Compare to new function. Note that due to interpolation, there will
        # be issues at the boundary of the step function. This will distort up
        # to two points in the interpolated function, and those points should
        # be off by at most 0.5.
        newstep = heaviside(x_morph, 1.5, 3)
        res = sum(numpy.fabs(newstep - y_morph))
        assert res < 1

        # Stretch by -10%
        morph.stretch = -0.1
        x_morph, y_morph, x_target, y_target = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        # Target should be unchanged
        assert numpy.allclose(self.y_target, y_target)

        # Compare to new function. Note that due to interpolation, there will
        # be issues at the boundary of the step function. This will distort up
        # to two points in the interpolated function, and those points should
        # be off by at most 0.5.
        newstep = heaviside(x_morph, 0.9, 1.8)
        res = sum(numpy.fabs(newstep - y_morph))
        assert res < 1
        return


def heaviside(x, lb, ub):
    """The Heaviside function."""
    y = numpy.ones_like(x)
    y[x < lb] = 0.0
    y[x > ub] = 0.0
    return y


@pytest.mark.parametrize(
    "stretch, wmsg_gen",
    [
        # extrapolate below
        (
            0.01,
            lambda x: (
                "Warning: points with grid value below "
                f"{x[0]} are extrapolated."
            ),
        ),
        # extrapolate above
        (
            -0.01,
            lambda x: (
                "Warning: points with grid value above "
                f"{x[1]} are extrapolated."
            ),
        ),
    ],
)
def test_morphshift_extrapolate(user_filesystem, stretch, wmsg_gen):
    x_morph = numpy.linspace(1, 10, 101)
    y_morph = numpy.sin(x_morph)
    x_target = x_morph.copy()
    y_target = y_morph.copy()
    with pytest.warns() as warning:
        morphpy.morph_arrays(
            numpy.array([x_morph, y_morph]).T,
            numpy.array([x_target, y_target]).T,
            stretch=stretch,
            apply=True,
        )
        assert len(warning) == 1
        assert warning[0].category is UserWarning
        actual_wmsg = str(warning[0].message)
    expected_wmsg = wmsg_gen([min(x_morph), max(x_morph)])
    assert actual_wmsg == expected_wmsg

    # CLI test
    morph_file, target_file = create_morph_data_file(
        user_filesystem / "cwd_dir", x_morph, y_morph, x_target, y_target
    )

    parser = create_option_parser()
    (opts, pargs) = parser.parse_args(
        [
            f"--stretch={stretch}",
            f"{morph_file.as_posix()}",
            f"{target_file.as_posix()}",
            "--apply",
            "-n",
        ]
    )
    with pytest.warns(UserWarning, match=expected_wmsg):
        single_morph(parser, opts, pargs, stdout_flag=False)


def test_morphshift_no_warning(user_filesystem):
    # Apply a stretch with no extrapolation
    # There should be no warning or errors produced
    x_morph = numpy.linspace(1, 10, 101)
    y_morph = numpy.sin(x_morph)
    x_target = x_morph.copy()
    y_target = y_morph.copy()
    morphpy.morph_arrays(
        numpy.array([x_morph, y_morph]).T,
        numpy.array([x_target, y_target]).T,
        stretch=0,
        apply=True,
    )

    # CLI test
    morph_file, target_file = create_morph_data_file(
        user_filesystem / "cwd_dir", x_morph, y_morph, x_target, y_target
    )

    parser = create_option_parser()
    (opts, pargs) = parser.parse_args(
        [
            "--stretch=0",
            f"{morph_file.as_posix()}",
            f"{target_file.as_posix()}",
            "--apply",
            "-n",
        ]
    )
    single_morph(parser, opts, pargs, stdout_flag=False)
