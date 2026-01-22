import pytest

from pya2l.a2lparser import A2LParser
from pya2l.api.inspect import (
    AxisPts,
    Blob,
    CompuMethod,
    FilteredList,
    Function,
    Group,
    Measurement,
    MemoryType,
    ModCommon,
    ModPar,
    NoCompuMethod,
    NoModCommon,
    PrgTypeLayout,
    PrgTypeSegment,
    Project,
    RecordLayout,
    SegmentAttributeType,
    Transformer,
    TypedefStructure,
    Unit,
    UserRights,
    VariantCoding,
)


@pytest.fixture
def parser():
    return A2LParser()


@pytest.fixture
def db(parser, tmp_path, request):
    import hashlib

    a2l_content = request.param
    h = hashlib.md5(a2l_content.encode("latin-1")).hexdigest()[:8]
    a2l_file = tmp_path / f"t_{h}.a2l"
    a2l_file.write_text(a2l_content, encoding="latin-1")
    database = parser.parse(str(a2l_file), in_memory=True)
    return database


MEASUREMENT_BASIC_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
    /begin MEASUREMENT
        N /* name */
        "Engine speed" /* long identifier */
        UWORD /* datatype */
        NO_COMPU_METHOD /* conversion */
        2 /* resolution */
        2.5 /* accuracy */
        120.0 /* lower limit */
        8400.0 /* upper limit */
    /end MEASUREMENT
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [MEASUREMENT_BASIC_A2L], indirect=True)
def test_measurement_basic(db):
    meas = Measurement(db.session, "N")
    assert meas.name == "N"
    assert meas.longIdentifier == "Engine speed"
    assert meas.datatype == "UWORD"
    assert meas.resolution == 2
    assert meas.accuracy == 2.5
    assert meas.lowerLimit == 120
    assert meas.upperLimit == 8400.0
    assert meas.annotations == []
    assert meas.arraySize is None
    assert meas.bitMask is None
    assert meas.compuMethod.conversionType == "NO_COMPU_METHOD"


