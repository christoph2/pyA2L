API Reference
=============

This reference covers the three public API modules:

- **Inspect** (``pya2l.api.inspect``) — read-only access to A2L entities
- **Create** (``pya2l.api.create``) — build or augment A2L databases
- **Validate** (``pya2l.api.validate``) — run diagnostic checks

All APIs operate on a ``SessionProxy`` obtained via
:func:`pya2l.import_a2l`, :func:`pya2l.open_existing`, or
:func:`pya2l.open_create`.

.. contents:: On this page
   :local:
   :depth: 2


Session Management
------------------

Every workflow starts by obtaining a session:

.. code-block:: python

   from pya2l import DB

   db = DB()

   # Parse A2L → SQLite  (creates .a2ldb)
   session = db.import_a2l("ASAP2_Demo_V161.a2l")

   # Open existing database  (fast, no reparsing)
   session = db.open_existing("ASAP2_Demo_V161")

   # Open-or-create  (convenience method)
   session = db.open_create("ASAP2_Demo_V161.a2l")

The returned ``session`` is a
:class:`~pya2l.model.SessionProxy` that wraps a SQLAlchemy ``Session``
and adds IF_DATA parsing capabilities.  You can use it for raw
SQLAlchemy queries *and* for the high-level inspect/create/validate
APIs.

Function-level API (no ``DB`` class needed):

.. code-block:: python

   from pya2l import import_a2l, open_existing, export_a2l

   session = import_a2l("file.a2l", encoding="utf-8", progress_bar=False)
   session = open_existing("file")
   export_a2l("file", "output.a2l")


Inspect API
-----------

The inspect API lives in ``pya2l.api.inspect`` and provides read-only,
high-level wrappers around the ORM model.

Project and Module
~~~~~~~~~~~~~~~~~~

``Project`` is the top-level entry point.  It contains one or more
``Module`` objects, each holding all A2L entities.

.. code-block:: python

   from pya2l.api.inspect import Project, Module

   project = Project(session)
   print(project.name)            # e.g. "DemoProject"
   print(project.header.version)  # e.g. "1.0"

   # Iterate modules
   for mod in project.module:
       print(mod.name, mod.longIdentifier)

   # Direct access if you know the module name
   module = Module(session, "MyModule")

``Module`` attributes (all are :class:`FilteredList` unless noted):

.. list-table::
   :header-rows: 1
   :widths: 30 70

   * - Attribute
     - Type / Description
   * - ``axis_pts``
     - ``FilteredList[AxisPts]``
   * - ``blob``
     - ``FilteredList[Blob]``
   * - ``characteristic``
     - ``FilteredList[Characteristic]``
   * - ``compu_method``
     - ``FilteredList[CompuMethod]``
   * - ``compu_tab``
     - ``FilteredList[CompuTab]``
   * - ``compu_tab_verb``
     - ``FilteredList[CompuTabVerb]``
   * - ``compu_tab_verb_ranges``
     - ``FilteredList[CompuTabVerbRanges]``
   * - ``frame``
     - ``FilteredList[Frame]``
   * - ``function``
     - ``FilteredList[Function]``
   * - ``group``
     - ``FilteredList[Group]``
   * - ``measurement``
     - ``FilteredList[Measurement]``
   * - ``record_layout``
     - ``FilteredList[RecordLayout]``
   * - ``transformer``
     - ``FilteredList[Transformer]``
   * - ``unit``
     - ``FilteredList[Unit]``
   * - ``mod_common``
     - ``ModCommon`` — byte order, alignment, data size
   * - ``mod_par``
     - ``ModPar`` — ECU metadata, memory segments, system constants
   * - ``variant_coding``
     - ``VariantCoding`` or ``None``
   * - ``if_data``
     - ``IfData`` — module-level IF_DATA

FilteredList and query()
~~~~~~~~~~~~~~~~~~~~~~~~

All collections on ``Module`` are ``FilteredList`` objects.  Use
``.query()`` to iterate high-level inspect wrappers:

.. code-block:: python

   # All measurements (generator → list)
   all_meas = list(module.measurement.query())

   # With predicate (applied to ORM row, not inspect object)
   float_meas = list(module.measurement.query(
       lambda row: row.datatype in ("FLOAT32_IEEE", "FLOAT64_IEEE")
   ))

   # Prefix match
   engine = list(module.characteristic.query(
       lambda row: row.name.startswith("ENGINE_")
   ))

   # Count without materialising
   n = sum(1 for _ in module.measurement.query())

   # Sort after materialising
   by_name = sorted(module.measurement.query(), key=lambda m: m.name)

