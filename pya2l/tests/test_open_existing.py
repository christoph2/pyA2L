import gc

import pytest

import pya2l
import pya2l.model as model


def test_open_existing_keeps_database_owner_alive(tmp_path, monkeypatch):
    monkeypatch.setattr(model.SessionProxy, "setup_ifdata_parser", lambda self, loglevel="INFO": None)

    db_path = tmp_path / "owned.a2ldb"
    db = model.A2LDatabase(str(db_path))
    db.close()

    session = pya2l.open_existing(str(db_path))
    try:
        owner = getattr(session, "_a2l_db_owner", None)
        assert owner is not None

        gc.collect()

        assert session.query(model.MetaData).first() is not None
    finally:
        session.close()
        session._a2l_db_owner.close()


@pytest.mark.skip
def test_open_existing_rejects_empty_database_without_metadata(tmp_path):
    db_path = tmp_path / "empty.a2ldb"
    db_path.touch()

    with pytest.raises(pya2l.InvalidA2LDatabase, match="no meta-data"):
        pya2l.open_existing(str(db_path))
