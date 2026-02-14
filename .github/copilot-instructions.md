# Copilot instructions for pyA2L

## Project overview
- Purpose: Parse ASAP2/A2L files, persist them as SQLite `.a2ldb` databases, inspect/validate them with SQLAlchemy models, and optionally export back to A2L.
- Core flow: `pya2l.import_a2l`/`open_existing` (A2LParser + native extensions) → `pya2l.model` SessionProxy (SQLite-backed) → API layers (`pya2l.api.inspect` for read-only helpers, `pya2l.api.create` for mutations, `pya2l.api.validate.Validator` for diagnostics) → optional CLI `a2ldb-imex`.
- Native pieces: pybind11/CMake-built extensions (`a2lparser_ext`, `amlparser_ext`, `preprocessor`) plus ANTLR-generated grammar artifacts (`pya2l/a2lLexer.py`, `amlLexer.py`, parsers) — treat generated files as read-only; rebuild via ANTLR/CMake if changes are needed.
- Package name on PyPI is **`pya2ldb`**; import namespace is `pya2l`. Default import encoding is latin-1; `.a2ldb` extension is implied by helpers.

## Build / install
- Dev install (PEP 517 backend, builds native extensions): `pip install -v -e .` (requires Python 3.10+, CMake ≥ 3.12, C/C++ toolchain, pybind11).
- Poetry workflow (matches CI): `poetry install --with dev` (use `poetry config virtualenvs.create false` to install into current env if desired).
- Source/wheel artifacts: `python -m build`.
- Docs: `python -m pip install -r docs/requirements.txt sphinx` then `sphinx-build -b html docs docs/_build/html` (entrypoint `docs/index.rst` / `docs/README.rst`).

## Test commands
- Full suite: `poetry run pytest` (tests live in `pya2l/tests`, pytest settings in `pyproject.toml`).
- Single test/module example: `python -m pytest pya2l/tests/test_a2l_parser.py -k basic` (add `-q` for quiet).

## Linting/format/security
- Format/check: `poetry run black --check .` (line length 132), `poetry run isort --check-only .`.
- Lint: `poetry run ruff check .` (target py312), `poetry run flake8`.
- Security: `poetry run bandit -c bandit.yml -r pya2l`.
- Pre-commit (recommended locally): `poetry run pre-commit run --all-files`.
- Generated parser files and build outputs are excluded from lint/format (see tool configs in `pyproject.toml`); avoid manual edits there.

## Usage hints and conventions
- Prefer the high-level APIs instead of direct SQLAlchemy model manipulation: `pya2l.import_a2l`/`open_existing` for session setup, `pya2l.api.inspect` for read-only access, `pya2l.api.create` for mutations, and `pya2l.api.validate.Validator` for rule checks (yields structured `Message` tuples).
- CLI shortcuts: `poetry run a2ldb-imex -V` for version, `... -i file.a2l` to import (creates `.a2ldb` in place or with `-L` in CWD), `... -e file.a2ldb -o out.a2l` to export.
- Test fixtures include sample A2L files under `pya2l/tests`; reuse them for regression cases.
- When handling IF_DATA/AML, use the existing parsers (`pya2l.aml`, `if_data_parser`) and session `setup_ifdata_parser` rather than rolling bespoke parsing.
