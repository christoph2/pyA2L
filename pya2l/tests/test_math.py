
import pytest

#from pya2l.math import math_fast as mf
from pya2l.math import math_slow as ms

Xs = [0.0, 200.0, 400.0, 1000.0, 5700.0]
Ys = [2.0,  2.7, 3.0,  4.2, 4.9]

Xins = [-1.0, 0.0, 850.0, 5700.0, 8000.0]
Rs = [2.0, 2.0, 3.9000000000000004, 4.9, 4.9]


interp_slow = ms.Interpolate1D
#interp_fast = mf.Interpolate1D

@pytest.mark.parametrize("interp_klass", [interp_slow, ]) # interp_fast
@pytest.mark.parametrize("x, expected", zip(Xins, Rs))
def test_interpolate1D_saturate(interp_klass, x, expected):
    interp = interp_klass(xs = Xs, ys = Ys, saturate = True)
    assert interp(x) == expected


XsOutOfBounds = [-1.0, 8000.0]
expected = [None, None]


@pytest.mark.parametrize("interp_klass", [interp_slow, ])    # interp_fast
@pytest.mark.parametrize("x, expected", zip(XsOutOfBounds, expected))
def test_interpolate1D_out_of_bounds(interp_klass, x, expected):
    interp = interp_klass(xs = Xs, ys = Ys, saturate = False)
    with pytest.raises(ValueError):
        interp(x) == expected
