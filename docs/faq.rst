
Frequently Asked Questions
==========================


Where to start?
---------------

*a2ldb* uses a `sqlite3 <http://www.sqlite3.org/>`_ database to store your A2L files to make the contained information easily accessible for your project work. You may start with the command-line script *a2ldb-imex*. There are two use-cases:

    - Read an A2L file and store it to an A2LDB (import). Use the *-i* option in this case. Optionally you may want to specify an encoding (s. next question) with the *-E* option, like ascii, latin-1, utf-8, ...

    .. code-block:: shell

        » a2ldb-imex -i XCPlite-0002E248-5555.A2L -E latin-1


    - Read an A2lDB file and write A2L data (export).

    .. code-block:: shell

        » a2ldb-imex -e XCPlite-0002E248-5555   # A2L data gets written to standard output.

File extensions can be ommited, then automatic addition happens: .a2l (while importing), .a2ldb (export). Note: Depending of your operating system, A2L and a2l may be different (Unix-like OSes)!
There's also a *-h*, resp. *--help* option, giving you some more details.



While importing my A2L file I'm getting strange Unicode decode errors, what can I do?
-------------------------------------------------------------------------------------

By default *pya2ldb* does its best to guess the encoding of your A2L file (by means of `chardet <https:github.com/chardet/chardet>`_,
but this may not work in any case. Then you need to specify an encoding:

.. code-block:: python

    from pya2l import DB

    db = DB()
    session = db.import_a2l("", encoding = "latin-1")

Note: There are also two command-line utilities to play around with, *file* and *chardetect*.

In action:

.. code-block:: shell

   ~ » file examples/tst.a2l
   examples/tst.a2l: UTF-8 Unicode (with BOM) text

   ~ » chardetect examples/tst.a2l
   examples/tst.a2l: UTF-8-SIG with confidence 1.0

   ~ » file XCPlite-0002E248-5555.A2L
   XCPlite-0002E248-5555.A2L: ASCII text, with very long lines

   ~ » chardetect XCPlite-0002E248-5555.A2L
   XCPlite-0002E248-5555.A2L: ascii with confidence 1.0


My A2L file includes tons of files, which in turn include other files. Do I have to copy all of them to my current working directory?
-------------------------------------------------------------------------------------------------------------------------------------

No. There's a environment variable called *ASAP_INCLUDE*, which -- if present, is used to search for */INCLUDE* files. Conventions of your operating system hold. Just like *C*/*C++* *INCLUDE* or good old *PATH*.


How do I work with IF_DATA sections in A2L files?
--------------------------------------------------

IF_DATA sections contain vendor-specific information in A2L files. pyA2L provides a dedicated parser for these sections:

.. code-block:: python

    from pya2l import DB
    from pya2l.aml.ifdata_parser import IfDataParser

    db = DB()
    session = db.open_create("ASAP2_Demo_V161.a2l")

    # Create an IF_DATA parser
    ifdata_parser = IfDataParser(session)

    # Parse an IF_DATA section
    ifdata_text = """/begin IF_DATA XCP
    /begin SEGMENT 0x01 0x02 0x00 0x00 0x00
    /begin CHECKSUM XCP_ADD_44 MAX_BLOCK_SIZE 0xFFFF EXTERNAL_FUNCTION "" /end CHECKSUM
    /end SEGMENT
    /end IF_DATA"""

    result = ifdata_parser.parse(ifdata_text)
    print(result)

You can also access IF_DATA sections that are already parsed from A2L elements:

.. code-block:: python

    from pya2l import DB
    from pya2l.api.inspect import Project

    db = DB()
    session = db.open_create("ASAP2_Demo_V161.a2l")
    project = Project(session)

    # Access module IF_DATA
    module = project.module[0]
    if hasattr(module, 'if_data') and module.if_data:
        print(module.if_data)


How do I create new A2L elements programmatically?
-------------------------------------------------

pyA2L provides creator classes in the `pya2l.api.create` module for creating new A2L elements:

.. code-block:: python

    from pya2l import DB
    from pya2l.api.create import CompuMethodCreator, MeasurementCreator

    db = DB()
    session = db.create("new_database")

    # Create a computation method
    cm_creator = CompuMethodCreator(session)
    compu_method = cm_creator.create_compu_method(
        name="CM_LINEAR",
        long_identifier="Linear conversion",
        conversion_type="LINEAR",
        format_str="%.2f",
        unit="km/h"
    )
    cm_creator.add_coeffs_linear(compu_method, a=0.1, b=0.0)

    # Create a measurement
    meas_creator = MeasurementCreator(session)
    measurement = meas_creator.create_measurement(
        name="ENGINE_SPEED",
        long_identifier="Engine speed",
        datatype="UWORD",
        compu_method="CM_LINEAR",
        lower_limit=0,
        upper_limit=8000,
        unit="rpm"
    )

    # Commit changes
    session.commit()

See the `create_elements.py` example in the examples directory for a more comprehensive demonstration.


How do I filter query results when working with A2L elements?
-----------------------------------------------------------

When querying A2L elements, you can use lambda functions to filter the results:

.. code-block:: python

    from pya2l import DB
    from pya2l.api.inspect import Project

    db = DB()
    session = db.open_create("ASAP2_Demo_V161.a2l")
    project = Project(session)
    module = project.module[0]

    # Get all measurements with FLOAT32_IEEE data type
    float_measurements = list(module.measurement.query(
        lambda x: x.datatype == "FLOAT32_IEEE"
    ))

    # Get all characteristics with names starting with "ENGINE_"
    engine_chars = list(module.characteristic.query(
        lambda x: x.name.startswith("ENGINE_")
    ))


Any missing questions and answers?
----------------------------------

There's a `discussion <https://github.com/christoph2/pyA2l/discussions/33/>`_ on *Github*, feel free to ask, post, whatsoever!
