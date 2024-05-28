#!/usr/bin/env python
##############################################################################
#
# diffpy.pdfmorph   by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################


from __future__ import print_function

import sys
from pathlib import Path

import numpy

import diffpy.pdfmorph.tools as tools
from diffpy.pdfmorph import __save_morph_as__


def single_morph_output(
    morph_inputs,
    morph_results,
    save_file=None,
    morph_file=None,
    xy_out=None,
    verbose=False,
    stdout_flag=False,
):
    """Helper function for printing details about a single morph.
     Handles both printing to terminal and printing to a file.

    Parameters
    ----------
    morph_inputs: dict
        Parameters given by the user.
    morph_results: dict
        Resulting data after morphing.
    save_file
        Name of file to print to. If None (defualt) print to terminal.
    morph_file
        Name of the morphed PDF file. Required when printing to a non-terminal file.
    param xy_out: list
        List of the form [x_morph_out, y_morph_out]. x_morph_out is a List of r values
         and y_morph_out is a List of gr values.
    verbose: bool
        Print additional details about the morph when True (default False).
    stdout_flag: bool
        Print to terminal when True (default False).
    """

    # Input and output parameters
    morphs_in = "\n# Input morphing parameters:\n"
    morphs_in += "\n".join(f"# {key} = {morph_inputs[key]}" for key in morph_inputs.keys()) + "\n"

    morphs_out = "# Optimized morphing parameters:\n"
    morphs_out += "\n".join(f"# {key} = {morph_results[key]: .6f}" for key in morph_results.keys())

    # Printing to terminal
    if stdout_flag:
        print(f"{morphs_in}\n{morphs_out}\n")

    # Saving to file
    if save_file is not None:
        path_name = str(Path(morph_file).resolve())
        header = "# PDF created by pdfmorph\n"
        header += f"# from {path_name}"

        header_verbose = f"{morphs_in}\n{morphs_out}"

        if save_file != "-":
            with open(save_file, "w") as outfile:
                # Print out a header (more if verbose)
                print(header, file=outfile)
                if verbose:
                    print(header_verbose, file=outfile)

                # Print table with label
                print("\n# Labels: [r] [gr]", file=outfile)
                numpy.savetxt(outfile, numpy.transpose(xy_out))

            if stdout_flag:
                # Indicate successful save
                save_message = f"# Morph saved to {save_file}\n"
                print(save_message)

        else:
            # Just print table with label if save is to stdout
            print("# Labels: [r] [gr]")
            numpy.savetxt(sys.stdout, numpy.transpose(xy_out))


def create_morphs_directory(save_directory):
    """Create a directory for saving multiple morphed PDFs.

    Takes in a user-given path to a directory save_directory and create a subdirectory named Morphs.
     PDFmorph will save all morphs into the Morphs subdirectory while metadata about the morphs will
     be stored in save_directory outside Morphs.

    Parameters
    ----------
    save_directory
        Path to a directory. PDFmorph will save all generated files within this directory.

    Returns
    -------
    str
        The absolute path to the Morph subdirectory.
    """
    # Make directory to save files in if it does not already exist
    Path(save_directory).mkdir(parents=True, exist_ok=True)

    # Morphs will be saved in the subdirectory "Morphs"
    morphs_subdirectory = Path(save_directory).joinpath("Morphs")
    morphs_subdirectory.mkdir(exist_ok=True)

    return str(morphs_subdirectory.resolve())


def get_multisave_names(target_list: list, save_names_file=None):
    """Create or import a dictionary that specifies names to save morphs as.
     First attempt to import names from a specified file. If names for certain morphs not found,
     use default naming scheme: 'Morph_with_Target_<target file name>.cgr'.

    Used when saving multiple morphs.

    Parameters
    ----------
    target_list: list
        Target PDFs used for each morph.
    save_names_file
        Name of file to import save names dictionary from (default None).

    Returns
    -------
    dict
        The names to save each morph as. Keys are the target PDF file names used to produce that morph.
    """

    # Dictionary storing save file names
    save_names = {}

    # Import names from a serial file
    if save_names_file is not None:
        # Names should be stored properly in save_names_file
        save_names = tools.deserialize(save_names_file)
    # Apply default naming scheme to missing targets
    for target_file in target_list:
        if target_file.name not in save_names.keys():
            save_names.update({target_file.name: {__save_morph_as__: f"Morph_with_Target_{target_file.stem}.cgr"}})
    return save_names


