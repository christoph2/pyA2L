#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""These test-cases are based on the examples from ASAM MCD-2MC Version 1.6 specification.
"""
import os
from setuptools import sandbox
import pytest

import pya2l.model as model
from pya2l.a2l_listener import ParserWrapper, A2LListener, cut_a2ml, delist

# pylint: disable=C0111
# pylint: disable=C0103


@pytest.mark.first
def test_code_generation():
    """Generate lexers and parsers as a side-effect."""
    sandbox.run_setup("setup.py", ["antlr"])
    lexers = [os.path.join("pya2l", p) for p in ["a2lLexer.py", "amlLexer.py"]]
    parsers = [os.path.join("pya2l", p) for p in ["a2lParser.py", "amlParser.py"]]
    assert all([os.path.exists(p) for p in lexers + parsers])

def test_delist_empty():
    DATA = []
    assert delist(DATA, False) == []

def test_delist_empty_scalar():
    DATA = []
    assert delist(DATA, True) == None

def test_delist_single():
    DATA = ['1111']
    assert delist(DATA, False) == ['1111']

def test_delist_single_scalar():
    DATA = ['1111']
    assert delist(DATA, True) == '1111'

def test_delist_multiple():
    DATA = ['1111', '2222', '3333', '4444']
    assert delist(DATA, False) == ['1111']

def test_delist_multiple_scalar():
    DATA = ['1111', '2222', '3333', '4444']
    assert delist(DATA, True) == '1111'

def test_addr_epk():
    parser = ParserWrapper('a2l', 'addrEpk', A2LListener, debug = False)
    DATA = "ADDR_EPK 0x145678"
    session = parser.parseFromString(DATA)
    res = session.query(model.AddrEpk).all()
    assert len(res) == 1
    assert res[0].address == 0x145678

def test_alignment_byte():
    parser = ParserWrapper('a2l', 'alignmentByte', A2LListener, debug = False)
    DATA = "ALIGNMENT_BYTE 4 /* bytes have a 4-byte alignment */"
    session = parser.parseFromString(DATA)
    res = session.query(model.AlignmentByte).all()
    assert len(res) == 1
    assert res[0].alignmentBorder == 4

def test_alignment_float32_ieee():
    parser = ParserWrapper('a2l', 'alignmentFloat32Ieee', A2LListener, debug = False)
    DATA = "ALIGNMENT_FLOAT32_IEEE 4 /* 32bit floats have a 4-byte alignment */"
    session = parser.parseFromString(DATA)
    res = session.query(model.AlignmentFloat32Ieee).all()
    assert len(res) == 1
    assert res[0].alignmentBorder == 4

def test_alignment_float64_ieee():
    parser = ParserWrapper('a2l', 'alignmentFloat64Ieee', A2LListener, debug = False)
    DATA = "ALIGNMENT_FLOAT64_IEEE 4 /* 64bit floats have a 4-byte alignment */"
    session = parser.parseFromString(DATA)
    res = session.query(model.AlignmentFloat64Ieee).all()
    assert len(res) == 1
    assert res[0].alignmentBorder == 4

def test_alignment_int64():
    parser = ParserWrapper('a2l', 'alignmentInt64', A2LListener, debug = False)
    DATA = "ALIGNMENT_INT64 4 /* int64 have a 4-byte alignment */"
    session = parser.parseFromString(DATA)
    res = session.query(model.AlignmentInt64).all()
    assert len(res) == 1
    assert res[0].alignmentBorder == 4

def test_alignment_long():
    parser = ParserWrapper('a2l', 'alignmentLong', A2LListener, debug = False)
    DATA = "ALIGNMENT_LONG 8 /* longs have a 8-byte alignment */"
    session = parser.parseFromString(DATA)
    res = session.query(model.AlignmentLong).all()
    assert len(res) == 1
    assert res[0].alignmentBorder == 8

def test_alignment_word():
    parser = ParserWrapper('a2l', 'alignmentWord', A2LListener, debug = False)
    DATA = "ALIGNMENT_WORD 4 /* words have a 4-byte alignment */"
    session = parser.parseFromString(DATA)
    res = session.query(model.AlignmentWord).all()
    assert len(res) == 1
    assert res[0].alignmentBorder == 4

def test_annotation():
    parser = ParserWrapper('a2l', 'characteristic', A2LListener, debug = False)
    DATA = '''
    /begin CHARACTERISTIC annotation.example1 "richtig"
        VALUE             /* type: constant */
        0x0408            /* address        */
        DAMOS_FW          /* deposit        */
        5.0               /* max_diff       */
        FACTOR01          /* conversion     */
        0.0               /* lower limit    */
        255.0             /* upper limit    */
        /begin ANNOTATION
            ANNOTATION_LABEL "Luftsprungabhängigkeit"
            ANNOTATION_ORIGIN "Graf Zeppelin"
            /begin ANNOTATION_TEXT
                "Die luftklasseabhängigen Zeitkonstanten t_hinz\r\n"
                "& t_kunz können mit Hilfe von Luftsprüngen ermittelt werden.\r\n"
                "Die Taupunktendezeiten in großen Flughöhen sind stark schwankend"
            /end ANNOTATION_TEXT
        /end ANNOTATION
        /begin ANNOTATION
            ANNOTATION_LABEL "Taupunktendezeiten"
            /begin ANNOTATION_TEXT
                "Flughöhe Taupunktendezeit\r\n"
                " 13000ft 20 sec\r\n"
                " 25000ft 40 sec\r\n"
                " 35000ft 12 sec"
            /end ANNOTATION_TEXT
        /end ANNOTATION
    /end CHARACTERISTIC
    '''
    session = parser.parseFromString(DATA)
    chx = session.query(model.Characteristic).filter(model.Characteristic.name == "annotation.example1").first()
    assert chx.name == 'annotation.example1'
    assert chx.longIdentifier == 'richtig'
    assert chx.type == 'VALUE'
    assert chx.address == 0x0408
    assert chx.deposit == 'DAMOS_FW'
    assert chx.maxDiff == 5.0
    assert chx.conversion == 'FACTOR01'
    assert chx.lowerLimit == 0.0
    assert chx.upperLimit == 255.0
    assert len(chx.annotation) == 2
    an0, an1 = chx.annotation
    assert an0.annotation_label.label == 'Luftsprungabhängigkeit'
    assert an0.annotation_origin.origin == 'Graf Zeppelin'
    assert an0.annotation_text.text == [
        'Die luftklasseabhängigen Zeitkonstanten t_hinz\r\n',
        '& t_kunz können mit Hilfe von Luftsprüngen ermittelt werden.\r\n',
        'Die Taupunktendezeiten in großen Flughöhen sind stark schwankend'
    ]
    assert an1.annotation_label.label == 'Taupunktendezeiten'
    assert an1.annotation_origin is None
    assert an1.annotation_text.text == [
        'Flughöhe Taupunktendezeit\r\n',
        ' 13000ft 20 sec\r\n',
        ' 25000ft 40 sec\r\n',
        ' 35000ft 12 sec'
    ]

def test_annotation_label():
    parser = ParserWrapper('a2l', 'annotationLabel', A2LListener, debug = False)
    DATA = 'ANNOTATION_LABEL    "Calibration Note"'
    session = parser.parseFromString(DATA)
    res = session.query(model.AnnotationLabel).first()
    assert res.label == 'Calibration Note'

def test_annotation_origin():
    parser = ParserWrapper('a2l', 'annotationOrigin', A2LListener, debug = False)
    DATA = 'ANNOTATION_ORIGIN   "from the calibration planning department"'
    session = parser.parseFromString(DATA)
    res = session.query(model.AnnotationOrigin).all()
    assert len(res) == 1
    assert res[0].origin == 'from the calibration planning department'

def test_annotation_text():
    # TODO: Fix lexer ""
    parser = ParserWrapper('a2l', 'characteristic', A2LListener, debug = False)
    DATA = '''
    /begin CHARACTERISTIC PUMCD "Pump characteristic map"
        MAP    /* type: characteristic map */
        0x7140   /* address */
        DAMOS_KF  /* deposit */
        100.0    /* max_diff */
        VOLTAGE   /* conversion */
        0.0    /* lower limit */
        5000.0   /* upper limit */
        /begin ANNOTATION
            ANNOTATION_LABEL "Calibration Note"
            /begin ANNOTATION_TEXT
                "The very nice ASAM MCD-2MC Specification."
                "Text.\r\n"
                "In case of a quotation mark"
//                "use \" or "" to mark it."
            /end ANNOTATION_TEXT
        /end ANNOTATION
    /end CHARACTERISTIC
    '''
    session = parser.parseFromString(DATA)
    chx = session.query(model.Characteristic).filter(model.Characteristic.name == "PUMCD").first()
    assert chx.name == 'PUMCD'
    assert chx.longIdentifier == 'Pump characteristic map'
    assert chx.type == 'MAP'
    assert chx.address == 0x7140
    assert chx.deposit == 'DAMOS_KF'
    assert chx.maxDiff == 100.0
    assert chx.conversion == 'VOLTAGE'
    assert chx.lowerLimit == 0.0
    assert chx.upperLimit == 5000.0
    assert len(chx.annotation) == 1
    an0 = chx.annotation[0]
    assert an0.annotation_label.label == 'Calibration Note'
    assert an0.annotation_origin is None
    assert an0.annotation_text.text == [
        "The very nice ASAM MCD-2MC Specification.",
        "Text.\r\n",
        "In case of a quotation mark",
#        "use \" or "" to mark it."
    ]

def test_array_size():
    parser = ParserWrapper('a2l', 'measurement', A2LListener, debug = False)
    DATA = """
    /begin MEASUREMENT
        N /* name */
        "Engine speed" /* long identifier */
        UWORD /* datatype */
        R_SPEED_3 /* conversion */
        2 /* resolution */
        2.5 /* accuracy */
        120.0 /* lower limit */
        8400.0 /* upper limit */
        ARRAY_SIZE 8 /* array of 8 values */
        BIT_MASK 0x0FFF
        BYTE_ORDER MSB_FIRST
        /begin FUNCTION_LIST
            ID_ADJUSTM
            FL_ADJUSTM
        /end FUNCTION_LIST
/*
        /begin IF_DATA ISO
            SND
            0x10
            0x00
            0x05
            0x08
            RCV
            4
            long
        /end IF_DATA
*/
    /end MEASUREMENT
    """
    session = parser.parseFromString(DATA)
    meas = session.query(model.Measurement).filter(model.Measurement.name == "N").first()
    assert meas.name == "N"
    assert meas.longIdentifier == "Engine speed"
    assert meas.datatype == "UWORD"
    assert meas.conversion == "R_SPEED_3"
    assert meas.resolution == 2
    assert meas.accuracy == 2.5
    assert meas.lowerLimit == 120
    assert meas.upperLimit == 8400.0
    assert meas.array_size.number == 8
    assert meas.bit_mask.mask == 0x0fff
    assert meas.byte_order.byteOrder == "MSB_FIRST"
    fl = meas.function_list
    assert fl.name == ['ID_ADJUSTM', 'FL_ADJUSTM']

def test_axis_descr():
    parser = ParserWrapper('a2l', 'axisDescr', A2LListener, debug = False)
    DATA = """
    /begin AXIS_DESCR STD_AXIS /* Standard axis points */
        N                   /* Reference to input quantity */
        CONV_N              /* Conversion */
        14                  /* Max.number of axis points*/
        0.0                 /* Lower limit */
        5800.0              /* Upper limit*/
        MAX_GRAD    20.0    /* Axis: maximum gradient*/
    /end AXIS_DESCR
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.AxisDescr).all()
    assert len(res) == 1
    ad = res[0]
    assert ad.attribute == 'STD_AXIS'
    assert ad.inputQuantity == 'N'
    assert ad.conversion == 'CONV_N'
    assert ad.maxAxisPoints == 14
    assert ad.lowerLimit == 0.0
    assert ad.upperLimit == 5800.0
    assert ad.max_grad.maxGradient == 20.0

def test_axis_pts():
    parser = ParserWrapper('a2l', 'axisPts', A2LListener, debug = False)
    DATA = """
    /begin AXIS_PTS STV_N /* name */
        "axis points distribution speed"    /* long identifier */
        0x9876 /* address */
        N /* input quantity */
        DAMOS_SST /* deposit */
        100.0 /* maxdiff */
        R_SPEED /* conversion */
        21 /* maximum number of axis points */
        0.0 /* lower limit */
        5800.0 /* upper limit */
        GUARD_RAILS /* uses guard rails*/
        REF_MEMORY_SEGMENT Data3
        /begin FUNCTION_LIST
            ID_ADJUSTM
            FL_ADJUSTM
            SPEED_LIM
        /end FUNCTION_LIST
/*
        /begin IF_DATA DIM
            EXTERNAL
            DIRECT
        /end IF_DATA
*/
        CALIBRATION_ACCESS CALIBRATION
    /end AXIS_PTS
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.AxisPts).all()
    assert len(res) == 1
    ap = res[0]
    assert ap.name == 'STV_N'
    assert ap.longIdentifier == 'axis points distribution speed'
    assert ap.address == 0x9876
    assert ap.inputQuantity == 'N'
    assert ap.depositAttr == "DAMOS_SST"
    assert ap.deposit is None
    assert ap.maxDiff == 100.0
    assert ap.conversion == 'R_SPEED'
    assert ap.maxAxisPoints == 21
    assert ap.lowerLimit == 0.0
    assert ap.upperLimit == 5800.0
    assert ap.guard_rails is not None
    assert ap.ref_memory_segment.name == 'Data3'
    fl = ap.function_list
    assert fl.name == ['ID_ADJUSTM', 'FL_ADJUSTM', 'SPEED_LIM']
    assert ap.calibration_access.type == "CALIBRATION"

def test_axis_pts_ref():
    parser = ParserWrapper('a2l', 'characteristic', A2LListener, debug = False)
    DATA = """
        /begin CHARACTERISTIC
            TORQUE              /* name */
            "Torque limitation" /* long identifier */
            CURVE               /* type*/
            0x1432              /* address */
            DAMOS_GKL           /* deposit */
            0.2                 /* maxdiff */
            R_TORQUE            /* conversion */
            0.0                 /* lower limit */
            43.0                /* upper limit */
/*
            /begin IF_DATA DIM
                EXTERNAL
                INDIRECT
            /end IF_DATA
*/
            /begin AXIS_DESCR   /* description of X-axis points */
                COM_AXIS        /* common axis points */
                N               /* input quantity */
                CONV_N          /* conversion */
                14              /* max. no. of axis p.*/
                0.0             /* lower limit */
                5800.0          /* upper limit */
                AXIS_PTS_REF GRP_N
            /end AXIS_DESCR
        /end CHARACTERISTIC
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.Characteristic).all()
    assert len(res) == 1
    chx = res[0]
    assert chx.name == 'TORQUE'
    assert chx.longIdentifier == 'Torque limitation'
    assert chx.type == 'CURVE'
    assert chx.address == 0x1432
    assert chx.deposit == 'DAMOS_GKL'
    assert chx.maxDiff == 0.2
    assert chx.conversion == 'R_TORQUE'
    assert chx.lowerLimit == 0.0
    assert chx.upperLimit == 43.0
    assert len(chx.axis_descr) == 1
    descr = chx.axis_descr[0]
    assert descr.attribute == 'COM_AXIS'
    assert descr.inputQuantity == 'N'
    assert descr.conversion == 'CONV_N'
    assert descr.maxAxisPoints == 14
    assert descr.lowerLimit == 0.0
    assert descr.upperLimit == 5800.0
    assert descr.axis_pts_ref.axisPoints == 'GRP_N'

def test_axis_pts_x():
    parser = ParserWrapper('a2l', 'axisPtsX', A2LListener, debug = False)
    DATA = """AXIS_PTS_X 3
        ULONG
        INDEX_INCR
        DIRECT
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.AxisPtsX).all()
    assert len(res) == 1
    pt = res[0]
    assert pt.position == 3
    assert pt.datatype == 'ULONG'
    assert pt.indexIncr == 'INDEX_INCR'
    assert pt.addressing == 'DIRECT'

def test_axis_pts_y():
    parser = ParserWrapper('a2l', 'axisPtsY', A2LListener, debug = False)
    DATA = """AXIS_PTS_Y 3
        ULONG
        INDEX_INCR
        DIRECT
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.AxisPtsY).all()
    assert len(res) == 1
    pt = res[0]
    assert pt.position == 3
    assert pt.datatype == 'ULONG'
    assert pt.indexIncr == 'INDEX_INCR'
    assert pt.addressing == 'DIRECT'

def test_axis_pts_z():
    parser = ParserWrapper('a2l', 'axisPtsZ', A2LListener, debug = False)
    DATA = """AXIS_PTS_Z 3
        ULONG
        INDEX_INCR
        DIRECT
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.AxisPtsZ).all()
    assert len(res) == 1
    pt = res[0]
    assert pt.position == 3
    assert pt.datatype == 'ULONG'
    assert pt.indexIncr == 'INDEX_INCR'
    assert pt.addressing == 'DIRECT'

def test_axis_pts_4():
    parser = ParserWrapper('a2l', 'axisPts4', A2LListener, debug = False)
    DATA = """AXIS_PTS_4 3
        ULONG
        INDEX_INCR
        DIRECT
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.AxisPts4).all()
    assert len(res) == 1
    pt = res[0]
    assert pt.position == 3
    assert pt.datatype == 'ULONG'
    assert pt.indexIncr == 'INDEX_INCR'
    assert pt.addressing == 'DIRECT'

def test_axis_pts_5():
    parser = ParserWrapper('a2l', 'axisPts5', A2LListener, debug = False)
    DATA = """AXIS_PTS_5 3
        ULONG
        INDEX_INCR
        DIRECT
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.AxisPts5).all()
    assert len(res) == 1
    pt = res[0]
    assert pt.position == 3
    assert pt.datatype == 'ULONG'
    assert pt.indexIncr == 'INDEX_INCR'
    assert pt.addressing == 'DIRECT'

def test_axis_rescale_x():
    parser = ParserWrapper('a2l', 'axisRescaleX', A2LListener, debug = False)
    DATA = """AXIS_RESCALE_X 3
        UBYTE
        5
        INDEX_INCR
        DIRECT
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.AxisRescaleX).all()
    assert len(res) == 1
    pt = res[0]
    assert pt.position == 3
    assert pt.datatype == 'UBYTE'
    assert pt.maxNumberOfRescalePairs == 5
    assert pt.indexIncr == 'INDEX_INCR'
    assert pt.addressing == 'DIRECT'

