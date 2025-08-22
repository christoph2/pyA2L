# Installation

- Pythons: Python ≥ 3.10 (see pyproject classifiers for exact versions)
- Platforms: No platform-specific restrictions for installing the Python package; building from source may require additional tools (see Building).
- Documentation: Latest docs are in this repository under `docs/` as Markdown.

## Prerequisites

If you plan to build from source, ensure you have a C/C++ toolchain and CMake installed (see Building). Java/ANTLR are not required for normal builds.

## Install from PyPI

```bash
pip install pya2ldb
```

Important: The package name is `pya2ldb` (not `pya2l`).

## Install from source (editable)

```bash
git clone https://github.com/christoph2/pyA2L.git
cd pyA2L
pip install -v -e .
```
