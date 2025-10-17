#!/usr/bin/env python
"""These test-cases are based on the examples from ASAM MCD-2MC Version 1.6 specification.
"""
import math
from dataclasses import dataclass

import numpy as np
import pytest

from pya2l import exceptions, functions


RUN_MATH_TEST = True


@dataclass
class Coeffs:
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float


Xs = [0.0, 200.0, 400.0, 1000.0, 5700.0]
Ys = [2.0, 2.7, 3.0, 4.2, 4.9]
Xins = [-1.0, 0.0, 850.0, 5700.0, 8000.0]
Rs = [2.0, 2.0, 3.9000000000000004, 4.9, 4.9]


@pytest.mark.skipif("RUN_MATH_TEST == False")
@pytest.mark.parametrize("x, expected", zip(Xins, Rs))
def test_interpolate1D_saturate(x, expected):
    interp = functions.Interpolate1D(pairs=zip(Xs, Ys), saturate=True)
    assert interp(x) == expected


XsOutOfBounds = [-1.0, 8000.0]
expected = [None, None]


@pytest.mark.skipif("RUN_MATH_TEST == False")
@pytest.mark.parametrize("x, expected", zip(XsOutOfBounds, expected))
def test_interpolate1D_out_of_bounds(x, expected):
    interp = functions.Interpolate1D(pairs=zip(Xs, Ys), saturate=False)
    with pytest.raises(ValueError):
        interp(x) == expected


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_axis_rescale_ok():
    EXPECTED = [
        0,
        16.666666666666668,
        33.333333333333336,
        50.0,
        66.66666666666667,
        83.33333333333333,
        100.0,
        158.9206349206349,
        216,
    ]
    assert np.array_equal(
        functions.axis_rescale(
            no_rescale_x=3,
            no_axis_pts=9,
            axis=(0x00, 0x64, 0xD8),
            virtual=(0x00, 0xC0, 0xFF),
        ),
        EXPECTED,
    )


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_fix_axis_par_ok():
    assert np.array_equal(
        functions.fix_axis_par(10, 3, 10),
        np.array([10, 18, 26, 34, 42, 50, 58, 66, 74, 82]),
    )


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_fix_axis_par_dist_ok():
    assert np.array_equal(
        functions.fix_axis_par_dist(7, 4, 10),
        np.array([7, 11, 15, 19, 23, 27, 31, 35, 39, 43]),
    )


X_NORM = (
    (0.0, 2.0),
    (200.0, 2.7),
    (400.0, 3.0),
    (1000.0, 4.2),
    (5700, 4.9),
)

X_IDENT = (
    (0.0, 0.0),
    (1.0, 1.0),
    (2.0, 2.0),
    (3.0, 3.0),
    (4.0, 4.0),
    (5.0, 5.0),
    (6.0, 6.0),
)

Y_NORM = (
    (0.0, 0.5),
    (50.0, 1.0),
    (70.0, 2.4),
    (100.0, 4.2),
)

