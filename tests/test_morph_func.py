#!/usr/bin/env python


import numpy as np

from diffpy.morph.morph_api import morph, morph_default_config
from tests.test_morphstretch import heaviside


def test_morphfunc_verbose():
    lb, ub = 1, 2
    x_target = np.arange(0.01, 5, 0.01)
    y_target = heaviside(x_target, lb, ub)
    # expand 30%
    stretch = 0.3
    x_morph = x_target.copy()
    y_morph = heaviside(x_target, lb * (1 + stretch), ub * (1 + stretch))
    cfg = morph_default_config(stretch=0.1)  # off init
    morph(x_morph, y_morph, x_target, y_target, verbose=True, **cfg)


def test_fixed_morph_with_morphfunc():
    lb, ub = 1, 2
    x_target = np.arange(0.01, 5, 0.01)
    y_target = heaviside(x_target, lb, ub)
    # expand 30%
    stretch = 0.3
    x_morph = x_target.copy()
    y_morph = heaviside(x_target, lb * (1 + stretch), ub * (1 + stretch))
    cfg = morph_default_config(stretch=0.1)  # off init
    cfg["scale"] = 30
    morph(
        x_morph,
        y_morph,
        x_target,
        y_target,
        verbose=True,
        fixed_operations=["scale"],
        **cfg,
    )


def test_stretch_with_morphfunc():
    # use the same setup as test_moprhchain
    lb, ub = 1, 2
    x_target = np.arange(0.01, 5, 0.01)
    y_target = heaviside(x_target, lb, ub)
    # expand 30%
    stretch = 0.3
    x_morph = x_target.copy()
    y_morph = heaviside(x_target, lb * (1 + stretch), ub * (1 + stretch))
    cfg = morph_default_config(stretch=0.1)  # off init
    morph_rv = morph(x_morph, y_morph, x_target, y_target, **cfg)
    morphed_cfg = morph_rv["morphed_config"]
    # verified they are morphable
    x1, y1, x0, y0 = morph_rv["morph_chain"].xyallout
    assert np.allclose(x0, x1)
    assert np.allclose(y0, y1)
    # verify morphed param
    # note: because interpolation, the value might be off by 0.5
    # negative sign as we are compress the gref
    assert np.allclose(-stretch, morphed_cfg["stretch"], atol=1e-1)


def test_scale_with_morphfunc():
    lb, ub = 1, 2
    x_target = np.arange(0.01, 5, 0.01)
    y_target = heaviside(x_target, lb, ub)
    # scale 300%
    scale = 3
    x_morph = x_target.copy()
    y_morph = y_target.copy()
    y_morph *= scale
    cfg = morph_default_config(scale=1.5)  # off init
    morph_rv = morph(x_morph, y_morph, x_target, y_target, **cfg)
    morphed_cfg = morph_rv["morphed_config"]
    # verified they are morphable
    x1, y1, x0, y0 = morph_rv["morph_chain"].xyallout
    assert np.allclose(x0, x1)
    assert np.allclose(y0, y1)
    # verify morphed param
    assert np.allclose(scale, 1 / morphed_cfg["scale"], atol=1e-1)


def test_smear_with_morph_func():
    # gaussian func
    sigma0 = 0.1
    smear = 0.15
    sigbroad = (sigma0**2 + smear**2) ** 0.5
    r0 = 7 * np.pi / 22.0 * 2
    x_target = np.arange(0.01, 5, 0.01)
    y_target = np.exp(-0.5 * ((x_target - r0) / sigbroad) ** 2)
    x_morph = x_target.copy()
    y_morph = np.exp(-0.5 * ((x_morph - r0) / sigma0) ** 2)
    cfg = morph_default_config(smear=0.1, scale=1.1, stretch=0.1)  # off init
    morph_rv = morph(x_morph, y_morph, x_target, y_target, **cfg)
    morphed_cfg = morph_rv["morphed_config"]
    # verified they are morphable
    x1, y1, x0, y0 = morph_rv["morph_chain"].xyallout
    assert np.allclose(x0, x1)
    assert np.allclose(y0, y1, atol=1e-3)  # numerical error -> 1e-4
    # verify morphed param
    assert np.allclose(smear, morphed_cfg["smear"], atol=1e-1)


def test_squeeze_with_morph_func():
    squeeze_init = {"a0": 0, "a1": -0.001, "a2": -0.0001, "a3": 0.0001}
    x_morph = np.linspace(0, 10, 101)
    y_morph = 2 * np.sin(
        x_morph + x_morph * 0.01 + 0.0001 * x_morph**2 + 0.001 * x_morph**3
    )
    expected_squeeze = {"a0": 0, "a1": 0.01, "a2": 0.0001, "a3": 0.001}
    expected_scale = 1 / 2
    x_target = np.linspace(0, 10, 101)
    y_target = np.sin(x_target)
    cfg = morph_default_config(scale=1.1, squeeze=squeeze_init)
    morph_rv = morph(x_morph, y_morph, x_target, y_target, **cfg)
    morphed_cfg = morph_rv["morphed_config"]
    x_morph_out, y_morph_out, x_target_out, y_target_out = morph_rv[
        "morph_chain"
    ].xyallout
    assert np.allclose(x_morph_out, x_target_out)
    assert np.allclose(y_morph_out, y_target_out, atol=1e-6)
    assert np.allclose(
        expected_squeeze["a0"], morphed_cfg["squeeze"]["a0"], atol=1e-6
    )
    assert np.allclose(
        expected_squeeze["a1"], morphed_cfg["squeeze"]["a1"], atol=1e-6
    )
    assert np.allclose(
        expected_squeeze["a2"], morphed_cfg["squeeze"]["a2"], atol=1e-6
    )
    assert np.allclose(
        expected_squeeze["a3"], morphed_cfg["squeeze"]["a3"], atol=1e-6
    )
    assert np.allclose(expected_scale, morphed_cfg["scale"], atol=1e-6)


def test_funcy_with_morph_func():
    def linear_function(x, y, scale, offset):
        return (scale * x) * y + offset

    x_morph = np.linspace(0, 10, 101)
    y_morph = np.sin(x_morph)
    x_target = x_morph.copy()
    y_target = np.sin(x_target) * 2 * x_target + 0.4
    cfg = morph_default_config(funcy={"scale": 1.2, "offset": 0.1})
    cfg["function"] = linear_function
    morph_rv = morph(x_morph, y_morph, x_target, y_target, **cfg)
    morphed_cfg = morph_rv["morphed_config"]
    x_morph_out, y_morph_out, x_target_out, y_target_out = morph_rv[
        "morph_chain"
    ].xyallout
    assert np.allclose(x_morph_out, x_target_out)
    assert np.allclose(y_morph_out, y_target_out, atol=1e-6)
    fitted_parameters = morphed_cfg["funcy"]
    assert np.allclose(fitted_parameters["scale"], 2, atol=1e-6)
    assert np.allclose(fitted_parameters["offset"], 0.4, atol=1e-6)
