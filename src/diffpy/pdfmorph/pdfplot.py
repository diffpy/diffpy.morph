#!/usr/bin/env python
##############################################################################
#
# diffpy.pdfmorph   by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2008 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################
"""Collection of plotting functions for PDFs."""

import matplotlib.pyplot as plt
import numpy
from bg_mpl_stylesheets.styles import all_styles

plt.style.use(all_styles["bg-style"])


# FIXME - make this return the figure object in the future, so several views
# can be composed.
def plotPDFs(pairlist, labels=None, offset="auto", rmin=None, rmax=None):
    """Plots several PDFs on top of one another.

    Parameters
    ----------
    pairlist
        Iterable of (r, gr) pairs to plot.
    labels
        Iterable of names for the pairs. If this is not the same length as the pairlist, a legend will not
        be shown (default []).
    offset
        Offset to place between plots. PDFs will be sequentially shifted in the y-direction by the offset.
        If offset is 'auto' (default), the optimal offset will be determined automatically.
    rmin
        The minimum r-value to plot. If this is None (default), the lower bound of the PDF is not altered.
    rmax
        The maximum r-value to plot. If this is None (default), the upper bound of the PDF is not altered.
    """
    if labels is None:
        labels = []
    if offset == "auto":
        offset = _find_offset(pairlist)

    gap = len(pairlist) - len(labels)
    labels = list(labels)
    labels.extend([""] * gap)

    for idx, pair in enumerate(pairlist):
        r, gr = pair
        plt.plot(r, gr + idx * offset, label=labels[idx])
    plt.xlim(rmin, rmax)

    if gap == 0:
        plt.legend(loc=0)

    plt.legend()
    plt.xlabel(r"$r (\mathrm{\AA})$")
    plt.ylabel(r"$G (\mathrm{\AA}^{-1})$")
    plt.show()
    return


def comparePDFs(
    pairlist,
    labels=None,
    rmin=None,
    rmax=None,
    show=True,
    maglim=None,
    mag=5,
    rw=None,
    legend=True,
    l_width=1.5,
):
    """Plot two PDFs on top of each other and difference curve.

    The second PDF will be shown as blue circles below and the first as a red line.
    The difference curve will be in green and offset for clarity.

    Parameters
    ----------
    pairlist
        Iterable of (r, gr) pairs to plot
    labels
        Iterable of names for the pairs. If this is not the same length as the pairlist, a legend will not
        be shown (default []).
    rmin
        The minimum r-value to plot. If this is None (default), the lower bound of the PDF is not altered.
    rmax
        The maximum r-value to plot. If this is None (default), the upper bound of the PDF is not altered.
    show
        Show the plot (default True)
    maglim
        Point after which to magnify the signal by mag. If None (default), no magnification will take place.
    mag
        Magnification factor (default 5)
    rw
        Rw value to display on the plot, if any.
    legend
        Display the legend (default True).
    """
    if labels is None:
        labels = [2]
        labeldata = None
        labelfit = None
    else:
        labeldata = labels[1]
        labelfit = labels[0]
    rfit, grfit = pairlist[0]
    rdat, grdat = pairlist[1]

    # View min and max
    rvmin = max(rfit[0], rdat[0])
    rvmin = rmin or rvmin
    rvmax = min(rfit[-1], rdat[-1])
    rvmax = rmax or rvmax

    gap = 2 - len(labels)
    labels = list(labels)
    labels.extend([""] * gap)

    # Put gr1 on the same grid as rdat
    gtemp = numpy.interp(rdat, rfit, grfit)

    # Calculate the difference
    diff = grdat - gtemp

    # Put rw in the label
    labeldiff = "difference" if len(labels) < 3 else labels[2]
    if rw is not None:
        labeldiff += " (Rw = %.3f)" % rw

    # Magnify if necessary
    if maglim is not None:
        grfit = grfit.copy()
        grfit[rfit > maglim] *= mag
        sel = rdat > maglim
        grdat = grdat.copy()
        grdat[sel] *= mag
        diff[sel] *= mag
        gtemp[sel] *= mag

    # Determine the offset for the difference curve.
    sel = numpy.logical_and(rdat <= rvmax, rdat >= rvmin)
    ymin = min(min(grdat[sel]), min(gtemp[sel]))
    ymax = max(diff[sel])
    offset = -1.1 * (ymax - ymin)

    # Scale the x-limit based on the r-extent of the signal. This gives a nice
    # density of PDF peaks.
    rlim = rvmax - rvmin
    scale = rlim / 25.0
    # Set a reasonable minimum of .8 and maximum of 1
    scale = min(1, max(scale, 0.8))
    figsize = [13.5, 4.5]
    figsize[0] *= scale
    fig = plt.figure(1, figsize=figsize)
    # Get the margins based on the figure size
    lm = 0.12 / scale
    bm = 0.20 / scale
    rm = 0.02 / scale
    tm = 0.15 / scale
    axes = plt.Axes(fig, [lm, bm, 1 - lm - rm, 1 - bm - tm])
    fig.add_axes(axes)
    plt.minorticks_on()

    plt.plot(rdat, grdat, linewidth=l_width, label=labeldata)
    plt.plot(rfit, grfit, linewidth=l_width, label=labelfit)
    plt.plot(rdat, offset * numpy.ones_like(diff), linewidth=3, color="black")

    diff += offset
    plt.plot(rdat, diff, linewidth=l_width, label=labeldiff)

    if maglim is not None:
        # Add a line for the magnification cutoff
        plt.axvline(
            maglim,
            0,
            1,
            linestyle="--",
            color="black",
            linewidth=1.5,
            dashes=(14, 7),
        )
        # FIXME - look for a place to put the maglim
        xpos = (rvmax * 0.85 + maglim) / 2 / (rvmax - rvmin)
        if xpos <= 0.9:
            plt.figtext(xpos, 0.7, "x%.1f" % mag, backgroundcolor="w")

    # Get a tight view
    plt.xlim(rvmin, rvmax)
    ymin = min(diff[sel])
    ymax = max(max(grdat[sel]), max(gtemp[sel]))
    yspan = ymax - ymin
    # Give a small border to the plot
    gap = 0.05 * yspan
    ymin -= gap
    ymax += gap
    plt.ylim(ymin, ymax)

    # Make labels and legends
    plt.xlabel(r"r ($\mathrm{\AA})$")
    plt.ylabel(r"G $(\mathrm{\AA}^{-1})$")
    if legend:
        plt.legend(
            bbox_to_anchor=(0.005, 1.02, 0.99, 0.10),
            loc=3,
            ncol=3,
            mode="expand",
            borderaxespad=0,
        )
    if show:
        plt.show()

    return


