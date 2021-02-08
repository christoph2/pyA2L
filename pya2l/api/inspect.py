#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2020-2021 by Christoph Schueler <cpu12.gems@googlemail.com>

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

import collections
import weakref

from sqlalchemy import exists, not_

import pya2l.model as model
from pya2l.utils import align_as, ffs

DB_CACHE_SIZE = 4096  # Completly arbitrary, could be configurable.

ASAM_TO_NUMPY_TYPES = {
    "UBYTE": "uint8",
    "SBYTE": "int8",
    "BYTE": "int8",
    "UWORD": "uint16",
    "SWORD": "int16",
    "WORD": "int16",
    "ULONG": "uint32",
    "SLONG": "int32",
    "LONG": "int32",
    "A_UINT64": "uint64",
    "A_INT64": "int64",
    "FLOAT32_IEEE": "float32",
    "FLOAT64_IEEE": "float64",
}

ASAM_TYPE_SIZES = {
    "BYTE": 1,
    "UBYTE": 1,
    "SBYTE": 1,
    "WORD": 2,
    "UWORD": 2,
    "SWORD": 2,
    "LONG": 4,
    "ULONG": 4,
    "SLONG": 4,
    "A_UINT64": 8,
    "A_INT64": 8,
    "FLOAT32_IEEE": 4,
    "FLOAT64_IEEE": 8,
}

NATURAL_ALIGNMENTS = {
    "BYTE": 1,
    "WORD": 2,
    "DWORD": 4,
    "QWORD": 8,
    "FLOAT32": 4,
    "FLOAT64": 8,
}

ASAM_ALIGNMENT_TYPES = {
    "BYTE": "BYTE",
    "UBYTE": "BYTE",
    "SBYTE": "BYTE",
    "WORD": "WORD",
    "UWORD": "WORD",
    "SWORD": "WORD",
    "LONG": "DWORD",
    "ULONG": "DWORD",
    "SLONG": "DWORD",
    "A_UINT64": "QWORD",
    "A_INT64": "QWORD",
    "FLOAT32_IEEE": "FLOAT32",
    "FLOAT64_IEEE": "FLOAT64",
}

ASAM_TYPE_RANGES = {
    "BYTE":             (0, 255),
    "UBYTE":            (0, 255),
    "SBYTE":            (-128, 127),
    "WORD":             (0, 65535),
    "UWORD":            (0, 65535),
    "SWORD":            (-32768, 32767),
    "LONG":             (0, 4294967295),
    "ULONG":            (0, 4294967295),
    "SLONG":            (-2147483648, 2147483647),
    "A_UINT64":         (0, 18446744073709551615),
    "A_INT64":          (-9223372036854775808, 9223372036854775807),
    "FLOAT32_IEEE":     (1.175494351e-38, 3.402823466e+38),
    "FLOAT64_IEEE":     (2.2250738585072014e-308, 1.7976931348623157e+308),
}


def asam_type_size(datatype: str):
    """"""
    return ASAM_TYPE_SIZES[datatype]


def asam_align_as(alignment: dict, datatype: str, offset: int):
    return align_as(offset, alignment[ASAM_ALIGNMENT_TYPES[datatype]])


def all_axes_names():
    """"""
    return list("x y z 4 5".split())


def get_module(session, module_name: str = None):
    """"""
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


def fnc_np_shape(matrixDim):
    """Convert `matrixDim` dict to tuple suitable as Numpy array `shape` argument."""
    if matrixDim is None:
        return None
    result = []
    for dim in ("x", "y", "z"):
        d = matrixDim[dim]
        if d is None or d <= 1:
            break
        else:
            result.append(d)
    return tuple(result) or None


def fnc_np_order(order):
    """"""


class CachedBase:
    """Base class for all user classes in this module, implementing a cache manager.

    Note
    ----
    To take advantage of caching, always use `get` method.

    Example
    -------
    meas = Measurement.get(session, "someMeasurement")  # This is the right way.

    meas = Measurement(session, "someMeasurement")      # Constructor directly called, no caching.
    """

    _cache = weakref.WeakValueDictionary()
    _strong_ref = collections.deque(maxlen=DB_CACHE_SIZE)

    @classmethod
    def get(cls, session, name: str = None, module_name: str = None):
        entry = (cls.__name__, name)
        if entry not in cls._cache:
            inst = cls(session, name, module_name)
            cls._cache[entry] = inst
            cls._strong_ref.append(inst)
        return cls._cache[entry]


class ModPar(CachedBase):
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

    __slots__ = (
        "modpar",
        "comment",
        "addrEpk",
        "cpu",
        "customer",
        "customerNo",
        "ecu",
        "ecuCalibrationOffset",
        "epk",
        "memoryLayouts",
        "memorySegments",
        "noOfInterfaces",
        "phoneNo",
        "supplier",
        "systemConstants",
        "user",
        "version",
    )

    def __init__(self, session, name=None, module_name: str = None):
        module = get_module(session, module_name)
        self.modpar = module.mod_par
        self.comment = self.modpar.comment
        self.addrEpk = [a.address for a in self.modpar.addr_epk]
        self.cpu = self.modpar.cpu_type.cPU if self.modpar.cpu_type else None
        self.customer = self.modpar.customer.customer if self.modpar.customer else None
        self.customerNo = (
            self.modpar.customer_no.number if self.modpar.customer_no else None
        )
        self.ecu = self.modpar.ecu.controlUnit if self.modpar.ecu else None
        self.ecuCalibrationOffset = (
            self.modpar.ecu_calibration_offset.offset
            if self.modpar.ecu_calibration_offset
            else None
        )
        self.epk = self.modpar.epk.identifier if self.modpar.epk else None
        self.memoryLayouts = self._dissect_memory_layouts(self.modpar.memory_layout)
        self.memorySegments = self._dissect_memory_segments(self.modpar.memory_segment)
        self.noOfInterfaces = (
            self.modpar.no_of_interfaces.num if self.modpar.no_of_interfaces else None
        )
        self.phoneNo = self.modpar.phone_no.telnum if self.modpar.phone_no else None
        self.supplier = (
            self.modpar.supplier.manufacturer if self.modpar.supplier else None
        )
        self.systemConstants = self._dissect_sysc(self.modpar.system_constant)
        self.user = self.modpar.user.userName if self.modpar.user else None
        self.version = (
            self.modpar.version.versionIdentifier if self.modpar.version else None
        )

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
        names = (
            self.comment,
            self.addrEpk,
            self.cpu or "",
            self.customer or "",
            self.customerNo or "",
            self.ecu or "",
            self.ecuCalibrationOffset or 0,
            self.epk or "",
            self.memoryLayouts,
            self.memorySegments,
            self.noOfInterfaces or 0,
            self.phoneNo or "",
            self.supplier or "",
            self.systemConstants,
            self.user or "",
            self.version or "",
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
}}""".format(
            *names
        )

    __repr__ = __str__


class ModCommon(CachedBase):
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

    __slots__ = (
        "modcommon",
        "comment",
        "alignment",
        "byteOrder",
        "dataSize",
        "deposit",
        "sRecLayout",
    )

    def __init__(self, session, name=None, module_name: str = None):
        module = get_module(session, module_name)
        self.modcommon = module.mod_common
        self.comment = self.modcommon.comment
        self.alignment = {
            "BYTE": self.modcommon.alignment_byte.alignmentBorder
            if self.modcommon.alignment_byte
            else NATURAL_ALIGNMENTS["BYTE"],
            "WORD": self.modcommon.alignment_word.alignmentBorder
            if self.modcommon.alignment_word
            else NATURAL_ALIGNMENTS["WORD"],
            "DWORD": self.modcommon.alignment_long.alignmentBorder
            if self.modcommon.alignment_long
            else NATURAL_ALIGNMENTS["DWORD"],
            "QWORD": self.modcommon.alignment_int64.alignmentBorder
            if self.modcommon.alignment_int64
            else NATURAL_ALIGNMENTS["QWORD"],
            "FLOAT32": self.modcommon.alignment_float32_ieee.alignmentBorder
            if self.modcommon.alignment_float32_ieee
            else NATURAL_ALIGNMENTS["FLOAT32"],
            "FLOAT64": self.modcommon.alignment_float64_ieee.alignmentBorder
            if self.modcommon.alignment_float64_ieee
            else NATURAL_ALIGNMENTS["FLOAT64"],
        }
        self.byteOrder = (
            self.modcommon.byte_order.byteOrder if self.modcommon.byte_order else None
        )
        self.dataSize = (
            self.modcommon.data_size.size if self.modcommon.data_size else None
        )
        self.deposit = self.modcommon.deposit.mode if self.modcommon.deposit else None
        self.sRecLayout = (
            self.modcommon.s_rec_layout.name if self.modcommon.s_rec_layout else None
        )

    def __str__(self):
        names = (
            self.comment,
            self.alignment,
            self.byteOrder,
            self.dataSize or "",
            self.deposit or "",
            self.sRecLayout or "",
        )
        return """
