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
