Getting Started with pyA2L
==========================

You'll find the example code `here <../pya2l/examples>`_.

Import an .a2l file to database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pya2l import DB

    db = DB()
    session = db.import_a2l(
        "ASAP2_Demo_V161.a2l",
        # encoding="latin-1" is default; override if your file differs
        # progress_bar=False or loglevel="ERROR" to silence progress
    )

If nothing went wrong, your working directory now contains a file named `ASAP2_Demo_V161.a2ldb`,
which is simply a `Sqlite3 <https://www.sqlite.org/>`_ database file.

Unlike other ASAP2 toolkits, you are not required
to parse your `.a2l` files over and over again, which can be quite expensive.

Open an existing .a2ldb database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pya2l import DB

    db = DB()
    session = db.open_existing("ASAP2_Demo_V161")   # No need to specify extension .a2ldb

You may have noticed, that in both cases the return value is stored in an object named `session`:

Enter `SQLAlchemy <https://www.sqlalchemy.org/>`_!

SQLAlchemy offers, amongst other things, a powerful expression language.


Running a first database query
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pya2l import DB
    import pya2l.model as model

    db = DB()
    session = db.open_existing("ASAP2_Demo_V161")
    measurements = session.query(model.Measurement).order_by(model.Measurement.name).all()
    for m in measurements:
        print(f"{m.name:48} {m.datatype:12} 0x{m.ecu_address.address:08x}")

Yields the following output:

::

    ASAM.M.ARRAY_SIZE_16.UBYTE.IDENTICAL             UBYTE        0x00013a30
    ASAM.M.MATRIX_DIM_16_1_1.UBYTE.IDENTICAL         UBYTE        0x00013a30
    ASAM.M.MATRIX_DIM_8_2_1.UBYTE.IDENTICAL          UBYTE        0x00013a30
    ASAM.M.MATRIX_DIM_8_4_2.UBYTE.IDENTICAL          UBYTE        0x00013a30
    ASAM.M.SCALAR.FLOAT32.IDENTICAL                  FLOAT32_IEEE 0x00013a10
    ASAM.M.SCALAR.FLOAT64.IDENTICAL                  FLOAT64_IEEE 0x00013a14
    ASAM.M.SCALAR.SBYTE.IDENTICAL                    SBYTE        0x00013a01
    ASAM.M.SCALAR.SBYTE.LINEAR_MUL_2                 SBYTE        0x00013a01
    ASAM.M.SCALAR.SLONG.IDENTICAL                    SLONG        0x00013a0c
    ASAM.M.SCALAR.SWORD.IDENTICAL                    SWORD        0x00013a04
    ASAM.M.SCALAR.UBYTE.FORM_X_PLUS_4                UBYTE        0x00013a00
    ASAM.M.SCALAR.UBYTE.IDENTICAL                    UBYTE        0x00013a00
    ASAM.M.SCALAR.UBYTE.TAB_INTP_DEFAULT_VALUE       UBYTE        0x00013a00
    ASAM.M.SCALAR.UBYTE.TAB_INTP_NO_DEFAULT_VALUE    UBYTE        0x00013a00
    ASAM.M.SCALAR.UBYTE.TAB_NOINTP_DEFAULT_VALUE     UBYTE        0x00013a00
    ASAM.M.SCALAR.UBYTE.TAB_NOINTP_NO_DEFAULT_VALUE  UBYTE        0x00013a00
    ASAM.M.SCALAR.UBYTE.TAB_VERB_DEFAULT_VALUE       UBYTE        0x00013a00
    ASAM.M.SCALAR.UBYTE.TAB_VERB_NO_DEFAULT_VALUE    UBYTE        0x00013a00
    ASAM.M.SCALAR.UBYTE.VTAB_RANGE_DEFAULT_VALUE     UBYTE        0x00013a00
    ASAM.M.SCALAR.UBYTE.VTAB_RANGE_NO_DEFAULT_VALUE  UBYTE        0x00013a00
    ASAM.M.SCALAR.ULONG.IDENTICAL                    ULONG        0x00013a08
    ASAM.M.SCALAR.UWORD.IDENTICAL                    UWORD        0x00013a02
    ASAM.M.SCALAR.UWORD.IDENTICAL.BITMASK_0008       UWORD        0x00013a20
    ASAM.M.SCALAR.UWORD.IDENTICAL.BITMASK_0FF0       UWORD        0x00013a20
    ASAM.M.VIRTUAL.SCALAR.SWORD.PHYSICAL             SWORD        0x00000000

