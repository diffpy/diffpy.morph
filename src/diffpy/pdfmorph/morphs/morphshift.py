#!/usr/bin/env python
##############################################################################
#
# diffpy.pdfmorph   by DANSE Diffraction group
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


"""class MorphShift -- shift the morph
"""


import numpy

from diffpy.pdfmorph.morphs.morph import LABEL_GR, LABEL_RA, Morph


class MorphShift(Morph):
    """Shift the morph.

    Configuration Variables
    -----------------------
    vshift
        The vertical shift to apply to the morph.
    hshift
        The horizontal shift to apply to the morph.

    Note that a horizontal shift may cause edge effects, since the morph does
    not know what lies beyond the edge of the signals.
    """

    # Define input output types
    summary = "Shift morph by specified amount"
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["hshift", "vshift"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Apply the shifts."""
        try:
            hshift = self.hshift
        except AttributeError:
            hshift = 0
        try:
            vshift = self.vshift
        except AttributeError:
            vshift = 0

        Morph.morph(self, x_morph, y_morph, x_target, y_target)
        r = self.x_morph_in - hshift
        self.y_morph_out = numpy.interp(r, self.x_morph_in, self.y_morph_in)
        self.y_morph_out += vshift
        return self.xyallout


# End of class MorphShift
