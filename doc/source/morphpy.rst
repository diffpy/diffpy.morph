.. _morphpy:

Using diffpy.morph in Python
############################

On top of the command-line usage described in the `quickstart tutorial <quickstart.html>`__,
``diffpy.morph`` also supports Python integration.
This functionality is intended for those acquainted with the basic morphs
described in the aforementioned quickstart tutorial who want to use ``diffpy.morph`` in their
Python scripts.

Python Morphing Functions
=========================

    1. In the quickstart tutorial, you were asked to try a combined scale, stretch, and smear
       morph on the files `darkSub_rh20_C_01.gr` and `darkSub_rh20_C_44.gr` using the command-line
       command ::

          diffpy.morph --scale=0.8 --smear=-0.08 --stretch=0.5 --rmin=1.5 --rmax=30 darkSub_rh20_C_01.gr darkSub_rh20_C_44.gr

    2. To do the same on Python, we must first create a new Python script in the same directory as the
       data files `darkSub_rh20_C_01.gr` and `darkSub_rh20_C_44.gr`.
    3. Then, in that script, import ::

           from diffpy.morph.morphpy import morph

    3. Finally, we run the ``morph`` function ::

           morph_info, morph_table = morph("darkSub_rh20_C_01.gr", "darkSub_rh20_C_44.gr", scale=0.8, smear=-0.08, stretch=0.5, rmin=1.5, rmax=30)

           * The ``morph`` function takes in two file names (or paths). You can also provide various parameters
             for morphing (see the Full Parameter List below).
           * If, let's say, the file `darkSub_rh20_C_01.gr` is in a subdirectory `subdir/darkSub_rh20_C_01.gr`,
             you should replace ``"darkSub_rh20_C_01.gr"`` in the above example with ``"subdir/darkSub_rh20_C_01.gr"``.

    4. The ``morph`` function returns a dictionary ``morph_info`` and a numpy array ``morph_table``.

       * ``morph_info`` contains all morphs as keys (e.g. ``"scale"``, ``"stretch"``, ``"smear"``) with
         the optimized morphing parameters found by ``diffpy.morph`` as values. ``morph_info`` also contains
         the Rw and Pearson correlation coefficients found post-morphing.
       * ``morph_table`` is a two-column array of the morphed function interpolated onto the grid of the
         target function (e.g. in our example, it returns the contents of `darkSub_rh20_C_01.gr` after
         the morphs are applied interpolated onto the grid of `darkSub_rh20_C_44.gr`).
    5. Notice that most parameters you are able to use are the same as the options provided in the command-line
       interface version of ``diffpy.morph``. For example, the ``--apply`` option becomes the ``apply=True`` parameter.
    6. With that, you have already mastered the basics of using ``diffpy.morph`` on Python!
    7. Note that instead of passing two files to ``diffpy.morph``, you might instead want to directly
       pass arrays. For example, rather than passing `darkSub_rh20_C_01.gr`, I may want to pass
       a two-column array named ``ds_rh20_c_01_array`` containing the data table contents of the file
       `darkSub_rh20_C_01.gr`. In this case, we have a separate function ::

           from diffpy.morph.morphpy import morph_arrays

    8. Assuming we have loaded the data in `darkSub_rh20_C_01.gr` into ``ds_rh20_c_01_array`` and
       `darkSub_rh20_C_44.gr` into ``ds_rh20_c_44_array``, we can apply the same morph as step 3
       by running ::

           morph_info, morph_table = morph_arrays(ds_rh20_c_01_array, ds_rh20_c_44_array, scale=0.8, smear=-0.08, stretch=0.5, rmin=1.5, rmax=30)

    9. Notice that the two-column format of the input to ``morph_arrays`` is the same as the
       output of ``morph`` and ``morph_arrays``. It is VERY IMPORTANT that the data is in two-column format
       rather than the traditional two-row format. This is to reflect the file formats conventionally
       used to store PDFs.
    10. For a full list of parameters used by (both) ``morph`` and ``morph_arrays``, see the Full Parameter List
        section below.

Full Parameter List
===================

General Parameters
------------------

save: str or path
    Save the morphed function to a the file passed to save. Use '-' for stdout.
verbose: bool
    Print additional header details to saved files. These include details about the morph
    inputs and outputs.
rmin: float
    Minimum r-value (abscissa) to use for function comparisons.
rmax: float
    Maximum r-value (abscissa) to use for function comparisons.
tolerance: float
    Specify least squares refiner tolerance when optimizing for morph parameters. Default: 10e-8.
pearson: bool
    The refiner instead maximizes agreement in the Pearson function
    (default behavior is to minimize the residual).
    Note that this is insensitive to scale.
addpearson: bool
    Maximize agreement in the Pearson function as well as minimizing the residual.

Manipulations
-------------
These parameters select the manipulations that are to be applied to the
function. The passed values will be refined unless specifically
excluded with the apply or exclude parameters.

apply: bool
    Apply morphs but do not refine.
exclude: str
    Exclude a manipulation from refinement by name.
scale: float
    Apply scale factor. This multiplies the function ordinate by scale.
stretch: float
    Stretch function grid by a fraction stretch. Specifically, this multiplies the function grid by 1+stretch.
