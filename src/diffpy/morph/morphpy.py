#!/usr/bin/env python

import numpy as np

from diffpy.morph.morphapp import create_option_parser, single_morph


def get_args(parser, params, kwargs):
    inputs = []
    for key, value in params.items():
        if value is not None:
            inputs.append(f"--{key}")
            inputs.append(f"{value}")
    for key, value in kwargs.items():
        key = key.replace("_", "-")
        inputs.append(f"--{key}")
        inputs.append(f"{value}")
    (opts, pargs) = parser.parse_args(inputs)
    return opts, pargs


def __get_morph_opts__(parser, scale, stretch, smear, plot, **kwargs):
    # Check for Python-specific options
    python_morphs = ["funcy"]
    pymorphs = {}
    for pmorph in python_morphs:
        if pmorph in kwargs:
            pmorph_value = kwargs.pop(pmorph)
            pymorphs.update({pmorph: pmorph_value})

    # Special handling of parameters with dashes
    kwargs_copy = kwargs.copy()
    kwargs = {}
    for key in kwargs_copy.keys():
        new_key = key
        if "_" in key:
            new_key = key.replace("_", "-")
        kwargs.update({new_key: kwargs_copy[key]})

    # Special handling of store_true and store_false parameters
    opts_storing_values = [
        "verbose",
        "pearson",
        "addpearson",
        "apply",
        "reverse",
        "diff",
        "get-diff",
    ]
    opts_to_ignore = ["multiple-morphs", "multiple-targets"]
    for opt in opts_storing_values:
        if opt in kwargs:
            # Remove if user sets false in params
            if not kwargs[opt]:
                kwargs.pop(opt)
    for opt in opts_to_ignore:
        if opt in kwargs:
            kwargs.pop(opt)

    # Wrap the CLI
    params = {
        "scale": scale,
        "stretch": stretch,
        "smear": smear,
        "noplot": True if not plot else None,
    }
    opts, _ = get_args(parser, params, kwargs)

    if not len(pymorphs) > 0:
        pymorphs = None

    return opts, pymorphs


# Take in file names as input.
def morph(
    morph_file,
    target_file,
    scale=None,
    stretch=None,
    smear=None,
    plot=False,
    **kwargs,
):
    """Run diffpy.morph at Python level.

    Parameters
    ----------
    morph_file: str or numpy.array
        Path-like object to the file to be morphed.
    target_file: str or numpy.array
        Path-like object to the target file.
    scale: float, optional
        Initial guess for the scaling parameter.
        Refinement is done only for parameter that are not None.
    stretch: float, optional
        Initial guess for the stretching parameter.
    smear: float, optional
        Initial guess for the smearing parameter.
    plot: bool
        Show a plot of the morphed and target functions as well as the
        difference curve (default: False).
    kwargs: dict
        See the diffpy.morph website for full list of options.
    Returns
    -------
    morph_info: dict
        Summary of morph parameters (e.g. scale, stretch, smear, rmin, rmax)
        and results (e.g. Pearson, Rw).
    morph_table: list
        Function after morph where morph_table[:,0] is the abscissa and
        morph_table[:,1] is the ordinate.
    """
    pargs = [morph_file, target_file]
    parser = create_option_parser()
    opts, pymorphs = __get_morph_opts__(
        parser, scale, stretch, smear, plot, **kwargs
    )

    return single_morph(
        parser,
        opts,
        pargs,
        stdout_flag=False,
        python_wrap=True,
        pymorphs=pymorphs,
    )


# Take in array-like objects as input.
def morph_arrays(
    morph_table,
    target_table,
    scale=None,
    stretch=None,
    smear=None,
    plot=False,
    **kwargs,
):
    """Run diffpy.morph at Python level.

    Parameters
    ----------
    morph_table: numpy.array
        Two-column array of (r, gr) for morphed function.
    target_table: numpy.array
        Two-column array of (r, gr) for target function.
    scale: float, optional
        Initial guess for the scaling parameter.
        Refinement is done only for parameter that are not None.
    stretch: float, optional
        Initial guess for the stretching parameter.
    smear: float, optional
        Initial guess for the smearing parameter.
    plot: bool
        Show a plot of the morphed and target functions as well as the
        difference curve (default: False).
    kwargs: dict
        See the diffpy.morph website for full list of options.
    Returns
    -------
    morph_info: dict
        Summary of morph parameters (e.g. scale, stretch, smear, rmin, rmax)
        and results (e.g. Pearson, Rw).
    morph_table: list
        Function after morph where morph_table[:,0] is the abscissa and
        morph_table[:,1] is the ordinate.
    """
    morph_table = np.array(morph_table)
    target_table = np.array(target_table)
    x_morph = morph_table[:, 0]
    y_morph = morph_table[:, 1]
    x_target = target_table[:, 0]
    y_target = target_table[:, 1]
    pargs = ["Morph", "Target", x_morph, y_morph, x_target, y_target]
    parser = create_option_parser()
    opts, pymorphs = __get_morph_opts__(
        parser, scale, stretch, smear, plot, **kwargs
    )

    return single_morph(
        parser,
        opts,
        pargs,
        stdout_flag=False,
        python_wrap=True,
        pymorphs=pymorphs,
    )
