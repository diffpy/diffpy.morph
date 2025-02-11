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
"""Class MorphISphere -- apply inverse spherical shape function class
MorphISpheroid -- apply inverse spheroidal shape function."""


import numpy

from diffpy.pdfmorph.morphs.morph import LABEL_GR, LABEL_RA, Morph
from diffpy.pdfmorph.morphs.morphshape import _sphericalCF, _spheroidalCF


class MorphISphere(Morph):
    """Apply inverse spherical characteristic function to the morph.

    Configuration Variables
    -----------------------
    iradius
        The radius of the sphere.
    """

    # Define input output types
    summary = "Apply inverse spherical characteristic function to morph"
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["iradius"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Apply a scale factor."""
        Morph.morph(self, x_morph, y_morph, x_target, y_target)
        f = _sphericalCF(x_morph, 2 * self.iradius)
        with numpy.errstate(divide="ignore", invalid="ignore"):
            self.y_morph_out /= f
        self.y_morph_out[f == 0] = 0
        return self.xyallout


# End of class MorphISphere


class MorphISpheroid(Morph):
    """Apply inverse spherical characteristic function to the morph.

    Configuration Variables
    -----------------------
    iradius
        The equatorial radius of the spheroid.
    ipradius
        The polar radius of the spheroid.
    """

    # Define input output types
    summary = "Apply inverse spheroidal characteristic function to morph"
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["iradius", "ipradius"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Apply a scale factor."""
        Morph.morph(self, x_morph, y_morph, x_target, y_target)
        f = _spheroidalCF(x_morph, self.iradius, self.ipradius)
        with numpy.errstate(divide="ignore", invalid="ignore"):
            self.y_morph_out /= f
        self.y_morph_out[f == 0] = 0
        return self.xyallout


# End of class MorphSpheroid