ModCommon {{
    comment     = "{}";
    alignment   = {};
    byteOrder   = {};
    dataSize    = "{}";
    deposit     = "{}";
    sRecLayout  = "{}";
}}""".format(
            *names
        )

    __repr__ = __str__


class AxisDescr(CachedBase):
    """"""

    __slots__ = (
        "attribute",
        "inputQuantity",
        "_conversionRef",
        "compuMethod",
        "maxAxisPoints",
        "lowerLimit",
        "upperLimit",
        "byteOrder",
        "annotations",
        "axisPtsRef",
        "curveAxisRef",
        "deposit",
        "extendedLimits",
        "fixAxisPar",
        "fixAxisParDist",
        "fixAxisParList",
        "format",
        "maxGrad",
        "monotony",
        "physUnit",
        "readOnly",
        "stepSize",
    )

    def __init__(self, session, axis, module_name=None):
        self.attribute = axis.attribute
        self.axisPtsRef = (
            AxisPts.get(session, axis.axis_pts_ref.axisPoints)
            if axis.axis_pts_ref
            else None
        )
        if self.attribute in ("COM_AXIS", "RES_AXIS", "CURVE_AXIS"):
            pass
        else:
            pass
        self.inputQuantity = axis.inputQuantity
        self._conversionRef = axis.conversion
        self.maxAxisPoints = axis.maxAxisPoints
        self.lowerLimit = axis.lowerLimit
        self.upperLimit = axis.upperLimit

        self.compuMethod = (
            CompuMethod.get(session, self._conversionRef)
            if self._conversionRef != "NO_COMPU_METHOD"
            else "NO_COMPU_METHOD"
        )
        self.annotations = _annotations(session, axis.annotation)
        self.byteOrder = axis.byte_order.byteOrder if axis.byte_order else None
        self.curveAxisRef = (
            Characteristic.get(session, axis.curve_axis_ref.curveAxis)
            if axis.curve_axis_ref
            else None
        )
        self.deposit = axis.deposit.mode if axis.deposit else None
        self.extendedLimits = self._dissect_extended_limits(axis.extended_limits)
        self.fixAxisPar = self._dissect_fix_axis_par(axis.fix_axis_par)
        self.fixAxisParDist = self._dissect_fix_axis_par_dist(axis.fix_axis_par_dist)
        self.fixAxisParList = (
            axis.fix_axis_par_list.axisPts_Value if axis.fix_axis_par_list else []
        )
        self.format = axis.format.formatString if axis.format else None
        self.maxGrad = axis.max_grad.maxGradient if axis.max_grad else None
        self.monotony = axis.monotony.monotony if axis.monotony else None
        self.physUnit = axis.phys_unit.unit if axis.phys_unit else None
        self.readOnly = axis.read_only
        self.stepSize = axis.step_size.stepSize if axis.step_size else None

    @staticmethod
    def _dissect_extended_limits(limits):
        if limits is not None:
            result = {}
            result["lowerLimit"] = limits.lowerLimit
            result["upperLimit"] = limits.upperLimit
        else:
            result = None
        return result

    @staticmethod
    def _dissect_fix_axis_par(axis):
        if axis is not None:
            result = {}
            result["offset"] = axis.offset
            result["shift"] = axis.shift
            result["numberapo"] = axis.numberapo
        else:
            result = None
        return result

    @staticmethod
    def _dissect_fix_axis_par_dist(axis):
        if axis is not None:
            result = {}
            result["offset"] = axis.offset
            result["distance"] = axis.distance
            result["numberapo"] = axis.numberapo
        else:
            result = None
        return result

    def __str__(self):
        names = (
            self.attribute,
            self.inputQuantity,
            self.compuMethod,
            self.maxAxisPoints,
            self.lowerLimit,
            self.upperLimit,
            self.annotations,
            self.byteOrder,
            self.axisPtsRef,
            self.curveAxisRef,
            self.deposit,
            self.extendedLimits,
            self.fixAxisPar,
            self.fixAxisParDist,
            self.fixAxisParList,
            self.format,
            self.maxGrad,
            self.monotony or "",
            self.physUnit or "",
            self.readOnly,
            self.stepSize,
        )
        return """