MEASUREMENT_FULL_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
    /begin COMPU_METHOD Velocity
        "conversion method for velocity"
        RAT_FUNC
        "%6.2"
        "km/h"
        COEFFS 0 100 0 0 0 1
    /end COMPU_METHOD

    /begin MEASUREMENT
        N /* name */
        "Engine speed" /* long identifier */
        UWORD /* datatype */
        Velocity /* conversion */
        2 /* resolution */
        2.5 /* accuracy */
        120.0 /* lower limit */
        8400.0 /* upper limit */
        /begin ANNOTATION
            ANNOTATION_LABEL "ASAM Workinggroup"
            ANNOTATION_ORIGIN "Python Universe"
            /begin ANNOTATION_TEXT
                "Test the A2L annotation"
                "Another line"
            /end ANNOTATION_TEXT
        /end ANNOTATION
        ARRAY_SIZE 8 /* array of 8 values */
        BIT_MASK 0x0FFF
        /begin BIT_OPERATION
            RIGHT_SHIFT 4 /*4 positions*/
            SIGN_EXTEND
        /end BIT_OPERATION
        BYTE_ORDER MSB_FIRST
        DISCRETE
        DISPLAY_IDENTIFIER load_engine
        ECU_ADDRESS 0xcafebabe
        ECU_ADDRESS_EXTENSION 42
        ERROR_MASK 0x00000001
        FORMAT "%4.2f"
        /begin FUNCTION_LIST
            ID_ADJUSTM
            FL_ADJUSTM
        /end FUNCTION_LIST
        LAYOUT ROW_DIR
        MATRIX_DIM  2   4   3
        MAX_REFRESH 3 15 /* 15 msec */
        PHYS_UNIT "mph"
        READ_WRITE
        REF_MEMORY_SEGMENT Data2
        SYMBOL_LINK "VehicleSpeed" /* Symbol name */
                4711
        /begin VIRTUAL
            PHI_BASIS
            PHI_CORR
        /end VIRTUAL
    /end MEASUREMENT
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [MEASUREMENT_FULL_A2L], indirect=True)
def test_measurement_full_featured(db):
    meas = Measurement(db.session, "N")
    assert meas.name == "N"
    assert meas.longIdentifier == "Engine speed"
    assert meas.datatype == "UWORD"
    assert meas.resolution == 2
    assert meas.accuracy == 2.5
    assert meas.lowerLimit == 120
    assert meas.upperLimit == 8400.0
    assert meas.arraySize == 8
    assert meas.bitMask == 0x0FFF
    assert meas.annotations[0].label == "ASAM Workinggroup"
    assert meas.annotations[0].origin == "Python Universe"
    assert meas.annotations[0].text == ["Test the A2L annotation", "Another line"]
    assert meas.bitOperation == {"amount": 4, "direction": "R", "sign_extend": True}
    assert meas.byteOrder == "MSB_FIRST"
    assert meas.discrete
    assert meas.displayIdentifier == "load_engine"
    assert meas.ecuAddress == 0xCAFEBABE
    assert meas.ecuAddressExtension == 42
    assert meas.errorMask == 1
    assert meas.format == "%4.2f"
    assert meas.functionList == ["ID_ADJUSTM", "FL_ADJUSTM"]
    assert meas.layout == "ROW_DIR"
    assert meas.matrixDim.x == 2
    assert meas.matrixDim.y == 4
    assert meas.matrixDim.z == 3
    assert meas.maxRefresh.rate == 15
    assert meas.maxRefresh.scalingUnit == 3
    assert meas.physUnit == "mph"
    assert meas.readWrite
    assert meas.refMemorySegment == "Data2"
    assert meas.symbolLink.offset == 4711
    assert meas.symbolLink.symbolLink == "VehicleSpeed"
    assert meas.virtual == ["PHI_BASIS", "PHI_CORR"]
    assert meas.compuMethod.conversionType == "RAT_FUNC"
    assert meas.compuMethod.unit == "km/h"
    assert meas.compuMethod.format == "%6.2"
    assert meas.compuMethod.longIdentifier == "conversion method for velocity"
    assert meas.compuMethod.coeffs.a == 0.0
    assert meas.compuMethod.coeffs.b == 100.0
    assert meas.compuMethod.coeffs.f == 1.0


MOD_PAR_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE testModule ""
    /begin MOD_PAR "Note: Provisional release for test purposes only!"
        VERSION "Test version of 01.02.1994"
        ADDR_EPK 0x45678
        EPK     "EPROM identifier test"
        SUPPLIER "M&K GmbH Chemnitz"
        CUSTOMER "LANZ-Landmaschinen"
        CUSTOMER_NO "0123456789"
        USER "A.N.Wender"
        PHONE_NO "09951 56456"
        ECU "Engine control"
        CPU_TYPE "Motorola 0815"
        NO_OF_INTERFACES 2
        /begin MEMORY_SEGMENT ext_Ram
            "external RAM"
            DATA
            RAM
            EXTERN
            0x30000
            0x1000
            -1 -1 -1 -1 -1
        /end MEMORY_SEGMENT
        /begin MEMORY_LAYOUT PRG_RESERVED
            0x0000
            0x0400
            -1 -1 -1 -1 -1
        /end MEMORY_LAYOUT
        /begin MEMORY_LAYOUT PRG_CODE
            0x0400
            0x3C00
            -1 -1 -1 -1 -1
        /end MEMORY_LAYOUT
        /begin MEMORY_LAYOUT PRG_DATA
            0x4000
            0x5800
            -1 -1 -1 -1 -1
        /end MEMORY_LAYOUT
        SYSTEM_CONSTANT "CONTROLLERx constant1" "0.33"
        SYSTEM_CONSTANT "CONTROLLERx constant2" "2.79"
    /end MOD_PAR
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [MOD_PAR_A2L], indirect=True)
def test_mod_par_full_featured(db):
    mp = ModPar(db.session, module_name="testModule")
    assert mp.comment == "Note: Provisional release for test purposes only!"
    assert mp.version == "Test version of 01.02.1994"
    assert mp.addrEpk[0] == 0x45678
    assert mp.epk == "EPROM identifier test"
    assert mp.supplier == "M&K GmbH Chemnitz"
    assert mp.customer == "LANZ-Landmaschinen"
    assert mp.customerNo == "0123456789"
    assert mp.user == "A.N.Wender"
    assert mp.phoneNo == "09951 56456"
    assert mp.ecu == "Engine control"
    assert mp.cpu == "Motorola 0815"
    assert mp.noOfInterfaces == 2

    ms = mp.memorySegments[0]
    assert ms.name == "ext_Ram"
    assert ms.address == 0x30000
    assert ms.size == 0x1000

    sc = mp.systemConstants
    assert sc["CONTROLLERx constant1"] == 0.33
    assert sc["CONTROLLERx constant2"] == 2.79


