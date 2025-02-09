#!/usr/bin/env python

from pathlib import Path

import pytest

from diffpy.pdfmorph.pdfmorphapp import (
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

testsaving_dir = testdata_dir.joinpath("testsaving")
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
            "--rmin",
            "--rmax",
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

    def test_parser_systemexits(self, setup_parser):
        # ###Basic tests for any variety of morphing###

        # Ensure only two pargs given for morphing
        (opts, pargs) = self.parser.parse_args(["toofewfiles"])
        with pytest.raises(SystemExit):
            single_morph(self.parser, opts, pargs, stdout_flag=False)
        with pytest.raises(SystemExit):
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)
        (opts, pargs) = self.parser.parse_args(["too", "many", "files"])
        with pytest.raises(SystemExit):
            single_morph(self.parser, opts, pargs, stdout_flag=False)
        with pytest.raises(SystemExit):
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)

        # Make sure rmax greater than rmin
        (opts, pargs) = self.parser.parse_args(
            [f"{nickel_PDF}", f"{nickel_PDF}", "--rmin", "10", "--rmax", "1"]
        )
        with pytest.raises(SystemExit):
            single_morph(self.parser, opts, pargs, stdout_flag=False)

        # ###Tests exclusive to multiple morphs###
        # Make sure we save to a directory that exists (user must create the directory if non-existing)
        (opts, pargs) = self.parser.parse_args(
            [
                f"{nickel_PDF}",
                f"{nickel_PDF}",
                "-s",
                "/nonexisting_directory/no_way_this_exists/nonexisting_path",
            ]
        )
        with pytest.raises(SystemExit):
            single_morph(self.parser, opts, pargs, stdout_flag=False)
        with pytest.raises(SystemExit):
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)

        # Ensure first parg is a FILE and second parg is a DIRECTORY
        (opts, pargs) = self.parser.parse_args(
            [f"{nickel_PDF}", f"{nickel_PDF}"]
        )
        with pytest.raises(SystemExit):
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)
        (opts, pargs) = self.parser.parse_args(
            [f"{testsequence_dir}", f"{testsequence_dir}"]
        )
        with pytest.raises(SystemExit):
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)

        # Try sorting by non-existing field
        (opts, pargs) = self.parser.parse_args(
            [f"{nickel_PDF}", f"{testsequence_dir}", "--sort-by", "fake_field"]
        )
        with pytest.raises(SystemExit):
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)
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
        with pytest.raises(SystemExit):
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)

        # Try plotting an unknown parameter
        (opts, pargs) = self.parser.parse_args(
            [
                f"{nickel_PDF}",
                f"{testsequence_dir}",
                "--plot-parameter",
                "unknown",
            ]
        )
        with pytest.raises(SystemExit):
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)

        # Try plotting an unrefined parameter
        (opts, pargs) = self.parser.parse_args(
            [
                f"{nickel_PDF}",
                f"{testsequence_dir}",
                "--plot-parameter",
                "stretch",
            ]
        )
        with pytest.raises(SystemExit):
            multiple_targets(self.parser, opts, pargs, stdout_flag=False)

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


if __name__ == "__main__":
    TestApp()
