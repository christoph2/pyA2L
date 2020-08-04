#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__="""
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2020 by Christoph Schueler <cpu12.gems@googlemail.com>

   All Rights Reserved

  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License along
  with this program; if not, write to the Free Software Foundation, Inc.,
  51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

"""Classes for easy, convenient, read-only access to A2L databases.
"""

from pya2l import DB
import pya2l.model as model


def get_module(session, module_name: str = None):
    """

    """
    query = session.query(model.Module)
    if module_name:
        query = query.filter(model.Module.name == module_name)
    return query.first()


def _annotations(session, refs):
    """
    Parameters
    ----------
    session: Sqlite3 session object

    refs: list of raw database objects.

    Returns
    -------
    list of dicts with the following entries:
        - label: str
            Title of annotation

        - origin: str
            Creator of annotation

        - text: list of strings
            Actual text.

    """
    items = []
    for anno in refs:
        entry = {}
        entry["label"] = anno.annotation_label.label
        entry["origin"] = anno.annotation_origin.origin
        lines = []
        for line in anno.annotation_text._text:
            lines.append(line.text)
        entry["text"] = lines
        items.append(entry)
    return items


class ModPar:
    """

    Parameters
    ----------
    session: Sqlite3 session object

    Attributes
    ----------
    modpar:
        Raw Sqlite3 database object.

    comment: str
        comment, description.

    addrEpk: int
        Address of EPROM identifier.

    cpu: str
        CPU identifier.

    customer: str
        Customer name.

    customerNo: str
        Customer number.

    ecu: str
        Control unit.

    ecuCalibrationOffset: int
        Offset that has to be added to each address of a characteristic.

    epk: str
        EPROM identifier.

    memoryLayouts: list of dicts
        Layout of memory segments (deprecated, `memorySegments` should be used instead.

        - address: int
            Initial address of the program segment to be described.

        - offset_0': int

        - offset_1': int

        - offset_2': int

        - offset_3': int

        - offset_4': int
            Offsets for mirrored segments 0..4

        - prgType': ['PRG_CODE' | 'PRG_DATA' | 'PRG_RESERVED']

        - size': int
            Length of the program segment to be described.

    memorySegments: list of dicts
        Layout of memory segments

        - address: int

        - attribute: ['INTERN' | 'EXTERN']

        - longIdentifier: 'external RAM',
            comment, description

        - memoryType: ['EEPROM' | 'EPROM' | 'FLASH' | 'RAM' | 'ROM' | 'REGISTER']

        - name: str
            Identifier, reference to IF_DATA Blob is based on this 'name'.

        - offset_0: int

        - offset_1: int

        - offset_2: int

        - offset_3: int

        - offset_4: int
            Offsets for mirrored segments 0..4

        - prgType: ['CALIBRATION_VARIABLES' | 'CODE' | 'DATA' | 'EXCLUDE_FROM_FLASH' | 'OFFLINE_DATA' |
                    'RESERVED' | 'SERAM' | 'VARIABLES']
        - size: int
            Length of the segment.

    noOfInterfaces: int
        Number of interfaces.

    phoneNo: str
        Phone number of the calibration engineer responsible.

    supplier: str
        Manufacturer or supplier.

    systemConstants: list of dicts
        - key: str
            Name of constant.

        - value: int, float or str

    user: str
        User.

    version: str
        Version identifier.
    """

    __slots__ = ("modpar", "comment", "addrEpk", "cpu", "customer", "customerNo", "ecu", "ecuCalibrationOffset",
        "epk", "memoryLayouts", "memorySegments", "noOfInterfaces", "phoneNo", "supplier", "systemConstants",
        "user", "version",
    )

    def __init__(self, session, module_name: str = None):
        module = get_module(session, module_name)
        self.modpar = module.mod_par
        self.comment = self.modpar.comment
        self.addrEpk = [a.address for a in self.modpar.addr_epk]
        self.cpu = self.modpar.cpu_type.cPU if self.modpar.cpu_type else None
        self.customer = self.modpar.customer.customer if self.modpar.customer else None
        self.customerNo = self.modpar.customer_no.number if self.modpar.customer_no else None
        self.ecu = self.modpar.ecu.controlUnit if self.modpar.ecu else None
        self.ecuCalibrationOffset = self.modpar.ecu_calibration_offset.offset if self.modpar.ecu_calibration_offset else None
        self.epk =  self.modpar.epk.identifier if self.modpar.epk else None
        self.memoryLayouts = self._dissect_memory_layouts(self.modpar.memory_layout)
        self.memorySegments = self._dissect_memory_segments(self.modpar.memory_segment)
        self.noOfInterfaces = self.modpar.no_of_interfaces.num if self.modpar.no_of_interfaces else None
        self.phoneNo = self.modpar.phone_no.telnum if self.modpar.phone_no else None
        self.supplier = self.modpar.supplier.manufacturer if self.modpar.supplier else None
        self.systemConstants = self._dissect_sysc(self.modpar.system_constant)
        self.user = self.modpar.user.userName if self.modpar.user else None
        self.version = self.modpar.version.versionIdentifier if self.modpar.version else None

    @staticmethod
    def _dissect_sysc(constants):
        if constants is not None:
            result = {}
            for const in constants:
                try:
                    value = int(const.value)
                except ValueError:
                    try:
                        value = float(const.value)
                    except ValueError:
                        value = const.value
                result[const.name] = value
        else:
            result = None
        return result

    @staticmethod
    def _dissect_memory_layouts(layouts):
        if layouts is not None:
            result = []
            for layout in layouts:
                entry = {}
                entry["prgType"] = layout.prgType
                entry["address"] = layout.address
                entry["size"] = layout.size
                entry["offset_0"] = layout.offset_0
                entry["offset_1"] = layout.offset_1
                entry["offset_2"] = layout.offset_2
                entry["offset_3"] = layout.offset_3
                entry["offset_4"] = layout.offset_4
                result.append(entry)
        else:
            result = None
        return result

    @staticmethod
    def _dissect_memory_segments(segments):
        if segments is not None:
            result = []
            for segment in segments:
                entry = {}
                entry["name"] = segment.name
                entry["longIdentifier"] = segment.longIdentifier
                entry["prgType"] = segment.prgType
                entry["memoryType"] = segment.memoryType
                entry["attribute"] = segment.attribute
                entry["address"] = segment.address
                entry["size"] = segment.size
                entry["offset_0"] = segment.offset_0
                entry["offset_1"] = segment.offset_1
                entry["offset_2"] = segment.offset_2
                entry["offset_3"] = segment.offset_3
                entry["offset_4"] = segment.offset_4
                result.append(entry)
        else:
            result = None
        return result

    def __str__(self):
        names = (self.comment, self.addrEpk, self.cpu or "", self.customer or "", self.customerNo or "", self.ecu or "",
            self.ecuCalibrationOffset or 0, self.epk or "", self.memoryLayouts, self.memorySegments,
            self.noOfInterfaces or 0, self.phoneNo or "", self.supplier or "", self.systemConstants,
            self.user or "", self.version or ""
        )
        return """
ModPar {{
    comment                 = "{}";
    adrEpk                  = {};
    cpu                     = "{}":
    customer                = "{}";
    customerNo              = "{}";
    ecu                     = "{}";
    ecuCalibrationOffset    = {};
    epk                     = {};
    memoryLayouts           = {};
    memorySegments          = {};
    noOfInterfaces          = {};
    phoneNo                 = "{}";
    supplier                = "{}";
    systemConstants         = {};
    user                    = "{}";
    version                 = "{}";
}}""".format(*names)


