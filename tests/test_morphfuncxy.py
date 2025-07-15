import numpy as np
import pytest

# from diffpy.morph.morphs.morphfuncxy import MorphFuncxy
from diffpy.morph.morphs.morphfuncy import MorphFuncy


def sine_function(x, y, amplitude, frequency):
    return amplitude * np.sin(frequency * x) * y


def exponential_decay_function(x, y, amplitude, decay_rate):
    return amplitude * np.exp(-decay_rate * x) * y


def gaussian_function(x, y, amplitude, mean, sigma):
    return amplitude * np.exp(-((x - mean) ** 2) / (2 * sigma**2)) * y


def polynomial_function(x, y, a, b, c):
    return (a * x**2 + b * x + c) * y


def logarithmic_function(x, y, scale):
    return scale * np.log(1 + x) * y


# FIXME:
@pytest.mark.parametrize(
    "function, parameters, expected_function",
    [
        (
            sine_function,
            {"amplitude": 2, "frequency": 5},
            lambda x, y: 2 * np.sin(5 * x) * y,
        ),
        (
            exponential_decay_function,
            {"amplitude": 5, "decay_rate": 0.1},
            lambda x, y: 5 * np.exp(-0.1 * x) * y,
        ),
        (
            gaussian_function,
            {"amplitude": 1, "mean": 5, "sigma": 1},
            lambda x, y: np.exp(-((x - 5) ** 2) / (2 * 1**2)) * y,
        ),
        (
            polynomial_function,
            {"a": 1, "b": 2, "c": 0},
            lambda x, y: (x**2 + 2 * x) * y,
        ),
        (
            logarithmic_function,
            {"scale": 0.5},
            lambda x, y: 0.5 * np.log(1 + x) * y,
        ),
    ],
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