AxisDescr {{
    attribute       = "{}";
    inputQuantity   = "{}";
    compuMethod     = {};
    maxAxisPoints   = {};
    lowerLimit      = {};
    upperLimit      = {};
    annotations     = {};
    byteOrder       = {};
    axisPtsRef      = {};
    curveAxisRef    = {};
    deposit         = "{}";
    extendedLimits  = {};
    fixAxisPar      = {};
    fixAxisParDist  = {};
    fixAxisParList  = {};
    format          = "{}";
    maxGrad         = {};
    monotony        = "{}";
    physUnit        = "{}";
    readOnly        = {};
    stepSize        = {};

}}""".format(
            *names
        )

    __repr__ = __str__


class Characteristic(CachedBase):
    """Convenient access (read-only) to CHARACTERISTIC objects.

    Parameters
    ----------
    session: Sqlite3 session object

    name: str
        name of one existing CHARACTERISTIC object.

    Attributes
    ----------
    characteristic:
        Raw Sqlite3 database object.

    name: str
        name of the Characteristic (s. Parameters...)

    longIdentifier: str
        comment, description.

    """

    __slots__ = (
        "characteristic",
        "name",
        "longIdentifier",
        "type",
        "address",
        "deposit",
        "maxDiff",
        "_conversionRef",
        "lowerLimit",
        "upperLimit",
        "annotations",
        "axisDescriptions",
        "bitMask",
        "byteOrder",
        "compuMethod",
        "calibrationAccess",
        "comparisonQuantity",
        "dependentCharacteristic",
        "discrete",
        "displayIdentifier",
        "ecuAddressExtension",
        "extendedLimits",
        "format",
        "functionList",
        "guardRails",
        "mapList",
        "matrixDim",
        "maxRefresh",
        "number",
        "physUnit",
        "readOnly",
        "refMemorySegment",
        "stepSize",
        "symbolLink",
        "virtualCharacteristic",
        "fnc_np_shape",
        "_record_layout_components",
    )

    def __init__(self, session, name: str, module_name: str = None):
        self.characteristic = (
            session.query(model.Characteristic)
            .filter(model.Characteristic.name == name)
            .first()
        )
        self.name = name
        self.longIdentifier = self.characteristic.longIdentifier
        self.type = self.characteristic.type
        self.address = self.characteristic.address
        self.deposit = RecordLayout(
            session, self.characteristic.deposit, module_name
        )
        self.maxDiff = self.characteristic.maxDiff
        self._conversionRef = self.characteristic.conversion
        self.compuMethod = (
            CompuMethod.get(session, self._conversionRef)
            if self._conversionRef != "NO_COMPU_METHOD"
            else "NO_COMPU_METHOD"
        )
        self.lowerLimit = self.characteristic.lowerLimit
        self.upperLimit = self.characteristic.upperLimit
        self.annotations = _annotations(session, self.characteristic.annotation)
        self.bitMask = (
            self.characteristic.bit_mask.mask if self.characteristic.bit_mask else None
        )
        self.byteOrder = (
            self.characteristic.byte_order.byteOrder
            if self.characteristic.byte_order
            else None
        )
        self.axisDescriptions = [
            AxisDescr.get(session, a) for a in self.characteristic.axis_descr
        ]
        self.calibrationAccess = self.characteristic.calibration_access
        self.comparisonQuantity = self.characteristic.comparison_quantity
        self.dependentCharacteristic = (
            self.characteristic.dependent_characteristic.formula
            if self.characteristic.dependent_characteristic
            else None
        )
        self.discrete = self.characteristic.discrete
        self.displayIdentifier = (
            self.characteristic.display_identifier.display_name
            if self.characteristic.display_identifier
            else None
        )
        self.ecuAddressExtension = (
            self.characteristic.ecu_address_extension.extension
            if self.characteristic.ecu_address_extension
            else 0
        )
        self.extendedLimits = self._dissect_extended_limits(
            self.characteristic.extended_limits
        )
        self.format = (
            self.characteristic.format.formatString
            if self.characteristic.format
            else None
        )
        self.functionList = (
            [f.name for f in self.characteristic.function_list]
            if self.characteristic.function_list
            else []
        )
        self.guardRails = self.characteristic.guard_rails
        self.mapList = (
            [f.name for f in self.characteristic.map_list]
            if self.characteristic.map_list
            else []
        )
        self.matrixDim = self._dissect_matrix_dim(self.characteristic.matrix_dim)
        self.maxRefresh = self._dissect_max_refresh(self.characteristic.max_refresh)
        self.number = (
            self.characteristic.number.number if self.characteristic.number else None
        )
        self.physUnit = self.characteristic.phys_unit
        self.readOnly = self.characteristic.read_only
        self.refMemorySegment = self.characteristic.ref_memory_segment
        self.stepSize = self.characteristic.step_size
        self.symbolLink = self._dissect_symbol_link(self.characteristic.symbol_link)
        self.virtualCharacteristic = (
            self.characteristic.virtual_characteristic.formula
            if self.characteristic.virtual_characteristic
            else []
        )
        self.fnc_np_shape = fnc_np_shape(self.matrixDim) or (
            None if self.number is None else (self.number,)
        )
        self._set_components()

    def _set_components(self):
        ITEMS = (
            "axisPts",
            "axisRescale",
            "distOp",
            "fncValues",
            "identification",
            "noAxisPts",
            "noRescale",
            "offset",
            "reserved",
            "ripAddr",
            "srcAddr",
            "shiftOp",
            "reserved",
        )

        items = {name: getattr(self.deposit, name) for name in ITEMS}
        self._record_layout_components = RecordLayoutComponents(
            self, items, self.deposit.alignment
        )
        self._record_layout_components.calculate_offsets_and_sizes(
            self.fnc_allocated_memory
        )

    def axisDescription(self, axis):
        MAP = {
            "x": 0,
            "y": 1,
            "z": 2,
            "4": 3,
            "5": 4,
        }
        descriptions = self.axisDescriptions
        if isinstance(axis, int):
            index = axis
        elif isinstance(axis, str):
            if axis not in MAP:
                raise ValueError("'{}' is an invalid axis name.".format(axis))
            index = MAP.get(axis)
        if index > len(descriptions) - 1:
            raise ValueError("axis value out of range.")
        return descriptions[index]

    @property
    def is_virtual(self):
        return self.virtualCharacteristic != []

    @property
    def num_axes(self):
        return len(self.axisDescriptions)

    @property
    def record_layout_components(self):
        return self._record_layout_components

    @property
    def fnc_asam_dtype(self):
        if self.deposit is None:
            return None
        else:
            return self.deposit.fnc_asam_dtype

    @property
    def fnc_np_dtype(self):
        if self.deposit is None:
            return None
        else:
            return self.deposit.fnc_np_dtype

    @property
    def fnc_np_order(self):
        if self.deposit is None:
            return None
        else:
            return self.deposit.fnc_np_order

    @property
    def fnc_element_size(self):
        """Size of a single function value."""
        if self.deposit is None:
            return None
        else:
            return self.deposit.fnc_element_size

    @property
    def fnc_allocated_memory(self):
        """Statically allocated memory by function value(s)."""
        dim = self.dim
        element_size = self.fnc_element_size
        if self.type == "VALUE":
            return element_size  # Scalar Characteristic
        elif self.type == "ASCII":
            return dim["x"]  # Chars are always 8bit quantities.
        else:
            axes_names = all_axes_names()
            result = 1
            for axis in axes_names:
                value = dim[axis]
                if value is None:
                    break
                result *= value
            return result * element_size

    @property
    def axes_allocated_memory(self):
        """Statically allocated memory by axes."""
        if self.type in ("VALUE", "ASCII", "VAL_BLK"):
            return 0
        else:
            dim = self.dim
            axes_names = all_axes_names()
            result = 0
            for axis in axes_names:
                value = dim[axis]
                if value is None:
                    break
                axis_desc = self.axisDescription(axis)
                axis_pts = self.deposit.axisPts.get(axis)
                if axis_desc.attribute in (
                    "COM_AXIS",
                    "FIX_AXIS",
                    "RES_AXIS",
                    "CURVE_AXIS",
                ):
                    continue
                result += value * asam_type_size(axis_pts["datatype"])
            return result

    @property
    def total_allocated_memory(self):
        """Total amount of statically allocated memory by Characteristic."""
        return self.record_layout_components.sizeof

    @property
    def dim(self):
        """Statically allocated dimensions."""
        if self.type == "VALUE":
            return {}  # n/a
        result = {"x": None, "y": None, "z": None, "4": None, "5": None}
        if self.type == "ASCII":
            result["x"] = self._ascii_length
        elif self.type == "VAL_BLK":
            md = self.matrixDim
            result["x"] = md["x"]
            result["y"] = md["y"]
            result["z"] = md["z"]
        else:
            axes_names = all_axes_names()
            for desc in self.axisDescriptions:
                if axes_names == []:
                    break  # More than five axes means malformed Characteristic.
                axis_name = axes_names.pop(0)
                result[axis_name] = desc.maxAxisPoints
        return result

    @property
    def _ascii_length(self):
        l0 = self.number
        l1 = self.matrixDim
        if l1:
            return l1["x"]
        elif l0:
            return l0
        else:
            return None

    @staticmethod
    def _dissect_extended_limits(limits):
        if limits is not None:
            result = {}
            result["lowerLimit"] = limits.lowerLimit
            result["upperLimit"] = limits.upperLimit
        else:
            result = None
        return result

    @staticmethod
    def _dissect_matrix_dim(matrix):
        if matrix is not None:
            result = {}
            result["x"] = matrix.xDim if matrix.xDim > 1 else None
            result["y"] = matrix.yDim if matrix.yDim > 1 else None
            result["z"] = matrix.zDim if matrix.zDim > 1 else None
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

    def __str__(self):
        names = (
            self.name,
            self.longIdentifier,
            self.type,
            self.address,
            self.deposit,
            self.maxDiff,
            self.compuMethod,
            self.lowerLimit,
            self.upperLimit,
            self.annotations,
            self.axisDescriptions,
            self.bitMask,
            self.byteOrder,
            self.calibrationAccess,
            self.comparisonQuantity,
            self.dependentCharacteristic,
            self.discrete,
            self.displayIdentifier,
            self.ecuAddressExtension,
            self.extendedLimits,
            self.format,
            self.functionList,
            self.guardRails,
            self.mapList,
            self.matrixDim,
            self.maxRefresh,
            self.number,
            self.physUnit,
            self.readOnly,
            self.refMemorySegment,
            self.stepSize,
            self.symbolLink,
            self.virtualCharacteristic,
            self.fnc_np_shape,
        )
        return """
