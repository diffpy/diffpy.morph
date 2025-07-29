import numpy as np
import pytest

from diffpy.morph.morphs.morphfuncxy import MorphFuncxy

from .test_morphfuncx import funcx_test_suite
from .test_morphfuncy import funcy_test_suite

funcxy_test_suite = []
for entry_y in funcy_test_suite:
    for entry_x in funcx_test_suite:
        funcxy_test_suite.append(
            (
                entry_x[0],
                entry_y[0],
                entry_x[1],
                entry_y[1],
                entry_x[2],
                entry_y[2],
            )
        )


# FIXME:
@pytest.mark.parametrize(
    "funcx_func, funcy_func, funcx_params, funcy_params, "
    "funcx_lambda, funcy_lambda",
    funcxy_test_suite,
)
def test_funcy(
    funcx_func,
    funcy_func,
    funcx_params,
    funcy_params,
    funcx_lambda,
    funcy_lambda,
):
    x_morph = np.linspace(0, 10, 101)
    y_morph = np.sin(x_morph)
    x_target = x_morph.copy()
    y_target = y_morph.copy()
    x_morph_expected = funcx_lambda(x_morph, y_morph)
    y_morph_expected = funcy_lambda(x_morph, y_morph)

    funcxy_params = {}
    funcxy_params.update(funcx_params)
    funcxy_params.update(funcy_params)

    def funcxy_func(x, y, **funcxy_params):
        funcx_params = {}
        funcy_params = {}
        for param in funcxy_params.keys():
            if param[:2] == "x_":
                funcx_params.update({param: funcxy_params[param]})
            elif param[:2] == "y_":
                funcy_params.update({param: funcxy_params[param]})
        return funcx_func(x, y, **funcx_params), funcy_func(
            x, y, **funcy_params
        )

    morph = MorphFuncxy()
    morph.funcxy_function = funcxy_func
    morph.funcxy = funcxy_params
    x_morph_actual, y_morph_actual, x_target_actual, y_target_actual = (
        morph.morph(x_morph, y_morph, x_target, y_target)
    )

    assert np.allclose(y_morph_actual, y_morph_expected)
    assert np.allclose(x_morph_actual, x_morph_expected)
    assert np.allclose(x_target_actual, x_target)
    assert np.allclose(y_target_actual, y_target)
