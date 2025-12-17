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

from __future__ import print_function

import sys
from pathlib import Path

import numpy

import diffpy.morph.morph_helpers as helpers
import diffpy.morph.morph_io as io
import diffpy.morph.morphs as morphs
import diffpy.morph.plot as plot
import diffpy.morph.refine as refine
import diffpy.morph.tools as tools
from diffpy.morph import __save_morph_as__
from diffpy.morph.version import __version__


def create_option_parser():
    import optparse

    prog_short = Path(
        sys.argv[0]
    ).name  # Program name, compatible w/ all OS paths

    class CustomParser(optparse.OptionParser):
        def __init__(self, *args, **kwargs):
            super(CustomParser, self).__init__(*args, **kwargs)

        def custom_error(self, msg):
            """custom_error(msg : string)

            Print a message incorporating 'msg' to stderr and exit. Does
            not print usage.
            """
            self.exit(2, "%s: error: %s\n" % (self.get_prog_name(), msg))

    parser = CustomParser(
        usage="\n".join(
            [
                "%prog [options] MORPHFILE TARGETFILE",
                "Manipulate and compare functions.",
                "Use --help for help.",
            ]
        ),
        epilog="\n".join(
            [
                "Please report bugs to diffpy-users@googlegroups.com.",
                (
                    "For more information, see the diffpy.morph website at "
                    "https://www.diffpy.org/diffpy.morph."
                ),
            ]
        ),
    )

    parser.add_option(
        "-V",
        "--version",
        action="version",
        help="Show program version and exit.",
    )
    parser.version = __version__
    parser.add_option(
        "-s",
        "--save",
        metavar="NAME",
        dest="slocation",
        help=(
            "Save the manipulated function to a file named NAME. "
            "Use '-' for stdout. "
            "When --multiple-<targets/morphs> is enabled, "
            "save each manipulated function as a file in a directory "
            "named NAME. "
            "you can specify names for each saved function file using "
            "--save-names-file."
        ),
    )
    parser.add_option(
        "--diff",
        "--get-diff",
        dest="get_diff",
        action="store_true",
        help=(
            "Save the difference curve rather than the manipulated function. "
            "This is computed as manipulated function minus target function. "
            "The difference curve is computed on the interval shared by the "
            "grid of the objective and target function."
        ),
    )
    parser.add_option(
        "-v",
        "--verbose",
        dest="verbose",
        action="store_true",
        help="Print additional header details to saved files.",
    )
    parser.add_option(
        "--xmin",
        type="float",
        metavar="XMIN",
        help="Minimum x-value (abscissa) to use for function comparisons.",
    )
    parser.add_option(
        "--xmax",
        type="float",
        metavar="XMAX",
        help="Maximum x-value (abscissa) to use for function comparisons.",
    )
    parser.add_option(
        "--tolerance",
        "-t",
        type="float",
        metavar="TOL",
        help="Specify refiner tolerance as TOL. Default: 10e-8.",
    )
    parser.add_option(
        "--pearson",
        action="store_true",
        dest="pearson",
        help=(
            "Maximize agreement in the Pearson function. "
            "Note that this is insensitive to scale."
        ),
    )
    parser.add_option(
        "--addpearson",
        action="store_true",
        dest="addpearson",
        help=(
            "Maximize agreement in the Pearson function as well as "
            "minimizing the residual."
        ),
    )

    # Manipulations
    group = optparse.OptionGroup(
        parser,
        "Manipulations",
        (
            "These options select the manipulations that are to be applied "
            "to the function from MORPHFILE. "
            "The passed values will be refined unless specifically "
            "excluded with the -a or -x options. "
            "If no option is specified, the functions from MORPHFILE and "
            "TARGETFILE will be plotted without any manipulations."
        ),
    )
    parser.add_option_group(group)
    group.add_option(
        "-a",
        "--apply",
        action="store_false",
        dest="refine",
        help="Apply manipulations but do not refine.",
    )
    group.add_option(
        "-x",
        "--exclude",
        action="append",
        dest="exclude",
        metavar="MANIP",
        help=(
            "Exclude a manipulation from refinement by name. "
            "This can appear multiple times."
        ),
    )
    group.add_option(
        "--scale",
        type="float",
        metavar="SCALE",
        help=(
            "Apply scale factor SCALE. "
            "This multiplies the function ordinate by SCALE."
        ),
    )
    group.add_option(
        "--stretch",
        type="float",
        metavar="STRETCH",
        help=(
            "Stretch function grid by a fraction STRETCH. "
            "This multiplies the function grid by 1+STRETCH."
        ),
    )
    group.add_option(
        "--squeeze",
        metavar="a0,a1,...,an",
        help=(
            "Squeeze function grid given a polynomial "
            "a0+a1*x+a2*x^2+...a_n*x^n."
            "n is dependent on the number of values in the "
            "user-inputted comma-separated list. "
            "Repeated and trailing commas are removed before parsing."
            "When this option is enabled, --hshift is disabled. "
            "When n>1, --stretch is disabled. "
            "See online documentation for more information."
        ),
    )
    group.add_option(
        "--smear",
        type="float",
        metavar="SMEAR",
        help=(
            "Smear the peaks with a Gaussian of width SMEAR. "
            "This is done by convolving the function with a "
            "Gaussian with standard deviation SMEAR. "
            "If both --smear and --smear-pdf are enabled, "
            "only --smear-pdf will be applied."
        ),
    )
    group.add_option(
        "--smear-pdf",
        type="float",
        metavar="SMEAR",
        help=(
            "Convert PDF to RDF. "
            "Then, smear peaks with a Gaussian of width SMEAR. "
            "Convert back to PDF. "
            "If both --smear and --smear-pdf are enabled, "
            "only --smear-pdf will be applied."
        ),
    )
    group.add_option(
        "--slope",
        type="float",
        dest="baselineslope",
        help=(
            "Slope of the baseline. This is used with the option "
            "--smear-pdf to convert from the PDF to RDF. "
            "It will be estimated if not provided."
        ),
    )
    group.add_option(
        "--hshift",
        type="float",
        metavar="HSHIFT",
        help="Shift the PDF horizontally by HSHIFT to the right.",
    )
    group.add_option(
        "--vshift",
        type="float",
        metavar="VSHIFT",
        help="Shift the PDF vertically by VSHIFT upward.",
    )
    group.add_option(
        "--qdamp",
        type="float",
        metavar="QDAMP",
        help="Dampen PDF by a factor QDAMP.",
    )
    group.add_option(
        "--radius",
        type="float",
        metavar="RADIUS",
        help=(
            "Apply characteristic function of sphere with radius "
            "RADIUS. If PRADIUS is also specified, instead apply "
            "characteristic function of spheroid with equatorial "
            "radius RADIUS and polar radius PRADIUS."
        ),
    )
    group.add_option(
        "--pradius",
        type="float",
        metavar="PRADIUS",
        help=(
            "Apply characteristic function of spheroid with "
            "equatorial radius RADIUS and polar radius PRADIUS. If only "
            "PRADIUS is specified, instead apply characteristic function of "
            "sphere with radius PRADIUS."
        ),
    )
    group.add_option(
        "--iradius",
        type="float",
        metavar="IRADIUS",
        help=(
            "Apply inverse characteristic function of sphere with radius "
            "IRADIUS. If IPRADIUS is also specified, instead apply inverse "
            "characteristic function of spheroid with equatorial radius "
            "IRADIUS and polar radius IPRADIUS."
        ),
    )
    group.add_option(
        "--ipradius",
        type="float",
        metavar="IPRADIUS",
        help=(
            "Apply inverse characteristic function of spheroid with "
            "equatorial radius IRADIUS and polar radius IPRADIUS. If only "
            "IPRADIUS is specified, instead apply inverse characteristic "
            "function of sphere with radius IPRADIUS."
        ),
    )

    # Plot Options
    group = optparse.OptionGroup(
        parser,
        "Plot Options",
        (
            "These options control plotting. The manipulated and target"
            "functions will be plotted against each other with a difference "
            "curve below. "
            "When --multiple-<targets/morphs> is enabled, the value of a "
            "parameter (specified by --plot-parameter) will be plotted "
            "instead."
        ),
    )
    parser.add_option_group(group)
    group.add_option(
        "-n",
        "--noplot",
        action="store_false",
        dest="plot",
        help="""Do not show a plot.""",
    )
    group.add_option(
        "--mlabel",
        metavar="MLABEL",
        dest="mlabel",
        help=(
            "Set label for morphed data to MLABEL on plot. "
            "Default label is MORPHFILE."
        ),
    )
    group.add_option(
        "--tlabel",
        metavar="TLABEL",
        dest="tlabel",
        help=(
            "Set label for target data to TLABEL on plot. "
            "Default label is TARGETFILE."
        ),
    )
    group.add_option(
        "--pmin",
        type="float",
        help="Minimum x-value to plot. Defaults to XMIN.",
    )
    group.add_option(
        "--pmax",
        type="float",
        help="Maximum x-value to plot. Defaults to XMAX.",
    )
    group.add_option(
        "--maglim",
        type="float",
        help="Magnify plot curves beyond x=MAGLIM by MAG.",
    )
    group.add_option(
        "--mag",
        type="float",
        help="Magnify plot curves beyond x=MAGLIM by MAG.",
    )
    group.add_option(
        "--lwidth", type="float", help="Line thickness of plotted curves."
    )

    # Multiple morph options
    group = optparse.OptionGroup(
        parser,
        "Multiple Morphs",
        (
            "This program can morph a function against multiple targets in"
            " one command. "
            "See -s and Plot Options for how saving and plotting "
            "functionality changes when performing multiple morphs."
        ),
    )
    parser.add_option_group(group)
    group.add_option(
        "--multiple-morphs",
        dest="multiple_morphs",
        action="store_true",
        help=(
            f"Usage: '{prog_short} --multiple-morphs [options] DIRECTORY "
            f"TARGET'. "
            f"Morphs every file in DIRECTORY to the a single TARGET file. "
            f"Paths for DIRECTORY and TARGET are relative to the current "
            f"working directory. "
            "By default, the Rw for each morph is plotted, where the x-axis "
            "is sorted alphanumerically by filename of the file being "
            "morphed. "
            "Use --sort-by option to change the x-axis order. "
            "Use --plot-parameter to modify the parameter plotted on the "
            "y-axis."
        ),
    )
    group.add_option(
        "--multiple-targets",
        dest="multiple_targets",
        action="store_true",
        help=(
            f"Usage: '{prog_short} --multiple-targets [options] MORPH "
            f"DIRECTORY'. "
            f"Morphs the MORPH file to every file in DIRECTORY. "
            f"Paths for MORPH and DIRECTORY are relative to the current "
            f"working directory. "
            "By default, the Rw for each morph is plotted, where the x-axis "
            "is sorted alphanumerically by filename of the file being "
            "morphed. "
            "Use --sort-by option to change the x-axis order. "
            "Use --plot-parameter to modify the parameter plotted on the "
            "y-axis."
        ),
    )
    group.add_option(
        "--sort-by",
        metavar="FIELD",
        dest="field",
        help=(
            "Used with --multiple-<targets/morphs> to sort files in "
            "DIRECTORY by FIELD. "
            "If the FIELD being used has a numerical value, sort from "
            "lowest to highest unless --reverse is enabled. "
            "Otherwise, sort in ASCII sort order. "
            "The program will look for the FIELD (case insensitive) in the "
            "header of each of the files in DIRECTORY. "
            "If plotting is enabled, the x-axis of the plot will be the "
            "field."
        ),
    )
    group.add_option(
        "--reverse",
        dest="reverse",
        action="store_true",
        help="""Sort from highest to lowest instead.""",
    )
    group.add_option(
        "--serial-file",
        metavar="SERIALFILE",
        dest="serfile",
        help=(
            "Look for FIELD in a serial file instead. "
            "Must specify name of serial file SERIALFILE."
        ),
    )
    group.add_option(
        "--save-names-file",
        metavar="NAMESFILE",
        dest="snamesfile",
        help=(
            "Used when both -s and --multiple-<targets/morphs> are enabled. "
            "Specify names for each manipulated PDF when saving (see -s) "
            "using a serial file NAMESFILE. The format of NAMESFILE should "
            "be as follows: each target PDF is an entry in NAMESFILE. "
            "For each entry, there should be a key {__save_morph_as__} "
            "whose value specifies the name to save the manipulated "
            "function as."
            "An example .json serial file is included in the tutorial "
            "directory on the package GitHub repository."
        ),
    )
    group.add_option(
        "--plot-parameter",
        metavar="PLOTPARAM",
        dest="plotparam",
        help=(
            "Used when both plotting and --multiple-<targets/morphs> are "
            "enabled. Choose a PLOTPARAM to plot for each morph (i.e. adding "
            "--plot-parameter=Pearson means the program will display a plot "
            "of the Pearson correlation coefficient for each morph-target pair"
            "). PLOTPARAM is not case sensitive, so both Pearson and pearson "
            "indicate the same parameter. When PLOTPARAM is not specified, Rw "
            "values for each morph-target pair will be plotted. PLOTPARAM "
            "will be displayed as the vertical axis label for the plot."
        ),
    )

    # Defaults
    parser.set_defaults(multiple=False)
    parser.set_defaults(reverse=False)
    parser.set_defaults(plot=True)
    parser.set_defaults(refine=True)
    parser.set_defaults(pearson=False)
    parser.set_defaults(addpearson=False)
    parser.set_defaults(mag=5)
    parser.set_defaults(lwidth=1.5)

    return parser