class ModCommon:
    """

    Parameters
    ----------
    session: Sqlite3 session object

    Attributes
    ----------
    modcommon:
        Raw Sqlite3 database object.

    comment: str
        comment, description.

    alignment: dict
        keys:  ("BYTE", "WORD", "DWORD", "QWORD", "FLOAT32", "FLOAT64")
        values: int or None

    byteOrder: ["LITTLE_ENDIAN" | "BIG_ENDIAN" | "MSB_LAST" | "MSB_FIRST"] or None

    dataSize: int
        a.k.a word-size of the MCU.

    deposit: ["ASBOLUTE" | "DIFFERENCE"]


    sRecLayout: str
        Standard record layout.

    """

    __slots__ = ("modcommon", "comment", "alignment", "byteOrder", "dataSize", "deposit", "sRecLayout")

    def __init__(self, session, module_name: str = None):
        module = get_module(session, module_name)
        self.modcommon = module.mod_common
        #self.modcommon = session.query(model.ModCommon).first()
        self.comment = self.modcommon.comment
        self.alignment = {
            "BYTE": self.modcommon.alignment_byte.alignmentBorder if self.modcommon.alignment_byte else None,
            "WORD": self.modcommon.alignment_word.alignmentBorder if self.modcommon.alignment_word else None,
            "DWORD": self.modcommon.alignment_long.alignmentBorder if self.modcommon.alignment_long else None,
            "QWORD": self.modcommon.alignment_int64.alignmentBorder if self.modcommon.alignment_int64 else None,
            "FLOAT32": self.modcommon.alignment_float32_ieee.alignmentBorder if self.modcommon.alignment_float32_ieee else None,
            "FLOAT64": self.modcommon.alignment_float64_ieee.alignmentBorder if self.modcommon.alignment_float64_ieee else None,
        }
        self.byteOrder = self.modcommon.byte_order.byteOrder if self.modcommon.byte_order else None
        self.dataSize = self.modcommon.data_size.size if self.modcommon.data_size else None
        self.deposit = self.modcommon.deposit.mode if self.modcommon.deposit else None
        self.sRecLayout = self.modcommon.s_rec_layout.name if self.modcommon.s_rec_layout else None

    def __str__(self):
        names = (
            self.comment, self.alignment, self.byteOrder, self.dataSize or "", self.deposit or "", self.sRecLayout or ""
        )
        return """
ModCommon {{
    comment     = "{}";
    alignment   = {};
    byteOrder   = {};
    dataSize    = "{}";
    deposit     = "{}";
    sRecLayout  = "{}";
}}""".format(*names)


