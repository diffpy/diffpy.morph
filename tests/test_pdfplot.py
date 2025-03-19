#!/usr/bin/env python


import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from diffpy.morph.morph_api import morph, morph_default_config, plot_morph
from tests.test_morphstretch import heaviside


# smoke test
def test_plot_morph():
    lb, ub = 1, 2
    x_target = np.arange(0.01, 5, 0.01)
    y_target = heaviside(x_target, lb, ub)
    # expand 30%
    stretch = 0.3
    x_morph = x_target.copy()
    y_morph = heaviside(x_target, lb * (1 + stretch), ub * (1 + stretch))
    cfg = morph_default_config(stretch=0.1)  # off init
    morph_rv = morph(x_morph, y_morph, x_target, y_target, verbose=True, **cfg)
    chain = morph_rv["morph_chain"]
    fig, ax = plt.subplots()
    l_list = plot_morph(chain, ax)
    assert all([isinstance(x, mpl.lines.Line2D) for x in l_list])
