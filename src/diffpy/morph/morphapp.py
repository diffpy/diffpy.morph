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

            Print a message incorporating 'msg' to stderr and exit.
            Does not print usage.
            """
            self.exit(2, "%s: error: %s\n" % (self.get_prog_name(), msg))

    parser = CustomParser(
        usage="\n".join(
            [
                "%prog [options] FILE1 FILE2",
                "Manipulate and compare PDFs.",
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
            "Save the manipulated PDF to a file named NAME. "
            "Use '-' for stdout.\n"
            "When --multiple-<targets/morphs> is enabled, "
            "save each manipulated PDF as a file in a directory named NAME;\n"
            "you can specify names for each saved PDF file using "
            "--save-names-file."
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
        "--rmin",
        type="float",
        help="Minimum r-value to use for PDF comparisons.",
    )
    parser.add_option(
        "--rmax",
        type="float",
        help="Maximum r-value to use for PDF comparisons.",
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
        help="""Maximize agreement in the Pearson function as well as
 minimizing the residual.""",
    )

    # Manipulations
    group = optparse.OptionGroup(
        parser,
        "Manipulations",
        (
            "These options select the manipulations that are to be applied to "
            "the PDF from FILE1. "
            "The passed values will be refined unless specifically "
            "excluded with the -a or -x options. "
            "If no option is specified, the PDFs from FILE1 and FILE2 will "
            "be plotted without any manipulations."
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
        help="""Exclude a manipulation from refinement by name. This can
 appear multiple times.""",
    )
    group.add_option(
        "--scale",
        type="float",
        metavar="SCALE",
        help="Apply scale factor SCALE.",
    )
    group.add_option(
        "--stretch",
        type="float",
        metavar="STRETCH",
        help="Stretch PDF by a fraction STRETCH.",
    )
    group.add_option(
        "--smear",
        type="float",
        metavar="SMEAR",
        help="Smear peaks with a Gaussian of width SMEAR.",
    )
    group.add_option(
        "--slope",
        type="float",
        dest="baselineslope",
        help="""Slope of the baseline. This is used when applying the smear
 factor. It will be estimated if not provided.""",
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
            "These options control plotting. The manipulated and target PDFs "
            "will be plotted against each other with a difference curve "
            "below. "
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
            "Default label is FILE1."
        ),
    )
    group.add_option(
        "--tlabel",
        metavar="TLABEL",
        dest="tlabel",
        help=(
            "Set label for target data to TLABEL on plot. "
            "Default label is FILE2."
        ),
    )
    group.add_option(
        "--pmin",
        type="float",
        help="Minimum r-value to plot. Defaults to RMIN.",
    )
    group.add_option(
        "--pmax",
        type="float",
        help="Maximum r-value to plot. Defaults to RMAX.",
    )
    group.add_option(
        "--maglim",
        type="float",
        help="Magnify plot curves beyond r=MAGLIM by MAG.",
    )
    group.add_option(
        "--mag",
        type="float",
        help="Magnify plot curves beyond r=MAGLIM by MAG.",
    )
    group.add_option(
        "--lwidth", type="float", help="Line thickness of plotted curves."
    )

    # Multiple morph options
    group = optparse.OptionGroup(
        parser,
        "Multiple Morphs",
        (
            "This program can morph a PDF against multiple targets in one "
            "command. See -s and Plot Options for how saving and plotting "
            "functionality changes when performing multiple morphs."
        ),
    )
    parser.add_option_group(group)
    group.add_option(
        "--multiple-morphs",
        dest="multiple_morphs",
        action="store_true",
        help=(
            f"Changes usage to '{prog_short} [options] FILE DIRECTORY'. "
            f"FILE will be morphed with each file in DIRECTORY as target. "
            f"Files in DIRECTORY are sorted by alphabetical order unless a "
            f"field is specified by --sort-by."
        ),
    )
    group.add_option(
        "--multiple-targets",
        dest="multiple_targets",
        action="store_true",
        help=(
            f"Changes usage to '{prog_short} [options] DIRECTORY FILE'. "
            f"Each file in DIRECTORY will be morphed with FILE as target. "
            f"Files in DIRECTORY are sorted by alphabetical order unless a "
            f"field is specified by --sort-by."
        ),
    )
    group.add_option(
        "--sort-by",
        metavar="FIELD",
        dest="field",
        help=(
            "Used with --multiple-<targets/morphs> to sort files in DIRECTORY "
            "by FIELD. "
            "If the FIELD being used has a numerical value, sort from lowest "
            "to highest. Otherwise, sort in ASCII sort order. FIELD must be "
            "included in the header of all the PDF files."
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
        help="""Look for FIELD in a serial file instead.
 Must specify name of serial file SERIALFILE.""",
    )
    group.add_option(
        "--save-names-file",
        metavar="NAMESFILE",
        dest="snamesfile",
        help=(
            "Used when both -s and --multiple-<targets/morphs> are enabled. "
            "Specify names for each manipulated PDF when saving (see -s) "
            "using a serial file NAMESFILE. The format of NAMESFILE should be "
            "as follows: each target PDF is an entry in NAMESFILE. For each "
            "entry, there should be a key {__save_morph_as__} whose value "
            "specifies the name to save the manipulated PDF as. An example "
            ".json serial file is shown in the diffpy.morph manual."
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


def single_morph(parser, opts, pargs, stdout_flag=True, python_wrap=False):
    if len(pargs) < 2:
        parser.error("You must supply FILE1 and FILE2.")
    elif len(pargs) > 2 and not python_wrap:
        parser.error(
            "Too many arguments. Make sure you only supply FILE1 and FILE2."
        )
    elif not (len(pargs) == 2 or len(pargs) == 6) and python_wrap:
        parser.error(
            "Python wrapper error."
        )

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

    # Get configuration values
    scale_in = "None"
    stretch_in = "None"
    smear_in = "None"
    hshift_in = "None"
    vshift_in = "None"
    config = {}
    config["rmin"] = opts.rmin
    config["rmax"] = opts.rmax
    config["rstep"] = None
    if (
        opts.rmin is not None
        and opts.rmax is not None
        and opts.rmax <= opts.rmin
    ):
        e = "rmin must be less than rmax"
        parser.custom_error(e)

    # Set up the morphs
    chain = morphs.MorphChain(config)
    # Add the r-range morph, we will remove it when saving and plotting
    chain.append(morphs.MorphRGrid())
    refpars = []

    # Scale
    if opts.scale is not None:
        scale_in = opts.scale
        chain.append(morphs.MorphScale())
        config["scale"] = scale_in
        refpars.append("scale")
    # Stretch
    if opts.stretch is not None:
        stretch_in = opts.stretch
        chain.append(morphs.MorphStretch())
        config["stretch"] = stretch_in
        refpars.append("stretch")
    # Shift
    if opts.hshift is not None or opts.vshift is not None:
        chain.append(morphs.MorphShift())
    if opts.hshift is not None:
        hshift_in = opts.hshift
        config["hshift"] = hshift_in
        refpars.append("hshift")
    if opts.vshift is not None:
        vshift_in = opts.vshift
        config["vshift"] = vshift_in
        refpars.append("vshift")
    # Smear
    if opts.smear is not None:
        smear_in = opts.smear
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

    # Now remove non-refinable parameters
    if opts.exclude is not None:
        refpars = list(set(refpars) - set(opts.exclude))

    # Refine or execute the morph
    refiner = refine.Refiner(chain, x_morph, y_morph, x_target, y_target)
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

    # Get Rw for the morph range
    rw = tools.getRw(chain)
    pcc = tools.get_pearson(chain)
    # Replace the MorphRGrid with Morph identity
    chain[0] = morphs.Morph()
    chain(x_morph, y_morph, x_target, y_target)

    # Input morph parameters
    morph_inputs = {
        "scale": scale_in,
        "stretch": stretch_in,
        "smear": smear_in,
    }
    morph_inputs.update({"hshift": hshift_in, "vshift": vshift_in})

    # Output morph parameters
    morph_results = dict(config.items())
    # Ensure Rw, Pearson last two outputs
    morph_results.update({"Rw": rw})
    morph_results.update({"Pearson": pcc})

    # Print summary to terminal and save morph to file if requested
    try:
        io.single_morph_output(
            morph_inputs,
            morph_results,
            save_file=opts.slocation,
            morph_file=pargs[0],
            xy_out=[chain.x_morph_out, chain.y_morph_out],
            verbose=opts.verbose,
            stdout_flag=stdout_flag,
        )

    except (FileNotFoundError, RuntimeError):
        save_fail_message = "Unable to save to designated location."
        parser.custom_error(save_fail_message)

    if opts.plot:
        pairlist = [chain.xy_morph_out, chain.xy_target_out]
        labels = [pargs[0], pargs[1]]  # Default is to use file names

        # If user chooses labels
        if opts.mlabel is not None:
            labels[0] = opts.mlabel
        if opts.tlabel is not None:
            labels[1] = opts.tlabel

        # Plot extent defaults to calculation extent
        pmin = opts.pmin if opts.pmin is not None else opts.rmin
        pmax = opts.pmax if opts.pmax is not None else opts.rmax
        maglim = opts.maglim
        mag = opts.mag
        l_width = opts.lwidth
        plot.comparePDFs(
            pairlist,
            labels,
            rmin=pmin,
            rmax=pmax,
            maglim=maglim,
            mag=mag,
            rw=rw,
            l_width=l_width,
        )

    # Return different things depending on whether it is python interfaced
    if python_wrap:
        return morph_results, chain.x_morph_out, chain.y_morph_out
    else:
        return morph_results


def multiple_targets(parser, opts, pargs, stdout_flag=True, python_wrap=False):
    # Custom error messages since usage is distinct when --multiple tag is
    # applied
    if len(pargs) < 2:
        parser.custom_error(
            "You must supply FILE and DIRECTORY. "
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
    for target in target_list:
        if target.is_dir():
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
                    "The requested field is missing from a PDF file header."
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
        "smear": opts.smear,
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

    if python_wrap:
        # FIXME: Return dictionary of morphs
        return morph_results
    else:
        return morph_results


def multiple_morphs(parser, opts, pargs, stdout_flag=True, python_wrap=False):
    # Custom error messages since usage is distinct when --multiple tag is
    # applied
    if len(pargs) < 2:
        parser.custom_error(
            "You must supply DIRECTORY and FILE. "
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
    for morph in morph_list:
        if morph.is_dir():
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
        "smear": opts.smear,
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

    if python_wrap:
        # FIXME: Return dictionary of morphs
        return morph_results
    else:
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
