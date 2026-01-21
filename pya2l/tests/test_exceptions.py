import pytest
from pya2l.exceptions import MathError, StructuralError, RangeError

def test_math_error():
    with pytest.raises(MathError):
        raise MathError("Math error")

def test_structural_error():
    with pytest.raises(StructuralError):
        raise StructuralError("Structural error")

def test_range_error():
    with pytest.raises(RangeError):
        raise RangeError("Range error")
