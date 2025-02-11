#!/usr/bin/env python


import os

import numpy
import pytest

from diffpy.pdfmorph.morph_helpers.transformrdftopdf import (
    TransformXtalRDFtoPDF,
)

# useful variables
thisfile = locals().get("__file__", "file.py")
tests_dir = os.path.dirname(os.path.abspath(thisfile))
# testdata_dir = os.path.join(tests_dir, 'testdata')


class TestTransformXtalRDFtoPDF:
    @pytest.fixture
    def setup(self):
        self.x_morph = numpy.arange(0.01, 5, 0.01)
        self.y_morph = numpy.exp(-0.5 * (self.x_morph - 1.0) ** 2)
        self.x_target = numpy.arange(0.01, 5, 0.01)
        self.y_target = numpy.exp(-0.5 * (self.x_morph - 2.0) ** 2)
        return

    def test_transform(self, setup):
        """Check TransformXtalRDFtoPDF.morph()"""
        config = {"baselineslope": -1.0}
        transform = TransformXtalRDFtoPDF(config)

        x_morph, y_morph, x_target, y_target = transform(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        rdf1 = numpy.exp(-0.5 * (x_morph - 1.0) ** 2) / x_morph - x_morph
        rdf2 = numpy.exp(-0.5 * (x_target - 2.0) ** 2) / x_target - x_target
        assert numpy.allclose(rdf1, y_morph)
        assert numpy.allclose(rdf2, y_target)
        return


# End of class TestTransformXtalRDFtoPDF

if __name__ == "__main__":
    TestTransformXtalRDFtoPDF()

# End of file