def single_morph(
    parser, opts, pargs, stdout_flag=True, python_wrap=False, pymorphs=None
):
    if len(pargs) < 2:
        parser.error("You must supply MORPHFILE and TARGETFILE.")
    elif len(pargs) > 2 and not python_wrap:
        parser.error(
            "Too many arguments. Make sure you only supply "
            "MORPHFILE and TARGETFILE."
        )
    elif not (len(pargs) == 2 or len(pargs) == 6) and python_wrap:
        parser.error("Python wrapper error.")

    # Get the PDFs
    # If we get from python, we may wrap, which has input size 4
    if len(pargs) == 6 and python_wrap:
        x_morph = pargs[2]
        y_morph = pargs[3]
        x_target = pargs[4]
        y_target = pargs[5]
    else:
        x_morph, y_morph = getPDFFromFile(pargs[0])
        x_target, y_target = getPDFFromFile(pargs[1])

    if y_morph is None:
        parser.error(f"No data table found in: {pargs[0]}.")
    if y_target is None:
        parser.error(f"No data table found in: {pargs[1]}.")

    # Get tolerance
    tolerance = 1e-08
    if opts.tolerance is not None:
        tolerance = opts.tolerance

    # Get configuration values
    scale_in = "None"
    stretch_in = "None"
    smear_in = "None"
    hshift_in = "None"
    vshift_in = "None"
    config = {"xmin": opts.xmin, "xmax": opts.xmax, "xstep": None}
    if (
        opts.xmin is not None
        and opts.xmax is not None
        and opts.xmax <= opts.xmin
    ):
        e = "xmin must be less than xmax"
        parser.custom_error(e)

    # Set up the morphs
    chain = morphs.MorphChain(config)
    refpars = []

    # Python-Specific Morphs
    if pymorphs is not None:
        # funcxy/funcx/funcy value is a tuple (function,{param_dict})
        if "funcxy" in pymorphs:
            mfxy_function = pymorphs["funcxy"][0]
            mfxy_params = pymorphs["funcxy"][1]
            chain.append(morphs.MorphFuncxy())
            config["funcxy_function"] = mfxy_function
            config["funcxy"] = mfxy_params
            refpars.append("funcxy")
        if "funcx" in pymorphs:
            mfx_function = pymorphs["funcx"][0]
            mfx_params = pymorphs["funcx"][1]
            chain.append(morphs.MorphFuncx())
            config["funcx_function"] = mfx_function
            config["funcx"] = mfx_params
            refpars.append("funcx")
        if "funcy" in pymorphs:
            mfy_function = pymorphs["funcy"][0]
            mfy_params = pymorphs["funcy"][1]
            chain.append(morphs.MorphFuncy())
            config["funcy_function"] = mfy_function
            config["funcy"] = mfy_params
            refpars.append("funcy")

    # Squeeze
    squeeze_poly_deg = -1
    squeeze_dict_in = {}
    squeeze_morph = None
    if opts.squeeze is not None:
        # Handles both list and csv input
        if (
            len(opts.squeeze) > 1
            and opts.squeeze[0] == "["
            and opts.squeeze[-1] == "]"
        ):
            opts.squeeze = opts.squeeze[1:-1]
        elif (
            len(opts.squeeze) > 1
            and opts.squeeze[0] == "("
            and opts.squeeze[-1] == ")"
        ):
            opts.squeeze = opts.squeeze[1:-1]
        squeeze_coeffs = opts.squeeze.strip().split(",")
        idx = 0
        for _, coeff in enumerate(squeeze_coeffs):
            if coeff.strip() != "":
                try:
                    squeeze_dict_in.update({f"a{idx}": float(coeff)})
                    idx += 1
                except ValueError:
                    parser.error(f"{coeff} could not be converted to float.")
        squeeze_poly_deg = len(squeeze_dict_in.keys())
        squeeze_morph = morphs.MorphSqueeze()
        chain.append(squeeze_morph)
        config["squeeze"] = squeeze_dict_in
        # config["extrap_index_low"] = None
        # config["extrap_index_high"] = None
        refpars.append("squeeze")
    # Scale
    if opts.scale is not None:
        scale_in = opts.scale
        chain.append(morphs.MorphScale())
        config["scale"] = scale_in
        refpars.append("scale")
    # Stretch
    # Only enable stretch if squeeze is lower than degree 1
    stretch_morph = None
    if opts.stretch is not None and squeeze_poly_deg < 1:
        stretch_morph = morphs.MorphStretch()
        chain.append(stretch_morph)
        stretch_in = opts.stretch
        config["stretch"] = stretch_in
        refpars.append("stretch")
    # Smear
    if opts.smear_pdf is not None:
        smear_in = opts.smear_pdf
        chain.append(helpers.TransformXtalPDFtoRDF())
        chain.append(morphs.MorphSmear())
        chain.append(helpers.TransformXtalRDFtoPDF())
        refpars.append("smear")
        config["smear"] = smear_in
        # Set baselineslope if not given
        config["baselineslope"] = opts.baselineslope
        if opts.baselineslope is None:
            config["baselineslope"] = -0.5
        refpars.append("baselineslope")
    elif opts.smear is not None:
        smear_in = opts.smear
        chain.append(morphs.MorphSmear())
        refpars.append("smear")
        config["smear"] = smear_in
    # Shift
    # Only enable hshift is squeeze is not enabled
    shift_morph = None
    if (
        opts.hshift is not None and squeeze_poly_deg < 0
    ) or opts.vshift is not None:
        shift_morph = morphs.MorphShift()
        chain.append(shift_morph)
    if opts.hshift is not None and squeeze_poly_deg < 0:
        hshift_in = opts.hshift
        config["hshift"] = hshift_in
        refpars.append("hshift")
    if opts.vshift is not None:
        vshift_in = opts.vshift
        config["vshift"] = vshift_in
        refpars.append("vshift")
    # Size
    radii = [opts.radius, opts.pradius]
    nrad = 2 - radii.count(None)
    if nrad == 1:
        radii.remove(None)
        config["radius"] = tools.nn_value(radii[0], "radius or pradius")
        chain.append(morphs.MorphSphere())
        refpars.append("radius")
    elif nrad == 2:
        config["radius"] = tools.nn_value(radii[0], "radius")
        refpars.append("radius")
        config["pradius"] = tools.nn_value(radii[1], "pradius")
        refpars.append("pradius")
        chain.append(morphs.MorphSpheroid())
    iradii = [opts.iradius, opts.ipradius]
    inrad = 2 - iradii.count(None)
    if inrad == 1:
        iradii.remove(None)
        config["iradius"] = tools.nn_value(iradii[0], "iradius or ipradius")
        chain.append(morphs.MorphISphere())
        refpars.append("iradius")
    elif inrad == 2:
        config["iradius"] = tools.nn_value(iradii[0], "iradius")
        refpars.append("iradius")
        config["ipradius"] = tools.nn_value(iradii[1], "ipradius")
        refpars.append("ipradius")
        chain.append(morphs.MorphISpheroid())

    # Resolution
    if opts.qdamp is not None:
        chain.append(morphs.MorphResolutionDamping())
        refpars.append("qdamp")
        config["qdamp"] = opts.qdamp

    # Add the r-range morph, we will remove it when saving and plotting
    mrg = morphs.MorphRGrid()
    chain.append(mrg)

    # Now remove non-refinable parameters
    if opts.exclude is not None:
        refpars = list(set(refpars) - set(opts.exclude))
        if "stretch" in opts.exclude:
            stretch_morph = None

    # Refine or execute the morph
    refiner = refine.Refiner(
        chain, x_morph, y_morph, x_target, y_target, tolerance=tolerance
    )
    if opts.pearson:
        refiner.residual = refiner._pearson
    if opts.addpearson:
        refiner.residual = refiner._add_pearson
    if opts.refine and refpars:
        try:
            # This works better when we adjust scale and smear first.
            if "smear" in refpars:
                rptemp = ["smear"]
                if "scale" in refpars:
                    rptemp.append("scale")
                refiner.refine(*rptemp)
            # Adjust all parameters
            refiner.refine(*refpars)
        except ValueError as e:
            parser.custom_error(str(e))
    # Smear is not being refined, but baselineslope needs to refined to apply
    # smear
    # Note that baselineslope is only added to the refine list if smear is
    # applied
    elif "baselineslope" in refpars:
        try:
            refiner.refine(
                "baselineslope", baselineslope=config["baselineslope"]
            )
        except ValueError as e:
            parser.custom_error(str(e))
    else:
        chain(x_morph, y_morph, x_target, y_target)

    # THROW ANY WARNINGS HERE
    io.handle_warnings(squeeze_morph)
    io.handle_warnings(shift_morph)
    io.handle_warnings(stretch_morph)

    # Get Rw for the morph range
    rw = tools.getRw(chain)
    pcc = tools.get_pearson(chain)
    # Replace the MorphRGrid with Morph identity
    # This removes the r-range morph as mentioned above
    mrg = morphs.Morph()
    chain(x_morph, y_morph, x_target, y_target)

    # FOR FUTURE MAINTAINERS
    # Any new morph should have their input morph parameters updated here
    # You should also update the IO in morph_io
    # if you think there requires special handling

    # Input morph parameters
    morph_inputs = {
        "scale": scale_in,
        "stretch": stretch_in,
        "smear": smear_in,
    }
    morph_inputs.update({"hshift": hshift_in, "vshift": vshift_in})
    # More complex input morph parameters are only displayed conditionally
    if opts.squeeze is not None:
        squeeze_dict = squeeze_dict_in.copy()
        for idx, _ in enumerate(squeeze_dict):
            morph_inputs.update({f"squeeze a{idx}": squeeze_dict[f"a{idx}"]})
    if pymorphs is not None:
        if "funcxy" in pymorphs:
            for funcxy_param in pymorphs["funcxy"][1].keys():
                morph_inputs.update(
                    {
                        f"funcxy {funcxy_param}": pymorphs["funcxy"][1][
                            funcxy_param
                        ]
                    }
                )
        if "funcy" in pymorphs:
            for funcy_param in pymorphs["funcy"][1].keys():
                morph_inputs.update(
                    {f"funcy {funcy_param}": pymorphs["funcy"][1][funcy_param]}
                )
        if "funcx" in pymorphs:
            for funcy_param in pymorphs["funcx"][1].keys():
                morph_inputs.update(
                    {f"funcx {funcy_param}": pymorphs["funcx"][1][funcy_param]}
                )

    # Output morph parameters
    morph_results = dict(config.items())
    # Ensure Rw, Pearson last two outputs
    morph_results.update({"Rw": rw})
    morph_results.update({"Pearson": pcc})

    # Print summary to terminal and save morph to file if requested
    xy_save = [chain.x_morph_out, chain.y_morph_out]
    if opts.get_diff is not None:
        diff_chain = morphs.MorphChain(
            {"xmin": None, "xmax": None, "xstep": None}
        )
        diff_chain.append(morphs.MorphRGrid())
        diff_chain(
            chain.x_morph_out,
            chain.y_morph_out,
            chain.x_target_in,
            chain.y_target_in,
        )
        xy_save = [
            diff_chain.x_morph_out,
            diff_chain.y_morph_out - diff_chain.y_target_out,
        ]
    try:
        io.single_morph_output(
            morph_inputs,
            morph_results,
            save_file=opts.slocation,
            morph_file=pargs[0],
            xy_out=xy_save,
            verbose=opts.verbose,
            stdout_flag=stdout_flag,
        )

    except (FileNotFoundError, RuntimeError):
        save_fail_message = "Unable to save to designated location."
        parser.custom_error(save_fail_message)

    if opts.plot:
        pairlist = [chain.xy_target_out, chain.xy_morph_out]
        labels = [pargs[1], pargs[0]]  # Default is to use file names

        # If user chooses labels
        if opts.mlabel is not None:
            labels[1] = opts.mlabel
        if opts.tlabel is not None:
            labels[0] = opts.tlabel

        # Plot extent defaults to calculation extent
        pmin = opts.pmin if opts.pmin is not None else opts.xmin
        pmax = opts.pmax if opts.pmax is not None else opts.xmax
        maglim = opts.maglim
        mag = opts.mag
        l_width = opts.lwidth
        plot.compare_funcs(
            pairlist,
            labels,
            xmin=pmin,
            xmax=pmax,
            maglim=maglim,
            mag=mag,
            rw=rw,
            l_width=l_width,
        )

    # Return different things depending on whether it is python interfaced
    if python_wrap:
        morph_info = morph_results
        morph_table = numpy.array(xy_save).T
        return morph_info, morph_table
    else:
        return morph_results


