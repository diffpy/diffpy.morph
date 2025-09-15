#!/usr/bin/env python


import os

import numpy
import pytest

import diffpy.morph.morphpy as morphpy
from diffpy.morph.morphapp import create_option_parser, single_morph
from diffpy.morph.morphs.morphshift import MorphShift
from tests.helper import create_morph_data_file

# useful variables
thisfile = locals().get("__file__", "file.py")
tests_dir = os.path.dirname(os.path.abspath(thisfile))
# testdata_dir = os.path.join(tests_dir, 'testdata')


class TestMorphShift:
    @pytest.fixture
    def setup(self):
        self.hshift = 2.0
        self.vshift = 3.0

        # Original dataset goes from 0.1 to 5.0
        self.x_morph = numpy.arange(0.01, 5 + self.hshift, 0.01)
        self.y_morph = numpy.arange(0.01, 5 + self.hshift, 0.01)

        # New dataset is moved to the right by 2.0 and upward by 3.0
        self.x_target = numpy.arange(0.01 + self.hshift, 5 + self.hshift, 0.01)
        self.y_target = numpy.arange(0.01 + self.vshift, 5 + self.vshift, 0.01)
        return

    def test_morph(self, setup):
        """Check MorphScale.morph()"""
        config = {"hshift": self.hshift, "vshift": self.vshift}
        morph = MorphShift(config)

        x_morph, y_morph, x_target, y_target = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        # Only care about the shifted data past the shift
        # Everything to left of shift is outside our input data domain
        assert numpy.allclose(y_morph[x_morph > self.hshift], y_target)
        assert numpy.allclose(self.x_target, x_target)
        assert numpy.allclose(self.y_target, y_target)
        return


@pytest.mark.parametrize(
    "hshift, wmsg_gen",
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
def test_morphshift_extrapolate(user_filesystem, capsys, hshift, wmsg_gen):
    x_morph = numpy.linspace(0, 10, 101)
    y_morph = numpy.sin(x_morph)
    x_target = x_morph.copy()
    y_target = y_morph.copy()
    with pytest.warns() as w:
        morphpy.morph_arrays(
            numpy.array([x_morph, y_morph]).T,
            numpy.array([x_target, y_target]).T,
            hshift=hshift,
            apply=True,
        )
        assert len(w) == 1
        assert w[0].category is UserWarning
        actual_wmsg = str(w[0].message)
    expected_wmsg = wmsg_gen([min(x_morph), max(x_morph)])
    assert actual_wmsg == expected_wmsg

    # CLI test
    morph_file, target_file = create_morph_data_file(
        user_filesystem / "cwd_dir", x_morph, y_morph, x_target, y_target
    )

    parser = create_option_parser()
    (opts, pargs) = parser.parse_args(
        [
            f"--hshift={hshift}",
            f"{morph_file.as_posix()}",
            f"{target_file.as_posix()}",
            "--apply",
            "-n",
        ]
    )
    with pytest.warns(UserWarning, match=expected_wmsg):
        single_morph(parser, opts, pargs, stdout_flag=False)
