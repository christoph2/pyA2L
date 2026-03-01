import sqlite3
import threading
from pathlib import Path

import pya2l.imex.a2l_exporter as a2l_exporter
import pya2l.model as model
from pya2l.model import A2LDatabase


def test_export_allows_concurrent_writer(tmp_path):
    db_path = tmp_path / "example.a2ldb"
    builder = A2LDatabase(str(db_path))
    try:
        proj = model.Project(name="P", longIdentifier="Project")
        mod = model.Module(name="MOD", longIdentifier="Module")
        proj.module.append(mod)
        builder.session.add(proj)
        builder.session.commit()
    finally:
        builder.close()

    out_path = tmp_path / "out.a2l"
    started = threading.Event()
    writer_error: list[Exception] = []

    def run_export():
        db = a2l_exporter.open_database(db_path)
        try:
            started.set()
            a2l_exporter.export_db(db, out_path)
        finally:
            db.close()

    export_thread = threading.Thread(target=run_export)
    export_thread.start()
    assert started.wait(timeout=2)

    def writer():
        conn = sqlite3.connect(db_path, timeout=5)
        try:
            conn.execute("PRAGMA busy_timeout=5000")
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("BEGIN IMMEDIATE")
            conn.execute("INSERT INTO system_constant (name, value) VALUES ('LOCK_TEST', '1')")
            conn.commit()
        except Exception as exc:  # noqa: BLE001
            writer_error.append(exc)
        finally:
            conn.close()

    writer()
    export_thread.join(timeout=10)
    assert not export_thread.is_alive(), "export did not finish"
    if writer_error:
        raise writer_error[0]
    assert out_path.exists()
