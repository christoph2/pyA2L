Tutorial
========

This tutorial provides a comprehensive guide to using the pyA2L library for working with ASAM A2L files. It covers basic usage, advanced features, and common use cases.

Basic Usage
----------

Importing A2L Files
~~~~~~~~~~~~~~~~~~

The first step in working with A2L files is to import them into a database. This allows for faster access and querying of the data.

.. code-block:: python

    from pya2l import DB

    # Create a database instance
    db = DB()

    # Import an A2L file into a database
    session = db.import_a2l("ASAP2_Demo_V161.a2l")

This creates a SQLite database file with the extension `.a2ldb` in your working directory.

Opening Existing Databases
~~~~~~~~~~~~~~~~~~~~~~~~~

If you've already imported an A2L file, you can open the existing database:

.. code-block:: python

    from pya2l import DB

    db = DB()
    session = db.open_existing("ASAP2_Demo_V161")  # No need to specify .a2ldb extension

Alternatively, you can use `open_create()` which will open an existing database if it exists, or create a new one if it doesn't:

.. code-block:: python

    session = db.open_create("ASAP2_Demo_V161.a2l")  # Creates database from A2L file
    # or
    session = db.open_create("ASAP2_Demo_V161")      # Opens existing database

Accessing Project Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have a session, you can access the project information:

.. code-block:: python

    from pya2l.api.inspect import Project

    # Create a Project instance
    project = Project(session)

    # Access project attributes
    print(project.name)
    print(project.header.version)

    # Access modules
    for module in project.module:
        print(module.name)

Working with Modules
------------------

Modules are the main containers for A2L data. Most of your work will involve accessing and manipulating module data.

Accessing Module Elements
~~~~~~~~~~~~~~~~~~~~~~~

You can access various elements within a module:

.. code-block:: python

    # Get the first module
    module = project.module[0]

    # Access module attributes
    print(module.name)
    print(module.description)

    # Access module elements using query methods
    measurements = list(module.measurement.query())
    characteristics = list(module.characteristic.query())
    axis_points = list(module.axis_pts.query())
    compu_methods = list(module.compu_method.query())

Filtering Queries
~~~~~~~~~~~~~~~

You can filter queries using lambda functions:

.. code-block:: python

    # Get all measurements with FLOAT32_IEEE or FLOAT64_IEEE data types
    float_measurements = list(module.measurement.query(
        lambda x: x.datatype in ("FLOAT32_IEEE", "FLOAT64_IEEE")
    ))

    # Get all characteristics with a specific name pattern
    specific_chars = list(module.characteristic.query(
        lambda x: x.name.startswith("ENGINE_")
    ))

Advanced Features
---------------

Working with IF_DATA Sections
~~~~~~~~~~~~~~~~~~~~~~~~~~~

IF_DATA sections contain vendor-specific information. pyA2L provides a parser for these sections:

.. code-block:: python

    from pya2l.aml.ifdata_parser import IfDataParser

    # Create an IF_DATA parser
    ifdata_parser = IfDataParser(session)

    # Parse an IF_DATA section
    ifdata_text = """/begin IF_DATA XCP
    /begin SEGMENT 0x01 0x02 0x00 0x00 0x00
    /begin CHECKSUM XCP_ADD_44 MAX_BLOCK_SIZE 0xFFFF EXTERNAL_FUNCTION "" /end CHECKSUM
    /begin PAGE 0x01 ECU_ACCESS_WITH_XCP_ONLY XCP_READ_ACCESS_WITH_ECU_ONLY XCP_WRITE_ACCESS_NOT_ALLOWED /end PAGE
    /begin PAGE 0x00 ECU_ACCESS_WITH_XCP_ONLY XCP_READ_ACCESS_WITH_ECU_ONLY XCP_WRITE_ACCESS_WITH_ECU_ONLY /end PAGE
    /end SEGMENT
    /end IF_DATA"""

    result = ifdata_parser.parse(ifdata_text)
    print(result)

Creating New A2L Elements
~~~~~~~~~~~~~~~~~~~~~~~

You can create new A2L elements using the creator classes:

.. code-block:: python

    from pya2l.api.create import CompuMethodCreator, MeasurementCreator

    # Create a new computation method
    cm_creator = CompuMethodCreator(session)
    compu_method = cm_creator.create_compu_method(
        name="CM_LINEAR",
        long_identifier="Linear conversion",
        conversion_type="LINEAR",
        format_str="%.2f",
        unit="km/h"
    )

    # Add coefficients to the computation method
    cm_creator.add_coeffs_linear(compu_method, a=0.1, b=0.0)

    # Create a new measurement
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

    # Commit changes to the database
    session.commit()

Working with Variant Coding
~~~~~~~~~~~~~~~~~~~~~~~~~

Variant coding allows for different configurations of the same ECU:

.. code-block:: python

    # Access variant coding information
    variant_coding = module.variant_coding

    # Print variant coding details
    print(variant_coding.var_characteristic)
    print(variant_coding.var_criterion)
    print(variant_coding.var_forbidden_comb)

Common Use Cases
--------------

Extracting Measurement Information
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A common task is to extract information about all measurements:

.. code-block:: python

    # Get all measurements
    measurements = list(module.measurement.query())

    # Print measurement details
    for meas in measurements:
        print(f"Name: {meas.name}")
        print(f"Description: {meas.longIdentifier}")
        print(f"Data Type: {meas.datatype}")
        print(f"ECU Address: 0x{meas.address:08x}")
        print(f"Conversion: {meas.compuMethod.conversionType}")
        print(f"Unit: {meas.physUnit}")
        print("---")

Working with Characteristics
~~~~~~~~~~~~~~~~~~~~~~~~~~

Characteristics represent calibration parameters:

.. code-block:: python

    # Get all characteristics
    characteristics = list(module.characteristic.query())

    # Print characteristic details
    for char in characteristics:
        print(f"Name: {char.name}")
        print(f"Type: {char.type}")
        print(f"Address: 0x{char.address:08x}")
        print(f"Record Layout: {char.depositAttr.name}")
        print("---")

Analyzing Record Layouts
~~~~~~~~~~~~~~~~~~~~~

Record layouts define how data is stored in memory:

.. code-block:: python

    # Get all record layouts
    record_layouts = list(module.record_layout.query())

    # Print record layout details
    for rl in record_layouts:
        print(f"Name: {rl.name}")
        print(f"Alignment: {rl.alignment}")

        # Print components
        if rl.fnc_values:
            print(f"Function Values: {rl.fnc_values.position}, {rl.fnc_values.data_type}")

        if rl.axis_pts_x:
            print(f"X-Axis Points: {rl.axis_pts_x.position}, {rl.axis_pts_x.data_type}")

        if rl.axis_pts_y:
            print(f"Y-Axis Points: {rl.axis_pts_y.position}, {rl.axis_pts_y.data_type}")

        print("---")

Best Practices
------------

1. **Close Sessions**: Always close your database sessions when you're done:

   .. code-block:: python

       session.close()

2. **Error Handling**: Use try-except blocks to handle potential errors:

   .. code-block:: python

       try:
           session = db.open_existing("NonExistentFile")
       except Exception as e:
           print(f"Error opening database: {e}")

3. **Commit Changes**: When making changes to the database, remember to commit them:

   .. code-block:: python

       # After making changes
       session.commit()

       # If something goes wrong, you can roll back
       # session.rollback()

4. **Use Query Filters**: Filter your queries to improve performance:

   .. code-block:: python

       # This is more efficient than getting all measurements and filtering in Python
       float_measurements = list(module.measurement.query(
           lambda x: x.datatype == "FLOAT32_IEEE"
       ))

5. **Cache Results**: For frequently accessed data, consider caching the results:

   .. code-block:: python

       # Cache all measurements
       all_measurements = list(module.measurement.query())

       # Use the cached list instead of querying again
       float_measurements = [m for m in all_measurements if m.datatype == "FLOAT32_IEEE"]

Conclusion
---------

This tutorial covered the basics of working with pyA2L. For more detailed information, refer to the API reference documentation and the example scripts in the `pya2l/examples` directory.
