#!/usr/bin/env python
"""Classes for easy, convenient, read-only access to A2L databases.
"""
__copyright__ = """
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2020-2025 by Christoph Schueler <cpu12.gems@googlemail.com>

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

import collections
import itertools
import weakref
from dataclasses import asdict, dataclass, field
from enum import IntEnum
from functools import cached_property, reduce
from operator import mul
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from sqlalchemy import exists, not_

import pya2l.model as model
from pya2l import exceptions
from pya2l.a2lparser_ext import process_sys_consts
from pya2l.functions import (
    Coeffs,
    CoeffsLinear,
    Formula,
    Identical,
    InterpolatedTable,
    Linear,
    LookupTable,
    LookupTableWithRanges,
    RatFunc,
)
from pya2l.utils import SingletonBase, align_as, enum_from_str, ffs


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
    "FLOAT16_IEEE": "float16",
    "FLOAT32_IEEE": "float32",
    "FLOAT64_IEEE": "float64",
}

ASAM_INTEGER_QUANTITIES = {
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
    "FLOAT16_IEEE": 2,
    "FLOAT32_IEEE": 4,
    "FLOAT64_IEEE": 8,
}

ASAM_TYPE_RANGES = {
    "BYTE": (0, 255),
    "UBYTE": (0, 255),
    "SBYTE": (-128, 127),
    "WORD": (0, 65535),
    "UWORD": (0, 65535),
    "SWORD": (-32768, 32767),
    "LONG": (0, 4294967295),
    "ULONG": (0, 4294967295),
    "SLONG": (-2147483648, 2147483647),
    "A_UINT64": (0, 18446744073709551615),
    "A_INT64": (-9223372036854775808, 9223372036854775807),
    "FLOAT16_IEEE": (-65504, 65504),
    "FLOAT32_IEEE": (1.175494351e-38, 3.402823466e38),
    "FLOAT64_IEEE": (2.2250738585072014e-308, 1.7976931348623157e308),
}


class PrgTypeLayout(IntEnum):
    PRG_CODE = 0
    PRG_DATA = 1
    PRG_RESERVED = 2


class PrgTypeSegment(IntEnum):
    CALIBRATION_VARIABLES = 0
    CODE = 1
    DATA = 2
    EXCLUDE_FROM_FLASH = 3
    OFFLINE_DATA = 4
    RESERVED = 5
    SERAM = 6
    VARIABLES = 7


class MemoryType(IntEnum):
    EEPROM = 0
    EPROM = 1
    FLASH = 2
    RAM = 3
    ROM = 4
    NOT_IN_ECU = 5


class SegmentAttributeType(IntEnum):
    INTERN = 0
    EXTERN = 1


##
## Dataclasses.
##


@dataclass
class Alignment:
    byte: int
    dword: int
    float16: int
    float32: int
    float64: int
    qword: int
    word: int

    TYPE_MAP = {
        "BYTE": "byte",
        "UBYTE": "byte",
        "SBYTE": "byte",
        "WORD": "word",
        "UWORD": "word",
        "SWORD": "word",
        "LONG": "dword",
        "ULONG": "dword",
        "SLONG": "dword",
        "A_UINT64": "qword",
        "A_INT64": "qword",
        "FLOAT16_IEEE": "float16",
        "FLOAT32_IEEE": "float32",
        "FLOAT64_IEEE": "float64",
    }

    def get(self, data_type: str) -> int:
        if data_type not in self.TYPE_MAP:
            raise ValueError(f"Invalid data type {data_type!r}.")
        attr = self.TYPE_MAP.get(data_type)
        return getattr(self, attr)

    def align(self, data_type: str, offset: int) -> int:
        return align_as(offset, self.get(data_type))


NATURAL_ALIGNMENTS = Alignment(byte=1, dword=4, float16=2, float32=4, float64=8, qword=8, word=2)


@dataclass
class RecordLayoutBase:
    position: Optional[int] = field(default=None)
    data_type: Optional[str] = field(default=None)
    axis: str = field(default="-")
    address: int = field(default=-1)

    def valid(self) -> bool:
        return self.position is not None and self.data_type is not None

    @cached_property
    def byte_size(self) -> int:
        return ASAM_TYPE_SIZES.get(self.data_type)


@dataclass
class RecordLayoutAxisPts(RecordLayoutBase):
    indexIncr: Optional[str] = field(default=None)
    addressing: Optional[str] = field(default=None)


@dataclass
class RecordLayoutAxisRescale(RecordLayoutBase):
    indexIncr: Optional[str] = field(default=None)
    maxNumberOfRescalePairs: Optional[int] = field(default=None)
    addressing: Optional[str] = field(default=None)


@dataclass
class RecordLayoutFncValues(RecordLayoutBase):
    indexMode: Optional[str] = field(default=None)
    addresstype: Optional[str] = field(default=None)


@dataclass
class RecordLayoutDistOp(RecordLayoutBase):
    pass


@dataclass
class RecordLayoutIdentification(RecordLayoutBase):
    pass


@dataclass
class RecordLayoutNoAxisPts(RecordLayoutBase):
    pass


@dataclass
class RecordLayoutNoRescale(RecordLayoutBase):
    pass


@dataclass
class RecordLayoutOffset(RecordLayoutBase):
    pass


@dataclass
class RecordLayoutReserved(RecordLayoutBase):
    pass


@dataclass
class RecordLayoutRipAddr(RecordLayoutBase):
    pass


@dataclass
class RecordLayoutSrcAddr(RecordLayoutBase):
    pass


@dataclass
class RecordLayoutShiftOp(RecordLayoutBase):
    pass


@dataclass
class RecordLayoutFixNoAxisPts:
    number: Optional[int] = field(default=None)
    position: int = field(default=0)
    axis: str = field(default="-")


RL_COMPONENT_NAMES = {
    RecordLayoutAxisPts: "axis_pts",
    RecordLayoutAxisRescale: "axis_rescale",
    RecordLayoutFncValues: "fnc_values",
    RecordLayoutDistOp: "dist_op",
    RecordLayoutIdentification: "identification",
    RecordLayoutNoAxisPts: "no_axis_pts",
    RecordLayoutNoRescale: "no_rescale",
    RecordLayoutOffset: "offset",
    RecordLayoutReserved: "reserved",
    RecordLayoutRipAddr: "rip_addr",
    RecordLayoutSrcAddr: "src_addr",
    RecordLayoutShiftOp: "shift_op",
    RecordLayoutFixNoAxisPts: "fix_no_axis_pts",
}


@dataclass
class FixAxisPar:
    offset: Optional[int] = field(default=None)
    shift: Optional[int] = field(default=None)
    numberapo: Optional[int] = field(default=None)

    def valid(self) -> bool:
        return self.offset is not None and self.shift is not None and self.numberapo is not None


@dataclass
class FixAxisParDist:
    offset: Optional[int] = field(default=None)
    distance: Optional[int] = field(default=None)
    numberapo: Optional[int] = field(default=None)

    def valid(self) -> bool:
        return self.offset is not None and self.distance is not None and self.numberapo is not None


@dataclass
class ExtendedLimits:
    lowerLimit: Optional[float] = field(default=None)
    upperLimit: Optional[float] = field(default=None)

    def valid(self) -> bool:
        return self.lowerLimit is not None and self.upperLimit is not None


@dataclass
class MatrixDim:
    x: Optional[int] = field(default=None)
    y: Optional[int] = field(default=None)
    z: Optional[int] = field(default=None)

    def valid(self) -> bool:
        return self.x is not None and self.y is not None and self.z is not None


@dataclass
class Annotation:
    label: Optional[str]
    origin: Optional[str]
    text: List[str]


@dataclass
class MemoryLayout:
    prgType: PrgTypeLayout
    address: int
    size: int
    offset_0: int
    offset_1: int
    offset_2: int
    offset_3: int
    offset_4: int


@dataclass
class MemorySegment:
    name: str
    longIdentifier: str
    prgType: PrgTypeSegment
    memoryType: MemoryType
    attribute: SegmentAttributeType
    address: int
    size: int
    offset_0: int
    offset_1: int
    offset_2: int
    offset_3: int
    offset_4: int


@dataclass
class DependentCharacteristic:
    formula: str
    characteristics: List[str]


@dataclass
class VirtualCharacteristic:
    formula: str
    characteristics: List[str]


@dataclass
class AxisInfo:
    data_type: str
    category: str
    maximum_points: int
    reversed_storage: bool
    addressing: str
    elements: Dict = field(default_factory=dict)


def asam_type_size(datatype: str) -> str:
    """"""
    return ASAM_TYPE_SIZES[datatype]


def all_axes_names() -> List[str]:
    """"""
    return list("x y z 4 5".split())


def get_module(session, module_name: Optional[str] = None) -> model.Module:
    """"""
    query = session.query(model.Module)
    if module_name:
        query = query.filter(model.Module.name == module_name)
    return query.first()


def _annotations(session, refs) -> List[Annotation]:
    """
    Parameters
    ----------
    session: Sqlite3 session object

    refs: list of raw database objects.

    Returns
    -------
    Annotation

    """
    items = []
    if refs is None:
        return []
    for anno in refs:
        label = anno.annotation_label.label if anno.annotation_label else None
        origin = anno.annotation_origin.origin if anno.annotation_origin else None
        lines = []
        if anno.annotation_text is not None:
            for line in anno.annotation_text._text:
                lines.append(line.text)
        entry = Annotation(label=label, origin=origin, text=lines)
        items.append(entry)
    return items


def fnc_np_shape(matrixDim: MatrixDim) -> tuple:
    """Convert `matrixDim` dict to tuple suitable as Numpy array `shape` argument."""
    if not matrixDim.valid():
        return ()
    result = []
    for n, dim in sorted(asdict(matrixDim).items(), key=lambda x: x[0]):
        if dim is None or dim < 1:
            continue
        else:
            result.append(dim)
    return tuple(result)


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
    def get(cls, session, name: str = None, module_name: str = None, *args):
        entry = (cls.__name__, name, args)
        if entry not in cls._cache:
            inst = cls(session, name, module_name, *args)
            cls._cache[entry] = inst
            cls._strong_ref.append(inst)
        return cls._cache[entry]


class NoCompuMethod(SingletonBase):
    """Sort of Null-Object for NO_COMPU_METHOD."""

    def __init__(self):
        self._name = None
        self._longIdentifier = None
        self._conversionType = "NO_COMPU_METHOD"
        self._format = None
        self._unit = None
        self._coeffs = []
        self._coeffs_linear = []
        self._formula = None
        self._tab = None
        self._tab_verb = None
        self._statusStringRef = None
        self._refUnit = None

    @property
    def name(self):
        return self._name

    @property
    def longIdentifier(self):
        return self._longIdentifier

    @property
    def conversionType(self):
        return self._conversionType

    @property
    def format(self):
        return self._format

    @property
    def unit(self):
        return self._unit

    @property
    def coeffs(self):
        return self._coeffs

    @property
    def coeffs_linear(self):
        return self._coeffs_linear

    @property
    def formula(self):
        return self._formula

    @property
    def tab(self):
        return self._tab

    @property
    def tab_verb(self):
        return self._tab_verb

    @property
    def statusStringRef(self):
        return self._statusStringRef

    @property
    def refUnit(self):
        return self._refUnit

    def int_to_physical(self, i):
        return i

    def physical_to_int(self, p):
        return p

    def __str__(self):
        return "NoCompuMethod()"


@dataclass
class CompuMethod(CachedBase):
    """"""

    compu_method: model.CompuMethod = field(repr=False)
    name: str
    longIdentifier: str
    conversionType: str
    format: Optional[str]
    unit: Optional[str]
    coeffs: Coeffs
    coeffs_linear: CoeffsLinear
    formula: Dict[str, float]
    tab: Dict
    tab_verb: Dict
    statusStringRef: Optional[str]
    refUnit: Optional[str]
    evaluator: Callable = field(repr=False, default=Identical())

    def __init__(self, session, name: str, module_name: str = None):
        self.compu_method = session.query(model.CompuMethod).filter(model.CompuMethod.name == name).first()
        if not self.compu_method:
            return
        self.name = name
        self.longIdentifier = self.compu_method.longIdentifier
        self.conversionType = self.compu_method.conversionType
        self.format = self.compu_method.format
        self.unit = self.compu_method.unit
        self.formula = {}
        self.tab = {}
        self.tab_verb = {}
        self.statusStringRef = self.compu_method.status_string_ref.conversionTable if self.compu_method.status_string_ref else None
        self.refUnit = self.compu_method.ref_unit.unit if self.compu_method.ref_unit else None
        cm_type = self.conversionType
        self.coeffs_linear = None
        self.coeffs = None
        if cm_type == "IDENTICAL":
            pass
        elif cm_type == "FORM":
            self.formula["formula_inv"] = (
                self.compu_method.formula.formula_inv.g_x if self.compu_method.formula.formula_inv else None
            )
            self.formula["formula"] = self.compu_method.formula.f_x
        elif cm_type == "LINEAR":
            self.coeffs_linear = CoeffsLinear(a=self.compu_method.coeffs_linear.a, b=self.compu_method.coeffs_linear.b)
        elif cm_type == "RAT_FUNC":
            self.coeffs = Coeffs(
                a=self.compu_method.coeffs.a,
                b=self.compu_method.coeffs.b,
                c=self.compu_method.coeffs.c,
                d=self.compu_method.coeffs.d,
                e=self.compu_method.coeffs.e,
                f=self.compu_method.coeffs.f,
            )
        elif cm_type in ("TAB_INTP", "TAB_NOINTP"):
            cvt = (
                session.query(model.CompuTab).filter(model.CompuTab.name == self.compu_method.compu_tab_ref.conversionTable).first()
            )
            pairs = cvt.pairs
            self.tab["num_values"] = len(pairs)
            self.tab["interpolation"] = True if cm_type == "TAB_INTP" else False
            self.tab["default_value"] = cvt.default_value_numeric.display_value if cvt.default_value_numeric else None
            self.tab["in_values"] = [x.inVal for x in pairs]
            self.tab["out_values"] = [x.outVal for x in pairs]
        elif cm_type == "TAB_VERB":
            cvt = (
                session.query(model.CompuVtab)
                .filter(model.CompuVtab.name == self.compu_method.compu_tab_ref.conversionTable)
                .first()
            )
            if cvt:
                self.tab_verb["ranges"] = False
                pairs = cvt.pairs
                self.tab_verb["num_values"] = len(pairs)
                self.tab_verb["in_values"] = [x.inVal for x in pairs]
                self.tab_verb["text_values"] = [x.outVal for x in pairs]
                self.tab_verb["default_value"] = cvt.default_value.display_string if cvt.default_value else None
            else:
                cvt = (
                    session.query(model.CompuVtabRange)
                    .filter(model.CompuVtabRange.name == self.compu_method.compu_tab_ref.conversionTable)
                    .first()
                )
                if cvt:
                    self.tab_verb["ranges"] = True
                    triples = cvt.triples
                    self.tab_verb["num_values"] = len(triples)
                    self.tab_verb["lower_values"] = [x.inValMin for x in triples]
                    self.tab_verb["upper_values"] = [x.inValMax for x in triples]
                    self.tab_verb["text_values"] = [x.outVal for x in triples]
                    self.tab_verb["default_value"] = cvt.default_value.display_string if cvt.default_value else None
        conversionType = cm_type
        if conversionType in ("IDENTICAL", "NO_COMPU_METHOD"):
            self.evaluator = Identical()
        elif conversionType == "FORM":
            formula = self.formula["formula"]
            formula_inv = self.formula["formula_inv"]
            mod_par = ModPar.get(session)
            system_constants = mod_par.systemConstants
            self.evaluator = Formula(formula, formula_inv, system_constants)
        elif conversionType == "LINEAR":
            coeffs = self.coeffs_linear
            if coeffs is None:
                raise exceptions.StructuralError("'LINEAR' requires coefficients (COEFFS_LINEAR).")
            self.evaluator = Linear(coeffs)
        elif conversionType == "RAT_FUNC":
            coeffs = self.coeffs
            if coeffs is None:
                raise exceptions.StructuralError("'RAT_FUNC' requires coefficients (COEFFS).")
            self.evaluator = RatFunc(coeffs)
        elif conversionType in ("TAB_INTP", "TAB_NOINTP"):
            klass = InterpolatedTable if self.tab["interpolation"] else LookupTable
            pairs = zip(self.tab["in_values"], self.tab["out_values"])
            default = self.tab["default_value"]
            self.evaluator = klass(pairs, default)
        elif conversionType == "TAB_VERB":
            default = self.tab_verb["default_value"]
            if self.tab_verb["ranges"]:
                triples = zip(
                    self.tab_verb["lower_values"],
                    self.tab_verb["upper_values"],
                    self.tab_verb["text_values"],
                )
                self.evaluator = LookupTableWithRanges(triples, default)
            else:
                pairs = zip(self.tab_verb["in_values"], self.tab_verb["text_values"])
                self.evaluator = LookupTable(pairs, default)
        else:
            raise ValueError(f"Unknown conversation type '{conversionType}'.")

    def int_to_physical(self, i):
        """Evaluate computation method INT ==> PHYS

        Parameters
        ----------
            x: int or float, scalar or array
        """
        return self.evaluator.int_to_physical(i)

    def physical_to_int(self, p):
        """Evaluate computation method PHYS ==> INT

        Parameters
        ----------
            p: int or float, scalar or array
        """
        return self.evaluator.physical_to_int(p)

    @classmethod
    def get(cls, session, name: str = None, module_name: str = None):
        if name == "NO_COMPU_METHOD":
            return NoCompuMethod()
        else:
            return super(cls, CompuMethod).get(session, name, module_name)


@dataclass
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

    modpar: model.ModPar = field(repr=False)
    comment: str
    addrEpk: List[int]
    cpu: Optional[str]
    customer: Optional[str]
    customerNo: Optional[str]
    ecu: Optional[str]
    ecuCalibrationOffset: Optional[int]
    epk: Optional[str]
    memoryLayouts: List[MemoryLayout]
    memorySegments: List[MemorySegment]
    noOfInterfaces: Optional[int]
    phoneNo: Optional[str]
    supplier: Optional[str]
    systemConstants: Dict[str, Union[str, float]]
    user: Optional[str]
    version: Optional[str]

    def __init__(self, session, name=None, module_name: str = None):
        module = get_module(session, module_name)
        self.modpar = module.mod_par
        self.comment = self.modpar.comment
        self.addrEpk = [a.address for a in self.modpar.addr_epk]
        self.cpu = self.modpar.cpu_type.cPU if self.modpar.cpu_type else None
        self.customer = self.modpar.customer.customer if self.modpar.customer else None
        self.customerNo = self.modpar.customer_no.number if self.modpar.customer_no else None
        self.ecu = self.modpar.ecu.controlUnit if self.modpar.ecu else None
        self.ecuCalibrationOffset = self.modpar.ecu_calibration_offset.offset if self.modpar.ecu_calibration_offset else None
        self.epk = self.modpar.epk.identifier if self.modpar.epk else None
        self.memoryLayouts = self._create_memory_layout(self.modpar.memory_layout)
        self.memorySegments = self._create_memory_segments(self.modpar.memory_segment)
        self.noOfInterfaces = self.modpar.no_of_interfaces.num if self.modpar.no_of_interfaces else None
        self.phoneNo = self.modpar.phone_no.telnum if self.modpar.phone_no else None
        self.supplier = self.modpar.supplier.manufacturer if self.modpar.supplier else None
        self.systemConstants = self._dissect_sysc(self.modpar.system_constant)
        self.user = self.modpar.user.userName if self.modpar.user else None
        self.version = self.modpar.version.versionIdentifier if self.modpar.version else None

    @staticmethod
    def exists(session, name: str = None, module_name: str = None) -> bool:  # TODO: Better move to base class...
        module = get_module(session, module_name)
        return module.mod_par is not None

    @staticmethod
    def _dissect_sysc(constants: list) -> Dict:
        if constants is not None:
            return process_sys_consts(
                list(
                    (
                        c.name,
                        c.value,
                    )
                    for c in constants
                )
            )
        return []

    @staticmethod
    def _create_memory_layout(layouts) -> List[MemoryLayout]:
        result = []
        if layouts is not None:
            for layout in layouts:
                entry = MemoryLayout(
                    enum_from_str(PrgTypeLayout, layout.prgType),
                    layout.address,
                    layout.size,
                    layout.offset_0,
                    layout.offset_1,
                    layout.offset_2,
                    layout.offset_3,
                    layout.offset_4,
                )
                result.append(entry)
        return result

    @staticmethod
    def _create_memory_segments(segments) -> List[MemorySegment]:
        result = []
        if segments is not None:
            for segment in segments:
                entry = MemorySegment(
                    segment.name,
                    segment.longIdentifier,
                    enum_from_str(PrgTypeSegment, segment.prgType),
                    enum_from_str(MemoryType, segment.memoryType),
                    enum_from_str(SegmentAttributeType, segment.attribute),
                    segment.address,
                    segment.size,
                    segment.offset_0,
                    segment.offset_1,
                    segment.offset_2,
                    segment.offset_3,
                    segment.offset_4,
                )
                result.append(entry)
        return result


class NoModCommon(SingletonBase):
    """Sort of Null-Object for non-existing MOD_COMMON."""

    def __init__(self):
        self._comment = None
        self._alignment = NATURAL_ALIGNMENTS
        self._byteOrder = "MSB_FIRST"
        self._dataSize = None
        self._deposit = None
        self._sRecLayout = None

    @property
    def comment(self):
        return self._comment

    @property
    def alignment(self):
        return self._alignment

    @property
    def byteOrder(self):
        return self._byteOrder

    @property
    def dataSize(self):
        return self._dataSize

    @property
    def deposit(self):
        return self._deposit

    @property
    def sRecLayout(self):
        return self._sRecLayout

    def __str__(self):
        return "NoModCommon()"

    __repr__ = __str__


@dataclass
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

    alignment: Alignment

    byteOrder: ["LITTLE_ENDIAN" | "BIG_ENDIAN" | "MSB_LAST" | "MSB_FIRST"] or None

    dataSize: int
        a.k.a word-size of the MCU.

    deposit: ["ASBOLUTE" | "DIFFERENCE"]


    sRecLayout: str
        Standard record layout.

    """

    modcommon: model.ModCommon = field(repr=False)
    comment: Optional[str]
    alignment: Alignment
    byteOrder: Optional[str]
    dataSize: Optional[int]
    deposit: str
    sRecLayout: Optional[str]

    def __init__(self, session, name=None, module_name: str = None):
        module = get_module(session, module_name)
        self.modcommon = module.mod_common
        self.comment = self.modcommon.comment
        self.alignment = Alignment(
            byte=self.modcommon.alignment_byte.alignmentBorder if self.modcommon.alignment_byte else NATURAL_ALIGNMENTS.byte,
            word=self.modcommon.alignment_word.alignmentBorder if self.modcommon.alignment_word else NATURAL_ALIGNMENTS.word,
            dword=self.modcommon.alignment_long.alignmentBorder if self.modcommon.alignment_long else NATURAL_ALIGNMENTS.dword,
            qword=self.modcommon.alignment_int64.alignmentBorder if self.modcommon.alignment_int64 else NATURAL_ALIGNMENTS.qword,
            float16=(
                self.modcommon.alignment_float16_ieee.alignmentBorder
                if self.modcommon.alignment_float16_ieee
                else NATURAL_ALIGNMENTS.float16
            ),
            float32=(
                self.modcommon.alignment_float32_ieee.alignmentBorder
                if self.modcommon.alignment_float32_ieee
                else NATURAL_ALIGNMENTS.float32
            ),
            float64=(
                self.modcommon.alignment_float64_ieee.alignmentBorder
                if self.modcommon.alignment_float64_ieee
                else NATURAL_ALIGNMENTS.float64
            ),
        )
        self.byteOrder = self.modcommon.byte_order.byteOrder if self.modcommon.byte_order else None
        self.dataSize = self.modcommon.data_size.size if self.modcommon.data_size else None
        self.deposit = self.modcommon.deposit.mode if self.modcommon.deposit else None
        self.sRecLayout = self.modcommon.s_rec_layout.name if self.modcommon.s_rec_layout else None

    @classmethod
    def get(cls, session, name: str = None, module_name: str = None):
        module = get_module(session, module_name)
        if module.mod_common is None:
            return NoModCommon()
        else:
            return super(cls, ModCommon).get(session, name, module_name)


