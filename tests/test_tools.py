#!/usr/bin/env python

"""Unit tests for tools.py."""


import os
from pathlib import Path

import numpy
import pytest

import diffpy.morph.tools as tools

# useful variables
thisfile = locals().get("__file__", "file.py")
tests_dir = os.path.dirname(os.path.abspath(thisfile))
testdata_dir = os.path.join(tests_dir, "testdata")
testsequence_dir = os.path.join(testdata_dir, "testsequence")


##############################################################################
class TestTools:
    @pytest.fixture
    def setup(self):
        morph_file = os.path.join(testdata_dir, "nickel_ss0.01.cgr")
        self.x_morph, self.y_morph = numpy.loadtxt(morph_file, unpack=True)
        self.rho0 = 0.0917132
        return

    def test_estimateBaselineSlope(self, setup):
        """Check estimateBaselineSlope() using calculated data."""
        slope = tools.estimateBaselineSlope(self.x_morph, self.y_morph)
        slopecalc = -4 * numpy.pi * self.rho0
        assert numpy.allclose(slopecalc, slope, 1e-2)
        return

    def test_estimateScale(self, setup):
        """Check estimateScale() using calculated data."""
        import random

        x = random.random()
        scale = tools.estimateScale(self.y_morph, x * self.y_morph)
        assert x, scale
        return

    def test_nn_value(self, setup):
        import random

        # Values with 6 and 7 decimals (limit of assertAlmostEqual)
        test_values = [10.0000001, 10.00000001, 0.9999999, 0.99999999]

        # Random values
        for i in range(100):
            test_values.append(random.uniform(0, 65535))

        # Check positive and negative
        for value in test_values:
            pytest.approx(tools.nn_value(value, name=None), abs(value))
            pytest.approx(tools.nn_value(-value, name=None), abs(-value))

    def test_field_sort(self, setup):
        sequence_files = [file for file in Path(testsequence_dir).iterdir()]
        to_remove = []
        for file in sequence_files:
            if file.is_dir():
                to_remove.append(file)
        for d in to_remove:
            sequence_files.remove(d)
        absolute_sf = []
        for file in sequence_files:
            absolute_sf.append(Path(testsequence_dir) / file.name)

        # Fisher-Yates randomization
        import random

        length = len(absolute_sf)
        for i in range(length - 1, 0, -1):
            j = random.randint(0, i)
            absolute_sf[i], absolute_sf[j] = absolute_sf[j], absolute_sf[i]

        # Prepare and run through field_sort by temperature
        path_sequence = []
        for file in absolute_sf:
            path_sequence.append(Path(file).absolute())
        sorted_path_sequence, fvs = tools.field_sort(
            path_sequence, "temperature", get_field_values=True
        )
        sorted_sequence = []
        for path in sorted_path_sequence:
            print(path)
            sorted_sequence.append(path.name)

        # Temperature sort should produce same result as alphanumerical if
        # leading character is removed
        sequence_files.sort(key=lambda entry: entry.name[2:])
        assert [file.name for file in sequence_files] == sorted_sequence

        # Check temperatures are correct
        assert fvs == [174, 180, 186, 192, 198, 204, 210]

        # Now reverse the sort
        reversed_path_sequence = tools.field_sort(
            path_sequence, "temperature", reverse=True
        )
        reversed_sequence = []
        for path in reversed_path_sequence:
            reversed_sequence.append(path.name)

        # Reversed sort should match alphanumerical sort
        sequence_files.sort()
        assert [file.name for file in sequence_files] == reversed_sequence

        # Check we get the same sequence when we load header information from
        # a serial file
        serial_file = os.path.join(
            testdata_dir, "testsequence_serialfile.json"
        )
        metadata_path_sequence = tools.field_sort(
            path_sequence, "temperature", serfile=serial_file, reverse=True
        )
        metadata_sequence = []
        for path in metadata_path_sequence:
            metadata_sequence.append(path.name)
        assert [file.name for file in sequence_files] == metadata_sequence

        # Check error thrown when field does not exist
        with pytest.raises(KeyError):
            tools.field_sort(path_sequence, "non_existing_field")

    def test_get_values_from_dictionary_collection(self):
        # Four dictionaries
        dict1 = {"target": "this"}
        dict2 = {"target": "forms", "false": "this"}
        dict3 = {"false target": "does", "target": "a"}
        dict4 = {"target": "sentence", "target2": "not"}

        # Target sentence
        target_list = ["this", "forms", "a", "sentence"]

        # Various iterable collections of dictionaries
        # No sets since dictionaries are not hashable
        d_type = {"d1": dict1, "d2": dict2, "d3": dict3, "d4": dict4}
        l_type = [dict1, dict2, dict3, dict4]
        t_type = (dict1, dict2, dict3, dict4)
        npa_type = numpy.array(l_type)
        all_types = [d_type, l_type, t_type, npa_type]

        # Check get_values_from_dictionary_collection output gives target
        for collection_type in all_types:
            assert (
                tools.get_values_from_dictionary_collection(
                    collection_type, target_key="target"
                )
                == target_list
            )
