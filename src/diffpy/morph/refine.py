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
"""refine -- Refine a morph or morph chain"""

import warnings

from numpy import array, concatenate, diag, dot, exp, ones_like, sqrt
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
        if len(rvec) < len(pvals):
            raise ValueError(
                f"\nNumber of parameters (currently {len(pvals)}) cannot "
                "exceed the number of shared grid points "
                f"(currently {len(rvec)}). "
                "Please reduce the number of morphing parameters or "
                "provide new morphing and target functions with more "
                "shared grid points."
            )
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
            # For removal, pass the average RMS
            # This is fast and easy to compute
            # For sufficiently functions, this approximation becomes exact
            elif len(rvec) > self.res_length:
                avg_rms = sum(rvec**2) / len(rvec)
                rvec = array([avg_rms for _ in range(self.res_length)])

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

    def refine(self, *args, estimate_uncertainty=False, **kw):
        """Refine the chain.

        Additional arguments are used to specify which parameters are to be
        refined.
        If no arguments are passed, then all parameters will be refined.
        Keywords pass initial values to the parameters, whether or not they
        are refined.

        This uses the leastsq algorithm from scipy.optimize.

        If estimate_uncertainty is True, return an estimated uncertainty
        for each parameter.
        Otherwise, return the final scalar residual value (used for testing).
        The parameters from the fit can be retrieved from the config
        dictionary of the morph or morph chain.

        Raises
        ------
        ValueError
            Exception raised if a minimum cannot be found.
        ValueError
            If the number of shared grid points between morphed function and
            target function is smaller than the number of parameters.
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

        sol, hess_inv_sol, infodict, emesg, ier = leastsq(
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

        if estimate_uncertainty:
            par_names = list(self.pars)
            if hess_inv_sol is None:
                if len(par_names) == 1:
                    warnings.warn(
                        "Warning: Could not estimate "
                        f"uncertainty of {par_names[0].lower()} parameter "
                        "as estimated Hessian is singular.",
                        UserWarning,
                    )
                else:
                    warnings.warn(
                        "Warning: Certain parameters may be "
                        "missing uncertainties as estimated Hessian "
                        "is singular.",
                        UserWarning,
                    )
                return None
            dof = len(fvec) - len(sol)
            if dof <= 0:
                warnings.warn(
                    "Warning: Could not estimate "
                    "uncertainty as the number of fit parameters "
                    "exceeds the number of data points.",
                    UserWarning,
                )
                return None
            # Handle squeeze morph params
            if "squeeze" in par_names and "squeeze" in config.keys():
                squeeze_par_names = [
                    f"squeeze a{i}"
                    for i in range(len(config["squeeze"].keys()))
                ]
                squeeze_idx = par_names.index("squeeze")
                par_names[squeeze_idx : squeeze_idx + 1] = squeeze_par_names
            # Handle funcx, funcy, funcxy morph params
            func_types = ["funcx", "funcy", "funcxy"]
            for func in func_types:
                if func in par_names and func in config.keys():
                    func_par_names = [
                        f"{func} {fparam}" for fparam in config[func].keys()
                    ]
                    func_idx = par_names.index(func)
                    par_names[func_idx : func_idx + 1] = func_par_names
            cov_sol = hess_inv_sol * dot(fvec, fvec) / dof
            unc = sqrt(diag(cov_sol))

            return dict(zip(par_names, unc))
        else:
            return dot(fvec, fvec)


# End class Refiner