@dataclass
class RecordLayout(CachedBase):
    """"""

    layout: model.RecordLayout = field(repr=False)
    _mod_common: ModCommon = field(repr=False)
    name: str
    axes: collections.defaultdict[dict]
    staticRecordLayout: bool
    alignment: Alignment
    fncValues: RecordLayoutFncValues
    identification: RecordLayoutIdentification
    reserved: List[RecordLayoutReserved]

    def __init__(self, session, name: str, module_name: str = None):
        self.layout = session.query(model.RecordLayout).filter(model.RecordLayout.name == name).first()
        if self.layout is None:
            raise RuntimeError(f"RECORD_LAYOUT '{name}' not found")
        self._mod_common = ModCommon.get(session)
        self.name = name
        self.alignment = Alignment(
            byte=self.layout.alignment_byte.alignmentBorder if self.layout.alignment_byte else self._mod_common.alignment.byte,
            word=self.layout.alignment_word.alignmentBorder if self.layout.alignment_word else self._mod_common.alignment.word,
            dword=self.layout.alignment_long.alignmentBorder if self.layout.alignment_long else self._mod_common.alignment.dword,
            qword=self.layout.alignment_int64.alignmentBorder if self.layout.alignment_int64 else self._mod_common.alignment.qword,
            float16=(
                self.layout.alignment_float16_ieee.alignmentBorder
                if self.layout.alignment_float16_ieee
                else self._mod_common.alignment.float16
            ),
            float32=(
                self.layout.alignment_float32_ieee.alignmentBorder
                if self.layout.alignment_float32_ieee
                else self._mod_common.alignment.float32
            ),
            float64=(
                self.layout.alignment_float64_ieee.alignmentBorder
                if self.layout.alignment_float64_ieee
                else self._mod_common.alignment.float64
            ),
        )

        AX_VARIABLES = (
            ("axis_pts", self.create_axis_pts),
            ("axis_rescale", self.create_axis_rescale),
            ("dist_op", self.create_dist_op),
            ("fix_no_axis_pts", self.create_fix_no_axis_pts),
            ("no_axis_pts", self.create_no_axis_pts),
            ("no_rescale", self.create_no_rescale),
            ("offset", self.create_offset),
            ("rip_addr", self.create_rip_addr),
            ("src_addr", self.create_src_addr),
            ("shift_op", self.create_shift_op),
        )
        self.axes = collections.defaultdict(dict)
        elements = []
        for axis in ("x", "y", "z", "4", "5"):
            for variable, factory in AX_VARIABLES:
                res = getattr(self.layout, f"{variable}_{axis}")
                if res is not None:
                    obj = factory(axis, res)
                    elements.append(obj)
                    self.axes[axis][variable] = obj
        self.fncValues = self.create_fnc_values("-", self.layout.fnc_values)
        self.identification = self.create_identification("-", self.layout.identification)
        self.reserved = self.create_reserved("-", self.layout.reserved)
        self.staticRecordLayout = False if self.layout.static_record_layout is None else True
        if self.fncValues.valid():
            elements.append(self.fncValues)
        if self.identification.valid():
            elements.append(self.identification)
        if self.reserved:
            elements.extend(self.reserved)
        self.elements = sorted(elements, key=lambda x: x.position)

    @staticmethod
    def create_axis_pts(axis_name, axis) -> RecordLayoutAxisPts:
        return RecordLayoutAxisPts(axis.position, axis.datatype, axis_name, -1, axis.indexIncr, axis.addressing)

    @staticmethod
    def create_axis_rescale(axis_name, axis) -> RecordLayoutAxisRescale:
        return RecordLayoutAxisRescale(
            axis.position, axis.datatype, axis_name, -1, axis.indexIncr, axis.maxNumberOfRescalePairs, axis.addressing
        )

    @staticmethod
    def create_dist_op(axis_name, axis) -> RecordLayoutDistOp:
        return RecordLayoutDistOp(axis.position, axis.datatype, axis_name, -1)

    @staticmethod
    def create_fix_no_axis_pts(axis_name, axis):  ## TODO
        if axis is not None:
            return RecordLayoutFixNoAxisPts(number=axis.numberOfAxisPoints, axis=axis_name)
        else:
            return RecordLayoutFixNoAxisPts()

    @staticmethod
    def create_fnc_values(axis_name, fnc) -> RecordLayoutFncValues:
        if fnc is not None:
            return RecordLayoutFncValues(fnc.position, fnc.datatype, axis_name, -1, fnc.indexMode, fnc.addresstype)
        else:
            return RecordLayoutFncValues()

    @staticmethod
    def create_identification(axis_name, ident) -> RecordLayoutIdentification:
        if ident is not None:
            return RecordLayoutIdentification(ident.position, ident.datatype, axis_name, -1)
        else:
            return RecordLayoutIdentification()

    @staticmethod
    def create_no_axis_pts(axis_name, axis) -> RecordLayoutNoAxisPts:
        return RecordLayoutNoAxisPts(axis.position, axis.datatype, axis_name, -1)

    @staticmethod
    def create_no_rescale(axis_name, axis) -> RecordLayoutNoRescale:
        return RecordLayoutNoRescale(axis.position, axis.datatype, axis_name, -1)

    @staticmethod
    def create_offset(axis_name, offset) -> RecordLayoutOffset:
        return RecordLayoutOffset(offset.position, offset.datatype, axis_name, -1)

    @staticmethod
    def create_reserved(axis_name, reserved) -> List[RecordLayoutReserved]:
        result = []
        if len(reserved) > 0:
            for r in reserved:
                result.append(RecordLayoutReserved(r.position, r.dataSize, axis_name, -1))
        return result

    @staticmethod
    def create_rip_addr(axis_name, addr) -> RecordLayoutRipAddr:
        return RecordLayoutRipAddr(addr.position, addr.datatype, axis_name, -1)

    @staticmethod
    def create_src_addr(axis_name, addr) -> RecordLayoutSrcAddr:
        return RecordLayoutSrcAddr(addr.position, addr.datatype)

    @staticmethod
    def create_shift_op(axis_name, op) -> RecordLayoutShiftOp:
        return RecordLayoutShiftOp(op.position, op.datatype, axis_name, -1)

    @property
    def fnc_asam_dtype(self):
        """Return `str` (e.g. `SLONG`)."""
        if self.fncValues is None:
            return None
        fnc_asam_dtype = self.fncValues.data_type
        return None if fnc_asam_dtype is None else fnc_asam_dtype

    @property
    def fnc_np_dtype(self):
        """Return `str` (e.g. `int32`) suitable for Numpy."""
        if self.fncValues is None:
            return None
        fnc_asam_dtype = self.fncValues.data_type
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
        indexMode = self.fncValues.indexMode
        if indexMode is None:
            return None
        if indexMode == "COLUMN_DIR":
            return "F"
        elif indexMode == "ROW_DIR":
            return "C"
        else:
            return None


