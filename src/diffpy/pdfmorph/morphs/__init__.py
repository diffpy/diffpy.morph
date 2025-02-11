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
"""Definition of morphs."""


from diffpy.pdfmorph.morphs.morph import Morph  # noqa: F401
from diffpy.pdfmorph.morphs.morphchain import MorphChain  # noqa: F401
from diffpy.pdfmorph.morphs.morphishape import MorphISphere, MorphISpheroid
from diffpy.pdfmorph.morphs.morphresolution import MorphResolutionDamping
from diffpy.pdfmorph.morphs.morphrgrid import MorphRGrid
from diffpy.pdfmorph.morphs.morphscale import MorphScale
from diffpy.pdfmorph.morphs.morphshape import MorphSphere, MorphSpheroid
from diffpy.pdfmorph.morphs.morphshift import MorphShift
from diffpy.pdfmorph.morphs.morphsmear import MorphSmear
from diffpy.pdfmorph.morphs.morphstretch import MorphStretch

# List of morphs
morphs = [
    MorphRGrid,
    MorphScale,
    MorphStretch,
    MorphSmear,
    MorphSphere,
    MorphSpheroid,
    MorphISphere,
    MorphISpheroid,
    MorphResolutionDamping,
    MorphShift,
]

# End of file
