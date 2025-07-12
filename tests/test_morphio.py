#!/usr/bin/env python

from pathlib import Path

import numpy as np
import pytest

from diffpy.morph.morphapp import (
    create_option_parser,
    multiple_targets,
    single_morph,
)
from diffpy.morph.morphpy import morph_arrays
from diffpy.utils.parsers.loaddata import loadData

# Support Python 2
try:
    from future_builtins import filter, zip
except ImportError:
    pass

thisfile = locals().get("__file__", "file.py")
tests_dir = Path(thisfile).parent.resolve()
testdata_dir = tests_dir.joinpath("testdata")
testsequence_dir = testdata_dir.joinpath("testsequence")

testsaving_dir = testsequence_dir.joinpath("testsaving")
test_saving_succinct = testsaving_dir.joinpath("succinct")
test_saving_verbose = testsaving_dir.joinpath("verbose")
tssf = testdata_dir.joinpath("testsequence_serialfile.json")


# Ignore PATH data when comparing files
def ignore_path(line):
    # Lines containing FILE PATH data begin with '# from '
    if "# from " in line:
        return False
    # Lines containing DIRECTORY PATH data begin with '# with '
    if "# with " in line:
        return False
    return True


def isfloat(s):
    """True if s is convertible to float."""
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False


def are_files_same(file1, file2):
    """Assert that two files have (approximately) the same numerical
    values."""
    for f1_row, f2_row in zip(file1, file2):
        f1_arr = f1_row.split()
        f2_arr = f2_row.split()
        assert len(f1_arr) == len(f2_arr)
        for idx, _ in enumerate(f1_arr):
            if isfloat(f1_arr[idx]) and isfloat(f2_arr[idx]):
                assert np.isclose(float(f1_arr[idx]), float(f2_arr[idx]))
            else:
                assert f1_arr[idx] == f2_arr[idx]


def are_diffs_right(file1, file2, diff_file):
    """Assert that diff_file ordinate data is approximately file1
    ordinate data minus file2 ordinate data."""
    f1_data = loadData(file1)
    f2_data = loadData(file2)
    diff_data = loadData(diff_file)

    rmin = max(min(f1_data[:, 0]), min(f1_data[:, 1]))
    rmax = min(max(f2_data[:, 0]), max(f2_data[:, 1]))
    rnumsteps = max(
        len(f1_data[:, 0][(rmin <= f1_data[:, 0]) & (f1_data[:, 0] <= rmax)]),
        len(f2_data[:, 0][(rmin <= f2_data[:, 0]) & (f2_data[:, 0] <= rmax)]),
    )

    share_grid = np.linspace(rmin, rmax, rnumsteps)
    f1_interp = np.interp(share_grid, f1_data[:, 0], f1_data[:, 1])
    f2_interp = np.interp(share_grid, f2_data[:, 0], f2_data[:, 1])
    diff_interp = np.interp(share_grid, diff_data[:, 0], diff_data[:, 1])

    for idx, diff in enumerate(diff_interp):
        assert np.isclose(f1_interp[idx] - f2_interp[idx], diff)


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
                    actual = filter(ignore_path, gf)
                    expected = filter(ignore_path, tf)
                    are_files_same(actual, expected)

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
                    actual = filter(ignore_path, gf)
                    expected = filter(ignore_path, tf)
                    are_files_same(actual, expected)

    # Similar format as test_morph_outputs
    def test_morph_diff_outputs(self, setup, tmp_path):
        morph_file = self.testfiles[0]
        target_file = self.testfiles[-1]

        # Save multiple diff morphs
        tmp_diff = tmp_path.joinpath("diff")
        tmp_diff_name = tmp_diff.resolve().as_posix()

        (opts, pargs) = self.parser.parse_args(
            [
                "--multiple-targets",
                "--sort-by",
                "temperature",
                "-s",
                tmp_diff_name,
                "-n",
                "--save-names-file",
                tssf,
                "--diff",
            ]
        )
        pargs = [morph_file, testsequence_dir]
        multiple_targets(self.parser, opts, pargs, stdout_flag=False)

        # Save a single diff morph
        diff_name = "single_diff_morph.cgr"
        diff_file = tmp_diff.joinpath(diff_name)
        df_name = diff_file.resolve().as_posix()
        (opts, pargs) = self.parser.parse_args(["-s", df_name, "-n", "--diff"])
        pargs = [morph_file, target_file]
        single_morph(self.parser, opts, pargs, stdout_flag=False)

        # Check that the saved diff matches the morph minus target
        # Morphs are saved in testdata/testsequence/testsaving/succinct
        # Targets are stored in testdata/testsequence

        # Single morph diff
        morphed_file = test_saving_succinct / diff_name.replace(
            "diff", "succinct"
        )
        are_diffs_right(morphed_file, target_file, diff_file)

        # Multiple morphs diff
        diff_files = list((tmp_diff / "Morphs").iterdir())
        morphed_files = list((test_saving_succinct / "Morphs").iterdir())
        target_files = self.testfiles[1:]
        diff_files.sort()
        morphed_files.sort()
        target_files.sort()
        for idx, diff_file in enumerate(diff_files):
            are_diffs_right(morphed_files[idx], target_files[idx], diff_file)

    def test_morphsqueeze_outputs(self, setup, tmp_path):
        # The file squeeze_morph has a squeeze and stretch applied
        morph_file = testdata_dir / "squeeze_morph.cgr"
        target_file = testdata_dir / "squeeze_target.cgr"
        sqr = tmp_path / "squeeze_morph_result.cgr"
        sqr_name = sqr.resolve().as_posix()
        # Note that stretch and hshift should not be considered
        (opts, _) = self.parser.parse_args(
            [
                "--scale",
                "2",
                "--squeeze",
                # Ignore duplicate commas and trailing commas
                # Handle spaces and non-spaces
                "0,, ,-0.001, -0.0001,0.0001,",
                "--stretch",
                "1",
                "--hshift",
                "1",
                "-s",
                sqr_name,
                "-n",
                "--verbose",
            ]
        )
        pargs = [morph_file, target_file]
        single_morph(self.parser, opts, pargs, stdout_flag=False)

        # Check squeeze morph generates the correct output
        with open(sqr) as mf:
            with open(target_file) as tf:
                actual = filter(ignore_path, mf)
                expected = filter(ignore_path, tf)
                are_files_same(actual, expected)

    def test_morphfuncy_outputs(self, tmp_path):
        def quadratic(x, y, a0, a1, a2):
            return a0 + a1 * x + a2 * y**2

        r = np.linspace(0, 10, 101)
        gr = np.linspace(0, 10, 101)

        morph_arrays(
            np.array([r, gr]).T,
            np.array([r, quadratic(r, gr, 1, 2, 3)]).T,
            squeeze=[0, 0, 0],
            funcy=(quadratic, {"a0": 1.0, "a1": 2.0, "a2": 3.0}),
            apply=True,
            save=tmp_path / "funcy_target.cgr",
            verbose=True,
        )

        with open(testdata_dir.joinpath("funcy_target.cgr")) as tf:
            with open(tmp_path.joinpath("funcy_target.cgr")) as gf:
                actual = filter(ignore_path, gf)
                expected = filter(ignore_path, tf)
                are_files_same(actual, expected)
