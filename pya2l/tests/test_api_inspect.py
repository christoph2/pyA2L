#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

import pya2l.model as model
from pya2l.a2l_listener import ParserWrapper, A2LListener
from pya2l.api.inspect import Measurement



def test_measurement_basic():
    parser = ParserWrapper('a2l', 'measurement', A2LListener, debug = False)
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
    session = parser.parseFromString(DATA)
    meas = Measurement(session, "N")
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
    assert meas.bitOperation == {}
    assert meas.byteOrder is None
    assert meas.discrete == False
    assert meas.displayIdentifier is None
    assert meas.ecuAddress is None
    assert meas.ecuAddressExtension is None
    assert meas.errorMask is None
    assert meas.format is None
    assert meas.functionList == []
    assert meas.layout is None
    assert meas.matrixDim == {}
    assert meas.maxRefresh == {}
    assert meas.physUnit is None
    assert meas.readWrite == False
    assert meas.refMemorySegment is None
    assert meas.symbolLink == {}
    assert meas.virtual == []
    assert meas.compuMethod == {'type': 'NO_COMPU_METHOD'}

def test_measurement_full_featured():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
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

    session = parser.parseFromString(DATA)
    meas = Measurement(session, "N")
    assert meas.name == "N"
    assert meas.longIdentifier == "Engine speed"
    assert meas.datatype == "UWORD"
    assert meas.resolution == 2
    assert meas.accuracy == 2.5
    assert meas.lowerLimit == 120
    assert meas.upperLimit == 8400.0
    assert meas.arraySize == 8
    assert meas.bitMask == 0x0FFF
    assert meas.annotations == [{
            'label': 'ASAM Workinggroup',
            'origin': 'Python Universe',
            'text': ['Test the A2L annotation', 'Another line']
        }]
    assert meas.bitOperation == {'left_shift': 0, 'right_shift': 4, 'sign_extend': True}
    assert meas.byteOrder == "MSB_FIRST"
    assert meas.discrete == True
    assert meas.displayIdentifier == 'load_engine'
    assert meas.ecuAddress == 0xcafebabe
    assert meas.ecuAddressExtension == 42
    assert meas.errorMask == 1
    assert meas.format == "%4.2f"
    assert meas.functionList == ["ID_ADJUSTM", "FL_ADJUSTM"]
    assert meas.layout == "ROW_DIR"
    assert meas.matrixDim == {'x': 2, 'y': 4, 'z': 3}
    assert meas.maxRefresh == {'rate': 15, 'scalingUnit': 3}
    assert meas.physUnit == "mph"
    assert meas.readWrite == True
    assert meas.refMemorySegment == "Data2"
    assert meas.symbolLink == {'offset': 4711, 'symbolName': 'VehicleSpeed'}
    assert meas.virtual == ['PHI_BASIS', 'PHI_CORR']
    assert meas.compuMethod == {
        'type': 'RAT_FUNC', 'unit': 'km/h', 'format': '%6.2',
        'a': 0.0, 'b': 100.0, 'c': 0.0, 'd': 0.0, 'e': 0.0, 'f': 1.0,
        'longIdentifier': 'conversion method for velocity'
    }

def test_measurement_no_compu_method():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
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
    session = parser.parseFromString(DATA)
    meas = Measurement(session, "N")
    assert meas.compuMethod == {'type': 'NO_COMPU_METHOD'}

def test_measurement_compu_method_identical():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
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
    session = parser.parseFromString(DATA)
    meas = Measurement(session, "N")
    assert meas.compuMethod == {
        'format': '%3.0', 'type': 'IDENTICAL', 'unit': 'hours',
        'longIdentifier': 'conversion that delivers always phys = int'
        }


def test_measurement_compu_method_form():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
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
    session = parser.parseFromString(DATA)
    meas = Measurement(session, "N")
    assert meas.compuMethod == {
        'format': '%6.1', 'type': 'FORM', 'unit': 'rpm', 'formula': 'X1+4', 'formula_inv': 'X1-4', 'longIdentifier': ''
        }


def test_measurement_compu_method_linear():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
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
    session = parser.parseFromString(DATA)
    meas = Measurement(session, "N")
    assert meas.compuMethod == {
        'format': '%3.1', 'type': 'LINEAR', 'unit': 'm/s', 'a': 2.0, 'b': 0.0,
        'longIdentifier': 'Linear function with parameter set for phys = f(int) = 2*int + 0'
        }

def test_measurement_compu_method_rat_func():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
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
    session = parser.parseFromString(DATA)
    meas = Measurement(session, "N")
    assert meas.compuMethod == {
        'format': '%8.4', 'type': 'RAT_FUNC', 'unit': 'grad C', 'a': 0.0, 'b': 81.9175,
        'c': 0.0, 'd': 0.0, 'e': 0.0, 'f': 1.0,
        'longIdentifier': 'rational function with parameter set for impl = f(phys) = phys * 81.9175'
        }

def test_measurement_compu_method_tab_intp():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
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
    session = parser.parseFromString(DATA)
    meas = Measurement(session, "N")
    assert meas.compuMethod == {
        'format': '%8.4', 'type': 'TAB_INTP', 'unit': 'U/min', 'default_value': 300.56, 'interpolation': True,
        'num_values': 12,
        'in_values': [-3.0, -1.0, 0.0, 2.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 13.0],
        'out_values': [98.0, 99.0, 100.0, 102.0, 104.0, 105.0, 106.0, 107.0, 108.0, 109.0, 110.0, 111.0],
        'longIdentifier': ''
        }


def test_measurement_compu_method_tab_verb():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
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
    session = parser.parseFromString(DATA)
    meas = Measurement(session, "N")
    assert meas.compuMethod == {
        'format': '%12.0', 'type': 'TAB_VERB', 'unit': '', 'default_value': "unknown signal type",
        'num_values': 6, 'ranges': False,
        'in_values': [2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
        'text_values': ['red', 'orange', 'yellow', 'green', 'blue', 'violet'],
        'longIdentifier': 'Verbal conversion with default value'
        }


def test_measurement_compu_method_tab_verb_range():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
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
    session = parser.parseFromString(DATA)
    meas = Measurement(session, "N")
    assert meas.compuMethod == {
        'format': '%4.2', 'type': 'TAB_VERB', 'unit': '', 'default_value': "out of range value",
        'num_values': 11, 'ranges': True,
        'lower_values': [0.0, 2.0, 4.0, 14.0, 18.0, 100.0, 101.0, 102.0, 103.0, 104.0, 105.0],
        'text_values': ['Zero_to_one', 'two_to_three', 'four_to_seven', 'fourteen_to_seventeen',
            'eigteen_to_ninetynine', 'hundred', 'hundredone', 'hundredtwo', 'hundredthree',
            'hundredfour', 'hundredfive'],
        'upper_values': [1.0, 3.0, 7.0, 17.0, 99.0, 100.0, 101.0, 102.0, 103.0, 104.0, 105.0],
        'longIdentifier': 'verbal range with default value'
        }

