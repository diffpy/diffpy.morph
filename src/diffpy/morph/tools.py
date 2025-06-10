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
"""Tools used in morphs and morph chains."""


import numpy

from diffpy.utils.parsers.loaddata import loadData
from diffpy.utils.parsers.serialization import deserialize_data


def estimateScale(y_morph_in, y_target_in):
    """Set the scale that best matches the morph to the target."""
    dot = numpy.dot
    scale = dot(y_morph_in, y_target_in) / dot(y_morph_in, y_morph_in)
    return scale


def estimateBaselineSlope(r, gr, rmin=None, rmax=None):
    """Estimate the slope of the linear baseline of a PDF.

    This fits a slope into the equation slope*r through the bottom of the PDF.

    Parameters
    ----------
    r
        The r-grid used for the PDF.
    gr
        The PDF over the r-grid.
    rmin
        The minimum r-value to consider. If this is None (default) is None,
        then the minimum of r is used.
    rmax
        The maximum r-value to consider. If this is None (default) is None,
        then the maximum of r is used.

    Returns
    -------
    slope: float
        The slope of baseline. If the PDF is scaled properly, this is equal
        to -4*pi*rho0.
    """
    from numpy import dot
    from scipy.optimize import leastsq

    rp = r.copy()
    grp = gr.copy()
    if rmax is not None:
        grp = grp[rp <= rmax]
        rp = rp[rp <= rmax]
    if rmin is not None:
        grp = grp[rp >= rmin]
        rp = rp[rp >= rmin]

    def chiv(pars):
        slope = pars[0]
        # This tries to fit the baseline through the center of the PDF.
        chiv = grp - slope * rp

        # This adds additional penalty if there are negative terms, that
        # is, if baseline > PDF.
        diff = chiv.copy()
        diff[diff > 0] = 0
        negpenalty = dot(diff, diff)
        chiv *= 1 + 0.5 * negpenalty

        return chiv

    # Optimize to get the best slope
    slope, ier = leastsq(chiv, [0.0])

    # Return the slope
    return slope


def getRw(chain):
    """Get Rw from the outputs of a morph or chain."""
    # Make sure we put these on the proper grid
    x_morph, y_morph, x_target, y_target = chain.xyallout
    diff = y_target - y_morph
    rw = numpy.dot(diff, diff)
    rw /= numpy.dot(y_target, y_target)
    rw = rw**0.5
    return rw


def get_pearson(chain):
    from scipy.stats import pearsonr

    x_morph, y_morph, x_target, y_target = chain.xyallout
    pcc, pval = pearsonr(y_morph, y_target)
    return pcc


def readPDF(fname):
    """Reads an .gr file, loads r and G(r) vectors.

    Parameters
    ----------
    fname
        Name of the file we want to read.

    Returns
    -------
    r,gr
        Arrays read from data.
    """

    rv = loadData(fname, unpack=True)
    if len(rv) >= 2:
        return rv[:2]
    return (None, None)


def nn_value(val, name):
    """Convenience function for ensuring certain non-negative inputs."""
    if val < 0:
        negative_value_warning = (
            f"\n# Negative value for {name} given. "
            "Using absolute value instead."
        )
        print(negative_value_warning)
        return -val
    return val


def deserialize(serial_file):
    """Call deserialize_data from diffpy.utils.

    Parameters
    ----------
    serial_file
        Name of file to deserialize.

    Returns
    -------
    dict
        Data read from serial file.
    """
    return deserialize_data(serial_file)


def case_insensitive_dictionary_search(key: str, dictionary: dict):
    """Search for key in dictionary ignoring case.

    Parameters
    ----------
    key: str
    dictionary: dict

    Returns
    -------
    value or None
        Corresponding value if key is in dictionary. None otherwise.
    """

    for ci_key in dictionary.keys():
        if key.lower() == ci_key.lower():
            key = ci_key
            break

    return dictionary.get(key)


def field_sort(
    filepaths: list, field, reverse=False, serfile=None, get_field_values=False
):
    """Sort a list of files by a field stored in header information. All files
    must contain this header information.

    Parameters
    ----------
    filepaths
        List of paths to files that we want to sort.
    field
        The field we want to sort by. Not case-sensitive.
    reverse
        Sort in reverse alphabetical/numerical order.
    serfile
        Path to a serial file with field information for each file.
    get_field_values: bool
        Boolean indicating whether to also return a List of field values
        (default False). This List of field values is parallel to the sorted
        list of filepaths with items in the same position corresponding to
        each other.

    Returns
    -------
    list
        Sorted list of paths. When get_fv is true, also return an associated
        field list.
    """

    # Get the field from each file
    files_field_values = []
    if serfile is None:
        for path in filepaths:
            fhd = loadData(path, headers=True)
            files_field_values.append(
                [path, case_insensitive_dictionary_search(field, fhd)]
            )
    else:
        # deserialize the serial file
        des_dict = deserialize_data(serfile)

        # get names of each file to search the serial file
        import pathlib

        for path in filepaths:
            name = pathlib.Path(path).name
            fv = case_insensitive_dictionary_search(field, des_dict.get(name))
            files_field_values.append([path, fv])

    # Sort files by field, reverse if reverse flag true
    try:
        files_field_values.sort(key=lambda entry: entry[1], reverse=reverse)
    # Raised if fields for any file are missing
    except (ValueError, TypeError):
        raise KeyError("Field missing.")
    if get_field_values:
        return [pair[0] for pair in files_field_values], [
            pair[1] for pair in files_field_values
        ]
    else:
        return [pair[0] for pair in files_field_values]


def get_values_from_dictionary_collection(
    dictionary_collection: iter, target_key
):
    """In an (iterable) collection of dictionaries, search for a target key in
    each dictionary. Return a list of all found values corresponding to that
    key.

    Parameters
    ----------
    dictionary_collection: iter
        The collection of dictionaries to search through.
    target_key
        The key to search for in each dictionary. For each dictionary in
        dictionary_collection that has that key, the corresponding value is
        appended to a List called values.

    Returns
    -------
    list
        The found values.
    """

    # Store all values corresponding to the target_key into this list
    values = []

    # Handle dictionary-type iterable
    if type(dictionary_collection) is dict:
        # Assume the dictionaries are stored in the values and keys indicate
        # names of the dictionaries
        dictionary_collection = dictionary_collection.values()
    # All other type iterables are handled the same way as a list

    # Perform the (case-insensitive) search
    for entry in dictionary_collection:
        search_result = case_insensitive_dictionary_search(target_key, entry)
        if search_result is not None:
            values.append(search_result)
    return values
