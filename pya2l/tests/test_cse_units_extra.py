from pya2l.cse_units import CSE, Referer

def test_cse_units_existence():
    assert 0 in CSE
    assert 6 in CSE
    assert 100 in CSE
    assert 1000 in CSE

def test_cse_values():
    unit_0 = CSE[0]
    assert unit_0.code == 0
    assert unit_0.unit == "1 µsec"
    assert unit_0.referred_to == Referer.TIME

    unit_100 = CSE[100]
    assert unit_100.code == 100
    assert unit_100.unit == "Angular degrees"
    assert unit_100.referred_to == Referer.ANGLE

def test_referer_enum():
    assert Referer.TIME == 1
    assert Referer.ANGLE == 2
