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

Export back to A2L or JSON
--------------------------

Round‑trip a database back to A2L text:

.. code-block:: python

   from pya2l import export_a2l

   export_a2l("ASAP2_Demo_V161", "exported.a2l")

Or export to JSON for further processing:

.. code-block:: python

   from pya2l.imex.json_exporter import export_json

   export_json("ASAP2_Demo_V161.a2ldb", "exported.json")

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

Creating A2L content programmatically
-------------------------------------

Use the Creator API (``pya2l.api.create``) to build or augment A2L databases.
All creator classes follow a consistent pattern: instantiate with a session,
call ``create_*`` methods to add entities, then commit.

Basic workflow
~~~~~~~~~~~~~~

.. code-block:: python

   from pya2l import DB
   from pya2l.api.create import ProjectCreator, ModuleCreator

   db = DB()
   session = db.open_create("MyProject.a2ldb")

   # Create project
   pc = ProjectCreator(session)
   project = pc.create_project("DemoProject", "Example ECU calibration")

   # Create module
   mc = ModuleCreator(session)
   module = mc.create_module("DemoModule", "Main module", project=project)

   # Commit changes
   mc.commit()
   db.close()

Creating conversion methods (COMPU_METHOD)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define how raw ECU values map to physical units:

.. code-block:: python

   from pya2l.api.create import CompuMethodCreator

   cmc = CompuMethodCreator(session)

   # Linear conversion: phys = a*x + b
   cm_linear = cmc.create_compu_method(
       "CM_Temperature", "Temperature conversion",
       "LINEAR", "%6.2", "°C", module_name="DemoModule"
   )
   cmc.add_coeffs_linear(cm_linear, offset=-40.0, factor=0.1)

   # Rational conversion: phys = (a*x² + b*x + c) / (d*x² + e*x + f)
   cm_rational = cmc.create_compu_method(
       "CM_Pressure", "Non-linear pressure", "RAT_FUNC",
       "%8.3", "bar", module_name="DemoModule"
   )
   cmc.add_formula_rational(cm_rational, a=0, b=0.01, c=0, d=0, e=0, f=1)

   # Tabular conversion (value pairs)
   cm_tab = cmc.create_compu_method(
       "CM_GearState", "Gear position", "TAB_VERB",
       "%d", "", module_name="DemoModule"
   )
   cmc.add_compu_tab_verbal_range(cm_tab, [
       (0, 0, "Neutral"),
       (1, 1, "First"),
       (2, 2, "Second"),
       (3, 3, "Third"),
   ])

Creating measurements
~~~~~~~~~~~~~~~~~~~~~

Measurements are ECU signals read by calibration tools:

.. code-block:: python

   from pya2l.api.create import MeasurementCreator

   mec = MeasurementCreator(session)

   # Scalar measurement
   meas = mec.create_measurement(
       "EngineSpeed", "Engine rotational speed",
       "UWORD", "CM_Speed", resolution=1, accuracy=0.5,
       lower_limit=0.0, upper_limit=8000.0,
       module_name="DemoModule"
   )
   mec.add_ecu_address(meas, 0x10000)

   # Measurement with matrix dimensions (e.g., 2D sensor array)
   meas_matrix = mec.create_measurement(
       "SensorArray", "Temperature sensor grid",
       "SWORD", "CM_Temperature", resolution=1, accuracy=0.1,
       lower_limit=-40.0, upper_limit=150.0,
       module_name="DemoModule"
   )
   mec.add_matrix_dim(meas_matrix, dims=[8, 8])  # 8×8 grid
   mec.add_ecu_address(meas_matrix, 0x20000)

   # Measurement with symbol link (no direct address)
   meas_sym = mec.create_measurement(
       "SymLinkedSignal", "Signal via symbol",
       "FLOAT32_IEEE", "CM_Voltage", resolution=1, accuracy=0.01,
       lower_limit=0.0, upper_limit=5.0,
       module_name="DemoModule"
   )
   mec.add_symbol_link(meas_sym, "g_sensor_voltage", offset=0)