def create_record_layout_components(parent) -> Dict:
    result = {}
    result["axes"] = {}
    result["elements"] = {}
    if isinstance(parent, AxisPts):
        record_layout = parent.depositAttr
    elif isinstance(parent, Characteristic):
        record_layout = parent.deposit
    base_address = parent.address
    elements = []
    axes_names = record_layout.axes.keys()
    for idx, axis_name in enumerate(axes_names):
        axis_components = record_layout.axes.get(axis_name)
        if isinstance(parent, Characteristic):
            if parent.type == "VAL_BLK":
                max_axis_points = reduce(mul, parent.fnc_np_shape, 1)
            else:
                axis_desc = parent.axisDescription(axis_name)
                max_axis_points = axis_desc.maxAxisPoints
        else:
            max_axis_points = parent.maxAxisPoints
        # if "axis_pts" not in axis_components and "axisRescale" not in axis_components:
        #    raise ValueError(f"Neither `axis_pts` nor `axisRescale` in RecordLayout {parent.name!r}")
        if "axis_pts" in axis_components:
            axis_pts = axis_components.get("axis_pts")
            index_incr = axis_pts.indexIncr
            if index_incr == "INDEX_DECR":
                reversed_storage = True
            else:
                reversed_storage = False
            axis_info = AxisInfo(
                data_type=axis_pts.data_type,
                category="COM_AXIS",
                maximum_points=max_axis_points,
                reversed_storage=reversed_storage,
                addressing=axis_pts.addressing,
            )
        elif "axis_rescale" in axis_components:
            axis_rescale = axis_components.get("axis_rescale")
            index_incr = axis_rescale.indexIncr
            if index_incr == "INDEX_DECR":
                reversed_storage = True
            else:
                reversed_storage = False
            if "no_rescale" in axis_components:
                axis_components.get("no_rescale")
            else:
                pass
            axis_info = AxisInfo(
                data_type=axis_rescale.data_type,
                category="RES_AXIS",
                maximum_points=axis_rescale.maxNumberOfRescalePairs << 1,
                reversed_storage=reversed_storage,
                addressing=axis_rescale.addressing,
            )
        elif "offset" in axis_components:
            offset = axis_components.get("offset")
            dist_op = axis_components.get("dist_op")
            ## FIX_AXIS_PAR_DIST
            shift_op = axis_components.get("shift_op")
            ## FIX_AXIS_PAR
            if dist_op is not None:
                pass
            elif shift_op is not None:
                pass
            else:
                raise ValueError(f"Either `DIST_OP` or `SHIFT_OP` needed for FIX_AXIS in RecordLayout {parent.name!r}")
            axis_info = AxisInfo(
                data_type="FLOAT64_IEEE",
                category="FIX_AXIS",
                maximum_points=axis_desc.maxAxisPoints,
                reversed_storage=False,
                addressing="DIRECT",
            )
        elif "fix_no_axis_pts" in axis_components:
            fix_no_axis_pts = axis_components.get("fix_no_axis_pts")
            axis_info = AxisInfo(
                data_type="-",
                category="COM_AXIS",
                maximum_points=fix_no_axis_pts.number,
                reversed_storage=False,
                addressing="DIRECT",
            )
        elif "no_axis_pts" in axis_components:
            axis_info = AxisInfo(
                data_type="-",
                category="COM_AXIS",
                maximum_points=axis_desc.maxAxisPoints,
                reversed_storage=False,
                addressing="DIRECT",
            )
        else:
            print("*** ax", axis_components)
            raise TypeError("???")
        result["axes"][axis_name] = axis_info
    for ax in record_layout.axes.keys():
        for key, value in record_layout.axes[ax].items():
            result["axes"][ax].elements[key] = value
            elements.append((key, value))
    if record_layout.fncValues.valid():
        elements.append(("fnc_values", record_layout.fncValues))
        result["elements"]["fnc_values"] = record_layout.fncValues
    if record_layout.identification.valid():
        elements.append(("identification", record_layout.identification))
        result["elements"]["identification"] = record_layout.identification
    if record_layout.reserved:
        for idx, reserved in enumerate(record_layout.reserved):
            elment_name = f"reserved_{idx}"
            elements.append((elment_name, reserved))
            result["elements"][elment_name] = reserved
    elements = sorted(elements, key=lambda x: x[1].position)
    for name, attr in elements:
        if name in ("fix_no_axis_pts",):
            continue
        aligned_address = record_layout.alignment.align(attr.data_type, base_address)
        attr.address = aligned_address
        if name == "axis_pts":
            if "fix_no_axis_pts" in record_layout.axes[attr.axis]:
                max_axis_points = record_layout.axes[attr.axis].get("fix_no_axis_pts").number
            else:
                max_axis_points = result["axes"][attr.axis].maximum_points
            base_address = aligned_address + (attr.byte_size * max_axis_points)
        elif name == "axis_rescale":
            base_address = attr.byte_size * attr.maxNumberOfRescalePairs * 2
        else:
            base_address = aligned_address + attr.byte_size
    return result


