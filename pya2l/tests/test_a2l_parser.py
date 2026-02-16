from pathlib import Path

import pytest

from pya2l import A2L_TEMPLATE, _render_a2l, model
from pya2l.a2lparser import A2LParser
from pya2l.templates import doTemplateFromText


MINIMAL_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT MiniProject "Minimal A2L Project"
  /begin MODULE MiniModule "Minimal Module"
  /end MODULE
/end PROJECT
"""

CHARACTERISTIC_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT CharProject "Characteristic Test"
  /begin MODULE CharModule "Module with Characteristics"
    /begin CHARACTERISTIC
      MyChar
      "Test Characteristic"
      VALUE
      0x1234
      RecordLayout_Value
      0
      CompuMethod_Identical
      0 100
    /end CHARACTERISTIC

    /begin RECORD_LAYOUT RecordLayout_Value
      FNC_VALUES 1 Int16_Intel COLUMN_DIR DIRECT
    /end RECORD_LAYOUT

    /begin COMPU_METHOD CompuMethod_Identical
      "Identical mapping"
      IDENTICAL
      "%6.3"
      "unit"
    /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""

MEASUREMENT_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT MeasProject "Measurement Test"
  /begin MODULE MeasModule "Module with Measurements"
    /begin MEASUREMENT
      MyMeas
      "Test Measurement"
      UBYTE
      CompuMethod_Identical
      1
      100
      0 100
      ECU_ADDRESS 0x5678
    /end MEASUREMENT

    /begin COMPU_METHOD CompuMethod_Identical
      "Identical mapping"
      IDENTICAL
      "%6.3"
      "unit"
    /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""

COMPU_VTAB_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT TabProject "CompuVtab Test"
  /begin MODULE TabModule "Module with CompuVtabs"
    /begin COMPU_METHOD CompuMethod_Vtab
      "Vtab mapping"
      TAB_VERB
      "%6.3"
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

AXIS_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT AxisProject "Axis Test"
  /begin MODULE AxisModule "Module with Axis"
    /begin AXIS_PTS
      MyAxis "Test Axis" 0x2000 InputQuantity_Ident RecordLayout_Ident 0.0 CompuMethod_Ident 5 0.0 100.0
    /end AXIS_PTS

    /begin RECORD_LAYOUT RecordLayout_Ident
      AXIS_PTS_X 1 Int16_Intel INDEX_INCR DIRECT
    /end RECORD_LAYOUT

    /begin COMPU_METHOD CompuMethod_Ident
      "Identical mapping"
      IDENTICAL
      "%6.3"
      "unit"
    /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""

IFDATA_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT IfDataProject "IfData Test"
  /begin MODULE IfDataModule "Module with IfData"
    /begin CHARACTERISTIC
      CharWithIfData
      "Char with IfData"
      VALUE 0x1000 RL 0 CM 0 100
      /begin IF_DATA XCP
        /begin PROTOCOL_LAYER
          0x100
        /end PROTOCOL_LAYER
      /end IF_DATA
    /end CHARACTERISTIC
    /begin RECORD_LAYOUT RL FNC_VALUES 1 Int16_Intel COLUMN_DIR DIRECT /end RECORD_LAYOUT
    /begin COMPU_METHOD CM "desc" IDENTICAL "%6.3" "unit" /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""

COEFFS_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT CoeffProject "Coeff Test"
  /begin MODULE CoeffModule "Module with Coeffs"
    /begin COMPU_METHOD LinearMethod
      "Linear mapping"
      LINEAR
      "%6.3"
      "unit"
      COEFFS_LINEAR 2.0 1.0
    /end COMPU_METHOD

    /begin COMPU_METHOD RatMethod
      "Rational mapping"
      RAT_FUNC
      "%6.3"
      "unit"
      COEFFS 0.0 1.0 0.0 0.0 0.0 1.0
    /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""

NESTED_IFDATA_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT NestedIfDataProject "Nested IfData Test"
  /begin MODULE NestedIfDataModule "Module with Nested IfData"
    /begin CHARACTERISTIC
      NestedIfDataChar
      "Char with nested IfData"
      VALUE 0x1000 RL 0 CM 0 100
      /begin IF_DATA XCP
        /begin PROTOCOL_LAYER
          0x100
          /begin IF_DATA CAN
            0x200
          /end IF_DATA
        /end PROTOCOL_LAYER
      /end IF_DATA
    /end CHARACTERISTIC
    /begin RECORD_LAYOUT RL FNC_VALUES 1 Int16_Intel COLUMN_DIR DIRECT /end RECORD_LAYOUT
    /begin COMPU_METHOD CM "desc" IDENTICAL "%6.3" "unit" /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""

COMPU_METHOD_COMMENT_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT CommentProject "CompuMethod comment Test"
  /begin MODULE CommentModule ""
    /begin COMPU_METHOD CM ""
      /* multi-line
         comment inside COMPU_METHOD */
      IDENTICAL /* inline trailing comment */
      "%6.3"
      "unit"
    /end COMPU_METHOD
  /end MODULE
/end PROJECT
"""


