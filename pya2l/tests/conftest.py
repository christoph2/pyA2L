"""
Shared pytest configuration for pya2l tests.

The autouse fixture `_gc_after_test` forces a full garbage-collection cycle
after every test.  SQLAlchemy sessions (and the underlying SQLite connections)
contain circular references that CPython's reference-counter alone cannot
immediately free.  Without explicit gc.collect() calls the in-memory databases
from earlier tests stay alive and consume heap space, which can eventually
cause MemoryError (std::bad_alloc) inside the native C++ parser extension on
memory-constrained CI runners such as the GitHub Actions Windows agent.
"""

import gc

import pytest


@pytest.fixture(autouse=True)
def _gc_after_test():
    """Force garbage collection after every test to release SQLAlchemy cycles."""
    yield
    gc.collect()