def test_axis_rescale_y():
    parser = ParserWrapper('a2l', 'axisRescaleY', A2LListener, debug = False)
    DATA = """AXIS_RESCALE_Y 3
        UBYTE
        5
        INDEX_INCR
        DIRECT
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.AxisRescaleY).all()
    assert len(res) == 1
    pt = res[0]
    assert pt.position == 3
    assert pt.datatype == 'UBYTE'
    assert pt.maxNumberOfRescalePairs == 5
    assert pt.indexIncr == 'INDEX_INCR'
    assert pt.addressing == 'DIRECT'

def test_axis_rescale_z():
    parser = ParserWrapper('a2l', 'axisRescaleZ', A2LListener, debug = False)
    DATA = """AXIS_RESCALE_Z 3
        UBYTE
        5
        INDEX_INCR
        DIRECT
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.AxisRescaleZ).all()
    assert len(res) == 1
    pt = res[0]
    assert pt.position == 3
    assert pt.datatype == 'UBYTE'
    assert pt.maxNumberOfRescalePairs == 5
    assert pt.indexIncr == 'INDEX_INCR'
    assert pt.addressing == 'DIRECT'

def test_axis_rescale_4():
    parser = ParserWrapper('a2l', 'axisRescale4', A2LListener, debug = False)
    DATA = """AXIS_RESCALE_4 3
        UBYTE
        5
        INDEX_INCR
        DIRECT
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.AxisRescale4).all()
    assert len(res) == 1
    pt = res[0]
    assert pt.position == 3
    assert pt.datatype == 'UBYTE'
    assert pt.maxNumberOfRescalePairs == 5
    assert pt.indexIncr == 'INDEX_INCR'
    assert pt.addressing == 'DIRECT'

def test_axis_rescale_5():
    parser = ParserWrapper('a2l', 'axisRescale5', A2LListener, debug = False)
    DATA = """AXIS_RESCALE_5 3
        UBYTE
        5
        INDEX_INCR
        DIRECT
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.AxisRescale5).all()
    assert len(res) == 1
    pt = res[0]
    assert pt.position == 3
    assert pt.datatype == 'UBYTE'
    assert pt.maxNumberOfRescalePairs == 5
    assert pt.indexIncr == 'INDEX_INCR'
    assert pt.addressing == 'DIRECT'

def test_bitmask():
    parser = ParserWrapper('a2l', 'bitMask', A2LListener, debug = False)
    DATA = "BIT_MASK 0x40"
    session = parser.parseFromString(DATA)
    res = session.query(model.BitMask).all()
    assert len(res) == 1
    assert res[0].mask == 0x40

def test_bit_operation_right_shift():
    parser = ParserWrapper('a2l', 'bitOperation', A2LListener, debug = False)
    DATA = """
    /begin BIT_OPERATION
        RIGHT_SHIFT 4 /*4 positions*/
        SIGN_EXTEND
    /end BIT_OPERATION
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.BitOperation).all()
    assert len(res) == 1
    assert res[0].right_shift.bitcount == 4
    assert res[0].sign_extend is not None

def test_bit_operation_left_shift():
    parser = ParserWrapper('a2l', 'bitOperation', A2LListener, debug = False)
    DATA = """
    /begin BIT_OPERATION
        LEFT_SHIFT 4 /*4 positions*/
        SIGN_EXTEND
    /end BIT_OPERATION
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.BitOperation).all()
    assert len(res) == 1
    assert res[0].left_shift.bitcount == 4
    assert res[0].sign_extend is not None

def test_calibration_access():
    parser = ParserWrapper('a2l', 'calibrationAccess', A2LListener, debug = False)
    DATA = "CALIBRATION_ACCESS CALIBRATION"
    session = parser.parseFromString(DATA)
    res = session.query(model.CalibrationAccess).all()
    assert len(res) == 1
    assert res[0].type == "CALIBRATION"

def test_calibration_handle():
    parser = ParserWrapper('a2l', 'calibrationHandle', A2LListener, debug = False)
    DATA = """
    /begin CALIBRATION_HANDLE
        0x10000 /* start address of pointer table */
        0x200   /* length of pointer table */
        0x4     /* size of one pointer table entry */
        0x30000 /* start address of flash section */
        0x20000 /* length of flash section */
        CALIBRATION_HANDLE_TEXT "Nmot"
    /end CALIBRATION_HANDLE
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.CalibrationHandle).all()
    assert len(res) == 1
    ch = res[0]
    assert ch.handle == [65536, 512, 4, 196608, 131072]
    assert ch.calibration_handle_text.text == "Nmot"

def test_calibration_handle_text():
    parser = ParserWrapper('a2l', 'calibrationHandleText', A2LListener, debug = False)
    DATA = 'CALIBRATION_HANDLE_TEXT "Torque"'
    session = parser.parseFromString(DATA)
    res = session.query(model.CalibrationHandleText).all()
    assert len(res) == 1
    assert res[0].text == "Torque"

def test_calibration_method():
    parser = ParserWrapper('a2l', 'calibrationMethod', A2LListener, debug = False)
    DATA = """
    /begin CALIBRATION_METHOD
        "InCircuit"
        2
        /begin CALIBRATION_HANDLE
            0x10000     /* start address of pointer table */
            0x200       /* length of pointer table */
            0x4         /* size of one pointer table entry */
            0x10000     /* start address of flash section */
            0x10000     /* length of flash section */
        /end CALIBRATION_HANDLE
    /end CALIBRATION_METHOD
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.CalibrationMethod).all()
    assert len(res) == 1
    cm = res[0]
    assert cm.method == 'InCircuit'
    assert cm.version == 2
    assert cm.calibration_handle[0].handle == [65536, 512, 4, 65536, 65536]

def test_characteristic():
    parser = ParserWrapper('a2l', 'characteristic', A2LListener, debug = False)
    DATA = """
    /begin CHARACTERISTIC PUMKF     /* name */
        "Pump characteristic map"   /* long identifier */
        MAP                         /* type */
        0x7140                      /* address */
        DAMOS_KF                    /* deposit */
        100.0                       /* maxdiff */
        R_VOLTAGE                   /* conversion */
        0.0                         /* lower limit */
        5000.0                      /* upper limit */
        MAX_REFRESH 3 15            /* 15 msec */
        /begin DEPENDENT_CHARACTERISTIC
        "sin(X1)"
            ALPHA
        /end DEPENDENT_CHARACTERISTIC
        /begin VIRTUAL_CHARACTERISTIC
            "sqrt(X1)"
            B_AREA
        /end VIRTUAL_CHARACTERISTIC
        REF_MEMORY_SEGMENT Data1
        /begin FUNCTION_LIST
            NL_ADJUSTMENT
            FL_ADJUSTMENT
            SPEED_LIM
        /end FUNCTION_LIST
/*
        /begin IF_DATA
            DIM
            EXTERNAL
            INDIRECT
        /end IF_DATA
*/
        /begin AXIS_DESCR   /* description of X-axis points */
            STD_AXIS        /* standard axis points */
            N               /* reference to input quantity */
            CON_N           /* conversion */
            13              /* maximum number of axis points*/
            0.0             /* lower limit */
            5800.0          /* upper limit */
            MAX_GRAD 20.0   /* X-axis: maximum gradient */
        /end AXIS_DESCR
        /begin AXIS_DESCR   /* description of Y-axis points */
            STD_AXIS        /* standard axis points */
            AMOUNT          /* reference to input quantity */
            CON_ME          /* conversion */
            17              /* maximum number of axis points*/
            0.0             /* lower limit */
            43.0            /* upper limit */
        /end AXIS_DESCR
    /end CHARACTERISTIC
    """
    session = parser.parseFromString(DATA)
    res = session.query(model.Characteristic).all()
    assert len(res) == 1
    cr = res[0]
    assert cr.name == 'PUMKF'
    assert cr.longIdentifier == 'Pump characteristic map'
    assert cr.type == 'MAP'
    assert cr.address == 28992
    assert cr.deposit == 'DAMOS_KF'
    assert cr.maxDiff == 100.0
    assert cr.conversion == 'R_VOLTAGE'
    assert cr.lowerLimit == 0.0
    assert cr.upperLimit == 5000.0
    ax = cr.axis_descr
    assert ax[0].attribute == 'STD_AXIS'
    assert ax[0].inputQuantity == 'N'
    assert ax[0].conversion == 'CON_N'
    assert ax[0].maxAxisPoints == 13
    assert ax[0].lowerLimit == 0.0
    assert ax[0].upperLimit == 5800.0
    assert ax[1].attribute == 'STD_AXIS'
    assert ax[1].inputQuantity == 'AMOUNT'
    assert ax[1].conversion == 'CON_ME'
    assert ax[1].maxAxisPoints == 17
    assert ax[1].lowerLimit == 0.0
    assert ax[1].upperLimit == 43.0

def test_calibration_coeffs():
    parser = ParserWrapper('a2l', 'coeffs', A2LListener, debug = False)
    DATA = """
    COEFFS 0 4 8 0 0 5
    /* Control unit internal values of revolutions (INT) is calculated from */
    /* physical values (PHYS: unit of PHYS is [rpm]) as follows: */
    /* INT = (4/5) * PHYS/[rpm] + (8/5) */
    /* inverted: PHYS/[rpm] = 1.25 * INT - 2.0 */
    """
    session = parser.parseFromString(DATA)
    coeffs = session.query(model.Coeffs).first()
    assert coeffs.a == 0.0
    assert coeffs.b == 4.0
    assert coeffs.c == 8.0
    assert coeffs.d == 0.0
    assert coeffs.e == 0.0
    assert coeffs.f == 5.0

def test_calibration_coeffs_linear():
    parser = ParserWrapper('a2l', 'coeffsLinear', A2LListener, debug = False)
    DATA = """
    COEFFS_LINEAR 1.25 -2.0
    /* The physical value (PHYS) with unit is calculated from the */
    /* control unit’s internal value of revolutions (INT) as follows: */
    /* PHYS = 1.25 * INT – 2.0 */
    """
    session = parser.parseFromString(DATA)
    coeffs = session.query(model.CoeffsLinear).first()
    assert coeffs.a == 1.25
    assert coeffs.b == -2.0

def test_comparision_quantity():
    parser = ParserWrapper('a2l', 'comparisonQuantity', A2LListener, debug = False)
    DATA = """
    COMPARISON_QUANTITY Test
    """
    session = parser.parseFromString(DATA)
    cq = session.query(model.ComparisonQuantity).first()
    assert cq.name == "Test"

def test_compu_method():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_METHOD TMPCON1 /* name */
            "conversion method for engine temperature"
            TAB_NOINTP /* convers_type */
            "%4.2" /* display format */
            "°C" /* physical unit */
            COMPU_TAB_REF MOTEMP1
        /end COMPU_METHOD

        /begin COMPU_METHOD CM_IDENTITY /* name */
            "conversion method identity (no formula)"
            IDENTICAL /* convers_type */
            "%4.0" /* display format */
            "" /* physical unit */
        /end COMPU_METHOD

        /begin COMPU_METHOD CM_LINFUNC /* name */
            "conversion method for linear function"
            LINEAR /* convers_type */
            "%4.0" /* display format */
            "rpm" /* physical unit */
            COEFFS_LINEAR 2.0 5.0
        /end COMPU_METHOD

        /begin COMPU_METHOD TMPCON2 /* name */
            "conversion method for air temperature"
            FORM /* convers_type */
            "%4.2" /* display format */
            "°C" /* physical unit */
            /begin FORMULA
                "3*X1/100 + 22.7"
            /end FORMULA
        /end COMPU_METHOD

        /begin COMPU_METHOD CM_DiagStatus /* name */
            "" /*convers_type */
            TAB_VERB /*convers_type */
            "%0.0" /* display format */
            "" /* physical unit */
            COMPU_TAB_REF CT_DiagStatus
        /end COMPU_METHOD

        /begin COMPU_METHOD CM_RPM /* name */
            "conversion method for engine rpm"
            TAB_INTP /*convers_type */
            "%7.1" /* display format */
            "rpm " /* physical unit */
            COMPU_TAB_REF CT_RPM
        /end COMPU_METHOD

        /begin COMPU_METHOD CM_NM /* name */
            " conversion method for air temperature "
            TAB_INTP /* convers_type */
            "%7.1" /* display format */
            "nm " /* physical unit */
            COMPU_TAB_REF CT_NM
        /end COMPU_METHOD

        /begin COMPU_METHOD FIXED_UW_03
            "Conversion method for FIXED_UW_03"
            RAT_FUNC /* convers_type */
            "%8.3" /* display format */
            "NO_PHYSICAL_QTY"
            COEFFS 0 8 0 0 0 1
        /end COMPU_METHOD

        /begin COMPU_METHOD BYTE_   /* TODO: Allow reserved words as IDENTs. */
            "Conversion method for BYTE"
            RAT_FUNC /* convers_type */
            "%3.0" /* display format */
            "NO_PHYSICAL_QTY"
            COEFFS 0 1 0 0 0 1
        /end COMPU_METHOD

        /begin COMPU_METHOD SHORTINT
            "Conversion method for SHORTINT"
            RAT_FUNC
            "%4.0"
            "NO_PHYSICAL_QTY"
            COEFFS 0 1 0 0 0 1
        /end COMPU_METHOD

        /begin COMPU_METHOD WORD_   /* TODO: Allow reserved words as IDENTs. */
            "Conversion method for WORD"
            RAT_FUNC
            "%5.0"
            "NO_PHYSICAL_QTY"
            COEFFS 0 1 0 0 0 1
        /end COMPU_METHOD

        /begin COMPU_METHOD INTEGER
            "Conversion method for INTEGER"
            RAT_FUNC
            "%6.0"
            "NO_PHYSICAL_QTY"
            COEFFS 0 1 0 0 0 1
        /end COMPU_METHOD

        /begin COMPU_METHOD LONGWORD
            "Conversion method for LONGWORD"
            RAT_FUNC
            "%10.0"
            "NO_PHYSICAL_QTY"
            COEFFS 0 1 0 0 0 1
        /end COMPU_METHOD

        /begin COMPU_METHOD LONGINT
            "Conversion method for LONGINT"
            RAT_FUNC
            "%11.0"
            "NO_PHYSICAL_QTY"
            COEFFS 0 1 0 0 0 1
            /end COMPU_METHOD
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    mod = session.query(model.Module).first()
    cm = mod.compu_method
    assert len(cm) == 14

    assert cm[0].name == 'TMPCON1'
    assert cm[0].longIdentifier == 'conversion method for engine temperature'
    assert cm[0].conversionType == 'TAB_NOINTP'
    assert cm[0].format == '%4.2'
    assert cm[0].unit == '°C'
    assert cm[0].compu_tab_ref.conversionTable == "MOTEMP1"

    assert cm[1].name == 'CM_IDENTITY'
    assert cm[1].longIdentifier == 'conversion method identity (no formula)'
    assert cm[1].conversionType == 'IDENTICAL'
    assert cm[1].format == '%4.0'
    assert cm[1].unit == ''

    assert cm[2].name == 'CM_LINFUNC'
    assert cm[2].longIdentifier == 'conversion method for linear function'
    assert cm[2].conversionType == 'LINEAR'
    assert cm[2].format == '%4.0'
    assert cm[2].unit == 'rpm'
    assert cm[2].coeffs_linear.a == 2.0
    assert cm[2].coeffs_linear.b == 5.0

    assert cm[3].name == 'TMPCON2'
    assert cm[3].longIdentifier == 'conversion method for air temperature'
    assert cm[3].conversionType == 'FORM'
    assert cm[3].format == '%4.2'
    assert cm[3].unit == '°C'
    assert cm[3].formula.f_x == "3*X1/100 + 22.7"

    assert cm[4].name == 'CM_DiagStatus'
    assert cm[4].longIdentifier == ''
    assert cm[4].conversionType == 'TAB_VERB'
    assert cm[4].format == '%0.0'
    assert cm[4].unit == ''
    assert cm[4].compu_tab_ref.conversionTable == "CT_DiagStatus"

    assert cm[5].name == 'CM_RPM'
    assert cm[5].longIdentifier == 'conversion method for engine rpm'
    assert cm[5].conversionType == 'TAB_INTP'
    assert cm[5].format == '%7.1'
    assert cm[5].unit == 'rpm '
    assert cm[5].compu_tab_ref.conversionTable == "CT_RPM"

    assert cm[6].name == 'CM_NM'
    assert cm[6].longIdentifier == ' conversion method for air temperature '
    assert cm[6].conversionType == 'TAB_INTP'
    assert cm[6].format == '%7.1'
    assert cm[6].unit == 'nm '
    assert cm[6].compu_tab_ref.conversionTable == "CT_NM"

    assert cm[7].name == 'FIXED_UW_03'
    assert cm[7].longIdentifier == 'Conversion method for FIXED_UW_03'
    assert cm[7].conversionType == 'RAT_FUNC'
    assert cm[7].format == '%8.3'
    assert cm[7].unit == 'NO_PHYSICAL_QTY'
    assert cm[7].coeffs.a == 0
    assert cm[7].coeffs.b == 8
    assert cm[7].coeffs.c == 0
    assert cm[7].coeffs.d == 0
    assert cm[7].coeffs.e == 0
    assert cm[7].coeffs.f == 1

    assert cm[8].name == 'BYTE_'
    assert cm[8].longIdentifier == 'Conversion method for BYTE'
    assert cm[8].conversionType == 'RAT_FUNC'
    assert cm[8].format == '%3.0'
    assert cm[8].unit == 'NO_PHYSICAL_QTY'
    assert cm[8].coeffs.a == 0
    assert cm[8].coeffs.b == 1
    assert cm[8].coeffs.c == 0
    assert cm[8].coeffs.d == 0
    assert cm[8].coeffs.e == 0
    assert cm[8].coeffs.f == 1

    assert cm[9].name == 'SHORTINT'
    assert cm[9].longIdentifier == 'Conversion method for SHORTINT'
    assert cm[9].conversionType == 'RAT_FUNC'
    assert cm[9].format == '%4.0'
    assert cm[9].unit == 'NO_PHYSICAL_QTY'
    assert cm[9].coeffs.a == 0
    assert cm[9].coeffs.b == 1
    assert cm[9].coeffs.c == 0
    assert cm[9].coeffs.d == 0
    assert cm[9].coeffs.e == 0
    assert cm[9].coeffs.f == 1

    assert cm[10].name == 'WORD_'
    assert cm[10].longIdentifier == 'Conversion method for WORD'
    assert cm[10].conversionType == 'RAT_FUNC'
    assert cm[10].format == '%5.0'
    assert cm[10].unit == 'NO_PHYSICAL_QTY'
    assert cm[10].coeffs.a == 0
    assert cm[10].coeffs.b == 1
    assert cm[10].coeffs.c == 0
    assert cm[10].coeffs.d == 0
    assert cm[10].coeffs.e == 0
    assert cm[10].coeffs.f == 1

    assert cm[11].name == 'INTEGER'
    assert cm[11].longIdentifier == 'Conversion method for INTEGER'
    assert cm[11].conversionType == 'RAT_FUNC'
    assert cm[11].format == '%6.0'
    assert cm[11].unit == 'NO_PHYSICAL_QTY'
    assert cm[11].coeffs.a == 0
    assert cm[11].coeffs.b == 1
    assert cm[11].coeffs.c == 0
    assert cm[11].coeffs.d == 0
    assert cm[11].coeffs.e == 0
    assert cm[11].coeffs.f == 1

    assert cm[12].name == 'LONGWORD'
    assert cm[12].longIdentifier == 'Conversion method for LONGWORD'
    assert cm[12].conversionType == 'RAT_FUNC'
    assert cm[12].format == '%10.0'
    assert cm[12].unit == 'NO_PHYSICAL_QTY'
    assert cm[12].coeffs.a == 0
    assert cm[12].coeffs.b == 1
    assert cm[12].coeffs.c == 0
    assert cm[12].coeffs.d == 0
    assert cm[12].coeffs.e == 0
    assert cm[12].coeffs.f == 1

    assert cm[13].name == 'LONGINT'
    assert cm[13].longIdentifier == 'Conversion method for LONGINT'
    assert cm[13].conversionType == 'RAT_FUNC'
    assert cm[13].format == '%11.0'
    assert cm[13].unit == 'NO_PHYSICAL_QTY'
    assert cm[13].coeffs.a == 0
    assert cm[13].coeffs.b == 1
    assert cm[13].coeffs.c == 0
    assert cm[13].coeffs.d == 0
    assert cm[13].coeffs.e == 0
    assert cm[13].coeffs.f == 1

