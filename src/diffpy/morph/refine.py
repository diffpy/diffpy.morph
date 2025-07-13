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
"""refine -- Refine a morph or morph chain
"""

from numpy import array, concatenate, dot, exp, ones_like
from scipy.optimize import leastsq
from scipy.stats import pearsonr

# Map of scipy minimizer names to the method that uses them


class Refiner(object):
    """Class for refining a Morph or MorphChain.

    This is provided to allow for custom residuals and refinement algorithms.

    Attributes
    ----------
    chain
        The Morph or MorphChain to refine.
    x_morph, y_morph
        Morphed arrays.
    x_target, y_target
        Target arrays.
    pars
        List of names of parameters to be refined.
    residual
        The residual function to optimize. Default _residual. Can be assigned
        to other functions.
    """

    def __init__(
        self, chain, x_morph, y_morph, x_target, y_target, tolerance=1e-08
    ):
        self.chain = chain
        self.x_morph = x_morph
        self.y_morph = y_morph
        self.x_target = x_target
        self.y_target = y_target
        self.tolerance = tolerance
        self.pars = []
        self.residual = self._residual
        self.flat_to_grouped = {}

        # Padding required for the residual vector to ensure constant length
        # across the entire morph process
        self.res_length = None
        return

    def _update_chain(self, pvals):
        """Update the parameters in the chain."""
        updated = {}
        for idx, value in enumerate(pvals):
            param, subkey = self.flat_to_grouped[idx]
            if subkey is None:  # Scalar
                updated[param] = value
            else:
                if param not in updated:
                    updated[param] = {}
                updated[param][subkey] = value

        # Apply the reconstructed grouped parameter back to config
        self.chain.config.update(updated)
        return

    def _residual(self, pvals):
        """Standard vector residual."""
        self._update_chain(pvals)
        _x_morph, _y_morph, _x_target, _y_target = self.chain(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )
        rvec = _y_target - _y_morph

        # If first time computing residual
        if self.res_length is None:
            self.res_length = len(rvec)
        # Ensure residual length is constant
        else:
            # Padding
            if len(rvec) < self.res_length:
                diff_length = self.res_length - len(rvec)
                rvec = list(rvec)
                rvec.extend([0] * diff_length)
                rvec = array(rvec)
            # Removal
            elif len(rvec) > self.res_length:
                diff_length = len(rvec) - self.res_length
                rvec = list(rvec)
                for _ in range(diff_length):
                    rvec.pop(max(rvec))
                rvec = array(rvec)

        return rvec

    def _pearson(self, pvals):
        """Pearson correlation function.

        This gives e**-p (vector), where p is the pearson correlation
        function. We seek to minimize this, which occurs when the
        correlation is the largest.
        """
        self._update_chain(pvals)
        _x_morph, _y_morph, _x_target, _y_target = self.chain(
            self.x_morph, self.y_morph, self.x_target, self.y_target
        )
        pcc, pval = pearsonr(_y_morph, _y_target)
        return ones_like(_x_morph) * exp(-pcc)

    def _add_pearson(self, pvals):
        """Refine both the pearson and residual."""
        res1 = self._residual(pvals)
        res2 = self._pearson(pvals)
        res = concatenate([res1, res2])
        return res

    def refine(self, *args, **kw):
        """Refine the chain.

        Additional arguments are used to specify which parameters are to be
        refined.
        If no arguments are passed, then all parameters will be refined.
        Keywords pass initial values to the parameters, whether or not they
        are refined.

        This uses the leastsq algorithm from scipy.optimize.

        This returns the final scalar residual value.
        The parameters from the fit can be retrieved from the config
        dictionary of the morph or morph chain.

        Raises
        ------
        ValueError
            Exception raised if a minimum cannot be found.
        """

        self.pars = args or self.chain.config.keys()

        config = self.chain.config
        config.update(kw)

        if not self.pars:
            return 0.0

        # Build flat list of initial parameters and flat_to_grouped mapping
        initial = []
        self.flat_to_grouped = {}

        for p in self.pars:
            val = config[p]
            if isinstance(val, dict):
                for k, v in val.items():
                    initial.append(v)
                    self.flat_to_grouped[len(initial) - 1] = (p, k)
            else:
                initial.append(val)
                self.flat_to_grouped[len(initial) - 1] = (p, None)

        sol, cov_sol, infodict, emesg, ier = leastsq(
            self.residual,
            array(initial),
            full_output=True,
            ftol=self.tolerance,
            xtol=self.tolerance,
        )
        fvec = infodict["fvec"]

        if ier not in (1, 2, 3, 4):
            emesg
            raise ValueError(emesg)

        # Place the fit parameters in config
        vals = sol
        if not hasattr(vals, "__iter__"):
            vals = [vals]
        self._update_chain(vals)

        return dot(fvec, fvec)


# End class Refiner
