#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest

from pya2l import exceptions
from pya2l import model
from pya2l.a2l_listener import A2LListener
from pya2l.api.inspect import CompuMethod
from pya2l.api.inspect import Group
from pya2l.api.inspect import Measurement
from pya2l.api.inspect import ModCommon
from pya2l.api.inspect import ModPar
from pya2l.api.inspect import NoCompuMethod
from pya2l.api.inspect import TypedefStructure
from pya2l.parserlib import ParserWrapper


try:
    import numpy as np
except ImportError:
    has_numpy = False
else:
    has_numpy = True

try:
    from scipy.interpolate import RegularGridInterpolator
except ImportError:
    has_scipy = False
else:
    has_scipy = True


RUN_MATH_TEST = has_numpy and has_scipy


def test_measurement_basic():
    parser = ParserWrapper("a2l", "measurement", A2LListener, debug=False)
    DATA = """
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
    """
    db, _ = parser.parseFromString(DATA)
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
    assert meas.bitOperation is None
    assert meas.byteOrder is None
    assert meas.discrete is False
    assert meas.displayIdentifier is None
    assert meas.ecuAddress is None
    # assert meas.ecuAddressExtension is None
    assert meas.errorMask is None
    assert meas.format is None
    assert meas.functionList == []
    assert meas.layout is None
    assert meas.matrixDim is None
    assert meas.maxRefresh is None
    assert meas.physUnit is None
    assert meas.readWrite is False
    assert meas.refMemorySegment is None
    assert meas.symbolLink is None
    assert meas.virtual == []
    assert meas.compuMethod is NoCompuMethod()


def test_measurement_full_featured():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """
    /begin MODULE testModule ""
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
            BYTE_ORDER MSB_FIRST
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
    """

    db, _ = parser.parseFromString(DATA)
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
    assert meas.annotations == [
        {
            "label": "ASAM Workinggroup",
            "origin": "Python Universe",
            "text": ["Test the A2L annotation", "Another line"],
        }
    ]
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
    assert meas.matrixDim == {"x": 2, "y": 4, "z": 3}
    assert meas.maxRefresh == {"rate": 15, "scalingUnit": 3}
    assert meas.physUnit == "mph"
    assert meas.readWrite
    assert meas.refMemorySegment == "Data2"
    assert meas.symbolLink == {"offset": 4711, "symbolName": "VehicleSpeed"}
    assert meas.virtual == ["PHI_BASIS", "PHI_CORR"]
    assert meas.compuMethod.conversionType == "RAT_FUNC"
    assert meas.compuMethod.unit == "km/h"
    assert meas.compuMethod.format == "%6.2"
    assert meas.compuMethod.longIdentifier == "conversion method for velocity"
    assert meas.compuMethod.coeffs["a"] == 0.0
    assert meas.compuMethod.coeffs["b"] == 100.0
    assert meas.compuMethod.coeffs["c"] == 0.0
    assert meas.compuMethod.coeffs["d"] == 0.0
    assert meas.compuMethod.coeffs["e"] == 0.0
    assert meas.compuMethod.coeffs["f"] == 1.0


def test_measurement_no_compu_method():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """
    /begin MODULE testModule ""
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
    """
    db, _ = parser.parseFromString(DATA)
    meas = Measurement(db.session, "N")
    assert meas.compuMethod is NoCompuMethod()


def test_measurement_compu_method_identical():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.IDENTICAL
            "conversion that delivers always phys = int"
            IDENTICAL "%3.0" "hours"
        /end COMPU_METHOD
        /begin MEASUREMENT
            N /* name */
            "Engine speed" /* long identifier */
            UWORD /* datatype */
            CM.IDENTICAL /* conversion */
            2 /* resolution */
            2.5 /* accuracy */
            120.0 /* lower limit */
            8400.0 /* upper limit */
        /end MEASUREMENT
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    meas = Measurement(db.session, "N")
    assert meas.compuMethod.format == "%3.0"
    assert meas.compuMethod.conversionType == "IDENTICAL"
    assert meas.compuMethod.unit == "hours"
    assert meas.compuMethod.longIdentifier == "conversion that delivers always phys = int"


def test_measurement_compu_method_form():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.FORM.X_PLUS_4
          "" FORM "%6.1" "rpm"
          /begin FORMULA
            "X1+4"
            FORMULA_INV "X1-4"
            /end FORMULA
        /end COMPU_METHOD
        /begin MEASUREMENT
            N /* name */
            "Engine speed" /* long identifier */
            UWORD /* datatype */
            CM.FORM.X_PLUS_4 /* conversion */
            2 /* resolution */
            2.5 /* accuracy */
            120.0 /* lower limit */
            8400.0 /* upper limit */
        /end MEASUREMENT
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    meas = Measurement(db.session, "N")
    assert meas.compuMethod.format == "%6.1"
    assert meas.compuMethod.conversionType == "FORM"
    assert meas.compuMethod.unit == "rpm"
    assert meas.compuMethod.longIdentifier == ""
    assert meas.compuMethod.formula["formula"] == "X1+4"
    assert meas.compuMethod.formula["formula_inv"] == "X1-4"


def test_measurement_compu_method_linear():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.LINEAR.MUL_2
          "Linear function with parameter set for phys = f(int) = 2*int + 0"
          LINEAR "%3.1" "m/s"
          COEFFS_LINEAR 2 0
        /end COMPU_METHOD
        /begin MEASUREMENT
            N /* name */
            "Engine speed" /* long identifier */
            UWORD /* datatype */
            CM.LINEAR.MUL_2 /* conversion */
            2 /* resolution */
            2.5 /* accuracy */
            120.0 /* lower limit */
            8400.0 /* upper limit */
        /end MEASUREMENT
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    meas = Measurement(db.session, "N")

    assert meas.compuMethod.format == "%3.1"
    assert meas.compuMethod.conversionType == "LINEAR"
    assert meas.compuMethod.unit == "m/s"
    assert meas.compuMethod.longIdentifier == "Linear function with parameter set for phys = f(int) = 2*int + 0"
    assert meas.compuMethod.coeffs_linear["a"] == 2.0
    assert meas.compuMethod.coeffs_linear["b"] == 0.0


