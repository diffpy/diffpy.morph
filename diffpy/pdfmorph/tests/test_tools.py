#!/usr/bin/env python

"""Unit tests for tools.py
"""


import os
import unittest
import pytest
import numpy

from pathlib import Path

# useful variables
thisfile = locals().get('__file__', 'file.py')
tests_dir = os.path.dirname(os.path.abspath(thisfile))
testdata_dir = os.path.join(tests_dir, 'testdata')
testsequence_dir = os.path.join(testdata_dir, 'testsequence')

import diffpy.pdfmorph.tools as tools


##############################################################################
class TestTools(unittest.TestCase):
    def setUp(self):
        morph_file = os.path.join(testdata_dir, "nickel_ss0.01.cgr")
        self.x_morph, self.y_morph = numpy.loadtxt(morph_file, unpack=True)
        self.rho0 = 0.0917132
        return

    def test_estimateBaselineSlope(self):
        """check estimateBaselineSlope() using calculated data"""
        slope = tools.estimateBaselineSlope(self.x_morph, self.y_morph)
        slopecalc = -4 * numpy.pi * self.rho0
        self.assertTrue(numpy.allclose(slopecalc, slope, 1e-2))
        return

    def test_estimateScale(self):
        """check estimateScale() using calculated data"""
        import random

        x = random.random()
        scale = tools.estimateScale(self.y_morph, x * self.y_morph)
        self.assertAlmostEqual(x, scale)
        return

    def test_nn_value(self):
        import random

        # Values with 6 and 7 decimals (limit of assertAlmostEqual)
        test_values = [10.0000001, 10.00000001, 0.9999999, 0.99999999]

        # Random values
        for i in range(100):
            test_values.append(random.uniform(0, 65535))

        # Check positive and negative
        for value in test_values:
            self.assertAlmostEqual(tools.nn_value(value, name=None), abs(value))
            self.assertAlmostEqual(tools.nn_value(-value, name=None), abs(-value))

    def test_field_sort(self):
        sequence_files = [*os.listdir(testsequence_dir)]
        absolute_sf = []
        for file in sequence_files:
            absolute_sf.append(os.path.join(testsequence_dir, file))

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
        sorted_path_sequence, fvs = tools.field_sort(path_sequence, "temperature", get_field_values=True)
        sorted_sequence = []
        for path in sorted_path_sequence:
            print(path)
            sorted_sequence.append(path.name)

        # Temperature sort should produce same result as alphanumerical if leading character is removed
        sequence_files.sort(key=lambda entry: entry[2:])
        assert sequence_files == sorted_sequence

        # Check temperatures are correct
        assert fvs == [174, 180, 186, 192, 198, 204, 210]

        # Now reverse the sort
        reversed_path_sequence = tools.field_sort(path_sequence, "temperature", reverse=True)
        reversed_sequence = []
        for path in reversed_path_sequence:
            reversed_sequence.append(path.name)

        # Reversed sort should match alphanumerical sort
        sequence_files.sort()
        assert sequence_files == reversed_sequence

        # Check we get the same sequence when we load header information from a serial file
        serial_file = os.path.join(testdata_dir, "testsequence_serialfile.json")
        metadata_path_sequence = tools.field_sort(path_sequence, "temperature", serfile=serial_file, reverse=True)
        metadata_sequence = []
        for path in metadata_path_sequence:
            metadata_sequence.append(path.name)
        assert sequence_files == metadata_sequence

        # Check error thrown when field does not exist
        with pytest.raises(KeyError):
            tools.field_sort(path_sequence, "non_existing_field")


# End of class TestRoutines

if __name__ == '__main__':
    unittest.main()

# End of file
