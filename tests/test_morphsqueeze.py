import numpy as np
import pytest
from numpy.polynomial import Polynomial

from diffpy.morph.morphs.morphsqueeze import MorphSqueeze


@pytest.mark.parametrize(
    "squeeze_coeffs",
    [
        # The order of coefficients is [a0, a1, a2, ..., an]
        # Negative cubic squeeze coefficients
        [-0.2, -0.01, -0.001, -0.001],
        # Positive cubic squeeze coefficients
        [0.2, 0.01, 0.001, 0.001],
        # Positive and negative cubic squeeze coefficients
        [0.2, -0.01, 0.002, -0.001],
        # Quadratic squeeze coefficients
        [-0.2, 0.005, -0.007],
        # Linear squeeze coefficients
        [0.1, 0.3],
        # 4th order squeeze coefficients
        [0.2, -0.01, 0.001, -0.001, 0.0004],
        # Zeros and non-zeros, expect 0 + a1x + 0 + a3x**3
        [0, 0.03, 0, -0.001],
        # Testing zeros, expect no squeezing
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
)
def test_morphsqueeze(squeeze_coeffs):
    x_target = np.linspace(0, 10, 1001)
    y_target = np.sin(x_target)

    x_make = np.linspace(-3, 13, 1601)
    lower_idx = np.where(x_make == 0.0)[0][0]
    upper_idx = np.where(x_make == 10.0)[0][0]

    squeeze_polynomial = Polynomial(squeeze_coeffs)
    x_squeezed = x_make + squeeze_polynomial(x_make)

    x_morph = x_make.copy()
    y_morph = np.sin(x_squeezed)

    morph = MorphSqueeze()
    morph.squeeze = squeeze_coeffs

    x_actual, y_actual, x_expected, y_expected = morph(
        x_morph, y_morph, x_target, y_target
    )
    y_actual = y_actual[lower_idx : upper_idx + 1]
    assert np.allclose(y_actual, y_expected)

    # Plotting code used for figures in PR comments
    # https://github.com/diffpy/diffpy.morph/pull/180
    # plt.figure()
    # plt.scatter(x_expected, y_expected, color='black', label='Expected')
    # plt.plot(x_morph, y_morph, color='purple', label='morph')
    # plt.plot(x_actual, y_actual, '--', color='gold', label='Actual')
    # plt.legend()
    # plt.show()
