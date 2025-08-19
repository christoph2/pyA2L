pyA2L
=====

[![Code Climate](https://codeclimate.com/github/christoph2/pyA2L/badges/gpa.svg)](https://codeclimate.com/github/christoph2/pyA2L)
[![Coverage Status](https://coveralls.io/repos/github/christoph2/pyA2L/badge.svg?branch=master)](https://coveralls.io/github/christoph2/pyA2L?branch=master)
[![Build Status](https://travis-ci.org/christoph2/pyA2L.svg)](https://travis-ci.org/christoph2/pyA2L)
[![Build status](https://ci.appveyor.com/api/projects/status/2sa0ascmg0b6lbt6?svg=true)](https://ci.appveyor.com/project/christoph2/pya2l)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![GPL License](http://img.shields.io/badge/license-GPL-blue.svg)](http://opensource.org/licenses/GPL-2.0)

pyA2L is an ASAM MCD-2 MC (ASAP2) processing library for Python that turns A2L files into a convenient, queryable SQLite database and a rich Python API.

If you work with ECUs, ASAP2/A2L is the contract that describes what and how to measure or calibrate. pyA2L helps you parse once, inspect and validate programmatically, automate checks, and export back when needed — all from Python.

Contents
--------
- About ASAM MCD-2 MC (ASAP2)
- What pyA2L offers
- Installation
- Getting Started (Quickstart)
- Command-line usage
- Tips
- Examples
- Compatibility
- Project links
- Contributing
- Code of Conduct
- License
- Changelog / Release notes
- Acknowledgements

About ASAM MCD-2 MC (ASAP2)
---------------------------
ASAM MCD-2 MC, commonly referred to as ASAP2, defines a standardized description format for measurement signals and calibration parameters in Electronic Control Units (ECUs). It specifies the human‑readable A2L file that acts as a contract between ECU software and tooling so that different vendors’ tools can interpret memory, convert raw values to physical engineering units, and apply calibrations consistently.

Scope and workflow context
- ASAP2/A2L describes WHAT exists in ECU memory (addresses, data types, layouts) and HOW to interpret it (conversions, units, limits). It does not define the runtime transport; that’s typically handled by CCP or XCP.
- In practice, engineers combine an A2L with CCP/XCP to stream measurements from the ECU and to write calibration values during development, testing, and calibration.

Top‑level A2L structure (essentials)
- PROJECT → MODULE: A2L is organized into a PROJECT with one or more MODULE blocks (usually one per ECU software image).
- COMMON / MOD_PAR / MOD_COMMON: Module‑wide settings such as byte order, alignment, system constants, EPK/addresses, and global defaults.
- MEASUREMENT: Declares read‑only measurement signals with data type, ECU address, bit mask (if needed), sampling characteristics, and the conversion to physical values.
- CHARACTERISTIC: Declares calibratable data such as scalars, curves, and maps, including storage class, ECU address, record layout, default values, limits, and associated axes.
- AXIS_DESCR / AXIS_PTS: Define axis properties for curves/maps (type, points count, data type, address or reference to axis characteristics, default values).
- RECORD_LAYOUT: Describes the binary layout of calibrations in memory (order and type of elements, alignment, bit/byte order), enabling tools to read/write structured data correctly.
- UNIT: Defines engineering units and display formats; COMPU_METHOD/COMPU_TAB specify how raw ECU values become physical values.
- FUNCTION / GROUP: Provide logical grouping of measurements and characteristics and their relationships (e.g., for browsing and authorization).
- VARIANT_CODING: Describes variant handling if the ECU image contains multiple feature variants.
- IF_DATA: Vendor‑ or protocol‑specific extensions embedded in the A2L.

Data types, addresses, and memory layout
- ASAP2 supports integer and floating‑point types with explicit byte order and alignment rules; elements may be masked or bit‑positioned within a larger word.
- Addresses may be absolute or segmented/banked depending on the target; A2L captures the necessary address space info used by CCP/XCP.
- RECORD_LAYOUT is key for complex objects (CURVE/MAP) and encodes structure (e.g., axis first vs. column‑major, reserved bytes, fix‑axis handling).

From raw to physical values (conversions)
- COMPU_METHOD covers conversion formulas and formatting; common methods include:
  - IDENTICAL (no conversion), LINEAR/RATIONAL (y = (a·x + b) / (c·x + d)), LOG, and user‑defined FORMULA strings.
- COMPU_TAB / COMPU_VTAB / COMPU_VTAB_RANGE provide table‑based conversions for enumerations, lookup tables, and range‑to‑text mappings.
- Units, display formats, and value limits are part of the conversion context and are referenced by MEASUREMENTs and CHARACTERISTICs.

Axes and multidimensional calibrations
- CHARACTERISTICs may have 0D (SCALAR), 1D (CURVE), 2D/3D (MAP) and beyond; each dimension is described by an AXIS_DESCR.
- Axis types include STD_AXIS, COM_AXIS, FIX_AXIS, and RESCALE. An axis can reference another CHARACTERISTIC (axis‑points characteristic) or embed FIX_AXIS definitions.

Namespaces, includes, and modularization
- A2L supports INCLUDE of other files, and namespaces allow structuring large projects across suppliers and domains.

Versioning and compatibility
- A2L has evolved through several revisions; this project currently targets ASAP2 v1.6. Many concepts are stable across versions, but certain keywords and IF_DATA blocks are version‑specific.

For a detailed, authoritative overview of the standard, see the ASAM wiki page: https://www.asam.net/standards/detail/mcd-2-mc/wiki/

What pyA2L offers
-----------------
- Parse .a2l files and persist them as compact, queryable SQLite databases (.a2ldb) to avoid repeated parse costs.
- Programmatic access to ASAP2 entities via SQLAlchemy ORM models (MODULE, MEASUREMENT, CHARACTERISTIC, AXIS_DESCR, RECORD_LAYOUT, COMPU_METHOD/COMPU_TAB, UNIT, FUNCTION, GROUP, VARIANT_CODING, etc.).
- Rich inspection helpers in pya2l.api.inspect (e.g., Characteristic, Measurement, AxisDescr, ModPar, ModCommon) to compute shapes, axis info, allocated memory, conversions, and more.
- Validation utilities (pya2l.api.validate) to check common ASAP2 rules and project-specific consistency.
- Export .a2ldb content back to A2L text when needed.
- Building blocks for automation: reporting, quality gates, CI checks, and integration with CCP/XCP workflows.

Supported ASAP2 version: 1.6.

Why pyA2L?
----------
- Parse once, query fast: Avoid repeated parser runs by working from SQLite.
- Powerful model: Use SQLAlchemy ORM to navigate ASAP2 entities naturally.
- Beyond parsing: Inspect derived properties, validate consistency, and export back to A2L.
- Automate: Integrate with CI to enforce quality gates on A2L content.

Design highlights
-----------------
- SQLite-backed storage (.a2ldb) with SQLAlchemy models
- High-level inspection helpers in `pya2l.api.inspect`
- Validator framework in `pya2l.api.validate` yielding structured diagnostics
- Optional CLI for import/export tasks

Learn more about the standard at the ASAM website: https://www.asam.net/standards/detail/mcd-2-mc/wiki/

Installation
------------

- Via `pip` (Currently only Windows and MacOS):
    ```shell
    $ pip install pya2ldb
    ```
    **IMPORTANT**: Package-name is `pya2ldb` **NOT** `pya2l`!!!

- From Github:
    - Clone / fork / download [pyA2Ldb repository](https://github.com/christoph2/pya2l).
    - Make sure you have a working Java installation on your system, like [AdoptOpenJDK](https://adoptopenjdk.net/) or [OpenJDK](https://openjdk.java.net/).
    - Download and install ANTLR 4 (tested with 4.13.1):
        - `curl -O -C - -L https://www.antlr.org/download/antlr-4.13.1-complete.jar`
        - Add ANTLR to your CLASSPATH, e.g.: `export CLASSPATH=$CLASSPATH:~/jars/antlr-4.13.1-complete.jar` (consider adding this to `.bashrc` / `.zshrc`).
    - Run setup-script: `python setup.py develop`

Getting Started (Quickstart)
---------------------------

Parse an A2L once, work from SQLite thereafter
- Import a .a2l file and persist it as .a2ldb (SQLite):

```python
from pya2l import DB

db = DB()
session = db.import_a2l("ASAP2_Demo_V161.a2l")
# Creates ASAP2_Demo_V161.a2ldb in the working directory
```

- Open an existing .a2ldb without re-parsing:

```python
from pya2l import DB

db = DB()
session = db.open_existing("ASAP2_Demo_V161")  # extension .a2ldb is implied
```

Query with SQLAlchemy ORM
- List all measurements ordered by name with address and data type:

```python
from pya2l import DB
import pya2l.model as model

db = DB()
session = db.open_existing("ASAP2_Demo_V161")
measurements = (
    session.query(model.Measurement)
    .order_by(model.Measurement.name)
    .all()
)
for m in measurements:
    print(f"{m.name:48} {m.datatype:12} 0x{m.ecu_address.address:08x}")
```

High-level inspection helpers
- Use convenience wrappers from pya2l.api.inspect to access derived info:

```python
from pya2l import DB
from pya2l.api.inspect import Characteristic, Measurement, AxisDescr

db = DB()
session = db.open_existing("ASAP2_Demo_V161")
ch = Characteristic(session, "ASAM.C.MAP.UBYTE.IDENTICAL")
print("shape:", ch.dim().shape)
print("element size:", ch.fnc_element_size(), "bytes")
print("num axes:", ch.num_axes())

me = Measurement(session, "ASAM.M.SCALAR.UBYTE.IDENTICAL")
print("is virtual:", me.is_virtual())

axis = ch.axisDescription("X")
print("axis info:", axis.axisDescription("X"))
```

Validate your database

```python
from pya2l import DB
from pya2l.api.validate import Validator

db = DB()
session = db.open_existing("ASAP2_Demo_V161")
vd = Validator(session)
for msg in vd():  # iterate diagnostics
    # msg has fields: type (Level), category (Category), diag_code (Diagnostics), text (str)
    print(msg.type.name, msg.category.name, msg.diag_code.name, "-", msg.text)
```

Export back to A2L (optional)

```python
from pya2l import export_a2l

export_a2l("ASAP2_Demo_V161", "exported.a2l")
```

Tips
- The default file encoding for A2L import is latin-1; override via encoding= parameter if needed.
- You need a working Java and ANTLR setup when building from source; pip wheels are provided for supported platforms.
- The Python package name is pya2ldb (not pya2l).

Examples
- See pya2l/examples for sample A2L files and scripts.
- The Sphinx docs contain a fuller tutorial and how-to guides.

Create API and coverage parity
------------------------------
pyA2L offers a Creator API in pya2l.api.create to programmatically build or augment A2L content. The project’s goal is coverage parity: everything you can query via pya2l.api.inspect is intended to be creatable via pya2l.api.create.

Example: creating common entities

```python
from pya2l import DB
from pya2l.api.create import ModuleCreator
from pya2l.api.inspect import Module

# Open or create a database
session = DB().open_create("MyProject.a2l")  # or .a2ldb

mc = ModuleCreator(session)
# Create a module
mod = mc.create_module("DEMO", "Demo ECU module")

# Units and conversions
temp_unit = mc.add_unit(mod, name="degC", long_identifier="Celsius",
                        display="°C", type_str="TEMPERATURE")
ct = mc.add_compu_tab(mod, name="TAB_NOINTP_DEMO", long_identifier="Demo Tab",
                      conversion_type="TAB_NOINTP",
                      pairs=[(0, 0.0), (100, 1.0)], default_numeric=0.0)

# Frames and transformers
fr = mc.add_frame(mod, name="FRAME1", long_identifier="Demo frame",
                  scaling_unit=1, rate=10, measurements=["ENGINE_SPEED"])
tr = mc.add_transformer(mod, name="TR1", version="1.0",
                        dllname32="tr32.dll", dllname64="tr64.dll",
                        timeout=1000, trigger="ON_CHANGE", reverse="NONE",
                        in_objects=["ENGINE_SPEED"], out_objects=["SPEED_PHYS"])

# Typedefs and instances
ts = mc.add_typedef_structure(mod, name="TSig", long_identifier="Signal",
                              size=8)
mc.add_structure_component(ts, name="raw", type_ref="UWORD", offset=0)
inst = mc.add_instance(mod, name="S1", long_identifier="Inst of TSig",
                       type_name="TSig", address=0x1000)

# Verify with inspect helpers
mi = Module(session)
print("#frames:", len(list(mi.frame.query())))
print("#compu tabs:", len(list(mi.compu_tab.query())))
```

See pya2l/examples/create_quickstart.py for a more complete example.

Command-line usage
------------------
A small CLI is provided as a console script named `a2ldb-imex`:

```bash
# Show version
$ a2ldb-imex -V

# Import an A2L (creates .a2ldb next to the input or in CWD with -L)
$ a2ldb-imex -i path/to/file.a2l

# Import with explicit encoding and create DB in current directory
$ a2ldb-imex -i path/to/file.a2l -E latin-1 -L

# Export an .a2ldb back to A2L text (stdout by default or -o file)
$ a2ldb-imex -e path/to/file.a2ldb -o exported.a2l
```

Compatibility
-------------
- Python: 3.10 – 3.13 (per pyproject classifiers)
- Platforms: Prebuilt wheels are published for selected platforms. From source, Windows/macOS are supported; Linux may require building native extensions.
- ASAP2: Version 1.6

Project links
-------------
- Source code: https://github.com/christoph2/pyA2L
- Issue tracker: https://github.com/christoph2/pyA2L/issues
- PyPI: https://pypi.org/project/pya2ldb/
- Documentation (source): ./docs

Contributing
------------
Contributions are welcome! Please open an issue to discuss significant changes before submitting a PR. See the existing tests under `pya2l/tests` and examples under `pya2l/examples` to get started.

Code of Conduct
---------------
This project adheres to a Code of Conduct. By participating, you are expected to uphold it. See CODE_OF_CONDUCT.md.

License
-------
GPL-2.0. See LICENSE for details.

Changelog / Release notes
-------------------------
See GitHub Releases: https://github.com/christoph2/pyA2L/releases

Acknowledgements
----------------
- Based on and inspired by the ASAM MCD-2 MC (ASAP2) standard.
- Part of the pySART ecosystem.

Mining fixes and feature ideas from GitHub issues
-------------------------------------------------
You can generate a categorized report of “Fix candidates” and “Feature ideas” from the GitHub issue tracker:

- Run from your shell (requires internet access):

```bash
# Basic: list open issues for the default repo
python -m pya2l.scripts.issues_report

# Specify repository and write to a Markdown file
python -m pya2l.scripts.issues_report --repo christoph2/pyA2L --state open --out issues_report.md

# Use a GitHub token to increase rate limits
GITHUB_TOKEN=ghp_your_token python -m pya2l.scripts.issues_report
```

The script groups issues by labels:
- Fix candidates: bug, regression, defect
- Feature ideas: enhancement, feature, idea, improvement
- Others: Uncategorized

----------

**pyA2L is part of pySART (Simplified AUTOSAR-Toolkit for Python).**
----------
