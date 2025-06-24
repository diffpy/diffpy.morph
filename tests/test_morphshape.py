#!/usr/bin/env python


import os

import numpy
import pytest

from diffpy.morph.morphs.morphishape import MorphISpheroid
from diffpy.morph.morphs.morphshape import MorphSphere, MorphSpheroid

# FIXME: add MorphISphere test

# useful variables
thisfile = locals().get("__file__", "file.py")
tests_dir = os.path.dirname(os.path.abspath(thisfile))
testdata_dir = os.path.join(tests_dir, "testdata")


class TestMorphSphere:
    @pytest.fixture
    def setup(self):
        morph_file = os.path.join(testdata_dir, "ni_qmax25.cgr")
        self.x_morph, self.y_morph = numpy.loadtxt(morph_file, unpack=True)
        target_file = os.path.join(testdata_dir, "ni_qmax25_psize35.cgr")
        self.x_target, self.y_target = numpy.loadtxt(target_file, unpack=True)
        return

    def test_morph(self, setup):
        """Check MorphSphere.morph()"""
        config = {"radius": 17.5}
        morph = MorphSphere(config)

        x_morph, y_morph, x_target, y_target = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        assert numpy.allclose(self.y_target, y_target)
        assert numpy.allclose(y_morph, y_target)
        return


# End of class TestMorphSphere


class TestMorphSpheroid:
    # Common configs for testing MorphSpheroid and MorphISpheroid
    config_sphere = {"radius": 17.5, "pradius": 17.5}
    config_oblate = {"radius": 17.5, "pradius": 5.0}
    config_prolate = {"radius": 5.0, "pradius": 17.5}
    spheroid_configs = [config_sphere, config_oblate, config_prolate]
    iconfig_sphere = {"iradius": 17.5, "ipradius": 17.5}
    iconfig_oblate = {"iradius": 17.5, "ipradius": 5.0}
    iconfig_prolate = {"iradius": 5.0, "ipradius": 17.5}
    ispheroid_configs = [iconfig_sphere, iconfig_oblate, iconfig_prolate]

    # Files used for testing
    flag_inverse = (
        0  # Indicates whether we are testing MorphSpheroid or MorphISpheroid
    )
    testfiles = [
        ["ni_qmax25.cgr", "ni_qmax25_psize35.cgr"],  # Sphere
        ["ni_qmax25.cgr", "ni_qmax25_e17.5_p5.0.cgr"],  # Oblate spheroid
        ["ni_qmax25.cgr", "ni_qmax25_e5.0_p17.5.cgr"],  # Prolate spheroid
    ]
    testfile = []  # Initialize testfile array

    def reset(self):
        if len(self.testfile) == 0:
            # Ignore first init
            return
        morph_file = os.path.join(
            testdata_dir, self.testfile[0 - self.flag_inverse]
        )
        self.x_morph, self.y_morph = numpy.loadtxt(morph_file, unpack=True)
        target_file = os.path.join(
            testdata_dir, self.testfile[1 - self.flag_inverse]
        )
        self.x_target, self.y_target = numpy.loadtxt(target_file, unpack=True)
        return

    def test_morph(self):
        """Check MorphSpheroid.morph() and MorphISpheroid.morph()"""

        for idx in range(len(self.testfiles)):
            self.testfile = self.testfiles[idx]

            # Test MorphSpheroid.morph()
            self.flag_inverse = 0
            self.reset()
            self.shape_test_helper(self.spheroid_configs[idx])

            # Test MorphISpheroid.morph()
            self.flag_inverse = 1
            self.reset()
            self.ishape_test_helper(self.ispheroid_configs[idx])
        return

    def shape_test_helper(self, config):
        morph = MorphSpheroid(config)

        x_morph, y_morph, x_target, y_target = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        assert numpy.allclose(self.y_target, y_target)
        assert numpy.allclose(y_morph, y_target)
        return

    def ishape_test_helper(self, config):
        morph = MorphISpheroid(config)

        x_morph, y_morph, x_target, y_target = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        assert numpy.allclose(self.y_target, y_target)

        psize = 2 * max(config["iradius"], config["ipradius"])
        for idx in range(len(x_morph)):
            if x_morph[idx] < psize:  # Within the particle
                assert numpy.isclose(y_morph[idx], y_target[idx])
            elif x_morph[idx] == psize:
                pass  # FIXME: determine behavior at boundary
            else:  # Outside the particle morph should be zero
                assert y_morph[idx] == 0
        return


# End of class TestMorphSpheroid

if __name__ == "__main__":
    TestMorphSphere()
    TestMorphSpheroid()

# End of file
