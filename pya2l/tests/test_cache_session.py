import tempfile
from pathlib import Path

from pya2l import DB
from pya2l.api.inspect import CachedBase, Project


class _DummySession:
    def __init__(self):
        self.info = {}


class _DummyCached(CachedBase):
    def __init__(self, session, name, module_name=None):
        self.session = session
        self.name = name
        self.module_name = module_name


def test_cached_base_is_session_scoped():
    CachedBase.clear()

    s1 = _DummySession()
    s2 = _DummySession()

    a = _DummyCached.get(s1, "foo")
    b = _DummyCached.get(s1, "foo")
    c = _DummyCached.get(s2, "foo")

    assert a is b
    assert a is not c


def test_cached_base_reopen_uses_fresh_session_bucket():
    CachedBase.clear()

    first_session = _DummySession()
    a = _DummyCached.get(first_session, "foo")
    CachedBase.clear_session(first_session)

    second_session = _DummySession()
    b = _DummyCached.get(second_session, "foo")

    assert a is not b


def test_project_cache_isolation_between_different_a2l_files():
    """Regression test for issue #93: Cache should not leak between different A2L imports.
    
    This test verifies that when importing two different A2L files sequentially,
    the Project cache does not return stale data from the first file when querying
    the second file.
    """
    # Define two minimal A2L files with same measurement name but different addresses
    a2l_old = """ASAP2_VERSION 1 71
/begin PROJECT TestProject_Old ""
  /begin MODULE TestModule_Old ""
    /begin MEASUREMENT Speed_Sensor
      "Vehicle speed sensor"
      UWORD
      NO_COMPU_METHOD
      0 0 0 100
      ECU_ADDRESS 0x1000
    /end MEASUREMENT
  /end MODULE
/end PROJECT
"""
    
    a2l_new = """ASAP2_VERSION 1 71
/begin PROJECT TestProject_New ""
  /begin MODULE TestModule_New ""
    /begin MEASUREMENT Speed_Sensor
      "Vehicle speed sensor (new address)"
      UWORD
      NO_COMPU_METHOD
      0 0 0 100
      ECU_ADDRESS 0x2000
    /end MEASUREMENT
  /end MODULE
/end PROJECT
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        old_file = tmpdir / "old.a2l"
        new_file = tmpdir / "new.a2l"
        
        old_file.write_text(a2l_old, encoding="latin-1")
        new_file.write_text(a2l_new, encoding="latin-1")
        
        # Import first A2L file
        db = DB()
        session = db.import_a2l(str(old_file), in_memory=True)
        project = Project(session)
        module_old = project.module[0]
        
        # Query measurement from first file
        meas_old = next(module_old.measurement.query(lambda row: row.name == "Speed_Sensor"), None)
        assert meas_old is not None
        address_old = meas_old.ecuAddress
        assert address_old == 0x1000, f"Expected 0x1000, got {address_old:#x}"
        
        # Close first session
        session.close()
        
        # Import second A2L file (different content, same measurement name)
        session = db.import_a2l(str(new_file), in_memory=True)
        project = Project(session)
        module_new = project.module[0]
        
        # Query measurement from second file
        # This MUST return data from the second file, not from cache of first file
        meas_new = next(module_new.measurement.query(lambda row: row.name == "Speed_Sensor"), None)
        assert meas_new is not None
        address_new = meas_new.ecuAddress
        
        # CRITICAL: Address must be from second file (0x2000), not first file (0x1000)
        assert address_new == 0x2000, (
            f"Cache isolation failed! Got address {address_new:#x} from first file, "
            f"expected {0x2000:#x} from second file. Issue #93 regression."
        )
        
        # Also verify the module names are different to ensure we're really in different sessions
        assert module_old.name == "TestModule_Old"
        assert module_new.name == "TestModule_New"
        
        session.close()
