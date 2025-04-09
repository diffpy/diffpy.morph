import numpy as np
from numpy.polynomial import Polynomial
from scipy.interpolate import interp1d

from diffpy.morph.morphs.morph import LABEL_GR, LABEL_RA, Morph


class MorphSqueeze(Morph):
    """Squeeze the morph function.

    This applies a polynomial to squeeze the morph non-linearly.

    Configuration Variables
    -----------------------
    squeeze
        list or array-like
        Polynomial coefficients [a0, a1, ..., an] for the squeeze function.
    """

    # Define input output types
    summary = "Squeeze morph by polynomial shift"
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["squeeze"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        Morph.morph(self, x_morph, y_morph, x_target, y_target)
        if self.squeeze is None or np.allclose(self.squeeze, 0):
            self.x_morph_out = self.x_morph_in
            self.y_morph_out = self.y_morph_in
            return self.xyallout

        squeeze_polynomial = Polynomial(self.squeeze)
        x_squeezed = self.x_morph_in + squeeze_polynomial(self.x_morph_in)

        self.y_morph_out = interp1d(
            x_squeezed, self.y_morph_in, kind="cubic", bounds_error=False
        )(self.x_morph_in)

        self.x_morph_out = self.x_morph_in
        return self.xyallout
