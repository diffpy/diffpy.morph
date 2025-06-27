#!/usr/bin/env python


import os

import numpy
import pytest

from diffpy.morph.morphs.morphshift import MorphShift

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
