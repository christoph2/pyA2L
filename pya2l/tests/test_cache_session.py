from pya2l.api.inspect import CachedBase


class _DummyCached(CachedBase):
    def __init__(self, session, name, module_name=None):
        self.session = session
        self.name = name
        self.module_name = module_name


def test_cached_base_is_session_scoped():
    CachedBase._cache.clear()
    CachedBase._strong_ref.clear()

    s1 = object()
    s2 = object()

    a = _DummyCached.get(s1, "foo")
    b = _DummyCached.get(s1, "foo")
    c = _DummyCached.get(s2, "foo")

    assert a is b
    assert a is not c
