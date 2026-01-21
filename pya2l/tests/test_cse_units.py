from pya2l.cse_units import CSE, Referer

def test_cse_units():
    assert 0 in CSE
    assert CSE[0].unit == "1 µsec"
    assert CSE[0].referred_to == Referer.TIME
    
    assert 100 in CSE
    assert CSE[100].unit == "Angular degrees"
    assert CSE[100].referred_to == Referer.ANGLE
    
    assert 1000 in CSE
    assert CSE[1000].unit == "Non deterministic"
    assert CSE[1000].referred_to == Referer.NONE
