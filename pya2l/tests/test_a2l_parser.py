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
            ANNOTATION_LABEL "Luftsprungabh�ngigkeit"
            ANNOTATION_ORIGIN "Graf Zeppelin"
            /begin ANNOTATION_TEXT
                "Die luftklasseabh�ngigen Zeitkonstanten t_hinz\r\n"
                "& t_kunz k�nnen mit Hilfe von Luftspr�ngen ermittelt werden.\r\n"
                "Die Taupunktendezeiten in gro�en Flugh�hen sind stark schwankend"
            /end ANNOTATION_TEXT
        /end ANNOTATION
        /begin ANNOTATION
            ANNOTATION_LABEL "Taupunktendezeiten"
            /begin ANNOTATION_TEXT
                "Flugh�he Taupunktendezeit\r\n"
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
    assert an0.annotation_label.label == 'Luftsprungabh�ngigkeit'
    assert an0.annotation_origin.origin == 'Graf Zeppelin'
    assert an0.annotation_text.text == [
        'Die luftklasseabh�ngigen Zeitkonstanten t_hinz\r\n',
        '& t_kunz k�nnen mit Hilfe von Luftspr�ngen ermittelt werden.\r\n',
        'Die Taupunktendezeiten in gro�en Flugh�hen sind stark schwankend'
    ]
    assert an1.annotation_label.label == 'Taupunktendezeiten'
    assert an1.annotation_origin is None
    assert an1.annotation_text.text == [
        'Flugh�he Taupunktendezeit\r\n',
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
    /* control unit�s internal value of revolutions (INT) as follows: */
    /* PHYS = 1.25 * INT � 2.0 */
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
            "�C" /* physical unit */
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
            "�C" /* physical unit */
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
    assert cm[0].unit == '�C'
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
    assert cm[3].unit == '�C'
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
    assert ct.default_value_numeric.display_Value == 99.0
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
    assert cvr.default_value[0].display_String == 'Value_out_of_Range'
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


    assert ch1.name == 'SPD_NORM'
    assert ch1.longIdentifier == 'Speed normalizing function'
    assert ch1.type == 'CURVE'
    assert ch1.address == 33296
    assert ch1.deposit == 'SPD_DEP'
    assert ch1.maxDiff == 100.0
    assert ch1.conversion == 'R_NORM'
    assert ch1.lowerLimit == 0.0
    assert ch1.upperLimit == 6.0


    assert ch2.name == 'MAF_NORM'
    assert ch2.longIdentifier == 'Load normalizing function'
    assert ch2.type == 'CURVE'
    assert ch2.address == 33832
    assert ch2.deposit == 'LOAD_DEP'
    assert ch2.maxDiff == 100.0
    assert ch2.conversion == 'R_NORM'
    assert ch2.lowerLimit == 0.0
    assert ch2.upperLimit == 16.0
 #   print(ch2)
    """

"""