def test_measurement_compu_method_rat_func():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.RAT_FUNC.DIV_81_9175
          "rational function with parameter set for impl = f(phys) = phys * 81.9175"
          RAT_FUNC "%8.4" "grad C"
          COEFFS 0 81.9175 0 0 0 1
        /end COMPU_METHOD
        /begin MEASUREMENT
            N /* name */
            "Engine speed" /* long identifier */
            UWORD /* datatype */
            CM.RAT_FUNC.DIV_81_9175 /* conversion */
            2 /* resolution */
            2.5 /* accuracy */
            120.0 /* lower limit */
            8400.0 /* upper limit */
        /end MEASUREMENT
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    meas = Measurement(db.session, "N")

    assert meas.compuMethod.format == "%8.4"
    assert meas.compuMethod.conversionType == "RAT_FUNC"
    assert meas.compuMethod.unit == "grad C"
    assert meas.compuMethod.longIdentifier == "rational function with parameter set for impl = f(phys) = phys * 81.9175"
    assert meas.compuMethod.coeffs["a"] == 0.0
    assert meas.compuMethod.coeffs["b"] == 81.9175
    assert meas.compuMethod.coeffs["c"] == 0.0
    assert meas.compuMethod.coeffs["d"] == 0.0
    assert meas.compuMethod.coeffs["e"] == 0.0
    assert meas.compuMethod.coeffs["f"] == 1.0


def test_measurement_compu_method_tab_intp():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_INTP.DEFAULT_VALUE
          ""
          TAB_INTP "%8.4" "U/min"
          COMPU_TAB_REF CM.TAB_INTP.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_TAB CM.TAB_INTP.DEFAULT_VALUE.REF
           ""
           TAB_INTP
           12
           -3 98
           -1 99
           0 100
           2 102
           4 104
           5 105
           6 106
           7 107
           8 108
           9 109
           10 110
           13 111
           DEFAULT_VALUE_NUMERIC 300.56
        /end COMPU_TAB
        /begin MEASUREMENT
            N /* name */
            "Engine speed" /* long identifier */
            UWORD /* datatype */
            CM.TAB_INTP.DEFAULT_VALUE /* conversion */
            2 /* resolution */
            2.5 /* accuracy */
            120.0 /* lower limit */
            8400.0 /* upper limit */
        /end MEASUREMENT
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    meas = Measurement(db.session, "N")
    assert meas.compuMethod.format == "%8.4"
    assert meas.compuMethod.conversionType == "TAB_INTP"
    assert meas.compuMethod.unit == "U/min"
    assert meas.compuMethod.longIdentifier == ""
    assert meas.compuMethod.tab["default_value"] == 300.56
    assert meas.compuMethod.tab["interpolation"]
    assert meas.compuMethod.tab["num_values"] == 12
    assert meas.compuMethod.tab["in_values"] == [
        -3.0,
        -1.0,
        0.0,
        2.0,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        9.0,
        10.0,
        13.0,
    ]
    assert meas.compuMethod.tab["out_values"] == [
        98.0,
        99.0,
        100.0,
        102.0,
        104.0,
        105.0,
        106.0,
        107.0,
        108.0,
        109.0,
        110.0,
        111.0,
    ]


def test_measurement_compu_method_tab_verb():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_VERB.DEFAULT_VALUE
          "Verbal conversion with default value"
          TAB_VERB "%12.0" ""
          COMPU_TAB_REF CM.TAB_VERB.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB CM.TAB_VERB.DEFAULT_VALUE.REF
          "List of text strings and relation to impl value"
          TAB_VERB 6
          2 "red"
          3 "orange"
          4 "yellow"
          5 "green"
          6 "blue"
          7 "violet"
          DEFAULT_VALUE "unknown signal type"
        /end COMPU_VTAB
        /begin MEASUREMENT
            N /* name */
            "Engine speed" /* long identifier */
            UWORD /* datatype */
            CM.TAB_VERB.DEFAULT_VALUE /* conversion */
            2 /* resolution */
            2.5 /* accuracy */
            120.0 /* lower limit */
            8400.0 /* upper limit */
        /end MEASUREMENT
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    meas = Measurement(db.session, "N")
    assert meas.compuMethod.format == "%12.0"
    assert meas.compuMethod.conversionType == "TAB_VERB"
    assert meas.compuMethod.unit == ""
    assert meas.compuMethod.longIdentifier == "Verbal conversion with default value"
    assert meas.compuMethod.tab_verb["default_value"] == "unknown signal type"
    assert meas.compuMethod.tab_verb["num_values"] == 6
    assert meas.compuMethod.tab_verb["ranges"] is False
    assert meas.compuMethod.tab_verb["in_values"] == [2.0, 3.0, 4.0, 5.0, 6.0, 7.0]
    assert meas.compuMethod.tab_verb["text_values"] == [
        "red",
        "orange",
        "yellow",
        "green",
        "blue",
        "violet",
    ]