def compareCompuTabPair(pair, inVal, outVal):
    return pair.inVal == inVal and pair.outVal == outVal

def test_compu_tab():
    parser = ParserWrapper('a2l', 'compuTab', A2LListener, debug = False)
    DATA = """
    /begin COMPU_TAB TT /* name */
        "conversion table for oil temperatures"
        TAB_NOINTP  /* convers_type */
        7           /* number_value_pairs */
        1 4.3 2 4.7 3 5.8 4 14.2 5 16.8 6 17.2 7 19.4 /* value pairs */
        DEFAULT_VALUE_NUMERIC 99.0
    /end COMPU_TAB
    """
    session = parser.parseFromString(DATA)
    ct = session.query(model.CompuTab).first()
    assert ct.name == 'TT'
    assert ct.longIdentifier == 'conversion table for oil temperatures'
    assert ct.conversionType == 'TAB_NOINTP'
    assert ct.numberValuePairs == 7
    assert ct.default_value_numeric.display_value == 99.0
    assert len(ct.pairs) == ct.numberValuePairs
    p0, p1, p2, p3, p4, p5, p6 = ct.pairs
    assert compareCompuTabPair(p0, inVal = 1.0, outVal = 4.3) == True
    assert compareCompuTabPair(p1, inVal = 2.0, outVal = 4.7) == True
    assert compareCompuTabPair(p2, inVal = 3.0, outVal = 5.8) == True
    assert compareCompuTabPair(p3, inVal = 4.0, outVal = 14.2) == True
    assert compareCompuTabPair(p4, inVal = 5.0, outVal = 16.8) == True
    assert compareCompuTabPair(p5, inVal = 6.0, outVal = 17.2) == True
    assert compareCompuTabPair(p6, inVal = 7.0, outVal = 19.4) == True

def test_compu_tab_ref():
    parser = ParserWrapper('a2l', 'compuTabRef', A2LListener, debug = False)
    DATA = """COMPU_TAB_REF TEMP_TAB /*TEMP_TAB: conversion table*/"""
    session = parser.parseFromString(DATA)
    ctr = session.query(model.CompuTabRef).first()
    assert ctr.conversionTable == "TEMP_TAB"

def test_compu_v_tab():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
    DATA = """
    /begin MODULE testModule ""
        /begin COMPU_VTAB TT /* name */ "engine status conversion"
            TAB_VERB /* convers_type */
            4 /* number_value_pairs */
            0 "engine off" /* value pairs */
            1 "idling"
            2 "partial load"
            3 "full load"
        /end COMPU_VTAB
        /begin COMPU_VTAB CT_DiagStatus ""
            TAB_VERB /* convers_type */
            3 /* number_value_pairs */
            0 "C_Fail"
            1 "C_Pass"
            2 "C_Indeterminate"
        /end COMPU_VTAB
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    module = session.query(model.Module).first()
    assert module.name == "testModule"
    assert module.longIdentifier == ""
    cvt = module.compu_vtab
    assert len(cvt) == 2

    assert cvt[0].name == 'TT'
    assert cvt[0].longIdentifier == 'engine status conversion'
    assert cvt[0].conversionType == 'TAB_VERB'
    assert cvt[0].numberValuePairs == len(cvt[0].pairs)
    p0, p1, p2, p3, = cvt[0].pairs
    assert compareCompuTabPair(p0, inVal = 0.0, outVal = 'engine off') == True
    assert compareCompuTabPair(p1, inVal = 1.0, outVal = 'idling') == True
    assert compareCompuTabPair(p2, inVal = 2.0, outVal = 'partial load') == True
    assert compareCompuTabPair(p3, inVal = 3.0, outVal = 'full load') == True

    assert cvt[1].name == 'CT_DiagStatus'
    assert cvt[1].longIdentifier == ''
    assert cvt[1].conversionType == 'TAB_VERB'
    assert cvt[1].numberValuePairs == 3
    assert cvt[1].numberValuePairs == len(cvt[1].pairs)
    p0, p1, p2 = cvt[1].pairs
    assert compareCompuTabPair(p0, inVal = 0.0, outVal = 'C_Fail') == True
    assert compareCompuTabPair(p1, inVal = 1.0, outVal = 'C_Pass') == True
    assert compareCompuTabPair(p2, inVal = 2.0, outVal = 'C_Indeterminate') == True

def compareCompuVTabRangeTriple(pair, inValMin, inValMax, outVal):
    return pair.inValMin == inValMin and pair.inValMax == inValMax and pair.outVal == outVal

def test_compu_v_tab_range():
    parser = ParserWrapper('a2l', 'compuVtabRange', A2LListener, debug = False)
    DATA = """
    /begin COMPU_VTAB_RANGE TT /* name */
        "engine status conversion"
        5
        0   0   "ONE"
        1   2   "first_section"
        3   3   "THIRD"
        4   5   "second_section"
        6   500 "usual_case"
        DEFAULT_VALUE "Value_out_of_Range"
    /end COMPU_VTAB_RANGE
    """
    session = parser.parseFromString(DATA)
    cvr = session.query(model.CompuVtabRange).first()
    assert cvr.name == 'TT'
    assert cvr.longIdentifier == 'engine status conversion'
    assert cvr.numberValueTriples == len(cvr.triples)
    assert cvr.default_value.display_string == 'Value_out_of_Range'
    t0, t1, t2, t3, t4 = cvr.triples
    assert compareCompuVTabRangeTriple(t0, inValMin = 0.0, inValMax = 0.0, outVal = 'ONE') == True
    assert compareCompuVTabRangeTriple(t1, inValMin = 1.0, inValMax = 2.0, outVal = 'first_section') == True
    assert compareCompuVTabRangeTriple(t2, inValMin = 3.0, inValMax = 3.0, outVal = 'THIRD') == True
    assert compareCompuVTabRangeTriple(t3, inValMin = 4.0, inValMax = 5.0, outVal = 'second_section') == True
    assert compareCompuVTabRangeTriple(t4, inValMin = 6.0, inValMax = 500.0, outVal = 'usual_case') == True

def test_cpu_type():
    parser = ParserWrapper('a2l', 'cpuType', A2LListener, debug = False)
    DATA = """
    CPU_TYPE "INTEL 4711"
    """
    session = parser.parseFromString(DATA)
    cpu = session.query(model.CpuType).first()
    assert cpu.cPU == 'INTEL 4711'

def test_curve_axis_ref():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
    DATA = """
    /begin MODULE test ""
        /begin CHARACTERISTIC FUEL_ADJ /* name */
            "Air fuel table" /* long identifier */
            MAP /* type */
            0x7140 /* address */
            DEP_12E /* deposit */
            1.0 /* maxdiff */
            R_MULT /* conversion */
            0.0 /* lower limit */
            2.0 /* upper limit */
            /begin AXIS_DESCR /* description of X-axis points */
                CURVE_AXIS /* curve axis points */
                SPEED /* reference to input quantity*/
                NO_COMPU_METHOD /* conversion */
                13 /*maximum number of axis points*/
                0 /*lower limit */
                12 /*upper limit */
                CURVE_AXIS_REF SPD_NORM
            /end AXIS_DESCR
            /begin AXIS_DESCR /* description of Y-axis points */
                CURVE_AXIS /* curve axis points */
                LOAD /* reference to input quantity*/
                NO_COMPU_METHOD /* conversion */
                17 /*maximum number of axis points*/
                0 /*lower limit */
                16 /*upper limit */
                CURVE_AXIS_REF MAF_NORM
            /end AXIS_DESCR
        /end CHARACTERISTIC
        /begin RECORD_LAYOUT DEP_12E
            FNC_VALUES 1 FLOAT32_IEEE ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin CHARACTERISTIC SPD_NORM /* name */
            "Speed normalizing function"
            /* long identifier */
            CURVE /* type */
            0x8210 /* address */
            SPD_DEP /* deposit */
            100 /* maxdif */
            R_NORM /* conversion */
            0 6 /* lower limit, upper limit */
            /begin AXIS_DESCR /* description of X-axis points */
                STD_AXIS /* standard axis */
                SPEED /* reference to input quantity */
                R_SPEED /* conversion */
                7 /* maximum number of axis points*/
                0 /* lower limit */
                10000 /* upper limit */
            /end AXIS_DESCR
        /end CHARACTERISTIC
        /begin RECORD_LAYOUT SPD_DEP
            AXIS_PTS_X 1 FLOAT32_IEEE INDEX_INCR DIRECT
            FNC_VALUES 2 FLOAT32_IEEE ALTERNATE_WITH_X DIRECT
        /end RECORD_LAYOUT
        /begin CHARACTERISTIC MAF_NORM /* name */
            "Load normalizing function"
            /* long identifier */
            CURVE /* type */
            0x8428 /* address */
            LOAD_DEP /* deposit */
            100 /* maxdif */
            R_NORM /* conversion */
            0 16 /* lower limit, upper limit */
            /begin AXIS_DESCR /* description of X-axis points */
                STD_AXIS /* standard axis */
                LOAD /* reference to input quantity */
                R_LOAD /* conversion */
                17 /* maximum number of axis points*/
                0.0 /* lower limit */
                100.0 /* upper limit */
            /end AXIS_DESCR
        /end CHARACTERISTIC
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    mod = session.query(model.Module).first()
    assert mod.name == "test"
    assert mod.longIdentifier == ""
    rl0, rl1 = mod.record_layout
    assert rl0.name == "DEP_12E"
    assert rl0.fnc_values.position == 1
    assert rl0.fnc_values.datatype == 'FLOAT32_IEEE'
    assert rl0.fnc_values.indexMode == 'ROW_DIR'
    assert rl0.fnc_values.addresstype == 'DIRECT'
    assert rl1.name == "SPD_DEP"
    assert rl1.fnc_values.position == 2
    assert rl1.fnc_values.datatype == 'FLOAT32_IEEE'
    assert rl1.fnc_values.indexMode == 'ALTERNATE_WITH_X'
    assert rl1.fnc_values.addresstype == 'DIRECT'
    chx = mod.characteristic
    assert len(chx) == 3
    ch0, ch1, ch2 = chx

    assert ch0.name == 'FUEL_ADJ'
    assert ch0.longIdentifier == 'Air fuel table'
    assert ch0.type == 'MAP'
    assert ch0.address == 28992
    assert ch0.deposit == 'DEP_12E'
    assert ch0.maxDiff == 1.0
    assert ch0.conversion == 'R_MULT'
    assert ch0.lowerLimit == 0.0
    assert ch0.upperLimit == 2.0
    ad0, ad1 = ch0.axis_descr
    assert ad0.attribute == 'CURVE_AXIS'
    assert ad0.inputQuantity == 'SPEED'
    assert ad0.conversion == 'NO_COMPU_METHOD'
    assert ad0.maxAxisPoints == 13
    assert ad0.lowerLimit == 0.0
    assert ad0.upperLimit == 12.0
    assert ad1.attribute == 'CURVE_AXIS'
    assert ad1.inputQuantity == 'LOAD'
    assert ad1.conversion == 'NO_COMPU_METHOD'
    assert ad1.maxAxisPoints == 17
    assert ad1.lowerLimit == 0.0
    assert ad1.upperLimit == 16.0

    assert ch1.name == 'SPD_NORM'
    assert ch1.longIdentifier == 'Speed normalizing function'
    assert ch1.type == 'CURVE'
    assert ch1.address == 33296
    assert ch1.deposit == 'SPD_DEP'
    assert ch1.maxDiff == 100.0
    assert ch1.conversion == 'R_NORM'
    assert ch1.lowerLimit == 0.0
    assert ch1.upperLimit == 6.0
    ad0 = ch1.axis_descr[0]
    assert ad0.attribute == 'STD_AXIS'
    assert ad0.inputQuantity == 'SPEED'
    assert ad0.conversion == 'R_SPEED'
    assert ad0.maxAxisPoints == 7
    assert ad0.lowerLimit == 0.0
    assert ad0.upperLimit == 10000.0

    assert ch2.name == 'MAF_NORM'
    assert ch2.longIdentifier == 'Load normalizing function'
    assert ch2.type == 'CURVE'
    assert ch2.address == 33832
    assert ch2.deposit == 'LOAD_DEP'
    assert ch2.maxDiff == 100.0
    assert ch2.conversion == 'R_NORM'
    assert ch2.lowerLimit == 0.0
    assert ch2.upperLimit == 16.0
    ad0 = ch2.axis_descr[0]
    assert ad0.attribute == 'STD_AXIS'
    assert ad0.inputQuantity == 'LOAD'
    assert ad0.conversion == 'R_LOAD'
    assert ad0.maxAxisPoints == 17
    assert ad0.lowerLimit == 0.0
    assert ad0.upperLimit == 100.0

def test_customer():
    parser = ParserWrapper('a2l', 'customer', A2LListener, debug = False)
    DATA = """
    CUSTOMER "LANZ - Landmaschinen"
    """
    session = parser.parseFromString(DATA)
    cust = session.query(model.Customer).first()
    assert cust.customer == "LANZ - Landmaschinen"

def test_customer_no():
    parser = ParserWrapper('a2l', 'customerNo', A2LListener, debug = False)
    DATA = """
    CUSTOMER_NO     "191188"
    """
    session = parser.parseFromString(DATA)
    cust = session.query(model.CustomerNo).first()
    assert cust.number == "191188"

def test_data_size():
    parser = ParserWrapper('a2l', 'dataSize', A2LListener, debug = False)
    DATA = """
    DATA_SIZE   16
    """
    session = parser.parseFromString(DATA)
    ds = session.query(model.DataSize).first()
    assert ds.size == 16

def test_def_characteristic():
    parser = ParserWrapper('a2l', 'defCharacteristic', A2LListener, debug = False)
    DATA = """
    /begin DEF_CHARACTERISTIC
        INJECTION_CURVE
        DELAY_FACTOR
    /end DEF_CHARACTERISTIC
    """
    session = parser.parseFromString(DATA)
    dc = session.query(model.DefCharacteristic).first()
    ids = dc.identifier
    assert ids[0] == "INJECTION_CURVE"
    assert ids[1] == "DELAY_FACTOR"

def test_default_value():
    parser = ParserWrapper('a2l', 'defaultValue', A2LListener, debug = False)
    DATA = """
    DEFAULT_VALUE "overflow_state"
    """
    session = parser.parseFromString(DATA)
    dv = session.query(model.DefaultValue).first()
    assert dv.display_string == "overflow_state"

def test_default_value_numeric():
    parser = ParserWrapper('a2l', 'defaultValueNumeric', A2LListener, debug = False)
    DATA = """
    DEFAULT_VALUE_NUMERIC 999.0
    """
    session = parser.parseFromString(DATA)
    dv = session.query(model.DefaultValueNumeric).first()
    assert dv.display_value == 999.0

