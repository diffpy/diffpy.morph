#!/usr/bin/env python


import os

import numpy
import pytest

from diffpy.pdfmorph.morphs.morphchain import MorphChain
from diffpy.pdfmorph.morphs.morphrgrid import MorphRGrid
from diffpy.pdfmorph.morphs.morphscale import MorphScale

# useful variables
thisfile = locals().get("__file__", "file.py")
tests_dir = os.path.dirname(os.path.abspath(thisfile))
# testdata_dir = os.path.join(tests_dir, 'testdata')


class TestMorphChain:
    @pytest.fixture
    def setup(self):
        self.x_morph = numpy.arange(0.01, 5, 0.01)
        self.y_morph = numpy.ones_like(self.x_morph)
        self.x_target = numpy.arange(0.01, 5, 0.01)
        self.y_target = 3 * numpy.ones_like(self.x_target)

        return

    def test_morph(self, setup):
        """check MorphChain.morph()"""
        # Define the morphs
        config = {
            "rmin": 1,
            "rmax": 6,
            "rstep": 0.1,
            "scale": 3.0,
        }

        mgrid = MorphRGrid()
        mscale = MorphScale()
        chain = MorphChain(config, mgrid, mscale)

        x_morph, y_morph, x_target, y_target = chain(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        assert (x_morph == x_target).all()
        pytest.approx(x_morph[0], 1.0)
        pytest.approx(x_morph[-1], 4.9)
        pytest.approx(x_morph[1] - x_morph[0], 0.1)
        pytest.approx(x_morph[0], mgrid.rmin)
        pytest.approx(x_morph[-1], mgrid.rmax - mgrid.rstep)
        pytest.approx(x_morph[1] - x_morph[0], mgrid.rstep)
        assert numpy.allclose(y_morph, y_target)
        return


# End of class TestMorphChain

if __name__ == "__main__":
    TestMorphChain()

# End of file
