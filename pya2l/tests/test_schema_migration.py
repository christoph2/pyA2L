"""Smoke tests for schema migration in pya2l.model.

These tests verify the migration chain in A2LDatabase:
 - a UserWarning is issued when no migration path is registered
 - a registered migration step is executed and the version is bumped
"""

import warnings

import pytest
import sqlalchemy
from sqlalchemy.orm import sessionmaker

import pya2l.model as model
from pya2l.model import (
    CURRENT_SCHEMA_VERSION,
    A2LDatabase,
    MetaData,
    _MIGRATIONS,
    _register_migration,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_db_at_version(path, version: int) -> None:
    """Create a minimal .a2ldb file at the given schema version."""
    engine = sqlalchemy.create_engine(f"sqlite:///{path}")
    model.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(MetaData(schema_version=version))
    session.commit()
    session.close()
    engine.dispose()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


def test_migration_warning_when_no_path_registered(tmp_path):
    """Opening a DB whose version has no registered migration path emits UserWarning."""
    old_version = CURRENT_SCHEMA_VERSION - 1
    db_path = tmp_path / "test_no_migration.a2ldb"
    _make_db_at_version(db_path, old_version)

    # Ensure no migration is registered for this step
    _MIGRATIONS.pop((old_version, CURRENT_SCHEMA_VERSION), None)
    _MIGRATIONS.pop((old_version, old_version + 1), None)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        db = A2LDatabase(str(db_path))
        db.close()

    user_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
    assert user_warnings, "Expected a UserWarning about missing migration path"
    assert "migration" in str(user_warnings[0].message).lower() or "schema" in str(user_warnings[0].message).lower()


def test_migration_succeeds_when_step_registered(tmp_path):
    """A registered one-step migration upgrades the schema version and commits it."""
    old_version = CURRENT_SCHEMA_VERSION - 1
    db_path = tmp_path / "test_migration.a2ldb"
    _make_db_at_version(db_path, old_version)

    side_effects = []

    @_register_migration(old_version, CURRENT_SCHEMA_VERSION)
    def _test_step(session):
        side_effects.append("ran")

    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            db = A2LDatabase(str(db_path))
            # Verify the migration callable was invoked
            assert side_effects == ["ran"], "Migration step should have been called"
            # Verify no compatibility warning was issued
            compat_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
            assert not compat_warnings, f"Unexpected warning: {[str(w.message) for w in compat_warnings]}"
            # Verify schema version was persisted
            updated = db.session.query(MetaData).first()
            assert updated is not None
            assert updated.schema_version == CURRENT_SCHEMA_VERSION, (
                f"schema_version should be {CURRENT_SCHEMA_VERSION}, got {updated.schema_version}"
            )
            db.close()
    finally:
        _MIGRATIONS.pop((old_version, CURRENT_SCHEMA_VERSION), None)


def test_migration_chain_two_steps(tmp_path):
    """A two-step migration chain walks both steps in order."""
    start_version = CURRENT_SCHEMA_VERSION - 2
    db_path = tmp_path / "test_chain.a2ldb"
    _make_db_at_version(db_path, start_version)

    order = []

    @_register_migration(start_version, start_version + 1)
    def _step_a(session):
        order.append("A")

    @_register_migration(start_version + 1, CURRENT_SCHEMA_VERSION)
    def _step_b(session):
        order.append("B")

    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            db = A2LDatabase(str(db_path))
            assert order == ["A", "B"], f"Expected ['A','B'], got {order}"
            compat_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
            assert not compat_warnings
            updated = db.session.query(MetaData).first()
            assert updated.schema_version == CURRENT_SCHEMA_VERSION
            db.close()
    finally:
        _MIGRATIONS.pop((start_version, start_version + 1), None)
        _MIGRATIONS.pop((start_version + 1, CURRENT_SCHEMA_VERSION), None)


def test_fresh_database_gets_current_version(tmp_path):
    """A freshly created database receives CURRENT_SCHEMA_VERSION without migration."""
    db_path = tmp_path / "fresh.a2ldb"
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        db = A2LDatabase(str(db_path))
        meta = db.session.query(MetaData).first()
        assert meta is not None
        assert meta.schema_version == CURRENT_SCHEMA_VERSION
        compat_warnings = [w for w in caught if issubclass(w.category, UserWarning)]
        assert not compat_warnings
        db.close()
