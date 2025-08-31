Building pyA2L (from source)
============================

pyA2L ships binary wheels for common platforms on PyPI as ``pya2ldb``.
If a wheel is not available for your platform, you can build from
source.

Prerequisites
-------------

- Python 3.10+
- A C/C++ toolchain (e.g., MSVC Build Tools on Windows, Xcode Command
  Line Tools on macOS, or GCC/Clang on Linux)
- CMake 3.12+
- pip >= 21.3

Note: The project uses pybind11 and CMake under the hood. ANTLR and Java
are not required for normal builds.

One‑liner build and install (recommended)
-----------------------------------------

Using pip (PEP 517):

.. code:: bash

   pip install -v .

This will compile the native extensions and install ``pya2ldb`` into
your environment.

Development install
-------------------

If you plan to work on the codebase, a development install keeps sources
editable:

.. code:: bash

   pip install -v -e .

This uses the build backend defined in ``pyproject.toml`` and will
recompile extensions as needed.

Building distribution artifacts
-------------------------------

Build a source distribution and wheel into the ``dist/`` directory:

.. code:: bash

   python -m build

You can then upload with ``twine``.

Building the documentation
--------------------------

The user guides live in ``docs/`` (mostly Markdown). The Sphinx entry
point is ``docs/index.rst``, which links to those pages for convenient
browsing on GitHub.

To build the Sphinx site locally:

.. code:: bash

   python -m pip install -r docs/requirements.txt sphinx
   sphinx-build -b html docs docs/_build/html

Open ``docs/_build/html/index.html`` in your browser.
