import numpy as np
import pytest
from numpy.polynomial import Polynomial

from diffpy.morph.morphs.morphsqueeze import MorphSqueeze

squeeze_coeffs_list = [
    # The order of coefficients is [a0, a1, a2, ..., an]
    # Negative cubic squeeze coefficients
    [-0.2, -0.01, -0.001, -0.0001],
    # Positive cubic squeeze coefficients
    [0.2, 0.01, 0.001, 0.0001],
    # Positive and negative cubic squeeze coefficients
    [0.2, -0.01, 0.002, -0.0001],
    # Quadratic squeeze coefficients
    [-0.2, 0.005, -0.007],
    # Linear squeeze coefficients
    [0.1, 0.3],
    # 4th order squeeze coefficients
    [0.2, -0.01, 0.001, -0.001, 0.0004],
    # Zeros and non-zeros, the full polynomial is applied
    [0, 0.03, 0, -0.0001],
    # Testing zeros, expect no squeezing
    [0, 0, 0, 0, 0, 0],
]
morph_target_grids = [
    # UCs from issue 181: https://github.com/diffpy/diffpy.morph/issues/181
    # UC2: Same range and same grid density
    (np.linspace(0, 10, 101), np.linspace(0, 10, 101)),
    # UC4: Target range wider than morph, same grid density
    (np.linspace(0, 10, 101), np.linspace(-2, 20, 221)),
    # UC6: Target range wider than morph, target grid density finer than morph
    (np.linspace(0, 10, 101), np.linspace(-2, 20, 421)),
    # UC8: Target range wider than morph, morph grid density finer than target
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
    (
        x_morph_actual,
        y_morph_actual,
        x_target_actual,
        y_target_actual,
        low_extrap_idx,
        high_extrap_idx,
    ) = morph(x_morph, y_morph, x_target, y_target)
    if low_extrap_idx is None and high_extrap_idx is None:
        assert np.allclose(y_morph_actual, y_morph_expected, atol=1e-6)
    else:
        interp_start = low_extrap_idx + 1 if low_extrap_idx is not None else 0
        interp_end = (
            high_extrap_idx
            if high_extrap_idx is not None
            else len(y_morph_actual)
        )
        assert np.allclose(
            y_morph_actual[interp_start:interp_end],
            y_morph_expected[interp_start:interp_end],
            atol=1e-6,
        )
    assert np.allclose(x_morph_actual, x_morph_expected)
    assert np.allclose(x_target_actual, x_target)
    assert np.allclose(y_target_actual, y_target)
