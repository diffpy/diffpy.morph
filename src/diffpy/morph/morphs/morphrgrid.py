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
"""Class MorphRGrid -- put morph and target on desired grid."""


import numpy

from diffpy.morph.morphs.morph import LABEL_GR, LABEL_RA, Morph

# roundoff tolerance for selecting bounds on arrays.
epsilon = 1e-8


class MorphRGrid(Morph):
    """Resample to specified r-grid.

    This resamples both the morph and target arrays to be on the
    specified grid.

    Configuration Variables
    -----------------------
    rmin
        The lower-bound on the r-range.
    rmax
        The upper-bound on the r-range (exclusive within tolerance of 1e-8).
    rstep
        The r-spacing.

    Notes
    -----
        If any of these is not defined or outside the bounds of the input
        arrays, then it will be taken to be the most inclusive value from the
        input arrays. These modified values will be stored as the above
        attributes.
    """

    # Define input output types
    summary = "Interplolate data onto specified grid"
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["rmin", "rmax", "rstep"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Resample arrays onto specified grid."""
        Morph.morph(self, x_morph, y_morph, x_target, y_target)
        rmininc = max(self.x_target_in[0], self.x_morph_in[0])
        r_step_target = (self.x_target_in[-1] - self.x_target_in[0]) / (
            len(self.x_target_in) - 1
        )
        r_step_morph = (self.x_morph_in[-1] - self.x_morph_in[0]) / (
            len(self.x_morph_in) - 1
        )
        rstepinc = max(r_step_target, r_step_morph)
        rmaxinc = min(
            self.x_target_in[-1] + r_step_target,
            self.x_morph_in[-1] + r_step_morph,
        )
        if self.rmin is None or self.rmin < rmininc:
            self.rmin = rmininc
        if self.rmax is None or self.rmax > rmaxinc:
            self.rmax = rmaxinc
        if self.rstep is None or self.rstep < rstepinc:
            self.rstep = rstepinc
        # Make sure that rmax is exclusive
        self.x_morph_out = numpy.arange(
            self.rmin, self.rmax - epsilon, self.rstep
        )
        self.y_morph_out = numpy.interp(
            self.x_morph_out, self.x_morph_in, self.y_morph_in
        )
        self.x_target_out = self.x_morph_out.copy()
        self.y_target_out = numpy.interp(
            self.x_target_out, self.x_target_in, self.y_target_in
        )
        return self.xyallout


# End of class MorphRGrid