.. important::

   The predicate receives the **ORM row** (``pya2l.model.*``), not the
   inspect wrapper.  Use the schema field names (e.g. ``row.name``,
   ``row.datatype``, ``row.groupName``).

CachedBase and .get()
~~~~~~~~~~~~~~~~~~~~~

All entity classes inherit from ``CachedBase`` which maintains a per-session
LRU cache.  **Always use** ``.get()`` instead of the constructor:

.. code-block:: python

   from pya2l.api.inspect import Measurement, Characteristic, AxisPts

   meas = Measurement.get(session, "ENGINE_SPEED")
   char = Characteristic.get(session, "InjectionMap")
   axis = AxisPts.get(session, "RPM_Axis")

   # Cache is transparent — second call returns same object
   assert Measurement.get(session, "ENGINE_SPEED") is meas

Measurement
~~~~~~~~~~~

Read-only access to MEASUREMENT entities.

.. code-block:: python

   from pya2l.api.inspect import Measurement

   m = Measurement.get(session, "ENGINE_SPEED")

   # Core attributes
   print(m.name)               # "ENGINE_SPEED"
   print(m.longIdentifier)     # "Engine rotational speed"
   print(m.datatype)           # "UWORD"
   print(m.resolution)         # 1
   print(m.accuracy)           # 0.5
   print(m.lowerLimit)         # 0.0
   print(m.upperLimit)         # 8000.0

   # Address
   print(f"0x{m.ecuAddress:08X}")     # e.g. 0x00100000
   print(m.ecuAddressExtension)       # 0

   # Conversion (CompuMethod)
   print(m.compuMethod.name)          # "CM_Speed"
   print(m.compuMethod.conversionType)  # "LINEAR"
   raw_value = 1200
   phys = m.compuMethod.int_to_physical(raw_value)
   print(f"{raw_value} → {phys} {m.physUnit}")  # "1200 → 300.0 rpm"

   # Optional attributes
   print(m.byteOrder)          # "LITTLE_ENDIAN" or None
   print(m.bitMask)            # e.g. 0xFFFF or None
   print(m.format)             # e.g. "%8.2" or None
   print(m.displayIdentifier)  # e.g. "EngSpd" or None
   print(m.symbolLink)         # SymbolLink namedtuple or None
   print(m.arraySize)          # int or None
   print(m.matrixDim)          # MatrixDim dataclass
   print(m.discrete)           # bool
   print(m.readWrite)          # bool
   print(m.annotations)        # list of Annotation
   print(m.functionList)       # list of function names
   print(m.virtual)            # list of measuring channels
   print(m.if_data)            # IfData instance

   # NumPy shape (for arrays/matrices)
   print(m.fnc_np_shape)       # e.g. (8, 4)

Characteristic
~~~~~~~~~~~~~~

Read-only access to CHARACTERISTIC entities (VALUE, CURVE, MAP, CUBOID, …).

.. code-block:: python

   from pya2l.api.inspect import Characteristic

   c = Characteristic.get(session, "InjectionMap")

   # Core
   print(c.name)            # "InjectionMap"
   print(c.type)            # "MAP"
   print(f"0x{c.address:08X}")
   print(c.maxDiff)
   print(c.lowerLimit, c.upperLimit)

   # Conversion
   print(c.compuMethod.name)
   print(c.compuMethod.int_to_physical(42))

   # Record layout
   rl = c.deposit           # RecordLayout instance
   print(rl.name)
   print(rl.fncValues)      # FncValues(position=…, data_type=…, …)
   print(rl.axes)           # dict of axis components

   # Axis descriptions
   for i, ax in enumerate(c.axisDescriptions):
       print(f"Axis {i}: {ax.attribute}, max={ax.maxAxisPoints}")
       print(f"  CompuMethod: {ax.compuMethod.name}")
       print(f"  Limits: [{ax.lowerLimit}, {ax.upperLimit}]")

   # Number of axes
   print(c.num_axes)        # 2 for MAP

   # Shape
   print(c.fnc_np_shape)    # e.g. (16, 16)
   print(c.dim)             # total number of function values

   # Memory layout
   print(c.record_layout_components)
   print(f"Total memory: {c.total_allocated_memory} bytes")

   # Optional attributes
   print(c.calibrationAccess)  # e.g. "CALIBRATION"
   print(c.encoding)           # e.g. "UTF8" or None
   print(c.matrixDim)          # MatrixDim
   print(c.extendedLimits)     # ExtendedLimits or None
   print(c.if_data)            # IfData instance

   # Dependent / virtual characteristics
   print(c.dependent_characteristic)
   print(c.virtual_characteristic)

