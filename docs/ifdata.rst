Working with IF_DATA
====================

IF_DATA sections in A2L files carry vendor-specific transport-layer and
protocol information (XCP, CCP, KWP2000, …).  pyA2L parses these blocks
automatically when an AML description is available and wraps the result
in the :class:`~pya2l.api.inspect.IfData` dataclass, which gives you
simultaneous access to the **parsed** (structured) and **raw** (text)
representation.

The IfData class
----------------

Every inspect object that can contain IF_DATA blocks
(``Module``, ``Measurement``, ``Characteristic``, ``AxisPts``,
``Function``, ``Group``, ``Frame``, ``Instance``, ``Blob``, and the
``MemoryLayout`` / ``MemorySegment`` entries inside ``ModPar``)
exposes an ``if_data`` attribute of type ``IfData``.

.. code-block:: python

   from dataclasses import dataclass, field
   from typing import Any, Dict, List, Union

   @dataclass
   class IfData:
       """Parsed + raw IF_DATA container.

       Parameters
       ----------
       if_data_parsed : List[Any]
           Structured representation produced by the AML-based parser.
           Each list element corresponds to one ``/begin IF_DATA … /end IF_DATA``
           block in the source file.
       if_data_raw : list
           The original model objects (``pya2l.model.IfData``) that hold the
           raw text.  Useful when you need the verbatim A2L source, e.g. for
           re-export or manual inspection.

       Attributes
       ----------
       flatmap : Dict[str, List[Any]]
           A lazily built dictionary that flattens the nested parsed structure
           into a key → [values…] mapping.  Handy for quick look-ups when
           you know the tag name but not the nesting depth.
       """
       if_data_parsed: List[Any]
       if_data_raw: list
       items: Dict[str, List[Any]] = field(default_factory=dict)

       @property
       def flatmap(self) -> Dict[str, List[Any]]: ...

Quick start
-----------

.. code-block:: python

   from pya2l import DB
   from pya2l.api.inspect import Measurement

   db = DB()
   session = db.open_create("ASAP2_Demo_V161.a2l")

   meas = Measurement.get(session, "ASAM.M.SCALAR.UBYTE.IDENTICAL")

   # IfData instance — always present, may be empty
   ifd = meas.if_data

   # Parsed data (list of dicts/nested structures)
   print(ifd.if_data_parsed)          # e.g. [{'XCP': { ... }}]

   # Raw model objects (for re-export or text inspection)
   print(len(ifd.if_data_raw))        # number of IF_DATA blocks

   # Quick key-based look-up via flatmap
   if "DAQ_LIST" in ifd.flatmap:
       print(ifd.flatmap["DAQ_LIST"])

Parsed data vs. raw data
-------------------------

+---------------------------+-----------------------------------------------+
| Attribute                 | Description                                   |
+===========================+===============================================+
| ``if_data_parsed``        | ``List[Any]`` — structured dicts/lists built  |
|                           | by the AML parser.  One entry per             |
|                           | ``/begin IF_DATA`` block.                     |
+---------------------------+-----------------------------------------------+
| ``if_data_raw``           | ``list`` of ORM ``model.IfData`` objects.     |
|                           | Each carries a ``.raw`` attribute with the    |
|                           | verbatim text between                         |
|                           | ``/begin IF_DATA … /end IF_DATA``.            |
+---------------------------+-----------------------------------------------+
| ``flatmap``               | ``Dict[str, List[Any]]`` — lazily traverses   |
|                           | ``if_data_parsed`` and collects every key it  |
|                           | encounters.  Subsequent accesses are instant.  |
+---------------------------+-----------------------------------------------+

Why both?  The parsed representation is the fast path for programmatic
access — you get Python dicts you can index into.  The raw representation
is essential when you need the original text for diagnostics, logging,
or when the AML schema is unavailable (in which case ``if_data_parsed``
is empty but the raw text is still there).

Using the flatmap
-----------------

Deeply nested IF_DATA trees can be tedious to traverse.  ``flatmap``
flattens every key it encounters into a dictionary of lists:

