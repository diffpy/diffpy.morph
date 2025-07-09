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
"""Definition of morphs."""


from diffpy.morph.morphs.morph import Morph  # noqa: F401
from diffpy.morph.morphs.morphchain import MorphChain  # noqa: F401
from diffpy.morph.morphs.morphfuncxy import MorphFuncxy
from diffpy.morph.morphs.morphfuncy import MorphFuncy
from diffpy.morph.morphs.morphishape import MorphISphere, MorphISpheroid
from diffpy.morph.morphs.morphresolution import MorphResolutionDamping
from diffpy.morph.morphs.morphrgrid import MorphRGrid
from diffpy.morph.morphs.morphscale import MorphScale
from diffpy.morph.morphs.morphshape import MorphSphere, MorphSpheroid
from diffpy.morph.morphs.morphshift import MorphShift
from diffpy.morph.morphs.morphsmear import MorphSmear
from diffpy.morph.morphs.morphsqueeze import MorphSqueeze
from diffpy.morph.morphs.morphstretch import MorphStretch

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
    MorphSqueeze,
    MorphFuncy,
    MorphFuncxy,
]

# End of file