def test_dependent_characteristic():
    parser = ParserWrapper('a2l', 'characteristic', A2LListener, debug = False)
    DATA = """
    /begin CHARACTERISTIC FUEL_ADJ /* name */
        "Air fuel table" /* long identifier */
        MAP /* type */
        0x7140 /* address */
        DEP_12E /* deposit */
        1.0 /* maxdiff */
        R_MULT /* conversion */
        0.0 /* lower limit */
        2.0 /* upper limit */
/*
        /begin DEPENDENT_CHARACTERISTIC
            "sqrt(1-X1*X1)"
            A
        /end DEPENDENT_CHARACTERISTIC
*/
        /* Example for ParamB - ParamA */
        /begin DEPENDENT_CHARACTERISTIC
            "X2-X1"
            ParamA /* is referenced by X1 */
            ParamB /* is referenced by X2 */
        /end DEPENDENT_CHARACTERISTIC
    /end CHARACTERISTIC
    """
    session = parser.parseFromString(DATA)
    chx = session.query(model.Characteristic).first()
    assert chx.name == 'FUEL_ADJ'
    assert chx.longIdentifier == 'Air fuel table'
    assert chx.type == 'MAP'
    assert chx.address == 28992
    assert chx.deposit == 'DEP_12E'
    assert chx.maxDiff == 1.0
    assert chx.conversion == 'R_MULT'
    assert chx.lowerLimit == 0.0
    assert chx.upperLimit == 2.0
    dc0 = chx.dependent_characteristic
    assert dc0.formula == "X2-X1"
    assert dc0.characteristic_id == ['ParamA', 'ParamB']

def test_deposit():
    parser = ParserWrapper('a2l', 'deposit', A2LListener, debug = False)
    DATA = """
    DEPOSIT DIFFERENCE
    """
    session = parser.parseFromString(DATA)
    ds = session.query(model.Deposit).first()
    assert ds.mode == 'DIFFERENCE'

def test_discrete():
    parser = ParserWrapper('a2l', 'measurement', A2LListener, debug = False)
    DATA = """
    /begin MEASUREMENT
        counter
        "..."
        UBYTE
        NO_COMPU_METHOD
        2
        1
        0
        255
        DISCRETE
    /end MEASUREMENT
    """
    session = parser.parseFromString(DATA)
    meas = session.query(model.Measurement).first()
    assert meas.name == 'counter'
    assert meas.longIdentifier == '...'
    assert meas.datatype == 'UBYTE'
    assert meas.conversion == 'NO_COMPU_METHOD'
    assert meas.resolution == 2
    assert meas.accuracy == 1.0
    assert meas.lowerLimit == 0.0
    assert meas.upperLimit == 255.0
    assert meas.discrete is not None

def test_display_identifier():
    parser = ParserWrapper('a2l', 'displayIdentifier', A2LListener, debug = False)
    DATA = """
    DISPLAY_IDENTIFIER load_engine
    """
    session = parser.parseFromString(DATA)
    di = session.query(model.DisplayIdentifier).first()
    assert di.display_name == "load_engine"

def test_dist_op_x():
    parser = ParserWrapper('a2l', 'distOpX', A2LListener, debug = False)
    DATA = """
    DIST_OP_X   21
                UWORD
    """
    session = parser.parseFromString(DATA)
    di = session.query(model.DistOpX).first()
    assert di.position == 21
    assert di.datatype == "UWORD"

def test_dist_op_y():
    parser = ParserWrapper('a2l', 'distOpY', A2LListener, debug = False)
    DATA = """
    DIST_OP_Y   21
                UWORD
    """
    session = parser.parseFromString(DATA)
    di = session.query(model.DistOpY).first()
    assert di.position == 21
    assert di.datatype == "UWORD"

def test_dist_op_z():
    parser = ParserWrapper('a2l', 'distOpZ', A2LListener, debug = False)
    DATA = """
    DIST_OP_Z   21
                UWORD
    """
    session = parser.parseFromString(DATA)
    di = session.query(model.DistOpZ).first()
    assert di.position == 21
    assert di.datatype == "UWORD"

def test_dist_op_4():
    parser = ParserWrapper('a2l', 'distOp4', A2LListener, debug = False)
    DATA = """
    DIST_OP_4   21
                UWORD
    """
    session = parser.parseFromString(DATA)
    di = session.query(model.DistOp4).first()
    assert di.position == 21
    assert di.datatype == "UWORD"

def test_dist_op_5():
    parser = ParserWrapper('a2l', 'distOp5', A2LListener, debug = False)
    DATA = """
    DIST_OP_5   21
                UWORD
    """
    session = parser.parseFromString(DATA)
    di = session.query(model.DistOp5).first()
    assert di.position == 21
    assert di.datatype == "UWORD"

def test_ecu():
    parser = ParserWrapper('a2l', 'ecu', A2LListener, debug = False)
    DATA = 'ECU "Steering control"'
    session = parser.parseFromString(DATA)
    ec = session.query(model.Ecu).first()
    assert ec.controlUnit == "Steering control"

def test_ecu_address():
    parser = ParserWrapper('a2l', 'ecuAddress', A2LListener, debug = False)
    DATA = "ECU_ADDRESS 0x12FE"
    session = parser.parseFromString(DATA)
    ec = session.query(model.EcuAddress).first()
    assert ec.address == 0x12FE

def test_ecu_address_extension():
    parser = ParserWrapper('a2l', 'measurement', A2LListener, debug = False)
    DATA = """
    /begin MEASUREMENT N /* name */
        "Engine speed" /* long identifier */
        UWORD /* datatype */
        R_SPEED_3 /* conversion */
        2 /* resolution */
        2.5 /* accuracy */
        120.0 /* lower limit */
        8400.0 /* upper limit */
        ECU_ADDRESS 0x12345
        ECU_ADDRESS_EXTENSION 1
    /end MEASUREMENT
    """
    session = parser.parseFromString(DATA)
    meas = session.query(model.Measurement).first()
    assert meas.name == 'N'
    assert meas.longIdentifier == 'Engine speed'
    assert meas.datatype == 'UWORD'
    assert meas.conversion == 'R_SPEED_3'
    assert meas.resolution == 2
    assert meas.accuracy == 2.5
    assert meas.lowerLimit == 120.0
    assert meas.upperLimit == 8400.0
    assert meas.ecu_address_extension.extension == 1
    assert meas.ecu_address.address == 0x12345

def test_ecu_calibration_offset():
    parser = ParserWrapper('a2l', 'ecuCalibrationOffset', A2LListener, debug = False)
    DATA = "ECU_CALIBRATION_OFFSET 0x1000"
    session = parser.parseFromString(DATA)
    ec = session.query(model.EcuCalibrationOffset).first()
    assert ec.offset == 0x1000

def test_epk():
    parser = ParserWrapper('a2l', 'epk', A2LListener, debug = False)
    DATA = 'EPK "EPROM identifier test"'
    session = parser.parseFromString(DATA)
    epk = session.query(model.Epk).first()
    assert epk.identifier == "EPROM identifier test"

def test_error_mask():
    parser = ParserWrapper('a2l', 'errorMask', A2LListener, debug = False)
    DATA = 'ERROR_MASK 0x00000001'
    session = parser.parseFromString(DATA)
    em = session.query(model.ErrorMask).first()
    assert em.mask == 0x00000001

def test_extended_limits():
    parser = ParserWrapper('a2l', 'extendedLimits', A2LListener, debug = False)
    DATA = """
        EXTENDED_LIMITS     0
                            6000.0
    """
    session = parser.parseFromString(DATA)
    el = session.query(model.ExtendedLimits).first()
    assert el.lowerLimit == 0.0
    assert el.upperLimit == 6000.0

def test_fix_axis_par():
    parser = ParserWrapper('a2l', 'fixAxisPar', A2LListener, debug = False)
    DATA = """
    /* Define axis points 0, 16, 32, 48, 64, 80 */
    FIX_AXIS_PAR    0
                    4
                    6
    """
    session = parser.parseFromString(DATA)
    fap = session.query(model.FixAxisPar).first()
    assert fap.offset == 0
    assert fap.shift == 4
    assert fap.numberapo == 6

def test_fix_axis_par_dist():
    parser = ParserWrapper('a2l', 'fixAxisParDist', A2LListener, debug = False)
    DATA = """
    FIX_AXIS_PAR_DIST   0
                        100
                        8
    """
    session = parser.parseFromString(DATA)
    fap = session.query(model.FixAxisParDist).first()
    assert fap.offset == 0
    assert fap.distance == 100
    assert fap.numberapo == 8

def test_fix_axis_par_list():
    parser = ParserWrapper('a2l', 'fixAxisParList', A2LListener, debug = False)
    DATA = """
    /begin FIX_AXIS_PAR_LIST
        2 5 9
    /end FIX_AXIS_PAR_LIST
    """
    session = parser.parseFromString(DATA)
    fal = session.query(model.FixAxisParList).first()
    assert fal.axisPts_Value == [2.0, 5.0, 9.0]

def test_fix_no_axis_pts_x():
    parser = ParserWrapper('a2l', 'fixNoAxisPtsX', A2LListener, debug = False)
    DATA = 'FIX_NO_AXIS_PTS_X   17'
    session = parser.parseFromString(DATA)
    fp = session.query(model.FixNoAxisPtsX).first()
    assert fp.numberOfAxisPoints == 17

def test_fix_no_axis_pts_y():
    parser = ParserWrapper('a2l', 'fixNoAxisPtsY', A2LListener, debug = False)
    DATA = 'FIX_NO_AXIS_PTS_Y   17'
    session = parser.parseFromString(DATA)
    fp = session.query(model.FixNoAxisPtsY).first()
    assert fp.numberOfAxisPoints == 17

def test_fix_no_axis_pts_z():
    parser = ParserWrapper('a2l', 'fixNoAxisPtsZ', A2LListener, debug = False)
    DATA = 'FIX_NO_AXIS_PTS_Z   17'
    session = parser.parseFromString(DATA)
    fp = session.query(model.FixNoAxisPtsZ).first()
    assert fp.numberOfAxisPoints == 17

def test_fix_no_axis_pts_4():
    parser = ParserWrapper('a2l', 'fixNoAxisPts4', A2LListener, debug = False)
    DATA = 'FIX_NO_AXIS_PTS_4   17'
    session = parser.parseFromString(DATA)
    fp = session.query(model.FixNoAxisPts4).first()
    assert fp.numberOfAxisPoints == 17

def test_fix_no_axis_pts_5():
    parser = ParserWrapper('a2l', 'fixNoAxisPts5', A2LListener, debug = False)
    DATA = 'FIX_NO_AXIS_PTS_5   17'
    session = parser.parseFromString(DATA)
    fp = session.query(model.FixNoAxisPts5).first()
    assert fp.numberOfAxisPoints == 17

def test_fnc_values():
    parser = ParserWrapper('a2l', 'fncValues', A2LListener, debug = False)
    DATA = """
    FNC_VALUES  7
                SWORD
                COLUMN_DIR
                DIRECT
    """
    session = parser.parseFromString(DATA)
    fv = session.query(model.FncValues).first()
    assert fv.position == 7
    assert fv.datatype == 'SWORD'
    assert fv.indexMode == 'COLUMN_DIR'
    assert fv.addresstype == 'DIRECT'

def test_format():
    parser = ParserWrapper('a2l', 'format_', A2LListener, debug = False)
    DATA = 'FORMAT "%4.2"'
    session = parser.parseFromString(DATA)
    fm = session.query(model.Format).first()
    assert fm.formatString == "%4.2"

def test_formula():
    parser = ParserWrapper('a2l', 'formula', A2LListener, debug = False)
    DATA = """
        /begin FORMULA "sqrt( 3 - 4*sin(X1) )"
        /end FORMULA
    """
    session = parser.parseFromString(DATA)
    fm = session.query(model.Formula).first()
    assert fm.f_x == "sqrt( 3 - 4*sin(X1) )"

def test_formula_inv():
    parser = ParserWrapper('a2l', 'formulaInv', A2LListener, debug = False)
    DATA = """
    FORMULA_INV "asin( sqrt( (3 - X1)/4 ) )"
    """
    session = parser.parseFromString(DATA)
    fm = session.query(model.FormulaInv).first()
    assert fm.g_x == "asin( sqrt( (3 - X1)/4 ) )"

def test_frame():
    parser = ParserWrapper('a2l', 'frame', A2LListener, debug = False)
    DATA = """
    /begin FRAME ABS_ADJUSTM
        "function group ABS adjustment"
        3
        2 /* 2 msec. */
        FRAME_MEASUREMENT LOOP_COUNTER TEMPORARY_1
    /end FRAME
    """
    session = parser.parseFromString(DATA)
    frame = session.query(model.Frame).first()
    assert frame.name == 'ABS_ADJUSTM'
    assert frame.longIdentifier == 'function group ABS adjustment'
    assert frame.scalingUnit == 3
    assert frame.rate == 2
    assert frame.frame_measurement.identifier == ['LOOP_COUNTER', 'TEMPORARY_1']

def test_frame_measurement():
    parser = ParserWrapper('a2l', 'frameMeasurement', A2LListener, debug = False)
    DATA = """
    FRAME_MEASUREMENT WHEEL_REVOLUTIONS ENGINE_SPEED
    """
    session = parser.parseFromString(DATA)
    fm = session.query(model.FrameMeasurement).first()
    assert fm.identifier == ['WHEEL_REVOLUTIONS', 'ENGINE_SPEED']

def test_function():
    parser = ParserWrapper('a2l', 'function', A2LListener, debug = False)
    DATA = """
    /begin FUNCTION ID_ADJUSTM /* name */
        "function group idling adjustment"
        /begin DEF_CHARACTERISTIC INJECTION_CURVE
        /end DEF_CHARACTERISTIC
        /begin REF_CHARACTERISTIC FACTOR_1
        /end REF_CHARACTERISTIC
        /begin IN_MEASUREMENT WHEEL_REVOLUTIONS ENGINE_SPEED
        /end IN_MEASUREMENT
        /begin OUT_MEASUREMENT OK_FLAG SENSOR_FLAG
        /end OUT_MEASUREMENT
        /begin LOC_MEASUREMENT LOOP_COUNTER TEMPORARY_1
        /end LOC_MEASUREMENT
        /begin SUB_FUNCTION ID_ADJUSTM_SUB
        /end SUB_FUNCTION
    /end FUNCTION
    """
    session = parser.parseFromString(DATA)
    func = session.query(model.Function).first()
    assert func.name == 'ID_ADJUSTM'
    assert func.longIdentifier == 'function group idling adjustment'
    assert func.def_characteristic.identifier == ['INJECTION_CURVE']

    assert func.sub_function.identifier == ['ID_ADJUSTM_SUB']
    assert func.in_measurement.identifier == ['WHEEL_REVOLUTIONS', 'ENGINE_SPEED']
    assert func.out_measurement.identifier == ['OK_FLAG', 'SENSOR_FLAG']
    assert func.loc_measurement.identifier == ['LOOP_COUNTER', 'TEMPORARY_1']
    assert func.ref_characteristic.identifier == ['FACTOR_1']


def test_function_list():
    parser = ParserWrapper('a2l', 'functionList', A2LListener, debug = False)
    DATA = """
    /begin FUNCTION_LIST ID_ADJUSTM
        FL_ADJUSTM
        SPEED_LIM
    /end FUNCTION_LIST
    """
    session = parser.parseFromString(DATA)
    func = session.query(model.FunctionList).first()
    assert func.name == ['ID_ADJUSTM', 'FL_ADJUSTM', 'SPEED_LIM']

def test_function_version():
    parser = ParserWrapper('a2l', 'functionVersion', A2LListener, debug = False)
    DATA = """
    FUNCTION_VERSION "BG5.0815"
    """
    session = parser.parseFromString(DATA)
    func = session.query(model.FunctionVersion).first()
    assert func.versionIdentifier == 'BG5.0815'

def test_group():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
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
        /begin SUB_GROUP injec1
            injec2
        /end SUB_GROUP
    /end GROUP
    /begin GROUP Injec1
        "Module filename Injec1"
        /begin REF_CHARACTERISTIC
            INJECTION_CURVE
        /end REF_CHARACTERISTIC
        /begin REF_MEASUREMENT
            LOOP_COUNTER
            TEMPORARY_1
        /end REF_MEASUREMENT
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
        "assignment of the definitions to calibration components"
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
        " L4-PCM 2002 C modules"
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
    session = parser.parseFromString(DATA)
    groups = session.query(model.Group).all()
    assert len(groups) == 17
    g0, g1, g2, g3, g4, g5, g6, g7, g8, g9, g10, g11, g12, g13, g14, g15, g16 = groups

    assert g0.groupName == 'SOFTWARE_COMPONENTS'
    assert g0.groupLongIdentifier == 'assignment of the definitions to C files'
    assert g0.root is not None
    assert g0.sub_group.identifier == ['INJE', 'C6TD']

    assert g1.groupName == 'INJE'
    assert g1.groupLongIdentifier == 'Subsystem Injection'
    assert g1.sub_group.identifier == ['injec1', 'injec2']

    assert g2.groupName == 'Injec1'
    assert g2.groupLongIdentifier == 'Module filename Injec1'
    assert g2.ref_characteristic.identifier == ['INJECTION_CURVE']
    assert g2.ref_measurement.identifier == ['LOOP_COUNTER', 'TEMPORARY_1']

    assert g3.groupName == 'Injec2'
    assert g3.groupLongIdentifier == 'Module filename Injec2'

    assert g4.groupName == 'C6TD'
    assert g4.groupLongIdentifier == 'Shift Point Control'

    assert g5.groupName == 'c6tdvder'
    assert g5.groupLongIdentifier == 'Module filename c6tdvder'

    assert g6.groupName == 'c6tderft'
    assert g6.groupLongIdentifier == 'Module filename c6tderft'

    assert g7.groupName == 'CALIBRATION_COMPONENTS'
    assert g7.groupLongIdentifier == 'assignment of the definitions to calibration components'

    assert g8.groupName == 'CALIBRATION_COMPONENTS_L4'
    assert g8.groupLongIdentifier == 'L4-PCM 2002 cals'

    assert g9.groupName == 'LUFT'
    assert g9.groupLongIdentifier == 'Cals in LUFT Subsystem'

    assert g10.groupName == 'CLOSED_LOOP'
    assert g10.groupLongIdentifier == 'Cals in FCLS, FCLP & FCLL Subsystem'

    assert g11.groupName == 'Winter_Test'
    assert g11.groupLongIdentifier == 'Flash this in winter time'

    assert g12.groupName == 'Summer_Test'
    assert g12.groupLongIdentifier == 'Flash that in summer time'

    assert g13.groupName == 'SOFTWARE_COMPONENTS'
    assert g13.groupLongIdentifier == ' L4-PCM 2002 C modules'

    assert g14.groupName == 'luftkmgr.c'
    assert g14.groupLongIdentifier == 'Objects in luftkmgr.c'

    assert g15.groupName == 'fclpkout.c'
    assert g15.groupLongIdentifier == 'Objects in fclpkout.c'

    assert g16.groupName == 'viosmeng.c'
    assert g16.groupLongIdentifier == 'Objects in viosmeng.c'

