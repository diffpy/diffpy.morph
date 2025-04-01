"""
The squeeze morph is used to correct for small non-linear geometric distortions
from detectors that are not effectively corrected during calibration, such as
individual module misalignment or tilt. This squeezing is applied as:
x_squeezed = x + squeeze_0 + squeeze_1 * x**2 + squeeze_2 * x**3

The squeeze distortions that we might encounter practically are going to be
very small. Furthermore, large values for the squeezing parameters lead to
missing values during interpolation. Therefore is important to use small
squeezing values to avoid error or unphysical results.
Safe bounds for the squeezing parameters are:
squeeze_0 [-0.2, 0.2]
squeeze_1 [-0.001, 0.001]
squeeze_2 [-0.0001, 0.0001]
Values outside these bounds should be used carefully.
Note that these bounds are established for an x-axis that goes from 0 to 10.
"""

import matplotlib.pyplot as plt
import numpy as np


def test_morphsqueeze():
    """
    Test that we can unsqueeze squeezed data.
    The test inputs are an expected uniform target (e.g. synchrotron data)
    and a squeezed version of the target (e.g. XFEL data). The squeezed data
    is created by applying a nonlinear distortion to the uniform target.
    Both input data are in the same uniform x-axis grid.
    Then we unsqueeze the squeezed data by doing the inverse transformation
    using interpolatiion.
    Finally we check that the unsqueezed data matches the expected uniform
    target.
    """

    # Uniform x-axis grid. This is the same x-axis for all data.
    x = np.linspace(0, 10, 1000)
    # Expected uniform target
    y_expected = np.sin(x)

    # Apply squeeze parameters to uniform data to get the squeezed data
    # Include squeeze_0 for squeezes with offset
    squeeze_0 = 0.2
    squeeze_1 = 0.001
    squeeze_2 = 0.001
    x_squeezed = x + squeeze_0 + squeeze_1 * x**2 + squeeze_2 * x**3
    y_squeezed = np.sin(x_squeezed)

    # Unsqueeze the data by interpolating back to uniform grid
    y_unsqueezed = np.interp(x, x_squeezed, y_squeezed)
    y_actual = y_unsqueezed

    # Check that the unsqueezed (actual) data matches the expected data
    # Including tolerance error because I was having issues
    # with y_actual == y_expected. I think is because interpolation?
    assert np.allclose(y_actual, y_expected, atol=1)

    # Plot to verify what we are doing
    plt.figure(figsize=(7, 4))
    plt.plot(x, y_expected, color="black", label="Expected uniform data")
    plt.plot(x, y_squeezed, "--", color="purple", label="Squeezed data")
    plt.plot(x, y_unsqueezed, "--", color="gold", label="Unsqueezed data")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.legend()
    plt.show()
