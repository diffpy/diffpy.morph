#!/usr/bin/env python

from pathlib import Path

import pytest
import numpy

from diffpy.morph.morphapp import (
    create_option_parser,
    single_morph,
)
from diffpy.morph.tools import getRw
from diffpy.morph.morphpy import (
    morph,
    morphpy,
)

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


class TestApp:
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
            mr, grm = morph(morph_file, target_file, scale=1, stretch=0, sort_by="temperature")
            _, grt = morph(target_file, target_file)
            morph_results.update({target_file.name: mr})
            class Chain:
                xyallout = grm[:, 0], grm[:, 1], grt[:, 0], grt[:, 1]
            chain = Chain()
            rw = getRw(chain)
            del chain
            assert numpy.allclose([rw], [self.morphapp_results[target_file.name]["Rw"]])
        assert morph_results == self.morphapp_results

    def test_morphpy(self, setup_morph):
        morph_results = {}
        morph_file = self.testfiles[0]
        for target_file in self.testfiles[1:]:
            _, grm0 = morph(morph_file, morph_file)
            _, grt = morph(target_file, target_file)
            mr, grm = morphpy(grm0, grt, scale=1, stretch=0, sort_by="temperature")
            morph_results.update({target_file.name: mr})

            class Chain:
                xyallout = grm[:, 0], grm[:, 1], grt[:, 0], grt[:, 1]

            chain = Chain()
            rw = getRw(chain)
            del chain
            assert numpy.allclose([rw], [self.morphapp_results[target_file.name]["Rw"]])
        assert morph_results == self.morphapp_results


if __name__ == "__main__":
    TestApp()