def multiple_targets(parser, opts, pargs, stdout_flag=True, python_wrap=False):
    # Custom error messages since usage is distinct when --multiple tag is
    # applied
    if len(pargs) < 2:
        parser.custom_error(
            "You must supply a FILE and DIRECTORY. "
            "See --multiple-targets under --help for usage."
        )
    elif len(pargs) > 2:
        parser.custom_error(
            "Too many arguments. You must only supply a FILE and a DIRECTORY."
        )

    # Parse paths
    morph_file = Path(pargs[0])
    if not morph_file.is_file():
        parser.custom_error(
            f"{morph_file} is not a file. Go to --help for usage."
        )
    target_directory = Path(pargs[1])
    if not target_directory.is_dir():
        parser.custom_error(
            f"{target_directory} is not a directory. Go to --help for usage."
        )

    # Get list of files from target directory
    target_list = list(target_directory.iterdir())
    to_remove = []
    for target in target_list:
        if target.is_dir():
            to_remove.append(target)
    for target in to_remove:
        target_list.remove(target)

    # Do not morph morph_file against itself if it is in the same directory
    if morph_file in target_list:
        target_list.remove(morph_file)

    # Format field name for printing and plotting
    field = None
    if opts.field is not None:
        field_words = opts.field.split()
        field = ""
        for word in field_words:
            field += f"{word[0].upper()}{word[1:].lower()}"
    field_list = None

    # Sort files in directory by some field
    if field is not None:
        try:
            target_list, field_list = tools.field_sort(
                target_list,
                field,
                opts.reverse,
                opts.serfile,
                get_field_values=True,
            )
        except KeyError:
            if opts.serfile is not None:
                parser.custom_error(
                    "The requested field was not found in the metadata file."
                )
            else:
                parser.custom_error(
                    "The requested field is missing from a file header."
                )
    else:
        # Default is alphabetical sort
        target_list.sort(reverse=opts.reverse)

    # Disable single morph plotting
    plot_opt = opts.plot
    opts.plot = False

    # Set up saving
    save_directory = opts.slocation  # User-given directory for saves
    save_names_file = (
        opts.snamesfile
    )  # User-given serialfile with names for each morph
    save_morphs_here = None  # Subdirectory for saving morphed functions
    save_names = {}  # Dictionary of names to save each morph as
    if save_directory is not None:
        try:
            save_morphs_here = io.create_morphs_directory(save_directory)

        # Could not create directory or find names to save morphs as
        except (FileNotFoundError, RuntimeError):
            save_fail_message = "\nUnable to create directory"
            parser.custom_error(save_fail_message)

        try:
            save_names = io.get_multisave_names(
                target_list, save_names_file=save_names_file
            )
            # Could not create directory or find names to save morphs as
        except FileNotFoundError:
            save_fail_message = "\nUnable to read from save names file"
            parser.custom_error(save_fail_message)

    # Morph morph_file against all other files in target_directory
    morph_results = {}
    for target_file in target_list:
        if target_file.is_file:
            # Set the save file destination to be a file within the SLOC
            # directory
            if save_directory is not None:
                save_as = save_names[target_file.name][__save_morph_as__]
                opts.slocation = Path(save_morphs_here).joinpath(save_as)
            # Perform a morph of morph_file against target_file
            pargs = [morph_file, target_file]
            morph_results.update(
                {
                    target_file.name: single_morph(
                        parser, opts, pargs, stdout_flag=False
                    ),
                }
            )

    target_file_names = []
    for key in morph_results.keys():
        target_file_names.append(key)

    morph_inputs = {
        "scale": opts.scale,
        "stretch": opts.stretch,
        "smear": opts.smear_pdf,
    }
    morph_inputs.update({"hshift": opts.hshift, "vshift": opts.vshift})

    try:
        # Print summary of morphs to terminal and to file (if requested)
        io.multiple_morph_output(
            morph_inputs,
            morph_results,
            target_file_names,
            save_directory=save_directory,
            morph_file=morph_file,
            target_directory=target_directory,
            field=field,
            field_list=field_list,
            verbose=opts.verbose,
            stdout_flag=stdout_flag,
        )
    except (FileNotFoundError, RuntimeError):
        save_fail_message = "Unable to save summary to directory."
        parser.custom_error(save_fail_message)

    # Plot the values of some parameter for each target if requested
    if plot_opt:
        plot_results = io.tabulate_results(morph_results)
        # Default parameter is Rw
        param_name = r"$R_w$"
        param_list = plot_results["Rw"]
        # Find parameter if specified
        if opts.plotparam is not None:
            param_name = opts.plotparam
            param_list = tools.case_insensitive_dictionary_search(
                opts.plotparam, plot_results
            )
        # Not an available parameter to plot or no values found for the
        # parameter
        if param_list is None:
            parser.custom_error(
                "Cannot find specified plot parameter. No plot shown."
            )
        else:
            try:
                if field_list is not None:
                    plot.plot_param(field_list, param_list, param_name, field)
                else:
                    plot.plot_param(target_file_names, param_list, param_name)
            # Can occur for non-refined plotting parameters
            # i.e. --smear is not selected as an option, but smear is the
            # plotting parameter
            except ValueError:
                parser.custom_error(
                    "The plot parameter is missing values for at least one "
                    "morph and target pair. No plot shown."
                )

    return morph_results