def plot_param(target_labels, param_list, param_name=None, field=None):
    """
    Plot Rw values for multiple morphs.

    Parameters
    ----------
    target_labels: list
        Names (or field if --sort-by given) of each file acting as target for the morph.
    param_list: list
        Contains the values of some parameter corresponding to each file.
    param_name: str
        Name of the parameter.
    field: list or None
        When not None and entries in field are numerical, a line chart of Rw versus field is made.
        When None (default) or values are non-numerical, it plots a bar chart of Rw values per file.
    """

    # ensure all entries in target_labels are distinct for plotting
    unique_labels = set()
    for idx in range(len(target_labels)):
        item = target_labels[idx]
        # if repeat found, add additional label
        if item in unique_labels:
            counter = 1
            new_name = f"{item} ({counter})"
            while new_name in unique_labels:
                counter += 1
                new_name = f"{item} ({counter})"
            item = new_name
            target_labels[idx] = item
        unique_labels.update({item})

    # Check if numerical field
    numerical = True
    if field is None:
        numerical = False
    else:
        for item in target_labels:
            if type(item) is not float:
                numerical = False

    if numerical:
        # Plot the parameter against a numerical field
        plt.plot(target_labels, param_list, linestyle="-", marker="o")
        if param_name is not None:
            plt.ylabel(rf"{param_name}")
        plt.xlabel(rf"{field}")
        plt.minorticks_on()

    # Create bar chart for each file
    else:
        # Ensure file names do not crowd
        bar_size = 1  # FIXME: depends on resolution
        max_len = bar_size
        for item in target_labels:
            max_len = max(max_len, len(item))
        angle = numpy.arccos(bar_size / max_len)
        angle *= 180 / numpy.pi  # Convert to degrees
        plt.xticks(rotation=angle)

        # Plot Rw for each file
        plt.bar(target_labels, param_list)
        if param_name is not None:
            plt.ylabel(rf"{param_name}")
        if field is None:
            plt.xlabel(r"Target File")
        else:
            plt.xlabel(rf"{field}")

    # Show plot
    plt.tight_layout()
    plt.show()

    return


def truncatePDFs(r, gr, rmin=None, rmax=None):
    """Truncate a PDF to specified bounds.

    Parameters
    ----------
    r
        r-values of the PDF.
    gr
        PDF g(r) values.
    rmin
        The minimum r-value. If this is None (default), the lower bound of the PDF is not altered.
    rmax
        The maximum r-value. If this is None (default), the upper bound of the PDF is not altered.

    Returns
    -------
    r, gr
        Returns the truncated r, gr.
    """

    if rmin is not None:
        sel = r >= rmin
        gr = gr[sel]
        r = r[sel]
    if rmax is not None:
        sel = r <= rmax
        gr = gr[sel]
        r = r[sel]

    return r, gr


def _find_offset(pairlist):
    """Find an optimal offset between PDFs."""
    maxlist = [max(p[1]) for p in pairlist]
    minlist = [min(p[1]) for p in pairlist]
    difflist = numpy.subtract(maxlist[:-1], minlist[1:])
    offset = 1.1 * max(difflist)
    return offset