squeeze: list of float
    Squeeze function grid given a polynomial
    p(x) = squeeze[0]+squeeze[1]*x+...+squeeze[n]*x^n. n is dependent on the number
    of values in the user-inputted comma-separated list.
    The morph transforms the function grid from x to x+p(x).
    When this parameter is given, hshift is disabled.
    When n>1, stretch is disabled.
smear: float
    Smear the peaks with a Gaussian of width smear. This
    is done by convolving the function with a Gaussian
    with standard deviation smear. If both smear and
    smear_pdf are used, only smear_pdf will be
    applied.
smear_pdf: float
    Convert PDF to RDF. Then, smear peaks with a Gaussian
    of width smear_pdf. Convert back to PDF. If both smear and
    smear_pdf are used, only smear_pdf will be
    applied.
slope: float
    Slope of the baseline used in converting from PDF to RDF.
    This is used with the option smear_pdf. The slope will
    be estimated if not provided.
hshift: float
    Shift the function horizontally by hshift to the right.
vshift: float
    Shift the function vertically by vshift upward.
qdamp: float
    Dampen PDF by a factor qdamp.
radius: float
    Apply characteristic function of sphere with radius
    given by parameter radius. If pradius is also specified, instead apply
    characteristic function of spheroid with equatorial
    radius radius and polar radius pradius.
pradius: float
    Apply characteristic function of spheroid with
    equatorial radius given by above parameter radius and polar radius pradius.
    If only pradius is specified, instead apply
    characteristic function of sphere with radius pradius.
iradius: float
    Apply inverse characteristic function of sphere with
    radius iradius. If ipradius is also specified, instead
    apply inverse characteristic function of spheroid with
    equatorial radius iradius and polar radius ipradius.
ipradius: float
    Apply inverse characteristic function of spheroid with
    equatorial radius iradius and polar radius ipradius.
    If only ipradius is specified, instead apply inverse
    characteristic function of sphere with radius ipradius.
funcy: tuple (function, dict)
    This morph applies the function funcy[0] with parameters given in funcy[1].
    The function funcy[0] must be a function of both the abscissa and ordinate
    (e.g. take in at least two inputs with as many additional parameters as needed).
    For example, let's start with a two-column table with abscissa x and ordinate y.
    let us say we want to apply the function ::

        def linear(x, y, a, b, c):
            return a * x + b * y + c

    This function takes in both the abscissa and ordinate on top of three additional
    parameters a, b, and c. To use the funcy parameter with initial guesses
    a=1.0, b=2.0, c=3.0, we would pass ``funcy=(linear, {a: 1.0, b: 2.0, c: 3.0})``.
    For an example use-case, see the Python-Specific Morphs section below.


Python-Specific Morphs
======================

Some morphs in ``diffpy.morph`` are supported only in Python. Here, we detail
how they are used and how to call them.

MorphFuncy: Applying custom functions
-------------------------------------

The ``MorphFuncy`` morph allows users to apply a custom Python function
to the y-axis values of a dataset, enabling flexible and user-defined
transformations.

In this tutorial, we walk through how to use ``MorphFuncy`` with an example
transformation. Unlike other morphs that can be run from the command line,
``MorphFuncy`` requires a Python function and is therefore intended to be used
through Python scripting.

    1. Import the necessary modules into your Python script:

       .. code-block:: python

            from diffpy.morph.morph_api import morph, morph_default_config
            import numpy as np

    2. Define a custom Python function to apply a transformation to the data.
       The function must take ``x`` and ``y`` (1D arrays of the same length)
       along with named parameters, and return a transformed ``y`` array of the
       same length.
       For this example, we will use a simple linear transformation that
       scales the input and applies an offset:

       .. code-block:: python

            def linear_function(x, y, scale, offset):
                return (scale * x) * y + offset

    3. In this example, we use a sine function for the morph data and generate
       the target data by applying the linear transformation with known scale
       and offset to it:

       .. code-block:: python

            x_morph = np.linspace(0, 10, 101)
            y_morph = np.sin(x_morph)
            x_target = x_morph.copy()
            y_target = np.sin(x_target) * 20 * x_target + 0.8

    4. Set up the morph configuration dictionary. This includes both the
       transformation parameters (our initial guess) and the transformation
       function itself:

       .. code-block:: python

            morph_config = morph_default_config(funcy={"scale": 1.2, "offset": 0.1})
            morph_config["function"] = linear_function

            # morph_config now contains:
            # {'funcy': {'scale': 1.2, 'offset': 0.1}, 'function': linear_function}

    5. Run the morph using the ``morph(...)``. This will apply the user-defined
       function and refine the parameters to best align the morph data
       with the target data:

       .. code-block:: python

            morph_result = morph(x_morph, y_morph, x_target, y_target, **morph_config)

    6. Extract the morphed output and the fitted parameters from the result:

       .. code-block:: python

            fitted_config = morph_result["morphed_config"]
            x_morph_out, y_morph_out, x_target_out, y_target_out = morph_result["morph_chain"].xyallout

            fitted_params = fitted_config["funcy"]
            print(f"Fitted scale: {fitted_params['scale']}")
            print(f"Fitted offset: {fitted_params['offset']}")

As you can see, the fitted scale and offset values match the ones used
to generate the target (scale=20 & offset=0.8). This example shows how
``MorphFuncy`` can be used to fit and apply custom transformations. Now
it's your turn to experiment with other custom functions that may be useful
for analyzing your data.