Creating characteristics (calibration parameters)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Characteristics are tunable parameters written by calibration tools:

.. code-block:: python

   from pya2l.api.create import CharacteristicCreator

   cc = CharacteristicCreator(session)

   # Scalar (VALUE) characteristic
   char_value = cc.create_characteristic(
       "InjectionDuration", "Fuel injection time",
       "VALUE", 0x30000, "RL_UWORD", 0.0, "CM_Time",
       0.0, 100.0, module_name="DemoModule"
   )

   # Curve (1D lookup table)
   char_curve = cc.create_characteristic(
       "ThrottleCurve", "Throttle position vs. airflow",
       "CURVE", 0x31000, "RL_CURVE_8", 0.0, "CM_Airflow",
       0.0, 1000.0, module_name="DemoModule"
   )
   cc.add_axis_descr(char_curve, "STD_AXIS", "NO_INPUT_QUANTITY",
                     "CM_Percent", 8, 0.0, 100.0)

   # Map (2D lookup table)
   char_map = cc.create_characteristic(
       "InjectionMap", "RPM vs. Load injection map",
       "MAP", 0x32000, "RL_MAP_16x16", 0.0, "CM_Time",
       0.0, 50.0, module_name="DemoModule"
   )
   # X-axis: RPM
   cc.add_axis_descr(char_map, "STD_AXIS", "EngineSpeed",
                     "CM_Speed", 16, 0.0, 8000.0)
   # Y-axis: Load
   cc.add_axis_descr(char_map, "STD_AXIS", "EngineLoad",
                     "CM_Percent", 16, 0.0, 100.0)

Creating axis points (shared axes)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

AXIS_PTS define reusable axis definitions for multiple characteristics:

.. code-block:: python

   from pya2l.api.create import AxisPtsCreator

   apc = AxisPtsCreator(session)

   axis = apc.create_axis_pts(
       "RPM_Axis", "Standard RPM breakpoints",
       0x40000, "NO_INPUT_QUANTITY", "RL_AXIS_16",
       0.0, "CM_Speed", 16, 0.0, 8000.0,
       module_name="DemoModule"
   )

Creating record layouts
~~~~~~~~~~~~~~~~~~~~~~~

Record layouts describe memory structures for characteristics/measurements:

.. code-block:: python

   from pya2l.api.create import RecordLayoutCreator

   rlc = RecordLayoutCreator(session)

   # Simple scalar layout
   rl = rlc.create_record_layout("RL_UWORD", module_name="DemoModule")
   rlc.add_fnc_values(rl, position=1, datatype="UWORD", index_mode="ALTERNATE",
                      address_type="DIRECT")

   # Curve layout (axis + values)
   rl_curve = rlc.create_record_layout("RL_CURVE_8", module_name="DemoModule")
   rlc.add_axis_pts_x(rl_curve, position=1, datatype="UWORD", index_incr="INDEX",
                      address_type="DIRECT")
   rlc.add_fnc_values(rl_curve, position=2, datatype="UWORD", index_mode="ALTERNATE",
                      address_type="DIRECT")

Organizing with groups and functions
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Group related entities for better organization:

.. code-block:: python

   mc = ModuleCreator(session)

   # Create a function (logical grouping)
   func = mc.add_function(
       module, name="InjectionControl",
       long_identifier="Fuel injection calibration parameters"
   )
   mc.add_def_characteristic(func, ["InjectionDuration", "InjectionMap"])
   mc.add_ref_characteristic(func, ["ThrottleCurve"])  # read-only reference
   mc.add_in_measurement(func, ["EngineSpeed", "EngineLoad"])

   # Create a group (GUI folder structure)
   grp = mc.add_group(
       module, name="EngineParams",
       long_identifier="All engine-related parameters"
   )
   mc.add_group_ref_characteristic(grp, ["InjectionDuration", "InjectionMap"])
   mc.add_group_ref_measurement(grp, ["EngineSpeed"])
   mc.add_group_sub_group(grp, ["AdvancedSettings"])  # nested groups

Adding units
~~~~~~~~~~~~

Define physical units for conversions:

.. code-block:: python

   mc = ModuleCreator(session)

   unit_rpm = mc.add_unit(
       module, name="rpm",
       long_identifier="Revolutions per minute",
       display="rpm", type_str="DERIVED"
   )

   unit_celsius = mc.add_unit(
       module, name="degC",
       long_identifier="Degrees Celsius",
       display="°C", type_str="TEMPERATURE"
   )

Complete example: building a minimal ECU database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pya2l import DB
   from pya2l.api.create import (
       ProjectCreator, ModuleCreator, CompuMethodCreator,
       MeasurementCreator, CharacteristicCreator,
       RecordLayoutCreator
   )

   db = DB()
   session = db.open_create("MinimalECU.a2ldb")

   # Project and module
   pc = ProjectCreator(session)
   project = pc.create_project("MinimalECU", "Minimal ECU example")

   mc = ModuleCreator(session)
   module = mc.create_module("Engine", "Engine control", project=project)

   # Unit
   mc.add_unit(module, name="rpm", long_identifier="RPM",
               display="rpm", type_str="DERIVED")

   # Conversion
   cmc = CompuMethodCreator(session)
   cm = cmc.create_compu_method(
       "CM_RPM", "RPM conversion", "LINEAR",
       "%8.2", "rpm", module_name="Engine"
   )
   cmc.add_coeffs_linear(cm, offset=0.0, factor=0.25)

   # Record layout
   rlc = RecordLayoutCreator(session)
   rl = rlc.create_record_layout("RL_UWORD", module_name="Engine")
   rlc.add_fnc_values(rl, position=1, datatype="UWORD",
                      index_mode="ALTERNATE", address_type="DIRECT")

   # Measurement
   mec = MeasurementCreator(session)
   meas = mec.create_measurement(
       "EngineSpeed", "Current engine speed",
       "UWORD", "CM_RPM", resolution=1, accuracy=1.0,
       lower_limit=0.0, upper_limit=8000.0,
       module_name="Engine"
   )
   mec.add_ecu_address(meas, 0x100000)

   # Characteristic
   cc = CharacteristicCreator(session)
   char = cc.create_characteristic(
       "IdleSpeed", "Target idle speed",
       "VALUE", 0x200000, "RL_UWORD", 0.0, "CM_RPM",
       500.0, 1500.0, module_name="Engine"
   )

   # Group
   grp = mc.add_group(module, name="BasicParams",
                      long_identifier="Basic parameters")
   mc.add_group_ref_characteristic(grp, ["IdleSpeed"])
   mc.add_group_ref_measurement(grp, ["EngineSpeed"])

   # Commit and close
   mc.commit()
   db.close()

   # Export to A2L
   from pya2l import export_a2l
   export_a2l("MinimalECU", "MinimalECU.a2l")

Tips for using the Creator API
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- **Always commit**: Call ``creator.commit()`` before closing the database.
- **Module names**: Most ``create_*`` methods accept ``module_name="..."`` to
  associate entities with a specific module.
- **Referential integrity**: Creators validate references (e.g., conversion
  names, record layout names) exist before creating entities.
- **Incremental builds**: Open an existing database with ``open_existing()``
  and add to it; useful for augmenting imported A2L files.
- **Inspect to verify**: Use ``pya2l.api.inspect`` classes to query and
  validate what you've created.

Available creator classes
~~~~~~~~~~~~~~~~~~~~~~~~~

Full list in ``pya2l.api.create``:

- ``ProjectCreator`` – PROJECT
- ``ModuleCreator`` – MODULE, UNIT, GROUP, FUNCTION, FRAME, TRANSFORMER, etc.
- ``CompuMethodCreator`` – COMPU_METHOD, COMPU_TAB, COMPU_VTAB
- ``MeasurementCreator`` – MEASUREMENT
- ``CharacteristicCreator`` – CHARACTERISTIC
- ``AxisPtsCreator`` – AXIS_PTS
- ``RecordLayoutCreator`` – RECORD_LAYOUT

See ``pya2l/examples/create_quickstart.py`` for more examples.