Characteristic {{
    name                    = "{}";
    longIdentifier          = "{}";
    type                    = "{}";
    address                 = 0x{:08x};
    deposit                 = {};
    maxDiff                 = {};
    compuMethod             = "{}";
    lowerLimit              = {};
    upperLimit              = {};
    annotations             = {};
    axisDescriptions        = {};
    bitMask                 = {};
    byteOrder               = "{}";
    calibrationAccess       = {};
    comparisonQuantity      = {};
    dependentCharacteristic = {};
    discrete                = {};
    displayIdentifier       = {};
    ecuAddressExtension     = {};
    extendedLimits          = {};
    format                  = {};
    functionList            = {};
    guardRails              = {};
    mapList                 = {};
    matrixDim               = {};
    maxRefresh              = {};
    number                  = {};
    physUnit                = {};
    readOnly                = {};
    refMemorySegment        = {};
    stepSize                = {};
    symbolLink              = {};
    virtualCharacteristic   = {};
}}""".format(
            *names
        )

    __repr__ = __str__


class AxisPts(CachedBase):
    """"""

    __slots__ = (
        "axis",
        "name",
        "longIdentifier",
        "address",
        "inputQuantity",
        "deposit",
        "maxDiff",
        "_conversionRef",
        "compuMethod",
        "maxAxisPoints",
        "lowerLimit",
        "upperLimit",
        "annotations",
        "byteOrder",
        "calibrationAccess",
        "deposit",
        "displayIdentifier",
        "ecuAddressExtension",
        "extendedLimits",
        "format",
        "functionList",
        "guardRails",
        "monotony",
        "physUnit",
        "readOnly",
        "refMemorySegment",
        "stepSize",
        "symbolLink",
        "depositAttr",
        "_record_layout_components",
    )

    def __init__(self, session, name: str, module_name: str = None):
        self.axis = (
            session.query(model.AxisPts).filter(model.AxisPts.name == name).first()
        )
        self.name = name
        self.longIdentifier = self.axis.longIdentifier
        self.address = self.axis.address
        self.inputQuantity = self.axis.inputQuantity  # REF: Measurement
        self.depositAttr = RecordLayout(session, self.axis.depositAttr)
        self.deposit = self.axis.deposit.mode if self.axis.deposit else None
        self.maxDiff = self.axis.maxDiff
        self._conversionRef = self.axis.conversion
        self.compuMethod = (
            CompuMethod.get(session, self._conversionRef)
            if self._conversionRef != "NO_COMPU_METHOD"
            else "NO_COMPU_METHOD"
        )
        self.maxAxisPoints = self.axis.maxAxisPoints
        self.lowerLimit = self.axis.lowerLimit
        self.upperLimit = self.axis.upperLimit
        self.annotations = _annotations(session, self.axis.annotation)
        self.byteOrder = (
            self.axis.byte_order.byteOrder if self.axis.byte_order else None
        )
        self.calibrationAccess = self.axis.calibration_access
        self.deposit = self.axis.deposit.mode if self.axis.deposit else None
        self.displayIdentifier = (
            self.axis.display_identifier.display_name
            if self.axis.display_identifier
            else None
        )
        self.ecuAddressExtension = (
            self.axis.ecu_address_extension.extension
            if self.axis.ecu_address_extension
            else 0
        )
        self.extendedLimits = self._dissect_extended_limits(self.axis.extended_limits)
        self.format = self.axis.format.formatString if self.axis.format else None
        self.functionList = (
            [f.name for f in self.axis.function_list] if self.axis.function_list else []
        )
        self.guardRails = self.axis.guard_rails
        self.monotony = self.axis.monotony
        self.physUnit = self.axis.phys_unit
        self.readOnly = self.axis.read_only
        self.refMemorySegment = self.axis.ref_memory_segment
        self.stepSize = self.axis.step_size
        self.symbolLink = self._dissect_symbol_link(self.axis.symbol_link)
        self._set_components()

    def _set_components(self):
        ITEMS = (
            "axisPts",
            "axisRescale",
            "distOp",
            "fncValues",
            "identification",
            "noAxisPts",
            "noRescale",
            "offset",
            "reserved",
            "ripAddr",
            "srcAddr",
            "shiftOp",
        )

        items = {name: getattr(self.depositAttr, name) for name in ITEMS}
        self._record_layout_components = RecordLayoutComponents(
            self, items, self.depositAttr.alignment
        )
        self._record_layout_components.calculate_offsets_and_sizes(None)

    @property
    def record_layout_components(self):
        return self._record_layout_components

    @property
    def axis_allocated_memory(self):
        """Statically allocated memory by axis."""
        axis = self.record_layout_components.axes("x")
        return axis["memSize"]

    @property
    def total_allocated_memory(self):
        """Total amount of statically allocated memory by AxisPts."""
        return self.record_layout_components.sizeof

    @staticmethod
    def _dissect_extended_limits(limits):
        if limits is not None:
            result = {}
            result["lowerLimit"] = limits.lowerLimit
            result["upperLimit"] = limits.upperLimit
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

    def __str__(self):
        names = (
            self.name,
            self.longIdentifier,
            self.address,
            self.inputQuantity,
            self.maxDiff,
            self.compuMethod,
            self.maxAxisPoints,
            self.lowerLimit,
            self.upperLimit,
            self.annotations,
            self.byteOrder,
            self.calibrationAccess,
            self.deposit,
            self.depositAttr,
            self.ecuAddressExtension,
            self.extendedLimits,
            self.format,
            self.functionList,
            self.guardRails,
            self.monotony,
            self.physUnit,
            self.readOnly,
            self.refMemorySegment,
            self.stepSize,
            self.symbolLink,
            self.displayIdentifier,
        )
        return """
AxisPts {{
    name                = "{}";
    longIdentifier      = "{}";
    address             = {};
    inputQuantity       = {};
    maxDiff             = {};
    compuMethod         = {};
    maxAxisPoints       = {};
    lowerLimit          = {};
    upperLimit          = {};
    annotations         = {};
    byteOrder           = {};
    calibrationAccess   = {};
    deposit             = "{}";
    depositAttr         = {};
    ecuAddressExtension = {};
    extendedLimits      = {};
    format              = "{}";
    functionList        = {};
    guardRails          = {};
    monotony            = {};
    physUnit            = {};
    readOnly            = {};
    refMemorySegment    = {};
    stepSize            = {};
    symbolLink          = {};
    displayIdentifier   = "{}";
}}""".format(
            *names
        )

    __repr__ = __str__


class Measurement(CachedBase):
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

    ecuAddressExtension: int
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

    __slots__ = (
        "measurement",
        "name",
        "longIdentifier",
        "datatype",
        "_conversionRef",
        "resolution",
        "accuracy",
        "lowerLimit",
        "upperLimit",
        "annotations",
        "arraySize",
        "bitMask",
        "bitOperation",
        "byteOrder",
        "discrete",
        "displayIdentifier",
        "ecuAddress",
        "ecuAddressExtension",
        "errorMask",
        "format",
        "functionList",
        "layout",
        "matrixDim",
        "maxRefresh",
        "physUnit",
        "readWrite",
        "refMemorySegment",
        "symbolLink",
        "virtual",
        "compuMethod",
        "fnc_np_shape",
    )

    def __init__(self, session, name: str, module_name: str = None):
        self.measurement = (
            session.query(model.Measurement)
            .filter(model.Measurement.name == name)
            .first()
        )
        self.name = name
        self.longIdentifier = self.measurement.longIdentifier
        self.datatype = self.measurement.datatype
        self._conversionRef = self.measurement.conversion
        self.resolution = self.measurement.resolution
        self.accuracy = self.measurement.accuracy
        self.lowerLimit = self.measurement.lowerLimit
        self.upperLimit = self.measurement.upperLimit
        self.annotations = _annotations(session, self.measurement.annotation)
        self.arraySize = (
            self.measurement.array_size.number if self.measurement.array_size else None
        )
        self.bitMask = (
            self.measurement.bit_mask.mask if self.measurement.bit_mask else None
        )
        self.bitOperation = self._dissect_bit_operation(self, self.measurement.bit_operation)
        self.byteOrder = (
            self.measurement.byte_order.byteOrder
            if self.measurement.byte_order
            else None
        )
        self.discrete = self.measurement.discrete
        self.displayIdentifier = (
            self.measurement.display_identifier.display_name
            if self.measurement.display_identifier
            else None
        )
        self.ecuAddress = (
            self.measurement.ecu_address.address
            if self.measurement.ecu_address
            else None
        )
        self.ecuAddressExtension = (
            self.measurement.ecu_address_extension.extension
            if self.measurement.ecu_address_extension
            else 0
        )
        self.errorMask = (
            self.measurement.error_mask.mask if self.measurement.error_mask else None
        )
        self.format = (
            self.measurement.format.formatString if self.measurement.format else None
        )
        self.functionList = (
            self.measurement.function_list.name
            if self.measurement.function_list
            else []
        )
        self.layout = (
            self.measurement.layout.indexMode if self.measurement.layout else None
        )
        self.matrixDim = self._dissect_matrix_dim(self.measurement.matrix_dim)
        self.maxRefresh = self._dissect_max_refresh(self.measurement.max_refresh)
        self.physUnit = (
            self.measurement.phys_unit.unit if self.measurement.phys_unit else None
        )
        self.readWrite = False if self.measurement.read_write is None else True
        self.refMemorySegment = (
            self.measurement.ref_memory_segment.name
            if self.measurement.ref_memory_segment
            else None
        )
        self.symbolLink = self._dissect_symbol_link(self.measurement.symbol_link)
        self.virtual = (
            self.measurement.virtual.measuringChannel
            if self.measurement.virtual
            else []
        )
        self.compuMethod = (
            CompuMethod.get(session, self._conversionRef)
            if self._conversionRef != "NO_COMPU_METHOD"
            else "NO_COMPU_METHOD"
        )

        self.fnc_np_shape = fnc_np_shape(self.matrixDim)

    def __str__(self):
        names = (
            self.name,
            self.longIdentifier,
            self.datatype,
            self.resolution,
            self.accuracy,
            self.lowerLimit,
            self.upperLimit,
            self.annotations,
            self.arraySize,
            self.bitMask,
            self.bitOperation,
            self.byteOrder,
            self.discrete,
            self.displayIdentifier,
            self.ecuAddress or 0,
            self.ecuAddressExtension,
            self.errorMask,
            self.format,
            self.functionList,
            self.layout,
            self.matrixDim,
            self.maxRefresh,
            self.physUnit,
            self.refMemorySegment,
            self.readWrite,
            self.symbolLink,
            self.virtual,
            self.compuMethod,
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
    compuMethod = {};
}}""".format(
            *names
        )

    __repr__ = __str__

    @property
    def is_virtual(self):
        return self.virtual != []

    @staticmethod
    def _dissect_bit_operation(obj, bit_op):
        result = {}
        if bit_op is not None:
            if bit_op.left_shift is not None:
                result["direction"] = "L"
                result["amount"] = bit_op.left_shift.bitcount
            elif bit_op.right_shift is not None:
                result["direction"] = "R"
                result["amount"] = bit_op.right_shift.bitcount
            result["sign_extend"] = False if bit_op.sign_extend is None else True
        elif obj.bitMask is not None:
            result["direction"] = "R"
            result["amount"] = ffs(obj.bitMask)
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


