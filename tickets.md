# Tickets / Branch proposals

1) Title: Fix session-bound cache invalidation
Branch: fix/cache-session-reset
Description: Cache an SQLAlchemy-Session binden oder beim Import/Open leeren, damit nach erneutem Import korrekte Werte geliefert werden (Issues #93, #53).
Acceptance: Zwei aufeinanderfolgende Imports liefern die Werte des zweiten Files; kein Leck zwischen Sessions.
Tests: Neuer pytest-Fall mit zwei Imports (in_memory/off) prüft Measurements/Addresses frisch.

2) Title: Export roundtrip robustness (A2L↔A2LDB)
Branch: fix/export-roundtrip
Description: Exportierte A2L erneut parsebar machen; IF_DATA/Names/encoding korrekt, Template-Leerzeilen minimieren (#88, #85, #65, #64, #60).
Acceptance: import→export→reimport für ASAP2_Demo + IF_DATA-Variante ohne Parser-Fehler; kein Name/IF_DATA-Mangel; Export ohne überflüssige Leerzeilen-Blöcke.
Tests: Roundtrip-Integrationstest; Snapshots/regex auf exportiertes A2L (keine doppelten blank lines).

3) Title: Parser edge tokens (brackets/comments/CUSTOMER_NO)
Branch: fix/parser-edge-tokens
Description: Parser/Preprocessor robust gegen eckige Klammern in Namen, multiline /* */ in COMPU_METHOD, CUSTOMER_NO/Token-Mismatches (#50, #48, #39, #66).
Acceptance: Problemfälle werden fehlerfrei geparst; bestehende Grammatik nicht regressiv.
Tests: Fixtures mit den genannten Snippets; pytest erwartet keine Lexer/Parser errors.

4) Title: CompuMethod query completeness
Branch: fix/compumethod-query
Description: session.query(CompuMethod).all() liefert vollständige Menge, kein Filter/Bug (#72).
Acceptance: Repro-Skript aus Issue liefert vollständige Liste.
Tests: Unit/fixture test prüft Anzahl/Names gegen erwartete Testdaten.

5) Title: XCP_ON_CAN parsing support
Branch: feat/xcp-on-can
Description: XCP_ON_CAN Abschnitt parsen, modellieren und persistieren (IDs, baudrate, DAQ_LIST_CAN_ID) (#26).
Acceptance: Beispielstruktur wird ohne Fehler in DB abgebildet; API zugreifbar.
Tests: Parser/DB test mit Minimal-XCP_ON_CAN-Fixture, asserts auf gespeicherte Felder.

6) Title: stderr logging and quiet output
Branch: fix/stderr-logging
Description: Native/C++ Fehler auf stderr statt stdout; unnötige stdout-Warnungen/Noise reduzieren, optional Quiet (Progressbar) beachten (#59, optional #58).
Acceptance: Fehler-Paths gehen auf stderr; Quiet/CRITICAL Loglevel unterdrückt Progressbar.
Tests: Small C++/Python harness prüft Streams; python -m pytest log-capture.

7) Title: Import performance in long test batches
Branch: perf/import-batch
Description: Profiling/Fix für langsame import_a2l nach vielen Läufen (#51); ggf. Cache flush, resource cleanup.
Acceptance: Messen vor/nach: deutlich reduzierte Import-Zeit im Wiederholungsfall.
Tests: Benchmark-like pytest (marked) running multiple imports; asserts on max time or trend.

8) Title: Docs: usage, excel export, generator, encoding
Branch: docs/usage-excel-generator
Description: Kurz-Howtos: Installation/Quickstart, A2L→Excel Beispiel, Generator/ARXML Guidance, Encoding-Override Hinweis; setup.py Stolpersteine (#6, #5, #11, #44, #52, #47, #32, #9).
Acceptance: Neue/erweiterte Docs-Seiten mit Beispielen und Klarstellungen; Links aus Issues abgedeckt.
Tests: n/a (doc build optional), aber Sphinx build darf nicht brechen.