AxisPts
~~~~~~~

Shared axis definitions used by multiple characteristics.

.. code-block:: python

   from pya2l.api.inspect import AxisPts

   ax = AxisPts.get(session, "RPM_Axis")

   print(ax.name)              # "RPM_Axis"
   print(ax.longIdentifier)
   print(f"0x{ax.address:08X}")
   print(ax.maxAxisPoints)     # e.g. 16
   print(ax.lowerLimit, ax.upperLimit)

   # Conversion
   print(ax.compuMethod.name)

   # Record layout
   print(ax.depositAttr.name)  # RecordLayout name
   print(ax.record_layout_components)

   # Memory
   print(f"Allocated: {ax.total_allocated_memory} bytes")

   # IF_DATA
   print(ax.if_data)           # IfData instance

CompuMethod
~~~~~~~~~~~

Conversion methods translate internal (raw) ECU values to physical values
and back.

.. code-block:: python

   from pya2l.api.inspect import CompuMethod

   cm = CompuMethod.get(session, "CM_Speed")

   print(cm.name)              # "CM_Speed"
   print(cm.conversionType)    # "LINEAR", "RAT_FUNC", "TAB_VERB", …
   print(cm.format)            # "%8.2"
   print(cm.unit)              # "rpm"

   # Forward / inverse conversion
   phys = cm.int_to_physical(1200)
   raw  = cm.physical_to_int(300.0)

   # Type-specific attributes
   if cm.conversionType == "LINEAR":
       print(cm.coeffs_linear)  # CoeffsLinear(a=…, b=…)
   elif cm.conversionType == "RAT_FUNC":
       print(cm.coeffs)         # Coeffs(a, b, c, d, e, f)
   elif cm.conversionType == "FORM":
       print(cm.formula)        # {'formula': '…', 'formula_inv': '…'}
   elif cm.conversionType in ("TAB_INTP", "TAB_NOINTP"):
       print(cm.tab)            # CompuTab
   elif cm.conversionType == "TAB_VERB":
       print(cm.tab_verb)       # CompuTabVerb

Supported types:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Conversion Type
     - Description
   * - ``IDENTICAL``
     - Pass-through (phys = raw)
   * - ``LINEAR``
     - ``phys = a·x + b``
   * - ``RAT_FUNC``
     - ``phys = (a·x² + b·x + c) / (d·x² + e·x + f)``
   * - ``FORM``
     - Arbitrary formula string (evaluated via ``numexpr``)
   * - ``TAB_INTP``
     - Table with interpolation
   * - ``TAB_NOINTP``
     - Table without interpolation (nearest match)
   * - ``TAB_VERB``
     - Verbal table (numeric → text)
   * - ``NO_COMPU_METHOD``
     - Explicitly no conversion

RecordLayout
~~~~~~~~~~~~

Describes the physical memory structure of characteristics and axis points.

.. code-block:: python

   from pya2l.api.inspect import RecordLayout

   rl = RecordLayout.get(session, "RL_MAP_16x16")

   print(rl.name)
   print(rl.alignment)              # Alignment dataclass

   # Function values
   fv = rl.fncValues
   if fv.valid():
       print(f"FNC_VALUES: pos={fv.position}, type={fv.data_type}")
       print(f"  NumPy dtype : {rl.fnc_np_dtype}")
       print(f"  Element size: {rl.fnc_element_size} bytes")

   # Axes (dict: axis_name → dict of components)
   for axis_name, components in rl.axes.items():
       print(f"Axis '{axis_name}':")
       for comp_name, comp in components.items():
           print(f"  {comp_name}: {comp}")

   # Identification
   if rl.identification.valid():
       print(f"ID: pos={rl.identification.position}, type={rl.identification.data_type}")

Function and Group
~~~~~~~~~~~~~~~~~~

``Function`` represents logical groupings of calibration parameters.
``Group`` defines UI folder structures.

