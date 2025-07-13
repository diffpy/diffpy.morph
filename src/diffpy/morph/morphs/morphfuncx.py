"""Class MorphFuncx -- apply a user-supplied python function to the
x-axis."""

from diffpy.morph.morphs.morph import LABEL_GR, LABEL_RA, Morph


class MorphFuncx(Morph):
    """Apply a custom function to the x-axis (grid) of the morph
    function.

    General morph function that applies a user-supplied function to the
    x-coordinates of morph data to make it align with a target.

    Notice: the function provided must preserve the monotonic
    increase of the grid.
    I.e. the function f applied on the grid x must ensure for all
    indices i<j, f(x[i]) < f(x[j]).

    Configuration Variables
    -----------------------
    function: callable
        The user-supplied function that applies a transformation to the
        x-coordinates of the data.

    parameters: dict
        A dictionary of parameters to pass to the function.

    Returns
    -------
        A tuple (x_morph_out, y_morph_out, x_target_out, y_target_out)
        where the target values remain the same and the morph data is
        transformed according to the user-specified function and parameters
        The morphed data is returned on the same grid as the unmorphed data

    Example
    -------
    Import the funcx morph function:

        >>> from diffpy.morph.morphs.morphfuncx import MorphFuncx

    Define or import the user-supplied transformation function:

        >>> import numpy as np
        >>> def exp_function(x, y, scale, rate):
        >>>     return abs(scale) * np.exp(rate * x)

    Note that this transformation is monotonic increasing, so will preserve
    the monotonic increasing nature of the provided grid.

    Provide initial guess for parameters:

        >>> parameters = {'scale': 1, 'rate': 1}

    Run the funcy morph given input morph array (x_morph, y_morph)and target
    array (x_target, y_target):

        >>> morph = MorphFuncx()
        >>> morph.funcx_function = exp_function
        >>> morph.funcx = parameters
        >>> x_morph_out, y_morph_out, x_target_out, y_target_out =
        ... morph.morph(x_morph, y_morph, x_target, y_target)

    To access parameters from the morph instance:

        >>> x_morph_in = morph.x_morph_in
        >>> y_morph_in = morph.y_morph_in
        >>> x_target_in = morph.x_target_in
        >>> y_target_in = morph.y_target_in
        >>> parameters_out = morph.funcx
    """

    # Define input output types
    summary = "Apply a Python function to the x-axis data"
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["funcx_function", "funcx"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Apply the user-supplied Python function to the x-coordinates
        of the morph data."""
        Morph.morph(self, x_morph, y_morph, x_target, y_target)
        self.x_morph_out = self.funcx_function(
            self.x_morph_in, self.y_morph_in, **self.funcx
        )
        return self.xyallout
