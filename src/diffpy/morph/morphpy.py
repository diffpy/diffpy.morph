#!/usr/bin/env python

from pathlib import Path

from diffpy.morph.morphapp import create_option_parser, single_morph, multiple_targets, multiple_morphs


def morph(file1, file2, **kwargs):
    """Run diffpy.morph at Python level.

    Parameters
    ----------
    file1: str
        Path-like object to the file to be morphed.
    file2: str
        Path-like object to the target file.
    kwargs: dict
        See the diffpy.morph manual for options.

    Returns
    -------
    dict:
        Summary of morphs.
    """

    parser = create_option_parser()

    inputs = []
    for key, value in kwargs.items():
        inputs.append(f"--{key}")
        inputs.append(f"{value}")
    (opts, pargs) = parser.parse_args(inputs)
    pargs = [file1, file2]

    return single_morph(parser, opts, pargs)


def morph_multiple_targets(file, dir, **kwargs):
    """Run diffpy.morph with multiple targets at Python level.

        Parameters
        ----------
        file1: str
            Path-like object to the file to be morphed.
        file2: str
            Path-like object to the target file.
        kwargs: dict
            See the diffpy.morph manual for options.

        Returns
        -------
        dict:
            Summary of morphs.
        """

    parser = create_option_parser()

    inputs = []
    for key, value in kwargs.items():
        inputs.append(f"--{key}")
        inputs.append(f"{value}")
    (opts, pargs) = parser.parse_args(inputs)
    pargs = [file, dir]

    return multiple_targets(parser, opts, pargs)


def morph_multiple_morphs(dir, file, **kwargs):
    """Run diffpy.morph with multiple files morphed at Python level.

        Parameters
        ----------
        file1: str
            Path-like object to the file to be morphed.
        file2: str
            Path-like object to the target file.
        kwargs: dict
            See the diffpy.morph manual for options.

        Returns
        -------
        dict:
            Summary of morphs.
        """

    parser = create_option_parser()

    inputs = []
    for key, value in kwargs.items():
        inputs.append(f"--{key}")
        inputs.append(f"{value}")
    (opts, pargs) = parser.parse_args(inputs)
    pargs = [dir, file]

    return multiple_morphs(parser, opts, pargs)