.. code-block:: python

   from pya2l.api.inspect import Function, Group

   # --- Functions ---
   fn = Function.get(session, "InjectionControl")
   print(fn.name)
   print(fn.longIdentifier)
   print(fn.annotations)
   print(fn.functionVersion)

   # Associated elements
   print(fn.defCharacteristics)    # list of Characteristic
   print(fn.inMeasurements)        # list of Measurement
   print(fn.outMeasurements)       # list of Measurement
   print(fn.locMeasurements)       # list of Measurement
   print(fn.subFunctions)          # list of Function

   # Get all top-level functions
   roots = Function.get_root_functions(session, ordered=True)

   # --- Groups ---
   grp = Group.get(session, "EngineParams")
   print(grp.name)
   print(grp.root)                 # True if top-level group
   print(grp.characteristics)      # list of Characteristic/AxisPts
   print(grp.measurements)         # list of Measurement
   print(grp.functions)            # list of Function
   print(grp.subgroups)            # list of Group

   # Get all root groups
   roots = Group.get_root_groups(session, ordered=True)

ModCommon and ModPar
~~~~~~~~~~~~~~~~~~~~

Module-wide settings and ECU metadata.

.. code-block:: python

   from pya2l.api.inspect import Module

   module = Module(session)

   # --- ModCommon ---
   mc = module.mod_common
   print(mc.comment)
   print(mc.byteOrder)        # "LITTLE_ENDIAN" or "BIG_ENDIAN"
   print(mc.dataSize)         # default word width
   print(mc.alignment)        # Alignment dataclass
   print(mc.alignment.byte)   # e.g. 1
   print(mc.alignment.word)   # e.g. 2
   print(mc.alignment.dword)  # e.g. 4

   # --- ModPar ---
   mp = module.mod_par
   if mp:
       print(mp.comment)
       print(mp.cpu)           # e.g. "TC1766"
       print(mp.customer)
       print(mp.ecu)
       print(mp.epk)           # list of EPK strings
       print(mp.version)

       # System constants
       for name, value in mp.systemConstants.items():
           print(f"  {name} = {value}")

       # Memory segments
       for seg in mp.memorySegments:
           print(f"  {seg.name}: {seg.memoryType} @ 0x{seg.address:08X}, "
                 f"size={seg.size}")

Frame
~~~~~

.. code-block:: python

   from pya2l.api.inspect import Frame

   fr = Frame.get(session, "FRAME1")
   print(fr.name)
   print(fr.longIdentifier)
   print(fr.scalingUnit)
   print(fr.rate)
   print(fr.frame_measurement)   # list of measurement names
   print(fr.if_data)             # IfData instance

VariantCoding
~~~~~~~~~~~~~

Access variant definitions for ECUs with multiple calibration data-sets:

.. code-block:: python

   module = Module(session)
   vc = module.variant_coding

   if vc and vc.variant_coded:
       print(f"Separator: {vc.separator}")
       print(f"Naming   : {vc.naming}")

       # Available criterion values
       for crit_name in vc.criterions:
           values = vc.get_citerion_values(crit_name)
           print(f"  {crit_name}: {values}")

       # All valid combinations
       combos = vc.valid_combinations(list(vc.criterions.keys()))
       for combo in combos:
           print(combo)

       # Variants of a specific characteristic
       variants = vc.variants("MyCalibrationParam")
       for v in variants:
           print(v)

IfData
~~~~~~

See :doc:`ifdata` for a full guide.  Quick reference:

.. code-block:: python

   from pya2l.api.inspect import Measurement

   m = Measurement.get(session, "ENGINE_SPEED")

   ifd = m.if_data                   # IfData instance
   ifd.if_data_parsed                # List[Any] – structured dicts
   ifd.if_data_raw                   # list – original model objects
   ifd.flatmap                       # Dict[str, List[Any]] – lazy flat index


Create API
----------

The create API lives in ``pya2l.api.create`` and provides builder classes
for constructing A2L databases programmatically.

All creators follow the same pattern:

1. Instantiate with a session
2. Call ``create_*`` / ``add_*`` methods
3. Call ``commit()``

ProjectCreator
~~~~~~~~~~~~~~

.. code-block:: python

   from pya2l.api.create import ProjectCreator

   pc = ProjectCreator(session)
   project = pc.create_project("DemoProject", "Example ECU calibration")
   header = pc.add_header(project, "File comment / description")
   pc.add_project_no(header, "PRJ-001")
   pc.commit()

ModuleCreator
~~~~~~~~~~~~~

Creates modules and most structural elements (units, groups, functions,
frames, transformers, typedefs, instances, …):

