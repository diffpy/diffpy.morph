import numpy as np
import pytest
from numpy.polynomial import Polynomial
from scipy.interpolate import interp1d


@pytest.mark.parametrize(
    "squeeze_coeffs",
    [
        # The order of coefficients is [a0, a1, a2, ..., an]
        # Negative cubic squeeze coefficients
        [-0.2, -0.01, -0.001, -0.001],
        # Positive cubic squeeze coefficients
        [0.2, 0.01, 0.001, 0.001],
        # Positive and negative cubic squeeze coefficients
        [0.2, -0.01, 0.001, -0.001],
        # Quadratic squeeze coefficients
        [-0.2, 0.005, -0.003],
        # Linear squeeze coefficients
        [0.1, 0.3],
        # 4th order squeeze coefficients
        [0.2, -0.01, 0.001, -0.001, 0.0001],
    ],
)
def test_morphsqueeze(squeeze_coeffs):
    # Uniform x-axis grid. This is the same x-axis for all data.
    x = np.linspace(0, 10, 1000)
    # Expected uniform target
    y_expected = np.sin(x)

    # Create polynomial based on a list of values for polynomial coefficients
    squeeze_polynomial = Polynomial(squeeze_coeffs)
    # Apply squeeze parameters to uniform data to get the squeezed data
    x_squeezed = x + squeeze_polynomial(x)
    y_squeezed = np.sin(x_squeezed)

    # Unsqueeze the data by interpolating back to uniform grid
    y_unsqueezed = interp1d(
        x_squeezed,
        y_squeezed,
        kind="cubic",
        bounds_error=False,
        fill_value="extrapolate",
    )(x)
    y_actual = y_unsqueezed

    # Check that the unsqueezed (actual) data matches the expected data
    # Including tolerance error because of extrapolation error
    assert np.allclose(y_actual, y_expected, atol=1)

    # This plotting code was used for the comments in the github
    # PR https://github.com/diffpy/diffpy.morph/pull/180
    # plt.figure(figsize=(7, 4))
    # plt.plot(x, y_expected, color="black", label="Expected uniform data")
    # plt.plot(x, y_squeezed, "--", color="purple", label="Squeezed data")
    # plt.plot(x, y_unsqueezed, "--", color="gold", label="Unsqueezed data")
    # plt.xlabel("x")
    # plt.ylabel("y")
    # plt.legend()
    # plt.show()
