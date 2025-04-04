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


"""class MorphStretch -- stretch the morph.
"""


import numpy

from diffpy.morph.morphs.morph import LABEL_GR, LABEL_RA, Morph


class MorphStretch(Morph):
    """Smear the morph function.

    This stretches (broadens) the morph.

    Configuration Variables
    -----------------------
    stretch
        The stretch factor to apply to y_morph_in.
        This is applied such that a feature at r is moved to r * (1 + stretch).
    """

    # Define input output types
    summary = "Stretch morph by desired amount"
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["stretch"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Resample arrays onto specified grid."""
        Morph.morph(self, x_morph, y_morph, x_target, y_target)
        if self.stretch == 0:
            return self.xyallout

        r = self.x_morph_in / (1.0 + self.stretch)
        self.y_morph_out = numpy.interp(r, self.x_morph_in, self.y_morph_in)
        return self.xyallout


# End of class MorphSmear