@dataclass
class AxisPts(CachedBase):
    """"""

    axis: model.AxisPts = field(repr=False)
    name: str
    longIdentifier: Optional[str]
    address: int
    inputQuantity: Optional[str]
    deposit: Optional[str]
    maxDiff: Optional[float]
    _conversionRef: str = field(repr=False)
    compuMethod: CompuMethod
    maxAxisPoints: int
    lowerLimit: float
    upperLimit: float
    annotations: List[Annotation]
    byteOrder: Optional[str]
    calibrationAccess: Optional[str]
    displayIdentifier: Optional[str]
    ecuAddressExtension: int
    extendedLimits: ExtendedLimits
    format: Optional[str]
    functionList: List[str]
    guardRails: bool
    monotony: Optional[str]
    physUnit: Optional[str]
    readOnly: bool
    refMemorySegment: Optional[str]
    stepSize: Optional[float]
    symbolLink: Dict
    depositAttr: RecordLayout
    record_layout_components: Dict

    def __init__(self, session, name: str, module_name: str = None):
        self.axis = session.query(model.AxisPts).filter(model.AxisPts.name == name).first()
        self.name = name
        self.longIdentifier = self.axis.longIdentifier
        self.address = self.axis.address
        self.inputQuantity = self.axis.inputQuantity  # REF: Measurement
        self.depositAttr = RecordLayout(session, self.axis.depositAttr)
        self.deposit = self.axis.deposit.mode if self.axis.deposit else None
        self.maxDiff = self.axis.maxDiff
        self._conversionRef = self.axis.conversion
        self.compuMethod = CompuMethod.get(session, self._conversionRef)
        self.maxAxisPoints = self.axis.maxAxisPoints
        self.lowerLimit = self.axis.lowerLimit
        self.upperLimit = self.axis.upperLimit
        self.annotations = _annotations(session, self.axis.annotation)
        self.byteOrder = self.axis.byte_order.byteOrder if self.axis.byte_order else None
        self.calibrationAccess = self.axis.calibration_access
        self.displayIdentifier = self.axis.display_identifier.display_name if self.axis.display_identifier else None
        self.ecuAddressExtension = self.axis.ecu_address_extension.extension if self.axis.ecu_address_extension else 0
        self.extendedLimits = self._create_extended_limits(self.axis.extended_limits)
        self.format = self.axis.format.formatString if self.axis.format else None
        self.functionList = [f.name for f in self.axis.function_list] if self.axis.function_list else []
        self.guardRails = self.axis.guard_rails
        self.monotony = self.axis.monotony.monotony if self.axis.monotony else None
        self.physUnit = self.axis.phys_unit.unit if self.axis.phys_unit else None
        self.readOnly = self.axis.read_only
        self.refMemorySegment = self.axis.ref_memory_segment.name if self.axis.ref_memory_segment else None
        self.stepSize = self.axis.step_size
        self.symbolLink = self._dissect_symbol_link(self.axis.symbol_link)
        self.record_layout_components = create_record_layout_components(self)

    @property
    def record_layout(self) -> RecordLayout:
        return self.depositAttr

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
    def _create_extended_limits(limits):
        if limits is not None:
            return ExtendedLimits(limits.lowerLimit, limits.upperLimit)
        else:
            return ExtendedLimits()

    @staticmethod
    def _dissect_symbol_link(sym_link):
        if sym_link is not None:
            result = {}
            result["symbolName"] = sym_link.symbolName
            result["offset"] = sym_link.offset
        else:
            result = None
        return result

    @property
    def fnc_asam_dtype(self):
        """Return `str` (e.g. `SLONG`)."""
        if self.depositAttr is None:
            return None
        x_axis = self.depositAttr.axes.get("x")
        axis_pts = x_axis.get("axis_pts")
        if axis_pts is None:
            return None
        return axis_pts.data_type

    @property
    def fnc_np_dtype(self):
        """Return `str` (e.g. `int32`) suitable for Numpy."""
        if self.depositAttr is None:
            return None
        x_axis = self.depositAttr.axes.get("x")
        axis_pts = x_axis.get("axis_pts")
        if axis_pts is None:
            return None
        return ASAM_TO_NUMPY_TYPES.get(axis_pts.data_type)


