#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""These test-cases are based on the examples from ASAM MCD-2MC Version 1.6 specification.
"""

import math

import pytest

from pya2l import functions
from pya2l import exceptions
from pya2l.a2l_listener import ParserWrapper, A2LListener
from pya2l import model

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


RUN_MATH_TEST = has_numpy == True and has_scipy == True


class Value:
    """Value dummy class.
    """

Xs = [0.0, 200.0, 400.0, 1000.0, 5700.0]
Ys = [2.0,  2.7, 3.0,  4.2, 4.9]
Xins = [-1.0, 0.0, 850.0, 5700.0, 8000.0]
Rs = [2.0, 2.0, 3.9000000000000004, 4.9, 4.9]

@pytest.mark.skipif("RUN_MATH_TEST == False")
@pytest.mark.parametrize("x, expected", zip(Xins, Rs))
def test_interpolate1D_saturate(x, expected):
    interp = functions.Interpolate1D(pairs = zip(Xs, Ys), saturate = True)
    assert interp(x) == expected


XsOutOfBounds = [-1.0, 8000.0]
expected = [None, None]

@pytest.mark.skipif("RUN_MATH_TEST == False")
@pytest.mark.parametrize("x, expected", zip(XsOutOfBounds, expected))
def test_interpolate1D_out_of_bounds(x, expected):
    interp = functions.Interpolate1D(pairs = zip(Xs, Ys), saturate = False)
    with pytest.raises(ValueError):
        interp(x) == expected


@pytest.mark.skipif("RUN_MATH_TEST == False")
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

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_normalization_axes():
    na = functions.NormalizationAxes(X_NORM, Y_NORM, Z_MAP)
    assert na(850, 60) == 2.194

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_normalization_ident():
    na = functions.NormalizationAxes(X_IDENT, Y_IDENT, Z_MAP)
    for row_idx, row in enumerate(Z_MAP):
        for col_idx, value in enumerate(row):
            assert value == na(col_idx, row_idx)    # Interpolator should just pick every element from Z_MAP.

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_identity():
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 1
    coeffs.c = 0
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 1
    rf = functions.RatFunc(coeffs)
    assert rf(21845) == 21845

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_linear():
    xs = np.arange(-10, 11)
    ys = np.array(
        [-6.4, -5.6, -4.8, -4., -3.2, -2.4, -1.6, -0.8, 0., 0.8, 1.6, 2.4, 3.2, 4., 4.8, 5.6, 6.4, 7.2, 8., 8.8, 9.6],
        dtype = "float"
    )
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 4
    coeffs.c = 8
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 5
    rf = functions.RatFunc(coeffs)
    assert np.array_equal(rf(xs), ys)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_linear_scalar():
    x = -10
    y = -6.4
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 4
    coeffs.c = 8
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 5
    rf = functions.RatFunc(coeffs)
    assert rf(x) == y

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_linear_inv():
    xs = np.arange(-10, 11)
    ys = np.array(
        [-6.4, -5.6, -4.8, -4., -3.2, -2.4, -1.6, -0.8, 0., 0.8, 1.6, 2.4, 3.2, 4., 4.8, 5.6, 6.4, 7.2, 8., 8.8, 9.6],
        dtype = "float"
    )
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 4
    coeffs.c = 8
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 5
    rf = functions.RatFunc(coeffs)
    assert np.array_equal(rf.inv(ys), xs)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_linear_inv_scalar():
    x = -10
    y = -6.4
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 4
    coeffs.c = 8
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 5
    rf = functions.RatFunc(coeffs)
    assert rf.inv(y) == x

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_constant():
    xs = np.arange(-10, 11)
    ys = np.full((21,), 10.0)
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 0
    coeffs.c = 20
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 2
    rf = functions.RatFunc(coeffs)
    assert np.array_equal(rf(xs), ys)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_constant_scalar():
    x = -10
    y = 10.0
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 0
    coeffs.c = 20
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 2
    rf = functions.RatFunc(coeffs)
    assert rf(x) ==  y

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_constant_inv():
    xs = np.arange(-10, 11)
    ys = np.full((21,), 10.0)
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 0
    coeffs.c = 20
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 20
    rf = functions.RatFunc(coeffs)
    with pytest.raises(exceptions.MathError):
        rf.inv(ys)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_constant_inv_scalar():
    x = -10
    y = 10.0
    coeffs = Value()
    coeffs.a = 0
    coeffs.b = 0
    coeffs.c = 20
    coeffs.d = 0
    coeffs.e = 0
    coeffs.f = 20
    rf = functions.RatFunc(coeffs)
    with pytest.raises(exceptions.MathError):
        rf.inv(y)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_quadratic():
    xs = np.arange(-10, 11)
    ys = np.array([1.231638418079096, 1.1917808219178083, 1.1440677966101696, 1.086021505376344, 1.0140845070422535,
                   0.9230769230769231, 0.8055555555555556, 0.6521739130434783, 0.46153846153846156,0.3333333333333333,
                   1.5, 9.0, 6.666666666666667, 4.5, 3.5625, 3.074074074074074, 2.7804878048780486, 2.586206896551724,
                   2.448717948717949, 2.3465346534653464, 2.267716535433071
    ])
    coeffs = Value()
    coeffs.a = 5
    coeffs.b = 7
    coeffs.c = 6
    coeffs.d = 3
    coeffs.e = -5
    coeffs.f = 4
    rf = functions.RatFunc(coeffs)
    assert np.array_equal(rf(xs), ys)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_quadratic_scalar():
    x = -10
    y = 1.231638418079096
    coeffs = Value()
    coeffs.a = 5
    coeffs.b = 7
    coeffs.c = 6
    coeffs.d = 3
    coeffs.e = -5
    coeffs.f = 4
    rf = functions.RatFunc(coeffs)
    assert rf(x) == y

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_quadratic_inv():
    xs = np.arange(-10, 11)
    coeffs = Value()
    coeffs.a = 5
    coeffs.b = 7
    coeffs.c = 6
    coeffs.d = 3
    coeffs.e = -5
    coeffs.f = 4
    rf = functions.RatFunc(coeffs)
    with pytest.raises(NotImplementedError):
        rf.inv(xs)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_quadratic_inv_scalar():
    x = -10
    coeffs = Value()
    coeffs.a = 5
    coeffs.b = 7
    coeffs.c = 6
    coeffs.d = 3
    coeffs.e = -5
    coeffs.f = 4
    rf = functions.RatFunc(coeffs)
    with pytest.raises(NotImplementedError):
        rf.inv(x)

def test_identical():
    xs = np.arange(-10, 11)
    rf = functions.Identical()
    assert np.array_equal(rf(xs), xs)

def test_identical_scalar():
    x = -10
    rf = functions.Identical()
    assert rf(x) == x

def test_identical_inv():
    xs = np.arange(-10, 11)
    rf = functions.Identical()
    assert np.array_equal(rf.inv(xs), xs)

def test_identical_inv_scalar():
    x = -10
    rf = functions.Identical()
    assert rf.inv(x) == x

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_linear():
    xs = np.arange(-10, 11)
    ys = np.array([-43, -39, -35, -31, -27, -23, -19, -15, -11, -7, -3, 1, 5, 9, 13, 17, 21, 25, 29, 33, 37
    ])
    coeffs = Value()
    coeffs.a = 4
    coeffs.b = -3
    rf = functions.Linear(coeffs)
    assert np.array_equal(rf(xs), ys)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_linear_scalar():
    x = -10
    y = -43
    coeffs = Value()
    coeffs.a = 4
    coeffs.b = -3
    rf = functions.Linear(coeffs)
    assert rf(x) == y

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_linear_inv():
    xs = np.arange(-10, 11)
    ys = np.array([-43, -39, -35, -31, -27, -23, -19, -15, -11, -7, -3, 1, 5, 9, 13, 17, 21, 25, 29, 33, 37
    ])
    coeffs = Value()
    coeffs.a = 4
    coeffs.b = -3
    rf = functions.Linear(coeffs)
    assert np.array_equal(rf.inv(ys), xs)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_linear_inv_scalar():
    x = -10
    y = -43
    coeffs = Value()
    coeffs.a = 4
    coeffs.b = -3
    rf = functions.Linear(coeffs)
    assert rf.inv(y) == x

def test_tab_verb_with_default():
    mapping = [
        (1, "SawTooth"),
        (2, "Square"),
        (3, "Sinus"),
    ]
    default = "unknown signal type"
    tv = functions.LookupTable(mapping, default = default)
    assert tv(2) == "Square"
    assert tv(5) == default

def test_tab_verb_with_default_vectorized():
    mapping = [
        (1, "SawTooth"),
        (2, "Square"),
        (3, "Sinus"),
    ]
    default = "unknown signal type"
    xs = [1, 2, 3, 5]
    ys = ["SawTooth", "Square", "Sinus", default]
    tv = functions.LookupTable(mapping, default = default)
    assert np.array_equal(tv(xs), ys)

def test_tab_verb_with_default_inv():
    mapping = [
        (1, "SawTooth"),
        (2, "Square"),
        (3, "Sinus"),
    ]
    default = "unknown signal type"
    tv = functions.LookupTable(mapping, default = default)
    assert tv.inv("Square") == 2
    assert tv.inv(default) is None

def test_tab_verb_with_default_inv_vectorized():
    mapping = [
        (1, "SawTooth"),
        (2, "Square"),
        (3, "Sinus"),
    ]
    default = "unknown signal type"
    xs = [1, 2, 3]
    ys = ["SawTooth", "Square", "Sinus"]
    tv = functions.LookupTable(mapping, default = default)
    assert np.array_equal(tv.inv(ys), xs)

def test_tab_verb_ranges_with_default():
    mapping = [
       (0, 1, "Zero_to_one"),
       (2, 3, "two_to_three"),
       (4, 7, "four_to_seven"),
       (14, 17, "fourteen_to_seventeen"),
       (18, 99, "eigteen_to_ninetynine"),
       (100, 100, "hundred"),
       (101, 101, "hundredone"),
       (102, 102, "hundredtwo"),
       (103, 103, "hundredthree"),
       (104, 104, "hundredfour"),
       (105, 105, "hundredfive")
    ]
    default = "out of range value"
    tvr = functions.LookupTableWithRanges(mapping, default = default, dtype = int)
    assert tvr(0) == "Zero_to_one"
    assert tvr(6) == "four_to_seven"
    assert tvr(45) == "eigteen_to_ninetynine"
    assert tvr(100) == "hundred"
    assert tvr(105) == "hundredfive"
    assert tvr(-1) == "out of range value"
    assert tvr(106) == "out of range value"
    assert tvr(10) == "out of range value"

def test_tab_verb_ranges_with_default_vectorized():
    mapping = [
       (0, 1, "Zero_to_one"),
       (2, 3, "two_to_three"),
       (4, 7, "four_to_seven"),
       (14, 17, "fourteen_to_seventeen"),
       (18, 99, "eigteen_to_ninetynine"),
       (100, 100, "hundred"),
       (101, 101, "hundredone"),
       (102, 102, "hundredtwo"),
       (103, 103, "hundredthree"),
       (104, 104, "hundredfour"),
       (105, 105, "hundredfive")
    ]
    default = "out of range value"
    xs = [0, 6, 45, 100, 105, -1, 106, 10]
    ys = ["Zero_to_one", "four_to_seven", "eigteen_to_ninetynine", "hundred", "hundredfive",
          "out of range value", "out of range value", "out of range value"]
    tvr = functions.LookupTableWithRanges(mapping, default = default, dtype = int)
    assert np.array_equal(tvr(xs), ys)

def test_tab_verb_ranges_inverse():
    mapping = [
       (0, 1, "Zero_to_one"),
       (2, 3, "two_to_three"),
       (4, 7, "four_to_seven"),
       (14, 17, "fourteen_to_seventeen"),
       (18, 99, "eigteen_to_ninetynine"),
       (100, 100, "hundred"),
       (101, 101, "hundredone"),
       (102, 102, "hundredtwo"),
       (103, 103, "hundredthree"),
       (104, 104, "hundredfour"),
       (105, 105, "hundredfive")
    ]
    default = "out of range value"
    tvr = functions.LookupTableWithRanges(mapping, default = default, dtype = int)
    assert tvr.inv("Zero_to_one") == 0
    assert tvr.inv("four_to_seven") == 4
    assert tvr.inv("eigteen_to_ninetynine") == 18
    assert tvr.inv("hundred") == 100
    assert tvr.inv("hundredfive") == 105

def test_tab_verb_ranges_inverse_vectorized():
    mapping = [
       (0, 1, "Zero_to_one"),
       (2, 3, "two_to_three"),
       (4, 7, "four_to_seven"),
       (14, 17, "fourteen_to_seventeen"),
       (18, 99, "eigteen_to_ninetynine"),
       (100, 100, "hundred"),
       (101, 101, "hundredone"),
       (102, 102, "hundredtwo"),
       (103, 103, "hundredthree"),
       (104, 104, "hundredfour"),
       (105, 105, "hundredfive")
    ]
    default = "out of range value"
    tvr = functions.LookupTableWithRanges(mapping, default = default, dtype = int)
    xs = ["Zero_to_one", "four_to_seven", "eigteen_to_ninetynine", "hundred", "hundredfive"]
    ys = [0, 4, 18, 100, 105]
    assert np.array_equal(tvr.inv(xs), ys)

def test_tab_verb_ranges_with_default_negative():
    mapping = [
       (-1, 0, "minus_one_to_zero"),
       (-3, -2, "minus_three_minus_two"),
       (-7, -4, "minus_seven_to_minus_four"),
       (-17, -14, "minus_seventeen_minus_fourteen"),
       (-99, -18, "minus_ninetynine_minus_eigteen"),
       (-100, -100, "minus_hundred"),
       (-101, -101, "minus_hundredone"),
       (-102, -102, "minus_hundredtwo"),
       (-103, -103, "minus_hundredthree"),
       (-104, -104, "minus_hundredfour"),
       (-105, -105, "minus_hundredfive")
    ]
    default = "out of range value"
    tvr = functions.LookupTableWithRanges(mapping, default = default, dtype = int)
    assert tvr(0) == "minus_one_to_zero"
    assert tvr(-6) == "minus_seven_to_minus_four"
    assert tvr(-45) == "minus_ninetynine_minus_eigteen"
    assert tvr(-100) == "minus_hundred"
    assert tvr(-105) == "minus_hundredfive"
    assert tvr(1) == "out of range value"
    assert tvr(-106) == "out of range value"
    assert tvr(-10) == "out of range value"

def test_tab_verb_ranges_with_default_negative_vectorized():
    mapping = [
       (-1, 0, "minus_one_to_zero"),
       (-3, -2, "minus_three_minus_two"),
       (-7, -4, "minus_seven_to_minus_four"),
       (-17, -14, "minus_seventeen_minus_fourteen"),
       (-99, -18, "minus_ninetynine_minus_eigteen"),
       (-100, -100, "minus_hundred"),
       (-101, -101, "minus_hundredone"),
       (-102, -102, "minus_hundredtwo"),
       (-103, -103, "minus_hundredthree"),
       (-104, -104, "minus_hundredfour"),
       (-105, -105, "minus_hundredfive")
    ]
    default = "out of range value"
    tvr = functions.LookupTableWithRanges(mapping, default = default, dtype = int)
    xs = [0, -6, -45, -100, -105, 1, -106, -10]
    ys = ["minus_one_to_zero", "minus_seven_to_minus_four", "minus_ninetynine_minus_eigteen", "minus_hundred", "minus_hundredfive",
    "out of range value", "out of range value", "out of range value"]
    assert np.array_equal(tvr(xs), ys)

def test_formula_with_no_parameters_raises():
    form = functions.Formula("sin(X1)")
    with pytest.raises(ValueError):
        form()

def test_formula_for_required_operations():
    form = functions.Formula("X1 + X2")
    assert form(23.0, 42.0) == 65.0
    form = functions.Formula("X1 - X2")
    assert form(65.0, 42.0) == 23.0
    form = functions.Formula("X1 * X2")
    assert form(16.0, 16.0) == 256.0
    form = functions.Formula("X1 / X2")
    assert form(256.0, 16.0) == 16.0
#    form = functions.Formula("X1 & X2")
#    assert form(255, 32) == 32
#    form = functions.Formula("X1 | X2")
#    assert form(256, 32) == 0x120
    form = functions.Formula("X1 >> X2")
    assert form(64, 4) == 4
    form = functions.Formula("X1 << X2")
    assert form(64, 4) == 1024
    #form = functions.Formula("~X1")
    #assert form(0x55) == 0xaa

#    form = functions.Formula("X1 ^ X2")
#    assert form(0x55aa, 0x2222) == 0x7788
#    form = functions.Formula("X1 && X2")
#    assert form(1, 0) == 0
#    form = functions.Formula("X1 || X2")
#    assert form(1, 0) == 1
#    form = functions.Formula("!(X1 || X2)")
#    assert form(1, 0) == 0

def test_formula_for_required_functions():
    form = functions.Formula("sin(X1)")
    assert form(.5) == 0.479425538604203
    form = functions.Formula("asin(X1)")
    assert form(0.479425538604203) == .5
    form = functions.Formula("cos(X1)")
    assert form(.5) == 0.8775825618903728
    form = functions.Formula("acos(X1)")
    assert form(0.8775825618903728) == 0.4999999999999999
    form = functions.Formula("tan(X1)")
    assert form(.5) == 0.5463024898437905
    form = functions.Formula("atan(X1)")
    assert form(0.5463024898437905) == .5
    form = functions.Formula("cosh(X1)")
    assert form(math.log(2)) == 1.25
    form = functions.Formula("sinh(X1)")
    assert form(math.log(2)) == .75
    form = functions.Formula("tanh(X1)")
    assert form(math.log(2)) == 0.6
    form = functions.Formula("exp(X1)")
    assert form(math.log(10)) == 10.000000000000002
    form = functions.Formula("log(X1)")
    assert form(math.exp(10)) == 10.0
    form = functions.Formula("abs(X1)")
    assert form(-23.0) == 23.0
    form = functions.Formula("sqrt(X1)")
    assert form(225.0) == 15.0
    form = functions.Formula("pow(X1, X2)")
    assert form(2.0, 16.0) == 65536.0



##
## Basic Integration Tests.
##
@pytest.mark.skip
def test_compu_method_invalid():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_VERB.DEFAULT_VALUE
          "Verbal conversion with default value"
          FOO_BAR "%12.0" ""
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])

def test_compu_method_tab_verb():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_VERB.DEFAULT_VALUE
          "Verbal conversion with default value"
          TAB_VERB "%12.0" ""
          COMPU_TAB_REF CM.TAB_VERB.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB CM.TAB_VERB.DEFAULT_VALUE.REF
          "List of text strings and relation to impl value"
          TAB_VERB 3
          1 "SawTooth"
          2 "Square"
          3 "Sinus"
          DEFAULT_VALUE "unknown signal type"
        /end COMPU_VTAB
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    assert compu(1) == "SawTooth"
    assert compu.inv("Sinus") == 3
    assert compu(10) == "unknown signal type"

def test_compu_method_tab_verb_no_default_value():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_VERB.DEFAULT_VALUE
          "Verbal conversion with default value"
          TAB_VERB "%12.0" ""
          COMPU_TAB_REF CM.TAB_VERB.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB CM.TAB_VERB.DEFAULT_VALUE.REF
          "List of text strings and relation to impl value"
          TAB_VERB 3
          1 "SawTooth"
          2 "Square"
          3 "Sinus"
        /end COMPU_VTAB
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    assert compu(1) == "SawTooth"
    assert compu.inv("Sinus") == 3
    assert compu(10) is None

def test_compu_method_tab_verb_no_vtab():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_VERB.DEFAULT_VALUE
          "Verbal conversion with default value"
          TAB_VERB "%12.0" ""
          COMPU_TAB_REF CM.TAB_VERB.DEFAULT_VALUE.REF
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    with pytest.raises(exceptions.StructuralError):
        compu = functions.CompuMethod(session, module.compu_method[0])


def test_compu_method_tab_nointerp_default():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_NOINTP.DEFAULT_VALUE
          ""
          TAB_NOINTP "%8.4" "U/  min  "
          COMPU_TAB_REF CM.TAB_NOINTP.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_TAB CM.TAB_NOINTP.DEFAULT_VALUE.REF
           ""
           TAB_NOINTP
           12
           -3 98
           -1 99
           0 100
           2 102
           4 104
           5 105
           6 106
           7 107
           8 108
           9 109
           10 110
           13 111
           DEFAULT_VALUE_NUMERIC 300.56 /* DEFAULT_VALUE_NUME RIC should be used here as the normal output is numeric */
        /end COMPU_TAB
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    assert compu(-3) == 98
    assert compu(8) == 108
    assert compu.inv(108) == 8
    assert compu(1) == 300.56

def test_compu_method_tab_interp_default():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_INTP.DEFAULT_VALUE
          ""
          TAB_INTP "%8.4" "U/  min  "
          COMPU_TAB_REF CM.TAB_INTP.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_TAB CM.TAB_INTP.DEFAULT_VALUE.REF
           ""
           TAB_INTP
           12
           -3 98
           -1 99
           0 100
           2 102
           4 104
           5 105
           6 106
           7 107
           8 108
           9 109
           10 110
           13 111
           DEFAULT_VALUE_NUMERIC 300.56 /* DEFAULT_VALUE_NUME RIC should be used here as the normal output is numeric */
        /end COMPU_TAB
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    xs = np.arange(-3, 14)
    ys = np.array(
        [98., 98.5, 99., 100., 101., 102., 103., 104., 105., 106.,
         107., 108., 109., 110., 110.33333333333333, 110.66666666666667, 111.]
    )
    assert np.array_equal(compu(xs), ys)
    assert compu(-3) == 98
    assert compu(8) == 108
    assert compu(14) == 300.56
    assert compu(-4) == 300.56


def test_compu_method_tab_interp_no_default():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_INTP.NO_DEFAULT_VALUE
          ""
          TAB_INTP "%8.4" "U/  min  "
          COMPU_TAB_REF CM.TAB_INTP.NO_DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_TAB CM.TAB_INTP.NO_DEFAULT_VALUE.REF
           ""
           TAB_INTP
           12
           -3 98
           -1 99
           0 100
           2 102
           4 104
           5 105
           6 106
           7 107
           8 108
           9 109
           10 110
           13 111
        /end COMPU_TAB
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    xs = np.arange(-3, 14)
    ys = np.array(
        [98., 98.5, 99., 100., 101., 102., 103., 104., 105., 106.,
         107., 108., 109., 110., 110.33333333333333, 110.66666666666667, 111.]
    )
    assert np.array_equal(compu(xs), ys)
    assert compu(-3) == 98
    assert compu(8) == 108
    assert compu(14) is None
    assert compu(-4) is None

def test_compu_method_tab_nointerp_no_default():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_NOINTP.NO_DEFAULT_VALUE
          ""
          TAB_NOINTP "%8.4" "U/  min  "
          COMPU_TAB_REF CM.TAB_NOINTP.NO_DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_TAB CM.TAB_NOINTP.NO_DEFAULT_VALUE.REF
           ""
           TAB_NOINTP
           12
           -3 98
           -1 99
           0 100
           2 102
           4 104
           5 105
           6 106
           7 107
           8 108
           9 109
           10 110
           13 111
        /end COMPU_TAB
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    assert compu(-3) == 98
    assert compu(8) == 108
    assert compu.inv(108) == 8
    assert compu(1) is None

def test_compu_method_tab_nointerp_both_defaults():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_NOINTP.DEFAULT_VALUE
          ""
          TAB_NOINTP "%8.4" "U/  min  "
          COMPU_TAB_REF CM.TAB_NOINTP.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_TAB CM.TAB_NOINTP.DEFAULT_VALUE.REF
           ""
           TAB_NOINTP
           12
           -3 98
           -1 99
           0 100
           2 102
           4 104
           5 105
           6 106
           7 107
           8 108
           9 109
           10 110
           13 111
           DEFAULT_VALUE "value out of range"
           DEFAULT_VALUE_NUMERIC 300.56 /* DEFAULT_VALUE_NUME RIC should be used here as the normal output is numeric */
        /end COMPU_TAB
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    with pytest.raises(exceptions.StructuralError):
        compu = functions.CompuMethod(session, module.compu_method[0])

def test_compu_method_tab_verb_ranges():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.VTAB_RANGE.DEFAULT_VALUE
           "verbal range with default value"
           TAB_VERB
           "%4.2"
           ""
           COMPU_TAB_REF CM.VTAB_RANGE.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB_RANGE CM.VTAB_RANGE.DEFAULT_VALUE.REF
           ""
           11
           0 1 "Zero_to_one"
           2 3 "two_to_three"
           4 7 "four_to_seven"
           14 17 "fourteen_to_seventeen"
           18 99 "eigteen_to_ninetynine"
           100 100 "hundred"
           101 101 "hundredone"
           102 102 "hundredtwo"
           103 103 "hundredthree"
           104 104 "hundredfour"
           105 105 "hundredfive"
           DEFAULT_VALUE "out of range value"
        /end COMPU_VTAB_RANGE
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    assert compu(0) == "Zero_to_one"
    assert compu(6) == "four_to_seven"
    assert compu(45) == "eigteen_to_ninetynine"
    assert compu(100) == "hundred"
    assert compu(105) == "hundredfive"
    assert compu(-1) == "out of range value"
    assert compu(106) == "out of range value"
    assert compu(10) == "out of range value"

def test_compu_method_tab_verb_ranges_no_default():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.VTAB_RANGE.NO_DEFAULT_VALUE
           "verbal range without default value"
           TAB_VERB
           "%4.2"
           ""
           COMPU_TAB_REF CM.VTAB_RANGE.NO_DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB_RANGE CM.VTAB_RANGE.NO_DEFAULT_VALUE.REF
           ""
           11
           0 1 "Zero_to_one"
           2 3 "two_to_three"
           4 7 "four_to_seven"
           14 17 "fourteen_to_seventeen"
           18 99 "eigteen_to_ninetynine"
           100 100 "hundred"
           101 101 "hundredone"
           102 102 "hundredtwo"
           103 103 "hundredthree"
           104 104 "hundredfour"
           105 105 "hundredfive"
        /end COMPU_VTAB_RANGE
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    assert compu(0) == "Zero_to_one"
    assert compu(6) == "four_to_seven"
    assert compu(45) == "eigteen_to_ninetynine"
    assert compu(100) == "hundred"
    assert compu(105) == "hundredfive"
    assert compu(-1) is None
    assert compu(106) is None
    assert compu(10) is None

def test_compu_method_tab_verb_ranges_inv():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.VTAB_RANGE.DEFAULT_VALUE
           "verbal range with default value"
           TAB_VERB
           "%4.2"
           ""
           COMPU_TAB_REF CM.VTAB_RANGE.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB_RANGE CM.VTAB_RANGE.DEFAULT_VALUE.REF
           ""
           11
           0 1 "Zero_to_one"
           2 3 "two_to_three"
           4 7 "four_to_seven"
           14 17 "fourteen_to_seventeen"
           18 99 "eigteen_to_ninetynine"
           100 100 "hundred"
           101 101 "hundredone"
           102 102 "hundredtwo"
           103 103 "hundredthree"
           104 104 "hundredfour"
           105 105 "hundredfive"
           DEFAULT_VALUE "out of range value"
        /end COMPU_VTAB_RANGE
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    assert compu.inv("Zero_to_one") == 0
    assert compu.inv("four_to_seven") == 4
    assert compu.inv("eigteen_to_ninetynine") == 18
    assert compu.inv("hundred") == 100
    assert compu.inv("hundredfive") == 105
    assert compu.inv("out of range value") is None

def test_compu_method_identical():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.IDENTICAL
          "conversion that delivers always phys = int"
          IDENTICAL "%3.0" "hours"
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    xs = np.arange(-10, 11)
    assert np.array_equal(compu(xs), xs)
    assert np.array_equal(compu.inv(xs), xs)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_rat_func_identical():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.RAT_FUNC.IDENT
          "rational function with parameter set for int = f(phys) = phys"
          RAT_FUNC "%3.1" "m/s"
          COEFFS 0 1 0 0 0 1
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    xs = np.arange(-10, 11)
    assert np.array_equal(compu(xs), xs)
    assert np.array_equal(compu.inv(xs), xs)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_rat_func_linear():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.RAT_FUNC.DIV_81_9175
          "rational function with parameter set for impl = f(phys) = phys * 81.9175"
          RAT_FUNC "%8.4" "grad C"
          COEFFS 0 81.9175 0 0 0 1
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    xs = np.arange(-10, 11)
    ys = np.array([-819.1750000000001, -737.2575, -655.34, -573.4225, -491.505, -409.58750000000003, -327.67,
        -245.7525, -163.835, -81.9175, 0., 81.9175, 163.835, 245.7525, 327.67, 409.58750000000003,
        491.505, 573.4225, 655.34, 737.2575, 819.1750000000001
    ])
    assert np.array_equal(compu(xs), ys)
    assert np.array_equal(compu.inv(ys), xs)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_rat_func_no_coeffs():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.RAT_FUNC.DIV_81_9175
          "rational function with parameter set for impl = f(phys) = phys * 81.9175"
          RAT_FUNC "%8.4" "grad C"
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    with pytest.raises(exceptions.StructuralError):
        compu = functions.CompuMethod(session, module.compu_method[0])


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_linear():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.LINEAR.MUL_2
        "Linear function with parameter set for phys = f(int) = 2*int + 0"
         LINEAR "%3.1" "m/s"
         COEFFS_LINEAR 2 0
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    xs = np.arange(-10, 11)
    assert np.array_equal(compu(xs), xs * 2.0)
    assert np.array_equal(compu.inv(xs * 2.0), xs)

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_linear_no_coeffs():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.LINEAR.MUL_2
        "Linear function with parameter set for phys = f(int) = 2*int + 0"
         LINEAR "%3.1" "m/s"
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    with pytest.raises(exceptions.StructuralError):
        compu = functions.CompuMethod(session, module.compu_method[0])

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_formula_with_inv():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.FORM.X_PLUS_4
          ""
          FORM
          "%6.1"
          "rpm"
          /begin FORMULA
            "X1+4"
            FORMULA_INV "X1-4"
          /end FORMULA
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    assert compu(6) == 10
    assert compu.inv(4) == 0

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_formula_without_inv():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.FORM.X_PLUS_4
          ""
          FORM
          "%6.1"
          "rpm"
          /begin FORMULA
            "X1+4"
          /end FORMULA
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    assert compu(6) == 10

@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_formula_with_sysc():
    parser = ParserWrapper('a2l', 'module', A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin MOD_PAR ""
             SYSTEM_CONSTANT "System_Constant_1" "42"
             SYSTEM_CONSTANT "System_Constant_2" "Textual constant"
        /end MOD_PAR

        /begin COMPU_METHOD CM.FORM.X_PLUS_SYSC
          ""
          FORM
          "%6.1"
          "rpm"
          /begin FORMULA
            "X1 + sysc(System_Constant_1)"
          /end FORMULA
        /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    compu = functions.CompuMethod(session, module.compu_method[0])
    assert compu(23) == 65
