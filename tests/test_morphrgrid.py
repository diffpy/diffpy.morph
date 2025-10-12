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
        pytest.approx(x_morph[0], morph.xmin)
        pytest.approx(x_morph[-1], morph.xmax - morph.xstep)
        pytest.approx(x_morph[1] - x_morph[0], morph.xstep)
        pytest.approx(len(y_morph), len(y_target))
        return

    def testRangeInBounds(self, setup):
        """Selected range is within input bounds."""

        config = {
            "xmin": 1.0,
            "xmax": 2.0,
            "xstep": 0.1,
        }
        morph = MorphRGrid(config)
        xyallout = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )
        pytest.approx(config["xmin"], morph.xmin)
        pytest.approx(config["xmax"], morph.xmax)
        pytest.approx(config["xstep"], morph.xstep)
        self._runTests(xyallout, morph)
        return

    def testxmaxOut(self, setup):
        """Selected xmax is outside of input bounds."""

        config = {
            "xmin": 1.0,
            "xmax": 15.0,
            "xstep": 0.1,
        }
        morph = MorphRGrid(config)
        xyallout = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )
        pytest.approx(config["xmin"], morph.xmin)
        pytest.approx(5, morph.xmax)
        pytest.approx(config["xstep"], morph.xstep)
        self._runTests(xyallout, morph)
        return

    def testxminOut(self, setup):
        """Selected xmin is outside of input bounds."""

        config = {
            "xmin": 0.0,
            "xmax": 2.0,
            "xstep": 0.01,
        }
        morph = MorphRGrid(config)
        xyallout = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )
        pytest.approx(1.0, morph.xmin)
        pytest.approx(config["xmax"], morph.xmax)
        pytest.approx(config["xstep"], morph.xstep)
        self._runTests(xyallout, morph)
        return

    def testxstepOut(self, setup):
        """Selected xstep is outside of input bounds."""

        config = {
            "xmin": 1.0,
            "xmax": 2.0,
            "xstep": 0.001,
        }
        morph = MorphRGrid(config)
        xyallout = morph(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )
        pytest.approx(config["xmin"], morph.xmin)
        pytest.approx(config["xmax"], morph.xmax)
        pytest.approx(0.01, morph.xstep)
        self._runTests(xyallout, morph)
        return
