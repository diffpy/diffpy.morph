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

        return self.xyallout