@dataclass
class AxisDescr(CachedBase):
    """"""

    axisPtsRef: AxisPts = field(repr=False)
    attribute: str
    inputQuantity: Optional[str]
    _conversionRef: Optional[str] = field(repr=False)
    lowerLimit: float
    upperLimit: float
    compuMethod: Union[CompuMethod, str]
    maxAxisPoints: int
    byteOrder: Optional[str]
    annotations: List[Annotation]
    curveAxisRef: Optional[str]
    deposit: Optional[Any]
    extendedLimits: Dict
    fixAxisPar: FixAxisPar
    fixAxisParDist: FixAxisParDist
    fixAxisParList: Dict
    format: Optional[str]
    maxGrad: Optional[float]
    monotony: Optional[str]
    physUnit: Optional[str]
    readOnly: bool
    stepSize: Optional[float]

    def __init__(self, session, axis, module_name=None):
        self.attribute = axis.attribute
        self.axisPtsRef = AxisPts.get(session, axis.axis_pts_ref.axisPoints) if axis.axis_pts_ref else None
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
            CompuMethod.get(session, self._conversionRef) if self._conversionRef != "NO_COMPU_METHOD" else "NO_COMPU_METHOD"
        )
        self.annotations = _annotations(session, axis.annotation)
        self.byteOrder = axis.byte_order.byteOrder if axis.byte_order else None
        self.curveAxisRef = Characteristic.get(session, axis.curve_axis_ref.curveAxis) if axis.curve_axis_ref else None
        self.deposit = axis.deposit.mode if axis.deposit else None
        self.extendedLimits = self._create_extended_limits(axis.extended_limits)
        self.fixAxisPar = self._create_fix_axis_par(axis.fix_axis_par)
        self.fixAxisParDist = self._create_fix_axis_par_dist(axis.fix_axis_par_dist)
        self.fixAxisParList = axis.fix_axis_par_list.axisPts_Value if axis.fix_axis_par_list else []
        self.format = axis.format.formatString if axis.format else None
        self.maxGrad = axis.max_grad.maxGradient if axis.max_grad else None
        self.monotony = axis.monotony.monotony if axis.monotony else None
        self.physUnit = axis.phys_unit.unit if axis.phys_unit else None
        self.readOnly = axis.read_only
        self.stepSize = axis.step_size.stepSize if axis.step_size else None

    @staticmethod
    def _create_extended_limits(limits):
        if limits is not None:
            return ExtendedLimits(limits.lowerLimit, limits.upperLimit)
        else:
            return ExtendedLimits()

    @staticmethod
    def _create_fix_axis_par(axis):
        if axis is not None:
            return FixAxisPar(axis.offset, axis.shift, axis.numberapo)
        else:
            return FixAxisPar()

    @staticmethod
    def _create_fix_axis_par_dist(axis):
        if axis is not None:
            return FixAxisParDist(axis.offset, axis.distance, axis.numberapo)
        else:
            return FixAxisParDist()

    def axisDescription(self, axis):
        if axis == 0 or axis.lower() == "x":
            return self
        raise ValueError("axis value out of range.")