def test_guard_rails():
    parser = ParserWrapper('a2l', 'characteristic', A2LListener, debug = False)
    DATA = """
    /begin CHARACTERISTIC F_INJ_CORR /* name */
        "Injector correction factor"
        /* long identifier */
        CURVE /* type */
        0x7140 /* address */
        REC12 /* deposit */
        10.0 /* maxdiff */
        C_INJF /* conversion */
        0.0 /* lower limit */
        199.0 /* upper limit */
        GUARD_RAILS /* uses guard rails */
        /begin AXIS_DESCR /* description of X-axis points */
            STD_AXIS /* standard axis points */
            N /* reference to input quantity*/
            C_TEMP /* conversion */
            10 /* maximum number of axis points*/
            -40.0 /* lower limit */
            150.0 /* upper limit */
        /end AXIS_DESCR
    /end CHARACTERISTIC
    """
    session = parser.parseFromString(DATA)
    chx = session.query(model.Characteristic).first()

    assert chx.name == 'F_INJ_CORR'
    assert chx.longIdentifier == 'Injector correction factor'
    assert chx.type == 'CURVE'
    assert chx.address == 28992
    assert chx.deposit == 'REC12'
    assert chx.maxDiff == 10.0
    assert chx.conversion == 'C_INJF'
    assert chx.lowerLimit == 0.0
    assert chx.upperLimit == 199.0
    assert chx.guard_rails is not None
    ax = chx.axis_descr[0]
    assert ax.attribute == 'STD_AXIS'
    assert ax.inputQuantity == 'N'
    assert ax.conversion == 'C_TEMP'
    assert ax.maxAxisPoints == 10
    assert ax.lowerLimit == -40.0
    assert ax.upperLimit == 150.0

def test_header():
    parser = ParserWrapper('a2l', 'header', A2LListener, debug = False)
    DATA = """
    /begin HEADER "see also specification XYZ of 01.02.1994"
        VERSION "BG5.0815"
        PROJECT_NO M4711Z1
    /end HEADER
    """
    session = parser.parseFromString(DATA)
    hdr = session.query(model.Header).first()
    assert hdr.version.versionIdentifier == "BG5.0815"
    assert hdr.comment == 'see also specification XYZ of 01.02.1994'
    assert hdr.project_no.projectNumber == "M4711Z1"

def test_identification():
    parser = ParserWrapper('a2l', 'identification', A2LListener, debug = False)
    DATA = """
    IDENTIFICATION
        1
        UWORD
    """
    session = parser.parseFromString(DATA)
    idf = session.query(model.Identification).first()
    assert idf.position == 1
    assert idf.datatype == 'UWORD'

def test_in_measurement():
    parser = ParserWrapper('a2l', 'inMeasurement', A2LListener, debug = False)
    DATA = """
    /begin IN_MEASUREMENT WHEEL_REVOLUTIONS
        ENGINE_SPEED
    /end IN_MEASUREMENT
    """
    session = parser.parseFromString(DATA)
    im = session.query(model.InMeasurement).first()
    assert im.identifier == ['WHEEL_REVOLUTIONS', 'ENGINE_SPEED']

def test_loc_measurement():
    parser = ParserWrapper('a2l', 'locMeasurement', A2LListener, debug = False)
    DATA = """
    /begin LOC_MEASUREMENT LOOP_COUNTER
        TEMPORARY_1
    /end LOC_MEASUREMENT
    """
    session = parser.parseFromString(DATA)
    lm = session.query(model.LocMeasurement).first()
    assert lm.identifier == ['LOOP_COUNTER', 'TEMPORARY_1']

def test_map_list():
    parser = ParserWrapper('a2l', 'mapList', A2LListener, debug = False)
    DATA = """
    /begin MAP_LIST MAP_1
        MAP_2 MAP_3
    /end MAP_LIST
    """
    session = parser.parseFromString(DATA)
    lm = session.query(model.MapList).first()
    assert lm.name == ['MAP_1', 'MAP_2', 'MAP_3']

def test_matrix_dim():
    parser = ParserWrapper('a2l', 'matrixDim', A2LListener, debug = False)
    DATA = """
    MATRIX_DIM  2
                4
                3
    """
    session = parser.parseFromString(DATA)
    md = session.query(model.MatrixDim).first()
    assert md.xDim == 2
    assert md.yDim == 4
    assert md.zDim == 3

def test_max_grad():
    parser = ParserWrapper('a2l', 'maxGrad', A2LListener, debug = False)
    DATA = """
    MAX_GRAD 200.0
    """
    session = parser.parseFromString(DATA)
    mg = session.query(model.MaxGrad).first()
    assert mg.maxGradient == 200.0

def test_max_refresh():
    parser = ParserWrapper('a2l', 'maxRefresh', A2LListener, debug = False)
    DATA = """
    MAX_REFRESH
        998 2   /* ScalingUnit = 998 --> Every second frame */
    """
    session = parser.parseFromString(DATA)
    mr = session.query(model.MaxRefresh).first()
    assert mr.scalingUnit == 998
    assert mr.rate == 2

def test_measurement():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
    DATA = """
    /begin MODULE testModule ""
        /begin MEASUREMENT N /* name */
            "Engine speed" /* long identifier */
            UWORD /* datatype */
            R_SPEED_3 /* conversion */
            2 /* resolution */
            2.5 /* accuracy */
            120.0 /* lower limit */
            8400.0 /* upper limit */
            PHYS_UNIT "mph"
            BIT_MASK 0x0FFF
            /begin BIT_OPERATION
                RIGHT_SHIFT 4 /*4 positions*/
                SIGN_EXTEND
            /end BIT_OPERATION
            BYTE_ORDER MSB_FIRST
            REF_MEMORY_SEGMENT Data2
            /begin FUNCTION_LIST ID_ADJUSTM
                FL_ADJUSTM
            /end FUNCTION_LIST
/*
            /begin IF_DATA ISO SND
                0x10
                0x00
                0x05
                0x08
                RCV
                4
                long
            /end IF_DATA
*/
        /end MEASUREMENT
        /begin MEASUREMENT VdiagStatus /* name */
          "VdiagStatus" /* long identifier */
            SWORD /* datatype */
            CM_DiagSTatus /* conversion */
            16 /* resolution */
            1 /* accuracy */
            -32768 /* lower limit */
            32767 /* upper limit */
            ECU_ADDRESS 0x003FDFE0
        /end MEASUREMENT
        /begin MEASUREMENT VfSpinLoss /* name */
            "VfSpinLoss" /* long identifier */
            UWORD /* datatype */
            CM_RPM /* conversion */
            16 /* resolution */
            1 /* accuracy */
            -4096 /* lower limit */
            4095.875 /* upper limit */
            ECU_ADDRESS 0x003FE380
        /end MEASUREMENT
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    meas = session.query(model.Measurement).all()
    assert len(meas) == 3
    m0, m1, m2 = meas
    assert m0.name == 'N'
    assert m0.longIdentifier == 'Engine speed'
    assert m0.datatype == 'UWORD'
    assert m0.conversion == 'R_SPEED_3'
    assert m0.resolution == 2
    assert m0.accuracy == 2.5
    assert m0.lowerLimit == 120.0
    assert m0.upperLimit == 8400.0
    assert m0.phys_unit.unit == 'mph'
    assert m0.bit_mask.mask == 0x0fff
    assert m0.bit_operation.right_shift.bitcount == 4
    assert m0.bit_operation.sign_extend is not None
    assert m0.byte_order.byteOrder == 'MSB_FIRST'
    assert m0.ref_memory_segment.name == "Data2"
    assert m0.function_list.name == ['ID_ADJUSTM', 'FL_ADJUSTM']

    assert m1.name == 'VdiagStatus'
    assert m1.longIdentifier == 'VdiagStatus'
    assert m1.datatype == 'SWORD'
    assert m1.conversion == 'CM_DiagSTatus'
    assert m1.resolution == 16
    assert m1.accuracy == 1.0
    assert m1.lowerLimit == -32768.0
    assert m1.upperLimit == 32767.0
    assert m1.ecu_address.address == 0x003FDFE0

    assert m2.name == 'VfSpinLoss'
    assert m2.longIdentifier == 'VfSpinLoss'
    assert m2.datatype == 'UWORD'
    assert m2.conversion == 'CM_RPM'
    assert m2.resolution == 16
    assert m2.accuracy == 1.0
    assert m2.lowerLimit == -4096.0
    assert m2.upperLimit == 4095.875
    assert m2.ecu_address.address == 0x003FE380

def test_memory_layout():
    parser = ParserWrapper('a2l', 'modPar', A2LListener, debug = False)
    DATA = """
    /begin MOD_PAR ""
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
            0x0200
            0x10000
            0x20000
            -1 -1 -1
        /end MEMORY_LAYOUT
        /begin MEMORY_LAYOUT PRG_DATA
            0x4200
            0x0E00
            -1 -1 -1 -1 -1
        /end MEMORY_LAYOUT
        /begin MEMORY_LAYOUT PRG_DATA
            0x14200
            0x0E00
            -1 -1 -1 -1 -1
        /end MEMORY_LAYOUT
        /begin MEMORY_LAYOUT PRG_DATA
            0x24200
            0x0E00
            -1 -1 -1 -1 -1
        /end MEMORY_LAYOUT
    /end MOD_PAR
    """
    session = parser.parseFromString(DATA)
    ly = session.query(model.MemoryLayout).all()
    l0, l1, l2, l3, l4, l5 = ly

    assert l0.prgType == 'PRG_RESERVED'
    assert l0.address == 0
    assert l0.size == 1024
    assert l0.offset_0 == -1
    assert l0.offset_1 == -1
    assert l0.offset_2 == -1
    assert l0.offset_3 == -1
    assert l0.offset_4 == -1

    assert l1.prgType == 'PRG_CODE'
    assert l1.address == 1024
    assert l1.size == 15360
    assert l1.offset_0 == -1
    assert l1.offset_1 == -1
    assert l1.offset_2 == -1
    assert l1.offset_3 == -1
    assert l1.offset_4 == -1

    assert l2.prgType == 'PRG_DATA'
    assert l2.address == 16384
    assert l2.size == 512
    assert l2.offset_0 == 65536
    assert l2.offset_1 == 131072
    assert l2.offset_2 == -1
    assert l2.offset_3 == -1
    assert l2.offset_4 == -1

    assert l3.prgType == 'PRG_DATA'
    assert l3.address == 16896
    assert l3.size == 3584
    assert l3.offset_0 == -1
    assert l3.offset_1 == -1
    assert l3.offset_2 == -1
    assert l3.offset_3 == -1
    assert l3.offset_4 == -1

    assert l4.prgType == 'PRG_DATA'
    assert l4.address == 82432
    assert l4.size == 3584
    assert l4.offset_0 == -1
    assert l4.offset_1 == -1
    assert l4.offset_2 == -1
    assert l4.offset_3 == -1
    assert l4.offset_4 == -1

    assert l5.prgType == 'PRG_DATA'
    assert l5.address == 147968
    assert l5.size == 3584
    assert l5.offset_0 == -1
    assert l5.offset_1 == -1
    assert l5.offset_2 == -1
    assert l5.offset_3 == -1
    assert l5.offset_4 == -1

def test_memory_segment():
    parser = ParserWrapper('a2l', 'modPar', A2LListener, debug = False)
    DATA = """
    /begin MOD_PAR ""
        /begin MEMORY_SEGMENT Data1
            "Data internal Flash"
            DATA
            FLASH
            INTERN
            0x4000
            0x0200
            -1 -1 -1 -1 -1
        /end MEMORY_SEGMENT
        /begin MEMORY_SEGMENT Data2
            "Data external Flash"
            DATA
            FLASH
            EXTERN
            0x7000
            0x2000
            -1 -1 -1 -1 -1
        /end MEMORY_SEGMENT
        /begin MEMORY_SEGMENT Code1
            "Code external Flash"
            CODE
            FLASH
            EXTERN
            0x9000
            0x3000
            -1 -1 -1 -1 -1
        /end MEMORY_SEGMENT
        /begin MEMORY_SEGMENT ext_Ram
            "external RAM"
            DATA
            RAM
            EXTERN
            0x30000
            0x1000
            -1 -1 -1 -1 -1
        /end MEMORY_SEGMENT
        /begin MEMORY_SEGMENT int_Ram
            "internal RAM"
            DATA
            RAM
            INTERN
            0x0000
            0x0200
            -1 -1 -1 -1 -1
        /end MEMORY_SEGMENT
        /begin MEMORY_SEGMENT Seram1
            "emulation RAM 1"
            SERAM
            RAM
            EXTERN
            0x7000
            0x1000
            -1 -1 -1 -1 -1
        /end MEMORY_SEGMENT
        /begin MEMORY_SEGMENT Seram2
            "emulation RAM 2"
            SERAM
            RAM
            INTERN
            0x8000
            0x1000
            -1 -1 -1 -1 -1
        /end MEMORY_SEGMENT
    /end MOD_PAR
    """
    session = parser.parseFromString(DATA)
    ms = session.query(model.MemorySegment).all()
    m0, m1, m2, m3, m4, m5, m6 = ms
    assert m0.name == 'Data1'
    assert m0.longIdentifier == 'Data internal Flash'
    assert m0.prgType == 'DATA'
    assert m0.memoryType == 'FLASH'
    assert m0.attribute == 'INTERN'
    assert m0.address == 16384
    assert m0.size == 512
    assert m0.offset_0 == -1
    assert m0.offset_1 == -1
    assert m0.offset_2 == -1
    assert m0.offset_3 == -1
    assert m0.offset_4 == -1

    assert m1.name == 'Data2'
    assert m1.longIdentifier == 'Data external Flash'
    assert m1.prgType == 'DATA'
    assert m1.memoryType == 'FLASH'
    assert m1.attribute == 'EXTERN'
    assert m1.address == 28672
    assert m1.size == 8192
    assert m1.offset_0 == -1
    assert m1.offset_1 == -1
    assert m1.offset_2 == -1
    assert m1.offset_3 == -1
    assert m1.offset_4 == -1

    assert m2.name == 'Code1'
    assert m2.longIdentifier == 'Code external Flash'
    assert m2.prgType == 'CODE'
    assert m2.memoryType == 'FLASH'
    assert m2.attribute == 'EXTERN'
    assert m2.address == 36864
    assert m2.size == 12288
    assert m2.offset_0 == -1
    assert m2.offset_1 == -1
    assert m2.offset_2 == -1
    assert m2.offset_3 == -1
    assert m2.offset_4 == -1

    assert m3.name == 'ext_Ram'
    assert m3.longIdentifier == 'external RAM'
    assert m3.prgType == 'DATA'
    assert m3.memoryType == 'RAM'
    assert m3.attribute == 'EXTERN'
    assert m3.address == 196608
    assert m3.size == 4096
    assert m3.offset_0 == -1
    assert m3.offset_1 == -1
    assert m3.offset_2 == -1
    assert m3.offset_3 == -1
    assert m3.offset_4 == -1

    assert m4.name == 'int_Ram'
    assert m4.longIdentifier == 'internal RAM'
    assert m4.prgType == 'DATA'
    assert m4.memoryType == 'RAM'
    assert m4.attribute == 'INTERN'
    assert m4.address == 0
    assert m4.size == 512
    assert m4.offset_0 == -1
    assert m4.offset_1 == -1
    assert m4.offset_2 == -1
    assert m4.offset_3 == -1
    assert m4.offset_4 == -1

    assert m5.name == 'Seram1'
    assert m5.longIdentifier == 'emulation RAM 1'
    assert m5.prgType == 'SERAM'
    assert m5.memoryType == 'RAM'
    assert m5.attribute == 'EXTERN'
    assert m5.address == 28672
    assert m5.size == 4096
    assert m5.offset_0 == -1
    assert m5.offset_1 == -1
    assert m5.offset_2 == -1
    assert m5.offset_3 == -1
    assert m5.offset_4 == -1

    assert m6.name == 'Seram2'
    assert m6.longIdentifier == 'emulation RAM 2'
    assert m6.prgType == 'SERAM'
    assert m6.memoryType == 'RAM'
    assert m6.attribute == 'INTERN'
    assert m6.address == 32768
    assert m6.size == 4096
    assert m6.offset_0 == -1
    assert m6.offset_1 == -1
    assert m6.offset_2 == -1
    assert m6.offset_3 == -1
    assert m6.offset_4 == -1

def test_mod_common():
    parser = ParserWrapper('a2l', 'modCommon', A2LListener, debug = False)
    DATA = """
    /begin MOD_COMMON "Characteristic maps always deposited in same mode"
        S_REC_LAYOUT S_ABL
        DEPOSIT ABSOLUTE
        BYTE_ORDER MSB_LAST
        DATA_SIZE 16
        ALIGNMENT_BYTE 2
    /end MOD_COMMON
    """
    session = parser.parseFromString(DATA)
    mc = session.query(model.ModCommon).first()
    assert mc.comment == 'Characteristic maps always deposited in same mode'
    assert mc.s_rec_layout.name == "S_ABL"
    assert mc.deposit.mode == 'ABSOLUTE'
    assert mc.byte_order.byteOrder == 'MSB_LAST'
    assert mc.data_size.size == 16
    assert mc.alignment_byte.alignmentBorder == 2

def test_mod_par():
    parser = ParserWrapper('a2l', 'modPar', A2LListener, debug = False)
    DATA = """
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
    """
    session = parser.parseFromString(DATA)
    mp = session.query(model.ModPar).first()
    assert mp.comment == 'Note: Provisional release for test purposes only!'

    assert mp.version.versionIdentifier == 'Test version of 01.02.1994'
    assert mp.addr_epk[0].address == 284280
    assert mp.epk.identifier == 'EPROM identifier test'
    assert mp.supplier.manufacturer == 'M&K GmbH Chemnitz'
    assert mp.customer.customer == 'LANZ-Landmaschinen'
    assert mp.customer_no.number == '0123456789'
    assert mp.user.userName == 'A.N.Wender'
    assert mp.phone_no.telnum == '09951 56456'
    assert mp.ecu.controlUnit == 'Engine control'
    assert mp.cpu_type.cPU == 'Motorola 0815'
    assert mp.no_of_interfaces.num == 2
    ms = mp.memory_segment[0]

    assert ms.name == 'ext_Ram'
    assert ms.longIdentifier == 'external RAM'
    assert ms.prgType == 'DATA'
    assert ms.memoryType == 'RAM'
    assert ms.attribute == 'EXTERN'
    assert ms.address == 196608
    assert ms.size == 4096
    assert ms.offset_0 == -1
    assert ms.offset_1 == -1
    assert ms.offset_2 == -1
    assert ms.offset_3 == -1
    assert ms.offset_4 == -1
    m0, m1, m2 = mp.memory_layout
    assert m0.prgType == 'PRG_RESERVED'
    assert m0.address == 0
    assert m0.size == 1024
    assert m0.offset_0 == -1
    assert m0.offset_1 == -1
    assert m0.offset_2 == -1
    assert m0.offset_3 == -1
    assert m0.offset_4 == -1

    assert m1.prgType == 'PRG_CODE'
    assert m1.address == 1024
    assert m1.size == 15360
    assert m1.offset_0 == -1
    assert m1.offset_1 == -1
    assert m1.offset_2 == -1
    assert m1.offset_3 == -1
    assert m1.offset_4 == -1

    assert m2.prgType == 'PRG_DATA'
    assert m2.address == 16384
    assert m2.size == 22528
    assert m2.offset_0 == -1
    assert m2.offset_1 == -1
    assert m2.offset_2 == -1
    assert m2.offset_3 == -1
    assert m2.offset_4 == -1

    s0, s1 = mp.system_constant
    assert s0.name == 'CONTROLLERx constant1'
    assert s0.value == '0.33'

    assert s1.name == 'CONTROLLERx constant2'
    assert s1.value == '2.79'

def test_monotony():
    parser = ParserWrapper('a2l', 'monotony', A2LListener, debug = False)
    DATA = """
    MONOTONY MON_INCREASE
    """
    session = parser.parseFromString(DATA)
    mn = session.query(model.Monotony).first()
    assert mn.monotony == "MON_INCREASE"

def test_no_axis_pts_x():
    parser = ParserWrapper('a2l', 'noAxisPtsX', A2LListener, debug = False)
    DATA = """
    NO_AXIS_PTS_X   2
                    UWORD
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.NoAxisPtsX).first()
    assert na.position == 2
    assert na.datatype == 'UWORD'

