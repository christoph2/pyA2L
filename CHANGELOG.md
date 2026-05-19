# Changelog

All notable changes to **pya2ldb** are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

---

## [Unreleased]

### Added
- `import_a2l()`, `open_existing()`, `open_create()`, `export_a2l()` — module-level
  entry points (preferred over the deprecated `DB` class wrapper).
- `force_overwrite: bool = False` parameter on `import_a2l()` and `A2LParser.parse()`.
  When `True` the existing `.a2ldb` is silently replaced; when `False` and the file
  already exists the CLI prompts for confirmation instead of raising `OSError`.
- `-f` / `--force-overwrite` CLI flag for `a2ldb-imex -i`.
- `-q` / `--quiet` CLI flag — sets log level to CRITICAL and disables the progress
  bar; useful for scripting.
- `pya2l.api.validate.Validator` — five new checks:
  - Namespace uniqueness (duplicate names within a module, same name in multiple
    namespaces).
  - Cross-reference validation: MEASUREMENT / CHARACTERISTIC / AXIS_PTS →
    COMPU_METHOD; CHARACTERISTIC / AXIS_PTS → RECORD_LAYOUT.
  - C-identifier length (ISO C90 limit of 32 characters).
- Two new `Diagnostics` enum values: `MISSING_COMPU_METHOD`, `MISSING_RECORD_LAYOUT`.
- `__all__` defined in `pya2l/__init__.py`, `pya2l/exceptions.py`,
  `pya2l/api/inspect.py`, and `pya2l/api/create.py`.
- `pya2l.model._register_migration` / `_migrate_schema` — schema migration chain
  with full docstring and usage example.
- `pya2l/tests/test_validator.py` — 13 tests covering all new `Validator` checks.
- `pya2l/tests/test_schema_migration.py` — 4 smoke tests for the migration chain.
- `.github/dependabot.yml` — weekly Dependabot updates for GitHub Actions and pip.
- `.github/release.yml` — automatic release-note categories (features, bugs,
  maintenance, docs, CI).

### Changed
- **Logger architecture**: `Logger.__init__` now always keeps the named logger
  `pya2l.<name>`; Rich is used only as a `logging.Handler`, not as the logger
  itself. Application-level logging config (`logging.getLogger("pya2l")`) is now
  respected.
- `Logger.error(exc_info=True)` now logs the traceback at ERROR level (was DEBUG).
- `pya2l/utils.py`: `print()` calls replaced by `logging.getLogger("pya2l.utils")`.
- `pya2l/api/inspect.py`: remaining `print()` calls replaced by `_logger`.
- `pya2l/functions.py`: `print()` → `_logger.warning()`; specific exception types
  instead of bare `except Exception`.
- `pya2l/imex/json_exporter.py`, `imex/a2l_exporter.py`: float-conversion catch
  narrowed to `(TypeError, ValueError)`.
- `pya2l/aml/classes.py`: `_try()` catch narrowed to `AttributeError`.
- `pya2l/model/__init__.py`: metadata query catch narrowed to
  `sqlalchemy.exc.SQLAlchemyError`.
- `a2ldb-imex --version` exit code fixed from `1` to `0`.
- `a2ldb-imex` import errors now show a Rich Panel instead of a raw Python
  traceback.
- `pythonapp.yml` (CI): `upload_pypi` now depends on a `run_tests` gate job —
  wheels can no longer be published with failing tests.
- `pythonapp.yml` (CI): `build_sdist` now runs `twine check dist/*`.
- `pyproject.toml` mypy config: `no_implicit_optional = true`,
  `warn_return_any = true`, `[[tool.mypy.overrides]]` for generated files.

### Removed / Cleaned up
- Deleted `pya2l/preprocessor_orig.py` (replaced by the C++ extension).
- Deleted `pya2l/trie_stuff.py` and `pya2l/trie_stuff.cpp` (experimental,
  never integrated).
- Removed stale ANTLR Python-file references from `MANIFEST.in`.
- Removed unused `from pya2l import DB` from `pya2l/api/validate.py`.
- Removed ~60 lines of dead commented-out code from `pya2l/api/validate.py`.

### Deprecated
- `pya2l.DB` — emits `DeprecationWarning` since this release. Use the
  module-level functions `import_a2l()`, `open_existing()`, `open_create()`,
  and `export_a2l()` instead. `DB` will be removed in a future major release.
  See the *Migration guide* in `docs/getting_started.rst`.

### Fixed
- `pya2l/cgen/templates/a2l.tmpl`: fixed `COMPU_TAB` / `COMPU_VTAB` /
  `COMPU_VTAB_RANGE` pair export loop (was broken, causing export round-trip
  failures).
- `DEFAULT_VALUE_NUMERIC` export format corrected to a single-line keyword.

---

## Older releases

Release notes for versions before this changelog was introduced are available
on the [GitHub Releases page](https://github.com/christoph2/pyA2L/releases).
