HOW‑TOs
=======

Quick, task‑oriented guides for common workflows.

Import once, reuse the database
-------------------------------

Persist a parsed A2L as SQLite (.a2ldb) so you don't reparse on every run:

.. code-block:: python

   from pya2l import DB

   db = DB()
   session = db.import_a2l("ASAP2_Demo_V161.a2l")  # writes ASAP2_Demo_V161.a2ldb

Later, open the database without reparsing:

.. code-block:: python

   from pya2l import DB

   db = DB()
   session = db.open_existing("ASAP2_Demo_V161")  # .a2ldb suffix implied

Export back to A2L
------------------

Round‑trip a database back into text:

.. code-block:: python

   from pya2l import export_a2l

   export_a2l("ASAP2_Demo_V161", "exported.a2l")

CLI import/export (``a2ldb-imex``)
----------------------------------

Use the bundled console script instead of writing Python:

.. code-block:: console

   # Show help/version
   a2ldb-imex -h
   a2ldb-imex -V

   # Import with explicit encoding, write DB in current directory, silence progress
   a2ldb-imex -i examples\\ASAP2_Demo_V161.a2l -E utf-8 -L -p

   # Export an existing DB back to A2L (file or stdout)
   a2ldb-imex -e ASAP2_Demo_V161.a2ldb -o exported.a2l
   a2ldb-imex -e ASAP2_Demo_V161.a2ldb > exported.a2l

Dump measurements to Excel
--------------------------

Use pandas to move selected fields into Excel (install ``pandas`` and ``openpyxl`` first):

.. code-block:: python

   import pandas as pd
   from pya2l import DB, model

   session = DB().open_existing("ASAP2_Demo_V161")
   q = (
       session.query(
           model.Measurement.name,
           model.Measurement.datatype,
           model.Measurement.conversion,
           model.Measurement.ecu_address,
       )
       .order_by(model.Measurement.name)
   )
   df = pd.read_sql(q.statement, session.bind)
   df.to_excel("measurements.xlsx", index=False)

Handle encodings and quiet mode
-------------------------------

Override the default ``latin-1`` import encoding and silence the progress bar:

.. code-block:: python

   from pya2l import DB

   db = DB()
   session = db.import_a2l(
       "my_file.a2l",
       encoding="utf-8",
       progress_bar=False,
       loglevel="ERROR",  # also suppresses progress
   )
