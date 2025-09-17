"""Class MorphSqueeze -- Apply a polynomial to squeeze the morph
function."""

import numpy
from numpy.polynomial import Polynomial
from scipy.interpolate import CubicSpline

from diffpy.morph.morphs.morph import LABEL_GR, LABEL_RA, Morph


class MorphSqueeze(Morph):
    """Squeeze the morph function.

    This applies a polynomial to squeeze the morph non-linearly.

    Configuration Variables
    -----------------------
    squeeze : Dictionary
        The polynomial coefficients {a0, a1, ..., an} for the squeeze
        function where the polynomial would be of the form
        a0 + a1*x + a2*x^2 and so on.  The order of the polynomial is
        determined by the length of the dictionary.

    Returns
    -------
        A tuple (x_morph_out, y_morph_out, x_target_out, y_target_out)
        where the target values remain the same and the morph data is
        shifted according to the squeeze. The morphed data is returned on
        the same grid as the unmorphed data.

    Example
    -------
    Import the squeeze morph function:

        >>> from diffpy.morph.morphs.morphsqueeze import MorphSqueeze

    Provide initial guess for squeezing coefficients:

        >>> squeeze_coeff = {"a0":0.1, "a1":-0.01, "a2":0.005}

    Run the squeeze morph given input morph array (x_morph, y_morph) and target
    array (x_target, y_target):

        >>> morph = MorphSqueeze()
        >>> morph.squeeze = squeeze_coeff
        >>> x_morph_out, y_morph_out, x_target_out, y_target_out =
        ... morph(x_morph, y_morph, x_target, y_target)

    To access parameters from the morph instance:

        >>> x_morph_in = morph.x_morph_in
        >>> y_morph_in = morph.y_morph_in
        >>> x_target_in = morph.x_target_in
        >>> y_target_in = morph.y_target_in
        >>> squeeze_coeff_out = morph.squeeze
    """

    # Define input output types
    summary = "Squeeze morph by polynomial shift"
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["squeeze"]
    # extrap_index_low: last index before interpolation region
    # extrap_index_high: first index after interpolation region
    extrap_index_low = None
    extrap_index_high = None
    squeeze_cutoff_low = None
    squeeze_cutoff_high = None

    def __init__(self, config=None, check_increase=False):
        super().__init__(config)
        self.check_increase = check_increase

    def _set_squeeze_info(self, x, x_sorted):
        self.squeeze_info = {"monotonic": True, "overlapping_regions": None}
        if list(x) != list(x_sorted):
            if self.check_increase:
                raise ValueError(
                    "Error: The polynomial applied by the squeeze morph has "
                    "resulted in a grid that is no longer strictly increasing"
                    ", likely due to a convergence issue. A strictly "
                    "increasing grid is required for diffpy.morph to compute "
                    "the morphed function through cubic spline interpolation. "
                    "Here are some suggested methods to resolve this:\n"
                    "(1) Please decrease the order of your polynomial and "
                    "try again.\n"
                    "(2) If you are using initial guesses of all 0, please "
                    "ensure your objective function only requires a small "
                    "polynomial squeeze to match your reference. (In other "
                    "words, there is good agreement between the two functions"
                    ".)\n"
                    "(3) If you expect a large polynomial squeeze to be needed"
                    ", please ensure your initial parameters for the "
                    "polynomial morph result in good agreement between your "
                    "reference and objective functions. One way to obtain "
                    "such parameters is to first apply a --hshift and "
                    "--stretch morph. Then, use the hshift parameter for a0 "
                    "and stretch parameter for a1."
                )
            else:
                overlapping_regions = self._get_overlapping_regions(x)
                self.squeeze_info["monotonic"] = False
                self.squeeze_info["overlapping_regions"] = overlapping_regions

    def _sort_squeeze(self, x, y):
        """Sort x,y according to the value of x."""
        xy = list(zip(x, y))
        xy_sorted = sorted(xy, key=lambda pair: pair[0])
        x_sorted, y_sorted = list(zip(*xy_sorted))
        return x_sorted, y_sorted

    def _get_overlapping_regions(self, x):
        diffx = numpy.diff(x)
        monotomic_regions = []
        monotomic_signs = [numpy.sign(diffx[0])]
        current_region = [x[0], x[1]]
        for i in range(1, len(diffx)):
            if numpy.sign(diffx[i]) == monotomic_signs[-1]:
                current_region.append(x[i + 1])
            else:
                monotomic_regions.append(current_region)
                monotomic_signs.append(diffx[i])
                current_region = [x[i + 1]]
        monotomic_regions.append(current_region)
        overlapping_regions_sign = -1 if x[0] < x[-1] else 1
        overlapping_regions_x = [
            monotomic_regions[i]
            for i in range(len(monotomic_regions))
            if monotomic_signs[i] == overlapping_regions_sign
        ]
        overlapping_regions = [
            (min(region), max(region)) for region in overlapping_regions_x
        ]
        return overlapping_regions

    def _handle_duplicates(self, x, y):
        """Remove duplicated x and use the mean value of y corresponded
        to the duplicated x."""
        unq_x, unq_inv = numpy.unique(x, return_inverse=True)
        if len(unq_x) == len(x):
            return x, y
        else:
            y_avg = numpy.zeros_like(unq_x)
            for i in range(len(unq_x)):
                y_avg[i] = numpy.array(y)[unq_inv == i].mean()
            return unq_x, y_avg

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Apply a polynomial to squeeze the morph function.

        The morphed data is returned on the same grid as the unmorphed
        data.
        """
        Morph.morph(self, x_morph, y_morph, x_target, y_target)

        coeffs = [self.squeeze[f"a{i}"] for i in range(len(self.squeeze))]
        squeeze_polynomial = Polynomial(coeffs)
        x_squeezed = self.x_morph_in + squeeze_polynomial(self.x_morph_in)
        x_squeezed_sorted, y_morph_sorted = self._sort_squeeze(
            x_squeezed, self.y_morph_in
        )
        self._set_squeeze_info(x_squeezed, x_squeezed_sorted)
        x_squeezed_sorted, y_morph_sorted = self._handle_duplicates(
            x_squeezed_sorted, y_morph_sorted
        )
        self.y_morph_out = CubicSpline(x_squeezed_sorted, y_morph_sorted)(
            self.x_morph_in
        )
        self.set_extrapolation_info(x_squeezed_sorted, self.x_morph_in)

        return self.xyallout
