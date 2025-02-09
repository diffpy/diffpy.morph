#!/usr/bin/env python


import os

import numpy
import pytest

from diffpy.pdfmorph.morphs.morphstretch import MorphStretch

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
        """check MorphStretch.morph()"""
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


# End of class TestMorphSmear


def heaviside(x, lb, ub):
    """The Heaviside function."""
    y = numpy.ones_like(x)
    y[x < lb] = 0.0
    y[x > ub] = 0.0
    return y


if __name__ == "__main__":
    TestMorphStretch()

# End of file
