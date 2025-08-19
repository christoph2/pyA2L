# Modules / API overview

This repository ships source code with rich docstrings. For a full API reference you can generate documentation using Sphinx. Below is a quick orientation to key modules:

- `pya2l.api.inspect`: High-level inspection helpers for ASAP2 entities.
- `pya2l.api.create`: Creator API to programmatically build/augment entities.
- `pya2l.model`: SQLAlchemy ORM types describing the A2L database schema.
- `pya2l.aml.ifdata_parser`: Parser for IF_DATA blocks.
- `pya2l.scripts`: CLI utilities like `a2ldb-imex`.

For usage examples, see:
- `pya2l/examples`
- The README sections “Getting Started” and “Create API and coverage parity”.

> Note: The old Sphinx `automodule` index (pya2l.rst) relied on Sphinx to render API details. GitHub markdown does not render these; prefer in-editor docstrings or build Sphinx docs locally if needed.