XCP_ON_CAN_A2L = """
ASAP2_VERSION 1 71
/begin PROJECT XcpProject "XCP on CAN Test"
  /begin MODULE XcpModule ""
    /begin A2ML
      taggedstruct Common_Parameters {
      };

      struct CAN_Parameters {
        uint;
        taggedstruct {
          "CAN_ID_MASTER" ulong;
          "CAN_ID_SLAVE" ulong;
          "BAUDRATE" ulong;
          "SAMPLE_POINT" uchar;
          "SAMPLE_RATE" enum {
            "SINGLE" = 1,
            "TRIPLE" = 3
          };
          "BTL_CYCLES" uchar;
          "SJW" uchar;
          "SYNC_EDGE" enum {
            "SINGLE" = 1,
            "DUAL" = 2
          };
          "MAX_DLC_REQUIRED" ;
          (block "DAQ_LIST_CAN_ID" struct {
            uint;
            taggedstruct {
              "VARIABLE" ;
              "FIXED" ulong;
            };
          })*;
        };
      };

      block "IF_DATA" taggedunion if_data {
        "XCP" struct {
          taggedstruct Common_Parameters;
          taggedstruct {
            block "XCP_ON_CAN" struct {
              struct CAN_Parameters;
              taggedstruct Common_Parameters;
            };
          };
        };
      };
    /end A2ML

    /begin IF_DATA XCP
      /begin XCP_ON_CAN
        0x0104
        CAN_ID_MASTER 0x7E0
        CAN_ID_SLAVE 0x7E8
        BAUDRATE 500000
        SAMPLE_POINT 75
        SAMPLE_RATE TRIPLE
        BTL_CYCLES 8
        SJW 2
        SYNC_EDGE DUAL
        MAX_DLC_REQUIRED
        /begin DAQ_LIST_CAN_ID
          1
          FIXED 0x18FF50E5
        /end DAQ_LIST_CAN_ID
        /begin DAQ_LIST_CAN_ID
          2
          VARIABLE
        /end DAQ_LIST_CAN_ID
      /end XCP_ON_CAN
    /end IF_DATA

  /end MODULE
/end PROJECT
"""


@pytest.fixture
def parser():
    return A2LParser()


def test_parse_minimal(parser, tmp_path):
    a2l_file = tmp_path / "minimal.a2l"
    a2l_file.write_text(MINIMAL_A2L, encoding="latin-1")

    db = parser.parse(str(a2l_file), in_memory=True)

    project = db.session.query(model.Project).first()
    assert project.name == "MiniProject"
    assert project.longIdentifier == "Minimal A2L Project"

    module = db.session.query(model.Module).first()
    assert module.name == "MiniModule"
    assert module.longIdentifier == "Minimal Module"


def test_parse_characteristic(parser, tmp_path):
    a2l_file = tmp_path / "char.a2l"
    a2l_file.write_text(CHARACTERISTIC_A2L, encoding="latin-1")

    db = parser.parse(str(a2l_file), in_memory=True)

    char = db.session.query(model.Characteristic).filter_by(name="MyChar").first()
    assert char is not None
    assert char.longIdentifier == "Test Characteristic"
    assert char.type == "VALUE"
    assert char.address == 0x1234
    assert char.deposit == "RecordLayout_Value"
    assert char.maxDiff == 0
    assert char.conversion == "CompuMethod_Identical"
    assert char.lowerLimit == 0
    assert char.upperLimit == 100

    rl = db.session.query(model.RecordLayout).filter_by(name="RecordLayout_Value").first()
    assert rl is not None
    assert rl.fnc_values.datatype == "Int16_Intel"


def test_parse_measurement(parser, tmp_path):
    a2l_file = tmp_path / "meas.a2l"
    a2l_file.write_text(MEASUREMENT_A2L, encoding="latin-1")

    db = parser.parse(str(a2l_file), in_memory=True)

    meas = db.session.query(model.Measurement).filter_by(name="MyMeas").first()
    assert meas is not None
    assert meas.longIdentifier == "Test Measurement"
    assert meas.datatype == "UBYTE"
    assert meas.conversion == "CompuMethod_Identical"
    assert meas.resolution == 1
    assert meas.accuracy == 100
    assert meas.lowerLimit == 0
    assert meas.upperLimit == 100
    assert meas.ecu_address.address == 0x5678