class RecordLayout(CachedBase):
    """"""

    __slots__ = (
        "layout",
        "name",
        "alignment",
        "axisPts",
        "axisRescale",
        "distOp",
        "fixNoAxisPts",
        "fncValues",
        "identification",
        "noAxisPts",
        "noRescale",
        "offset",
        "reserved",
        "ripAddr",
        "srcAddr",
        "shiftOp",
        "staticRecordLayout",
        "_mod_common",
    )

    def __init__(self, session, name: str, module_name: str = None):
        self.layout = (
            session.query(model.RecordLayout)
            .filter(model.RecordLayout.name == name)
            .first()
        )
        self._mod_common = ModCommon.get(session)
        self.name = name
        self.alignment = {
            "BYTE": self.layout.alignment_byte.alignmentBorder
            if self.layout.alignment_byte
            else self._mod_common.alignment["BYTE"],
            "WORD": self.layout.alignment_word.alignmentBorder
            if self.layout.alignment_word
            else self._mod_common.alignment["WORD"],
            "DWORD": self.layout.alignment_long.alignmentBorder
            if self.layout.alignment_long
            else self._mod_common.alignment["DWORD"],
            "QWORD": self.layout.alignment_int64.alignmentBorder
            if self.layout.alignment_int64
            else self._mod_common.alignment["QWORD"],
            "FLOAT32": self.layout.alignment_float32_ieee.alignmentBorder
            if self.layout.alignment_float32_ieee
            else self._mod_common.alignment["FLOAT32"],
            "FLOAT64": self.layout.alignment_float64_ieee.alignmentBorder
            if self.layout.alignment_float64_ieee
            else self._mod_common.alignment["FLOAT64"],
        }
        self.axisPts = {
            "x": self._dissect_axis_pts(self.layout.axis_pts_x),
            "y": self._dissect_axis_pts(self.layout.axis_pts_y),
            "z": self._dissect_axis_pts(self.layout.axis_pts_z),
            "4": self._dissect_axis_pts(self.layout.axis_pts_4),
            "5": self._dissect_axis_pts(self.layout.axis_pts_5),
        }
        self.axisRescale = {
            "x": self._dissect_axis_rescale(self.layout.axis_rescale_x),
            "y": self._dissect_axis_rescale(self.layout.axis_rescale_y),
            "z": self._dissect_axis_rescale(self.layout.axis_rescale_z),
            "4": self._dissect_axis_rescale(self.layout.axis_rescale_4),
            "5": self._dissect_axis_rescale(self.layout.axis_rescale_5),
        }
        self.distOp = {
            "x": self._dissect_dist_op(self.layout.dist_op_x),
            "y": self._dissect_dist_op(self.layout.dist_op_y),
            "z": self._dissect_dist_op(self.layout.dist_op_z),
            "4": self._dissect_dist_op(self.layout.dist_op_4),
            "5": self._dissect_dist_op(self.layout.dist_op_5),
        }
        self.fixNoAxisPts = {
            "x": self._dissect_fix_no_axis_pts(self.layout.fix_no_axis_pts_x),
            "y": self._dissect_fix_no_axis_pts(self.layout.fix_no_axis_pts_y),
            "z": self._dissect_fix_no_axis_pts(self.layout.fix_no_axis_pts_z),
            "4": self._dissect_fix_no_axis_pts(self.layout.fix_no_axis_pts_4),
            "5": self._dissect_fix_no_axis_pts(self.layout.fix_no_axis_pts_5),
        }
        self.fncValues = self._dissect_fnc_values(self.layout.fnc_values)
        self.identification = self._dissect_identification(self.layout.identification)
        self.noAxisPts = {
            "x": self._dissect_no_axis_pts(self.layout.no_axis_pts_x),
            "y": self._dissect_no_axis_pts(self.layout.no_axis_pts_y),
            "z": self._dissect_no_axis_pts(self.layout.no_axis_pts_z),
            "4": self._dissect_no_axis_pts(self.layout.no_axis_pts_4),
            "5": self._dissect_no_axis_pts(self.layout.no_axis_pts_5),
        }
        self.noRescale = {
            "x": self._dissect_no_rescale(self.layout.no_rescale_x),
            "y": self._dissect_no_rescale(self.layout.no_rescale_y),
            "z": self._dissect_no_rescale(self.layout.no_rescale_z),
            "4": self._dissect_no_rescale(self.layout.no_rescale_4),
            "5": self._dissect_no_rescale(self.layout.no_rescale_5),
        }
        self.offset = {
            "x": self._dissect_offset(self.layout.offset_x),
            "y": self._dissect_offset(self.layout.offset_y),
            "z": self._dissect_offset(self.layout.offset_z),
            "4": self._dissect_offset(self.layout.offset_4),
            "5": self._dissect_offset(self.layout.offset_5),
        }
        self.reserved = (
            self._dissect_reserved(self.layout.reserved[0])
            if self.layout.reserved
            else {}
        )
        self.ripAddr = {
            "w": self._dissect_rip_addr(self.layout.rip_addr_w),
            "x": self._dissect_rip_addr(self.layout.rip_addr_x),
            "y": self._dissect_rip_addr(self.layout.rip_addr_y),
            "z": self._dissect_rip_addr(self.layout.rip_addr_z),
            "4": self._dissect_rip_addr(self.layout.rip_addr_4),
            "5": self._dissect_rip_addr(self.layout.rip_addr_5),
        }
        self.srcAddr = {
            "x": self._dissect_src_addr(self.layout.src_addr_x),
            "y": self._dissect_src_addr(self.layout.src_addr_y),
            "z": self._dissect_src_addr(self.layout.src_addr_z),
            "4": self._dissect_src_addr(self.layout.src_addr_4),
            "5": self._dissect_src_addr(self.layout.src_addr_5),
        }
        self.shiftOp = {
            "x": self._dissect_shift_op(self.layout.shift_op_x),
            "y": self._dissect_shift_op(self.layout.shift_op_y),
            "z": self._dissect_shift_op(self.layout.shift_op_z),
            "4": self._dissect_shift_op(self.layout.shift_op_4),
            "5": self._dissect_shift_op(self.layout.shift_op_5),
        }
        self.staticRecordLayout = (
            False if self.layout.static_record_layout is None else True
        )

    @staticmethod
    def _dissect_axis_pts(axis):
        if axis is not None:
            result = {}
            result["position"] = axis.position
            result["datatype"] = axis.datatype
            result["indexIncr"] = axis.indexIncr
            result["addressing"] = axis.addressing
        else:
            result = {}
        return result

    @staticmethod
    def _dissect_axis_rescale(axis):
        if axis is not None:
            result = {}
            result["position"] = axis.position
            result["datatype"] = axis.datatype
            result["maxNumberOfRescalePairs"] = axis.maxNumberOfRescalePairs
            result["indexIncr"] = axis.indexIncr
            result["addressing"] = axis.addressing
        else:
            result = {}
        return result

    @staticmethod
    def _dissect_dist_op(axis):
        if axis is not None:
            result = {}
            result["position"] = axis.position
            result["datatype"] = axis.datatype
        else:
            result = {}
        return result

    @staticmethod
    def _dissect_fix_no_axis_pts(axis):
        if axis is not None:
            result = axis.numberOfAxisPoints
        else:
            result = None
        return result

    @staticmethod
    def _dissect_fnc_values(fnc):
        if fnc is not None:
            result = {}
            result["position"] = fnc.position
            result["datatype"] = fnc.datatype
            result["indexMode"] = fnc.indexMode
            result["addresstype"] = fnc.addresstype
        else:
            result = {}
        return result

    @staticmethod
    def _dissect_identification(ident):
        if ident is not None:
            result = {}
            result["position"] = ident.position
            result["datatype"] = ident.datatype
        else:
            result = {}
        return result

    @staticmethod
    def _dissect_no_axis_pts(axis):
        if axis is not None:
            result = {}
            result["position"] = axis.position
            result["datatype"] = axis.datatype
        else:
            result = {}
        return result

    @staticmethod
    def _dissect_no_rescale(axis):
        if axis is not None:
            result = {}
            result["position"] = axis.position
            result["datatype"] = axis.datatype
        else:
            result = {}
        return result

    @staticmethod
    def _dissect_offset(offset):
        if offset is not None:
            result = {}
            result["position"] = offset.position
            result["datatype"] = offset.datatype
        else:
            result = {}
        return result

    @staticmethod
    def _dissect_reserved(reserved):
        if reserved is not None:
            result = {}
            result["position"] = reserved.position
            result["datatype"] = reserved.dataSize
        else:
            result = {}
        return result

    @staticmethod
    def _dissect_rip_addr(addr):
        if addr is not None:
            result = {}
            result["position"] = addr.position
            result["datatype"] = addr.datatype
        else:
            result = {}
        return result

    @staticmethod
    def _dissect_src_addr(addr):
        if addr is not None:
            result = {}
            result["position"] = addr.position
            result["datatype"] = addr.datatype
        else:
            result = {}
        return result

    @staticmethod
    def _dissect_shift_op(op):
        if op is not None:
            result = {}
            result["position"] = op.position
            result["datatype"] = op.datatype
        else:
            result = {}
        return result

    @property
    def fnc_asam_dtype(self):
        """Return `str` (e.g. `SLONG`)."""
        if self.fncValues is None:
            return None
        fnc_asam_dtype = self.fncValues.get("datatype")
        return None if fnc_asam_dtype is None else fnc_asam_dtype

    @property
    def fnc_np_dtype(self):
        """Return `str` (e.g. `int32`) suitable for Numpy."""
        if self.fncValues is None:
            return None
        fnc_asam_dtype = self.fncValues.get("datatype")
        if fnc_asam_dtype is None:
            return None
        fnc_np_dtype = ASAM_TO_NUMPY_TYPES.get(fnc_asam_dtype)
        return fnc_np_dtype

    @property
    def fnc_element_size(self):
        """Get the size of a single function value."""
        asam_dtype = self.fnc_asam_dtype
        return asam_type_size(asam_dtype)

    @property
    def fnc_np_order(self):
        """Return `str` suitable for Numpy.
        - "C": C order ==> row-major.
        - "F": Fortran order ==> column-major.
        """
        if self.fncValues is None:
            return None
        indexMode = self.fncValues.get("indexMode")
        if indexMode is None:
            return None
        if indexMode == "COLUMN_DIR":
            return "F"
        elif indexMode == "ROW_DIR":
            return "C"
        else:
            return None

    def __str__(self):
        names = (
            self.name,
            self.alignment,
            self.axisPts,
            self.axisRescale,
            self.distOp,
            self.fixNoAxisPts,
            self.fncValues,
            self.identification,
            self.noAxisPts,
            self.noRescale,
            self.offset,
            self.reserved,
            self.ripAddr,
            self.srcAddr,
            self.shiftOp,
            self.staticRecordLayout,
        )
        return """
RecordLayout {{
    name               = "{}";
    alignment          = {};
    axisPts            = {};
    axisRescale        = {};
    distOp             = {};
    fixNoAxisPts       = {};
    fncValues          = {};
    identification     = {};
    noAxisPts          = {};
    noRescale          = {};
    offset             = {};
    reserved           = {};
    ripAddr            = {};
    srcAddr            = {};
    shiftOp            = {};
    staticRecordLayout = {};
}}""".format(
            *names
        )

    __repr__ = __str__


