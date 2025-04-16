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
    low_extrap = np.where(x_morph < x_squeezed[0])[0]
    high_extrap = np.where(x_morph > x_squeezed[-1])[0]
    extrap_index_low_expected = low_extrap[-1] if low_extrap.size else None
    extrap_index_high_expected = high_extrap[0] if high_extrap.size else None
    x_morph_expected = x_morph
    y_morph_expected = np.sin(x_morph)
    morph = MorphSqueeze()
    morph.squeeze = squeeze_coeffs
    x_morph_actual, y_morph_actual, x_target_actual, y_target_actual = morph(
        x_morph, y_morph, x_target, y_target
    )
    extrap_index_low = morph.extrap_index_low
    extrap_index_high = morph.extrap_index_high
    if extrap_index_low is None:
        extrap_index_low = 0
    elif extrap_index_high is None:
        extrap_index_high = -1
    assert np.allclose(
        y_morph_actual[extrap_index_low + 1 : extrap_index_high],
        y_morph_expected[extrap_index_low + 1 : extrap_index_high],
        atol=1e-6,
    )
    assert np.allclose(
        y_morph_actual[:extrap_index_low],
        y_morph_expected[:extrap_index_low],
        atol=1e-3,
    )
    assert np.allclose(
        y_morph_actual[extrap_index_high:],
        y_morph_expected[extrap_index_high:],
        atol=1e-3,
    )
    assert morph.extrap_index_low == extrap_index_low_expected
    assert morph.extrap_index_high == extrap_index_high_expected
    assert np.allclose(x_morph_actual, x_morph_expected)
    assert np.allclose(x_target_actual, x_target)
    assert np.allclose(y_target_actual, y_target)