def test_measurement_compu_method_tab_verb_range():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.VTAB_RANGE.DEFAULT_VALUE
           "verbal range with default value"
           TAB_VERB
           "%4.2"
           ""
           COMPU_TAB_REF CM.VTAB_RANGE.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB_RANGE CM.VTAB_RANGE.DEFAULT_VALUE.REF
           ""
           11
           0 1 "Zero_to_one"
           2 3 "two_to_three"
           4 7 "four_to_seven"
           14 17 "fourteen_to_seventeen"
           18 99 "eigteen_to_ninetynine"
           100 100 "hundred"
           101 101 "hundredone"
           102 102 "hundredtwo"
           103 103 "hundredthree"
           104 104 "hundredfour"
           105 105 "hundredfive"
           DEFAULT_VALUE "out of range value"
        /end COMPU_VTAB_RANGE
        /begin MEASUREMENT
            N /* name */
            "Engine speed" /* long identifier */
            UWORD /* datatype */
            CM.VTAB_RANGE.DEFAULT_VALUE /* conversion */
            2 /* resolution */
            2.5 /* accuracy */
            120.0 /* lower limit */
            8400.0 /* upper limit */
        /end MEASUREMENT
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    meas = Measurement.get(db.session, "N")
    assert meas.compuMethod.format == "%4.2"
    assert meas.compuMethod.conversionType == "TAB_VERB"
    assert meas.compuMethod.unit == ""
    assert meas.compuMethod.longIdentifier == "verbal range with default value"
    assert meas.compuMethod.name == "CM.VTAB_RANGE.DEFAULT_VALUE"
    assert meas.compuMethod.statusStringRef is None
    assert meas.compuMethod.tab_verb["default_value"] == "out of range value"
    assert meas.compuMethod.tab_verb["num_values"] == 11
    assert meas.compuMethod.tab_verb["ranges"]
    assert meas.compuMethod.tab_verb["lower_values"] == [
        0.0,
        2.0,
        4.0,
        14.0,
        18.0,
        100.0,
        101.0,
        102.0,
        103.0,
        104.0,
        105.0,
    ]
    assert meas.compuMethod.tab_verb["text_values"] == [
        "Zero_to_one",
        "two_to_three",
        "four_to_seven",
        "fourteen_to_seventeen",
        "eigteen_to_ninetynine",
        "hundred",
        "hundredone",
        "hundredtwo",
        "hundredthree",
        "hundredfour",
        "hundredfive",
    ]
    assert meas.compuMethod.tab_verb["upper_values"] == [
        1.0,
        3.0,
        7.0,
        17.0,
        99.0,
        100.0,
        101.0,
        102.0,
        103.0,
        104.0,
        105.0,
    ]


def test_mod_par_full_featured():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """
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
    """
    db, _ = parser.parseFromString(DATA)
    mp = ModPar(db.session, "testModule")
    assert mp.comment == "Note: Provisional release for test purposes only!"

    assert mp.version == "Test version of 01.02.1994"
    assert mp.addrEpk[0] == 284280
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
    assert ms == {
        "address": 196608,
        "attribute": "EXTERN",
        "longIdentifier": "external RAM",
        "memoryType": "RAM",
        "name": "ext_Ram",
        "offset_0": -1,
        "offset_1": -1,
        "offset_2": -1,
        "offset_3": -1,
        "offset_4": -1,
        "prgType": "DATA",
        "size": 4096,
    }
    m0, m1, m2 = mp.memoryLayouts
    assert m0 == {
        "address": 0,
        "offset_0": -1,
        "offset_1": -1,
        "offset_2": -1,
        "offset_3": -1,
        "offset_4": -1,
        "prgType": "PRG_RESERVED",
        "size": 1024,
    }
    assert m1 == {
        "address": 1024,
        "offset_0": -1,
        "offset_1": -1,
        "offset_2": -1,
        "offset_3": -1,
        "offset_4": -1,
        "prgType": "PRG_CODE",
        "size": 15360,
    }
    assert m2 == {
        "address": 16384,
        "offset_0": -1,
        "offset_1": -1,
        "offset_2": -1,
        "offset_3": -1,
        "offset_4": -1,
        "prgType": "PRG_DATA",
        "size": 22528,
    }
    sc = mp.systemConstants
    assert sc == {"CONTROLLERx constant1": 0.33, "CONTROLLERx constant2": 2.79}


def test_mod_par_basic():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """
    /begin MODULE testModule ""
        /begin MOD_PAR "Note: Provisional release for test purposes only!"
        /end MOD_PAR
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    mp = ModPar(db.session, "testModule")
    assert mp.comment == "Note: Provisional release for test purposes only!"
    assert mp.version is None
    assert mp.addrEpk == []
    assert mp.epk is None
    assert mp.supplier is None
    assert mp.customer is None
    assert mp.customerNo is None
    assert mp.user is None
    assert mp.phoneNo is None
    assert mp.ecu is None
    assert mp.cpu is None
    assert mp.noOfInterfaces is None
    assert mp.memorySegments == []
    assert mp.memoryLayouts == []
    assert mp.systemConstants == {}


def test_mod_common_full_featured():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """
    /begin MODULE testModule ""
        /begin MOD_COMMON "Characteristic maps always deposited in same mode"
            S_REC_LAYOUT S_ABL
            DEPOSIT ABSOLUTE
            BYTE_ORDER MSB_LAST
            DATA_SIZE 16
            ALIGNMENT_BYTE  1
            ALIGNMENT_WORD          2
            ALIGNMENT_LONG          4
            ALIGNMENT_INT64         8
            ALIGNMENT_FLOAT32_IEEE  4
            ALIGNMENT_FLOAT64_IEEE  8

        /end MOD_COMMON
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    mc = ModCommon(db.session, "testModule")
    assert mc.comment == "Characteristic maps always deposited in same mode"
    # assert mc.sRecLayout.name == "S_ABL"
    assert mc.sRecLayout == "S_ABL"
    assert mc.deposit == "ABSOLUTE"
    assert mc.byteOrder == "MSB_LAST"
    assert mc.dataSize == 16
    assert mc.alignment == {
        "FLOAT64": 8,
        "DWORD": 4,
        "BYTE": 1,
        "WORD": 2,
        "QWORD": 8,
        "FLOAT32": 4,
        "FLOAT16": 2,
    }


