Configuration
=============

pyA2L works out-of-the-box with sensible defaults.  This section
describes all available knobs for tuning import, export, and runtime
behaviour.

Import options
--------------

``import_a2l()`` (and ``DB.import_a2l()``) accept these parameters:

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Description
   * - ``file_name``
     - (required)
     - Path to the ``.a2l`` file.
   * - ``encoding``
     - ``"latin-1"``
     - Character encoding of the A2L source.  Common alternatives:
       ``"utf-8"``, ``"ascii"``, ``"iso-8859-1"``.  Use
       ``chardetect file.a2l`` on the command line to auto-detect.
   * - ``in_memory``
     - ``False``
     - If ``True``, the SQLite database is created in RAM (no ``.a2ldb``
       file on disk).  Faster, but the data is lost when the session
       closes.
   * - ``remove_existing``
     - ``False``
     - If ``True``, an existing ``.a2ldb`` file with the same name is
       deleted before importing.
   * - ``local``
     - ``False``
     - If ``True``, the ``.a2ldb`` is created in the current working
       directory instead of next to the source file.
   * - ``loglevel``
     - ``"INFO"``
     - Python logging level.  Set to ``"ERROR"`` or ``"WARNING"`` to
       suppress progress messages; ``"DEBUG"`` for verbose output.
   * - ``progress_bar``
     - ``True``
     - Show a Rich progress bar during import.  Disable with ``False``
       for batch/CI usage.
   * - ``debug``
     - ``False``
     - Enable parser-level debug output.

Example:

.. code-block:: python

   from pya2l import DB

   session = DB().import_a2l(
       "my_ecu.a2l",
       encoding="utf-8",
       local=True,
       progress_bar=False,
       loglevel="WARNING",
   )

Export options
-------------

``export_a2l()`` parameters:

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Description
   * - ``db_name``
     - (required)
     - Path to the ``.a2ldb`` database (extension implied if omitted).
   * - ``output``
     - ``sys.stdout``
     - Output file path (string) or a writable file-like object.
   * - ``encoding``
     - ``"latin1"``
     - Encoding for the output A2L text file.

Example:

.. code-block:: python

   from pya2l import export_a2l

   # Export to file
   export_a2l("my_ecu", "exported.a2l")

   # Export to stdout
   export_a2l("my_ecu")

Environment variables
---------------------

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Variable
     - Description
   * - ``ASAP_INCLUDE``
     - Platform-style separated list of directories used for resolving
       ``/INCLUDE`` file references in A2L files.  Works like ``PATH``
       on your operating system.

Example (Windows):

.. code-block:: console

   set ASAP_INCLUDE=C:\a2l\includes;D:\shared\a2l_libs
   a2ldb-imex -i my_ecu.a2l

Example (Linux/macOS):

.. code-block:: console

   export ASAP_INCLUDE=/opt/a2l/includes:/shared/a2l_libs
   a2ldb-imex -i my_ecu.a2l

CLI options (a2ldb-imex)
------------------------

The ``a2ldb-imex`` console script provides quick command-line access:

.. code-block:: console

   a2ldb-imex -h            # show help
   a2ldb-imex -V            # show version

   # Import
   a2ldb-imex -i file.a2l              # import (creates .a2ldb next to file)
   a2ldb-imex -i file.a2l -L           # create .a2ldb in current directory
   a2ldb-imex -i file.a2l -E utf-8     # specify encoding
   a2ldb-imex -i file.a2l -p           # silence progress bar

   # Export
   a2ldb-imex -e file.a2ldb -o out.a2l # export to file
   a2ldb-imex -e file.a2ldb            # export to stdout

   # JSON export
   a2ldb-imex -e file.a2ldb --json -o out.json       # export as JSON
   a2ldb-imex -e file.a2ldb --json --pretty -o out.json  # pretty-printed JSON
   a2ldb-imex -e file.a2ldb --json                    # JSON to stdout

Database pragmas
----------------

pyA2L configures SQLite for optimal performance.  These settings are
applied automatically and normally do not need to be changed:

.. list-table::
   :header-rows: 1
   :widths: 35 65

   * - Pragma
     - Effect
   * - ``journal_mode=WAL``
     - Write-Ahead Logging — allows concurrent readers during writes
   * - ``FOREIGN_KEYS=ON``
     - Enforce foreign key constraints
   * - ``SYNCHRONOUS=OFF``
     - Faster writes (safe with WAL mode)
   * - ``busy_timeout=5000``
     - Wait up to 5 seconds when the database is locked

Logging
-------

pyA2L uses Python's ``logging`` module.  The main loggers are:

- ``pya2l`` — general library messages
- ``pya2l.ifdata`` — IF_DATA parsing diagnostics

Adjust verbosity:

.. code-block:: python

   import logging
   logging.getLogger("pya2l").setLevel(logging.DEBUG)
   logging.getLogger("pya2l.ifdata").setLevel(logging.WARNING)