.. code-block:: python

   from pya2l.api.create import ModuleCreator

   mc = ModuleCreator(session)
   module = mc.create_module("Engine", "Engine control", project=project)

   # Common settings
   mc.add_mod_common(module, "Module comment",
       byte_order="LITTLE_ENDIAN", data_size=32)

   # Units
   mc.add_unit(module, "rpm", "Revolutions per minute",
               display="rpm", type_str="DERIVED")
   mc.add_unit(module, "degC", "Degrees Celsius",
               display="°C", type_str="DERIVED")

   # Groups
   grp = mc.add_group(module, "EngineParams", "Engine parameters")
   mc.add_group_ref_measurement(grp, ["EngineSpeed", "CoolantTemp"])
   mc.add_group_ref_characteristic(grp, ["IdleSpeed"])

   # Frames
   mc.add_frame(module, "Frame1", "CAN frame",
                scaling_unit=1, rate=10,
                measurements=["EngineSpeed"])

   # Typedef structures
   ts = mc.add_typedef_structure(module, "TSig", "Signal struct", size=4)
   mc.add_structure_component(ts, "raw", "UWORD", offset=0)
   mc.add_structure_component(ts, "status", "UBYTE", offset=2)

   # Instances
   mc.add_instance(module, "Signal1", "Instance of TSig",
                   type_name="TSig", address=0x1000)

   mc.commit()

CompuMethodCreator
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pya2l.api.create import CompuMethodCreator

   cmc = CompuMethodCreator(session)

   # LINEAR: phys = factor * raw + offset
   cm = cmc.create_compu_method(
       "CM_Temp", "Temperature", "LINEAR",
       "%6.1", "°C", module_name="Engine"
   )
   cmc.add_coeffs_linear(cm, offset=-40.0, factor=0.1)

   # RAT_FUNC: rational polynomial
   cm2 = cmc.create_compu_method(
       "CM_Pressure", "Pressure", "RAT_FUNC",
       "%8.3", "bar", module_name="Engine"
   )
   cmc.add_coeffs(cm2, a=0, b=0.01, c=-1.0, d=0, e=0, f=1)

   # TAB_VERB: enumeration
   cm3 = cmc.create_compu_method(
       "CM_GearPos", "Gear", "TAB_VERB",
       "%d", "", module_name="Engine"
   )

   # Numeric table
   ct = mc.add_compu_tab(
       module, "CT_Correction", "Correction factors",
       conversion_type="TAB_NOINTP",
       pairs=[(0, 1.0), (50, 1.05), (100, 1.12)],
       default_numeric=1.0,
   )

   # Verbal range table
   vr = mc.add_compu_vtab_range(
       module, "VR_State", "Operating states",
       triples=[(0.0, 0.9, "OFF"), (1.0, 1.9, "STANDBY"), (2.0, 10.0, "RUN")],
       default_value="UNKNOWN",
   )

   cmc.commit()

MeasurementCreator
~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pya2l.api.create import MeasurementCreator

   mec = MeasurementCreator(session)

   # Basic scalar measurement
   m = mec.create_measurement(
       "EngineSpeed", "Engine RPM",
       "UWORD", "CM_Speed",
       resolution=1, accuracy=1.0,
       lower_limit=0.0, upper_limit=8000.0,
       module_name="Engine"
   )
   mec.add_ecu_address(m, 0x100000)
   mec.add_format(m, "%8.2")
   mec.add_byte_order(m, "LITTLE_ENDIAN")
   mec.add_display_identifier(m, "EngSpd")

   # Matrix measurement
   m2 = mec.create_measurement(
       "TempGrid", "Temperature sensor array",
       "SWORD", "CM_Temp",
       resolution=1, accuracy=0.1,
       lower_limit=-40.0, upper_limit=150.0,
       module_name="Engine"
   )
   mec.add_matrix_dim(m2, dims=[4, 4])
   mec.add_ecu_address(m2, 0x200000)

   # Symbol-linked measurement (no direct address)
   m3 = mec.create_measurement(
       "VirtualSignal", "Computed signal",
       "FLOAT32_IEEE", "CM_Voltage",
       resolution=1, accuracy=0.01,
       lower_limit=0.0, upper_limit=5.0,
       module_name="Engine"
   )
   mec.add_symbol_link(m3, "g_voltage_sensor", offset=0)

   mec.commit()