@dataclass
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

    characteristic: model.Characteristic = field(repr=False)
    name: str
    longIdentifier: Optional[str]
    type: str
    address: int
    deposit: RecordLayout
    maxDiff: int
    _conversionRef: str = field(repr=False)
    lowerLimit: float
    upperLimit: float
    annotations: List[Annotation]
    axisDescriptions: List[AxisDescr]
    bitMask: Optional[int]
    byteOrder: Optional[str]
    compuMethod: CompuMethod
    calibrationAccess: Optional[str]
    comparisonQuantity: Optional[str]
    dependent_characteristic: DependentCharacteristic
    discrete: bool
    displayIdentifier: Optional[str]
    ecuAddressExtension: int
    extendedLimits: ExtendedLimits
    format: Optional[str]
    functionList: List[str]
    guardRails: bool
    mapList: List
    matrixDim: MatrixDim
    maxRefresh: Dict
    number: Optional[int]
    physUnit: Optional[str]
    readOnly: bool
    refMemorySegment: Optional[str]
    stepSize: Optional[float]
    symbolLink: Optional[str]
    virtual_characteristic: VirtualCharacteristic
    fnc_np_shape: tuple
    record_layout_components: Dict

    def __init__(self, session, name: str, module_name: str = None):
        self.characteristic = session.query(model.Characteristic).filter(model.Characteristic.name == name).first()
        if self.characteristic is None:
            raise ValueError(f"'{name}' object does not exist.")
        self.name = name
        self.longIdentifier = self.characteristic.longIdentifier
        self.type = self.characteristic.type
        self.address = self.characteristic.address
        self.deposit = RecordLayout(session, self.characteristic.deposit, module_name)
        self.maxDiff = self.characteristic.maxDiff
        self._conversionRef = self.characteristic.conversion
        self.compuMethod = (
            CompuMethod.get(session, self._conversionRef) if self._conversionRef != "NO_COMPU_METHOD" else "NO_COMPU_METHOD"
        )
        self.lowerLimit = self.characteristic.lowerLimit
        self.upperLimit = self.characteristic.upperLimit
        self.annotations = _annotations(session, self.characteristic.annotation)
        self.bitMask = self.characteristic.bit_mask.mask if self.characteristic.bit_mask else None
        self.byteOrder = self.characteristic.byte_order.byteOrder if self.characteristic.byte_order else None
        # all_axes_names()
        self.axisDescriptions = [AxisDescr.get(session, a) for a in self.characteristic.axis_descr]
        self.calibrationAccess = self.characteristic.calibration_access
        self.comparisonQuantity = self.characteristic.comparison_quantity
        if self.characteristic.dependent_characteristic:
            self.dependent_characteristic = DependentCharacteristic(
                self.characteristic.dependent_characteristic.formula,
                list(self.characteristic.dependent_characteristic.characteristic_id),
            )
        else:
            self.dependent_characteristic = None
        self.discrete = self.characteristic.discrete
        self.displayIdentifier = (
            self.characteristic.display_identifier.display_name if self.characteristic.display_identifier else None
        )
        self.ecuAddressExtension = (
            self.characteristic.ecu_address_extension.extension if self.characteristic.ecu_address_extension else 0
        )
        self.extendedLimits = self._create_extended_limits(self.characteristic.extended_limits)
        self.format = self.characteristic.format.formatString if self.characteristic.format else None
        self.functionList = [f.name for f in self.characteristic.function_list] if self.characteristic.function_list else []
        self.guardRails = self.characteristic.guard_rails
        self.mapList = [f.name for f in self.characteristic.map_list] if self.characteristic.map_list else []
        self.matrixDim = self._create_matrix_dim(self.characteristic.matrix_dim)
        self.maxRefresh = self._dissect_max_refresh(self.characteristic.max_refresh)
        self.number = self.characteristic.number.number if self.characteristic.number else None
        self.physUnit = self.characteristic.phys_unit.unit if self.characteristic.phys_unit else None
        self.readOnly = self.characteristic.read_only
        self.refMemorySegment = self.characteristic.ref_memory_segment.name if self.characteristic.ref_memory_segment else None
        self.stepSize = self.characteristic.step_size
        self.symbolLink = self._dissect_symbol_link(self.characteristic.symbol_link)
        if self.characteristic.virtual_characteristic:
            self.virtual_characteristic = VirtualCharacteristic(
                self.characteristic.virtual_characteristic.formula,
                list(self.characteristic.virtual_characteristic.characteristic_id),
            )
        else:
            self.virtual_characteristic = None
        self.fnc_np_shape = fnc_np_shape(self.matrixDim) or (() if self.number is None else (self.number,))
        self.record_layout_components = create_record_layout_components(self)

    def axisDescription(self, axis) -> AxisDescr:
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
                raise ValueError(f"'{axis}' is an invalid axis name.")
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
    def record_layout(self) -> RecordLayout:
        return self.deposit

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

    def axis_info(self, axis_name: str) -> AxisInfo:
        axes = self.record_layout_components.get("axes")
        return axes.get(axis_name)

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
            if md.valid():
                result["x"] = md.x
                result["y"] = md.y
                result["z"] = md.z
            else:
                num = self.number  # Deprecated -- The use of NUMBER  should be replaced by MATRIX_DIM
                # TODO: Errorhandling.
                result["x"] = num
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
    def _create_extended_limits(limits):
        if limits is not None:
            return ExtendedLimits(limits.lowerLimit, limits.upperLimit)
        else:
            return ExtendedLimits()

    @staticmethod
    def _create_matrix_dim(matrix_dim):
        if matrix_dim is not None:
            return MatrixDim(matrix_dim.xDim, matrix_dim.yDim, matrix_dim.zDim)
        else:
            return MatrixDim()

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


def axispts_or_characteristic(session, name: str) -> Union[AxisPts, Characteristic]:
    """Load an AxisPts or Characteristic object (they share the same namespace).

    Parameters
    ----------
    session: Sqlite3 session object
    name: str
        The name of an `AxisPts` or `Characteristic` object.
    """
    if chs := session.query(model.Characteristic).filter(model.Characteristic.name == name).first():
        return chs
    elif axp := session.query(model.AxisPts).filter(model.AxisPts.name == name).first():
        return axp
    else:
        raise ValueError(f"No Characteristic or Axis found with name {name!r}")


