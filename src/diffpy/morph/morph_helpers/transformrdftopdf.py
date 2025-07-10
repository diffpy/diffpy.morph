#!/usr/bin/env python
##############################################################################
#
# diffpy.morph   by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################
"""Class TransformXtalRDFtoPDF -- Transform crystal RDFs to PDFs."""


import numpy

from diffpy.morph.morphs.morph import LABEL_GR, LABEL_RA, LABEL_RR, Morph


class TransformXtalRDFtoPDF(Morph):
    """Transform crystal RDFs to PDFs.

    Converts both morph data and target data RDFs to PDFs.

    Configuration variables:

    baselineslope   --  The slope of the PDF baseline.  With the perfect scale,
                        the baseline slope is equal to -4*pi*rho0, where rho0
                        is the density of the crystalline sample.

    With s = baselineslope,
    G(r) = R(r) / r + r * s
    """

    # Define input output types
    summary = "Turn the PDF into the RDF for both the morph and target"
    xinlabel = LABEL_RA
    yinlabel = LABEL_RR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["baselineslope"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Return corresponding PDF given RDF."""
        Morph.morph(self, x_morph, y_morph, x_target, y_target)
        morph_baseline = self.baselineslope * self.x_morph_in
        target_baseline = self.baselineslope * self.x_target_in
        with numpy.errstate(divide="ignore", invalid="ignore"):
            self.y_target_out = (
                self.y_target_in / self.x_target_in + target_baseline
            )
        self.y_target_out[self.x_target_in == 0] = 0
        with numpy.errstate(divide="ignore", invalid="ignore"):
            self.y_morph_out = (
                self.y_morph_in / self.x_morph_in + morph_baseline
            )
        self.y_morph_out[self.x_morph_in == 0] = 0
        return self.xyallout


# End of class MorphScale
