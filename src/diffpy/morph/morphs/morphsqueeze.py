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
    strictly_increasing = None

    def __init__(self, config=None):
        super().__init__(config)

    def _check_strictly_increasing(self, x, x_sorted):
        if list(x) != list(x_sorted):
            self.strictly_increasing = False
        else:
            self.strictly_increasing = True

    def _sort_squeeze(self, x, y):
        """Sort x,y according to the value of x."""
        xy = list(zip(x, y))
        xy_sorted = sorted(xy, key=lambda pair: pair[0])
        x_sorted, y_sorted = numpy.array(list(zip(*xy_sorted)))
        return x_sorted, y_sorted

    def _handle_duplicates(self, x, y):
        """Remove duplicated x and use the mean value of y corresponded
        to the duplicated x."""
        x_unique, inv = numpy.unique(x, return_inverse=True)
        if len(x_unique) == len(x):
            return x, y
        else:
            y_avg = numpy.zeros_like(x_unique)
            for idx, _ in enumerate(x_unique):
                y_avg[idx] = y[inv == idx].mean()
            return x_unique, y_avg

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
        self._check_strictly_increasing(x_squeezed, x_squeezed_sorted)
        x_squeezed_sorted, y_morph_sorted = self._handle_duplicates(
            x_squeezed_sorted, y_morph_sorted
        )
        self.y_morph_out = CubicSpline(x_squeezed_sorted, y_morph_sorted)(
            self.x_morph_in
        )
        self.set_extrapolation_info(x_squeezed_sorted, self.x_morph_in)

        return self.xyallout