COMPU_METHOD_TAB_VERB_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
    /begin COMPU_METHOD MyTabVerb
        "Verbal conversion"
        TAB_VERB
        "%s"
        "unit"
        COMPU_TAB_REF MyVtab
    /end COMPU_METHOD

    /begin COMPU_VTAB MyVtab
        "Test Table"
        TAB_VERB
        2
        0 "Off"
        1 "On"
        DEFAULT_VALUE "Unknown"
    /end COMPU_VTAB
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [COMPU_METHOD_TAB_VERB_A2L], indirect=True)
def test_compu_method_tab_verb(db):
    cm = CompuMethod(db.session, "MyTabVerb")
    assert cm.conversionType == "TAB_VERB"
    assert cm.tab_verb.name == "MyVtab"
    assert cm.tab_verb.default_value == "Unknown"
    assert cm.int_to_physical(0) == "Off"
    assert cm.int_to_physical(1) == "On"
    assert cm.int_to_physical(2) == "Unknown"


GROUP_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
    /begin GROUP Group1 "Test Group"
        /begin REF_CHARACTERISTIC Char1 /end REF_CHARACTERISTIC
        /begin REF_MEASUREMENT Meas1 /end REF_MEASUREMENT
        /begin SUB_GROUP SubGroup1 /end SUB_GROUP
    /end GROUP
    /begin GROUP SubGroup1 "Sub Group"
    /end GROUP
    /begin CHARACTERISTIC Char1 "" VALUE 0x1000 RL 0 CM 0 100 /end CHARACTERISTIC
    /begin MEASUREMENT Meas1 "" UBYTE CM 1 100 0 100 /end MEASUREMENT
    /begin RECORD_LAYOUT RL FNC_VALUES 1 UBYTE COLUMN_DIR DIRECT /end RECORD_LAYOUT
    /begin COMPU_METHOD CM "" IDENTICAL "%d" "" /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [GROUP_A2L], indirect=True)
def test_group(db):
    group = Group(db.session, "Group1")
    assert group.name == "Group1"
    assert group.longIdentifier == "Test Group"

    char_names = [c.name for c in group.characteristics]
    assert "Char1" in char_names

    meas_names = [m.name for m in group.measurements]
    assert "Meas1" in meas_names

    subgroup_names = [s.name for s in group.subgroups]
    assert "SubGroup1" in subgroup_names


CHARACTERISTIC_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
    /begin CHARACTERISTIC Char1 "Test Characteristic"
        VALUE 0x1000 RL_VAL 0 CM_IDENT 0 100
        ECU_ADDRESS_EXTENSION 0x11
        FORMAT "%6.2"
        PHYS_UNIT "V"
    /end CHARACTERISTIC
    /begin RECORD_LAYOUT RL_VAL FNC_VALUES 1 UWORD COLUMN_DIR DIRECT /end RECORD_LAYOUT
    /begin COMPU_METHOD CM_IDENT "" IDENTICAL "%d" "" /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [CHARACTERISTIC_A2L], indirect=True)
