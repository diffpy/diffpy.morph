#!/usr/bin/env python


import os

import numpy
import pytest

from diffpy.morph.morph_helpers.transformpdftordf import TransformXtalPDFtoRDF
from diffpy.morph.morph_helpers.transformrdftopdf import TransformXtalRDFtoPDF
from diffpy.morph.morphs.morphchain import MorphChain
from diffpy.morph.morphs.morphscale import MorphScale
from diffpy.morph.morphs.morphsmear import MorphSmear
from diffpy.morph.morphs.morphstretch import MorphStretch
from diffpy.morph.refine import Refiner

# useful variables
thisfile = locals().get("__file__", "file.py")
tests_dir = os.path.dirname(os.path.abspath(thisfile))
testdata_dir = os.path.join(tests_dir, "testdata")


class TestRefine:
    @pytest.fixture
    def setup(self):
        self.x_morph = numpy.arange(0.01, 5, 0.01)
        self.y_morph = numpy.ones_like(self.x_morph)
        self.x_target = numpy.arange(0.01, 5, 0.01)
        self.y_target = 3 * numpy.ones_like(self.x_target)
        return

    def test_refine_morph(self, setup):
        """refine a morph"""
        # Define the morphs
        config = {
            "scale": 1.0,
        }

        mscale = MorphScale(config)
        refiner = Refiner(
            mscale, self.x_morph, self.y_morph, self.x_target, self.y_target
        )
        refiner.refine()

        x_morph, y_morph, x_target, y_target = mscale.xyallout

        assert (x_morph == x_target).all()
        assert numpy.allclose(y_morph, y_target)
        pytest.approx(config["scale"], 3.0)
        return

    def test_refine_chain(self, setup):
        """refine a chain"""
        # Give this some texture
        self.y_morph[30:] = 5
        self.y_target[33:] = 15

        # Define the morphs
        config = {"scale": 1.0, "stretch": 0.0}

        mscale = MorphScale(config)
        mstretch = MorphStretch(config)
        chain = MorphChain(config, mscale, mstretch)

        refiner = Refiner(
            chain, self.x_morph, self.y_morph, self.x_target, self.y_target
        )
        res = refiner.refine()

        # Compare the morph to the target. Note that due to
        # interpolation, there will be issues at the boundary of the step
        # function.
        x_morph, y_morph, x_target, y_target = chain.xyallout
        err = 15.0 * 2
        res = sum(numpy.fabs(y_target - y_morph))
        assert res < err
        pytest.approx(chain.scale, 3, 2)
        pytest.approx(chain.stretch, 0.1, 2)
        return


# End of class TestRefine


class TestRefineUC:
    @pytest.fixture
    def setup(self):
        morph_file = os.path.join(testdata_dir, "nickel_ss0.01.cgr")
        self.x_morph, self.y_morph = numpy.loadtxt(
            morph_file, unpack=True, skiprows=8
        )
        target_file = os.path.join(testdata_dir, "nickel_ss0.02_eps0.002.cgr")
        self.x_target, self.y_target = numpy.loadtxt(
            target_file, unpack=True, skiprows=8
        )
        self.y_target *= 1.5
        return

    def test_refine(self, setup):
        config = {
            "scale": 1.0,
            "stretch": 0,
            "smear": 0,
            "baselineslope": -4 * numpy.pi * 0.0917132,
        }

        # Note that scale must go first, since it does not commute with the
        # PDF <--> RDF conversion.
        chain = MorphChain(config)
        chain.append(MorphScale())
        chain.append(MorphStretch())
        chain.append(TransformXtalPDFtoRDF())
        chain.append(MorphSmear())
        chain.append(TransformXtalRDFtoPDF())

        refiner = Refiner(
            chain, self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        # Do this as two-stage fit. First refine amplitude parameters, and then
        # position parameters.
        refiner.refine("scale", "smear")
        refiner.refine("scale", "stretch", "smear")

        x_morph, y_morph, x_target, y_target = chain.xyallout
        # We want the fit good to 1%. We will disregard the last bit of the
        # fit, since we know we have unavoidable edge effects there.
        sel = x_morph < 9.5
        yrsel = y_target[sel]
        diff = yrsel - y_morph[sel]
        rw = (numpy.dot(diff, diff) / numpy.dot(yrsel, yrsel)) ** 0.5
        assert rw < 0.01
        return


if __name__ == "__main__":
    TestRefine()
    TestRefineUC()

# End of file