CharacteristicCreator
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pya2l.api.create import CharacteristicCreator

   cc = CharacteristicCreator(session)

   # VALUE (scalar)
   c1 = cc.create_characteristic(
       "IdleSpeed", "Target idle RPM",
       "VALUE", 0x300000, "RL_UWORD", 0.0, "CM_Speed",
       500.0, 1500.0, module_name="Engine"
   )

   # CURVE (1-D)
   c2 = cc.create_characteristic(
       "ThrottleCurve", "Throttle map",
       "CURVE", 0x310000, "RL_CURVE", 0.0, "CM_Percent",
       0.0, 100.0, module_name="Engine"
   )
   cc.add_axis_descr(c2, "STD_AXIS", "NO_INPUT_QUANTITY",
                     "CM_Percent", 8, 0.0, 100.0)

   # MAP (2-D)
   c3 = cc.create_characteristic(
       "InjectionMap", "Fuel injection",
       "MAP", 0x320000, "RL_MAP", 0.0, "CM_Time",
       0.0, 50.0, module_name="Engine"
   )
   cc.add_axis_descr(c3, "STD_AXIS", "EngineSpeed",
                     "CM_Speed", 16, 0.0, 8000.0)
   cc.add_axis_descr(c3, "STD_AXIS", "EngineLoad",
                     "CM_Percent", 16, 0.0, 100.0)

   cc.commit()

RecordLayoutCreator
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pya2l.api.create import RecordLayoutCreator

   rlc = RecordLayoutCreator(session)

   # Scalar layout
   rl = rlc.create_record_layout("RL_UWORD", module_name="Engine")
   rlc.add_fnc_values(rl, position=1, datatype="UWORD",
                      index_mode="ALTERNATE", address_type="DIRECT")

   # Curve layout (axis + values)
   rl2 = rlc.create_record_layout("RL_CURVE", module_name="Engine")
   rlc.add_no_axis_pts_x(rl2, position=1, datatype="UBYTE")
   rlc.add_axis_pts_x(rl2, position=2, datatype="UWORD",
                      index_incr="INDEX_INCR", address_type="DIRECT")
   rlc.add_fnc_values(rl2, position=3, datatype="UWORD",
                      index_mode="ALTERNATE", address_type="DIRECT")

   # Map layout (2 axes + values)
   rl3 = rlc.create_record_layout("RL_MAP", module_name="Engine")
   rlc.add_no_axis_pts_x(rl3, position=1, datatype="UBYTE")
   rlc.add_no_axis_pts_y(rl3, position=2, datatype="UBYTE")
   rlc.add_axis_pts_x(rl3, position=3, datatype="UWORD",
                      index_incr="INDEX_INCR", address_type="DIRECT")
   rlc.add_axis_pts_y(rl3, position=4, datatype="UWORD",
                      index_incr="INDEX_INCR", address_type="DIRECT")
   rlc.add_fnc_values(rl3, position=5, datatype="UWORD",
                      index_mode="ALTERNATE", address_type="DIRECT")

   # Alignment settings
   rlc.add_alignment_byte(rl3, 1)
   rlc.add_alignment_word(rl3, 2)
   rlc.add_alignment_long(rl3, 4)

   rlc.commit()

FunctionCreator
~~~~~~~~~~~~~~~

.. code-block:: python

   from pya2l.api.create import FunctionCreator

   fc = FunctionCreator(session)

   fn = fc.create_function(
       "InjectionCtrl", "Injection control",
       module_name="Engine"
   )
   fc.add_function_version(fn, "1.2.0")
   fc.add_def_characteristic(fn, ["InjectionMap", "IdleSpeed"])
   fc.add_in_measurement(fn, ["EngineSpeed", "EngineLoad"])
   fc.add_out_measurement(fn, ["InjectorDuty"])
   fc.add_sub_function(fn, ["ColdStartEnrich"])

   fc.commit()

GroupCreator
~~~~~~~~~~~~

.. code-block:: python

   from pya2l.api.create import GroupCreator

   gc = GroupCreator(session)

   grp = gc.create_group("EngineBasic", "Basic engine parameters",
                         module_name="Engine")
   gc.add_root(grp)
   gc.add_ref_characteristic(grp, ["IdleSpeed", "ThrottleCurve"])
   gc.add_ref_measurement(grp, ["EngineSpeed"])
   gc.add_sub_group(grp, ["AdvancedParams"])

   gc.commit()

