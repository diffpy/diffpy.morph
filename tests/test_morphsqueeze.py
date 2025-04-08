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
        [0.2, -0.01, 0.001, -0.001],
        # Quadratic squeeze coefficients
        [-0.2, 0.005, -0.003],
        # Linear squeeze coefficients
        [0.1, 0.3],
        # 4th order squeeze coefficients
        [0.2, -0.01, 0.001, -0.001, 0.0001],
        # Testing zeros
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    ],
)
def test_morphsqueeze(squeeze_coeffs):

    x_target = np.linspace(0, 10, 1000)
    y_target = np.sin(x_target)

    squeeze_polynomial = Polynomial(squeeze_coeffs)
    x_squeezed = x_target + squeeze_polynomial(x_target)

    x_morph = x_target.copy()
    y_morph = np.sin(x_squeezed)

    morph = MorphSqueeze()
    morph.squeeze = squeeze_coeffs

    x_actual, y_actual, x_expected, y_expected = morph(
        x_morph, y_morph, x_target, y_target
    )

    # Check that the morphed (actual) data matches the expected data
    # Including tolerance error because of extrapolation error
    assert np.allclose(y_actual, y_expected, atol=0.1)