class Measurement:
    """Convenient access (read-only) to MEASUREMENT objects.

    Parameters
    ----------
    session: Sqlite3 session object

    name: str
        name of one existing MEASUREMENT object.

    Attributes
    ----------
    measurement:
        Raw Sqlite3 database object.

    name: str
        name of the Measurement (s. Parameters...)

    longIdentifier: str
        comment, description.

    datatype: ['UBYTE' | 'SBYTE' | 'UWORD' | 'SWORD' | 'ULONG' | 'SLONG' | 'A_UINT64' | 'A_INT64' |
        'FLOAT32_IEEE' | 'FLOAT64_IEEE']
        Type of the Measurement.

    resolution: int
        smallest possible change in bits

    accuracy: float
        possible variation from exact value in %

    lowerLimit: float
        plausible range of table values, lower limit

    upperLimit: float
        plausible range of table values, upper limit

    annotations: list
        s. :func:`_annotations`

    arraySize: int or None
        If not `None`, Measurement is an one dimensional array; higher order objects are using :attr:`matrixDim`.

    bitMask: int or None
        Mask out bits.

    bitOperation: dict or None
        - amount: int
            Number of shift positions
        - direction: ['L' | 'R']
        - sign_extend: bool

        perform `<<` and `>>` operations.

    byteOrder: ["LITTLE_ENDIAN" | "BIG_ENDIAN" | "MSB_LAST" | "MSB_FIRST"] or None

    discrete: bool
        If True, value should not be interpolated.

    displayIdentifier: str
        Can be used as a display name (alternative to the `name` attribute).

    ecuAddress: int or None
        Address of the measurement in the memory of the CU.

    ecuAddressExtension: int or None
        Additional address information, e.g. paging.

    errorMask: int or None
        Mask out bits  which indicate that the value is in error.

    format: str or None
        C printf like format string.

    functionList: list of strings.
        Used to specify a list of 'functions' to which this measurement object has been allocated.

    layout: ["ROW_DIR" | "COLUMN_DIR"] or None
        Describes the layout of a multi-dimensional measurement array.

    matrixDim: dict or None
        - x: int
        - y: int
        - z: int

        Shows the size and dimension of a multidimensional measurement.

    maxRefresh: dict or None
        - scalingUnit: int
            basic scaling unit (s. `Table Codes for scaling (CSE)`)

        - rate: int
            the maximum refresh rate of the concerning measurement object in the control unit.

    physUnit: str or None
        Physical unit for Measurement.

    readWrite: bool
        if True, mark this measurement object as writeable.

    refMemorySegment: str or None
        Reference to the memory segment which is needed if the address is not unique.

    symbolLink: dict or None
        - symbolName: str
            Name of the symbol within the corresponding linker map file.

        - offset: int
            Offset of the Symbol relative to the symbol's address in the linker map file.

    virtual: list of strings
        Referenced Measurements linked by a single conversion formula.


    compuMethod: dict

        - unit: str
            Physical unit for Measurement.

        - format: str
            C printf like format string.

        - longIdentifier: str
            comment, description.

        - type: str
            Discriminator field.

            - NO_COMPU_METHOD:

                no NO_COMPU_METHOD applied at all.

            - IDENTICAL:

                identity function.

            - FORM:
                - formula: str

                - formula_inv: str

                formula expression.

            - LINEAR:
                - a: float
                - b: float

                f(x) = ax + b

            - RAT_FUNC:
                - a: float
                - b: float
                - c: float
                - d: float
                - e: float
                - f: float

                f(x)=(axx + bx + c)/(dxx + ex + f)

            - TAB_INTP:
                - num_values: int
                - in_values: list of integers
                - out_values: list of integers
                - default_value: int

                table with interpolation.

            - TAB_NOINTP:
                - num_values: int
                - in_values: list of integers
                - out_values: list of integers
                - default_value: int

                table without interpolation.

            - TAB_VERB:
                - num_values: int
                - default_value: str
                - ranges: bool
                    - True
                        - lower_values: list of integers
                        - upper_values: list of integers
                        - text_values: list of strings
                    - False
                        - in_values: list of integers
                        - text_values: list of strings

                verbal conversion table.
    """

    __slots__ = ("measurement", "name", "longIdentifier", "datatype", "_conversionRef", "resolution",
        "accuracy", "lowerLimit", "upperLimit", "annotations", "arraySize", "bitMask", "bitOperation",
        "byteOrder", "discrete", "displayIdentifier", "ecuAddress", "ecuAddressExtension",
        "errorMask", "format", "functionList", "layout", "matrixDim", "maxRefresh", "physUnit",
        "readWrite", "refMemorySegment", "symbolLink", "virtual", "compuMethod"
        )

    def __init__(self, session, name: str, module_name: str = None):
        self.measurement = session.query(model.Measurement).filter(model.Measurement.name == name).first()
        self.name = name
        self.longIdentifier = self.measurement.longIdentifier
        self.datatype = self.measurement.datatype
        self._conversionRef = self.measurement.conversion
        self.resolution = self.measurement.resolution
        self.accuracy = self.measurement.accuracy
        self.lowerLimit = self.measurement.lowerLimit
        self.upperLimit = self.measurement.upperLimit
        self.annotations = _annotations(session, self.measurement.annotation)
        self.arraySize = self.measurement.array_size.number if self.measurement.array_size else None
        self.bitMask = self.measurement.bit_mask.mask if self.measurement.bit_mask else None
        self.bitOperation = self._dissect_bit_operation(self.measurement.bit_operation)
        self.byteOrder = self.measurement.byte_order.byteOrder if self.measurement.byte_order else None
        self.discrete = self.measurement.discrete
        self.displayIdentifier = self.measurement.display_identifier.display_name \
            if self.measurement.display_identifier else None
        self.ecuAddress = self.measurement.ecu_address.address if self.measurement.ecu_address else None
        self.ecuAddressExtension = self.measurement.ecu_address_extension.extension \
            if self.measurement.ecu_address_extension else None
        self.errorMask = self.measurement.error_mask.mask if self.measurement.error_mask else None
        self.format = self.measurement.format.formatString if self.measurement.format else None
        self.functionList = self.measurement.function_list.name if self.measurement.function_list else []
        self.layout = self.measurement.layout.indexMode if self.measurement.layout else None
        self.matrixDim = self._dissect_matrix_dim(self.measurement.matrix_dim)
        self.maxRefresh = self._dissect_max_refresh(self.measurement.max_refresh)
        self.physUnit = self.measurement.phys_unit.unit if self.measurement.phys_unit else None
        self.readWrite = False if self.measurement.read_write is None else True
        self.refMemorySegment = self.measurement.ref_memory_segment.name if self.measurement.ref_memory_segment else None
        self.symbolLink = self._dissect_symbol_link(self.measurement.symbol_link)
        self.virtual = self.measurement.virtual.measuringChannel if self.measurement.virtual else []
        self.compuMethod = _dissect_conversion(session, self._conversionRef)

    def __str__(self):
        names = (
            self.name, self.longIdentifier, self.datatype, self.resolution, self.accuracy, self.lowerLimit,
            self.upperLimit, self.annotations, self.arraySize, self.bitMask, self.bitOperation, self.byteOrder,
            self.discrete, self.displayIdentifier, self.ecuAddress, self.ecuAddressExtension, self.errorMask,
            self.format, self.functionList, self.layout, self.matrixDim, self.maxRefresh, self.physUnit,
            self.refMemorySegment, self.readWrite, self.symbolLink, self.virtual,
        )
        return """
Measurement {{
    name = {};
    longIdentifier = {};
    datatype  = {};
    resolution = {};
    accuracy = {};
    lowerLimit = {};
    upperLimit = {};
    annotations = {};
    arraySize = {};
    bitMask = {};
    bitOperation = {};
    byteOrder = {};
    discrete = {};
    displayIdentifier = {};
    ecuAddress = 0x{:08x};
    ecuAddressExtension = {};
    errorMask = {};
    format = {};
    functionList = {};
    layout = {};
    matrixDim = {};
    maxRefresh = {};
    physUnit = {};
    readWrite = {};
    refMemorySegment = {};
    symbolLink = {};
    virtual = {};
}}""".format(*names)

    @staticmethod
    def _dissect_bit_operation(bit_op):
        if bit_op is not None:
            result = {}
            if bit_op.left_shift is not None:
                result['direction'] = "L"
                result['amount'] = bit_op.left_shift.bitcount
            elif bit_op.right_shift is not None:
                result['direction'] = "R"
                result['amount'] = bit_op.right_shift.bitcount
            result['sign_extend'] = False if bit_op.sign_extend is None else True
        else:
            result = None
        return result

    @staticmethod
    def _dissect_matrix_dim(matrix_dim):
        if matrix_dim is not None:
            result = {}
            result["x"] = matrix_dim.xDim
            result["y"] = matrix_dim.yDim
            result["z"] = matrix_dim.zDim
        else:
            result = None
        return result

    @staticmethod
    def _dissect_max_refresh(max_ref):
        if max_ref is not None:
            result = {}
            result["scalingUnit"] = max_ref.scalingUnit
            result["rate"] = max_ref.rate
        else:
            result = None
        return result

    @staticmethod
    def _dissect_symbol_link(sym_link):
        if sym_link is not None:
            result = {}
            result["symbolName"] = sym_link.symbolName
            result["offset"] = sym_link.offset
        else:
            result = None
        return result


