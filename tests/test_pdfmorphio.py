#!/usr/bin/env python

from pathlib import Path

import pytest

from diffpy.pdfmorph.pdfmorphapp import (
    create_option_parser,
    multiple_targets,
    single_morph,
)

# Support Python 2
try:
    from future_builtins import filter, zip
except ImportError:
    pass

thisfile = locals().get("__file__", "file.py")
tests_dir = Path(thisfile).parent.resolve()
testdata_dir = tests_dir.joinpath("testdata")
testsequence_dir = testdata_dir.joinpath("testsequence")

testsaving_dir = testdata_dir.joinpath("testsaving")
test_saving_succinct = testsaving_dir.joinpath("succinct")
test_saving_verbose = testsaving_dir.joinpath("verbose")
tssf = testdata_dir.joinpath("testsequence_serialfile.json")


class TestApp:
    @pytest.fixture
    def setup(self):
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
        for filename in filenames:
            self.testfiles.append(testsequence_dir.joinpath(filename))
        return

    def test_morph_outputs(self, setup, tmp_path):
        # Ignore PATH data when comparing files
        def ignore_path(line):
            # Lines containing FILE PATH data begin with '# from '
            if "# from " in line:
                return False
            # Lines containing DIRECTORY PATH data begin with '# with '
            if "# with " in line:
                return False
            return True

        morph_file = self.testfiles[0]
        target_file = self.testfiles[-1]

        # Save multiple succinct morphs
        tmp_succinct = tmp_path.joinpath("succinct")
        tmp_succinct_name = tmp_succinct.resolve().as_posix()

        (opts, pargs) = self.parser.parse_args(
            [
                "--multiple-targets",
                "--sort-by",
                "temperature",
                "-s",
                tmp_succinct_name,
                "-n",
                "--save-names-file",
                tssf,
            ]
        )
        pargs = [morph_file, testsequence_dir]
        multiple_targets(self.parser, opts, pargs, stdout_flag=False)

        # Save a single succinct morph
        ssm = tmp_succinct.joinpath("single_succinct_morph.cgr")
        ssm_name = ssm.resolve().as_posix()
        (opts, pargs) = self.parser.parse_args(["-s", ssm_name, "-n"])
        pargs = [morph_file, target_file]
        single_morph(self.parser, opts, pargs, stdout_flag=False)

        # Check the saved files are the same for succinct
        common = []
        for item in tmp_succinct.glob("**/*.*"):
            if item.is_file():
                common.append(item.relative_to(tmp_succinct).as_posix())
        for file in common:
            with open(tmp_succinct.joinpath(file)) as gf:
                with open(test_saving_succinct.joinpath(file)) as tf:
                    generated = filter(ignore_path, gf)
                    target = filter(ignore_path, tf)
                    assert all(x == y for x, y in zip(generated, target))

        # Save multiple verbose morphs
        tmp_verbose = tmp_path.joinpath("verbose")
        tmp_verbose_name = tmp_verbose.resolve().as_posix()

        (opts, pargs) = self.parser.parse_args(
            [
                "--multiple-targets",
                "--sort-by",
                "temperature",
                "-s",
                tmp_verbose_name,
                "-n",
                "--save-names-file",
                tssf,
                "--verbose",
            ]
        )
        pargs = [morph_file, testsequence_dir]
        multiple_targets(self.parser, opts, pargs, stdout_flag=False)

        # Save a single verbose morph
        svm = tmp_verbose.joinpath("single_verbose_morph.cgr")
        svm_name = svm.resolve().as_posix()
        (opts, pargs) = self.parser.parse_args(
            ["-s", svm_name, "-n", "--verbose"]
        )
        pargs = [morph_file, target_file]
        single_morph(self.parser, opts, pargs, stdout_flag=False)

        # Check the saved files are the same for verbose
        common = []
        for item in tmp_verbose.glob("**/*.*"):
            if item.is_file():
                common.append(item.relative_to(tmp_verbose).as_posix())
        for file in common:
            with open(tmp_verbose.joinpath(file)) as gf:
                with open(test_saving_verbose.joinpath(file)) as tf:
                    generated = filter(ignore_path, gf)
                    target = filter(ignore_path, tf)
                    assert all(x == y for x, y in zip(generated, target))