def test_characteristic_basic(db):
    from pya2l.api.inspect import Characteristic

    char = Characteristic(db.session, "Char1")
    assert char.name == "Char1"
    assert char.longIdentifier == "Test Characteristic"
    assert char.address == 0x1000
    assert char.ecuAddressExtension == 0x11
    assert char.format == "%6.2"
    assert char.physUnit == "V"
    assert char.compuMethod.conversionType == "IDENTICAL"


TYPEDEF_STRUCTURE_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
    /begin TYPEDEF_STRUCTURE StructType "Test Structure Type" 0x10
        /begin STRUCTURE_COMPONENT Comp1 ULONG 0x0 /end STRUCTURE_COMPONENT
        /begin STRUCTURE_COMPONENT Comp2 FLOAT32_IEEE 0x4 /end STRUCTURE_COMPONENT
    /end TYPEDEF_STRUCTURE
    /begin INSTANCE Inst1 "Instance of StructType" StructType 0x2000
    /end INSTANCE
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [TYPEDEF_STRUCTURE_A2L], indirect=True)
def test_typedef_structure(db):
    ts = TypedefStructure(db.session, "StructType")
    assert ts.name == "StructType"
    assert ts.longIdentifier == "Test Structure Type"

    # TypedefStructure.components() returns a list of StructureComponent objects
    components = {c.name: c for c in ts.components}
    assert "Comp1" in components
    assert "Comp2" in components

    from pya2l.api.inspect import Instance

    inst = Instance(db.session, "Inst1")
    assert inst.name == "Inst1"
    assert inst.address == 0x2000


COMPU_METHOD_LINEAR_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
    /begin COMPU_METHOD LinearMethod
        "Linear conversion"
        LINEAR
        "%6.2"
        "V"
        COEFFS_LINEAR 2.0 1.0
    /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [COMPU_METHOD_LINEAR_A2L], indirect=True)
def test_compu_method_linear(db):
    cm = CompuMethod(db.session, "LinearMethod")
    assert cm.conversionType == "LINEAR"
    assert cm.coeffs_linear.a == 2.0
    assert cm.coeffs_linear.b == 1.0
    # physical = a * internal + b = 2 * 10 + 1 = 21
    assert cm.int_to_physical(10) == 21.0
    # internal = (physical - b) / a = (21 - 1) / 2 = 10
    assert cm.physical_to_int(21) == 10.0


MOD_COMMON_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
    /begin MOD_COMMON "Common module data"
        BYTE_ORDER MSB_FIRST
        ALIGNMENT_BYTE 1
        ALIGNMENT_WORD 2
        ALIGNMENT_LONG 4
        ALIGNMENT_FLOAT32_IEEE 4
        ALIGNMENT_FLOAT64_IEEE 8
        DATA_SIZE 100
    /end MOD_COMMON
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [MOD_COMMON_A2L], indirect=True)
def test_mod_common(db):
    mc = ModCommon(db.session)
    assert mc.comment == "Common module data"
    assert mc.byteOrder == "MSB_FIRST"
    assert mc.dataSize == 100
    # Alignment object should have correct values
    assert mc.alignment.get("BYTE") == 1
    assert mc.alignment.get("WORD") == 2
    assert mc.alignment.get("LONG") == 4
    assert mc.alignment.get("FLOAT32_IEEE") == 4
    assert mc.alignment.get("FLOAT64_IEEE") == 8

    # Test align method
    assert mc.alignment.align("WORD", 1) == 2
    assert mc.alignment.align("LONG", 1) == 4
    assert mc.alignment.align("BYTE", 1) == 1