def _dissect_conversion(session, conversion):
    result = {}
    if conversion == "NO_COMPU_METHOD":
        result["type"] = "NO_COMPU_METHOD"
    else:
        cm = session.query(model.CompuMethod).filter(model.CompuMethod.name ==  conversion).first()
        cm_type = cm.conversionType
        result["type"] = cm_type
        result["unit"] = cm.unit
        result["format"] = cm.format
        result["longIdentifier"] = cm.longIdentifier
        if cm_type == "IDENTICAL":
            pass
        elif cm_type == "FORM":
            result["formula_inv"] = cm.formula.formula_inv.g_x if cm.formula.formula_inv else None
            result["formula"] = cm.formula.f_x
        elif cm_type == "LINEAR":
            result["a"] = cm.coeffs_linear.a
            result["b"] = cm.coeffs_linear.b
        elif cm_type == "RAT_FUNC":
            result["a"] = cm.coeffs.a
            result["b"] = cm.coeffs.b
            result["c"] = cm.coeffs.c
            result["d"] = cm.coeffs.d
            result["e"] = cm.coeffs.e
            result["f"] = cm.coeffs.f
        elif cm_type in ("TAB_INTP", "TAB_NOINTP"):
            cvt = session.query(model.CompuTab).filter(model.CompuTab.name == cm.compu_tab_ref.conversionTable).first()
            pairs = cvt.pairs
            result["num_values"] = len(pairs)
            result["interpolation"] = True if cm_type == "TAB_INTP" else False
            result["default_value"] = cvt.default_value_numeric.display_value if cvt.default_value_numeric else None
            result["in_values"] = [x.inVal for x in pairs]
            result["out_values"] = [x.outVal for x in pairs]
        elif cm_type == "TAB_VERB":
            cvt = session.query(model.CompuVtab).filter(model.CompuVtab.name == cm.compu_tab_ref.conversionTable).first()
            if cvt:
                result["ranges"] = False
                pairs = cvt.pairs
                result["num_values"] = len(pairs)
                result["in_values"] = [x.inVal for x in pairs]
                result["text_values"] = [x.outVal for x in pairs]
                result["default_value"] = cvt.default_value.display_string if cvt.default_value else None
            else:
                cvt = session.query(model.CompuVtabRange).filter(model.CompuVtabRange.name == \
                        cm.compu_tab_ref.conversionTable).first()
                if cvt:
                    result["ranges"] = True
                    triples = cvt.triples
                    result["num_values"] = len(triples)
                    result["lower_values"] = [x.inValMin for x in triples]
                    result["upper_values"] = [x.inValMax for x in triples]
                    result["text_values"] = [x.outVal for x in triples]
                    result["default_value"] = cvt.default_value.display_string if cvt.default_value else None
    return result
