#!/usr/bin/env python


import os

import numpy
import pytest

from diffpy.pdfmorph.morphs.morphresolution import MorphResolutionDamping

# useful variables
thisfile = locals().get("__file__", "file.py")
tests_dir = os.path.dirname(os.path.abspath(thisfile))
testdata_dir = os.path.join(tests_dir, "testdata")


class TestMorphScale:
    @pytest.fixture
    def setup(self):
        morph_file = os.path.join(testdata_dir, "ni_qmax25.cgr")
        self.x_morph, self.y_morph = numpy.loadtxt(morph_file, unpack=True)
        target_file = os.path.join(testdata_dir, "ni_qmax25_qdamp0.01.cgr")
        self.x_target, self.y_target = numpy.loadtxt(target_file, unpack=True)
        return

    def test_morph(self, setup):
        """check MorphScale.morph()"""
        config = {"qdamp": 0.01}
        morph = MorphResolutionDamping(config)

        x_morph, y_morph, x_target, y_target = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        assert numpy.allclose(self.y_target, y_target)
        assert numpy.allclose(y_morph, y_target)
        return


# End of class TestMorphScale

if __name__ == "__main__":
    TestMorphScale()

# End of file
