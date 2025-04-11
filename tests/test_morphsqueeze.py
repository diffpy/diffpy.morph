import numpy as np
import pytest
from numpy.polynomial import Polynomial

from diffpy.morph.morphs.morphsqueeze import MorphSqueeze

squeeze_coeffs_list = [
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
]
morph_target_grids = [
    # UCs from issue 181: https://github.com/diffpy/diffpy.morph/issues/181
    # UC2: Same range and same grid density
    (np.linspace(0, 10, 101), np.linspace(0, 10, 101)),
    # UC4: Target range wider than morph, same grid density
    (np.linspace(0, 10, 101), np.linspace(-2, 20, 221)),
    # UC6: Target range wider than morph, finer target grid density
    (np.linspace(0, 10, 101), np.linspace(-2, 20, 421)),
    # UC8: Target range wider than morph, finer morph grid density
    (np.linspace(0, 10, 401), np.linspace(-2, 20, 200)),
    # UC10: Morph range starts and ends earlier than target, same grid density
    (np.linspace(-2, 10, 121), np.linspace(0, 20, 201)),
    # UC12: Morph range wider than target, same grid density
    (np.linspace(-2, 20, 221), np.linspace(0, 10, 101)),
]


@pytest.mark.parametrize("x_morph, x_target", morph_target_grids)
@pytest.mark.parametrize("squeeze_coeffs", squeeze_coeffs_list)
def test_morphsqueeze(x_morph, x_target, squeeze_coeffs):
    y_target = np.sin(x_target)
    squeeze_polynomial = Polynomial(squeeze_coeffs)
    x_squeezed = x_morph + squeeze_polynomial(x_morph)
    y_morph = np.sin(x_squeezed)
    x_morph_expected = x_morph
    y_morph_expected = np.sin(x_morph)
    morph = MorphSqueeze()
    morph.squeeze = squeeze_coeffs
    x_morph_actual, y_morph_actual, x_target_actual, y_target_actual = morph(
        x_morph, y_morph, x_target, y_target
    )
    assert np.allclose(y_morph_actual, y_morph_expected)
    assert np.allclose(x_morph_actual, x_morph_expected)
    assert np.allclose(x_target_actual, x_target)
    assert np.allclose(y_target_actual, y_target)