@dataclass
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
        'FLOAT16_IEEE' | 'FLOAT32_IEEE' | 'FLOAT64_IEEE']
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

    measurement: model.Measurement = field(repr=False)
    name: str
    longIdentifier: Optional[str]
    datatype: str
    _conversionRef: str
    resolution: int
    accuracy: float
    lowerLimit: float
    upperLimit: float
    annotations: List[Annotation]
    arraySize: Optional[int]
    bitMask: Optional[int]
    bitOperation: Dict
    byteOrder: Optional[str]
    discrete: bool
    displayIdentifier: Optional[str]
    ecuAddress: Optional[int]
    ecuAddressExtension: Optional[int]
    errorMask: Optional[int]
    format: Optional[str]
    functionList: List[Dict]
    layout: Optional[str]
    matrixDim: MatrixDim
    maxRefresh: Dict
    physUnit: Optional[str]
    readWrite: bool
    refMemorySegment: Optional[str]
    symbolLink: Dict
    virtual: List[str]
    compuMethod: CompuMethod
    fnc_np_shape: tuple

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
        self.bitOperation = self._dissect_bit_operation(self, self.measurement.bit_operation)
        self.byteOrder = self.measurement.byte_order.byteOrder if self.measurement.byte_order else None
        self.discrete = self.measurement.discrete
        self.displayIdentifier = self.measurement.display_identifier.display_name if self.measurement.display_identifier else None
        self.ecuAddress = self.measurement.ecu_address.address if self.measurement.ecu_address else None
        self.ecuAddressExtension = self.measurement.ecu_address_extension.extension if self.measurement.ecu_address_extension else 0
        self.errorMask = self.measurement.error_mask.mask if self.measurement.error_mask else None
        self.format = self.measurement.format.formatString if self.measurement.format else None
        self.functionList = self.measurement.function_list.name if self.measurement.function_list else []
        self.layout = self.measurement.layout.indexMode if self.measurement.layout else None
        self.matrixDim = self._create_matrix_dim(self.measurement.matrix_dim)
        self.maxRefresh = self._dissect_max_refresh(self.measurement.max_refresh)
        self.physUnit = self.measurement.phys_unit.unit if self.measurement.phys_unit else None
        self.readWrite = False if self.measurement.read_write is None else True
        self.refMemorySegment = self.measurement.ref_memory_segment.name if self.measurement.ref_memory_segment else None
        self.symbolLink = self._dissect_symbol_link(self.measurement.symbol_link)
        self.virtual = self.measurement.virtual.measuringChannel if self.measurement.virtual else []
        self.compuMethod = CompuMethod.get(session, self._conversionRef)
        self.fnc_np_shape = fnc_np_shape(self.matrixDim)

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
    def _create_matrix_dim(matrix_dim):
        if matrix_dim is not None:
            return MatrixDim(matrix_dim.xDim, matrix_dim.yDim, matrix_dim.zDim)
        else:
            return MatrixDim()

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


@dataclass
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

    session: Any = field(repr=False)
    function: model.Function = field(repr=False)
    name: str
    longIdentifier: Optional[str]
    annotations: List[Annotation]
    functionVersion: str
    _inMeasurements: List[str]
    _locMeasurements: List[str]
    _outMeasurements: List[str]
    _defCharacteristics: List[str]
    _refCharacteristics: List[str]
    _subFunctions: List[str]

    def __init__(self, session, name=None, module_name: str = None):
        self.session = session
        self.function = session.query(model.Function).filter(model.Function.name == name).first()
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
            self._inMeasurements = (
                [Measurement.get(self.session, m) for m in self.function.in_measurement.identifier]
                if self.function.in_measurement
                else []
            )
        return self._inMeasurements

    @property
    def locMeasurements(self):
        if self._locMeasurements is None:
            self._locMeasurements = (
                [Measurement.get(self.session, m) for m in self.function.loc_measurement.identifier]
                if self.function.loc_measurement
                else []
            )
        return self._locMeasurements

    @property
    def outMeasurements(self):
        if self._outMeasurements is None:
            self._outMeasurements = (
                [Measurement.get(self.session, m) for m in self.function.out_measurement.identifier]
                if self.function.out_measurement
                else []
            )
        return self._outMeasurements

    @property
    def defCharacteristics(self):
        if self._defCharacteristics is None:
            self._defCharacteristics = (
                [get_characteristic_or_axispts(self.session, r) for r in self.function.def_characteristic.identifier]
                if self.function.def_characteristic
                else []
            )
        return self._defCharacteristics

    @property
    def refCharacteristics(self):
        if self._refCharacteristics is None:
            self._refCharacteristics = (
                [get_characteristic_or_axispts(self.session, r) for r in self.function.ref_characteristic.identifier]
                if self.function.ref_characteristic
                else []
            )
        return self._refCharacteristics

    @property
    def subFunctions(self):
        if self._subFunctions is None:
            self._subFunctions = (
                [Function.get(self.session, g) for g in self.function.sub_function.identifier] if self.function.sub_function else []
            )
        return self._subFunctions

    @classmethod
    def get_root_functions(klass, session, ordered=False):
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
        func_names = [f[0] for f in session.query(model.Function.name).filter(not_(model.Function.name.in_(excluded_funcs))).all()]
        if ordered:
            func_names = sorted(func_names)
        result = []
        for func_name in func_names:
            result.append(Function.get(session, func_name))
        return result