def test_parse_compu_vtab(parser, tmp_path):
    a2l_file = tmp_path / "vtab.a2l"
    a2l_file.write_text(COMPU_VTAB_A2L, encoding="latin-1")

    db = parser.parse(str(a2l_file), in_memory=True)

    method = db.session.query(model.CompuMethod).filter_by(name="CompuMethod_Vtab").first()
    assert method is not None
    assert method.conversionType == "TAB_VERB"
    assert method.compu_tab_ref.conversionTable == "MyVtab"

    tab = db.session.query(model.CompuVtab).filter_by(name="MyVtab").first()
    assert tab is not None
    assert tab.conversionType == "TAB_VERB"
    assert tab.numberValuePairs == 2
    assert tab.default_value.display_string == "Unknown"

    # Check value pairs
    pairs = sorted(tab.pairs, key=lambda x: x.position)
    assert len(pairs) == 2
    assert pairs[0].inVal == 0
    assert pairs[0].outVal == "Off"
    assert pairs[1].inVal == 1
    assert pairs[1].outVal == "On"


def test_parse_axis(parser, tmp_path):
    a2l_file = tmp_path / "axis.a2l"
    a2l_file.write_text(AXIS_A2L, encoding="latin-1")

    db = parser.parse(str(a2l_file), in_memory=True)

    axis = db.session.query(model.AxisPts).filter_by(name="MyAxis").first()
    assert axis is not None
    assert axis.longIdentifier == "Test Axis"
    assert axis.address == 0x2000
    assert axis.inputQuantity == "InputQuantity_Ident"
    assert axis.depositAttr == "RecordLayout_Ident"
    assert axis.maxDiff == 0.0
    assert axis.conversion == "CompuMethod_Ident"
    assert axis.maxAxisPoints == 5
    assert axis.lowerLimit == 0.0
    assert axis.upperLimit == 100.0


def test_parse_if_data(parser, tmp_path):
    a2l_file = tmp_path / "ifdata.a2l"
    a2l_file.write_text(IFDATA_A2L, encoding="latin-1")

    db = parser.parse(str(a2l_file), in_memory=True)

    char = db.session.query(model.Characteristic).filter_by(name="CharWithIfData").first()
    assert char is not None
    assert len(char.if_data) == 1
    assert "PROTOCOL_LAYER" in char.if_data[0].raw
    assert "0x100" in char.if_data[0].raw


def test_parse_coeffs(parser, tmp_path):
    a2l_file = tmp_path / "coeffs.a2l"
    a2l_file.write_text(COEFFS_A2L, encoding="latin-1")

    db = parser.parse(str(a2l_file), in_memory=True)

    linear = db.session.query(model.CompuMethod).filter_by(name="LinearMethod").first()
    assert linear.conversionType == "LINEAR"
    assert linear.coeffs_linear.a == 2.0
    assert linear.coeffs_linear.b == 1.0

    rat = db.session.query(model.CompuMethod).filter_by(name="RatMethod").first()
    assert rat.conversionType == "RAT_FUNC"
    assert rat.coeffs.a == 0.0
    assert rat.coeffs.b == 1.0
    assert rat.coeffs.f == 1.0


def test_parse_nested_if_data(parser, tmp_path):
    a2l_file = tmp_path / "nested_ifdata.a2l"
    a2l_file.write_text(NESTED_IFDATA_A2L, encoding="latin-1")

    db = parser.parse(str(a2l_file), in_memory=True)

    char = db.session.query(model.Characteristic).filter_by(name="NestedIfDataChar").first()
    assert char is not None
    assert len(char.if_data) == 1
    raw = char.if_data[0].raw
    assert "PROTOCOL_LAYER" in raw
    assert "0x100" in raw
    assert "IF_DATA CAN" in raw
    assert "0x200" in raw


