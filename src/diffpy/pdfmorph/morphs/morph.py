#!/usr/bin/env python
##############################################################################
#
# diffpy.pdfmorph   by DANSE Diffraction group
#                   Simon J. L. Billinge
#                   (c) 2010 Trustees of the Columbia University
#                   in the City of New York.  All rights reserved.
#
# File coded by:    Pavol Juhas, Chris Farrow
#
# See AUTHORS.txt for a list of people who contributed.
# See LICENSE.txt for license information.
#
##############################################################################
"""Morph -- base class for defining a morph.
"""


LABEL_RA = "r (A)"  # r-grid
LABEL_GR = "G (1/A^2)"  # PDF G(r)
LABEL_RR = "R (1/A)"  # RDF R(r)


class Morph(object):
    """Base class for implementing a morph given a target.

    Adapted from diffpy.pdfgetx to include two sets of arrays that get passed
    through.

    Attributes are taken from config when not found locally. The morph may
    modify the config dictionary. This is the means by which to communicate
    automatically modified attributes.

    Class Attributes
    ----------------
    summary
        Short description of a morph.
    xinlabel
        Descriptive label for the x input array.
    yinlabel
        Descriptive label for the y input array.
    xoutlabel
        Descriptive label for the x output array.
    youtlabel
        Descriptive label for the y output array.
    parnames: list
        Names of configuration variables.

    Instance Attributes
    -------------------
    config: dict
        All configuration variables.
    x_morph_in
        Last morph input x data.
    y_morph_in
        Last morph input y data.
    x_morph_out
        Last morph result x data.
    y_morph_out
        Last morph result y data.
    x_target_in
        Last target input x data.
    y_target_in
        Last target input y data.
    x_target_out
        Last target result x data.
    y_target_out
        Last target result y data.

    Properties
    ----------
    xy_morph_in
        Tuple of (x_morph_in, y_morph_in).
    xy_morph_out
        Tuple of (x_morph_out, y_morph_out).
    xy_target_in
        Tuple of (x_target_in, y_target_in).
    xy_target_out
        Tuple of (x_target_out, y_target_out).
    xyallout
        Tuple of (x_morph_out, y_morph_out, x_target_out, y_target_out).
    """

    # Class variables
    # default array types are empty
    summary = "identity transformation"
    xinlabel = "x"
    yinlabel = "y"
    xoutlabel = "x"
    youtlabel = "y"
    parnames = []

    # Properties

    xy_morph_in = property(
        lambda self: (self.x_morph_in, self.y_morph_in),
        doc="Return a tuple of morph input arrays",
    )
    xy_morph_out = property(
        lambda self: (self.x_morph_out, self.y_morph_out),
        doc="Return a tuple of morph output arrays",
    )
    xy_target_in = property(
        lambda self: (self.x_target_in, self.y_target_in),
        doc="Return a tuple of target input arrays",
    )
    xy_target_out = property(
        lambda self: (self.x_target_out, self.y_target_out),
        doc="Return a tuple of target output arrays",
    )
    xyallout = property(
        lambda self: (
            self.x_morph_out,
            self.y_morph_out,
            self.x_target_out,
            self.y_target_out,
        ),
        doc="Return a tuple of all output arrays",
    )

    def __init__(self, config=None):
        """Create a default Morph instance.

        config: dict
            All configuration variables.
        """
        # declare empty attributes
        if config is None:
            config = {}
        self.x_morph_in = None
        self.y_morph_in = None
        self.x_morph_out = None
        self.y_morph_out = None
        self.x_target_in = None
        self.y_target_in = None
        self.x_target_out = None
        self.y_target_out = None
        # process arguments
        self.applyConfig(config)
        return

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Morph arrays morphed or target.

        Identity operation.
        This method should be overloaded in a derived class.

        Parameters
        ----------
        x_morph, y_morph
            Morphed arrays.
        x_target, y_target
            Target arrays.

        Returns
        -------
        tuple
            A tuple of numpy arrays
            (x_morph_out, y_morph_out, x_target_out, y_target_out)
        """
        self.x_morph_in = x_morph
        self.y_morph_in = y_morph
        self.x_target_in = x_target
        self.y_target_in = y_target
        self.x_morph_out = x_morph.copy()
        self.y_morph_out = y_morph.copy()
        self.x_target_out = x_target.copy()
        self.y_target_out = y_target.copy()
        self.checkConfig()
        return self.xyallout

    def __call__(self, x_morph, y_morph, x_target, y_target):
        """Alias for morph."""
        return self.morph(x_morph, y_morph, x_target, y_target)

    def applyConfig(self, config):
        """Process any configuration data from a dictionary.

        Parameters
        ----------
        config: dict
            Configuration dictionary.

        Returns
        -------
        No return value.
        """
        self.config = config
        return

    def checkConfig(self):
        """Verify data in self.config. No action by default.

        To be overridden in a derived class.
        """
        return

    def plotInputs(self, xylabels=True):
        """Plot input arrays using matplotlib.pyplot.

        Parameters
        ----------
        xylabels
            Flag for updating x and y axes labels.

        Returns
        -------
        list:
            A list of matplotlib line objects.
        """
        from matplotlib.pyplot import plot, xlabel, ylabel

        rv = plot(self.x_target_in, self.y_target_in, label="target")
        rv = plot(self.x_morph_in, self.y_morph_in, label="morph")
        if xylabels:
            xlabel(self.xinlabel)
            ylabel(self.yinlabel)
        return rv

    def plotOutputs(self, xylabels=True, **plotargs):
        """Plot output arrays using matplotlib.pyplot.

        Parameters
        ----------
        xylabels: bool
            Flag for updating x and y axes labels.
        plotargs
            Arguments passed to the pylab plot function.
            Note that "label" will be ignored.

        Returns
        -------
        list
            A list of matplotlib line objects.
        """
        from matplotlib.pyplot import plot, xlabel, ylabel

        pargs = dict(plotargs)
        pargs.pop("label", None)
        rv = plot(
            self.x_target_out, self.y_target_out, label="target", **pargs
        )
        rv = plot(self.x_morph_out, self.y_morph_out, label="morph", **pargs)
        if xylabels:
            xlabel(self.xoutlabel)
            ylabel(self.youtlabel)
        return rv

    def __getattr__(self, name):
        """Obtain the value from self.config, when normal lookup fails.

        Parameters
        ----------
        name
            Name of the attribute to be recovered.

        Returns
        -------
        self.config.get(name)

        Raises
        ------
        AttributeError
            Name is not available from self.config.
        """
        if name in self.config:
            return self.config[name]
        else:
            emsg = "Object has no attribute %r" % name
            raise AttributeError(emsg)

    def __setattr__(self, name, val):
        """Set configuration variables to config.

        Parameters
        ----------
        name
            Name of the attribute.
        val
            Value of the attribute.
        """
        if name in self.parnames:
            self.config[name] = val
        else:
            object.__setattr__(self, name, val)
        return


# End class Morph
