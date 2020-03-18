#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""These test-cases are based on the examples from ASAM MCD-2MC Version 1.6 specification.
"""

import pytest

from pya2l import functions

try:
    import numpy as np
except ImportError:
    has_numpy = False
else:
    has_numpy = True

try:
    from scipy.interpolate import RegularGridInterpolator
except ImportError:
    has_scipy = False
else:
    has_scipy = True


def test_axis_rescale_ok():
    EXPECTED = [
        0, 16.666666666666668, 33.333333333333336, 50.0, 66.66666666666667, 83.33333333333333, 100.0, 158.9206349206349, 216
    ]
    assert functions.axis_rescale(no_rescale_x = 3, no_axis_pts = 9,
        axis = (0x00, 0x64, 0xD8), virtual = (0x00, 0xC0, 0xFF)
        ) == EXPECTED

X_NORM = (
    (0.0,       2.0),
    (200.0,     2.7),
    (400.0,     3.0),
    (1000.0,    4.2),
    (5700,      4.9),
)

X_IDENT = (
    (0.0,       0.0),
    (1.0,       1.0),
    (2.0,       2.0),
    (3.0,       3.0),
    (4.0,       4.0),
    (5.0,       5.0),
    (6.0,       6.0),
)

Y_NORM = (
    (0.0,       0.5),
    (50.0,      1.0),
    (70.0,      2.4),
    (100.0,     4.2),
)

Y_IDENT = (
    (0.0,       0.0),
    (1.0,       1.0),
    (2.0,       2.0),
    (3.0,       3.0),
    (4.0,       4.0),
    (5.0,       5.0),
)

Z_MAP = (
    (3.4, 4.5, 2.1, 5.4, 1.2, 3.4, 4.4),
    (2.3, 1.2, 1.2, 5.6, 3.2, 2.1, 7.8),
    (3.2, 1.5, 3.2, 2.2, 1.6, 1.7, 1.7),
    (2.1, 0.4, 1.0, 1.5, 1.8, 3.2, 1.5),
    (1.1, 4.3, 2.1, 4.6, 1.2, 1.4, 3.2),
    (1.2, 5.3, 3.2, 3.5, 2.1, 1.4, 4.2),
)

@pytest.mark.skipif("has_numpy == False or has_scipy == False")
def test_normalization_axes():
    na = functions.NormalizationAxes(X_NORM, Y_NORM, Z_MAP)
    assert na(850, 60) == 2.194

@pytest.mark.skipif("has_numpy == False or has_scipy == False")
def test_normalization_ident():
    na = functions.NormalizationAxes(X_IDENT, Y_IDENT, Z_MAP)
    for row_idx, row in enumerate(Z_MAP):
        for col_idx, value in enumerate(row):
            assert value == na(col_idx, row_idx)    # Interpolator should just pick every element from Z_MAP.


@pytest.mark.skipif("has_numpy == False or has_scipy == False")
def test_ratfunc_identity():
    rf = functions.RatFunc([0, 1, 0, 0, 0, 1])
    assert rf(21845) == 21845
