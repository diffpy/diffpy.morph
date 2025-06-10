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
"""Class MorphResolutionDamping -- apply resolution broadening to the morph."""


import numpy

from diffpy.morph.morphs.morph import LABEL_RA, LABEL_RR, Morph


class MorphResolutionDamping(Morph):
    """Apply resolution damping and broadening to the morph.

    Configuration Variables
    -----------------------
    qdamp
        Peak dampening term.

    Notes
    -----
    See the PDFgui manual for how this is used.
    """

    # Define input output types
    summary = "Apply resolution damping to the morph"
    xinlabel = LABEL_RA
    yinlabel = LABEL_RR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_RR
    parnames = ["qdamp"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Apply a resolution damping."""
        Morph.morph(self, x_morph, y_morph, x_target, y_target)
        b = numpy.exp(-0.5 * (self.x_morph_in * self.qdamp) ** 2)
        self.y_morph_out *= b
        return self.xyallout


# End of class MorphResolutionDamping
