# Getting Started with pyA2L

You'll find the example code here: `pya2l/examples`.

## Import an .a2l file to database

```python
from pya2l import DB

db = DB()
session = db.import_a2l("ASAP2_Demo_V161.a2l")
```

If nothing went wrong, your working directory now contains a file named `ASAP2_Demo_V161.a2ldb`, which is simply a [SQLite](https://www.sqlite.org/) database file.

Unlike other ASAP2 toolkits, you are not required to parse your `.a2l` files over and over again, which can be quite expensive.

## Open an existing .a2ldb database

```python
from pya2l import DB

db = DB()
session = db.open_existing("ASAP2_Demo_V161")   # No need to specify extension .a2ldb
```

You may have noticed that in both cases the return value is stored in an object named `session`.

Enter [SQLAlchemy](https://www.sqlalchemy.org/)!

SQLAlchemy offers, amongst other things, a powerful expression language.

## Running a first database query

```python
from pya2l import DB
import pya2l.model as model

db = DB()
session = db.open_existing("ASAP2_Demo_V161")
measurements = session.query(model.Measurement).order_by(model.Measurement.name).all()
for m in measurements:
    print("{:48} {:12} 0x{:08x}".format(m.name, m.datatype, m.ecu_address.address))
```

Yields the following output:

```text
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
```

The classes describing an `.a2ldb` database live in `pya2l.model` (`pya2l/model/__init__.py`); they are required to query, modify, and add model instances.

The test suite at `pya2l/tests/test_a2l_parser.py` is a good starting point for further experimentation, because it touches virtually every A2L element/attribute.