def multiple_morphs(parser, opts, pargs, stdout_flag=True, python_wrap=False):
    # Custom error messages since usage is distinct when --multiple tag is
    # applied
    if len(pargs) < 2:
        parser.custom_error(
            "You must supply a DIRECTORY and FILE. "
            "See --multiple-morphs under --help for usage."
        )
    elif len(pargs) > 2:
        parser.custom_error(
            "Too many arguments. You must only supply a DIRECTORY and FILE."
        )

    # Parse paths
    target_file = Path(pargs[1])
    if not target_file.is_file():
        parser.custom_error(
            f"{target_file} is not a file. Go to --help for usage."
        )
    morph_directory = Path(pargs[0])
    if not morph_directory.is_dir():
        parser.custom_error(
            f"{morph_directory} is not a directory. Go to --help for usage."
        )

    # Get list of files from morph directory
    morph_list = list(morph_directory.iterdir())
    to_remove = []
    for morph in morph_list:
        if morph.is_dir():
            to_remove.append(morph)
    for morph in to_remove:
        morph_list.remove(morph)

    # Do not morph target_file against itself if it is in the same directory
    if target_file in morph_list:
        morph_list.remove(target_file)

    # Format field name for printing and plotting
    field = None
    if opts.field is not None:
        field_words = opts.field.split()
        field = ""
        for word in field_words:
            field += f"{word[0].upper()}{word[1:].lower()}"
    field_list = None

    # Sort files in directory by some field
    if field is not None:
        try:
            morph_list, field_list = tools.field_sort(
                morph_list,
                field,
                opts.reverse,
                opts.serfile,
                get_field_values=True,
            )
        except KeyError:
            if opts.serfile is not None:
                parser.custom_error(
                    "The requested field was not found in the metadata file."
                )
            else:
                parser.custom_error(
                    "The requested field is missing from a PDF file header."
                )
    else:
        # Default is alphabetical sort
        morph_list.sort(reverse=opts.reverse)

    # Disable single morph plotting
    plot_opt = opts.plot
    opts.plot = False

    # Set up saving
    save_directory = opts.slocation  # User-given directory for saves
    save_names_file = (
        opts.snamesfile
    )  # User-given serialfile with names for each morph
    save_morphs_here = None  # Subdirectory for saving morphed PDFs
    save_names = {}  # Dictionary of names to save each morph as
    if save_directory is not None:
        try:
            save_morphs_here = io.create_morphs_directory(save_directory)

        # Could not create directory or find names to save morphs as
        except (FileNotFoundError, RuntimeError):
            save_fail_message = "\nUnable to create directory"
            parser.custom_error(save_fail_message)

        try:
            save_names = io.get_multisave_names(
                morph_list, save_names_file=save_names_file
            )
            # Could not create directory or find names to save morphs as
        except FileNotFoundError:
            save_fail_message = "\nUnable to read from save names file"
            parser.custom_error(save_fail_message)

    # Morph morph_file against all other files in target_directory
    morph_results = {}
    for morph_file in morph_list:
        if morph_file.is_file:
            # Set the save file destination to be a file within the SLOC
            # directory
            if save_directory is not None:
                save_as = save_names[morph_file.name][__save_morph_as__]
                opts.slocation = Path(save_morphs_here).joinpath(save_as)
            # Perform a morph of morph_file against target_file
            pargs = [morph_file, target_file]
            morph_results.update(
                {
                    morph_file.name: single_morph(
                        parser, opts, pargs, stdout_flag=False
                    ),
                }
            )

    morph_file_names = []
    for key in morph_results.keys():
        morph_file_names.append(key)

    morph_inputs = {
        "scale": opts.scale,
        "stretch": opts.stretch,
        "smear": opts.smear_pdf,
    }
    morph_inputs.update({"hshift": opts.hshift, "vshift": opts.vshift})

    try:
        # Print summary of morphs to terminal and to file (if requested)
        io.multiple_morph_output(
            morph_inputs,
            morph_results,
            morph_file_names,
            save_directory=save_directory,
            morph_file=target_file,
            target_directory=morph_directory,
            field=field,
            field_list=field_list,
            verbose=opts.verbose,
            stdout_flag=stdout_flag,
            mm=True,
        )
    except (FileNotFoundError, RuntimeError):
        save_fail_message = "Unable to save summary to directory."
        parser.custom_error(save_fail_message)

    # Plot the values of some parameter for each target if requested
    if plot_opt:
        plot_results = io.tabulate_results(morph_results)
        # Default parameter is Rw
        param_name = r"$R_w$"
        param_list = plot_results["Rw"]
        # Find parameter if specified
        if opts.plotparam is not None:
            param_name = opts.plotparam
            param_list = tools.case_insensitive_dictionary_search(
                opts.plotparam, plot_results
            )
        # Not an available parameter to plot or no values found for the
        # parameter
        if param_list is None:
            parser.custom_error(
                "Cannot find specified plot parameter. No plot shown."
            )
        else:
            try:
                if field_list is not None:
                    plot.plot_param(field_list, param_list, param_name, field)
                else:
                    plot.plot_param(morph_file_names, param_list, param_name)
            # Can occur for non-refined plotting parameters
            # i.e. --smear is not selected as an option, but smear is the
            # plotting parameter
            except ValueError:
                parser.custom_error(
                    "The plot parameter is missing values for at least one "
                    "morph and target pair. No plot shown."
                )

    return morph_results


def getPDFFromFile(fn):
    from diffpy.morph.tools import readPDF

    try:
        r, gr = readPDF(fn)
    except IOError as errmsg:
        print("%s: %s" % (fn, errmsg), file=sys.stderr)
        sys.exit(1)
    except ValueError:
        print("Cannot read %s" % fn, file=sys.stderr)
        sys.exit(1)

    return r, gr


def main():
    parser = create_option_parser()
    (opts, pargs) = parser.parse_args()
    if opts.multiple_targets:
        multiple_targets(parser, opts, pargs, stdout_flag=True)
    elif opts.multiple_morphs:
        multiple_morphs(parser, opts, pargs, stdout_flag=True)
    else:
        single_morph(parser, opts, pargs, stdout_flag=True)


if __name__ == "__main__":
    main()