def test_no_axis_pts_y():
    parser = ParserWrapper('a2l', 'noAxisPtsY', A2LListener, debug = False)
    DATA = """
    NO_AXIS_PTS_Y   2
                    UWORD
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.NoAxisPtsY).first()
    assert na.position == 2
    assert na.datatype == 'UWORD'

def test_no_axis_pts_z():
    parser = ParserWrapper('a2l', 'noAxisPtsZ', A2LListener, debug = False)
    DATA = """
    NO_AXIS_PTS_Z   2
                    UWORD
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.NoAxisPtsZ).first()
    assert na.position == 2
    assert na.datatype == 'UWORD'

def test_no_axis_pts_4():
    parser = ParserWrapper('a2l', 'noAxisPts4', A2LListener, debug = False)
    DATA = """
    NO_AXIS_PTS_4   2
                    UWORD
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.NoAxisPts4).first()
    assert na.position == 2
    assert na.datatype == 'UWORD'

def test_no_axis_pts_5():
    parser = ParserWrapper('a2l', 'noAxisPts5', A2LListener, debug = False)
    DATA = """
    NO_AXIS_PTS_5   2
                    UWORD
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.NoAxisPts5).first()
    assert na.position == 2
    assert na.datatype == 'UWORD'

def test_no_of_interfaces():
    parser = ParserWrapper('a2l', 'noOfInterfaces', A2LListener, debug = False)
    DATA = """
    NO_OF_INTERFACES    2
    """
    session = parser.parseFromString(DATA)
    no = session.query(model.NoOfInterfaces).first()
    assert no.num == 2

def test_no_rescale_x():
    parser = ParserWrapper('a2l', 'noRescaleX', A2LListener, debug = False)
    DATA = """
    NO_RESCALE_X    1
                    UBYTE
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.NoRescaleX).first()
    assert na.position == 1
    assert na.datatype == 'UBYTE'

def test_no_rescale_y():
    parser = ParserWrapper('a2l', 'noRescaleY', A2LListener, debug = False)
    DATA = """
    NO_RESCALE_Y    1
                    UBYTE
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.NoRescaleY).first()
    assert na.position == 1
    assert na.datatype == 'UBYTE'

def test_no_rescale_z():
    parser = ParserWrapper('a2l', 'noRescaleZ', A2LListener, debug = False)
    DATA = """
    NO_RESCALE_Z    1
                    UBYTE
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.NoRescaleZ).first()
    assert na.position == 1
    assert na.datatype == 'UBYTE'

def test_no_rescale_4():
    parser = ParserWrapper('a2l', 'noRescale4', A2LListener, debug = False)
    DATA = """
    NO_RESCALE_4    1
                    UBYTE
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.NoRescale4).first()
    assert na.position == 1
    assert na.datatype == 'UBYTE'

def test_no_rescale_5():
    parser = ParserWrapper('a2l', 'noRescale5', A2LListener, debug = False)
    DATA = """
    NO_RESCALE_5    1
                    UBYTE
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.NoRescale5).first()
    assert na.position == 1
    assert na.datatype == 'UBYTE'

def test_number():
    parser = ParserWrapper('a2l', 'number', A2LListener, debug = False)
    DATA = """
    NUMBER  7
    """
    session = parser.parseFromString(DATA)
    nu = session.query(model.Number).first()
    assert nu.number == 7

def test_offset_x():
    parser = ParserWrapper('a2l', 'offsetX', A2LListener, debug = False)
    DATA = """
    OFFSET_X    16
                UWORD
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.OffsetX).first()
    assert na.position == 16
    assert na.datatype == 'UWORD'

def test_offset_y():
    parser = ParserWrapper('a2l', 'offsetY', A2LListener, debug = False)
    DATA = """
    OFFSET_Y    16
                UWORD
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.OffsetY).first()
    assert na.position == 16
    assert na.datatype == 'UWORD'

def test_offset_z():
    parser = ParserWrapper('a2l', 'offsetZ', A2LListener, debug = False)
    DATA = """
    OFFSET_Z    16
                UWORD
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.OffsetZ).first()
    assert na.position == 16
    assert na.datatype == 'UWORD'

def test_offset_4():
    parser = ParserWrapper('a2l', 'offset4', A2LListener, debug = False)
    DATA = """
    OFFSET_4    16
                UWORD
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.Offset4).first()
    assert na.position == 16
    assert na.datatype == 'UWORD'

def test_offset_5():
    parser = ParserWrapper('a2l', 'offset5', A2LListener, debug = False)
    DATA = """
    OFFSET_5    16
                UWORD
    """
    session = parser.parseFromString(DATA)
    na = session.query(model.Offset5).first()
    assert na.position == 16
    assert na.datatype == 'UWORD'

def test_out_measurement():
    parser = ParserWrapper('a2l', 'outMeasurement', A2LListener, debug = False)
    DATA = """
    /begin OUT_MEASUREMENT OK_FLAG
        SENSOR_FLAG
    /end OUT_MEASUREMENT
    """
    session = parser.parseFromString(DATA)
    om = session.query(model.OutMeasurement).first()
    assert om.identifier == ['OK_FLAG', 'SENSOR_FLAG']

def test_phone_no():
    parser = ParserWrapper('a2l', 'phoneNo', A2LListener, debug = False)
    DATA = """
    PHONE_NO "09498 594562"
    """
    session = parser.parseFromString(DATA)
    pn = session.query(model.PhoneNo).first()
    assert pn.telnum == "09498 594562"

def test_phys_unit():
    parser = ParserWrapper('a2l', 'physUnit', A2LListener, debug = False)
    DATA = """
    PHYS_UNIT "°C"
    """
    session = parser.parseFromString(DATA)
    pn = session.query(model.PhysUnit).first()
    assert pn.unit == "°C"

def test_project():
    parser = ParserWrapper('a2l', 'project', A2LListener, debug = False)
    DATA = """
    /begin PROJECT RAPE_SEED_ENGINE
        "Engine tuning for operation with rape oil"
        /begin HEADER "see also specification XYZ of 01.02.1994"
            VERSION "BG5.0815"
            PROJECT_NO M4711Z1
        /end HEADER
//        /include ENGINE_ECU.A2L /* Include for engine control module */
//        /include ABS_ECU.A2L /* Include for ABS module */
        /end PROJECT
    """
    session = parser.parseFromString(DATA)
    prj = session.query(model.Project).first()
    assert prj.name == 'RAPE_SEED_ENGINE'
    assert prj.longIdentifier == 'Engine tuning for operation with rape oil'
    assert prj.header.comment == 'see also specification XYZ of 01.02.1994'
    assert prj.header.version.versionIdentifier == 'BG5.0815'
    assert prj.header.project_no.projectNumber == 'M4711Z1'

def test_project_no():
    parser = ParserWrapper('a2l', 'projectNo', A2LListener, debug = False)
    DATA = """
    PROJECT_NO M4711Z1
    """
    session = parser.parseFromString(DATA)
    pn = session.query(model.ProjectNo).first()
    assert pn.projectNumber == 'M4711Z1'

def test_read_only():
    parser = ParserWrapper('a2l', 'characteristic', A2LListener, debug = False)
    DATA = """
    /begin CHARACTERISTIC KI "I-share for speed limitation"
        VALUE /* type: fixed value */
        0x408F /* address */
        DAMOS_FW /* deposit */
        0.0 /* max_diff */
        FACTOR01 /* conversion */
        0.0 /* lower limit */
        255.0 /* upper limit */
        /* interface-specific parameters: address location, addressing */
/*
        /begin IF_DATA "DIM" EXTERNAL
            DIRECT
        /end IF_DATA
*/
        /begin FUNCTION_LIST V_LIM /* Reference to functions */
        /end FUNCTION_LIST
        READ_ONLY
    /end CHARACTERISTIC
    """
    session = parser.parseFromString(DATA)
    chx = session.query(model.Characteristic).first()

    assert chx.name == 'KI'
    assert chx.longIdentifier == 'I-share for speed limitation'
    assert chx.type == 'VALUE'
    assert chx.address == 16527
    assert chx.deposit == 'DAMOS_FW'
    assert chx.maxDiff == 0.0
    assert chx.conversion == 'FACTOR01'
    assert chx.lowerLimit == 0.0
    assert chx.upperLimit == 255.0
    assert chx.function_list.name == ['V_LIM']
    assert chx.read_only == True
    """
    """

def test_read_write():
    parser = ParserWrapper('a2l', 'measurement', A2LListener, debug = False)
    DATA = """
    /begin MEASUREMENT N /* name */
        "Engine speed" /* long identifier */
        UWORD /* datatype */
        R_SPEED_3 /* conversion */
        2 /* resolution */
        2.5 /* accuracy */
        120.0 /* lower limit */
        8400.0 /* upper limit */
        READ_WRITE
/*
        /begin IF_DATA ISO SND
            0x10
            0x00
            0x05
            0x08
            RCV
            4
            long
        /end IF_DATA
*/
    /end MEASUREMENT
    """
    session = parser.parseFromString(DATA)
    meas = session.query(model.Measurement).first()
    assert meas.name == 'N'
    assert meas.longIdentifier == 'Engine speed'
    assert meas.datatype == 'UWORD'
    assert meas.conversion == 'R_SPEED_3'
    assert meas.resolution == 2
    assert meas.accuracy == 2.5
    assert meas.lowerLimit == 120.0
    assert meas.upperLimit == 8400.0
    assert meas.read_write is not None

def test_record_layout():
    parser = ParserWrapper('a2l', 'module', A2LListener, debug = False)
    DATA = """/begin MODULE testModule ""
        /begin RECORD_LAYOUT DAMOS_KF
            FNC_VALUES 7 SWORD COLUMN_DIR DIRECT
            AXIS_PTS_X 3 SWORD INDEX_INCR DIRECT
            AXIS_PTS_Y 6 UBYTE INDEX_INCR DIRECT
            NO_AXIS_PTS_X 2 UBYTE
            NO_AXIS_PTS_Y 5 UBYTE
