#!/usr/bin/env python

##############################################################################
#
# diffpy.pdfmorph   by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Andrew Yang
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################

from diffpy.pdfmorph.pdfmorphapp import create_option_parser, single_morph


def pdfmorph(file1, file2, stdout_flag=False, **kwargs):
    """Run PDFmorph at Python level.

    Parameters
    ----------
    file1: str
        Path-like object to the file to be morphed.
    file2: str
        Path-like object to the target file.
    kwargs: dict
        See the PDFmorph manual for options. Multiple morphs not supported.

    Returns
    -------
    dict:
        Summary of morphs.
    x: array-like
        The r grid after the morph is applied.
    y: array-like
        The g(r) values after the morph is applied.
    """

    parser = create_option_parser()

    inputs = []
    for key, value in kwargs.items():
        inputs.append(f"--{key}")
        inputs.append(f"{value}")
    (opts, pargs) = parser.parse_args(inputs)
    pargs = [file1, file2]

    return single_morph(parser, opts, pargs, stdout_flag=stdout_flag, return_morph=True)
