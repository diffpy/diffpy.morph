#!/usr/bin/env python


import os

import numpy
import pytest

from diffpy.morph.morphs.morphrgrid import MorphRGrid

# useful variables
thisfile = locals().get("__file__", "file.py")
tests_dir = os.path.dirname(os.path.abspath(thisfile))
# testdata_dir = os.path.join(tests_dir, 'testdata')


##############################################################################
class TestMorphRGrid:
    @pytest.fixture
    def setup(self):
        self.x_morph = numpy.arange(0, 10, 0.01)
        self.y_morph = self.x_morph.copy()
        self.x_target = numpy.arange(1, 5, 0.01)
        self.y_target = self.x_target**2
        return

    def _runTests(self, xyallout, morph):
        x_morph, y_morph, x_target, y_target = xyallout
        assert (x_morph == x_target).all()
        pytest.approx(x_morph[0], morph.rmin)
        pytest.approx(x_morph[-1], morph.rmax - morph.rstep)
        pytest.approx(x_morph[1] - x_morph[0], morph.rstep)
        pytest.approx(len(y_morph), len(y_target))
        return

    def testRangeInBounds(self, setup):
        """Selected range is within input bounds."""

        config = {
            "rmin": 1.0,
            "rmax": 2.0,
            "rstep": 0.1,
        }
        morph = MorphRGrid(config)
        xyallout = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )
        pytest.approx(config["rmin"], morph.rmin)
        pytest.approx(config["rmax"], morph.rmax)
        pytest.approx(config["rstep"], morph.rstep)
        self._runTests(xyallout, morph)
        return

    def testRmaxOut(self, setup):
        """Selected rmax is outside of input bounds."""

        config = {
            "rmin": 1.0,
            "rmax": 15.0,
            "rstep": 0.1,
        }
        morph = MorphRGrid(config)
        xyallout = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )
        pytest.approx(config["rmin"], morph.rmin)
        pytest.approx(5, morph.rmax)
        pytest.approx(config["rstep"], morph.rstep)
        self._runTests(xyallout, morph)
        return

    def testRminOut(self, setup):
        """Selected rmin is outside of input bounds."""

        config = {
            "rmin": 0.0,
            "rmax": 2.0,
            "rstep": 0.01,
        }
        morph = MorphRGrid(config)
        xyallout = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )
        pytest.approx(1.0, morph.rmin)
        pytest.approx(config["rmax"], morph.rmax)
        pytest.approx(config["rstep"], morph.rstep)
        self._runTests(xyallout, morph)
        return

    def testRstepOut(self, setup):
        """Selected rstep is outside of input bounds."""

        config = {
            "rmin": 1.0,
            "rmax": 2.0,
            "rstep": 0.001,
        }
        morph = MorphRGrid(config)
        xyallout = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )
        pytest.approx(config["rmin"], morph.rmin)
        pytest.approx(config["rmax"], morph.rmax)
        pytest.approx(0.01, morph.rstep)
        self._runTests(xyallout, morph)
        return
