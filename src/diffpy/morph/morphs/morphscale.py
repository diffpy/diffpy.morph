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
"""Class MorphScale -- scale the morph data."""


from diffpy.morph.morphs.morph import LABEL_GR, LABEL_RA, Morph


class MorphScale(Morph):
    """Scale the morph.

    This scales the morph.

    Configuration Variables
    -----------------------
    scale
        The scale to apply to y_target_in.

    Returns
    -------
    No return.
    """

    # Define input output types
    summary = "Scale morph by specified amount"
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["scale"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Apply a scale factor."""
        Morph.morph(self, x_morph, y_morph, x_target, y_target)
        self.y_morph_out *= self.scale
        return self.xyallout


# End of class MorphScale
