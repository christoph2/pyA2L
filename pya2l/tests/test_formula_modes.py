import math

import pytest

from pya2l.functions import Formula


def _approx(a, b, eps=1e-12):
    if isinstance(a, (list, tuple)):
        return all(_approx(x, y, eps) for x, y in zip(a, b))
    return abs(a - b) <= eps


@pytest.mark.skip
def test_current_mode_logical_tokens_and_bitwise():
    # current: &&, ||, ! are logical
    f = Formula("(X1 > 0) && (X2 < 0)")
    assert f.int_to_physical(1, -1) is True
    assert f.int_to_physical(0, -1) is False

    # &, |, ~ are bitwise
    f = Formula("(X1 & 0xF0) | (X2 & 0x0F)")
    assert f.int_to_physical(0xAB, 0xCD) == ((0xAB & 0xF0) | (0xCD & 0x0F))

    f = Formula("~X1")
    assert f.int_to_physical(0x00) == ~0x00

    # ^ is bitwise exclusive OR
    f = Formula("X1 ^ X2")
    assert f.int_to_physical(0x55AA, 0x2222) == (0x55AA ^ 0x2222)


def test_current_mode_disallows_XOR_keyword():
    with pytest.raises(ValueError):
        Formula("X1 XOR X2")


def test_current_mode_function_names_short_and_long():
    # accept short names and long numpy-style names equally
    f1 = Formula("asin(X1)")
    f2 = Formula("arcsin(X1)")
    res1 = f1.int_to_physical(0.5)
    res2 = f2.int_to_physical(0.5)
    assert _approx(res1, res2)

    f1 = Formula("acos(X1)")
    f2 = Formula("arccos(X1)")
    assert _approx(f1.int_to_physical(0.5), f2.int_to_physical(0.5))

    f1 = Formula("atan(X1)")
    f2 = Formula("arctan(X1)")
    assert _approx(f1.int_to_physical(0.5), f2.int_to_physical(0.5))


def test_legacy_mode_logical_and_power_and_xor():
    # legacy: &, |, ~ are logical
    f = Formula("(X1 > 0) & (X2 < 0)", legacy=True)
    assert f.int_to_physical(1, -1) is True
    assert f.int_to_physical(0, -1) is False

    f = Formula("(X1 > 0) | (X2 > 0)", legacy=True)
    assert f.int_to_physical(1, 0) is True
    assert f.int_to_physical(0, 0) is False

    f = Formula("~(X1 > 0)", legacy=True)
    assert f.int_to_physical(1) is False

    # legacy: ^ is power
    f = Formula("X1 ^ X2", legacy=True)
    assert _approx(f.int_to_physical(2.0, 4.0), 16.0)

    # legacy XOR keyword is exclusive OR
    f = Formula("X1 XOR X2", legacy=True)
    assert f.int_to_physical(1, 0) == (1 ^ 0)


def test_legacy_mode_disallows_current_tokens():
    for expr in ("X1 && X2", "X1 || X2", "!X1"):
        with pytest.raises(ValueError):
            Formula(expr, legacy=True)


def test_legacy_mode_function_name_aliases():
    # arcos -> acos (eval) / arccos (numexpr); arcsin/arctan should be accepted
    f = Formula("arcos(X1)", legacy=True)
    val = f.int_to_physical(0.5)
    assert _approx(val, math.acos(0.5))

    f = Formula("arcsin(X1)", legacy=True)
    assert _approx(f.int_to_physical(0.5), math.asin(0.5))

    f = Formula("arctan(X1)", legacy=True)
    assert _approx(f.int_to_physical(0.5), math.atan(0.5))


def test_pow_and_sysc_expansion_current_and_legacy():
    sysc = {"A": 2, "B": 5}
    f = Formula("pow(X1, X2) + sysc(A)", system_constants=sysc)
    assert f.int_to_physical(3, 4) == (3**4) + 2

    f = Formula("pow(X1, X2) + sysc(B)", legacy=True, system_constants=sysc)
    assert f.int_to_physical(2, 3) == (2**3) + 5


def test_missing_inverse_raises():
    f = Formula("X1 + 1")
    with pytest.raises(NotImplementedError):
        f.physical_to_int(1)


def test_inverse_formula_works_current_and_legacy():
    # linear invertible example: y = 2*x + 3; x = (y - 3)/2
    f = Formula("2*X + 3", inverse_formula="(X - 3)/2")
    assert f.int_to_physical(10) == 23
    assert f.physical_to_int(23) == 10

    f = Formula(
        "2*X + sysc(A)",
        inverse_formula="(X - sysc(A))/2",
        system_constants={"A": 7},
    )
    assert f.int_to_physical(10) == 27
    assert f.physical_to_int(27) == 10

    # legacy variant uses same formulas but with legacy True
    f = Formula("2*X + 3", inverse_formula="(X - 3)/2", legacy=True)
    assert f.int_to_physical(10) == 23
    assert f.physical_to_int(23) == 10


def test_x_alias_and_spacing_pow_sysc():
    # X aliases X1
    f = Formula("pow( X , 2 ) + sysc( A )", system_constants={"A": 4})
    assert f.int_to_physical(3) == 9 + 4

    # legacy with carets-as-power
    f = Formula(" X ^ 3  + sysc( A )", legacy=True, system_constants={"A": 1})
    assert f.int_to_physical(2) == 8 + 1
