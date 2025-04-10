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
def test_morphsqueeze_target_extends_beyond_morph(squeeze_coeffs):
    # Target data extends beyond morph and different grids
    x_target = np.linspace(-3, 25, 401)
    y_target = np.sin(x_target)
    x_morph = np.linspace(0, 10, 301)
    squeeze_polynomial = Polynomial(squeeze_coeffs)
    x_squeezed = x_morph + squeeze_polynomial(x_morph)
    y_morph = np.sin(x_squeezed)
    # Trim target data to the region overlapping with the squeezed morph
    x_min = max(float(x_target[0]), float(x_squeezed[0]))
    x_max = min(float(x_target[-1]), float(x_squeezed[-1]))
    min_index = np.where(x_target >= x_min)[0][0]
    max_index = np.where(x_target <= x_max)[0][-1]
    x_morph_expected = x_target[min_index : max_index + 1]
    y_morph_expected = y_target[min_index : max_index + 1]
    morph = MorphSqueeze()
    morph.squeeze = squeeze_coeffs
    x_morph_actual, y_morph_actual, x_target_actual, y_target_actual = morph(
        x_morph, y_morph, x_target, y_target
    )
    assert np.allclose(y_morph_actual, y_morph_expected)
    assert np.allclose(x_morph_actual, x_morph_expected)
    assert np.allclose(x_target_actual, x_morph_expected)
    assert np.allclose(y_target_actual, y_morph_expected)


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
def test_morphsqueeze_morph_extends_beyond_target(squeeze_coeffs):
    # Different grid for morph and target data to test different grids
    x_target = np.linspace(0, 10, 101)
    y_target = np.sin(x_target)
    x_morph = np.linspace(-3, 15, 301)
    squeeze_polynomial = Polynomial(squeeze_coeffs)
    x_squeezed = x_morph + squeeze_polynomial(x_morph)
    y_morph = np.sin(x_squeezed)
    # Trim target data to the region overlapping with the squeezed morph
    x_min = max(float(x_target[0]), float(x_squeezed[0]))
    x_max = min(float(x_target[-1]), float(x_squeezed[-1]))
    min_index = np.where(x_target >= x_min)[0][0]
    max_index = np.where(x_target <= x_max)[0][-1]
    x_morph_expected = x_target[min_index : max_index + 1]
    y_morph_expected = y_target[min_index : max_index + 1]
    morph = MorphSqueeze()
    morph.squeeze = squeeze_coeffs
    x_morph_actual, y_morph_actual, x_target_actual, y_target_actual = morph(
        x_morph, y_morph, x_target, y_target
    )
    assert np.allclose(y_morph_actual, y_morph_expected)
    assert np.allclose(x_morph_actual, x_morph_expected)
    assert np.allclose(x_target_actual, x_morph_expected)
    assert np.allclose(y_target_actual, y_morph_expected)