Y_IDENT = (
    (0.0, 0.0),
    (1.0, 1.0),
    (2.0, 2.0),
    (3.0, 3.0),
    (4.0, 4.0),
    (5.0, 5.0),
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
            assert value == na(col_idx, row_idx)  # Interpolator should just pick every element from Z_MAP.


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_identity():
    coeffs = Coeffs(0, 1, 0, 0, 0, 1)
    rf = functions.RatFunc(coeffs)
    assert rf.int_to_physical(21845) == 21845
    assert rf.physical_to_int(21845) == 21845


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_linear():
    xs = np.arange(-10, 11)
    ys = np.array(
        [
            -6.4,
            -5.6,
            -4.8,
            -4.0,
            -3.2,
            -2.4,
            -1.6,
            -0.8,
            0.0,
            0.8,
            1.6,
            2.4,
            3.2,
            4.0,
            4.8,
            5.6,
            6.4,
            7.2,
            8.0,
            8.8,
            9.6,
        ],
        dtype="float",
    )
    coeffs = Coeffs(0, 4, 8, 0, 0, 5)
    rf = functions.RatFunc(coeffs)
    assert np.array_equal(rf.physical_to_int(xs), ys)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_linear_scalar():
    x = -10
    y = -6.4
    coeffs = Coeffs(0, 4, 8, 0, 0, 5)
    rf = functions.RatFunc(coeffs)
    assert rf.physical_to_int(x) == y


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_linear_inv():
    xs = np.arange(-10, 11)
    ys = np.array(
        [
            -6.4,
            -5.6,
            -4.8,
            -4.0,
            -3.2,
            -2.4,
            -1.6,
            -0.8,
            0.0,
            0.8,
            1.6,
            2.4,
            3.2,
            4.0,
            4.8,
            5.6,
            6.4,
            7.2,
            8.0,
            8.8,
            9.6,
        ],
        dtype="float",
    )
    coeffs = Coeffs(0, 4, 8, 0, 0, 5)
    rf = functions.RatFunc(coeffs)
    assert np.array_equal(rf.int_to_physical(ys), xs)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_linear_inv_scalar():
    x = -10
    y = -6.4
    coeffs = Coeffs(0, 4, 8, 0, 0, 5)
    rf = functions.RatFunc(coeffs)
    assert rf.int_to_physical(y) == x


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_constant():
    xs = np.arange(-10, 11)
    ys = np.full((21,), 10.0)
    coeffs = Coeffs(0, 0, 20, 0, 0, 2)
    rf = functions.RatFunc(coeffs)
    assert np.array_equal(rf.physical_to_int(xs), ys)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_constant_scalar():
    x = -10
    y = 10.0
    coeffs = Coeffs(0, 0, 20, 0, 0, 2)
    rf = functions.RatFunc(coeffs)
    assert rf.physical_to_int(x) == y


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_constant_inv():
    ys = np.full((21,), 10.0)
    coeffs = Coeffs(0, 0, 20, 0, 0, 20)
    rf = functions.RatFunc(coeffs)
    with pytest.raises(exceptions.MathError):
        rf.int_to_physical(ys)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_constant_inv_scalar():
    y = 10.0
    coeffs = Coeffs(0, 0, 20, 0, 0, 20)
    rf = functions.RatFunc(coeffs)
    with pytest.raises(exceptions.MathError):
        rf.int_to_physical(y)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_quadratic():
    xs = np.arange(-10, 11)
    ys = np.array(
        [
            1.231638418079096,
            1.1917808219178083,
            1.1440677966101696,
            1.086021505376344,
            1.0140845070422535,
            0.9230769230769231,
            0.8055555555555556,
            0.6521739130434783,
            0.46153846153846156,
            0.3333333333333333,
            1.5,
            9.0,
            6.666666666666667,
            4.5,
            3.5625,
            3.074074074074074,
            2.7804878048780486,
            2.586206896551724,
            2.448717948717949,
            2.3465346534653464,
            2.267716535433071,
        ]
    )
    coeffs = Coeffs(5, 7, 6, 3, -5, 4)
    rf = functions.RatFunc(coeffs)
    assert np.array_equal(rf.physical_to_int(xs), ys)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_quadratic_scalar():
    x = -10
    y = 1.231638418079096
    coeffs = Coeffs(5, 7, 6, 3, -5, 4)
    rf = functions.RatFunc(coeffs)
    assert rf.physical_to_int(x) == y


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_quadratic_inv():
    xs = np.arange(-10, 11)
    coeffs = Coeffs(5, 7, 6, 3, -5, 4)
    rf = functions.RatFunc(coeffs)
    with pytest.raises(NotImplementedError):
        rf.int_to_physical(xs)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_ratfunc_quadratic_inv_scalar():
    x = -10
    coeffs = Coeffs(5, 7, 6, 3, -5, 4)
    rf = functions.RatFunc(coeffs)
    with pytest.raises(NotImplementedError):
        rf.int_to_physical(x)


def test_identical():
    xs = np.arange(-10, 11)
    rf = functions.Identical()
    assert np.array_equal(rf.int_to_physical(xs), xs)
    assert np.array_equal(rf.physical_to_int(xs), xs)


def test_identical_scalar():
    x = -10
    rf = functions.Identical()
    assert rf.int_to_physical(x) == x
    assert rf.physical_to_int(x) == x


def test_identical_inv():
    xs = np.arange(-10, 11)
    rf = functions.Identical()
    assert np.array_equal(rf.physical_to_int(xs), xs)


def test_identical_inv_scalar():
    x = -10
    rf = functions.Identical()
    assert rf.physical_to_int(x) == x


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_linear():
    xs = np.arange(-10, 11)
    ys = np.array(
        [
            -43,
            -39,
            -35,
            -31,
            -27,
            -23,
            -19,
            -15,
            -11,
            -7,
            -3,
            1,
            5,
            9,
            13,
            17,
            21,
            25,
            29,
            33,
            37,
        ]
    )
    coeffs = Coeffs(4, -3, 0, 0, 0, 0)
    rf = functions.Linear(coeffs)
    assert np.array_equal(rf.int_to_physical(xs), ys)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_linear_scalar():
    x = -10
    y = -43
    coeffs = Coeffs(4, -3, 0, 0, 0, 0)
    rf = functions.Linear(coeffs)
    assert rf.int_to_physical(x) == y


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_linear_inv():
    xs = np.arange(-10, 11)
    ys = np.array(
        [
            -43,
            -39,
            -35,
            -31,
            -27,
            -23,
            -19,
            -15,
            -11,
            -7,
            -3,
            1,
            5,
            9,
            13,
            17,
            21,
            25,
            29,
            33,
            37,
        ]
    )
    coeffs = Coeffs(4, -3, 0, 0, 0, 0)
    rf = functions.Linear(coeffs)
    assert np.array_equal(rf.physical_to_int(ys), xs)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_linear_inv_scalar():
    x = -10
    y = -43
    coeffs = Coeffs(4, -3, 0, 0, 0, 0)
    rf = functions.Linear(coeffs)
    assert rf.physical_to_int(y) == x


def test_tab_verb_with_default():
    mapping = [
        (1, "SawTooth"),
        (2, "Square"),
        (3, "Sinus"),
    ]
    default = "unknown signal type"
    tv = functions.LookupTable(mapping, default=default)
    assert tv.int_to_physical(2) == "Square"
    assert tv.int_to_physical(5) == default


def test_tab_verb_with_default_vectorized():
    mapping = [
        (1, "SawTooth"),
        (2, "Square"),
        (3, "Sinus"),
    ]
    default = "unknown signal type"
    xs = [1, 2, 3, 5]
    ys = ["SawTooth", "Square", "Sinus", default]
    tv = functions.LookupTable(mapping, default=default)
    assert np.array_equal(tv.int_to_physical(xs), ys)


def test_tab_verb_with_default_inv():
    mapping = [
        (1, "SawTooth"),
        (2, "Square"),
        (3, "Sinus"),
    ]
    default = "unknown signal type"
    tv = functions.LookupTable(mapping, default=default)
    assert tv.physical_to_int("Square") == 2
    assert tv.physical_to_int(default) is None


def test_tab_verb_with_default_inv_vectorized():
    mapping = [
        (1, "SawTooth"),
        (2, "Square"),
        (3, "Sinus"),
    ]
    default = "unknown signal type"
    xs = [1, 2, 3]
    ys = ["SawTooth", "Square", "Sinus"]
    tv = functions.LookupTable(mapping, default=default)
    assert np.array_equal(tv.physical_to_int(ys), xs)


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
        (105, 105, "hundredfive"),
    ]
    default = "out of range value"
    tvr = functions.LookupTableWithRanges(mapping, default=default, dtype=int)
    assert tvr.int_to_physical(0) == "Zero_to_one"
    assert tvr.int_to_physical(6) == "four_to_seven"
    assert tvr.int_to_physical(45) == "eigteen_to_ninetynine"
    assert tvr.int_to_physical(100) == "hundred"
    assert tvr.int_to_physical(105) == "hundredfive"
    assert tvr.int_to_physical(-1) == "out of range value"
    assert tvr.int_to_physical(106) == "out of range value"
    assert tvr.int_to_physical(10) == "out of range value"


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
        (105, 105, "hundredfive"),
    ]
    default = "out of range value"
    xs = [0, 6, 45, 100, 105, -1, 106, 10]
    ys = [
        "Zero_to_one",
        "four_to_seven",
        "eigteen_to_ninetynine",
        "hundred",
        "hundredfive",
        "out of range value",
        "out of range value",
        "out of range value",
    ]
    tvr = functions.LookupTableWithRanges(mapping, default=default, dtype=int)
    assert np.array_equal(tvr.int_to_physical(xs), ys)


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
        (105, 105, "hundredfive"),
    ]
    default = "out of range value"
    tvr = functions.LookupTableWithRanges(mapping, default=default, dtype=int)
    assert tvr.physical_to_int("Zero_to_one") == 0
    assert tvr.physical_to_int("four_to_seven") == 4
    assert tvr.physical_to_int("eigteen_to_ninetynine") == 18
    assert tvr.physical_to_int("hundred") == 100
    assert tvr.physical_to_int("hundredfive") == 105


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
        (105, 105, "hundredfive"),
    ]
    default = "out of range value"
    tvr = functions.LookupTableWithRanges(mapping, default=default, dtype=int)
    xs = [
        "Zero_to_one",
        "four_to_seven",
        "eigteen_to_ninetynine",
        "hundred",
        "hundredfive",
    ]
    ys = [0, 4, 18, 100, 105]
    assert np.array_equal(tvr.physical_to_int(xs), ys)


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
        (-105, -105, "minus_hundredfive"),
    ]
    default = "out of range value"
    tvr = functions.LookupTableWithRanges(mapping, default=default, dtype=int)
    assert tvr.int_to_physical(0) == "minus_one_to_zero"
    assert tvr.int_to_physical(-6) == "minus_seven_to_minus_four"
    assert tvr.int_to_physical(-45) == "minus_ninetynine_minus_eigteen"
    assert tvr.int_to_physical(-100) == "minus_hundred"
    assert tvr.int_to_physical(-105) == "minus_hundredfive"
    assert tvr.int_to_physical(1) == "out of range value"
    assert tvr.int_to_physical(-106) == "out of range value"
    assert tvr.int_to_physical(-10) == "out of range value"


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
        (-105, -105, "minus_hundredfive"),
    ]
    default = "out of range value"
    tvr = functions.LookupTableWithRanges(mapping, default=default, dtype=int)
    xs = [0, -6, -45, -100, -105, 1, -106, -10]
    ys = [
        "minus_one_to_zero",
        "minus_seven_to_minus_four",
        "minus_ninetynine_minus_eigteen",
        "minus_hundred",
        "minus_hundredfive",
        "out of range value",
        "out of range value",
        "out of range value",
    ]
    assert np.array_equal(tvr.int_to_physical(xs), ys)


