#!/usr/bin/env python

from pya2l.cse_units import CSE, CSE_Type, Referer


def test_cse_units():
    assert CSE.get(2) == CSE_Type(2, "100 µsec", Referer.TIME, "")