class RecordLayoutComponents:
    """"""

    def __init__(self, parent, items: dict, alignment: dict):
        self.parent = parent
        self.alignment = alignment
        result = []
        positions = {}
        sizeof = 0
        self._axes_names = set()
        self._fncValues = {}
        self._identification = {}
        self._axes = {k: {} for k in all_axes_names()}
        self._sizeof = 0
        for item_name, item in items.items():
            entry = {}
            for k, v in item.items():
                if v:
                    entry[k] = v
            if entry:
                if item_name in (
                    "axisPts",
                    "axisRescale",
                    "distOp",
                    "noAxisPts",
                    "noRescale",
                    "offset",
                    "srcAddr",
                    "shiftOp",
                ):
                    s, p = self._get_details(entry, item_name, all_axes_names())
                    if item_name not in ("axisPts", "axisRescale"):
                        sizeof += s
                    positions.update(p)
                elif item_name == "ripAddr":
                    s, p = self._get_details(entry, item_name, all_axes_names() + ["w"])
                    sizeof += s
                    positions.update(p)
                elif item_name in ("fncValues", "identification", "reserved"):
                    # These components are not related to any axis.
                    pos = entry["position"]
                    positions[pos] = entry
                    entry["type"] = item_name
                    if item_name == "fncValues":
                        self._fncValues = entry
                    elif item_name == "identification":
                        self._identification = entry
                        sizeof += asam_type_size(entry["datatype"])
                    elif item_name == "reserved":
                        sizeof += asam_type_size(entry["datatype"])
                result.append(entry)
        self._components_by_pos = sorted(positions.items(), key=lambda k: k[0])
        if isinstance(parent, Characteristic):
            self._calculate_sizes_characteristic()
        elif isinstance(parent, AxisPts):
            self._calculate_sizes_axis_pts()

    def _calculate_sizes_characteristic(self):
        """"""
        total_mem_size = 0
        total_length = 0
        func_value_length = 1
        for axis in self.axes_names:
            axis_descr = self.parent.axisDescription(axis)
            maxAxisPoints = axis_descr.maxAxisPoints
            func_value_length *= maxAxisPoints
            total_length += maxAxisPoints
            axis_pts = self.axes(axis).get("axisPts")
            if axis_pts:
                mem_size = maxAxisPoints * asam_type_size(axis_pts["datatype"])
            else:
                if axis_descr.attribute == "FIX_AXIS":
                    mem_size = 0  # No memory occupied in case of fix axis.
                else:
                    # Should never be reached.
                    raise TypeError("No axis_pts {}".format(axis_descr.attribute))
            self.axes(axis)["maxAxisPoints"] = maxAxisPoints
            self.axes(axis)["memSize"] = mem_size
            if axis_pts:
                axis_pts["maxAxisPoints"] = maxAxisPoints
                axis_pts["memSize"] = mem_size
            total_mem_size += mem_size

    def _calculate_sizes_axis_pts(self):
        """"""
        x_axis = self.axes("x")
        maxAxisPoints = self.parent.maxAxisPoints
        axis_pts = x_axis.get("axisPts")  # Exactly one axis per AXIS_PTS.
        if not axis_pts:
            axis_res = x_axis.get("axisRescale")  # Rescale axis?
            if not axis_res:
                raise TypeError(
                    "Type of axis '{}' is neither standard nor rescale".format(
                        self.parent.name
                    )
                )
            # noRescale = x_axis.get("noRescale")
            element_size = (
                asam_type_size(axis_res.get("datatype")) * 2
            )  # In this case elements are pairs.
        else:
            element_size = asam_type_size(axis_pts.get("datatype"))
        mem_size = maxAxisPoints * element_size
        x_axis["maxAxisPoints"] = maxAxisPoints
        x_axis["memSize"] = mem_size
        if axis_pts:
            axis_pts["maxAxisPoints"] = maxAxisPoints
            axis_pts["memSize"] = mem_size

    def calculate_offsets_and_sizes(self, fnc_allocated_memory: int):
        """"""
        offset = 0
        # axis_pts = {n: self.axis_pts(n) for n in self.axes_names}
        for idx, (_, pos) in enumerate(self._components_by_pos):
            tp = pos["type"]
            if len(tp) == 2:
                tp, axis = tp
            else:
                axis = None
            datatype = pos["datatype"]
            if tp == "fncValues":
                size = fnc_allocated_memory
            elif tp in ("axisPts", "axisRescale"):
                size = self.axes(axis).get("memSize")
            else:
                size = asam_type_size(datatype)
            pos["offset"] = offset
            alignment = asam_align_as(self.alignment, datatype, offset)
            offset = alignment + size
        self._sizeof = offset

    def _get_details(self, entry, name, keys):
        positions = {}
        sizeof = 0  # TODO: sizeof obsolete now.
        for key in keys:
            dim_entry = entry.get(key)
            if dim_entry:
                self._axes[key][name] = dim_entry
                self._axes_names.add(key)
                pos = dim_entry["position"]
                sizeof += asam_type_size(dim_entry["datatype"])
                dim_entry["type"] = (name, key)
                positions[pos] = dim_entry
        return sizeof, positions

    def axes(self, axis=None):
        if axis is None:
            result = self._axes.items()
        else:
            result = self._axes[self._get_axis_name(axis)]
        return result

    def axis_pts(self, axis):
        return self._axes[self._get_axis_name(axis)].get("axisPts")

    def _get_axis_name(self, axis):
        """Get axis name"""
        AXES = ("x", "y", "z", "4", "5")
        if isinstance(axis, int):
            return AXES[axis]
        elif isinstance(axis, str):
            if not axis in AXES:
                raise ValueError("Parameter axis must be [{}].".format(' | '.join(AXES)))
            return axis
        else:
            raise TypeError("Parameter axis must be of type int or str.")


    @property
    def fncValues(self):
        return self._fncValues

    @property
    def identification(self):
        return self._identification

    @property
    def sizeof(self):
        """Size of record layout, respecting alignment."""
        return self._sizeof

    @property
    def axes_names(self):
        """Names of utilized axes.

        Returns
        -------
        `frozenset`
        """
        return frozenset(self._axes_names)

    @property
    def axes_count(self):
        """"""
        return len(self._axes_names)

    def __len__(self):
        return len(self._components_by_pos)

    def __getitem__(self, index):
        return self._components_by_pos[index]

    def __iter__(self):
        return iter(self._components_by_pos)

    def update_component_by_pos(self, pos, component):
        """Update / replace a record layout component."""
        tmp_dict = collections.OrderedDict(self._components_by_pos)
        if pos in tmp_dict:
            tmp_dict[pos] = component
            self._components_by_pos = list(tmp_dict.items())

    def __next__(self):
        for item in self._components_by_pos:
            yield item

    def __str__(self):
        result = ["{}(".format(self.__class__.__name__)]
        for key, value in self:
            result.append("    {} ==> {}".format(key, value))
        result.append(")")
        return "\n".join(result)

    __repr__ = __str__