def test_formula_with_no_parameters_raises():
    form = functions.Formula("sin(X1)")
    result = form.int_to_physical()
    assert result.size == 0


def test_formula_for_required_operations():
    form = functions.Formula("X1 + X2")
    assert form.int_to_physical(23.0, 42.0) == 65.0
    form = functions.Formula("X1 - X2")
    assert form.int_to_physical(65.0, 42.0) == 23.0
    form = functions.Formula("X1 * X2")
    assert form.int_to_physical(16.0, 16.0) == 256.0
    form = functions.Formula("X1 / X2")
    assert form.int_to_physical(256.0, 16.0) == 16.0
    #    form = functions.Formula("X1 & X2")
    #    assert form(255, 32) == 32
    #    form = functions.Formula("X1 | X2")
    #    assert form(256, 32) == 0x120
    form = functions.Formula("X1 >> X2")
    assert form.int_to_physical(64, 4) == 4
    form = functions.Formula("X1 << X2")
    assert form.int_to_physical(64, 4) == 1024
    # form = functions.Formula("~X1")
    # assert form(0x55) == 0xaa


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
    assert form.int_to_physical(0.5) == 0.479425538604203
    form = functions.Formula("asin(X1)")
    assert form.int_to_physical(0.479425538604203) == 0.5
    form = functions.Formula("cos(X1)")
    assert form.int_to_physical(0.5) == 0.8775825618903728
    form = functions.Formula("acos(X1)")
    assert form.int_to_physical(0.8775825618903728) == 0.4999999999999999
    form = functions.Formula("tan(X1)")
    assert form.int_to_physical(0.5) == 0.5463024898437905
    form = functions.Formula("atan(X1)")
    assert form.int_to_physical(0.5463024898437905) == 0.5
    form = functions.Formula("cosh(X1)")
    assert form.int_to_physical(math.log(2)) == 1.25
    form = functions.Formula("sinh(X1)")
    assert form.int_to_physical(math.log(2)) == 0.75
    form = functions.Formula("tanh(X1)")
    assert form.int_to_physical(math.log(2)) == 0.6
    form = functions.Formula("exp(X1)")
    assert form.int_to_physical(math.log(10)) == 10.000000000000002
    form = functions.Formula("log(X1)")
    assert form.int_to_physical(math.exp(10)) == 10.0
    form = functions.Formula("abs(X1)")
    assert form.int_to_physical(-23.0) == 23.0
    form = functions.Formula("sqrt(X1)")
    assert form.int_to_physical(225.0) == 15.0
    form = functions.Formula("pow(X1, X2)")
    assert form.int_to_physical(2.0, 16.0) == 65536.0