Complete example: building an ECU database from scratch
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from pya2l import DB, export_a2l
   from pya2l.api.create import (
       ProjectCreator, ModuleCreator, CompuMethodCreator,
       MeasurementCreator, CharacteristicCreator,
       RecordLayoutCreator, FunctionCreator, GroupCreator,
   )
   from pya2l.api.inspect import Project

   # --- Setup ---
   db = DB()
   session = db.open_create("TurboECU.a2ldb")

   pc = ProjectCreator(session)
   project = pc.create_project("TurboECU", "Turbocharged engine ECU")
   hdr = pc.add_header(project, "Created by pyA2L automation")
   pc.add_project_no(hdr, "TE-2026-001")

   mc = ModuleCreator(session)
   module = mc.create_module("TCU", "Turbo control unit", project=project)
   mc.add_mod_common(module, "Common settings",
                     byte_order="LITTLE_ENDIAN", data_size=32)

   # --- Units ---
   mc.add_unit(module, "rpm",  "Revolutions per minute", "rpm", "DERIVED")
   mc.add_unit(module, "bar",  "Pressure",               "bar", "DERIVED")
   mc.add_unit(module, "degC", "Temperature",             "°C",  "DERIVED")

   # --- Conversions ---
   cmc = CompuMethodCreator(session)
   cm_rpm = cmc.create_compu_method(
       "CM_RPM", "RPM", "LINEAR", "%8.0", "rpm", module_name="TCU")
   cmc.add_coeffs_linear(cm_rpm, offset=0.0, factor=1.0)

   cm_bar = cmc.create_compu_method(
       "CM_Boost", "Boost pressure", "LINEAR", "%5.2", "bar", module_name="TCU")
   cmc.add_coeffs_linear(cm_bar, offset=-1.0, factor=0.01)

   cm_temp = cmc.create_compu_method(
       "CM_Temp", "Temperature", "LINEAR", "%6.1", "°C", module_name="TCU")
   cmc.add_coeffs_linear(cm_temp, offset=-40.0, factor=0.1)

   # --- Record Layouts ---
   rlc = RecordLayoutCreator(session)
   rl_u16 = rlc.create_record_layout("RL_U16", module_name="TCU")
   rlc.add_fnc_values(rl_u16, 1, "UWORD", "ALTERNATE", "DIRECT")

   rl_curve = rlc.create_record_layout("RL_CURVE_12", module_name="TCU")
   rlc.add_no_axis_pts_x(rl_curve, 1, "UBYTE")
   rlc.add_axis_pts_x(rl_curve, 2, "UWORD", "INDEX_INCR", "DIRECT")
   rlc.add_fnc_values(rl_curve, 3, "UWORD", "ALTERNATE", "DIRECT")

   # --- Measurements ---
   mec = MeasurementCreator(session)

   m_rpm = mec.create_measurement(
       "EngineSpeed", "Current engine speed",
       "UWORD", "CM_RPM", 1, 1.0, 0.0, 8000.0, module_name="TCU")
   mec.add_ecu_address(m_rpm, 0x100000)

   m_boost = mec.create_measurement(
       "BoostPressure", "Turbo boost pressure",
       "UWORD", "CM_Boost", 1, 0.1, -1.0, 3.5, module_name="TCU")
   mec.add_ecu_address(m_boost, 0x100002)

   m_temp = mec.create_measurement(
       "ChargeAirTemp", "Charge air temperature",
       "UWORD", "CM_Temp", 1, 0.5, -40.0, 150.0, module_name="TCU")
   mec.add_ecu_address(m_temp, 0x100004)

   # --- Characteristics ---
   cc = CharacteristicCreator(session)

   c_target = cc.create_characteristic(
       "TargetBoost", "Target boost pressure",
       "VALUE", 0x200000, "RL_U16", 0.0, "CM_Boost",
       0.0, 3.0, module_name="TCU")

   c_curve = cc.create_characteristic(
       "BoostCurve", "Boost vs RPM",
       "CURVE", 0x201000, "RL_CURVE_12", 0.0, "CM_Boost",
       0.0, 3.0, module_name="TCU")
   cc.add_axis_descr(c_curve, "STD_AXIS", "EngineSpeed",
                     "CM_RPM", 12, 0.0, 8000.0)

   # --- Organisation ---
   fc = FunctionCreator(session)
   fn = fc.create_function("BoostControl", "Boost control logic",
                           module_name="TCU")
   fc.add_def_characteristic(fn, ["TargetBoost", "BoostCurve"])
   fc.add_in_measurement(fn, ["EngineSpeed", "BoostPressure", "ChargeAirTemp"])

   gc = GroupCreator(session)
   grp = gc.create_group("TurboParams", "Turbo parameters",
                         module_name="TCU")
   gc.add_root(grp)
   gc.add_ref_characteristic(grp, ["TargetBoost", "BoostCurve"])
   gc.add_ref_measurement(grp, ["EngineSpeed", "BoostPressure", "ChargeAirTemp"])

   # --- Commit and export ---
   gc.commit()
   db.close()

   export_a2l("TurboECU", "TurboECU.a2l")
   print("Done — exported TurboECU.a2l")

   # --- Verify with inspect ---
   session2 = DB().open_existing("TurboECU")
   prj = Project(session2)
   mod = prj.module[0]
   print(f"Module: {mod.name}")
   print(f"  Measurements:    {sum(1 for _ in mod.measurement.query())}")
   print(f"  Characteristics: {sum(1 for _ in mod.characteristic.query())}")
   print(f"  Functions:       {sum(1 for _ in mod.function.query())}")
   print(f"  Groups:          {sum(1 for _ in mod.group.query())}")