.. code-block:: python

   from pya2l import DB
   from pya2l.api.inspect import Module

   session = DB().open_create("xcp_demo_autodetect.a2l")
   module = Module(session)

   ifd = module.if_data    # IfData instance

   # Iterate all keys the parser found
   for key, values in ifd.flatmap.items():
       print(f"{key}: {len(values)} occurrence(s)")

   # Direct look-up of a known tag
   if "PROTOCOL_LAYER" in ifd.flatmap:
       proto = ifd.flatmap["PROTOCOL_LAYER"]
       print("Protocol layer info:", proto)

   if "DAQ" in ifd.flatmap:
       daq = ifd.flatmap["DAQ"]
       print("DAQ configuration:", daq)

.. note::

   ``flatmap`` is built lazily on first access.  The cost is proportional
   to the depth of the parsed tree and is paid only once.

Accessing IF_DATA across all entity types
-----------------------------------------

Every entity that can carry IF_DATA in the ASAP2 standard exposes it:

.. code-block:: python

   from pya2l import DB
   from pya2l.api.inspect import (
       Module, Measurement, Characteristic, AxisPts,
       Function, Group, Frame,
   )

   session = DB().open_create("my_ecu.a2l")
   module = Module(session)

   # --- MODULE level ---
   print("Module IF_DATA:", module.if_data.if_data_parsed)

   # --- MEASUREMENT ---
   for meas in module.measurement.query():
       if meas.if_data.if_data_parsed:
           print(f"  {meas.name}: {meas.if_data.if_data_parsed}")

   # --- CHARACTERISTIC ---
   for char in module.characteristic.query():
       if char.if_data.if_data_parsed:
           print(f"  {char.name}: {char.if_data.if_data_parsed}")

   # --- AXIS_PTS ---
   for ax in module.axis_pts.query():
       if ax.if_data.if_data_parsed:
           print(f"  {ax.name}: {ax.if_data.if_data_parsed}")

   # --- FUNCTION, GROUP, FRAME ---
   for fn in module.function.query():
       if fn.if_data.if_data_parsed:
           print(f"  FUNCTION {fn.name}: {fn.if_data.if_data_parsed}")

   for grp in module.group.query():
       if grp.if_data.if_data_parsed:
           print(f"  GROUP {grp.name}: {grp.if_data.if_data_parsed}")

   for fr in module.frame.query():
       if fr.if_data.if_data_parsed:
           print(f"  FRAME {fr.name}: {fr.if_data.if_data_parsed}")

   # --- MEMORY_LAYOUT / MEMORY_SEGMENT (inside ModPar) ---
   mp = module.mod_par
   if mp:
       for layout in mp.memoryLayouts:
           if layout.if_data.if_data_parsed:
               print(f"  MEMORY_LAYOUT: {layout.if_data.if_data_parsed}")
       for seg in mp.memorySegments:
           if seg.if_data.if_data_parsed:
               print(f"  MEMORY_SEGMENT {seg.name}: {seg.if_data.if_data_parsed}")

Practical examples
------------------

Extracting XCP transport-layer parameters
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Many ECU projects use XCP on Ethernet or CAN.  The transport
configuration lives in the module-level IF_DATA:

