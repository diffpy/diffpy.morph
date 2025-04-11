from diffpy.morph.morphs.morph import LABEL_GR, LABEL_RA, Morph


class MorphSqueeze(Morph):
    """Squeeze the morph function.

    This applies a polynomial to squeeze the morph non-linearly. The morphed
    data is returned on the same grid as the unmorphed data.

    Configuration Variables
    -----------------------
    squeeze : list
        The polynomial coefficients [a0, a1, ..., an] for the squeeze function
        where the polynomial would be of the form a0 + a1*x + a2*x^2 and so
        on.  The order of the polynomial is determined by the length of the
        list.

    Example
    -------
    >>> import numpy as np
    >>> from numpy.polynomial import Polynomial
    >>> from diffpy.morph.morphs.morphsqueeze import MorphSqueeze

    >>> x_morph = np.linspace(0, 10, 101)
    >>> x_target = np.linspace(0, 10, 101)
    >>> squeeze_coeff = [0.1, -0.01, 0.005]
    >>> poly = Polynomial(squeeze_coeff)
    >>> y_morph = np.sin(x_morph + poly(x_morph))
    >>> y_target = np.sin(x_target)

    >>> morph = MorphSqueeze()
    >>> morph.squeeze = squeeze_coeff
    >>> x_morph_out, y_morph_out, x_target_out, y_target_out = morph(
    ...     x_morph, y_morph, x_target, y_target)
    """

    # Define input output types
    summary = "Squeeze morph by polynomial shift"
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["squeeze"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Apply a polynomial to squeeze the morph function"""
        Morph.morph(self, x_morph, y_morph, x_target, y_target)

        return self.xyallout