Validate API
------------

The validation API checks A2L databases for structural issues and common
mistakes.

.. code-block:: python

   from pya2l import DB
   from pya2l.api.validate import Validator, Level, Category

   session = DB().open_existing("ASAP2_Demo_V161")

   validator = Validator(session)
   diagnostics = validator()      # returns tuple of Message namedtuples

   for msg in diagnostics:
       print(f"[{msg.type.name}] {msg.category.name}: {msg.text}")

Message fields
~~~~~~~~~~~~~~

Each ``Message`` is a named tuple with:

.. list-table::
   :header-rows: 1
   :widths: 20 30 50

   * - Field
     - Type
     - Description
   * - ``type``
     - ``Level``
     - ``INFORMATION``, ``WARNING``, or ``ERROR``
   * - ``category``
     - ``Category``
     - ``DUPLICATE``, ``MISSING``, ``OBSOLETE``
   * - ``diag_code``
     - ``Diagnostics``
     - Specific diagnostic code
   * - ``text``
     - ``str``
     - Human-readable description

Diagnostic codes
~~~~~~~~~~~~~~~~

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Code
     - Meaning
   * - ``MULTIPLE_DEFINITIONS_IN_NAMESPACE``
     - Same name used twice in one module
   * - ``DEFINITION_IN_MULTIPLE_NAMESPACES``
     - Entity exists in multiple modules
   * - ``INVALID_C_IDENTIFIER``
     - Name is not a valid C identifier
   * - ``MISSING_BYTE_ORDER``
     - No byte order specified
   * - ``MISSING_ALIGNMENT``
     - No alignment settings in MOD_COMMON
   * - ``MISSING_EPK``
     - No EPK (ECU Program Key) defined
   * - ``MISSING_ADDR_EPK``
     - No ADDR_EPK specified
   * - ``MISSING_MODULE``
     - Project has no modules
   * - ``DEPRECATED``
     - Use of deprecated A2L features
   * - ``OVERLAPPING_MEMORY``
     - Memory ranges overlap

Practical validation workflow:

.. code-block:: python

   from pya2l import DB
   from pya2l.api.validate import Validator, Level

   session = DB().open_existing("my_project")
   diags = Validator(session)()

   errors   = [d for d in diags if d.type == Level.ERROR]
   warnings = [d for d in diags if d.type == Level.WARNING]
   info     = [d for d in diags if d.type == Level.INFORMATION]

   print(f"Errors: {len(errors)}, Warnings: {len(warnings)}, Info: {len(info)}")

   if errors:
       print("\n--- ERRORS ---")
       for e in errors:
           print(f"  [{e.diag_code.name}] {e.text}")


Low-Level ORM Access
--------------------

For advanced queries that the inspect API doesn't cover, use SQLAlchemy
directly with ``pya2l.model``:

.. code-block:: python

   import pya2l.model as model
   from pya2l import DB

   session = DB().open_existing("ASAP2_Demo_V161")

   # Raw SQL query
   measurements = (
       session.query(model.Measurement)
       .filter(model.Measurement.datatype == "FLOAT32_IEEE")
       .order_by(model.Measurement.name)
       .all()
   )
   for m in measurements:
       print(f"{m.name}: {m.datatype} @ 0x{m.ecu_address.address:08X}")

   # Projection (select specific columns)
   names_and_types = (
       session.query(model.Measurement.name, model.Measurement.datatype)
       .filter(model.Measurement.name.like("ENGINE_%"))
       .all()
   )

   # Count
   n = session.query(model.Measurement).count()

   # Join across relationships
   chars_with_axes = (
       session.query(model.Characteristic)
       .filter(model.Characteristic.type == "MAP")
       .all()
   )

   # Bridge from ORM to inspect
   from pya2l.api.inspect import Measurement as MeasInspect
   for row in measurements:
       meas_obj = MeasInspect.get(session, row.name)
       print(f"{meas_obj.name}: {meas_obj.compuMethod.conversionType}")
