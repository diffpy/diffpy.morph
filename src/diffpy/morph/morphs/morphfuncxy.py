"""Class MorphFuncxy -- apply a user-supplied python function to both
the x and y axes."""

from diffpy.morph.morphs.morph import LABEL_GR, LABEL_RA, Morph


class MorphFuncxy(Morph):
    """Apply a custom function to the morph function.

    General morph function that applies a user-supplied function to the
    morph data to make it align with a target.

    This function may modify both the grid (x-axis) and function (y-axis)
    of the morph data.

    The user-provided function must return a two-column 1D function.

    Configuration Variables
    -----------------------
    function: callable
        The user-supplied function that applies a transformation to the
        grid (x-axis) and morph function (y-axis).

    parameters: dict
        A dictionary of parameters to pass to the function.

    Returns
    -------
        A tuple (x_morph_out, y_morph_out, x_target_out, y_target_out)
        where the target values remain the same and the morph data is
        transformed according to the user-specified function and parameters
        The morphed data is returned on the same grid as the unmorphed data

    Example (EDIT)
    -------
    Import the funcxy morph function:

        >>> from diffpy.morph.morphs.morphfuncxy import MorphFuncxy

    Define or import the user-supplied transformation function:

        >>> import numpy as np
        >>> def shift_function(x, y, hshift, vshift):
        >>>     return x + hshift, y + vshift

    Provide initial guess for parameters:

        >>> parameters = {'hshift': 1, 'vshift': 1}

    Run the funcy morph given input morph array (x_morph, y_morph)and target
    array (x_target, y_target):

        >>> morph = MorphFuncxy()
        >>> morph.function = shift_function
        >>> morph.funcy = parameters
        >>> x_morph_out, y_morph_out, x_target_out, y_target_out =
        ... morph.morph(x_morph, y_morph, x_target, y_target)

    To access parameters from the morph instance:

        >>> x_morph_in = morph.x_morph_in
        >>> y_morph_in = morph.y_morph_in
        >>> x_target_in = morph.x_target_in
        >>> y_target_in = morph.y_target_in
        >>> parameters_out = morph.funcxy
    """

    # Define input output types
    summary = (
        "Apply a Python function to the data (y-axis) and data grid (x-axis)"
    )
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["funcxy_function", "funcxy"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Apply the user-supplied Python function to the y-coordinates
        of the morph data."""
        Morph.morph(self, x_morph, y_morph, x_target, y_target)
        self.x_morph_out, self.y_morph_out = self.funcxy_function(
            self.x_morph_in, self.y_morph_in, **self.funcxy
        )
        return self.xyallout