The classes describing an `.a2ldb` database live in `pya2l.model <../pya2l/model/__init__.py>`_, they are required to query, modify, and add model instances.

Using the Inspect API
~~~~~~~~~~~~~~~~~~~~~

The inspect API provides high-level, read-only wrappers with automatic
conversion and caching:

.. code-block:: python

    from pya2l import DB
    from pya2l.api.inspect import Project, Measurement, Characteristic

    session = DB().open_existing("ASAP2_Demo_V161")

    # Navigate the project hierarchy
    project = Project(session)
    module = project.module[0]
    print(f"Project: {project.name}")
    print(f"Module:  {module.name}")

    # Get a measurement by name
    m = Measurement.get(session, "ASAM.M.SCALAR.UBYTE.IDENTICAL")
    print(f"Name:      {m.name}")
    print(f"Data type: {m.datatype}")
    print(f"Address:   0x{m.ecuAddress:08X}")
    print(f"Limits:    [{m.lowerLimit}, {m.upperLimit}]")
    print(f"CompuMethod: {m.compuMethod.conversionType}")

    # Convert a raw ECU value to physical
    raw_value = 42
    phys = m.compuMethod.int_to_physical(raw_value)
    print(f"  {raw_value} raw → {phys} physical")

    # Query all FLOAT32 measurements
    float_meas = list(module.measurement.query(
        lambda row: row.datatype == "FLOAT32_IEEE"
    ))
    print(f"\nFLOAT32 measurements: {len(float_meas)}")
    for fm in float_meas:
        print(f"  {fm.name}")

    # Query characteristics by type
    maps = list(module.characteristic.query(
        lambda row: row.type == "MAP"
    ))
    print(f"\nMAP characteristics: {len(maps)}")
    for c in maps:
        print(f"  {c.name}: {c.num_axes} axes, shape={c.fnc_np_shape}")

Working with IF_DATA
~~~~~~~~~~~~~~~~~~~~

IF_DATA sections carry vendor-specific protocol information (XCP, CCP, …).
The ``if_data`` attribute on every inspect object returns an ``IfData``
instance with parsed and raw data:

.. code-block:: python

    from pya2l import DB
    from pya2l.api.inspect import Module

    session = DB().open_create("xcp_demo_autodetect.a2l")
    module = Module(session)

    # Access the IfData dataclass
    ifd = module.if_data

    # Parsed structure (list of dicts)
    for block in ifd.if_data_parsed:
        print(block)

    # Quick key look-up via flatmap
    for key in ifd.flatmap:
        print(f"  {key}: {len(ifd.flatmap[key])} occurrence(s)")

    # Raw text for debugging
    for raw in ifd.if_data_raw:
        print(raw.raw[:200], "...")

See :doc:`ifdata` for a comprehensive guide.

Validate and export
~~~~~~~~~~~~~~~~~~~

Basic validation:

.. code-block:: python

    from pya2l import DB
    from pya2l.api.validate import Validator

    session = DB().open_existing("ASAP2_Demo_V161")
    for msg in Validator(session)():
        print(msg.type.name, msg.category.name, msg.diag_code.name, "-", msg.text)

Export back to text:

.. code-block:: python

    from pya2l import export_a2l

    export_a2l("ASAP2_Demo_V161", "exported.a2l")

See :doc:`howto` for Excel export and other short recipes.

The test-suite found  `here <../pya2l/tests/test_a2l_parser.py>`_ is a good starting point for further experimentations, because
it touches virtually every A2L element/attribute.

Next steps
~~~~~~~~~~

- :doc:`tutorial` — In-depth walkthrough of all features
- :doc:`ifdata` — Comprehensive IF_DATA guide
- :doc:`api_reference` — Full API reference with examples
- :doc:`howto` — Task-oriented quick recipes
