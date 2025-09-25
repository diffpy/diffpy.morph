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


class MorphRGrid(Morph):
    """Resample to specified r-grid.

    This resamples both the morph and target arrays to be on the
    specified grid.

    Configuration Variables
    -----------------------
    xmin
        The lower-bound on the x-range.
    xmax
        The upper-bound on the x-range (exclusive within tolerance of 1e-8).
    xstep
        The x-spacing.

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
    parnames = ["xmin", "xmax", "xstep"]

    # Define xmin xmax holders for adaptive x-grid refinement
    # Without these, the program r-grid can only decrease in interval size
    xmin_origin = None
    xmax_origin = None
    xstep_origin = None

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Resample arrays onto specified grid."""
        if self.xmin is not None:
            self.xmin_origin = self.xmin
        if self.xmax is not None:
            self.xmax_origin = self.xmax
        if self.xstep is not None:
            self.xstep_origin = self.xstep

        Morph.morph(self, x_morph, y_morph, x_target, y_target)
        xmininc = max(min(self.x_target_in), min(self.x_morph_in))
        x_step_target = (max(self.x_target_in) - min(self.x_target_in)) / (
            len(self.x_target_in) - 1
        )
        x_step_morph = (max(self.x_morph_in) - min(self.x_morph_in)) / (
            len(self.x_morph_in) - 1
        )
        xstepinc = max(x_step_target, x_step_morph)
        xmaxinc = min(
            max(self.x_target_in) + x_step_target,
            max(self.x_morph_in) + x_step_morph,
        )
        if self.xmin_origin is None or self.xmin_origin < xmininc:
            self.xmin = xmininc
        if self.xmax_origin is None or self.xmax_origin > xmaxinc:
            self.xmax = xmaxinc
        if self.xstep_origin is None or self.xstep_origin < xstepinc:
            self.xstep = xstepinc
        # roundoff tolerance for selecting bounds on arrays.
        epsilon = self.xstep / 2
        # Make sure that xmax is exclusive
        self.x_morph_out = numpy.arange(
            self.xmin, self.xmax - epsilon, self.xstep
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
