#!/usr/bin/env python


import os

import numpy
import pytest

from diffpy.pdfmorph.morph_helpers.transformpdftordf import (
    TransformXtalPDFtoRDF,
)

# useful variables
thisfile = locals().get("__file__", "file.py")
tests_dir = os.path.dirname(os.path.abspath(thisfile))
# testdata_dir = os.path.join(tests_dir, 'testdata')


class TestTransformXtalPDFtoRDF:
    @pytest.fixture
    def setup(self):
        self.x_morph = numpy.arange(0.01, 5, 0.01)
        self.y_morph = (
            numpy.exp(-0.5 * (self.x_morph - 1.0) ** 2) / self.x_morph
            - self.x_morph
        )
        self.x_target = numpy.arange(0.01, 5, 0.01)
        self.y_target = (
            numpy.exp(-0.5 * (self.x_morph - 2.0) ** 2) / self.x_morph
            - self.x_morph
        )
        return

    def test_transform(self, setup):
        """Check TransformXtalPDFtoRDF.morph()"""
        config = {"baselineslope": -1.0}
        transform = TransformXtalPDFtoRDF(config)

        x_morph, y_morph, x_target, y_target = transform(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )

        rdf1 = numpy.exp(-0.5 * (x_morph - 1.0) ** 2)
        rdf2 = numpy.exp(-0.5 * (x_target - 2.0) ** 2)
        assert numpy.allclose(rdf1, y_morph)
        assert numpy.allclose(rdf2, y_target)
        return


# End of class TestTransformXtalPDFtoRDF

if __name__ == "__main__":
    TestTransformXtalPDFtoRDF()

# End of file
