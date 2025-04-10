import numpy as np
from numpy.polynomial import Polynomial
from scipy.interpolate import CubicSpline

from diffpy.morph.morphs.morph import LABEL_GR, LABEL_RA, Morph


class MorphSqueeze(Morph):
    """Squeeze the morph function.

    This applies a polynomial to squeeze the morph non-linearly. The resulting
    squeezed morph is interpolated to the (trimmed) target grid.
    Only the overlapping region between the squeezed morph and the target
    grid is used. The target is trimmed (or not) accordingly, and the final
    outputs (morph and target) are returned on the same grid, defined by this
    trimmed target range.

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
        if self.squeeze is None:
            self.x_morph_out = self.x_morph_in
            self.y_morph_out = self.y_morph_in
            return self.xyallout

        squeeze_polynomial = Polynomial(self.squeeze)
        x_squeezed = self.x_morph_in + squeeze_polynomial(self.x_morph_in)
        x_min = max(float(self.x_target_in[0]), float(x_squeezed[0]))
        x_max = min(float(self.x_target_in[-1]), float(x_squeezed[-1]))
        min_index = np.where(self.x_target_in >= x_min)[0][0]
        max_index = np.where(self.x_target_in <= x_max)[0][-1]
        self.x_target_out = self.x_target_in[min_index : max_index + 1]
        self.y_target_out = self.y_target_in[min_index : max_index + 1]
        self.y_morph_out = CubicSpline(x_squeezed, self.y_morph_in)(
            self.x_target_out
        )
        self.x_morph_out = self.x_target_out
        return self.xyallout