AXIS_PTS_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
    /begin AXIS_PTS Axis1 "Test Axis" 0x1000 InputQty RL_AXIS 0.0 CM_IDENT 10 0.0 100.0
        BYTE_ORDER MSB_FIRST
        /begin ANNOTATION
            ANNOTATION_LABEL "Label"
            /begin ANNOTATION_TEXT "Text" /end ANNOTATION_TEXT
        /end ANNOTATION
    /end AXIS_PTS
    /begin RECORD_LAYOUT RL_AXIS
        AXIS_PTS_X 1 UWORD INDEX_INCR DIRECT
    /end RECORD_LAYOUT
    /begin COMPU_METHOD CM_IDENT "" IDENTICAL "%d" "" /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [AXIS_PTS_A2L], indirect=True)
def test_axis_pts(db):
    axis = AxisPts(db.session, "Axis1")
    assert axis.name == "Axis1"
    assert axis.address == 0x1000
    assert axis.inputQuantity == "InputQty"
    assert axis.maxAxisPoints == 10
    assert axis.lowerLimit == 0.0
    assert axis.upperLimit == 100.0
    assert axis.byteOrder == "MSB_FIRST"
    assert len(axis.annotations) == 1
    assert axis.annotations[0].label == "Label"

    # Check record layout components
    assert "axis_pts" in axis.record_layout_components["position"][0][0]


FUNCTION_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
    /begin FUNCTION Func1 "Test Function"
        /begin IN_MEASUREMENT Meas1 /end IN_MEASUREMENT
        /begin OUT_MEASUREMENT Meas2 /end OUT_MEASUREMENT
        /begin DEF_CHARACTERISTIC Char1 /end DEF_CHARACTERISTIC
        /begin SUB_FUNCTION SubFunc1 /end SUB_FUNCTION
    /end FUNCTION
    /begin FUNCTION SubFunc1 "Sub Function" /end FUNCTION
    /begin MEASUREMENT Meas1 "" UBYTE CM 1 100 0 100 /end MEASUREMENT
    /begin MEASUREMENT Meas2 "" UBYTE CM 1 100 0 100 /end MEASUREMENT
    /begin CHARACTERISTIC Char1 "" VALUE 0x1000 RL 0 CM 0 100 /end CHARACTERISTIC
    /begin RECORD_LAYOUT RL FNC_VALUES 1 UBYTE COLUMN_DIR DIRECT /end RECORD_LAYOUT
    /begin COMPU_METHOD CM "" IDENTICAL "%d" "" /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [FUNCTION_A2L], indirect=True)
def test_function(db):
    func = Function(db.session, "Func1")
    assert func.name == "Func1"
    assert func.longIdentifier == "Test Function"

    assert "Meas1" in [m.name for m in func.inMeasurements]
    assert "Meas2" in [m.name for m in func.outMeasurements]
    assert "Char1" in [c.name for c in func.defCharacteristics]
    assert "SubFunc1" in [f.name for f in func.subFunctions]


UNIT_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
    /begin UNIT Unit1 "Test Unit" "U" PHYSICAL
        SI_EXPONENTS 1 0 0 0 0 0 0
        /begin UNIT_CONVERSION 1.0 0.0 /end UNIT_CONVERSION
    /end UNIT
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [UNIT_A2L], indirect=True)
def test_unit(db):
    unit = Unit(db.session, "Unit1")
    assert unit.name == "Unit1"
    assert unit.longIdentifier == "Test Unit"
    assert unit.display == "U"
    assert unit.type == "PHYSICAL"
    assert unit.si_exponents.length == 1
    assert unit.unit_conversion.gradient == 1.0


BLOB_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
    /begin BLOB Blob1 "Test Blob" 0x1000 100
        CALIBRATION_ACCESS READ_ONLY
    /end BLOB
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [BLOB_A2L], indirect=True)
def test_blob(db):
    blob = Blob(db.session, "Blob1")
    assert blob.name == "Blob1"
    assert blob.address == 0x1000
    assert blob.length == 100
    assert blob.calibration_access == "READ_ONLY"