.. code-block:: python

   from pya2l import DB
   from pya2l.api.inspect import Module

   session = DB().open_create("xcp_demo_autodetect.a2l")
   module = Module(session)

   ifd = module.if_data

   # Walk the parsed tree for XCP specifics
   for block in ifd.if_data_parsed:
       if not isinstance(block, dict):
           continue
       if "XCP" not in block:
           continue

       xcp = block["XCP"]

       # Protocol layer
       if "PROTOCOL_LAYER" in xcp:
           proto = xcp["PROTOCOL_LAYER"]
           print("XCP Protocol Layer:")
           print(f"  Version          : {proto.get('version', 'N/A')}")
           print(f"  T1 timeout [ms]  : {proto.get('T1', 'N/A')}")
           print(f"  Max CTO          : {proto.get('MAX_CTO', 'N/A')}")
           print(f"  Max DTO          : {proto.get('MAX_DTO', 'N/A')}")
           print(f"  Byte order       : {proto.get('BYTE_ORDER', 'N/A')}")

       # DAQ lists
       if "DAQ" in xcp:
           daq = xcp["DAQ"]
           print(f"DAQ: {daq}")

       # Transport layer (TCP/UDP)
       for tl_key in ("TRANSPORT_LAYER_CMD", "XCP_ON_TCP_IP", "XCP_ON_UDP_IP", "XCP_ON_CAN"):
           if tl_key in xcp:
               print(f"{tl_key}: {xcp[tl_key]}")

Inspecting CCP (CAN Calibration Protocol) blocks
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CCP information typically appears under measurement or characteristic
IF_DATA:

.. code-block:: python

   from pya2l import DB
   from pya2l.api.inspect import Module

   session = DB().open_create("If_ccp4.a2l")
   module = Module(session)

   # Collect all CCP-related IF_DATA across measurements
   for meas in module.measurement.query():
       for block in meas.if_data.if_data_parsed:
           if isinstance(block, dict) and "ASAP1B_CCP" in block:
               ccp = block["ASAP1B_CCP"]
               print(f"{meas.name}: CCP info = {ccp}")

   # Module-level CCP parameters
   for block in module.if_data.if_data_parsed:
       if isinstance(block, dict) and "ASAP1B_CCP" in block:
           print("Module CCP:", block["ASAP1B_CCP"])

Working with KWP2000 transport data
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

KWP2000-based A2L files store baud rates, timing, and security
parameters in IF_DATA:

.. code-block:: python

   from pya2l import DB
   from pya2l.api.inspect import Module

   session = DB().open_create("if_kwp6.a2l")
   module = Module(session)

   for block in module.if_data.if_data_parsed:
       if not isinstance(block, dict):
           continue
       if "ASAP1B_KWP2000" not in block:
           continue

       kwp = block["ASAP1B_KWP2000"]
       print("KWP2000 transport parameters:")

       # TP_BLOB contains baud rates, timing, SERAM, checksum config
       if "TP_BLOB" in kwp:
           tp = kwp["TP_BLOB"]
           print(f"  TP_BLOB: {tp}")

       # SOURCE blocks describe measurement channels
       if "SOURCE" in kwp:
           sources = kwp["SOURCE"]
           if not isinstance(sources, list):
               sources = [sources]
           for src in sources:
               print(f"  SOURCE: {src}")

Accessing raw IF_DATA text
~~~~~~~~~~~~~~~~~~~~~~~~~~

When the AML description is missing or you need the verbatim text:

.. code-block:: python

   from pya2l import DB
   from pya2l.api.inspect import Measurement

   session = DB().open_create("engine_ecu.a2l")
   meas = Measurement.get(session, "EngineSpeed")

   # Raw text of each IF_DATA block
   for raw_obj in meas.if_data.if_data_raw:
       print("--- raw IF_DATA text ---")
       print(raw_obj.raw)
       print("------------------------")

Combining parsed + raw for diagnostics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A typical diagnostic use-case: log both the parsed tree (for automated
processing) and the original text (for human review):

.. code-block:: python

   import json
   from pya2l import DB
   from pya2l.api.inspect import Module

   session = DB().open_create("my_project.a2l")
   module = Module(session)

   report = []
   for meas in module.measurement.query():
       ifd = meas.if_data
       if not ifd.if_data_parsed:
           continue
       entry = {
           "name": meas.name,
           "parsed": ifd.if_data_parsed,
           "raw_texts": [obj.raw for obj in ifd.if_data_raw],
           "flatmap_keys": list(ifd.flatmap.keys()),
       }
       report.append(entry)

   # Write a diagnostic JSON report
   with open("ifdata_report.json", "w") as f:
       json.dump(report, f, indent=2, default=str)

   print(f"Wrote {len(report)} IF_DATA entries to ifdata_report.json")

