from pya2l.api.inspect import CachedBase


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