TRANSFORMER_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
    /begin TRANSFORMER Trans1 "1.0" "lib32.dll" "lib64.dll" 100 ON_CHANGE NO_REVERSE
        /begin TRANSFORMER_IN_OBJECTS Meas1 /end TRANSFORMER_IN_OBJECTS
        /begin TRANSFORMER_OUT_OBJECTS Meas2 /end TRANSFORMER_OUT_OBJECTS
    /end TRANSFORMER
    /begin MEASUREMENT Meas1 "" UBYTE CM 1 100 0 100 /end MEASUREMENT
    /begin MEASUREMENT Meas2 "" UBYTE CM 1 100 0 100 /end MEASUREMENT
    /begin COMPU_METHOD CM "" IDENTICAL "%d" "" /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""


@pytest.mark.parametrize("db", [TRANSFORMER_A2L], indirect=True)
def test_transformer(db):
    trans = Transformer(db.session, "Trans1")
    assert trans.name == "Trans1"
    assert trans.version == "1.0"
    assert trans.dllname32 == "lib32.dll"
    assert trans.timeout == 100
    assert trans.trigger == "ON_CHANGE"
    assert "Meas1" in trans.transformer_in_objects
    assert "Meas2" in trans.transformer_out_objects


@pytest.mark.parametrize(
    "db",
    ["""
ASAP2_VERSION 1 71
/begin PROJECT Project1 "Test Project"
  /begin MODULE Module1 "Test Module" /end MODULE
/end PROJECT
"""],
    indirect=True,
)
def test_project(db):
    proj = Project(db.session)
    assert proj.name == "Project1"
    assert proj.longIdentifier == "Test Project"
    assert proj.module[0].name == "Module1"


@pytest.mark.parametrize(
    "db",
    ["""
ASAP2_VERSION 1 71
/begin PROJECT Project1 "Test Project"
  /begin MODULE Module1 "Test Module" /end MODULE
/end PROJECT
"""],
    indirect=True,
)
def test_module(db):
    from pya2l.api.inspect import Module

    module = Module(db.session, "Module1")
    assert module.name == "Module1"
    assert module.longIdentifier == "Test Module"


def test_enums():
    assert PrgTypeLayout.PRG_CODE == 0
    assert PrgTypeSegment.DATA == 2
    assert MemoryType.EEPROM == 0
    assert SegmentAttributeType.INTERN == 0


def test_no_compu_method():
    ncm = NoCompuMethod()
    assert ncm.name is None
    assert ncm.conversionType == "NO_COMPU_METHOD"
    assert ncm.coeffs == []
    assert ncm.int_to_physical(10) == 10


def test_no_mod_common():
    nmc = NoModCommon()
    assert nmc.comment is None
    assert nmc.alignment.align("BYTE", 1) == 1


@pytest.mark.parametrize(
    "db",
    ["""
ASAP2_VERSION 1 71
/begin PROJECT Project1 ""
  /begin MODULE Module1 ""
  /end MODULE
/end PROJECT
"""],
    indirect=True,
)
def test_filtered_list(db):
    # FilteredList needs session, association, klass, and attr_name (default="name")
    from pya2l import model

    fl = FilteredList(db.session, [], model.Measurement, "name")
    # FilteredList doesn't have __len__, but we can check query results
    assert len(list(fl.query())) == 0