Manual parsing with IfDataParser
--------------------------------

If you have raw IF_DATA text from an external source (not from a parsed
A2L), you can use ``IfDataParser`` directly.  This requires a session
whose AML schema has been loaded (i.e., the A2L file contained a
``/begin A2ML … /end A2ML`` block):

.. code-block:: python

   from pya2l import DB
   from pya2l.aml.ifdata_parser import IfDataParser

   db = DB()
   session = db.open_create("ASAP2_Demo_V161.a2l")

   # Create the parser (reads AML from the session)
   parser = IfDataParser(session)

   # Parse a raw IF_DATA snippet
   raw_text = """/begin IF_DATA XCP
       /begin SEGMENT 0x01 0x02 0x00 0x00 0x00
           /begin CHECKSUM XCP_ADD_44
               MAX_BLOCK_SIZE 0xFFFF
               EXTERNAL_FUNCTION ""
           /end CHECKSUM
           /begin PAGE 0x01
               ECU_ACCESS_WITH_XCP_ONLY
               XCP_READ_ACCESS_WITH_ECU_ONLY
               XCP_WRITE_ACCESS_NOT_ALLOWED
           /end PAGE
       /end SEGMENT
   /end IF_DATA"""

   result = parser.parse(raw_text)
   print(result)

.. note::

   ``IfDataParser`` requires a valid AML schema in the database.  If
   no ``/begin A2ML`` block was present in the original A2L,
   ``session.parse_ifdata()`` returns an empty list and the IfData
   object will have ``if_data_parsed == []``.

Using setup_ifdata_parser on the session
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can also set up IF_DATA parsing at the session level, which is what
the inspect API does internally:

.. code-block:: python

   from pya2l import DB

   db = DB()
   session = db.open_existing("ASAP2_Demo_V161")

   # Initialize the IF_DATA parser for this session
   session.setup_ifdata_parser(loglevel="DEBUG")

   # Now session.parse_ifdata() is available
   import pya2l.model as model
   meas_obj = session.query(model.Measurement).filter_by(name="SomeMeasurement").first()
   if meas_obj:
       parsed = session.parse_ifdata(meas_obj.if_data)
       print(parsed)

Empty IF_DATA and edge cases
-----------------------------

Not all entities have IF_DATA, and not all A2L files contain AML
schemas.  The ``IfData`` object handles these gracefully:

.. code-block:: python

   from pya2l import DB
   from pya2l.api.inspect import Measurement

   session = DB().open_create("simple_file.a2l")
   meas = Measurement.get(session, "SomeSignal")

   ifd = meas.if_data

   # No IF_DATA blocks → empty lists
   if not ifd.if_data_parsed:
       print("No parsed IF_DATA available")

   if not ifd.if_data_raw:
       print("No raw IF_DATA blocks")

   # flatmap is an empty dict
   assert ifd.flatmap == {} or len(ifd.flatmap) == 0

   # Safe to iterate — no exceptions
   for key, vals in ifd.flatmap.items():
       print(key, vals)

Best practices
--------------

1. **Check ``if_data_parsed`` first**: It's the convenient, structured
   representation.  Fall back to ``if_data_raw`` only when you need the
   original text or the AML-based parsing is unavailable.

2. **Use ``flatmap`` for tag-based look-ups**: Instead of walking nested
   dicts manually, use ``flatmap["TAG_NAME"]`` when you know the key.

3. **Iterate over ``if_data_raw`` for debugging**: The ``.raw`` attribute
   gives you the exact text from the A2L file — invaluable when the
   parsed structure looks unexpected.

4. **Guard for empty data**: Always check ``if ifd.if_data_parsed:``
   before accessing elements.  Empty IfData objects are normal and
   frequent.

5. **AML is required for parsing**: Without an AML schema in the A2L
   file, ``if_data_parsed`` will be empty even if raw IF_DATA blocks
   exist.  Use ``if_data_raw`` in that case.