@pytest.mark.skip
def test_group():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """
    /begin MODULE testModule ""
        /begin GROUP SOFTWARE_COMPONENTS
            "assignment of the definitions to C files"
            ROOT
            /begin SUB_GROUP INJE
                C6TD
            /end SUB_GROUP
        /end GROUP
        /begin GROUP INJE
            "Subsystem Injection"
            /begin SUB_GROUP Injec1
                Injec2
            /end SUB_GROUP
        /end GROUP
        /begin GROUP Injec1
            "Module filename Injec1"
            /begin REF_CHARACTERISTIC
                INJECTION_CURVE
            /end REF_CHARACTERISTIC
        /end GROUP
        /begin GROUP Injec2
            "Module filename Injec2"
            /begin REF_CHARACTERISTIC
                INJECTION_ADJUST
            /end REF_CHARACTERISTIC
            /begin REF_MEASUREMENT
                GAS_INPUT
                WHEEL_SPEED
            /end REF_MEASUREMENT
        /end GROUP
        /begin GROUP C6TD
            "Shift Point Control"
            /begin SUB_GROUP c6tdvder
                c6tdertf
            /end SUB_GROUP
        /end GROUP
        /begin GROUP c6tdvder
            "Module filename c6tdvder"
            /begin REF_CHARACTERISTIC
                SHIFT23_CURVE
            /end REF_CHARACTERISTIC
            /begin REF_MEASUREMENT
                LOOP_COUN2
                NO_GEAR
            /end REF_MEASUREMENT
        /end GROUP
        /begin GROUP c6tderft
            "Module filename c6tderft"
            /begin REF_CHARACTERISTIC
                LUP23_CURVE
            /end REF_CHARACTERISTIC
            /begin REF_MEASUREMENT
                TRANSMISSION_SP
                ENGINE_SPEED
            /end REF_MEASUREMENT
        /end GROUP
        /begin GROUP CALIBRATION_COMPONENTS
            "assignment of the definitions to
            calibration components"
            ROOT
            /begin SUB_GROUP
                Winter_Test
                Summer_Test
            /end SUB_GROUP
        /end GROUP
        /begin GROUP CALIBRATION_COMPONENTS_L4
            "L4-PCM 2002 cals"
            ROOT
            /begin SUB_GROUP LUFT
                CLOSED_LOOP
            /end SUB_GROUP
        /end GROUP
        /begin GROUP LUFT
        "Cals in LUFT Subsystem"
            /begin REF_CHARACTERISTIC
                KfLUFT_n_EngSpdThrsh
                KtLUFT_ScaledVE
                KaLUFT_AirPerCylCoeff
            /end REF_CHARACTERISTIC
        /end GROUP
        /begin GROUP CLOSED_LOOP
        "Cals in FCLS, FCLP & FCLL Subsystem"
            /begin REF_CHARACTERISTIC
                KaFCLP_U_O2LeanThrsh
                KfFCLP_t_O2AgainstMax
        /end REF_CHARACTERISTIC
        /end GROUP
        /begin GROUP Winter_Test
            "Flash this in winter time"
            /begin REF_CHARACTERISTIC
                GASOLINE_CURVE
            /end REF_CHARACTERISTIC
        /end GROUP
        /begin GROUP Summer_Test
            "Flash that in summer time"
            /begin REF_CHARACTERISTIC
                SUPER_CURVE
            /end REF_CHARACTERISTIC
        /end GROUP
        /begin GROUP SOFTWARE_COMPONENTS
            "L4-PCM 2002 C modules"
            ROOT
            /begin SUB_GROUP
                luftkmgr.c
                fclpkout.c
                viosmeng.c
            /end SUB_GROUP
        /end GROUP
        /begin GROUP luftkmgr.c
        "Objects in luftkmgr.c"
            /begin REF_CHARACTERISTIC
                KtLUFT_ScaledVE
            /end REF_CHARACTERISTIC
        /end GROUP
        /begin GROUP fclpkout.c
            "Objects in fclpkout.c"
            /begin REF_CHARACTERISTIC
                KaFCLP_U_O2LeanThrsh
                KfFCLP_t_O2AgainstMax
            /end REF_CHARACTERISTIC
        /end GROUP
        /begin GROUP viosmeng.c
            "Objects in viosmeng.c"
            /begin REF_CHARACTERISTIC
                VfVIOS_n_EngSpdLORES
                VfVIOS_p_AmbientAirPres
            /end REF_CHARACTERISTIC
        /end GROUP
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    gr = Group.get(db.session, "CALIBRATION_COMPONENTS")
    gr = Group.get(db.session, "CALIBRATION_COMPONENTS_L4")
    gr = Group.get(db.session, "SOFTWARE_COMPONENTS")
    print(gr)


def test_typedef_structure_no_instances():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """/begin MODULE testModule ""
        /begin RECORD_LAYOUT _UWORD FNC_VALUES 1 UWORD ROW_DIR DIRECT /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _FLOAT64_IEEE FNC_VALUES 1 FLOAT64_IEEE ROW_DIR DIRECT /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _UBYTE FNC_VALUES 1 UBYTE ROW_DIR DIRECT /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _ULONG FNC_VALUES 1 ULONG ROW_DIR DIRECT /end RECORD_LAYOUT
        /begin TYPEDEF_STRUCTURE EcuTask "TYPEDEF for class EcuTask" 0x58 SYMBOL_TYPE_LINK "EcuTask"
            /begin STRUCTURE_COMPONENT taskId _UWORD 0x0 SYMBOL_TYPE_LINK "taskId" /end STRUCTURE_COMPONENT
            /begin STRUCTURE_COMPONENT counter _UWORD 0x2 SYMBOL_TYPE_LINK "counter" /end STRUCTURE_COMPONENT
            /begin STRUCTURE_COMPONENT channel1 _FLOAT64_IEEE 0x10 SYMBOL_TYPE_LINK "channel1" /end STRUCTURE_COMPONENT
            /begin STRUCTURE_COMPONENT byte _UBYTE 0x38 SYMBOL_TYPE_LINK "byte" /end STRUCTURE_COMPONENT
            /begin STRUCTURE_COMPONENT word _UWORD 0x3A SYMBOL_TYPE_LINK "word" /end STRUCTURE_COMPONENT
            /begin STRUCTURE_COMPONENT dword _ULONG 0x3C SYMBOL_TYPE_LINK "dword" /end STRUCTURE_COMPONENT
        /end TYPEDEF_STRUCTURE
    /end MODULE"""
    db, _ = parser.parseFromString(DATA)
    tdef = TypedefStructure.get(db.session, "EcuTask")
    assert tdef.name == "EcuTask"
    assert tdef.longIdentifier == "TYPEDEF for class EcuTask"
    assert tdef.size == 88
    assert tdef.link == "SYMBOL_TYPE_LINK"
    assert tdef.symbol == "EcuTask"
    assert tdef.instances == []
    components = tdef.components
    assert len(components) == 6
    comp = components[0]
    assert comp.name == "taskId"
    assert comp.offset == 0
    assert comp.link == "SYMBOL_TYPE_LINK"
    assert comp.symbol == "taskId"
    comp = components[1]
    assert comp.name == "counter"
    assert comp.offset == 2
    assert comp.link == "SYMBOL_TYPE_LINK"
    assert comp.symbol == "counter"
    comp = components[2]
    assert comp.name == "channel1"
    assert comp.offset == 16
    assert comp.link == "SYMBOL_TYPE_LINK"
    assert comp.symbol == "channel1"
    comp = components[3]
    assert comp.name == "byte"
    assert comp.offset == 0x38
    assert comp.link == "SYMBOL_TYPE_LINK"
    assert comp.symbol == "byte"
    comp = components[4]
    assert comp.name == "word"
    assert comp.offset == 0x3A
    assert comp.link == "SYMBOL_TYPE_LINK"
    assert comp.symbol == "word"
    comp = components[5]
    assert comp.name == "dword"
    assert comp.offset == 0x3C
    assert comp.link == "SYMBOL_TYPE_LINK"
    assert comp.symbol == "dword"


@pytest.mark.skip
def test_typedef_structure_with_instances():
    parser = ParserWrapper("a2l", "module", A2LListener, debug=False)
    DATA = """/begin MODULE testModule ""
        /begin RECORD_LAYOUT _UWORD FNC_VALUES 1 UWORD ROW_DIR DIRECT /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _FLOAT64_IEEE FNC_VALUES 1 FLOAT64_IEEE ROW_DIR DIRECT /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _UBYTE FNC_VALUES 1 UBYTE ROW_DIR DIRECT /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _ULONG FNC_VALUES 1 ULONG ROW_DIR DIRECT /end RECORD_LAYOUT
        /begin TYPEDEF_STRUCTURE EcuTask "TYPEDEF for class EcuTask" 0x58 SYMBOL_TYPE_LINK "EcuTask"
            /begin STRUCTURE_COMPONENT taskId _UWORD 0x0 SYMBOL_TYPE_LINK "taskId" /end STRUCTURE_COMPONENT
            /begin STRUCTURE_COMPONENT counter _UWORD 0x2 SYMBOL_TYPE_LINK "counter" /end STRUCTURE_COMPONENT
            /begin STRUCTURE_COMPONENT channel1 _FLOAT64_IEEE 0x10 SYMBOL_TYPE_LINK "channel1" /end STRUCTURE_COMPONENT
            /begin STRUCTURE_COMPONENT byte _UBYTE 0x38 SYMBOL_TYPE_LINK "byte" /end STRUCTURE_COMPONENT
            /begin STRUCTURE_COMPONENT word _UWORD 0x3A SYMBOL_TYPE_LINK "word" /end STRUCTURE_COMPONENT
            /begin STRUCTURE_COMPONENT dword _ULONG 0x3C SYMBOL_TYPE_LINK "dword" /end STRUCTURE_COMPONENT
        /end TYPEDEF_STRUCTURE
        /begin INSTANCE ecuTask1 "ecupp task number 1" EcuTask 0x0 /end INSTANCE
        /begin INSTANCE ecuTask2 "ecu task number 2" EcuTask 0x0 /end INSTANCE
        /begin INSTANCE activeEcuTask "pointer to active ecu task" EcuTask 0x0 /end INSTANCE
    /end MODULE"""
    db, _ = parser.parseFromString(DATA)
    tdef = TypedefStructure.get(db.session, "EcuTask")
    assert tdef.name == "EcuTask"
    assert tdef.longIdentifier == "TYPEDEF for class EcuTask"
    assert tdef.size == 88
    assert tdef.link == "SYMBOL_TYPE_LINK"
    assert tdef.symbol == "EcuTask"
    components = tdef.components
    assert len(components) == 6
    comp = components[0]
    assert comp.name == "taskId"
    assert comp.offset == 0
    assert comp.link == "SYMBOL_TYPE_LINK"
    assert comp.symbol == "taskId"
    comp = components[1]
    assert comp.name == "counter"
    assert comp.offset == 2
    assert comp.link == "SYMBOL_TYPE_LINK"
    assert comp.symbol == "counter"
    comp = components[2]
    assert comp.name == "channel1"
    assert comp.offset == 16
    assert comp.link == "SYMBOL_TYPE_LINK"
    assert comp.symbol == "channel1"
    comp = components[3]
    assert comp.name == "byte"
    assert comp.offset == 0x38
    assert comp.link == "SYMBOL_TYPE_LINK"
    assert comp.symbol == "byte"
    comp = components[4]
    assert comp.name == "word"
    assert comp.offset == 0x3A
    assert comp.link == "SYMBOL_TYPE_LINK"
    assert comp.symbol == "word"
    comp = components[5]
    assert comp.name == "dword"
    assert comp.offset == 0x3C
    assert comp.link == "SYMBOL_TYPE_LINK"
    assert comp.symbol == "dword"
    assert len(tdef.instances) == 3
    instances = tdef.instances
    inst = instances[0]
    assert inst.name == "ecuTask1"
    assert inst.longIdentifier == "ecupp task number 1"
    assert inst.typeName == "EcuTask"
    assert inst.address == 0x00000000
    inst = instances[1]
    assert inst.name == "ecuTask2"
    assert inst.longIdentifier == "ecu task number 2"
    assert inst.typeName == "EcuTask"
    assert inst.address == 0x00000000
    inst = instances[2]
    assert inst.name == "activeEcuTask"
    assert inst.longIdentifier == "pointer to active ecu task"
    assert inst.typeName == "EcuTask"
    assert inst.address == 0x00000000


@pytest.mark.skip
def test_compu_method_invalid():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_VERB.DEFAULT_VALUE
          "Verbal conversion with default value"
          FOO_BAR "%12.0" ""
        /end COMPU_METHOD
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    CompuMethod(db.session, module.compu_method[0].name)


def test_compu_method_tab_verb():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_VERB.DEFAULT_VALUE
          "Verbal conversion with default value"
          TAB_VERB "%12.0" ""
          COMPU_TAB_REF CM.TAB_VERB.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB CM.TAB_VERB.DEFAULT_VALUE.REF
          "List of text strings and relation to impl value"
          TAB_VERB 3
          1 "SawTooth"
          2 "Square"
          3 "Sinus"
          DEFAULT_VALUE "unknown signal type"
        /end COMPU_VTAB
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    assert compu.int_to_physical(1) == "SawTooth"
    assert compu.physical_to_int("Sinus") == 3
    assert compu.int_to_physical(10) == "unknown signal type"


def test_compu_method_tab_verb_no_default_value():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_VERB.DEFAULT_VALUE
          "Verbal conversion with default value"
          TAB_VERB "%12.0" ""
          COMPU_TAB_REF CM.TAB_VERB.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB CM.TAB_VERB.DEFAULT_VALUE.REF
          "List of text strings and relation to impl value"
          TAB_VERB 3
          1 "SawTooth"
          2 "Square"
          3 "Sinus"
        /end COMPU_VTAB
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    assert compu.int_to_physical(1) == "SawTooth"
    assert compu.physical_to_int("Sinus") == 3
    assert compu.int_to_physical(10) is None


@pytest.mark.skip
def test_compu_method_tab_verb_no_vtab():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_VERB.DEFAULT_VALUE
          "Verbal conversion with default value"
          TAB_VERB "%12.0" ""
          COMPU_TAB_REF CM.TAB_VERB.DEFAULT_VALUE.REF
        /end COMPU_METHOD
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    with pytest.raises(exceptions.StructuralError):
        CompuMethod(db.session, module.compu_method[0])


def test_compu_method_tab_nointerp_default():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_NOINTP.DEFAULT_VALUE
          ""
          TAB_NOINTP "%8.4" "U/  min  "
          COMPU_TAB_REF CM.TAB_NOINTP.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_TAB CM.TAB_NOINTP.DEFAULT_VALUE.REF
           ""
           TAB_NOINTP
           12
           -3 98
           -1 99
           0 100
           2 102
           4 104
           5 105
           6 106
           7 107
           8 108
           9 109
           10 110
           13 111
           DEFAULT_VALUE_NUMERIC 300.56 /* DEFAULT_VALUE_NUME RIC should be used here as the normal output is numeric */
        /end COMPU_TAB
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    assert compu.int_to_physical(-3) == 98
    assert compu.int_to_physical(8) == 108
    assert compu.physical_to_int(108) == 8
    assert compu.int_to_physical(1) == 300.56


def test_compu_method_tab_interp_default():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_INTP.DEFAULT_VALUE
          ""
          TAB_INTP "%8.4" "U/  min  "
          COMPU_TAB_REF CM.TAB_INTP.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_TAB CM.TAB_INTP.DEFAULT_VALUE.REF
           ""
           TAB_INTP
           12
           -3 98
           -1 99
           0 100
           2 102
           4 104
           5 105
           6 106
           7 107
           8 108
           9 109
           10 110
           13 111
           DEFAULT_VALUE_NUMERIC 300.56 /* DEFAULT_VALUE_NUME RIC should be used here as the normal output is numeric */
        /end COMPU_TAB
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    xs = np.arange(-3, 14)
    ys = np.array(
        [
            98.0,
            98.5,
            99.0,
            100.0,
            101.0,
            102.0,
            103.0,
            104.0,
            105.0,
            106.0,
            107.0,
            108.0,
            109.0,
            110.0,
            110.33333333333333,
            110.66666666666667,
            111.0,
        ]
    )
    assert np.array_equal(compu.int_to_physical(xs), ys)
    assert compu.int_to_physical(-3) == 98
    assert compu.int_to_physical(8) == 108
    assert compu.int_to_physical(14) == 300.56
    assert compu.int_to_physical(-4) == 300.56


def test_compu_method_tab_interp_no_default():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_INTP.NO_DEFAULT_VALUE
          ""
          TAB_INTP "%8.4" "U/  min  "
          COMPU_TAB_REF CM.TAB_INTP.NO_DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_TAB CM.TAB_INTP.NO_DEFAULT_VALUE.REF
           ""
           TAB_INTP
           12
           -3 98
           -1 99
           0 100
           2 102
           4 104
           5 105
           6 106
           7 107
           8 108
           9 109
           10 110
           13 111
        /end COMPU_TAB
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    xs = np.arange(-3, 14)
    ys = np.array(
        [
            98.0,
            98.5,
            99.0,
            100.0,
            101.0,
            102.0,
            103.0,
            104.0,
            105.0,
            106.0,
            107.0,
            108.0,
            109.0,
            110.0,
            110.33333333333333,
            110.66666666666667,
            111.0,
        ]
    )
    assert np.array_equal(compu.int_to_physical(xs), ys)
    assert compu.int_to_physical(-3) == 98
    assert compu.int_to_physical(8) == 108
    assert compu.int_to_physical(14) is None
    assert compu.int_to_physical(-4) is None


def test_compu_method_tab_nointerp_no_default():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_NOINTP.NO_DEFAULT_VALUE
          ""
          TAB_NOINTP "%8.4" "U/  min  "
          COMPU_TAB_REF CM.TAB_NOINTP.NO_DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_TAB CM.TAB_NOINTP.NO_DEFAULT_VALUE.REF
           ""
           TAB_NOINTP
           12
           -3 98
           -1 99
           0 100
           2 102
           4 104
           5 105
           6 106
           7 107
           8 108
           9 109
           10 110
           13 111
        /end COMPU_TAB
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    assert compu.int_to_physical(-3) == 98
    assert compu.int_to_physical(8) == 108
    assert compu.physical_to_int(108) == 8
    assert compu.int_to_physical(1) is None


@pytest.mark.skip
def test_compu_method_tab_nointerp_both_defaults():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.TAB_NOINTP.DEFAULT_VALUE
          ""
          TAB_NOINTP "%8.4" "U/  min  "
          COMPU_TAB_REF CM.TAB_NOINTP.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_TAB CM.TAB_NOINTP.DEFAULT_VALUE.REF
           ""
           TAB_NOINTP
           12
           -3 98
           -1 99
           0 100
           2 102
           4 104
           5 105
           6 106
           7 107
           8 108
           9 109
           10 110
           13 111
           DEFAULT_VALUE "value out of range"
           DEFAULT_VALUE_NUMERIC 300.56 /* DEFAULT_VALUE_NUME RIC should be used here as the normal output is numeric */
        /end COMPU_TAB
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    with pytest.raises(exceptions.StructuralError):
        CompuMethod(db.session, module.compu_method[0])


def test_compu_method_tab_verb_ranges():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.VTAB_RANGE.DEFAULT_VALUE
           "verbal range with default value"
           TAB_VERB
           "%4.2"
           ""
           COMPU_TAB_REF CM.VTAB_RANGE.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB_RANGE CM.VTAB_RANGE.DEFAULT_VALUE.REF
           ""
           11
           0 1 "Zero_to_one"
           2 3 "two_to_three"
           4 7 "four_to_seven"
           14 17 "fourteen_to_seventeen"
           18 99 "eigteen_to_ninetynine"
           100 100 "hundred"
           101 101 "hundredone"
           102 102 "hundredtwo"
           103 103 "hundredthree"
           104 104 "hundredfour"
           105 105 "hundredfive"
           DEFAULT_VALUE "out of range value"
        /end COMPU_VTAB_RANGE
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    assert compu.int_to_physical(0) == "Zero_to_one"
    assert compu.int_to_physical(6) == "four_to_seven"
    assert compu.int_to_physical(45) == "eigteen_to_ninetynine"
    assert compu.int_to_physical(100) == "hundred"
    assert compu.int_to_physical(105) == "hundredfive"
    assert compu.int_to_physical(-1) == "out of range value"
    assert compu.int_to_physical(106) == "out of range value"
    assert compu.int_to_physical(10) == "out of range value"


def test_compu_method_tab_verb_ranges_no_default():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.VTAB_RANGE.NO_DEFAULT_VALUE
           "verbal range without default value"
           TAB_VERB
           "%4.2"
           ""
           COMPU_TAB_REF CM.VTAB_RANGE.NO_DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB_RANGE CM.VTAB_RANGE.NO_DEFAULT_VALUE.REF
           ""
           11
           0 1 "Zero_to_one"
           2 3 "two_to_three"
           4 7 "four_to_seven"
           14 17 "fourteen_to_seventeen"
           18 99 "eigteen_to_ninetynine"
           100 100 "hundred"
           101 101 "hundredone"
           102 102 "hundredtwo"
           103 103 "hundredthree"
           104 104 "hundredfour"
           105 105 "hundredfive"
        /end COMPU_VTAB_RANGE
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    assert compu.int_to_physical(0) == "Zero_to_one"
    assert compu.int_to_physical(6) == "four_to_seven"
    assert compu.int_to_physical(45) == "eigteen_to_ninetynine"
    assert compu.int_to_physical(100) == "hundred"
    assert compu.int_to_physical(105) == "hundredfive"
    assert compu.int_to_physical(-1) is None
    assert compu.int_to_physical(106) is None
    assert compu.int_to_physical(10) is None


def test_compu_method_tab_verb_ranges_inv():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.VTAB_RANGE.DEFAULT_VALUE
           "verbal range with default value"
           TAB_VERB
           "%4.2"
           ""
           COMPU_TAB_REF CM.VTAB_RANGE.DEFAULT_VALUE.REF
        /end COMPU_METHOD
        /begin COMPU_VTAB_RANGE CM.VTAB_RANGE.DEFAULT_VALUE.REF
           ""
           11
           0 1 "Zero_to_one"
           2 3 "two_to_three"
           4 7 "four_to_seven"
           14 17 "fourteen_to_seventeen"
           18 99 "eigteen_to_ninetynine"
           100 100 "hundred"
           101 101 "hundredone"
           102 102 "hundredtwo"
           103 103 "hundredthree"
           104 104 "hundredfour"
           105 105 "hundredfive"
           DEFAULT_VALUE "out of range value"
        /end COMPU_VTAB_RANGE
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    assert compu.physical_to_int("Zero_to_one") == 0
    assert compu.physical_to_int("four_to_seven") == 4
    assert compu.physical_to_int("eigteen_to_ninetynine") == 18
    assert compu.physical_to_int("hundred") == 100
    assert compu.physical_to_int("hundredfive") == 105
    assert compu.physical_to_int("out of range value") is None


def test_compu_method_identical():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.IDENTICAL
          "conversion that delivers always phys = int"
          IDENTICAL "%3.0" "hours"
        /end COMPU_METHOD
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    xs = np.arange(-10, 11)
    assert np.array_equal(compu.int_to_physical(xs), xs)
    assert np.array_equal(compu.physical_to_int(xs), xs)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_rat_func_identical():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.RAT_FUNC.IDENT
          "rational function with parameter set for int = f(phys) = phys"
          RAT_FUNC "%3.1" "m/s"
          COEFFS 0 1 0 0 0 1
        /end COMPU_METHOD
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    xs = np.arange(-10, 11)
    assert np.array_equal(compu.int_to_physical(xs), xs)
    assert np.array_equal(compu.physical_to_int(xs), xs)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_rat_func_linear():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.RAT_FUNC.DIV_81_9175
          "rational function with parameter set for impl = f(phys) = phys * 81.9175"
          RAT_FUNC "%8.4" "grad C"
          COEFFS 0 81.9175 0 0 0 1
        /end COMPU_METHOD
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    xs = np.arange(-10, 11)
    ys = np.array(
        [
            -819.1750000000001,
            -737.2575,
            -655.34,
            -573.4225,
            -491.505,
            -409.58750000000003,
            -327.67,
            -245.7525,
            -163.835,
            -81.9175,
            0.0,
            81.9175,
            163.835,
            245.7525,
            327.67,
            409.58750000000003,
            491.505,
            573.4225,
            655.34,
            737.2575,
            819.1750000000001,
        ]
    )
    assert np.array_equal(compu.int_to_physical(ys), xs)
    assert np.array_equal(compu.physical_to_int(xs), ys)


@pytest.mark.skip
@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_rat_func_no_coeffs():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.RAT_FUNC.DIV_81_9175
          "rational function with parameter set for impl = f(phys) = phys * 81.9175"
          RAT_FUNC "%8.4" "grad C"
        /end COMPU_METHOD
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    with pytest.raises(exceptions.StructuralError):
        CompuMethod(db.session, module.compu_method[0])


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_linear():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.LINEAR.MUL_2
        "Linear function with parameter set for phys = f(int) = 2*int + 0"
         LINEAR "%3.1" "m/s"
         COEFFS_LINEAR 2 0
        /end COMPU_METHOD
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    xs = np.arange(-10, 11)
    assert np.array_equal(compu.int_to_physical(xs), xs * 2.0)
    assert np.array_equal(compu.physical_to_int(xs * 2.0), xs)


@pytest.mark.skip
@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_linear_no_coeffs():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.LINEAR.MUL_2
        "Linear function with parameter set for phys = f(int) = 2*int + 0"
         LINEAR "%3.1" "m/s"
        /end COMPU_METHOD
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    with pytest.raises(exceptions.StructuralError):
        CompuMethod(db.session, module)


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_formula_with_inv():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.FORM.X_PLUS_4
          ""
          FORM
          "%6.1"
          "rpm"
          /begin FORMULA
            "X1+4"
            FORMULA_INV "X1-4"
          /end FORMULA
        /end COMPU_METHOD
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    assert compu.int_to_physical(6) == 10
    assert compu.physical_to_int(4) == 0


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_formula_without_inv():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD CM.FORM.X_PLUS_4
          ""
          FORM
          "%6.1"
          "rpm"
          /begin FORMULA
            "X1+4"
          /end FORMULA
        /end COMPU_METHOD
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    assert compu.int_to_physical(6) == 10


@pytest.mark.skipif("RUN_MATH_TEST == False")
def test_compu_method_formula_with_sysc():
    parser = ParserWrapper("a2l", "module", A2LListener)
    DATA = """
    /begin MODULE testModule ""
        /begin MOD_PAR ""
             SYSTEM_CONSTANT "System_Constant_1" "42"
             SYSTEM_CONSTANT "System_Constant_2" "Textual constant"
        /end MOD_PAR

        /begin COMPU_METHOD CM.FORM.X_PLUS_SYSC
          ""
          FORM
          "%6.1"
          "rpm"
          /begin FORMULA
            "X1 + sysc(System_Constant_1)"
          /end FORMULA
        /end COMPU_METHOD
    /end MODULE
    """
    db, _ = parser.parseFromString(DATA)
    module = db.session.query(model.Module).first()
    compu = CompuMethod(db.session, module.compu_method[0].name)
    assert compu.int_to_physical(23) == 65
