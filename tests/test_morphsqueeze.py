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
        # Zeros and non-zeros, the full polynomial is applied
        [0, 0.03, 0, -0.001],
        # Testing zeros, expect no squeezing
        [0, 0, 0, 0, 0, 0],
    ],
)
def test_morphsqueeze(squeeze_coeffs):
    x_target_expected = np.linspace(0, 10, 101)
    y_target_expected = np.sin(x_target_expected)
    # Different grid for morph data to test inputs with different grids
    # Morph grid must be finer than the target to avoid interpolation issues
    x_morph = np.linspace(-3, 13, 301)
    squeeze_polynomial = Polynomial(squeeze_coeffs)
    x_squeezed = x_morph + squeeze_polynomial(x_morph)
    y_morph = np.sin(x_squeezed)
    morph = MorphSqueeze()
    morph.squeeze = squeeze_coeffs
    x_morph_actual, y_morph_actual, x_target_actual, y_target_actual = morph(
        x_morph, y_morph, x_target_expected, y_target_expected
    )
    assert np.allclose(y_morph_actual, y_target_expected)
    assert np.allclose(x_morph_actual, x_target_expected)
    assert np.allclose(x_target_actual, x_target_expected)
    assert np.allclose(y_target_actual, y_target_expected)
