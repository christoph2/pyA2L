
import pytest

from pya2l import DB



def test_filename_with_a2l_ext():
    db = DB()
    db._set_path_components(r"f:\projects\examples\example-a2l-file.a2l")

    assert db._pth == r'f:\projects\examples'
    assert db._base == r'example-a2l-file.a2l'
    assert db._dbfn == r'example-a2l-file.a2ldb'
    assert db._a2lfn == r'example-a2l-file.a2l'

def test_filename_without_ext():
    db = DB()
    db._set_path_components(r"f:\projects\examples\example-a2l-file")

    assert db._pth == r'f:\projects\examples'
    assert db._base == r'example-a2l-file'
    assert db._dbfn == r'example-a2l-file.a2ldb'
    assert db._a2lfn == r'example-a2l-file.a2l'

def test_filename_with_a2ldb_ext():
    db = DB()
    db._set_path_components(r"f:\projects\examples\example-a2l-file.a2ldb")

    assert db._pth == r'f:\projects\examples'
    assert db._base == r'example-a2l-file.a2ldb'
    assert db._dbfn == r'example-a2l-file.a2ldb'
    assert db._a2lfn == r'example-a2l-file.a2l'

def test_filename_with_arbitrary_ext():
    db = DB()
    db._set_path_components(r"f:\projects\examples\example-a2l-file.foobar")

    assert db._pth == r'f:\projects\examples'
    assert db._base == r'example-a2l-file.foobar'
    assert db._dbfn == r'example-a2l-file.a2ldb'
    assert db._a2lfn == r'example-a2l-file.foobar'
