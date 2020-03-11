Getting Started with pyA2L
==========================

The following code snippets will give you an overview what could be done with pyA2L.

Import an .a2l file to database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from pya2l import DB

    db = DB()
    session = db.import_a2l("ASAP2_Demo_V161.a2l")

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
        print("{:48} {:12} 0x{:08x}".format(m.name, m.datatype, m.ecu_address.address))

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

There are several things to note:
    - The classes describing an `.a2ldb` database live in `pya2l.model <../pya2l/model/__init__.py>`_, they are required to query, modify, and add model instances.

More helpful would be...    / It's more reasonable to consult...
there's a comprehensive test-suite ??? touching virtually everything

You may ask, what about characteristics (parameters, maps, curves, the like), they also have
addresses 

not to confuse people knowing the ASAP2/ASAM MCD-2MC specification


Last words
~~~~~~~~~~

Creation and manipulation of databases is subject of another document.
