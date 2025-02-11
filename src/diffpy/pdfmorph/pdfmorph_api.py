#!/usr/bin/env python
##############################################################################
#
# diffpy.pdfmorph   by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2018 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Timothy Liu
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################


import sys

if sys.version_info.major < 3:
    # old import for py2.7
    from collections import Iterable
else:
    from collections.abc import Iterable

import matplotlib.pyplot as plt

from diffpy.pdfmorph import morph_helpers, morphs
from diffpy.pdfmorph import refine as ref
from diffpy.pdfmorph import tools

# map of operation dict
# TODO: include morphing on psize
_morph_step_dict = dict(
    scale=morphs.MorphScale,
    stretch=morphs.MorphStretch,
    smear=[
        morph_helpers.TransformXtalPDFtoRDF,
        morphs.MorphSmear,
        morph_helpers.TransformXtalRDFtoPDF,
    ],
    qdamp=morphs.MorphResolutionDamping,
)
_default_config = dict(
    scale=None, stretch=None, smear=None, baselineslope=None, qdamp=None
)


def morph_default_config(**kwargs):
    """Function to generate default morph configuration.

    Parameters
    ----------
    kwargs
        extra keyword arguments passed to the default morph config

    Returns
    -------
    morph_default_config: dict
        A dictionary of morph configuration

    Examples
    --------
    morph_cfg = morph_default_config(scale=1.01)
    """
    rv = dict(_default_config)
    # protect against foreign keys
    for k in kwargs.keys():
        if k not in rv:
            e = "operation: %s is not currently supported!" % k
            raise ValueError(e)
    rv.update(**kwargs)

    return rv