class CompuMethod(CachedBase):
    """"""

    __slots__ = (
        "compu_method",
        "name",
        "longIdentifier",
        "conversionType",
        "format",
        "unit",
        "coeffs",
        "coeffs_linear",
        "formula",
        "tab",
        "tab_verb",
        "statusStringRef",
        "refUnit",
    )

    def __init__(self, session, name: str, module_name: str = None):
        self.compu_method = (
            session.query(model.CompuMethod)
            .filter(model.CompuMethod.name == name)
            .first()
        )
        if not self.compu_method:
            return
        self.name = name
        self.longIdentifier = self.compu_method.longIdentifier
        self.conversionType = self.compu_method.conversionType
        self.format = self.compu_method.format
        self.unit = self.compu_method.unit

        self.coeffs = {}
        self.coeffs_linear = {}
        self.formula = {}
        self.tab = {}
        self.tab_verb = {}
        self.statusStringRef = (
            self.compu_method.status_string_ref.conversionTable
            if self.compu_method.status_string_ref
            else None
        )
        self.refUnit = (
            self.compu_method.ref_unit.unit if self.compu_method.ref_unit else None
        )
        cm_type = self.conversionType
        if cm_type == "IDENTICAL":
            pass
        elif cm_type == "FORM":
            self.formula["formula_inv"] = (
                self.compu_method.formula.formula_inv.g_x
                if self.compu_method.formula.formula_inv
                else None
            )
            self.formula["formula"] = self.compu_method.formula.f_x
        elif cm_type == "LINEAR":
            self.coeffs_linear["a"] = self.compu_method.coeffs_linear.a
            self.coeffs_linear["b"] = self.compu_method.coeffs_linear.b
        elif cm_type == "RAT_FUNC":
            self.coeffs["a"] = self.compu_method.coeffs.a
            self.coeffs["b"] = self.compu_method.coeffs.b
            self.coeffs["c"] = self.compu_method.coeffs.c
            self.coeffs["d"] = self.compu_method.coeffs.d
            self.coeffs["e"] = self.compu_method.coeffs.e
            self.coeffs["f"] = self.compu_method.coeffs.f
        elif cm_type in ("TAB_INTP", "TAB_NOINTP"):
            cvt = (
                session.query(model.CompuTab)
                .filter(
                    model.CompuTab.name
                    == self.compu_method.compu_tab_ref.conversionTable
                )
                .first()
            )
            pairs = cvt.pairs
            self.tab["num_values"] = len(pairs)
            self.tab["interpolation"] = True if cm_type == "TAB_INTP" else False
            self.tab["default_value"] = (
                cvt.default_value_numeric.display_value
                if cvt.default_value_numeric
                else None
            )
            self.tab["in_values"] = [x.inVal for x in pairs]
            self.tab["out_values"] = [x.outVal for x in pairs]
        elif cm_type == "TAB_VERB":
            cvt = (
                session.query(model.CompuVtab)
                .filter(
                    model.CompuVtab.name
                    == self.compu_method.compu_tab_ref.conversionTable
                )
                .first()
            )
            if cvt:
                self.tab_verb["ranges"] = False
                pairs = cvt.pairs
                self.tab_verb["num_values"] = len(pairs)
                self.tab_verb["in_values"] = [x.inVal for x in pairs]
                self.tab_verb["text_values"] = [x.outVal for x in pairs]
                self.tab_verb["default_value"] = (
                    cvt.default_value.display_string if cvt.default_value else None
                )
            else:
                cvt = (
                    session.query(model.CompuVtabRange)
                    .filter(
                        model.CompuVtabRange.name
                        == self.compu_method.compu_tab_ref.conversionTable
                    )
                    .first()
                )
                if cvt:
                    self.tab_verb["ranges"] = True
                    triples = cvt.triples
                    self.tab_verb["num_values"] = len(triples)
                    self.tab_verb["lower_values"] = [x.inValMin for x in triples]
                    self.tab_verb["upper_values"] = [x.inValMax for x in triples]
                    self.tab_verb["text_values"] = [x.outVal for x in triples]
                    self.tab_verb["default_value"] = (
                        cvt.default_value.display_string if cvt.default_value else None
                    )

    def __str__(self):
        names = (
            self.name,
            self.longIdentifier,
            self.conversionType,
            self.format,
            self.unit,
            self.coeffs,
            self.coeffs_linear,
            self.formula,
            self.tab,
            self.tab_verb,
            self.statusStringRef,
            self.refUnit,
        )
        return """
CompuMethod {{
    name               = "{}";
    longIdentifier     = "{}";
    conversionType     = {};
    format             = "{}";
    unit               = "{}";
    coeffs             = {};
    coeffs_linear      = {};
    formula            = {};
    tab                = {};
    tab_verb           = {};
    statusStringRef    = {};
    refUnit            = {};
}}""".format(
            *names
        )

    __repr__ = __str__