//            SRC_ADDR_X 1
//            SRC_ADDR_Y 4
            ALIGNMENT_BYTE 2
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT RESCALE_SST
            NO_RESCALE_X 1 UBYTE
            RESERVED 2 BYTE
            AXIS_RESCALE_X 3 UBYTE 5 INDEX_INCR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT SHORTINT
            FNC_VALUES 1 SBYTE ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT BYTE_
            FNC_VALUES 1 UBYTE ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT INTEGER
            FNC_VALUES 1 SWORD ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT WORD_
            FNC_VALUES 1 UWORD ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT LONGINT
            FNC_VALUES 1 SLONG ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT LONGWORD
            FNC_VALUES 1 ULONG ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _2D_structure_table_int    /* FIXME: Accept identifiers starting with numbers!? */
            NO_AXIS_PTS_X 1 UWORD
            FNC_VALUES 2 SWORD ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _2D_structure_table_word
            NO_AXIS_PTS_X 1 UWORD
            FNC_VALUES 2 UWORD ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _2D_structure_table_byte
            NO_AXIS_PTS_X 1 UBYTE
            RESERVED 2 BYTE
            FNC_VALUES 3 UBYTE ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _2D_structure_table_shortint
            NO_AXIS_PTS_X 1 UBYTE
            RESERVED 2 BYTE
            FNC_VALUES 3 SBYTE ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _3D_structure_table_int
            NO_AXIS_PTS_X 1 UWORD
            NO_AXIS_PTS_Y 2 UWORD
            FNC_VALUES 3 SWORD ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _3D_structure_table_word
            NO_AXIS_PTS_X 1 UWORD
            NO_AXIS_PTS_Y 2 UWORD
            FNC_VALUES 3 UWORD ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _3D_structure_table_byte
            NO_AXIS_PTS_X 1 UBYTE
            NO_AXIS_PTS_Y 2 UBYTE
            RESERVED 3 BYTE
            FNC_VALUES 4 UBYTE ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _3D_structure_table_shortint
            NO_AXIS_PTS_X 1 UBYTE
            NO_AXIS_PTS_Y 2 UBYTE
            RESERVED 3 BYTE
            FNC_VALUES 4 SBYTE ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _2D_array_table_int
            FNC_VALUES 1 SWORD ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _2D_array_table_word
            FNC_VALUES 1 UWORD ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _2D_array_table_byte
            FNC_VALUES 1 UBYTE ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _2D_array_table_shortint
            FNC_VALUES 1 SBYTE ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _3D_array_table_int
            FNC_VALUES 1 SWORD ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _3D_array_table_word
            FNC_VALUES 1 UWORD ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _3D_array_table_byte
            FNC_VALUES 1 UBYTE ROW_DIR DIRECT
        /end RECORD_LAYOUT
        /begin RECORD_LAYOUT _3D_array_table_shortint
            FNC_VALUES 1 SBYTE ROW_DIR DIRECT
        /end RECORD_LAYOUT
    /end MODULE
    """
    session = parser.parseFromString(DATA)
    recs = session.query(model.RecordLayout).all()
    r0, r1, r2, r3, r4, r5, r6, r7, r8, r9, r10, r11, r12, r13, r14, r15, r16, r17, r18, r19, r20, r21, r22, r23 = recs
    assert r0.name == 'DAMOS_KF'
    assert r0.fnc_values.position == 7
    assert r0.fnc_values.datatype == 'SWORD'
    assert r0.fnc_values.indexMode == 'COLUMN_DIR'
    assert r0.fnc_values.addresstype == 'DIRECT'
    assert r0.axis_pts_x.position == 3
    assert r0.axis_pts_x.datatype == 'SWORD'
    assert r0.axis_pts_x.indexIncr == 'INDEX_INCR'
    assert r0.axis_pts_x.addressing == 'DIRECT'
    assert r0.axis_pts_y.position == 6
    assert r0.axis_pts_y.datatype == 'UBYTE'
    assert r0.axis_pts_y.indexIncr == 'INDEX_INCR'
    assert r0.axis_pts_y.addressing == 'DIRECT'
    assert r0.no_axis_pts_x.position == 2
    assert r0.no_axis_pts_x.datatype == 'UBYTE'
    assert r0.no_axis_pts_y.position == 5
    assert r0.no_axis_pts_y.datatype == 'UBYTE'
    assert r0.alignment_byte.alignmentBorder == 2

    assert r1.name == 'RESCALE_SST'
    assert r1.no_rescale_x.position == 1
    assert r1.no_rescale_x.datatype == 'UBYTE'
    assert r1.reserved is not None # FIXME
    assert r1.axis_rescale_x.position == 3
    assert r1.axis_rescale_x.datatype == 'UBYTE'
    assert r1.axis_rescale_x.maxNumberOfRescalePairs == 5
    assert r1.axis_rescale_x.indexIncr == 'INDEX_INCR'
    assert r1.axis_rescale_x.addressing == 'DIRECT'

    assert r2.name == 'SHORTINT'
    assert r2.fnc_values.position == 1
    assert r2.fnc_values.datatype == 'SBYTE'
    assert r2.fnc_values.indexMode == 'ROW_DIR'
    assert r2.fnc_values.addresstype == 'DIRECT'

    assert r3.name == 'BYTE_'
    assert r3.fnc_values.position == 1
    assert r3.fnc_values.datatype == 'UBYTE'
    assert r3.fnc_values.indexMode == 'ROW_DIR'
    assert r3.fnc_values.addresstype == 'DIRECT'

    assert r4.name == 'INTEGER'
    assert r4.fnc_values.position == 1
    assert r4.fnc_values.datatype == 'SWORD'
    assert r4.fnc_values.indexMode == 'ROW_DIR'
    assert r4.fnc_values.addresstype == 'DIRECT'

    assert r5.name == 'WORD_'
    assert r5.fnc_values.position == 1
    assert r5.fnc_values.datatype == 'UWORD'
    assert r5.fnc_values.indexMode == 'ROW_DIR'
    assert r5.fnc_values.addresstype == 'DIRECT'

    assert r6.name == 'LONGINT'
    assert r6.fnc_values.position == 1
    assert r6.fnc_values.datatype == 'SLONG'
    assert r6.fnc_values.indexMode == 'ROW_DIR'
    assert r6.fnc_values.addresstype == 'DIRECT'

    assert r7.name == 'LONGWORD'
    assert r7.fnc_values.position == 1
    assert r7.fnc_values.datatype == 'ULONG'
    assert r7.fnc_values.indexMode == 'ROW_DIR'
    assert r7.fnc_values.addresstype == 'DIRECT'

    assert r8.name == '_2D_structure_table_int'
    assert r8.fnc_values.position == 2
    assert r8.fnc_values.datatype == 'SWORD'
    assert r8.fnc_values.indexMode == 'ROW_DIR'
    assert r8.fnc_values.addresstype == 'DIRECT'
    assert r8.no_axis_pts_x.position == 1
    assert r8.no_axis_pts_x.datatype == 'UWORD'

    assert r9.name == '_2D_structure_table_word'
    assert r9.fnc_values.position == 2
    assert r9.fnc_values.datatype == 'UWORD'
    assert r9.fnc_values.indexMode == 'ROW_DIR'
    assert r9.fnc_values.addresstype == 'DIRECT'
    assert r9.no_axis_pts_x.position == 1
    assert r9.no_axis_pts_x.datatype == 'UWORD'

    assert r10.name == '_2D_structure_table_byte'
    assert r10.no_axis_pts_x.position == 1
    assert r10.no_axis_pts_x.datatype == 'UBYTE'
    assert r10.reserved is not None # FIXME
    assert r10.fnc_values.position == 3
    assert r10.fnc_values.datatype == 'UBYTE'
    assert r10.fnc_values.indexMode == 'ROW_DIR'
    assert r10.fnc_values.addresstype == 'DIRECT'

    assert r11.name == '_2D_structure_table_shortint'
    assert r11.no_axis_pts_x.position == 1
    assert r11.no_axis_pts_x.datatype == 'UBYTE'
    assert r11.reserved[0].position == 2
    assert r11.reserved[0].dataSize == 'BYTE'
    assert r11.fnc_values.position == 3
    assert r11.fnc_values.datatype == 'SBYTE'
    assert r11.fnc_values.indexMode == 'ROW_DIR'
    assert r11.fnc_values.addresstype == 'DIRECT'

    assert r12.name == '_3D_structure_table_int'
    assert r12.no_axis_pts_x.position == 1
    assert r12.no_axis_pts_x.datatype == 'UWORD'
    assert r12.no_axis_pts_y.position == 2
    assert r12.no_axis_pts_y.datatype == 'UWORD'
    assert r12.fnc_values.position == 3
    assert r12.fnc_values.datatype == 'SWORD'
    assert r12.fnc_values.indexMode == 'ROW_DIR'
    assert r12.fnc_values.addresstype == 'DIRECT'

    assert r13.name == '_3D_structure_table_word'
    assert r13.no_axis_pts_x.position == 1
    assert r13.no_axis_pts_x.datatype == 'UWORD'
    assert r13.no_axis_pts_y.position == 2
    assert r13.no_axis_pts_y.datatype == 'UWORD'
    assert r13.fnc_values.position == 3
    assert r13.fnc_values.datatype == 'UWORD'
    assert r13.fnc_values.indexMode == 'ROW_DIR'
    assert r13.fnc_values.addresstype == 'DIRECT'

    assert r14.name == '_3D_structure_table_byte'
    assert r14.no_axis_pts_x.position == 1
    assert r14.no_axis_pts_x.datatype == 'UBYTE'
    assert r14.no_axis_pts_y.position == 2
    assert r14.no_axis_pts_y.datatype == 'UBYTE'
    assert r14.fnc_values.position == 4
    assert r14.fnc_values.datatype == 'UBYTE'
    assert r14.fnc_values.indexMode == 'ROW_DIR'
    assert r14.fnc_values.addresstype == 'DIRECT'
    assert r14.reserved[0].position == 3
    assert r14.reserved[0].dataSize == 'BYTE'

    assert r15.name == '_3D_structure_table_shortint'
    assert r15.no_axis_pts_x.position == 1
    assert r15.no_axis_pts_x.datatype == 'UBYTE'
    assert r15.no_axis_pts_y.position == 2
    assert r15.no_axis_pts_y.datatype == 'UBYTE'
    assert r15.fnc_values.position == 4
    assert r15.fnc_values.datatype == 'SBYTE'
    assert r15.fnc_values.indexMode == 'ROW_DIR'
    assert r15.fnc_values.addresstype == 'DIRECT'
    assert r15.reserved[0].position == 3
    assert r15.reserved[0].dataSize == 'BYTE'

    assert r16.name == '_2D_array_table_int'
    assert r16.fnc_values.position == 1
    assert r16.fnc_values.datatype == 'SWORD'
    assert r16.fnc_values.indexMode == 'ROW_DIR'
    assert r16.fnc_values.addresstype == 'DIRECT'

    assert r17.name == '_2D_array_table_word'
    assert r17.fnc_values.position == 1
    assert r17.fnc_values.datatype == 'UWORD'
    assert r17.fnc_values.indexMode == 'ROW_DIR'
    assert r17.fnc_values.addresstype == 'DIRECT'

    assert r18.name == '_2D_array_table_byte'
    assert r18.fnc_values.position == 1
    assert r18.fnc_values.datatype == 'UBYTE'
    assert r18.fnc_values.indexMode == 'ROW_DIR'
    assert r18.fnc_values.addresstype == 'DIRECT'

    assert r19.name == '_2D_array_table_shortint'
    assert r19.fnc_values.position == 1
    assert r19.fnc_values.datatype == 'SBYTE'
    assert r19.fnc_values.indexMode == 'ROW_DIR'
    assert r19.fnc_values.addresstype == 'DIRECT'

    assert r20.name == '_3D_array_table_int'
    assert r20.fnc_values.position == 1
    assert r20.fnc_values.datatype == 'SWORD'
    assert r20.fnc_values.indexMode == 'ROW_DIR'
    assert r20.fnc_values.addresstype == 'DIRECT'

    assert r21.name == '_3D_array_table_word'
    assert r21.fnc_values.position == 1
    assert r21.fnc_values.datatype == 'UWORD'
    assert r21.fnc_values.indexMode == 'ROW_DIR'
    assert r21.fnc_values.addresstype == 'DIRECT'

    assert r22.name == '_3D_array_table_byte'
    assert r22.fnc_values.position == 1
    assert r22.fnc_values.datatype == 'UBYTE'
    assert r22.fnc_values.indexMode == 'ROW_DIR'
    assert r22.fnc_values.addresstype == 'DIRECT'

    assert r23.name == '_3D_array_table_shortint'
    assert r23.fnc_values.position == 1
    assert r23.fnc_values.datatype == 'SBYTE'
    assert r23.fnc_values.indexMode == 'ROW_DIR'
    assert r23.fnc_values.addresstype == 'DIRECT'

def test_ref_characteristic():
    parser = ParserWrapper('a2l', 'refCharacteristic', A2LListener, debug = False)
    DATA = """
    /begin REF_CHARACTERISTIC ENG_SPEED_CORR_CURVE
    /end REF_CHARACTERISTIC
    """
    session = parser.parseFromString(DATA)
    rc = session.query(model.RefCharacteristic).first()
    assert rc.identifier == ['ENG_SPEED_CORR_CURVE']

def test_ref_group():
    parser = ParserWrapper('a2l', 'refGroup', A2LListener, debug = False)
    DATA = """
    /begin REF_GROUP GROUP_1
        GROUP_2
    /end REF_GROUP
    """
    session = parser.parseFromString(DATA)
    rg = session.query(model.RefGroup).first()
    assert rg.identifier == ['GROUP_1', 'GROUP_2']

def test_ref_measurement():
    parser = ParserWrapper('a2l', 'refMeasurement', A2LListener, debug = False)
    DATA = """
    /begin REF_MEASUREMENT LOOP_COUNTER
        TEMPORARY_1
    /end REF_MEASUREMENT
    """
    session = parser.parseFromString(DATA)
    rm = session.query(model.RefMeasurement).first()
    assert rm.identifier == ["LOOP_COUNTER", "TEMPORARY_1"]

def test_ref_memory_segment():
    parser = ParserWrapper('a2l', 'refMemorySegment', A2LListener, debug = False)
    DATA = """
    REF_MEMORY_SEGMENT Data1
    """
    session = parser.parseFromString(DATA)
    rm = session.query(model.RefMemorySegment).first()
    assert rm.name == "Data1"

def test_ref_unit():
    parser = ParserWrapper('a2l', 'compuMethod', A2LListener, debug = False)
    DATA = """
    /begin COMPU_METHOD Velocity
        "conversion method for velocity"
        RAT_FUNC
        "%6.2"
        "[km/h]"
        COEFFS 0 100 0 0 0 1
        REF_UNIT kms_per_hour /* new (optional) parameter */
    /end COMPU_METHOD
    """
    session = parser.parseFromString(DATA)
    cm = session.query(model.CompuMethod).first()
    assert cm.name == 'Velocity'
    assert cm.longIdentifier == 'conversion method for velocity'
    assert cm.conversionType == 'RAT_FUNC'
    assert cm.format == '%6.2'
    assert cm.unit == '[km/h]'
    assert cm.coeffs.a == 0.0
    assert cm.coeffs.b == 100.0
    assert cm.coeffs.c == 0.0
    assert cm.coeffs.d == 0.0
    assert cm.coeffs.e == 0.0
    assert cm.coeffs.f == 1.0
    assert cm.ref_unit.unit == 'kms_per_hour'

def test_reserved():
    parser = ParserWrapper('a2l', 'reserved', A2LListener, debug = False)
    DATA = """
    RESERVED 7
        LONG
    """
    session = parser.parseFromString(DATA)
    rs = session.query(model.Reserved).first()
    assert rs.position == 7
    assert rs.dataSize == 'LONG'

def test_rip_addr_w():
    parser = ParserWrapper('a2l', 'ripAddrW', A2LListener, debug = False)
    DATA = """
    RIP_ADDR_W 19
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.RipAddrW).first()
    assert ra.position == 19
    assert ra.datatype == 'UWORD'

def test_rip_addr_x():
    parser = ParserWrapper('a2l', 'ripAddrX', A2LListener, debug = False)
    DATA = """
    RIP_ADDR_X 19
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.RipAddrX).first()
    assert ra.position == 19
    assert ra.datatype == 'UWORD'

def test_rip_addr_y():
    parser = ParserWrapper('a2l', 'ripAddrY', A2LListener, debug = False)
    DATA = """
    RIP_ADDR_Y 19
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.RipAddrY).first()
    assert ra.position == 19
    assert ra.datatype == 'UWORD'

def test_rip_addr_z():
    parser = ParserWrapper('a2l', 'ripAddrZ', A2LListener, debug = False)
    DATA = """
    RIP_ADDR_Z 19
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.RipAddrZ).first()
    assert ra.position == 19
    assert ra.datatype == 'UWORD'

def test_rip_addr_4():
    parser = ParserWrapper('a2l', 'ripAddr4', A2LListener, debug = False)
    DATA = """
    RIP_ADDR_4 19
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.RipAddr4).first()
    assert ra.position == 19
    assert ra.datatype == 'UWORD'

def test_rip_addr_5():
    parser = ParserWrapper('a2l', 'ripAddr5', A2LListener, debug = False)
    DATA = """
    RIP_ADDR_5 19
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.RipAddr5).first()
    assert ra.position == 19
    assert ra.datatype == 'UWORD'

def test_root():
    parser = ParserWrapper('a2l', 'group', A2LListener, debug = False)
    DATA = """
    /begin GROUP SOFTWARE_COMPONENTS
        "assignment of the definitions to C files"
        ROOT
        /begin SUB_GROUP INJE
            C6TD
        /end SUB_GROUP
    /end GROUP
    """
    session = parser.parseFromString(DATA)
    grp = session.query(model.Group).first()
    assert grp.groupName == 'SOFTWARE_COMPONENTS'
    assert grp.groupLongIdentifier == 'assignment of the definitions to C files'
    assert grp.root is not None
    assert grp.sub_group.identifier == ['INJE', 'C6TD']

def test_shift_op_x():
    parser = ParserWrapper('a2l', 'shiftOpX', A2LListener, debug = False)
    DATA = """
    SHIFT_OP_X 21
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.ShiftOpX).first()
    assert ra.position == 21
    assert ra.datatype == 'UWORD'

def test_shift_op_y():
    parser = ParserWrapper('a2l', 'shiftOpY', A2LListener, debug = False)
    DATA = """
    SHIFT_OP_Y 21
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.ShiftOpY).first()
    assert ra.position == 21
    assert ra.datatype == 'UWORD'

def test_shift_op_z():
    parser = ParserWrapper('a2l', 'shiftOpZ', A2LListener, debug = False)
    DATA = """
    SHIFT_OP_Z 21
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.ShiftOpZ).first()
    assert ra.position == 21
    assert ra.datatype == 'UWORD'

def test_shift_op_4():
    parser = ParserWrapper('a2l', 'shiftOp4', A2LListener, debug = False)
    DATA = """
    SHIFT_OP_4 21
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.ShiftOp4).first()
    assert ra.position == 21
    assert ra.datatype == 'UWORD'

def test_shift_op_5():
    parser = ParserWrapper('a2l', 'shiftOp5', A2LListener, debug = False)
    DATA = """
    SHIFT_OP_5 21
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.ShiftOp5).first()
    assert ra.position == 21
    assert ra.datatype == 'UWORD'

def test_si_exponents():
    parser = ParserWrapper('a2l', 'unit', A2LListener, debug = False)
    DATA = """
    /begin UNIT
        newton
        "extended SI unit for force"
        "[N]"
        EXTENDED_SI
        SI_EXPONENTS 1 1 -2 0 0 0 0 /*[N] = [m]*[kg]*[s] -2 */
    /end UNIT
    """
    session = parser.parseFromString(DATA)
    unit = session.query(model.Unit).first()
    assert unit.name == 'newton'
    assert unit.longIdentifier == 'extended SI unit for force'
    assert unit.display == '[N]'
    assert unit.type == 'EXTENDED_SI'
    assert unit.si_exponents.length == 1
    assert unit.si_exponents.mass == 1
    assert unit.si_exponents.time == -2
    assert unit.si_exponents.electricCurrent == 0
    assert unit.si_exponents.temperature == 0
    assert unit.si_exponents.amountOfSubstance == 0
    assert unit.si_exponents.luminousIntensity == 0

def test_src_addr_x():
    parser = ParserWrapper('a2l', 'srcAddrX', A2LListener, debug = False)
    DATA = """
    SRC_ADDR_X 1
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.SrcAddrX).first()
    assert ra.position == 1
    assert ra.datatype == 'UWORD'

def test_src_addr_y():
    parser = ParserWrapper('a2l', 'srcAddrY', A2LListener, debug = False)
    DATA = """
    SRC_ADDR_Y 1
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.SrcAddrY).first()
    assert ra.position == 1
    assert ra.datatype == 'UWORD'

def test_src_addr_z():
    parser = ParserWrapper('a2l', 'srcAddrZ', A2LListener, debug = False)
    DATA = """
    SRC_ADDR_Z 1
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.SrcAddrZ).first()
    assert ra.position == 1
    assert ra.datatype == 'UWORD'

def test_src_addr_4():
    parser = ParserWrapper('a2l', 'srcAddr4', A2LListener, debug = False)
    DATA = """
    SRC_ADDR_4 1
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.SrcAddr4).first()
    assert ra.position == 1
    assert ra.datatype == 'UWORD'

def test_src_addr_5():
    parser = ParserWrapper('a2l', 'srcAddr5', A2LListener, debug = False)
    DATA = """
    SRC_ADDR_5 1
        UWORD
    """
    session = parser.parseFromString(DATA)
    ra = session.query(model.SrcAddr5).first()
    assert ra.position == 1
    assert ra.datatype == 'UWORD'

def test_static_record_layout():
    parser = ParserWrapper('a2l', 'recordLayout', A2LListener, debug = False)
    DATA = """
    /begin RECORD_LAYOUT
        mapLayoutNotCompact
        NO_AXIS_PTS_X 1 UWORD
        NO_AXIS_PTS_Y 2 UWORD
        AXIS_PTS_X 3 UBYTE INDEX_INCR DIRECT
        AXIS_PTS_Y 4 UBYTE INDEX_INCR DIRECT
        FNC_VALUES 5 UBYTE ROW_DIR DIRECT
        STATIC_RECORD_LAYOUT
    /end RECORD_LAYOUT
    """
    session = parser.parseFromString(DATA)
    rl = session.query(model.RecordLayout).first()
    assert rl.name == 'mapLayoutNotCompact'
    assert rl.no_axis_pts_x.position == 1
    assert rl.no_axis_pts_x.datatype == 'UWORD'
    assert rl.no_axis_pts_y.position == 2
    assert rl.no_axis_pts_y.datatype == 'UWORD'
    assert rl.axis_pts_x.position == 3
    assert rl.axis_pts_x.datatype == 'UBYTE'
    assert rl.axis_pts_x.indexIncr == 'INDEX_INCR'
    assert rl.axis_pts_x.addressing == 'DIRECT'
    assert rl.axis_pts_y.position == 4
    assert rl.axis_pts_y.datatype == 'UBYTE'
    assert rl.axis_pts_y.indexIncr == 'INDEX_INCR'
    assert rl.axis_pts_y.addressing == 'DIRECT'
    assert rl.fnc_values.position == 5
    assert rl.fnc_values.datatype == 'UBYTE'
    assert rl.fnc_values.indexMode == 'ROW_DIR'
    assert rl.fnc_values.addresstype == 'DIRECT'
    assert rl.static_record_layout is not None

