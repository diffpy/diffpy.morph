"""Class MorphFuncy -- apply a user-supplied python function to the
y-axis."""

from diffpy.morph.morphs.morph import LABEL_GR, LABEL_RA, Morph


class MorphFuncy(Morph):
    """Apply a custom function to the y-axis of the morph function.

    General morph function that applies a user-supplied function to the
    y-coordinates of morph data to make it align with a target.

    Configuration Variables
    -----------------------
    function: callable
        The user-supplied function that applies a transformation to the
        y-coordinates of the data.

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
    Import the funcy morph function:

        >>> from diffpy.morph.morphs.morphfuncy import MorphFuncy

    Define or import the user-supplied transformation function:

        >>> def sine_function(x, y, amplitude, frequency):
        >>>     return amplitude * np.sin(frequency * x) * y

    Provide initial guess for parameters:

        >>> parameters = {'amplitude': 2, 'frequency': 2}

    Run the funcy morph given input morph array (x_morph, y_morph)and target
    array (x_target, y_target):

        >>> morph = MorphFuncy()
        >>> morph.function = sine_function
        >>> morph.funcy = parameters
        >>> x_morph_out, y_morph_out, x_target_out, y_target_out =
        ... morph.morph(x_morph, y_morph, x_target, y_target)

    To access parameters from the morph instance:

        >>> x_morph_in = morph.x_morph_in
        >>> y_morph_in = morph.y_morph_in
        >>> x_target_in = morph.x_target_in
        >>> y_target_in = morph.y_target_in
        >>> parameters_out = morph.funcy
    """

    # Define input output types
    summary = "Apply a Python function to the y-axis data"
    xinlabel = LABEL_RA
    yinlabel = LABEL_GR
    xoutlabel = LABEL_RA
    youtlabel = LABEL_GR
    parnames = ["funcy_function", "funcy"]

    def morph(self, x_morph, y_morph, x_target, y_target):
        """Apply the user-supplied Python function to the y-coordinates
        of the morph data."""
        Morph.morph(self, x_morph, y_morph, x_target, y_target)
        self.y_morph_out = self.funcy_function(
            self.x_morph_in, self.y_morph_in, **self.funcy
        )
        return self.xyallout
