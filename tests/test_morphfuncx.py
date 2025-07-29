import numpy as np
import pytest

from diffpy.morph.morphs.morphfuncx import MorphFuncx


def x_exponential_function(x, y, x_amplitude, x_rate):
    return x_amplitude * np.exp(x_rate * x)


def x_linear_function(x, y, x_slope, x_intercept):
    return x_slope * x + x_intercept


def x_cubic_function(x, y, x_amplitude, x_shift):
    return x_amplitude * (x - x_shift) ** 3


def x_arctan_function(x, y, x_amplitude, x_frequency):
    return x_amplitude * np.arctan(x_frequency * x)


funcx_test_suite = [
    (
        x_exponential_function,
        {"x_amplitude": 2, "x_rate": 5},
        lambda x, y: 2 * np.exp(5 * x),
    ),
    (
        x_linear_function,
        {"x_slope": 5, "x_intercept": 0.1},
        lambda x, y: 5 * x + 0.1,
    ),
    (
        x_cubic_function,
        {"x_amplitude": 2, "x_shift": 5},
        lambda x, y: 2 * (x - 5) ** 3,
    ),
    (
        x_arctan_function,
        {"x_amplitude": 4, "x_frequency": 2},
        lambda x, y: 4 * np.arctan(2 * x),
    ),
]


@pytest.mark.parametrize(
    "function, parameters, expected_function",
    funcx_test_suite,
)
def test_funcy(function, parameters, expected_function):
    x_morph = np.linspace(0, 10, 101)
    y_morph = np.sin(x_morph)
    x_target = x_morph.copy()
    y_target = y_morph.copy()
    x_morph_expected = expected_function(x_morph, y_morph)
    y_morph_expected = y_morph
    morph = MorphFuncx()
    morph.funcx_function = function
    morph.funcx = parameters
    x_morph_actual, y_morph_actual, x_target_actual, y_target_actual = (
        morph.morph(x_morph, y_morph, x_target, y_target)
    )

    assert np.allclose(y_morph_actual, y_morph_expected)
    assert np.allclose(x_morph_actual, x_morph_expected)
    assert np.allclose(x_target_actual, x_target)
    assert np.allclose(y_target_actual, y_target)