def test_parse_and_export_xcp_on_can(parser, tmp_path):
    a2l_file = tmp_path / "xcp_can.a2l"
    a2l_file.write_text(XCP_ON_CAN_A2L, encoding="latin-1")

    db = parser.parse(str(a2l_file), in_memory=True, progress_bar=False, loglevel="ERROR")
    session = db.session
    session.setup_ifdata_parser(loglevel="ERROR")
    parsed = session.parse_ifdata(session.query(model.Module).first().if_data)

    assert parsed and "XCP" in parsed[0]
    xcp_entries = parsed[0]["XCP"]
    assert xcp_entries and "XCP_ON_CAN" in xcp_entries[0]

    can_entry = xcp_entries[0]["XCP_ON_CAN"][0]
    assert can_entry[0] == 0x0104
    params = can_entry[1]
    assert params["CAN_ID_MASTER"] == 0x7E0
    assert params["CAN_ID_SLAVE"] == 0x7E8
    assert params["BAUDRATE"] == 500000
    assert params["SAMPLE_POINT"] == 75
    assert params["SAMPLE_RATE"] == "TRIPLE"
    assert params["BTL_CYCLES"] == 8
    assert params["SJW"] == 2
    assert params["SYNC_EDGE"] == "DUAL"
    assert params["MAX_DLC_REQUIRED"] is True
    assert params["DAQ_LIST_CAN_ID"] == [
        [1, {"FIXED": 0x18FF50E5}],
        [2, {"VARIABLE": True}],
    ]

    exported = _render_a2l(session, encoding="latin-1")
    exported_path = tmp_path / "xcp_can_exported.a2l"
    exported_path.write_text(exported, encoding="latin-1")

    db_rt = parser.parse(str(exported_path), in_memory=True, progress_bar=False, loglevel="ERROR")
    db_rt.session.setup_ifdata_parser(loglevel="ERROR")
    parsed_rt = db_rt.session.parse_ifdata(db_rt.session.query(model.Module).first().if_data)
    assert parsed_rt == parsed


def test_export_roundtrip_asap2_demo(parser, tmp_path):
    repo_root = Path(__file__).resolve().parents[2]
    source = repo_root / "examples" / "ASAP2_Demo_V161.a2l"

    db = parser.parse(str(source), in_memory=True, progress_bar=False, loglevel="ERROR")
    session = db.session
    session.setup_ifdata_parser(loglevel="ERROR")

    exported = _render_a2l(session, encoding="latin-1")
    assert "\n\n\n" not in exported

    exported_path = tmp_path / "asap2_demo_exported.a2l"
    exported_path.write_text(exported, encoding="latin-1")

    db_rt = parser.parse(str(exported_path), in_memory=True, progress_bar=False, loglevel="ERROR")
    db_rt.session.setup_ifdata_parser(loglevel="ERROR")

    project = db_rt.session.query(model.Project).first()
    assert project is not None
    assert project.name == "ASAP2_Example"
    assert len(db_rt.session.query(model.IfData).all()) == len(session.query(model.IfData).all())


def test_export_roundtrip_ifdata_section(parser, tmp_path):
    repo_root = Path(__file__).resolve().parents[2]
    snippet = repo_root / "examples" / "ASAP2_Demo_V161_ifdata_section.a2l"
    wrapped = (
        "ASAP2_VERSION 1 71\n"
        '/begin PROJECT IfDataWrap ""\n'
        '  /begin MODULE IfDataMod ""\n'
        + "\n".join(("  " + line if line.strip() else "") for line in snippet.read_text(encoding="latin-1").splitlines())
        + "\n  /end MODULE\n"
        "/end PROJECT\n"
    )
    wrapped_path = tmp_path / "ifdata_wrapped.a2l"
    wrapped_path.write_text(wrapped, encoding="latin-1")

    db = parser.parse(str(wrapped_path), in_memory=True, progress_bar=False, loglevel="ERROR")
    session = db.session
    session.setup_ifdata_parser(loglevel="ERROR")

    exported = _render_a2l(session, encoding="latin-1")
    assert "\n\n\n" not in exported

    exported_path = tmp_path / "ifdata_exported.a2l"
    exported_path.write_text(exported, encoding="latin-1")

    db_rt = parser.parse(str(exported_path), in_memory=True, progress_bar=False, loglevel="ERROR")
    db_rt.session.setup_ifdata_parser(loglevel="ERROR")

    rt_ifdata = db_rt.session.query(model.IfData).first()
    assert rt_ifdata is not None
    assert "IF_DATA" in rt_ifdata.raw


def test_parse_compu_method_comment(parser, tmp_path):
    a2l_file = tmp_path / "compu_comment.a2l"
    a2l_file.write_text(COMPU_METHOD_COMMENT_A2L, encoding="latin-1")

    db = parser.parse(str(a2l_file), in_memory=True)

    compu = db.session.query(model.CompuMethod).filter_by(name="CM").first()
    assert compu is not None
    assert compu.conversionType == "IDENTICAL"
    assert compu.format == "%6.3"
    assert compu.unit == "unit"
