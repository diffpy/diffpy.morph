#!/usr/bin/env python


import os

import numpy
import pytest

from diffpy.pdfmorph.morphs.morphsmear import MorphSmear

# useful variables
thisfile = locals().get("__file__", "file.py")
tests_dir = os.path.dirname(os.path.abspath(thisfile))
# testdata_dir = os.path.join(tests_dir, 'testdata')


class TestMorphSmear:
    @pytest.fixture
    def setup(self):
        self.smear = 0.1
        self.r0 = 7 * numpy.pi / 22.0 * 2
        self.x_morph = numpy.arange(0.01, 5, 0.01)
        self.y_morph = numpy.exp(
            -0.5 * ((self.x_morph - self.r0) / self.smear) ** 2
        )
        self.x_target = self.x_morph.copy()
        self.y_target = self.x_target.copy()
        return

    def test_morph(self, setup):
        """check MorphSmear.morph()"""
        morph = MorphSmear()
        morph.smear = 0.15

        x_morph, y_morph, x_target, y_target = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        # Target should be unchanged
        assert numpy.allclose(self.y_target, y_target)

        # Compare to broadened Gaussian
        sigbroad = (self.smear**2 + morph.smear**2) ** 0.5
        ysmear = numpy.exp(-0.5 * ((self.x_morph - self.r0) / sigbroad) ** 2)
        ysmear *= self.smear / sigbroad

        assert numpy.allclose(ysmear, y_morph)
        return


# End of class TestMorphSmear

if __name__ == "__main__":
    TestMorphSmear()

# End of file