def multiple_morph_output(
    morph_inputs,
    morph_results,
    target_files,
    field=None,
    field_list=None,
    save_directory=None,
    morph_file=None,
    target_directory=None,
    verbose=False,
    stdout_flag=False,
):
    """Helper function for printing details about a series of multiple morphs.
     Handles both printing to terminal and printing to a file.

    Parameters
    ----------
    morph_inputs: dict
        Input parameters given by the user.
    morph_results: dict
        Resulting data after morphing.
    target_files: list
        PDF files that acted as targets to morphs.
    save_directory
        Name of directory to save morphs in.
    field
        Name of field if data was sorted by a particular field. Otherwise, leave blank.
    field_list: list
        List of field values for each target PDF. Generated by diffpy.pdfmorph.tools.field_sort().
    morph_file
        Name of the morphed PDF file. Required to give summary data after saving to a directory.
    target_directory
        Name of the directory containing the target PDF files.
         Required to give summary data after saving to a directory.
    verbose: bool
        Print additional summary details when True (default False).
    stdout_flag: bool
        Print to terminal when True (default False).
    """

    # Input parameters used for every morph
    inputs = "\n# Input morphing parameters:\n"
    inputs += "\n".join(f"# {key} = {morph_inputs[key]}" for key in morph_inputs.keys())

    # Verbose to get output for every morph
    verbose_outputs = ""
    if verbose:
        # Output for every morph (information repeated in a succinct table below)
        for target in morph_results.keys():
            output = f"\n# Target: {target}\n"
            output += "# Optimized morphing parameters:\n"
            output += "\n".join(
                f"# {param} = {morph_results[target][param]: .6f}" for param in morph_results[target]
            )
            verbose_outputs += f"{output}\n"

    # Get items we want to put in table
    tabulated_results = tabulate_results(morph_results)

    # Table labels
    labels = "\n# Labels: [Target]"
    if field is not None:
        labels += f" [{field}]"
    for param in tabulated_results.keys():
        if len(tabulated_results[param]) > 0:
            labels += f" [{param}]"

    # Corresponding table
    table = f"{labels}\n"
    for idx in range(len(target_files)):
        row = f"{target_files[idx]}"
        if field_list is not None:
            row += f" {field_list[idx]}"
        for param in tabulated_results.keys():
            if len(tabulated_results[param]) > idx:
                row += f" {tabulated_results[param][idx]: 0.6f}"
        table += f"{row}\n"
    table = table[:-1]  # Remove extra indent

    # Printing summary to terminal
    if stdout_flag:
        print(f"{inputs}\n{verbose_outputs}{table}\n")

    # Saving summary as a file
    if save_directory is not None:
        morph_path_name = str(Path(morph_file).resolve())
        target_path_name = str(Path(target_directory).resolve())

        header = "# Data generated by pdfmorph\n"
        header += f"# from morphing {morph_path_name}\n"
        header += f"# with target directory {target_path_name}"
        reference_table = Path(save_directory).joinpath("Morph_Reference_Table.csv")
        with open(reference_table, "w") as reference:
            print(f"{header}\n{inputs}\n{verbose_outputs}{table}", file=reference)

        if stdout_flag:
            # Indicate successful save
            save_message = f"# Morphs saved in the directory {save_directory}\n"
            print(save_message)


def tabulate_results(multiple_morph_results):
    """Helper function to make a data table summarizing details about the results of multiple morphs.

    Parameters
    ----------
    multiple_morph_results
        A collection of Dictionaries. Each Dictionary summarizes the resultsof a single morph.

    Returns
    -------
    tabulated_results: dict
        Keys in tabulated_results are the table's column names and each corresponding value is a list
         of data for that column.
    """

    # We only care about the following parameters in our data tables
    relevant_parameters = ["Scale", "Smear", "Stretch", "Pearson", "Rw"]

    # Keys in this table represent column names and the value will be a list of column data
    tabulated_results = {}
    for param in relevant_parameters:
        tabulated_results.update(
            {param: tools.get_values_from_dictionary_collection(multiple_morph_results, param)}
        )
    return tabulated_results
