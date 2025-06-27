#!/usr/bin/env python

from pathlib import Path

import numpy as np
import pytest

from diffpy.morph.morphapp import create_option_parser, single_morph
from diffpy.morph.morphpy import morph, morph_arrays
from diffpy.morph.tools import getRw

thisfile = locals().get("__file__", "file.py")
tests_dir = Path(thisfile).parent.resolve()
testdata_dir = tests_dir.joinpath("testdata")
testsequence_dir = testdata_dir.joinpath("testsequence")

nickel_PDF = testdata_dir.joinpath("nickel_ss0.01.cgr")
serial_JSON = testdata_dir.joinpath("testsequence_serialfile.json")

testsaving_dir = testsequence_dir.joinpath("testsaving")
test_saving_succinct = testsaving_dir.joinpath("succinct")
test_saving_verbose = testsaving_dir.joinpath("verbose")
tssf = testdata_dir.joinpath("testsequence_serialfile.json")


class TestMorphpy:
    @pytest.fixture
    def setup_morph(self):
        self.parser = create_option_parser()
        filenames = [
            "g_174K.gr",
            "f_180K.gr",
            "e_186K.gr",
            "d_192K.gr",
            "c_198K.gr",
            "b_204K.gr",
            "a_210K.gr",
        ]
        self.testfiles = []
        self.morphapp_results = {}

        # Parse arguments sorting by field
        (opts, pargs) = self.parser.parse_args(
            [
                "--scale",
                "1",
                "--stretch",
                "0",
                "-n",
                "--sort-by",
                "temperature",
            ]
        )
        for filename in filenames:
            self.testfiles.append(testsequence_dir.joinpath(filename))

            # Run multiple single morphs
            morph_file = self.testfiles[0]
            for target_file in self.testfiles[1:]:
                pargs = [morph_file, target_file]
                # store in same format of dictionary as multiple_targets
                self.morphapp_results.update(
                    {
                        target_file.name: single_morph(
                            self.parser, opts, pargs, stdout_flag=False
                        )
                    }
                )
        return

    def test_morph(self, setup_morph):
        morph_results = {}
        morph_file = self.testfiles[0]
        for target_file in self.testfiles[1:]:
            mr, grm = morph(
                morph_file,
                target_file,
                scale=1,
                stretch=0,
                sort_by="temperature",
            )
            _, grt = morph(target_file, target_file)
            morph_results.update({target_file.name: mr})

            class Chain:
                xyallout = grm[:, 0], grm[:, 1], grt[:, 0], grt[:, 1]

            chain = Chain()
            rw = getRw(chain)
            del chain
            assert np.allclose(
                [rw], [self.morphapp_results[target_file.name]["Rw"]]
            )
        assert morph_results == self.morphapp_results

    def test_morphpy(self, setup_morph):
        morph_results = {}
        morph_file = self.testfiles[0]
        for target_file in self.testfiles[1:]:
            _, grm0 = morph(morph_file, morph_file)
            _, grt = morph(target_file, target_file)
            mr, grm = morph_arrays(
                grm0, grt, scale=1, stretch=0, sort_by="temperature"
            )
            morph_results.update({target_file.name: mr})

            class Chain:
                xyallout = grm[:, 0], grm[:, 1], grt[:, 0], grt[:, 1]

            chain = Chain()
            rw = getRw(chain)
            del chain
            assert np.allclose(
                [rw], [self.morphapp_results[target_file.name]["Rw"]]
            )
        assert morph_results == self.morphapp_results

    def test_morphfuncy(self, setup_morph):
        def gaussian(x, mu, sigma):
            return np.exp(-((x - mu) ** 2) / (2 * sigma**2)) / (
                sigma * np.sqrt(2 * np.pi)
            )

        def gaussian_like_function(x, y, mu):
            return gaussian((x + y) / 2, mu, 3)

        morph_r = np.linspace(0, 100, 1001)
        morph_gr = np.linspace(0, 100, 1001)

        target_r = np.linspace(0, 100, 1001)
        target_gr = 0.5 * gaussian(target_r, 50, 5) + 0.05

        morph_info, _ = morph_arrays(
            np.array([morph_r, morph_gr]).T,
            np.array([target_r, target_gr]).T,
            scale=1,
            smear=3.75,
            vshift=0.01,
            funcy=(gaussian_like_function, {"mu": 47.5}),
            tolerance=1e-12,
        )

        assert pytest.approx(morph_info["scale"]) == 0.5
        assert pytest.approx(morph_info["vshift"]) == 0.05
        assert pytest.approx(abs(morph_info["smear"])) == 4.0
        assert pytest.approx(morph_info["funcy"]["mu"]) == 50.0

    def test_morphpy_outputs(self, tmp_path):
        r = np.linspace(0, 1, 11)
        gr = np.linspace(0, 1, 11)

        def linear(x, y, s):
            return s * (x + y)

        morph_info, _ = morph_arrays(
            np.array([r, gr]).T,
            np.array([r, gr]).T,
            squeeze=[1, 2, 3, 4, 5],
            funcy=(linear, {"s": 2.5}),
            apply=True,
        )

        print(morph_info)
        for i in range(5):
            assert pytest.approx(morph_info["squeeze"][f"a{i}"]) == i + 1
        assert pytest.approx(morph_info["funcy"]["s"]) == 2.5