def get_characteristic_or_axispts(session, name):
    found = session.query(exists().where(model.Characteristic.name == name)).scalar()
    if found:
        return Characteristic.get(session, name)
    else:
        found = session.query(exists().where(model.AxisPts.name == name)).scalar()
        if found:
            return AxisPts.get(session, name)
        else:
            return None


class Function(CachedBase):
    """

    Parameters
    ----------
    session: Sqlite3 session object

    Attributes
    ----------
    function:
        Raw Sqlite3 database object.

    name: str

    longIdentifier: str
        comment, description.
    """
    __slots__ = (
        "session",
        "function",
        "name",
        "longIdentifier",
        "functionVersion",
        "_inMeasurements",
        "_locMeasurements",
        "_outMeasurements",
        "_defCharacteristics",
        "_refCharacteristics",
        "_subFunctions",
    )
    def __init__(self, session, name = None, module_name: str = None):
        self.session = session
        self.function = (
            session.query(model.Function).filter(model.Function.name == name).first()
        )
        self.name = self.function.name
        self.longIdentifier = self.function.longIdentifier
        self.annotations = _annotations(session, self.function.annotation)
        self.functionVersion = self.function.function_version.versionIdentifier if self.function.function_version else None
        self._inMeasurements = None
        self._locMeasurements = None
        self._outMeasurements = None
        self._defCharacteristics = None
        self._refCharacteristics = None
        self._subFunctions = None

    @property
    def inMeasurements(self):
        if self._inMeasurements is None:
            self._inMeasurements = [Measurement.get(self.session, m) for m in self.function.in_measurement.identifier] if self.function.in_measurement else []
        return self._inMeasurements

    @property
    def locMeasurements(self):
        if self._locMeasurements is None:
            self._locMeasurements = [Measurement.get(self.session, m) for m in self.function.loc_measurement.identifier] if self.function.loc_measurement else []
        return self._locMeasurements

    @property
    def outMeasurements(self):
        if self._outMeasurements is None:
            self._outMeasurements = [Measurement.get(self.session, m) for m in self.function.out_measurement.identifier] if self.function.out_measurement else []
        return self._outMeasurements

    @property
    def defCharacteristics(self):
        if self._defCharacteristics is None:
            self._defCharacteristics = [get_characteristic_or_axispts(self.session, r) for r in self.function.def_characteristic.identifier] if self.function.def_characteristic else []
        return self._defCharacteristics

    @property
    def refCharacteristics(self):
        if self._refCharacteristics is None:
            self._refCharacteristics = [get_characteristic_or_axispts(self.session, r) for r in self.function.ref_characteristic.identifier] if self.function.ref_characteristic else []
        return self._refCharacteristics

    @property
    def subFunctions(self):
        if self._subFunctions is None:
            self._subFunctions = [Function.get(self.session, g) for g in self.function.sub_function.identifier] if self.function.sub_function else []
        return self._subFunctions

    @classmethod
    def get_root_functions(klass, session, ordered = False):
        """Fetch all toplevel Functions, i.e. Functions not referenced by other constructs.

        Parameters
        ----------
        session: Sqlite3 session object

        ordered: bool
            If True, order by function-name.

        """
        excluded_funcs = set()
        sfs = [f.sub_function for f in session.query(model.Function).all() if f.sub_function]
        for s in sfs:
            names = s.identifier
            if names:
                excluded_funcs.update(names)
        sgs = [g.function_list for g in session.query(model.Group).all() if g.function_list]
        for s in sgs:
            names = s.name
            if names:
                excluded_funcs.update(names)
        func_names = [f[0] for f in session.query(model.Function.name).\
            filter(not_(model.Function.name.in_(excluded_funcs))).all()]
        if ordered:
            funcs = sorted(func_names)
        result = []
        for func_name in func_names:
            result.append(Function.get(session, func_name))
        return result

    def __str__(self):
        names = (
            self.name,
            self.longIdentifier,
            self.annotations,
            self.functionVersion,
            self.inMeasurements,
            self.locMeasurements,
            self.outMeasurements,
            self.defCharacteristics,
            self.refCharacteristics,
            self.subFunctions,
        )
        return """
Function {{
    name                = "{}";
    longIdentifier      = "{}";
    annotations         = {};
    functionVersion     = {};
    inMeasurements      = {};
    locMeasurements     = {};
    outMeasurements     = {};
    defCharacteristics  = {};
    refCharacteristics  = {};
    subFunctions        = {};
";
}}""".format(
            *names
        )

    __repr__ = __str__


class Group(CachedBase):
    """

    Parameters
    ----------
    session: Sqlite3 session object

    Attributes
    ----------
    group:
        Raw Sqlite3 database object.

    name: str

    longIdentifier: str
        comment, description.

    annotations: list
        s. :func:`_annotations`

    root: bool
        Group is toplevel.

    characteristics:
        Adjustable objects in this group.

    measurements:
        Measurement objects in this group.

    functions:

    subgroups:
        Aggregated sub-groups.
    """

    __slots__ = (
        "session",
        "group",
        "name",
        "longIdentifier",
        "annotations",
        "root",
        "_characteristics",
        "_measurements",
        "_functions",
        "_subgroups",
    )

    def __init__(self, session, name = None, module_name: str = None):
        self.session = session
        self.group = (
            session.query(model.Group).filter(model.Group.groupName == name).first()
        )
        self.name = self.group.groupName
        self.longIdentifier = self.group.groupLongIdentifier
        self.annotations = _annotations(session, self.group.annotation)
        self.root = False if self.group.root is None else True
        self._characteristics = None
        self._measurements = None
        self._functions = None
        self._subgroups = None

    @property
    def characteristics(self):
        if self._characteristics is None:
            self._characteristics = [get_characteristic_or_axispts(self.session, r) for r in self.group.ref_characteristic.identifier] if self.group.ref_characteristic else []
        return self._characteristics

    @property
    def measurements(self):
        if self._measurements is None:
           self. _measurements = [Measurement.get(self.session, m) for m in self.group.ref_measurement.identifier] if self.group.ref_measurement else []
        return self. _measurements

    @property
    def functions(self):
        if self._functions is None:
            self._functions = [Function.get(self.session, f) for f in self.group.function_list.name] if self.group.function_list else []
        return self._functions

    @property
    def subgroups(self):
        if self._subgroups is None:
            self._subgroups = [Group.get(self.session, g) for g in self.group.sub_group.identifier] if self.group.sub_group else []
        return self._subgroups

    @classmethod
    def get_root_groups(klass, session, ordered = False):
        """Fetch all groups marked as root/toplevel.

        Parameters
        ----------
        session: Sqlite3 session object

        ordered: bool
            If True, order by group-name.

        """
        result = []
        query = session.query(model.Group).filter(model.Group.root != None)
        if ordered:
            query = query.order_by(model.Group.groupName)
        for group in query.all():
            result.append(Group.get(session, group.groupName))
        return result

    def __str__(self):
        names = (
            self.name,
            self.longIdentifier,
            self.annotations,
            self.root,
            self.characteristics,
            self.measurements,
            self.functions,
            self.subgroups,
        )
        return """
Group {{
    name            = "{}";
    longIdentifier  = "{}";
    annotations     = {};
    root            = {};
    characteristics = {};
    measurements    = {};
    functions       = {};
    subgroups       = {};
";
}}""".format(
            *names
        )

    __repr__ = __str__