def pdfmorph(
    x_morph,
    y_morph,
    x_target,
    y_target,
    rmin=None,
    rmax=None,
    rstep=None,
    pearson=False,
    add_pearson=False,
    fixed_operations=None,
    refine=True,
    verbose=False,
    **kwargs,
):
    """Function to perform PDF morphing.

    Parameters
    ----------
    x_morph: numpy.array
        An array of morphed x values, i.e., those will be manipulated by
        morphing.
    y_morph: numpy.array
        An array of morphed y values, i.e., those will be manipulated by
        morphing.
    x_target: numpy.array
        An array of target x values, i.e., those will be kept constant by
        morphing.
    y_morph: numpy.array
        An array of target y values, i.e., those will be kept constant by
        morphing.
    rmin: float, optional
        A value to specify lower r-limit of morph operations.
    rmax: float, optional
        A value to specify upper r-limit of morph operations.
    rstep: float, optional
        A value to specify rstep of morph operations.
    pearson: Bool, optional
        Option to include Pearson coefficient as a minimizing target
         during morphing. Default to False.
    add_pearson: Bool, optional
        Option to include **both** Pearson coefficient and Rw as
        minimizing targets during morphing. Default to False.
    fixed_operations: list, optional
        A list of string specifying operations will be keep fixed during
        morphing. Default is None.
    refine: bool, optional
        Option to execute the minimization step in morphing. If False,
        the morphing will be applied with parameter values specified in
        `morph_config`. Default to True.
    verbose: bool, optional
        Option to print full result after morph. Default to False.
    kwargs: dict, optional
        A dictionary with morph parameters as keys and initial
        values of morph parameters as values. Currently supported morph
        parparameters are:

            - 'scale'
            - 'stretch'
            - 'smear'
            - 'baselineslope'
            - 'qdamp'

    Returns
    -------
    morph_rv_dict: dict
        A dictionary contains following key-value pairs:

        - morph_chain: diffpy.pdfmorph.morphs.morphchain.MorphChain
              The instance of processed morph chain.
              Calling
              ``x_morph, y_morph, x_target, y_target = morph_chain.xyallout``
              will conveniently return morphed data and reference data
        - morphed_cfg: dict
              A dictionary of refined morphing parameters
        - rw: float
              The agreement factor between morphed data and reference
              data
        - pcc: float
              The pearson correlation coefficient between morphed
               data and referenced data

    Examples
    --------
    # morphing (x_morph, y_morph) pair to (x_target, y_target) pair with
    scaling from diffpy.pdfmorph.pdfmorph_api import pdfmorph,
    morph_default_config, plot_morph

    morph_cfg = morph_default_config(scale=1.01)
    morph_rv_dict = pdfmorph(x_morph, y_morph, x_target, y_target, **morph_cfg)

    # plot morhing result
    plot_morph(morph_rv_dict['morph_chain'])

    # print morphing parameters, pearson correlation coefficient, Rw
    print(morph_rv_dict['morphed_cfg'])
    print(morph_rv_dict['pcc'])
    print(morph_rv_dict['rw'])
    """
    refpars = []
    # input config
    rv_cfg = dict(kwargs)
    # configure morph operations
    active_morphs = [
        k
        for k, v in rv_cfg.items()
        if (v is not None) and k in _morph_step_dict
    ]
    rv_cfg["rmin"] = rmin
    rv_cfg["rmax"] = rmax
    rv_cfg["rstep"] = rstep
    # configure smear, guess baselineslope when it is not provided
    if rv_cfg.get("smear") is not None and rv_cfg.get("baselineslope") is None:
        rv_cfg["baselineslope"] = -0.5
    # config dict defines initial guess of parameters
    chain = morphs.MorphChain(rv_cfg)
    # rgrid
    chain.append(morphs.MorphRGrid())
    # configure morph chain
    for k in active_morphs:
        morph_cls = _morph_step_dict[k]
        if k == "smear":
            [chain.append(el()) for el in morph_cls]
            refpars.append("baselineslope")
        else:
            chain.append(morph_cls())
        refpars.append(k)
    # exclude fixed options
    if fixed_operations:
        if not isinstance(fixed_operations, Iterable):
            fixed_operations = [fixed_operations]
        for opt in fixed_operations:
            refpars.remove(opt)
    # define refiner
    refiner = ref.Refiner(chain, x_morph, y_morph, x_target, y_target)
    if pearson:
        refiner.residual = refiner._pearson
    if add_pearson:
        refiner.residual = refiner._add_pearson
    # execute morphing
    if refpars and refine:
        # This works better when we adjust scale and smear first.
        if "smear" in refpars:
            rptemp = ["smear"]
            if "scale" in refpars:
                rptemp.append("scale")
            refiner.refine(*rptemp)
        # Refine all params
        refiner.refine(*refpars)
    else:
        # no operation if refine=False or refpars is empty list
        chain(x_morph, y_morph, x_target, y_target)

    # summary
    rw = tools.getRw(chain)
    pcc = tools.get_pearson(chain)
    # restore rgrid
    chain[0] = morphs.Morph()
    chain(x_morph, y_morph, x_target, y_target)
    # print output
    if verbose:
        if fixed_operations:
            print("== INFO: Following steps are fixed during morphing ==:\n")
            print("\n".join(fixed_operations))
        print("== INFO: Refined morph parameters ==:\n")
        output = "\n".join(
            ["# %s = %f" % (k, v) for k, v in rv_cfg.items() if v is not None]
        )
        output += "\n# Rw = %f" % rw
        output += "\n# Pearson = %f" % pcc
        print(output)

    rv_dict = dict(morph_chain=chain, morphed_config=rv_cfg, rw=rw, pcc=pcc)
    return rv_dict


def plot_morph(chain, ax=None, **kwargs):
    """Plot the morphed PDF and the target PDF of a morphing operation.

    Open a new figure unless a specific axis is provided for plotting.

    Parameters
    ----------
    chain: diffpy.pdfmorph.morphs.morphchain.MorphChain
        An instance of processed morph chain.
    ax: matplotlib.axes.Axes, optional
        An instance of Axes class to plot the morphing result.
        If ax is None, instances of new Figure and Axes will be created.
        Default to None.
    kwargs:
        Additional keyword arguments will be passed to ``ax.plot(...**kwargs)``

    Returns
    -------
    l_list: list
        A list of ``matplotlib.lines.Line2D`` objects representing the
        plotted data.
    """
    if ax is None:
        fig, ax = plt.subplots()
    rfit, grfit = chain.xy_morph_out
    rdat, grdat = chain.xy_target_out
    l_list = ax.plot(rfit, grfit, label="morph", **kwargs)
    l_list += ax.plot(rdat, grdat, label="target", **kwargs)
    ax.set_xlim([chain.config["rmin"], chain.config["rmax"]])
    ax.legend()
    ax.set_xlabel(r"r ($\mathrm{\AA}$)")
    ax.set_ylabel(r"G ($\mathrm{\AA}^{-2}$)")

    return l_list
