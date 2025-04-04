#!/usr/bin/env python

import numpy as np

from diffpy.morph.morphapp import (
    create_option_parser,
    multiple_morphs,
    multiple_targets,
    single_morph,
)


def morph(morph_file, target_file, **kwargs):
    """Run diffpy.morph at Python level.

    Parameters
    ----------
    morph_file: str
        Path-like object to the file to be morphed.
    target_file: str
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
    pargs = [morph_file, target_file]

    return single_morph(
        parser, opts, pargs, stdout_flag=False, python_wrap=True
    )


def morphpy(morph_table, target_table, morph_header=None, target_header=None, **kwargs):
    """Run diffpy.morph at Python level.

    Parameters
    ----------
    morph_table: numpy.array
        Two-column array of (r, gr) for morphed function.
    target_table: numpy.array
        Two-column array of (r, gr) for target function.
    morph_header: dict
        Any relevant parameters (e.g. wavelength, composition, temperature)
        for the morphed function.
    target_header: dict
        Any relevant parameters for the target ction.
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

    morph_table = np.array(morph_table)
    target_table = np.array(target_table)

    x_morph = morph_table[:, 0]
    y_morph = morph_table[:, 1]
    x_target = target_table[:, 0]
    y_target = target_table[:, 1]

    pargs = ["Morph", "Target", x_morph, y_morph, x_target, y_target]
    print(pargs)

    return single_morph(
        parser, opts, pargs, stdout_flag=False, python_wrap=True
    )


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
