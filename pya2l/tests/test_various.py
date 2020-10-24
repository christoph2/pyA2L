#!/usr/bin/env python
# -*- coding: latin-1 -*-

import sys

import pytest

from pya2l import DB
from pya2l.cse_units import CSE, CSE_Type, Referer

if sys.platform == "win32":
    FILE_NAME = r"f:\projects\examples\example-a2l-file"
else:
    FILE_NAME = (
        r"~/projects/examples/example-a2l-file"  # We're assuming a Unix-like OS.
    )


@pytest.mark.skip
def test_filename_with_a2l_ext():
    db = DB()
    db._set_path_components(FILE_NAME)

    assert db._pth == r"f:\projects\examples"
    assert db._base == r"example-a2l-file.a2l"
    assert db._dbfn == r"example-a2l-file.a2ldb"
    assert db._a2lfn == r"example-a2l-file.a2l"


@pytest.mark.skip
def test_filename_without_ext():
    db = DB()
    db._set_path_components(FILE_NAME)

    assert db._pth == r"f:\projects\examples"
    assert db._base == r"example-a2l-file"
    assert db._dbfn == r"example-a2l-file.a2ldb"
    assert db._a2lfn == r"example-a2l-file.a2l"


@pytest.mark.skip
def test_filename_with_a2ldb_ext():
    db = DB()
    db._set_path_components(FILE_NAME)

    assert db._pth == r"f:\projects\examples"
    assert db._base == r"example-a2l-file.a2ldb"
    assert db._dbfn == r"example-a2l-file.a2ldb"
    assert db._a2lfn == r"example-a2l-file.a2l"


@pytest.mark.skip
def test_filename_with_arbitrary_ext():
    db = DB()
    db._set_path_components(FILE_NAME)

    assert db._pth == r"f:\projects\examples"
    assert db._base == r"example-a2l-file.foobar"
    assert db._dbfn == r"example-a2l-file.a2ldb"
    assert db._a2lfn == r"example-a2l-file.foobar"


def test_cse_units():
    assert CSE.get(2) == CSE_Type(2, "100 µsec", Referer.TIME, "")
