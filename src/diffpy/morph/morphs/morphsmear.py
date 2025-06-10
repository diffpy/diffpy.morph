#!/usr/bin/env python
##############################################################################
#
# diffpy.morph      by DANSE Diffraction group
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
"""Class MorphSmear -- smear the morph."""


import numpy

from diffpy.morph.morphs.morph import LABEL_RA, LABEL_RR, Morph


class MorphSmear(Morph):
    """Smear the morph function.

    This smears (broadens) the peaks of the morph.  Note that this operates
    on the RDF. Inputs are not automatically converted to the RDF.

    Configuration Variables
    -----------------------
    smear
        The smear factor to apply to y_morph_in.
    """

    # Define input output types
    summary = "Smear morph by desired amount"
    xinlabel = LABEL_RA
    yinlabel = LABEL_RR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_RR
    parnames = ["smear"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Resample arrays onto specified grid."""
        Morph.morph(self, x_morph, y_morph, x_target, y_target)

        if self.smear == 0:
            return self.xyallout

        # The Gaussian to convolute with. No need to normalize, we'll do that
        # later.
        r = self.x_morph_in
        rr = self.y_morph_in
        r0 = r[len(r) // 2]
        gaussian = numpy.exp(-0.5 * ((r - r0) / self.smear) ** 2)

        # Get the full convolution
        c = numpy.convolve(rr, gaussian, mode="full")
        # Find the centroid of the RDF, we don't want this to change from the
        # convolution.
        x1 = numpy.arange(len(rr), dtype=float)
        c1idx = numpy.sum(rr * x1) / sum(rr)
        # Find the centroid of the convolution
        xc = numpy.arange(len(c), dtype=float)
        ccidx = numpy.sum(c * xc) / sum(c)
        # Interpolate the convolution such that the centroids line up. This
        # uses linear interpolation.
        shift = ccidx - c1idx
        x1 += shift
        rrbroad = numpy.interp(x1, xc, c)

        # Normalize so that the integrated magnitude of the RDF doesn't change.
        rrbroad /= sum(gaussian)

        self.y_morph_out = rrbroad

        return self.xyallout


# End of class MorphSmear
