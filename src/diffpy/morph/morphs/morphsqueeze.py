"""class MorphSqueeze -- apply a non-linear squeeze to the morph.
This morph non-linearly adjusts the x-coordinates.
The y-values are then recomputed by interpolating the original data.
"""

import numpy as np

from diffpy.morph.morphs.morph import LABEL_GR, LABEL_RA, Morph


class MorphSqueeze(Morph):
    summary = "Squeeze morph by desired amount (non-linear transformation)"
    xinlabel = LABEL_RA  # This label need to change to be more generic
    yinlabel = LABEL_GR  # This label need to change to be more generic
    xoutlabel = LABEL_RA  # This label need to change to be more generic
    youtlabel = LABEL_GR  # This label need to change to be more generic
    parnames = ["squeeze"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Resample arrays onto the specified grid using a non-linear squeeze.

        Parameters
        ----------
        x_morph : array-like
            The input x-values to be transformed.
        y_morph : array-like
            The input y-values.
        x_target, y_target : array-like
            The target grid arrays (left unchanged by this morph).

        Returns
        -------
            (x_morph_out, y_morph_out, x_target, y_target)
        """
        # Initialize the parent class to set up attributes
        Morph.morph(self, x_morph, y_morph, x_target, y_target)

        # If squeeze is zero, return original output
        if self.squeeze == 0:
            return self.xyallout

        # Compute new x positions using the non-linear squeeze transformation:
        new_x = self.x_morph_in + self.squeeze * np.sin(self.x_morph_in)
        self.x_morph_out = new_x

        # Interpolate the y-values at the new x positions.
        self.y_morph_out = np.interp(new_x, self.x_morph_in, self.y_morph_in)

        return self.xyallout


# End of class MorphSqueeze
