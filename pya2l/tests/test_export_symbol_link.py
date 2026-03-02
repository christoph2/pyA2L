import io
import logging

import pya2l.imex.a2l_exporter as a2l_exporter
import pya2l.model as model
from pya2l.model import A2LDatabase


def test_export_symbol_link_missing_offset(tmp_path, caplog):
    db_path = tmp_path / "sym.a2ldb"
    builder = A2LDatabase(str(db_path))
    try:
        proj = model.Project(name="P", longIdentifier="Project")
        mod = model.Module(name="M", longIdentifier="Module")
        meas = model.Measurement(
            name="M1",
            longIdentifier="Measurement",
            datatype="UBYTE",
            conversion="CM",
            resolution=1,
            accuracy=0,
            lowerLimit=0,
            upperLimit=1,
        )
        meas.symbol_link = model.SymbolLink(symbolName="SYM", offset=None)
        mod.measurement.append(meas)
        proj.module.append(mod)
        builder.session.add(proj)
        builder.session.commit()
    finally:
        builder.close()

    caplog.set_level(logging.WARNING, logger=a2l_exporter.__name__)
    out = io.StringIO()
    db = a2l_exporter.open_database(db_path)
    try:
        a2l_exporter.export_db(db, out)
    finally:
        db.close()
    exported = out.getvalue()

    assert "SYMBOL_LINK" in exported
    assert '"SYM"' in exported
    assert "0  /* offset */" in exported
    assert any("missing offset" in rec.message for rec in caplog.records)