@dataclass
class Group(CachedBase):
    """

    Parameters
    ----------
    session: Sqlite3 session object

    Attributes
    ----------
    session:
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

    session: Any = field(repr=False)
    group: model.Group = field(repr=False)
    name: str
    longIdentifier: Optional[str]
    annotations: List[Annotation]
    root: bool
    _characteristics: List[Any]
    _measurements: List[Any]
    _functions: List[Any]
    _subgroups: List[Any]

    def __init__(self, session, name=None, module_name: str = None):
        self.session = session
        self.group = session.query(model.Group).filter(model.Group.groupName == name).first()
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
            self._characteristics = (
                [get_characteristic_or_axispts(self.session, r) for r in self.group.ref_characteristic.identifier]
                if self.group.ref_characteristic
                else []
            )
        return self._characteristics

    @property
    def measurements(self):
        if self._measurements is None:
            self._measurements = (
                [Measurement.get(self.session, m) for m in self.group.ref_measurement.identifier]
                if self.group.ref_measurement
                else []
            )
        return self._measurements

    @property
    def functions(self):
        if self._functions is None:
            self._functions = (
                [Function.get(self.session, f) for f in self.group.function_list.name] if self.group.function_list else []
            )
        return self._functions

    @property
    def subgroups(self):
        if self._subgroups is None:
            self._subgroups = [Group.get(self.session, g) for g in self.group.sub_group.identifier] if self.group.sub_group else []
        return self._subgroups

    @classmethod
    def get_root_groups(klass, session, ordered=False):
        """Fetch all groups marked as root/toplevel.

        Parameters
        ----------
        session: Sqlite3 session object

        ordered: bool
            If True, order by group-name.

        """
        result = []
        query = session.query(model.Group).filter(model.Group.root is not None)
        if ordered:
            query = query.order_by(model.Group.groupName)
        for group in query.all():
            result.append(Group.get(session, group.groupName))
        return result


@dataclass
class TypedefStructure(CachedBase):
    """

    Parameters
    ----------
    session: Sqlite3 session object


    Attributes
    ----------
    session:
        Raw Sqlite3 database object.

    name: str

    longIdentifier: str
        comment, description.

    size: int

    link: str

    symbol: str
    """

    session: Any = field(repr=False)
    typedef: model.TypedefStructure = field(repr=False)
    name: str
    longIdentifier: Optional[str]
    size: int
    link: str
    symbol: str

    def __init__(self, session, name=None, module_name: str = None):
        self.session = session
        self.typedef = session.query(model.TypedefStructure).filter(model.TypedefStructure.name == name).first()
        self.name = self.typedef.name
        self.longIdentifier = self.typedef.longIdentifier
        self.size = self.typedef.size
        self.link = self.typedef.link
        self.symbol = self.typedef.symbol
        instance_names = session.query(model.Instance.name).filter(model.Instance.typeName == self.name).all()
        self._instances = [Instance.get(session, name[0]) for name in instance_names]
        self._components = [
            StructureComponent.get(session, c.name, module_name, self.typedef) for c in self.typedef.structure_component
        ]

    @property
    def instances(self):
        return self._instances

    @property
    def components(self):
        return self._components


@dataclass
class StructureComponent(CachedBase):
    """

    Parameters
    ----------
    session: Sqlite3 session object


    Attributes
    ----------
    session:
        Raw Sqlite3 database object.

    name: str

    deposit: str

    offset: int

    link: str

    symbol: str
    """

    session: Any = field(repr=False)
    component: model.StructureComponent = field(repr=False)
    name: str
    deposit: RecordLayout
    link: str
    symbol: str

    def __init__(self, session, name=None, module_name: str = None, parent=None, *args):
        self.session = session
        self.component = (
            session.query(model.StructureComponent)
            .filter(
                # filter(and_(model.StructureComponent.name == name, model.StructureComponent.typedef_structure.rid == parent.rid)).first()
                model.StructureComponent.name
                == name
            )
            .first()
        )
        self.name = self.component.name
        self.deposit = RecordLayout(session, self.component.deposit, module_name)
        self.offset = self.component.offset
        self.link = self.component.link
        self.symbol = self.component.symbol


@dataclass
class Instance(CachedBase):
    """

    Parameters
    ----------
    session: Sqlite3 session object


    Attributes
    ----------
    session:
        Raw Sqlite3 database object.

    name: str

    longIdentifier: str
        comment, description.

    typeName: str
        s. :func:`_annotations`

    address: int


    symbol: str
    """

    session: Any = field(repr=False)
    instance: model.Instance = field(repr=False)
    name: str
    longIdentifier: Optional[str]
    typeName: str
    address: int

    def __init__(self, session, name=None, module_name: str = None):
        self.session = session
        self.instance = session.query(model.Instance).filter(model.Instance.name == name).first()
        self.name = self.instance.name
        self.longIdentifier = self.instance.longIdentifier
        self.typeName = self.instance.typeName
        self.address = self.instance.address
        # self._defined_by = TypedefStructure.get(session, self.typeName, module_name)

    """
    @property
    def defined_by(self):
        return self._defined_by
    """


@dataclass
class TypedefMeasurement(CachedBase):
    """
    Parameters
    ----------
    session: Sqlite3 session object

    name: str
        name of one existing TYPEDEF_MEASUREMENT object.

    Attributes
    ----------
    typedef:
        Raw Sqlite3 database object.

    name: str
        name of the TypedefMeasurement (s. Parameters...)

    longIdentifier: str
        comment, description.

    datatype: ['UBYTE' | 'SBYTE' | 'UWORD' | 'SWORD' | 'ULONG' | 'SLONG' | 'A_UINT64' | 'A_INT64' |
        'FLOAT16_IEEE' | 'FLOAT32_IEEE' | 'FLOAT64_IEEE']
        Type of the TypedefMeasurement.

    resolution: int
        smallest possible change in bits

    accuracy: float
        possible variation from exact value in %

    lowerLimit: float
        plausible range of table values, lower limit

    upperLimit: float
        plausible range of table values, upper limit
    """

    typedef: model.TypedefMeasurement = field(repr=False)
    name: str
    longIdentifier: Optional[str]
    datatype: str
    _conversionRef: Optional[str] = field(repr=False)
    resolution: Optional[int]
    accuracy: Optional[float]
    upperLimit: Optional[float]
    lowerLimit: Optional[float]
    compuMethod: CompuMethod

    def __init__(self, session, name: str, module_name: str = None):
        self.typedef = session.query(model.TypedefMeasurement).filter(model.TypedefMeasurement.name == name).first()
        self.name = name
        self.longIdentifier = self.typedef.longIdentifier
        self.datatype = self.typedef.datatype
        self._conversionRef = self.typedef.conversion
        self.resolution = self.typedef.resolution
        self.accuracy = self.typedef.accuracy
        self.lowerLimit = self.typedef.lowerLimit
        self.upperLimit = self.typedef.upperLimit
        self.compuMethod = (
            CompuMethod.get(session, self._conversionRef) if self._conversionRef != "NO_COMPU_METHOD" else "NO_COMPU_METHOD"
        )


@dataclass
class TypedefCharacteristic(CachedBase):
    """
    Parameters
    ----------
    session: Sqlite3 session object

    name: str
        name of one existing TYPEDEF_CHARACTERISTIC object.

    Attributes
    ----------
    typedef:
        Raw Sqlite3 database object.

    name: str
        name of the TypedefCharacteristic (s. Parameters...)

    longIdentifier: str
        comment, description.

    type: ("ASCII", "CURVE", "MAP", "CUBOID", "CUBE_4", "CUBE_5", "VAL_BLK", "VALUE")
        Type of the TypedefCharacteristic.

    deposit: RecordLayout
        Deposit in memory.

    maxDiff: float
        possible variation from exact value in %

    lowerLimit: float
        plausible range of table values, lower limit

    upperLimit: float
        plausible range of table values, upper limit
    """

    typedef: model.TypedefCharacteristic = field(repr=False)
    name: str
    longIdentifier: Optional[str]
    type: str
    _conversionRef: Optional[str] = field(repr=False)
    deposit: RecordLayout
    maxDiff: Optional[float]
    lowerLimit: Optional[float]
    upperLimit: Optional[float]
    compuMethod: CompuMethod

    def __init__(self, session, name: str, module_name: str = None):
        self.typedef = session.query(model.TypedefCharacteristic).filter(model.TypedefCharacteristic.name == name).first()
        self.name = name
        self.longIdentifier = self.typedef.longIdentifier
        self.type = self.typedef.type
        self._conversionRef = self.typedef.conversion
        self.deposit = RecordLayout(session, self.typedef.deposit, module_name)
        self.maxDiff = self.typedef.maxDiff
        self.lowerLimit = self.typedef.lowerLimit
        self.upperLimit = self.typedef.upperLimit
        self.compuMethod = (
            CompuMethod.get(session, self._conversionRef) if self._conversionRef != "NO_COMPU_METHOD" else "NO_COMPU_METHOD"
        )


@dataclass
class VarCriterion:
    name: str
    longIdentifier: str
    values: List[str]
    var_characteristic: Optional[str]
    var_measurement: Optional[str]


@dataclass
class VarCharacteristic:
    name: str
    criterions: List[str]
    addresses: List[int]


@dataclass
class VarCombination:
    address: int
    combinations: List[Dict[str, str]]


@dataclass
class VariantCoding(CachedBase):
    """
    Parameters
    ----------
    session: Sqlite3 session object

    name: str
        name of one existing VARIANT_CODING  object.

    Attributes
    ----------
    """

    variant_coding: model.VariantCoding = field(repr=False)
    session: Any = field(repr=False)
    variant_coded: bool
    naming: str
    separator: str
    criterions: Dict[str, VarCriterion]
    characteristics: Dict[str, VarCharacteristic]
    forbidden_combs: List[Dict[str, str]]
    _combination_cache: Dict[str, str] = field(repr=False)
    _product_cache: Dict[List[str], Tuple[str]] = field(repr=False)

    def __init__(self, session, name: str = None, module_name: str = None):
        variant_coding = session.query(model.VariantCoding)
        if module_name is not None:
            variant_coding.filter(model.Module.name == module_name)
        variant_coding = variant_coding.first()
        self.session = session
        if variant_coding:
            self.variant_coded = True
            self.naming = variant_coding.var_naming.tag if variant_coding.var_naming else "NUMERIC"
            self.separator = variant_coding.var_separator.separator if variant_coding.var_separator else "."
            self.criterions = {}
            self.characteristics = {}
            self.forbidden_combs = []
            self._combination_cache = {}
            self._product_cache = {}

            for characteristic in variant_coding.var_characteristic:
                self.characteristics[characteristic.name] = VarCharacteristic(
                    characteristic.name,
                    characteristic.criterionName,
                    characteristic.var_address.address if characteristic.var_address else [],
                )

            for criterion in variant_coding.var_criterion:
                self.criterions[criterion.name] = VarCriterion(
                    criterion.name,
                    criterion.longIdentifier,
                    criterion.value,
                    criterion.var_selection_characteristic.name if criterion.var_selection_characteristic else None,
                    criterion.var_measurement.name if criterion.var_measurement else None,
                )

            for comb in variant_coding.var_forbidden_comb:
                self.forbidden_combs.append({p.criterionName: p.criterionValue for p in comb.pairs})
        else:
            self.variant_coded = False

    def get_citerion_values(self, name: str) -> List[str]:
        res = self.criterions.get(name)
        if res:
            return res.values
        return []

    def values_product(self, criterions: List[str]) -> List[str]:
        criterions = tuple(criterions)
        if criterions in self._product_cache:
            return self._product_cache[criterions]
        result = itertools.product(*[self.criterions[c].values for c in criterions])
        self._product_cache[criterions] = result
        return result

    def valid_combinations(self, criterions: List[str]) -> List[str]:
        criterions = tuple(criterions)
        if criterions in self._combination_cache:
            return self._combination_cache[criterions]
        result = []
        for entry in self.values_product(criterions):
            line = dict(zip(criterions, entry))
            if line not in self.forbidden_combs:
                result.append(line)
        self._combination_cache[criterions] = result
        return result

    def variants(self, name: str) -> List[VarCombination]:
        ac = axispts_or_characteristic(self.session, name)
        vcc = self.characteristics.get(ac.name)
        combis = self.valid_combinations(vcc.criterions)
        return [VarCombination(a, c) for c, a in zip(combis, vcc.addresses)]
