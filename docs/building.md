# Building pyA2L

pyA2L uses code generated from ANTLR grammars for much of the heavy lifting when parsing ASAP2 documents. This code is not version controlled, but instead generated during build time. That means that if you just cloned this repository, it is not yet ready to use. You must first build it, which requires a working Java installation to run ANTLR.

## Prerequisites

1. Install Java
2. Install ANTLR: https://github.com/antlr/antlr4/blob/master/doc/getting-started.md

## Code generation

To generate code, call setup.py with the `antlr` command:

```bash
python setup.py antlr
```

However, it is generally not necessary to run this command directly.

## Development environment

If you want to contribute to the pyA2L project, running:

```bash
python setup.py develop
```

will also auto-generate code.

## Binary distribution

The same is true when creating a binary for distribution with:

```bash
python setup.py bdist
```

or

```bash
python setup.py bdist_wheel
```
