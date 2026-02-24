#!/usr/bin/env python

from pathlib import Path

import numpy as np
import pytest

from diffpy.morph.morphapp import (
    create_option_parser,
    multiple_targets,
    single_morph,
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
    def setup_parser(self):
        self.parser = create_option_parser()

    @pytest.fixture
    def setup_morphsequence(self):
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

    def test_parser_numerical(self, setup_parser):
        renamed_dests = {"slope": "baselineslope"}

        # Check values parsed correctly
        n_names = [
            "--xmin",
            "--xmax",
            "--scale",
            "--smear",
            "--stretch",
            "--slope",
            "--qdamp",
        ]
        n_values = [
            "2.5",
            "40",
            "2.1",
            "-0.8",
            "0.0000005",
            "-0.0000005",
            ".00000003",
        ]
        n_names.extend(
            [
                "--radius",
                "--pradius",
                "--iradius",
                "--ipradius",
                "--pmin",
                "--pmax",
            ]
        )
        n_values.extend(["+0.5", "-0.2", "+.3", "-.1", "2.5", "40"])
        n_names.extend(["--lwidth", "--maglim", "--mag"])
        n_values.extend(["1.6", "50", "5"])
        n_total = len(n_names)
        n_input = []
        for idx in range(n_total):
            n_input.append(n_names[idx])
            n_input.append(n_values[idx])
        n_input.append("leftover")  # One leftover
        n_opts, n_args = self.parser.parse_args(n_input)
        n_opts_dict = vars(n_opts)
        for idx in range(n_total):
            n_parsed_name = n_names[idx][2:]
            n_parsed_val = n_opts_dict.get(n_parsed_name)
            if n_parsed_val is None:
                assert (
                    n_parsed_name in renamed_dests
                )  # Ensure .get() failed due to destination renaming
                n_parsed_name = renamed_dests.get(n_parsed_name)
                n_parsed_val = n_opts_dict.get(n_parsed_name)
            assert isinstance(n_parsed_val, float)  # Check if value is a float
            assert n_parsed_val == float(
                n_values[idx]
            )  # Check correct value parsed
        assert len(n_args) == 1  # Check one leftover

    def test_parser_errors(self, capsys, setup_parser):
        # ###Basic tests for any variety of morphing###

        # Ensure only two pargs given for morphing
        (opts, pargs) = self.parser.parse_args(["toofewfiles"])
        with pytest.raises(TypeError) as excinfo:
            single_morph(self.parser, opts, pargs, stdout_flag=False)
        assert "You must supply MORPHFILE and TARGETFILE." in str(
            excinfo.value
        )
        with pytest.raises(TypeError) as excinfo:
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)
        assert "You must supply a FILE and DIRECTORY." in str(excinfo.value)
        (opts, pargs) = self.parser.parse_args(["too", "many", "files"])
        with pytest.raises(TypeError) as excinfo:
            single_morph(self.parser, opts, pargs, stdout_flag=False)
        assert (
            "Too many arguments. Make sure you only supply MORPHFILE and "
            "TARGETFILE." in str(excinfo.value)
        )
        with pytest.raises(TypeError) as excinfo:
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)
        assert (
            "Too many arguments. You must only supply a FILE and a DIRECTORY."
            in str(excinfo.value)
        )

        # Make sure xmax greater than xmin
        (opts, pargs) = self.parser.parse_args(
            [f"{nickel_PDF}", f"{nickel_PDF}", "--xmin", "10", "--xmax", "1"]
        )
        with pytest.raises(ValueError) as excinfo:
            single_morph(self.parser, opts, pargs, stdout_flag=False)
        assert "xmin must be less than xmax" in str(excinfo.value)

        # ###Tests exclusive to multiple morphs###
        # Make sure we save to a directory that exists
        # (user must create the directory if non-existing)
        (opts, pargs) = self.parser.parse_args(
            [
                f"{nickel_PDF}",
                f"{nickel_PDF}",
                "-s",
                "/nonexisting_directory/no_way_this_exists/nonexisting_path",
            ]
        )
        with pytest.raises(FileNotFoundError) as excinfo:
            single_morph(self.parser, opts, pargs, stdout_flag=False)
        assert "Unable to save to designated location." in str(excinfo.value)
        with pytest.raises(NotADirectoryError) as excinfo:
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)
        assert "is not a directory." in str(excinfo.value)

        # Ensure first parg is a FILE and second parg is a DIRECTORY
        (opts, pargs) = self.parser.parse_args(
            [f"{nickel_PDF}", f"{nickel_PDF}"]
        )
        with pytest.raises(NotADirectoryError) as excinfo:
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)
        (opts, pargs) = self.parser.parse_args(
            [f"{testsequence_dir}", f"{testsequence_dir}"]
        )
        assert "is not a directory." in str(excinfo.value)
        with pytest.raises(FileNotFoundError) as excinfo:
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)
        assert "is not a file." in str(excinfo.value)

        # Try sorting by non-existing field
        (opts, pargs) = self.parser.parse_args(
            [f"{nickel_PDF}", f"{testsequence_dir}", "--sort-by", "fake_field"]
        )
        with pytest.raises(KeyError) as excinfo:
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)
        assert "The requested field is missing from a file header." in str(
            excinfo.value
        )
        (opts, pargs) = self.parser.parse_args(
            [
                f"{nickel_PDF}",
                f"{testsequence_dir}",
                "--sort-by",
                "fake_field",
                "--serial-file",
                f"{serial_JSON}",
            ]
        )
        with pytest.raises(KeyError) as excinfo:
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)
        assert (
            "The requested field was not found in the metadata file."
            in str(excinfo.value)
        )

        # Try plotting an unknown parameter
        (opts, pargs) = self.parser.parse_args(
            [
                f"{nickel_PDF}",
                f"{testsequence_dir}",
                "--plot-parameter",
                "unknown",
            ]
        )
        with pytest.raises(KeyError) as excinfo:
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)
        assert "Cannot find specified plot parameter. No plot shown." in str(
            excinfo.value
        )

        # Try plotting an unrefined parameter
        (opts, pargs) = self.parser.parse_args(
            [
                f"{nickel_PDF}",
                f"{testsequence_dir}",
                "--plot-parameter",
                "stretch",
            ]
        )
        with pytest.raises(ValueError) as excinfo:
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)
        assert (
            "The plot parameter is missing values for at "
            "least one morph and target pair. "
            "No plot shown." in str(excinfo.value)
        )

        # Pass a non-float list to squeeze
        (opts, pargs) = self.parser.parse_args(
            [
                f"{nickel_PDF}",
                f"{nickel_PDF}",
                "--squeeze",
                "1,a,0",
            ]
        )
        with pytest.raises(ValueError) as excinfo:
            single_morph(self.parser, opts, pargs, stdout_flag=False)
        assert "a could not be converted to float." in str(excinfo.value)

    def test_morphsequence(self, setup_morphsequence):
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

        # Run multiple single morphs
        single_results = {}
        morph_file = self.testfiles[0]
        for target_file in self.testfiles[1:]:
            pargs = [morph_file, target_file]
            # store in same format of dictionary as multiple_targets
            single_results.update(
                {
                    target_file.name: single_morph(
                        self.parser, opts, pargs, stdout_flag=False
                    )
                }
            )
        pargs = [morph_file, testsequence_dir]

        # Run a morph sequence
        sequence_results = multiple_targets(
            self.parser, opts, pargs, stdout_flag=False
        )

        # Compare results
        assert sequence_results == single_results

        # Check using a serial file produces the same result
        s_file = tssf.resolve().as_posix()
        (opts, pargs) = self.parser.parse_args(
            [
                "--scale",
                "1",
                "--stretch",
                "0",
                "-n",
                "--sort-by",
                "temperature",
                "--serial-file",
                s_file,
            ]
        )
        pargs = [morph_file, testsequence_dir]
        s_sequence_results = multiple_targets(
            self.parser, opts, pargs, stdout_flag=False
        )
        assert s_sequence_results == sequence_results

    def test_morphsmear(self, setup_parser, tmp_path):
        def gaussian(x, mu, sigma):
            return np.exp(-((x - mu) ** 2) / (2 * sigma**2)) / (
                sigma * np.sqrt(2 * np.pi)
            )

        # Generate the test files
        x_grid = np.linspace(1, 101, 1001)
        # Gaussian with STD 3 (morph)
        g2 = gaussian(x_grid, 51, 3)
        mf = tmp_path / "morph.txt"
        with open(mf, "w") as f:
            np.savetxt(f, np.array([x_grid, g2]).T)
        # Gaussian with STD 5 (target)
        g3 = gaussian(x_grid, 51, 5)
        tf = tmp_path / "target.txt"
        with open(tf, "w") as f:
            np.savetxt(f, np.array([x_grid, g3]).T)
        # Gaussian with STD 3 and baseline slope -0.5 (PDF morph)
        g2_bl = gaussian(x_grid, 51, 3) / x_grid - 0.5 * x_grid
        pmf = tmp_path / "pdf_morph.txt"
        with open(pmf, "w") as f:
            np.savetxt(f, np.array([x_grid, g2_bl]).T)
        # Gaussian with STD 5 with baseline slope -0.5 (PDF target)
        g3_bl = gaussian(x_grid, 51, 5) / x_grid - 0.5 * x_grid
        ptf = tmp_path / "pdf_target.txt"
        with open(ptf, "w") as f:
            np.savetxt(f, np.array([x_grid, g3_bl]).T)

        # No PDF smear (should not activate baseline slope)
        (opts, _) = self.parser.parse_args(
            [
                "--smear",
                "1",
                "-n",
            ]
        )
        pargs = [mf, tf]
        smear_results = single_morph(
            self.parser, opts, pargs, stdout_flag=False
        )
        # Variances add, and 3^2+4^2=5^2
        assert pytest.approx(abs(smear_results["smear"])) == 4.0
        assert pytest.approx(smear_results["Rw"]) == 0.0

        # PDF-specific smear (should activate baseline slope)
        (opts, _) = self.parser.parse_args(
            [
                "--smear",
                "100",
                "--smear-pdf",
                "1",
                "-n",
            ]
        )
        pargs = [pmf, ptf]
        pdf_smear_results = single_morph(
            self.parser, opts, pargs, stdout_flag=False
        )
        assert pytest.approx(abs(pdf_smear_results["smear"])) == 4.0
        assert pytest.approx(pdf_smear_results["Rw"]) == 0.0
