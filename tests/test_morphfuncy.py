import numpy as np
import pytest

from diffpy.morph.morphs.morphfuncy import MorphFuncy


def y_sine_function(x, y, y_amplitude, y_frequency):
    return y_amplitude * np.sin(y_frequency * x) * y


def y_exponential_decay_function(x, y, y_amplitude, y_decay_rate):
    return y_amplitude * np.exp(-y_decay_rate * x) * y


def y_gaussian_function(x, y, y_amplitude, y_mean, y_sigma):
    return y_amplitude * np.exp(-((x - y_mean) ** 2) / (2 * y_sigma**2)) * y


def y_polynomial_function(x, y, y_a, y_b, y_c):
    return (y_a * x**2 + y_b * x + y_c) * y


def y_logarithmic_function(x, y, y_scale):
    return y_scale * np.log(1 + x) * y


funcy_test_suite = [
    (
        y_sine_function,
        {"y_amplitude": 2, "y_frequency": 5},
        lambda x, y: 2 * np.sin(5 * x) * y,
    ),
    (
        y_exponential_decay_function,
        {"y_amplitude": 5, "y_decay_rate": 0.1},
        lambda x, y: 5 * np.exp(-0.1 * x) * y,
    ),
    (
        y_gaussian_function,
        {"y_amplitude": 1, "y_mean": 5, "y_sigma": 1},
        lambda x, y: np.exp(-((x - 5) ** 2) / (2 * 1**2)) * y,
    ),
    (
        y_polynomial_function,
        {"y_a": 1, "y_b": 2, "y_c": 0},
        lambda x, y: (x**2 + 2 * x) * y,
    ),
    (
        y_logarithmic_function,
        {"y_scale": 0.5},
        lambda x, y: 0.5 * np.log(1 + x) * y,
    ),
]


@pytest.mark.parametrize(
    "function, parameters, expected_function",
    funcy_test_suite,
)
def test_funcy(function, parameters, expected_function):
    x_morph = np.linspace(0, 10, 101)
    y_morph = np.sin(x_morph)
    x_target = x_morph.copy()
    y_target = y_morph.copy()
    x_morph_expected = x_morph
    y_morph_expected = expected_function(x_morph, y_morph)
    morph = MorphFuncy()
    morph.funcy_function = function
    morph.funcy = parameters
    x_morph_actual, y_morph_actual, x_target_actual, y_target_actual = (
        morph.morph(x_morph, y_morph, x_target, y_target)
    )

    assert np.allclose(y_morph_actual, y_morph_expected)
    assert np.allclose(x_morph_actual, x_morph_expected)
    assert np.allclose(x_target_actual, x_target)
    assert np.allclose(y_target_actual, y_target)