def test_status_string_ref():
    parser = ParserWrapper('a2l', 'compuMethod', A2LListener, debug = False)
    DATA = """
    /begin COMPU_METHOD CM_LINFUNC_SENSOR_A /* name */
        "conversion method for Sensor A"
        LINEAR /* convers_type */
        "%4.0" /* display format */
        "rpm" /* physical unit */
        COEFFS_LINEAR 2.0 5.0
        STATUS_STRING_REF CT_SensorStatus
    /end COMPU_METHOD
    """
    session = parser.parseFromString(DATA)
    cm = session.query(model.CompuMethod).first()
    assert cm.name == 'CM_LINFUNC_SENSOR_A'
    assert cm.longIdentifier == 'conversion method for Sensor A'
    assert cm.conversionType == 'LINEAR'
    assert cm.format == '%4.0'
    assert cm.unit == 'rpm'
    assert cm.coeffs_linear.a == 2.0
    assert cm.coeffs_linear.b == 5.0
    assert cm.status_string_ref.conversionTable == 'CT_SensorStatus'

def test_step_size():
    parser = ParserWrapper('a2l', 'stepSize', A2LListener, debug = False)
    DATA = """
    STEP_SIZE 0.025
    """
    session = parser.parseFromString(DATA)
    ss = session.query(model.StepSize).first()
    assert ss.stepSize == 0.025

def test_sub_function():
    parser = ParserWrapper('a2l', 'subFunction', A2LListener, debug = False)
    DATA = """
    /begin SUB_FUNCTION ID_ADJUSTM_SUB
    /end SUB_FUNCTION
    """
    session = parser.parseFromString(DATA)
    sf = session.query(model.SubFunction).first()
    assert sf.identifier == ['ID_ADJUSTM_SUB']

def test_sub_group():
    parser = ParserWrapper('a2l', 'subGroup', A2LListener, debug = False)
    DATA = """
    /begin SUB_GROUP ID_ADJUSTM_SUB
    /end SUB_GROUP
    """
    session = parser.parseFromString(DATA)
    sf = session.query(model.SubGroup).first()
    assert sf.identifier == ['ID_ADJUSTM_SUB']

def test_supplier():
    parser = ParserWrapper('a2l', 'supplier', A2LListener, debug = False)
    DATA = """
    SUPPLIER "Smooth and Easy"
    """
    session = parser.parseFromString(DATA)
    sp = session.query(model.Supplier).first()
    assert sp.manufacturer == "Smooth and Easy"

def test_symbol_link():
    parser = ParserWrapper('a2l', 'symbolLink', A2LListener, debug = False)
    DATA = """
    SYMBOL_LINK "_VehicleSpeed" /* Symbol name */
                0
    """
    session = parser.parseFromString(DATA)
    sl = session.query(model.SymbolLink).first()
    assert sl.symbolName == '_VehicleSpeed'
    assert sl.offset == 0

def test_system_constant():
    parser = ParserWrapper('a2l', 'systemConstant', A2LListener, debug = False)
    DATA = """
    SYSTEM_CONSTANT "CONTROLLER_CONSTANT12"
        "2.7134"
    """
    session = parser.parseFromString(DATA)
    sc = session.query(model.SystemConstant).first()
    assert sc.name == 'CONTROLLER_CONSTANT12'
    assert sc.value == '2.7134'

def test_s_rec_layout():
    parser = ParserWrapper('a2l', 'sRecLayout', A2LListener, debug = False)
    DATA = """
    S_REC_LAYOUT S_ABL /* record layout */
    """
    session = parser.parseFromString(DATA)
    sl = session.query(model.SRecLayout).first()
    assert sl.name == "S_ABL"

def test_unit():
    parser = ParserWrapper('a2l', 'unit', A2LListener, debug = False)
    DATA = """
    /begin UNIT
        kms_per_hour
        "derived unit for velocity: kilometres per hour"
        "[km/h]"
        DERIVED
        REF_UNIT metres_per_second
        UNIT_CONVERSION 3.6 0.0 /* y [km/h] = (60*60/1000) * x [m/s] + 0.0 */
    /end UNIT
    """
    session = parser.parseFromString(DATA)
    unit = session.query(model.Unit).first()
    assert unit.name == 'kms_per_hour'
    assert unit.longIdentifier == 'derived unit for velocity: kilometres per hour'
    assert unit.display == '[km/h]'
    assert unit.type == 'DERIVED'
    assert unit.ref_unit.unit == 'metres_per_second'
    assert unit.unit_conversion.gradient == 3.6
    assert unit.unit_conversion.offset == 0.0

def test_unit_conversion():
    parser = ParserWrapper('a2l', 'unit', A2LListener, debug = False)
    DATA = """
    /begin UNIT
        degC
        "unit for temperature: degree Celsius"
        "[°C]"
        DERIVED
        REF_UNIT kelvin
        UNIT_CONVERSION 1.0 -273.15 /* y [°C] = 1.0 * x [K] + (-273.15) */
    /end UNIT
    """
    session = parser.parseFromString(DATA)
    unit = session.query(model.Unit).first()
    assert unit.name == 'degC'
    assert unit.longIdentifier == 'unit for temperature: degree Celsius'
    assert unit.display == '[°C]'
    assert unit.type == 'DERIVED'
    assert unit.ref_unit.unit == 'kelvin'
    assert unit.unit_conversion.gradient == 1.0
    assert unit.unit_conversion.offset == -273.15

def test_user():
    parser = ParserWrapper('a2l', 'user', A2LListener, debug = False)
    DATA = """
    USER "Nigel Hurst"
    """
    session = parser.parseFromString(DATA)
    sp = session.query(model.User).first()
    assert sp.userName == "Nigel Hurst"

def test_user_rights():
    parser = ParserWrapper('a2l', 'userRights', A2LListener, debug = False)
    DATA = """
    /begin USER_RIGHTS calibration_engineers
        /begin REF_GROUP group_1
        /end REF_GROUP
    /end USER_RIGHTS
    """
    session = parser.parseFromString(DATA)
    ur = session.query(model.UserRights).first()
    assert ur.userLevelId == 'calibration_engineers'
    assert ur.ref_group[0].identifier == ['group_1']

def test_var_address():
    parser = ParserWrapper('a2l', 'varAddress', A2LListener, debug = False)
    DATA = """
    /begin VAR_ADDRESS
        0x8840
        0x8858
        0x8870
        0x8888
    /end VAR_ADDRESS
    """
    session = parser.parseFromString(DATA)
    va = session.query(model.VarAddress).first()
    assert va.address == [34880, 34904, 34928, 34952]

def test_var_characteristic():
    parser = ParserWrapper('a2l', 'varCharacteristic', A2LListener, debug = False)
    DATA = """
    /begin VAR_CHARACTERISTIC /* define NLLM as variant coded */
        NLLM
        Gear Car
        /* gear box including the 2 variants "Manual" and "Automatic" */
        /* car body including the 3 variants "Limousine", "Kombi" and
        "Cabrio" */
        /* four addresses corresponding to the four valid combinations */
        /* of criterion 'Gear' and 'Car' (see example for VAR_CRITERION)*/
        /begin VAR_ADDRESS
            0x8840
            0x8858
            0x8870
            0x8888
        /end VAR_ADDRESS
    /end VAR_CHARACTERISTIC
    """
    session = parser.parseFromString(DATA)
    vc = session.query(model.VarCharacteristic).first()
    assert vc.name == 'NLLM'
    assert vc.criterionName == ['Gear', 'Car']
    va = vc.var_address
    assert va.address == [34880, 34904, 34928, 34952]

def test_var_criterion():
    parser = ParserWrapper('a2l', 'varCriterion', A2LListener, debug = False)
    DATA = """
    /* variant criterion "Car body" with three variants */
    /begin VAR_CRITERION Car
        "Car body"
        /*Enumeration of criterion values*/
        Limousine Kombi Cabrio
        VAR_MEASUREMENT S_CAR
        VAR_SELECTION_CHARACTERISTIC V_CAR
    /end VAR_CRITERION
    """
    session = parser.parseFromString(DATA)
    vc = session.query(model.VarCriterion).first()
    assert vc.name == 'Car'
    assert vc.longIdentifier == 'Car body'
    assert vc.var_measurement.name == 'S_CAR'
    assert vc.var_selection_characteristic.name == "V_CAR"

def test_var_forbidden_comb():
    parser = ParserWrapper('a2l', 'variantCoding', debug = False)
    DATA = """
    /begin VARIANT_CODING
        /begin VAR_FORBIDDEN_COMB
            Car Limousine
            Gear Manual
        /end VAR_FORBIDDEN_COMB
    /end VARIANT_CODING
    """
    session = parser.parseFromString(DATA)
    vf = session.query(model.VarForbiddenComb).first()
    print(vf)

def test_var_measurement():
    parser = ParserWrapper('a2l', 'varCriterion', A2LListener, debug = False)
    DATA = """
    /begin VAR_CRITERION Car
        "Car body"
        Limousine Kombi Cabrio
        VAR_MEASUREMENT S_GEAR_BOX
    /end VAR_CRITERION
    """
    session = parser.parseFromString(DATA)
    vc = session.query(model.VarCriterion).first()
    assert vc.name == 'Car'
    assert vc.longIdentifier == 'Car body'
    assert vc.var_measurement.name == "S_GEAR_BOX"

def test_var_naming():
    parser = ParserWrapper('a2l', 'varNaming', A2LListener, debug = False)
    DATA = """
    /* variant extension: see example VAR_CRITERION*/
    VAR_NAMING NUMERIC
    """
    session = parser.parseFromString(DATA)
    vn = session.query(model.VarNaming).first()
    assert vn.tag == 'NUMERIC'

def test_var_selection_characteristic():
    parser = ParserWrapper('a2l', 'varCriterion', A2LListener, debug = False)
    DATA = """
    /begin VAR_CRITERION Car
        "Car body"
        Limousine Kombi Cabrio
        VAR_SELECTION_CHARACTERISTIC S_GEAR_BOX
    /end VAR_CRITERION
    """
    session = parser.parseFromString(DATA)
    vs = session.query(model.VarCriterion).first()
    assert vs.name == 'Car'
    assert vs.longIdentifier == 'Car body'
    assert vs.var_selection_characteristic.name == 'S_GEAR_BOX'

def test_var_separator():
    parser = ParserWrapper('a2l', 'varSeparator', A2LListener, debug = False)
    DATA = """
    VAR_SEPARATOR "." /* example: "PUMKF.1" */
    /* three parts of variant coded adjustable objects name: */
    /* 1.) Identifier of adjustable object: "PUMKF" */
    /* 2.) Separator: "." (decimal point) */
    /* 3.) Variants extension: "1" */
    """
    session = parser.parseFromString(DATA)
    vs = session.query(model.VarSeparator).first()
    assert vs.separator == '.'

def test_variant_coding():
    parser = ParserWrapper('a2l', 'variantCoding', A2LListener, debug = False)
    DATA = """
    /begin VARIANT_CODING
        VAR_SEPARATOR "." /* PUMKF.1 */
        VAR_NAMING NUMERIC
        /* variant criterion "Car body" with three variants */
        /begin VAR_CRITERION Car
            "Car body"
            Limousine Kombi Cabrio
        /end VAR_CRITERION
        /* variant criterion "Type of gear box" with two variants */
        /begin VAR_CRITERION Gear
            "Type of gear box"
            Manual Automatic
        /end VAR_CRITERION
        /begin VAR_FORBIDDEN_COMB /* forbidden: Limousine-Manual*/
            Car Limousine
            Gear Manual
        /end VAR_FORBIDDEN_COMB
        /begin VAR_FORBIDDEN_COMB /* forbidden: Cabrio-Automatic*/
            Car Cabrio
            Gear Automatic
        /end VAR_FORBIDDEN_COMB
        /begin VAR_CHARACTERISTIC
            PUMKF /*define PUMKF as variant coded*/
            Gear /* Gear box variants */
            /begin VAR_ADDRESS
                0x7140
                0x7168
            /end VAR_ADDRESS
        /end VAR_CHARACTERISTIC
        /begin VAR_CHARACTERISTIC
            NLLM /*define NLLM as variant coded */
            Gear Car /*car body and gear box
            variants*/
            /begin VAR_ADDRESS
                0x8840
                0x8858
                0x8870
                0x8888
            /end VAR_ADDRESS
        /end VAR_CHARACTERISTIC
    /end VARIANT_CODING
    """
    session = parser.parseFromString(DATA)
    vc = session.query(model.VariantCoding).first()
    assert vc.var_separator.separator == '.'
    assert vc.var_naming.tag == 'NUMERIC'
    c0, c1= vc.var_criterion
    assert c0.name == 'Car'
    assert c0.longIdentifier == 'Car body'
    assert c1.name == 'Gear'
    assert c1.longIdentifier == 'Type of gear box'
    fc0, fc1 = vc.var_forbidden_comb
    fc0 = fc0.pairs
    fc1 = fc1.pairs
    assert fc0[0].criterionName == 'Car'
    assert fc0[0].criterionValue == 'Limousine'
    assert fc0[1].criterionName == 'Gear'
    assert fc0[1].criterionValue == 'Manual'
    assert fc1[0].criterionName == 'Car'
    assert fc1[0].criterionValue == 'Cabrio'
    assert fc1[1].criterionName == 'Gear'
    assert fc1[1].criterionValue == 'Automatic'
    v0, v1 = vc.var_characteristic
    assert v0.name == "PUMKF"
    assert v0.criterionName == ["Gear"]
    assert v0.var_address.address == [28992, 29032]
    assert v1.name == "NLLM"
    assert v1.criterionName == ['Gear', 'Car']
    assert v1.var_address.address == [34880, 34904, 34928, 34952]

def test_version():
    parser = ParserWrapper('a2l', 'version', A2LListener, debug = False)
    DATA = """
    VERSION "BG5.0815"
    """
    session = parser.parseFromString(DATA)
    vs = session.query(model.Version).first()
    assert vs.versionIdentifier == 'BG5.0815'

def test_virtual():
    parser = ParserWrapper('a2l', 'measurement', A2LListener, debug = False)
    DATA = """
    /begin MEASUREMENT PHI_FIRING /* Name */
        "Firing angle" /* Long identifier */
        UWORD /* Data type */
        R_PHI_FIRING /* Conversion */
        1 /* Resolution */
        0.01 /* Accuracy */
        120.0 /* Lower limit */
        8400.0 /* Upper limit */
        /*Quantities to be linked: 2 measurements */
        /begin VIRTUAL PHI_BASIS
            PHI_CORR
        /end VIRTUAL
    /end MEASUREMENT
    """
    session = parser.parseFromString(DATA)
    meas = session.query(model.Measurement).first()
    assert meas.name == 'PHI_FIRING'
    assert meas.longIdentifier == 'Firing angle'
    assert meas.datatype == 'UWORD'
    assert meas.conversion == 'R_PHI_FIRING'
    assert meas.resolution == 1
    assert meas.accuracy == 0.01
    assert meas.lowerLimit == 120.0
    assert meas.upperLimit == 8400.0
    assert meas.virtual.measuringChannel == ['PHI_BASIS', 'PHI_CORR']

def test_virtual_characteristic():
    parser = ParserWrapper('a2l', 'virtualCharacteristic', A2LListener, debug = False)
    DATA = """
    /begin VIRTUAL_CHARACTERISTIC
        "sin(X1)"
        B
    /end VIRTUAL_CHARACTERISTIC
    """
    session = parser.parseFromString(DATA)
    vs = session.query(model.VirtualCharacteristic).first()
    assert vs.characteristic_id == ['B']
    assert vs.formula == 'sin(X1)'

def test_meta_data():
    parser = ParserWrapper('a2l', 'project', A2LListener, debug = False)
    DATA = """
    /begin PROJECT FOO_BAR ""

    /end PROJECT
    """
    from pya2l.model import CURRENT_SCHEMA_VERSION

    session = parser.parseFromString(DATA)
    meta = session.query(model.MetaData).first()
    assert meta.schema_version == CURRENT_SCHEMA_VERSION

def test_multi_dimensional_array():
    parser = ParserWrapper('a2l', 'characteristic', A2LListener, debug = False)
    DATA = '''/begin CHARACTERISTIC TEST[0][0].TEST
        "TEST[FL,0].TEST"
        VALUE
        0x0003237C
        _HELLO
        30
        _TEST
        -18
        12
        DISPLAY_IDENTIFIER TEST[FL_0].TEST
        FORMAT "%3.1"
    /end CHARACTERISTIC
    '''
    session = parser.parseFromString(DATA)
    chx = session.query(model.Characteristic).first()

def test_asap2_version():
    parser = ParserWrapper('a2l', 'asap2Version', A2LListener, debug = False)
    DATA = """
    ASAP2_VERSION 1 60
    """
    session = parser.parseFromString(DATA)
    vers = session.query(model.Asap2Version).first()
    assert vers.versionNo == 1
    assert vers.upgradeNo == 60

def test_asap2_version_out_of_range():
    parser = ParserWrapper('a2l', 'asap2Version', A2LListener, debug = False)
    DATA = """
    ASAP2_VERSION 1 30
    """
    session = parser.parseFromString(DATA)
    vers = session.query(model.Asap2Version).first()
    assert vers.versionNo == 1
    assert vers.upgradeNo == 30

def test_a2ml_version():
    parser = ParserWrapper('a2l', 'a2mlVersion', A2LListener, debug = False)
    DATA = """
    A2ML_VERSION 1 2
    """
    session = parser.parseFromString(DATA)
    vers = session.query(model.A2mlVersion).first()
    assert vers.versionNo == 1
    assert vers.upgradeNo == 2
