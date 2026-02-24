#!/usr/bin/env python


import os

import numpy
import pytest

from diffpy.morph.morph_helpers.transformpdftordf import TransformXtalPDFtoRDF
from diffpy.morph.morph_helpers.transformrdftopdf import TransformXtalRDFtoPDF
from diffpy.morph.morphapp import create_option_parser, single_morph
from diffpy.morph.morphs.morphchain import MorphChain
from diffpy.morph.morphs.morphfuncx import MorphFuncx
from diffpy.morph.morphs.morphrgrid import MorphRGrid
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
        """Refine a morph."""
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
        assert pytest.approx(config["scale"]) == 3.0
        return

    def test_refine_chain(self, setup):
        """Refine a chain."""
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
        assert pytest.approx(chain.scale, 0.01, 0.01) == 3.0
        assert pytest.approx(chain.stretch, 0.01, 0.01) == 0.1
        return

    def test_refine_tolerance(self, setup):
        # Check that small tolerance gives good result
        stol = 1e-16
        config = {
            "scale": 1.0,
        }
        mscale = MorphScale(config)
        refiner = Refiner(
            mscale,
            self.x_morph,
            self.y_morph,
            self.x_target,
            self.y_target,
            tolerance=stol,
        )
        refiner.refine()
        assert pytest.approx(config["scale"], stol, stol) == 3.0

        # Check that larger tolerance does not give as good of result
        ltol = 100
        config = {
            "scale": 1.0,
        }
        mscale = MorphScale(config)
        refiner = Refiner(
            mscale,
            self.x_morph,
            self.y_morph,
            self.x_target,
            self.y_target,
            tolerance=ltol,
        )
        refiner.refine()
        assert not pytest.approx(config["scale"], stol, stol) == 3.0
        return

    def test_refine_grid_change(self):
        err = 1e-08

        # First test what occurs when the grid overlap increases
        # As we shift, the overlap number increases
        # In this case, overlap goes from 41 -> 51
        exp_hshift = 1
        grid1 = numpy.linspace(0, 5, 51)
        grid2 = numpy.linspace(0 + exp_hshift, 5 + exp_hshift, 51)
        func1 = numpy.zeros(grid1.shape)
        func1[(1 < grid1) & (grid1 < 4)] = 1
        func2 = numpy.zeros(grid2.shape)
        func2[(1 + exp_hshift < grid2) & (grid2 < 4 + exp_hshift)] = 1

        def shift(x, y, hshift):
            return x + hshift

        config = {
            "funcx_function": shift,
            "funcx": {"hshift": 0},
            "xmin": 0,
            "xmax": 7,
            "xstep": 0.01,
        }

        mfuncx = MorphFuncx(config)
        mrgrid = MorphRGrid(config)
        chain = MorphChain(config, mfuncx, mrgrid)
        refiner = Refiner(chain, grid1, func1, grid2, func2)
        refpars = ["funcx"]
        res = refiner.refine(*refpars)

        assert res < err

        # Second test when the grid overlap decreases
        # As we stretch, the grid spacing increases
        # Thus, the overlap number decreases
        # For this test, overlap goes from 12 -> 10
        grid1 = numpy.linspace(0, 4, 41)
        grid2 = numpy.linspace(2, 4, 21)
        func1 = numpy.zeros(grid1.shape)
        func1[grid1 <= 2] = 1
        func1[2 < grid1] = 2
        func2 = numpy.zeros(grid2.shape) + 1

        def stretch(x, y, stretch):
            return x * (1 + stretch)

        config = {
            "funcx_function": stretch,
            "funcx": {"stretch": 0.7},
            "xmin": 0,
            "xmax": 4,
            "xstep": 0.01,
        }

        mfuncx = MorphFuncx(config)
        mrgrid = MorphRGrid(config)
        chain = MorphChain(config, mfuncx, mrgrid)
        refiner = Refiner(chain, grid1, func1, grid2, func2)
        refpars = ["funcx"]
        res = refiner.refine(*refpars)

        assert res < err

    def test_refine_grid_bad(self, user_filesystem, capsys):
        grid = numpy.arange(2)
        func = numpy.sin(grid)
        grid1, func1, grid2, func2 = grid, func, grid, func
        config = {
            "stretch": 0.005,
            "scale": 1.0,
            "smear": 0,
        }
        chain = MorphChain(config)
        refiner = Refiner(chain, grid1, func1, grid2, func2)
        refpars = ["stretch", "scale", "smear"]
        expected_error_message = (
            "\nNumber of parameters (currently 3) cannot "
            "exceed the number of shared grid points "
            "(currently 2). "
            "Please reduce the number of morphing parameters or "
            "provide new morphing and target functions with more "
            "shared grid points."
        )
        with pytest.raises(
            ValueError,
        ) as error:
            refiner.refine(*refpars)
        actual_error_message = str(error.value)
        assert actual_error_message == expected_error_message

        # Test from command line
        data_dir_path = user_filesystem / "cwd_dir"
        morph_file = data_dir_path / "morph_data"
        morph_data_text = [
            str(grid1[i]) + " " + str(func1[i]) for i in range(len(grid1))
        ]
        morph_data_text = "\n".join(morph_data_text)
        morph_file.write_text(morph_data_text)
        target_file = data_dir_path / "target_data"
        target_data_text = [
            str(grid2[i]) + " " + str(func2[i]) for i in range(len(grid2))
        ]
        target_data_text = "\n".join(target_data_text)
        target_file.write_text(target_data_text)
        run_cmd = []
        for key, value in config.items():
            run_cmd.append(f"--{key}")
            run_cmd.append(f"{value}")
        run_cmd.extend([str(morph_file), str(target_file)])
        run_cmd.append("-n")
        parser = create_option_parser()
        (opts, pargs) = parser.parse_args(run_cmd)
        with pytest.raises(ValueError) as excinfo:
            single_morph(parser, opts, pargs, stdout_flag=False)
        assert expected_error_message in str(excinfo.value)


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
