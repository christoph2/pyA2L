#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""These test-cases are based on the examples from ASAM MCD-2MC Version 1.6 specification.
"""

import pytest

import pya2l.model as model
from pya2l.a2l_listener import ParserWrapper, A2LListener, cut_a2ml

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
    res = session.query(model.AnnotationLabel).all()
    assert len(res) == 1
    assert res[0].label == 'Calibration Note'

def test_annotation_origin():
    parser = ParserWrapper('a2l', 'annotationOrigin', A2LListener, debug = False)
    DATA = 'ANNOTATION_ORIGIN   "from the calibration planning department"'
    session = parser.parseFromString(DATA)
    res = session.query(model.AnnotationOrigin).all()
    assert len(res) == 1
    assert res[0].origin == 'from the calibration planning department'

def test_annotation_text():
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
    assert meas.bit_mask[0].mask == 0x0fff
    assert meas.byte_order[0].byteOrder == "MSB_FIRST"
    fl = meas.function_list[0]
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
    #assert ap.deposit == None  # TODO: FIXME!
    assert ap.maxDiff == 100.0
    assert ap.conversion == 'R_SPEED'
    assert ap.maxAxisPoints == 21
    assert ap.lowerLimit == 0.0
    assert ap.upperLimit == 5800.0
    assert ap.guard_rails is not None
    assert ap.ref_memory_segment[0].name == 'Data3'
    fl = ap.function_list[0]
    assert fl.name == ['ID_ADJUSTM', 'FL_ADJUSTM', 'SPEED_LIM']
    assert ap.calibration_access[0].type == "CALIBRATION"

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
    assert len(chx.axis_descrs) == 1
    descr = chx.axis_descrs[0]  # TODO: axis_descr
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

def test_bit_operation():
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
    assert cm.calibration_handles[0].handle == [65536, 512, 4, 65536, 65536]

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
    ax = cr.axis_descrs
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
    cm = mod.compu_methods
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
    cvt = module.compu_vtabs
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
    assert cvr.default_value[0].display_string == 'Value_out_of_Range'
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
    rl0, rl1 = mod.record_layouts
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
    chx = mod.characteristics
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
    ad0, ad1 = ch0.axis_descrs
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
    ad0 = ch1.axis_descrs[0]
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
    ad0 = ch2.axis_descrs[0]
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
    assert meas.ecu_address_extension[0].extension == 1
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
    print(func.ref_characteristic[0].identifier)
    #assert func.ref_characteristic[0].identifier == ['FACTOR_1']


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

    assert g1.groupName == 'INJE'
    assert g1.groupLongIdentifier == 'Subsystem Injection'

    assert g2.groupName == 'Injec1'
    assert g2.groupLongIdentifier == 'Module filename Injec1'

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

