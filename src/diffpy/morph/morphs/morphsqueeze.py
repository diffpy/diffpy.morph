from diffpy.morph.morphs.morph import LABEL_GR, LABEL_RA, Morph


class MorphSqueeze(Morph):
    """Squeeze the morph function.

    This applies a polynomial to squeeze the morph non-linearly. The morphed
    data is returned on the same grid as the unmorphed data.

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

        return self.xyallout