@pytest.mark.parametrize(
    "db",
    ["""
ASAP2_VERSION 1 71
/begin PROJECT Project1 ""
  /begin MODULE Module1 ""
    /begin MOD_PAR ""
        /begin MEMORY_LAYOUT PRG_CODE 0x0 0x100 0 0 0 0 0 /end MEMORY_LAYOUT
        /begin MEMORY_SEGMENT MS1 "" DATA FLASH INTERN 0x0 0x100 -1 -1 -1 -1 -1 /end MEMORY_SEGMENT
    /end MOD_PAR
    /begin RECORD_LAYOUT RL1
        FNC_VALUES 1 UBYTE COLUMN_DIR DIRECT
    /end RECORD_LAYOUT
  /end MODULE
/end PROJECT
"""],
    indirect=True,
)
def test_mod_par_extended(db):
    from pya2l.api.inspect import ModPar

    # ModPar constructor: def __init__(self, session, name=None, module_name: str = None)
    mp = ModPar(db.session, name="", module_name="Module1")
    assert mp is not None
    assert len(mp.memoryLayouts) == 1
    assert mp.memoryLayouts[0].prgType.name == "PRG_CODE"
    assert mp.memoryLayouts[0].address == 0x0
    assert mp.memoryLayouts[0].size == 0x100

    assert len(mp.memorySegments) == 1
    assert mp.memorySegments[0].name == "MS1"
    assert mp.memorySegments[0].prgType.name == "DATA"
    assert mp.memorySegments[0].memoryType.name == "FLASH"
    assert mp.memorySegments[0].attribute.name == "INTERN"


@pytest.mark.parametrize(
    "db",
    ["""
ASAP2_VERSION 1 71
/begin PROJECT Project1 ""
  /begin MODULE Module1 ""
    /begin RECORD_LAYOUT RL1
        FNC_VALUES 1 UBYTE COLUMN_DIR DIRECT
    /end RECORD_LAYOUT
  /end MODULE
/end PROJECT
"""],
    indirect=True,
)
def test_record_layout(db):
    rl = RecordLayout(db.session, "RL1")
    assert rl.name == "RL1"
    assert rl.fncValues.data_type == "UBYTE"
    assert rl.fncValues.indexMode == "COLUMN_DIR"
    assert rl.fncValues.addresstype == "DIRECT"


@pytest.mark.parametrize(
    "db",
    ["""
ASAP2_VERSION 1 71
/begin PROJECT Project1 ""
  /begin MODULE Module1 ""
    /begin CHARACTERISTIC C1 "" VALUE 0x0 RL1 0 CM 0 100
        /begin SYMBOL_LINK "symbol1" 0 /end SYMBOL_LINK
    /end CHARACTERISTIC
    /begin RECORD_LAYOUT RL1 FNC_VALUES 1 UBYTE COLUMN_DIR DIRECT /end RECORD_LAYOUT
    /begin COMPU_METHOD CM "" IDENTICAL "%d" "" /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""],
    indirect=True,
)
def test_characteristic_extended(db):
    from pya2l.api.inspect import Characteristic

    char = Characteristic(db.session, "C1")
    assert char.symbolLink.symbolLink == "symbol1"


@pytest.mark.parametrize(
    "db",
    ["""
ASAP2_VERSION 1 71
/begin PROJECT Project1 ""
  /begin MODULE Module1 ""
    /begin VARIANT_CODING
        VAR_NAMING NUMERIC
        /begin VAR_CRITERION VC1 "" "val1" /end VAR_CRITERION
        /begin VAR_CHARACTERISTIC VCH1 VC1 /end VAR_CHARACTERISTIC
    /end VARIANT_CODING
  /end MODULE
/end PROJECT
"""],
    indirect=True,
)
def test_variant_coding(db):
    vc = VariantCoding(db.session, module_name="Module1")
    assert vc.naming == "NUMERIC"
    assert "VC1" in vc.criterions
    assert vc.criterions["VC1"].name == "VC1"
    assert "VCH1" in vc.characteristics
    assert vc.characteristics["VCH1"].name == "VCH1"


@pytest.mark.parametrize(
    "db",
    ["""
ASAP2_VERSION 1 71
/begin PROJECT Project1 ""
  /begin MODULE Module1 ""
    /begin USER_RIGHTS "user1"
        /begin READ_ONLY /end READ_ONLY
    /end USER_RIGHTS
  /end MODULE
/end PROJECT
"""],
    indirect=True,
)
def test_user_rights(db):
    ur = UserRights(db.session, "user1")
    assert ur.userLevelId == "user1"
    assert ur.read_only is True
