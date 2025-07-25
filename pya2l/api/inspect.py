#!/usr/bin/env python
"""Classes for easy, convenient, read-only access to A2L databases.

This module provides a comprehensive API for accessing and inspecting A2L database
entities such as measurements, characteristics, axis points, and computation methods.
It is designed to be used with SQLAlchemy sessions to query the database and
present the results in a more user-friendly format.

The module includes classes for all major A2L entities, with methods to access
their properties and relationships. It also provides utility functions for
converting between different data formats and representations.
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
from operator import attrgetter, mul
from typing import (
    Any,
    Callable,
    Dict,
    Generator,
    Generic,
    List,
    Optional,
    Tuple,
    TypeVar,
    Union,
)

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


T = TypeVar("T")

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
    """Enumeration for program memory layout types.

    This enum defines the different types of program memory layouts
    that can be specified in an A2L file.

    Attributes
    ----------
    PRG_CODE : int
        Program code memory layout
    PRG_DATA : int
        Program data memory layout
    PRG_RESERVED : int
        Reserved program memory layout
    """

    PRG_CODE = 0
    PRG_DATA = 1
    PRG_RESERVED = 2


class PrgTypeSegment(IntEnum):
    """Enumeration for program memory segment types.

    This enum defines the different types of program memory segments
    that can be specified in an A2L file.

    Attributes
    ----------
    CALIBRATION_VARIABLES : int
        Segment containing calibration variables
    CODE : int
        Segment containing program code
    DATA : int
        Segment containing data
    EXCLUDE_FROM_FLASH : int
        Segment that should be excluded from flash programming
    OFFLINE_DATA : int
        Segment containing offline data
    RESERVED : int
        Reserved segment type
    SERAM : int
        Segment in Serial RAM
    VARIABLES : int
        Segment containing variables
    """

    CALIBRATION_VARIABLES = 0
    CODE = 1
    DATA = 2
    EXCLUDE_FROM_FLASH = 3
    OFFLINE_DATA = 4
    RESERVED = 5
    SERAM = 6
    VARIABLES = 7


class MemoryType(IntEnum):
    """Enumeration for memory types.

    This enum defines the different types of memory that can be
    specified in an A2L file.

    Attributes
    ----------
    EEPROM : int
        Electrically Erasable Programmable Read-Only Memory
    EPROM : int
        Erasable Programmable Read-Only Memory
    FLASH : int
        Flash memory
    RAM : int
        Random Access Memory
    ROM : int
        Read-Only Memory
    NOT_IN_ECU : int
        Memory not physically present in the ECU
    """

    EEPROM = 0
    EPROM = 1
    FLASH = 2
    RAM = 3
    ROM = 4
    NOT_IN_ECU = 5


class SegmentAttributeType(IntEnum):
    """Enumeration for segment attribute types.

    This enum defines the different types of segment attributes
    that can be specified in an A2L file.

    Attributes
    ----------
    INTERN : int
        Internal segment (within the ECU)
    EXTERN : int
        External segment (outside the ECU)
    """

    INTERN = 0
    EXTERN = 1


##
## Dataclasses.
##


@dataclass
class Alignment:
    """Class representing memory alignment requirements for different data types.

    This class defines the alignment requirements for various data types
    and provides methods to get the alignment for a specific data type
    and to align an offset according to the requirements.

    Attributes
    ----------
    byte : int
        Alignment requirement for byte-sized data types (8 bits)
    dword : int
        Alignment requirement for double word-sized data types (32 bits)
    float16 : int
        Alignment requirement for 16-bit floating point data types
    float32 : int
        Alignment requirement for 32-bit floating point data types
    float64 : int
        Alignment requirement for 64-bit floating point data types
    qword : int
        Alignment requirement for quad word-sized data types (64 bits)
    word : int
        Alignment requirement for word-sized data types (16 bits)
    """

    byte: int
    dword: int
    float16: int
    float32: int
    float64: int
    qword: int
    word: int

    # Mapping from ASAM data types to alignment type attributes
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
        """Get the alignment requirement for a specific data type.

        Parameters
        ----------
        data_type : str
            The ASAM data type name (e.g., 'UBYTE', 'SWORD', 'FLOAT32_IEEE')

        Returns
        -------
        int
            The alignment requirement in bytes

        Raises
        ------
        ValueError
            If the data type is not recognized
        """
        if data_type not in self.TYPE_MAP:
            raise ValueError(f"Invalid data type {data_type!r}.")
        attr = self.TYPE_MAP.get(data_type)
        return getattr(self, attr)

    def align(self, data_type: str, offset: int) -> int:
        """Align an offset according to the requirements of a data type.

        Parameters
        ----------
        data_type : str
            The ASAM data type name (e.g., 'UBYTE', 'SWORD', 'FLOAT32_IEEE')
        offset : int
            The offset to align

        Returns
        -------
        int
            The aligned offset

        Raises
        ------
        ValueError
            If the data type is not recognized
        """
        return align_as(offset, self.get(data_type))


NATURAL_ALIGNMENTS = Alignment(byte=1, dword=4, float16=2, float32=4, float64=8, qword=8, word=2)


@dataclass
class RecordLayoutBase:
    """Base class for record layout components.

    This class serves as a base for various record layout components
    such as axis points, function values, etc. It provides common
    attributes and methods used by all record layout components.

    Attributes
    ----------
    position : Optional[int]
        Position of the component in the record layout
    data_type : Optional[str]
        ASAM data type of the component
    axis : str
        Axis identifier (e.g., 'x', 'y', 'z')
    address : int
        Memory address of the component
    """

    position: Optional[int] = field(default=None)
    data_type: Optional[str] = field(default=None)
    axis: str = field(default="-")
    address: int = field(default=-1)

    def valid(self) -> bool:
        """Check if the record layout component is valid.

        A valid component must have both position and data_type defined.

        Returns
        -------
        bool
            True if the component is valid, False otherwise
        """
        return self.position is not None and self.data_type is not None

    @cached_property
    def byte_size(self) -> int:
        """Get the size of the component in bytes.

        Returns
        -------
        int
            Size of the component in bytes based on its data type
        """
        return ASAM_TYPE_SIZES.get(self.data_type)


@dataclass
class RecordLayoutAxisPts(RecordLayoutBase):
    """Record layout component for axis points.

    This class represents the axis points component in a record layout,
    which defines how axis points are stored in memory.

    Attributes
    ----------
    indexIncr : Optional[str]
        Increment type for indices
    addressing : Optional[str]
        Addressing mode for the axis points
    """

    indexIncr: Optional[str] = field(default=None)
    addressing: Optional[str] = field(default=None)


@dataclass
class RecordLayoutAxisRescale(RecordLayoutBase):
    """Record layout component for axis rescale points.

    This class represents the axis rescale component in a record layout,
    which defines how axis rescale points are stored in memory.

    Attributes
    ----------
    indexIncr : Optional[str]
        Increment type for indices
    maxNumberOfRescalePairs : Optional[int]
        Maximum number of rescale pairs
    addressing : Optional[str]
        Addressing mode for the rescale points
    """

    indexIncr: Optional[str] = field(default=None)
    maxNumberOfRescalePairs: Optional[int] = field(default=None)
    addressing: Optional[str] = field(default=None)


@dataclass
class RecordLayoutFncValues(RecordLayoutBase):
    """Record layout component for function values.

    This class represents the function values component in a record layout,
    which defines how function values are stored in memory.

    Attributes
    ----------
    indexMode : Optional[str]
        Mode for indexing the function values
    addresstype : Optional[str]
        Type of addressing for the function values
    """

    indexMode: Optional[str] = field(default=None)
    addresstype: Optional[str] = field(default=None)


@dataclass
class RecordLayoutDistOp(RecordLayoutBase):
    """Record layout component for distance operation.

    This class represents the distance operation component in a record layout,
    which defines how distance operations are stored in memory.
    """

    pass


@dataclass
class RecordLayoutIdentification(RecordLayoutBase):
    """Record layout component for identification.

    This class represents the identification component in a record layout,
    which defines how identification data is stored in memory.
    """

    pass


@dataclass
class RecordLayoutNoAxisPts(RecordLayoutBase):
    """Record layout component for number of axis points.

    This class represents the number of axis points component in a record layout,
    which defines how the count of axis points is stored in memory.
    """

    pass


@dataclass
class RecordLayoutNoRescale(RecordLayoutBase):
    """Record layout component for number of rescale points.

    This class represents the number of rescale points component in a record layout,
    which defines how the count of rescale points is stored in memory.
    """

    pass


@dataclass
class RecordLayoutOffset(RecordLayoutBase):
    """Record layout component for offset.

    This class represents the offset component in a record layout,
    which defines how offset values are stored in memory.
    """

    pass


@dataclass
class RecordLayoutReserved(RecordLayoutBase):
    """Record layout component for reserved space.

    This class represents the reserved space component in a record layout,
    which defines areas of memory that are reserved for future use.
    """

    pass


@dataclass
class RecordLayoutRipAddr(RecordLayoutBase):
    """Record layout component for RIP address.

    This class represents the RIP (Relative Instruction Pointer) address component
    in a record layout, which defines how RIP addresses are stored in memory.
    """

    pass


@dataclass
class RecordLayoutSrcAddr(RecordLayoutBase):
    """Record layout component for source address.

    This class represents the source address component in a record layout,
    which defines how source addresses are stored in memory.
    """

    pass


@dataclass
class RecordLayoutShiftOp(RecordLayoutBase):
    """Record layout component for shift operation.

    This class represents the shift operation component in a record layout,
    which defines how shift operations are stored in memory.
    """

    pass


@dataclass
class RecordLayoutFixNoAxisPts:
    """Record layout component for fixed number of axis points.

    This class represents a fixed number of axis points in a record layout,
    which defines a constant number of axis points rather than reading
    the count from memory.

    Attributes
    ----------
    number : Optional[int]
        The fixed number of axis points
    position : int
        Position in the record layout
    axis : str
        Axis identifier (e.g., 'x', 'y', 'z')
    """

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
    """Fixed axis parameters for axis descriptions.

    This class represents fixed axis parameters that define how axis points
    are distributed in memory using a shift-based approach.

    Attributes
    ----------
    offset : Optional[int]
        Offset of the first axis point
    shift : Optional[int]
        Shift value for calculating axis point positions
    numberapo : Optional[int]
        Number of axis points
    """

    offset: Optional[int] = field(default=None)
    shift: Optional[int] = field(default=None)
    numberapo: Optional[int] = field(default=None)

    def valid(self) -> bool:
        """Check if the fixed axis parameters are valid.

        Valid parameters must have offset, shift, and numberapo defined.

        Returns
        -------
        bool
            True if the parameters are valid, False otherwise
        """
        return self.offset is not None and self.shift is not None and self.numberapo is not None


@dataclass
class FixAxisParDist:
    """Fixed axis parameters with distance for axis descriptions.

    This class represents fixed axis parameters that define how axis points
    are distributed in memory using a distance-based approach.

    Attributes
    ----------
    offset : Optional[int]
        Offset of the first axis point
    distance : Optional[int]
        Distance between consecutive axis points
    numberapo : Optional[int]
        Number of axis points
    """

    offset: Optional[int] = field(default=None)
    distance: Optional[int] = field(default=None)
    numberapo: Optional[int] = field(default=None)

    def valid(self) -> bool:
        """Check if the fixed axis parameters are valid.

        Valid parameters must have offset, distance, and numberapo defined.

        Returns
        -------
        bool
            True if the parameters are valid, False otherwise
        """
        return self.offset is not None and self.distance is not None and self.numberapo is not None


@dataclass
class ExtendedLimits:
    """Extended limits for axis descriptions and characteristics.

    This class represents extended limits that define the valid range
    of values for an axis or characteristic beyond the standard limits.

    Attributes
    ----------
    lowerLimit : Optional[float]
        Lower limit of the valid range
    upperLimit : Optional[float]
        Upper limit of the valid range
    """

    lowerLimit: Optional[float] = field(default=None)
    upperLimit: Optional[float] = field(default=None)

    def valid(self) -> bool:
        """Check if the extended limits are valid.

        Valid limits must have both lowerLimit and upperLimit defined.

        Returns
        -------
        bool
            True if the limits are valid, False otherwise
        """
        return self.lowerLimit is not None and self.upperLimit is not None


@dataclass
class MatrixDim:
    """Matrix dimensions for multi-dimensional data.

    This class represents the dimensions of a matrix (1D, 2D, or 3D)
    used for multi-dimensional data in characteristics and measurements.

    Attributes
    ----------
    x : Optional[int]
        Size of the first dimension (X)
    y : Optional[int]
        Size of the second dimension (Y)
    z : Optional[int]
        Size of the third dimension (Z)
    numbers : tuple
        Tuple of dimension sizes
    """

    x: Optional[int] = field(default=None)
    y: Optional[int] = field(default=None)
    z: Optional[int] = field(default=None)

    def __init__(self, matrix_dim):
        """Initialize a MatrixDim instance.

        Parameters
        ----------
        matrix_dim : Any
            Object containing matrix dimension information

        Notes
        -----
        The matrix_dim object should have a 'numbers' attribute that is
        a sequence of dimension sizes.
        """
        self.numbers = ()
        if matrix_dim is not None:
            try:
                numbers = matrix_dim.numbers
                self.numbers = numbers
                length = len(numbers)
                if length >= 3:
                    self.z = numbers[2]
                    self.y = numbers[1]
                    self.x = numbers[0]
                elif length == 2:
                    self.y = numbers[1]
                    self.x = numbers[0]
                elif length == 1:
                    self.x = numbers[0]
            except (AttributeError, IndexError) as e:
                # Handle case where matrix_dim doesn't have expected structure
                print(f"Error initializing MatrixDim: {e}")

    def valid(self) -> bool:
        """Check if the matrix dimensions are valid.

        Valid dimensions must have x, y, and z defined.

        Returns
        -------
        bool
            True if the dimensions are valid, False otherwise
        """
        return self.x is not None and self.y is not None and self.z is not None


@dataclass
class Annotation:
    """Annotation for A2L objects.

    This class represents an annotation that can be attached to various
    A2L objects to provide additional information.

    Attributes
    ----------
    label : Optional[str]
        Label or title of the annotation
    origin : Optional[str]
        Origin or source of the annotation
    text : List[str]
        List of text lines in the annotation
    """

    label: Optional[str]
    origin: Optional[str]
    text: List[str]


@dataclass
class DependentCharacteristic:
    """Dependent characteristic definition.

    This class represents a dependent characteristic, which is a characteristic
    whose value depends on other characteristics through a formula.

    Attributes
    ----------
    formula : str
        Formula that defines how the dependent characteristic is calculated
    characteristics : List[str]
        List of characteristic names that the formula depends on
    """

    formula: str
    characteristics: List[str]


@dataclass
class VirtualCharacteristic:
    """Virtual characteristic definition.

    This class represents a virtual characteristic, which is a characteristic
    that doesn't have a physical representation in memory but is calculated
    from other characteristics.

    Attributes
    ----------
    formula : str
        Formula that defines how the virtual characteristic is calculated
    characteristics : List[str]
        List of characteristic names that the formula depends on
    """

    formula: str
    characteristics: List[str]


@dataclass
class MaxRefresh:
    """Maximum refresh rate information.

    This class represents the maximum refresh rate for a measurement,
    defining how frequently the measurement can be updated.

    Attributes
    ----------
    scalingUnit : Optional[int]
        Scaling unit for the refresh rate (e.g., 1=seconds, 1000=milliseconds)
    rate : Optional[int]
        Maximum refresh rate value
    """

    scalingUnit: Optional[int] = field(default=None)
    rate: Optional[int] = field(default=None)


@dataclass
class SymbolLink:
    """Symbol link information.

    This class represents a link to a symbol in the ECU code,
    which can be used to reference variables or functions.

    Attributes
    ----------
    symbolLink : Optional[str]
        Name of the symbol to link to
    offset : Optional[int]
        Offset to add to the symbol's address
    """

    symbolLink: Optional[str] = field(default=None)
    offset: Optional[int] = field(default=None)


@dataclass
class AxisInfo:
    """Axis information for characteristics and measurements.

    This class provides detailed information about an axis in a
    characteristic or measurement, including its data type, storage
    format, and element count.

    Attributes
    ----------
    data_type : str
        ASAM data type of the axis elements
    category : str
        Category of the axis (e.g., 'CURVE_AXIS', 'MAP_AXIS')
    maximum_element_count : int
        Maximum number of elements in the axis
    reversed_storage : bool
        Whether the axis elements are stored in reversed order
    addressing : str
        Addressing mode for the axis elements
    elements : Dict
        Dictionary of axis elements
    adjustable : bool
        Whether the axis is adjustable
    actual_element_count : Optional[int]
        Actual number of elements in the axis (may be less than maximum)
    """

    data_type: str
    category: str
    maximum_element_count: int
    reversed_storage: bool
    addressing: str
    elements: Dict = field(default_factory=dict)
    adjustable: bool = field(default=False)
    actual_element_count: Optional[int] = field(default=None)


def asam_type_size(datatype: str) -> int:
    """Get the size in bytes of an ASAM data type.

    Parameters
    ----------
    datatype : str
        The ASAM data type name (e.g., 'UBYTE', 'SWORD', 'FLOAT32_IEEE')

    Returns
    -------
    int
        Size of the data type in bytes

    Raises
    ------
    KeyError
        If the data type is not found in ASAM_TYPE_SIZES
    """
    return ASAM_TYPE_SIZES[datatype]


def all_axes_names() -> List[str]:
    """Get a list of all possible axis names.

    Returns
    -------
    List[str]
        List of axis names: ['x', 'y', 'z', '4', '5']
    """
    return list("x y z 4 5".split())


def get_module(session: Any, module_name: Optional[str] = None) -> Optional[model.Module]:
    """Get a module from the database.

    Parameters
    ----------
    session : Any
        SQLAlchemy session object
    module_name : Optional[str], optional
        Name of the module to retrieve, by default None

    Returns
    -------
    Optional[model.Module]
        The module object if found, None otherwise
    """
    query = session.query(model.Module)
    if module_name:
        query = query.filter(model.Module.name == module_name)
    return query.first()


def _annotations(session: Any, refs: Optional[List[Any]]) -> List[Annotation]:
    """Extract annotation information from database objects.

    Parameters
    ----------
    session : Any
        SQLAlchemy session object
    refs : Optional[List[Any]]
        List of raw database objects containing annotation information

    Returns
    -------
    List[Annotation]
        List of Annotation objects extracted from the database objects
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


def fnc_np_shape(matrixDim: MatrixDim) -> Tuple[int, ...]:
    """Convert MatrixDim object to tuple suitable as Numpy array `shape` argument.

    Parameters
    ----------
    matrixDim : MatrixDim
        MatrixDim object containing x, y, z dimensions

    Returns
    -------
    Tuple[int, ...]
        Tuple of dimensions suitable for Numpy array shape
        Empty tuple if matrixDim is not valid
    """
    if not matrixDim.valid():
        return ()
    result = []
    for n, dim in sorted(asdict(matrixDim).items(), key=lambda x: x[0]):
        if dim is None or dim < 1:
            continue
        else:
            result.append(dim)
    return tuple(result)


def fnc_np_order(order: Optional[str]) -> Optional[str]:
    """Convert ASAM indexMode to NumPy array order string.

    Parameters
    ----------
    order : Optional[str]
        The indexMode string, either "COLUMN_DIR" or "ROW_DIR"

    Returns
    -------
    Optional[str]
        "F" for "COLUMN_DIR" (Fortran order, column-major)
        "C" for "ROW_DIR" (C order, row-major)
        None if order is None or not recognized
    """
    if order is None:
        return None
    if order == "COLUMN_DIR":
        return "F"
    elif order == "ROW_DIR":
        return "C"
    else:
        return None


class FilteredList(Generic[T]):
    """A filtered list of objects from a database association.

    This class provides a way to filter and query objects from a database
    association, returning instances of a specified class.

    Attributes
    ----------
    session : Any
        SQLAlchemy session object
    association : Any
        Database association to query
    klass : Type[T]
        Class to instantiate for each row
    attribute : Callable
        Function to extract the attribute used for instantiation
    """

    def __init__(self, session, association, klass: T, attr_name: str = "name") -> None:
        """Initialize a FilteredList instance.

        Parameters
        ----------
        session : Any
            SQLAlchemy session object
        association : Any
            Database association to query
        klass : Type[T]
            Class to instantiate for each row
        attr_name : str, optional
            Name of the attribute to use for instantiation, by default "name"
        """
        self.session = session
        self.association = association
        self.klass = klass
        self.attribute = attrgetter(attr_name)

    def query(self, criterion: Optional[Callable] = None) -> Generator:
        """Query the association with an optional filter criterion.

        Parameters
        ----------
        criterion : Optional[Callable], optional
            Function to filter rows, by default None

        Returns
        -------
        Generator
            Generator yielding instances of the specified class

        Notes
        -----
        If criterion is None, all rows are returned.
        The criterion function should take a row and return True if the row
        should be included in the results.
        """
        if criterion is None:
            criterion = lambda x: x

        if self.association is None:
            return

        try:
            for row in self.association:
                if criterion(row):
                    try:
                        xn = self.klass.get(self.session, self.attribute(row))
                        if xn is not None:
                            yield xn
                    except (AttributeError, ValueError) as e:
                        print(f"Error getting {self.klass.__name__} instance: {e}")
        except Exception as e:
            print(f"Error querying association: {e}")


class CachedBase:
    """Base class for all user classes in this module, implementing a cache manager.

    This class provides a caching mechanism to avoid creating duplicate instances
    of the same object, which can improve performance and memory usage.

    Attributes
    ----------
    _cache : weakref.WeakValueDictionary
        Dictionary mapping (class_name, object_name, args) tuples to instances
    _strong_ref : collections.deque
        Deque of strong references to instances to prevent garbage collection

    Note
    ----
    To take advantage of caching, always use `get` method.

    Example
    -------
    meas = Measurement.get(session, "someMeasurement")  # This is the right way.

    meas = Measurement(session, "someMeasurement")      # Constructor directly called, no caching.
    """

    _cache: weakref.WeakValueDictionary = weakref.WeakValueDictionary()
    _strong_ref: collections.deque = collections.deque(maxlen=DB_CACHE_SIZE)

    def __new__(cls, *args, **kwargs):
        """Create a new instance of the class.

        This method is called when a new instance is created directly
        (not through the `get` method).

        Parameters
        ----------
        *args : Any
            Positional arguments to pass to the constructor
        **kwargs : Any
            Keyword arguments to pass to the constructor

        Returns
        -------
        Any
            A new instance of the class
        """
        instance = super().__new__(cls)  # Call the parent class's __new__ method
        return instance

    @classmethod
    def get(cls, session: Any, name: Optional[str] = None, module_name: Optional[str] = None, *args: Any) -> Any:
        """Get an instance of the class, using cache if available.

        Parameters
        ----------
        session : Any
            SQLAlchemy session object
        name : Optional[str], optional
            Name of the object to retrieve, by default None
        module_name : Optional[str], optional
            Name of the module, by default None
        *args : Any
            Additional arguments to pass to the constructor

        Returns
        -------
        Any
            An instance of the class, or None if an error occurs

        Notes
        -----
        This method first checks if an instance with the given parameters
        already exists in the cache. If it does, that instance is returned.
        Otherwise, a new instance is created, added to the cache, and returned.
        """
        if session is None:
            print(f"{cls.__name__}.get(): session cannot be None")
            return None

        entry = (cls.__name__, name, args)
        if entry not in cls._cache:
            try:
                inst = cls(session, name, module_name, *args)
                cls._cache[entry] = inst
                cls._strong_ref.append(inst)
            except Exception as e:
                print(f"{cls.__name__}.get({name!r}): {e!r}")
                return None
        return cls._cache[entry]

    @classmethod
    def inny(cls):
        """Debug method to print the class name.

        This method is used for debugging purposes.
        """
        print("INNY: ", cls.__name__)


class NoCompuMethod(SingletonBase):
    """Null-Object implementation for NO_COMPU_METHOD.

    This class provides a placeholder for when no computation method is available,
    implementing the same interface as CompuMethod but performing no conversion.
    """

    def __init__(self) -> None:
        """Initialize a NoCompuMethod instance with default values."""
        self._name: Optional[str] = None
        self._longIdentifier: Optional[str] = None
        self._conversionType: str = "NO_COMPU_METHOD"
        self._format: Optional[str] = None
        self._unit: Optional[str] = None
        self._coeffs: List[float] = []
        self._coeffs_linear: List[float] = []
        self._formula: Optional[str] = None
        self._tab: Optional[Any] = None
        self._tab_verb: Optional[Any] = None
        self._statusStringRef: Optional[str] = None
        self._refUnit: Optional[str] = None

    @property
    def name(self) -> Optional[str]:
        """Get the name of the computation method.

        Returns
        -------
        Optional[str]
            Name of the computation method, None for NoCompuMethod
        """
        return self._name

    @property
    def longIdentifier(self) -> Optional[str]:
        """Get the long identifier of the computation method.

        Returns
        -------
        Optional[str]
            Long identifier, None for NoCompuMethod
        """
        return self._longIdentifier

    @property
    def conversionType(self) -> str:
        """Get the conversion type.

        Returns
        -------
        str
            Always "NO_COMPU_METHOD" for this class
        """
        return self._conversionType

    @property
    def format(self) -> Optional[str]:
        """Get the format string.

        Returns
        -------
        Optional[str]
            Format string, None for NoCompuMethod
        """
        return self._format

    @property
    def unit(self) -> Optional[str]:
        """Get the unit.

        Returns
        -------
        Optional[str]
            Unit, None for NoCompuMethod
        """
        return self._unit

    @property
    def coeffs(self) -> List[float]:
        """Get the coefficients.

        Returns
        -------
        List[float]
            Empty list for NoCompuMethod
        """
        return self._coeffs

    @property
    def coeffs_linear(self) -> List[float]:
        """Get the linear coefficients.

        Returns
        -------
        List[float]
            Empty list for NoCompuMethod
        """
        return self._coeffs_linear

    @property
    def formula(self) -> Optional[str]:
        """Get the formula.

        Returns
        -------
        Optional[str]
            Formula, None for NoCompuMethod
        """
        return self._formula

    @property
    def tab(self) -> Optional[Any]:
        """Get the table.

        Returns
        -------
        Optional[Any]
            Table, None for NoCompuMethod
        """
        return self._tab

    @property
    def tab_verb(self) -> Optional[Any]:
        """Get the verbal table.

        Returns
        -------
        Optional[Any]
            Verbal table, None for NoCompuMethod
        """
        return self._tab_verb

    @property
    def statusStringRef(self) -> Optional[str]:
        """Get the status string reference.

        Returns
        -------
        Optional[str]
            Status string reference, None for NoCompuMethod
        """
        return self._statusStringRef

    @property
    def refUnit(self) -> Optional[str]:
        """Get the reference unit.

        Returns
        -------
        Optional[str]
            Reference unit, None for NoCompuMethod
        """
        return self._refUnit

    def int_to_physical(self, i: Any) -> Any:
        """Convert internal value to physical value (identity function).

        Parameters
        ----------
        i : Any
            Internal value

        Returns
        -------
        Any
            Same value (no conversion)
        """
        return i

    def physical_to_int(self, p: Any) -> Any:
        """Convert physical value to internal value (identity function).

        Parameters
        ----------
        p : Any
            Physical value

        Returns
        -------
        Any
            Same value (no conversion)
        """
        return p

    def __str__(self) -> str:
        """Get string representation.

        Returns
        -------
        str
            String representation of the object
        """
        return "NoCompuMethod()"


@dataclass
class CompuTab(CachedBase):
    session: Any = field(repr=False)
    compu_tab: model.CompuTab = field(repr=False)
    name: str
    longIdentifier: str
    interpolation: bool
    default_value: Optional[float] = field(default=None)
    in_values: List[float] = field(default_factory=list)
    out_values: List[float] = field(default_factory=list)

    def __init__(self, session, name: str, module_name: Optional[str] = None):
        self.session = session
        compu_tab = session.query(model.CompuTab).filter(model.CompuTab.name == name)
        if module_name is not None:
            compu_tab.join(model.Module).filter(model.Module.name == module_name)
        self.compu_tab = compu_tab.first()
        if self.compu_tab is None:
            raise ValueError(f"COMPU_TAB {name!r} does not exist.")
        self.name = self.compu_tab.name
        self.longIdentifier = self.compu_tab.longIdentifier
        self.interpolation = True if self.compu_tab.conversionType == "TAB_INTP" else False
        self.default_value = self.compu_tab.default_value_numeric.display_value if self.compu_tab.default_value_numeric else None
        self.in_values = [x.inVal for x in self.compu_tab.pairs]
        self.out_values = [x.outVal for x in self.compu_tab.pairs]


@dataclass
class CompuTabVerb(CachedBase):
    session: Any = field(repr=False)
    compu_tab_verb: model.CompuTab = field(repr=False)
    name: str
    longIdentifier: str
    interpolation: bool
    default_value: Optional[float] = field(default=None)
    in_values: List[float] = field(default_factory=list)
    text_values: List[str] = field(default_factory=list)

    def __init__(self, session, name: str, module_name: Optional[str] = None):
        self.session = session
        compu_tab_verb = session.query(model.CompuVtab).filter(model.CompuVtab.name == name)
        if module_name is not None:
            compu_tab_verb.join(model.Module).filter(model.Module.name == module_name)
        self.compu_tab_verb = compu_tab_verb.first()
        if self.compu_tab_verb is None:
            raise ValueError(f"COMPU_VTAB {name!r} does not exist.")
        self.name = self.compu_tab_verb.name
        self.longIdentifier = self.compu_tab_verb.longIdentifier
        self.interpolation = True if self.compu_tab_verb.conversionType == "TAB_INTP" else False
        self.default_value = self.compu_tab_verb.default_value.display_string if self.compu_tab_verb.default_value else None
        self.in_values = [x.inVal for x in self.compu_tab_verb.pairs]
        self.text_values = [x.outVal for x in self.compu_tab_verb.pairs]


@dataclass
class CompuTabVerbRanges(CachedBase):
    session: Any = field(repr=False)
    compu_tab_verb_ranges: model.CompuTab = field(repr=False)
    name: str
    longIdentifier: str
    default_value: Optional[float] = field(default=None)
    lower_values: List[float] = field(default_factory=list)
    upper_values: List[float] = field(default_factory=list)
    text_values: List[str] = field(default_factory=list)

    def __init__(self, session, name: str, module_name: Optional[str] = None):
        self.session = session
        compu_tab_verb_ranges = session.query(model.CompuVtabRange).filter(model.CompuVtabRange.name == name)
        if module_name is not None:
            compu_tab_verb_ranges.join(model.Module).filter(model.Module.name == module_name)
        self.compu_tab_verb_ranges = compu_tab_verb_ranges.first()
        if self.compu_tab_verb_ranges is None:
            raise ValueError(f"COMPU_VTAB_RANGE {name!r} does not exist.")
        self.name = self.compu_tab_verb_ranges.name
        self.longIdentifier = self.compu_tab_verb_ranges.longIdentifier
        self.default_value = (
            self.compu_tab_verb_ranges.default_value.display_string if self.compu_tab_verb_ranges.default_value else None
        )
        self.lower_values = [x.inValMin for x in self.compu_tab_verb_ranges.triples]
        self.upper_values = [x.inValMax for x in self.compu_tab_verb_ranges.triples]
        self.text_values = [x.outVal for x in self.compu_tab_verb_ranges.triples]


@dataclass
class CompuMethod(CachedBase):
    """Computation method for converting between internal and physical values.

    This class represents a computation method that defines how to convert between
    internal (ECU) values and physical values. It supports various conversion types
    such as linear, rational functions, tables, and formulas.

    Attributes
    ----------
    compu_method : model.CompuMethod
        Raw database object
    name : str
        Name of the computation method
    longIdentifier : str
        Description of the computation method
    conversionType : str
        Type of conversion (e.g., "IDENTICAL", "LINEAR", "RAT_FUNC", "TAB_INTP")
    format : Optional[str]
        Format string for displaying physical values
    unit : Optional[str]
        Physical unit of the values
    coeffs : Coeffs
        Coefficients for rational function conversion
    coeffs_linear : CoeffsLinear
        Coefficients for linear conversion
    formula : Dict[str, float]
        Formula for conversion
    tab : CompuTable
        Table for numeric conversion
    tab_verb : Union[CompuTableVerb, CompuTabVerbRanges]
        Table for verbal conversion
    statusStringRef : Optional[str]
        Reference to status strings
    refUnit : Optional[str]
        Reference unit
    evaluator : Callable
        Function object that performs the actual conversion
    """

    compu_method: model.CompuMethod = field(repr=False)
    session: Any = field(repr=False)
    name: str
    longIdentifier: str
    conversionType: str
    format: Optional[str]
    unit: Optional[str]
    coeffs: Optional[Coeffs]
    coeffs_linear: Optional[CoeffsLinear]
    formula: Dict[str, Any]
    tab: Optional[CompuTab]
    tab_verb: Optional[CompuTabVerb]
    tab_verb_ranges: Optional[CompuTabVerbRanges]
    statusStringRef: Optional[str]
    refUnit: Optional[str]
    evaluator: Callable = field(repr=False, default=Identical())

    def __init__(self, session: Any, name: str, module_name: Optional[str] = None) -> None:
        """Initialize a CompuMethod instance.

        Parameters
        ----------
        session : Any
            SQLAlchemy session object
        name : str
            Name of the computation method to retrieve
        module_name : Optional[str], optional
            Name of the module, by default None
        """
        compu_method = session.query(model.CompuMethod).filter(model.CompuMethod.name == name)
        self.session = session
        if module_name is not None:
            compu_method.join(model.Module).filter(model.Module.name == module_name)
        self.compu_method = compu_method.first()
        if self.compu_method is None:
            raise ValueError(f"COMPU_METHOD {name!r} does not exist.")
        self.name = name
        self.longIdentifier = self.compu_method.longIdentifier
        self.conversionType = self.compu_method.conversionType
        self.format = self.compu_method.format
        self.unit = self.compu_method.unit
        self.formula = {}
        self.tab = None
        self.tab_verb = None
        self.tab_verb_ranges = None
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
            self.tab = CompuTab.get(self.session, name=self.compu_method.compu_tab_ref.conversionTable, module_name=module_name)
        elif cm_type == "TAB_VERB":
            has_compu_vtab = self.session.query(
                self.session.query(model.CompuVtab)
                .filter(model.CompuVtab.name == self.compu_method.compu_tab_ref.conversionTable)
                .exists()
            ).scalar()
            if has_compu_vtab:
                self.tab_verb = CompuTabVerb.get(
                    self.session, name=self.compu_method.compu_tab_ref.conversionTable, module_name=module_name
                )
            else:
                self.tab_verb_ranges = CompuTabVerbRanges.get(
                    self.session, name=self.compu_method.compu_tab_ref.conversionTable, module_name=module_name
                )
        # Set evaluator.
        if cm_type in ("IDENTICAL", "NO_COMPU_METHOD"):
            self.evaluator = Identical()
        elif cm_type == "FORM":
            formula = self.formula["formula"]
            formula_inv = self.formula["formula_inv"]
            mod_par = ModPar.get(session)
            system_constants = mod_par.systemConstants
            self.evaluator = Formula(formula, formula_inv, system_constants)
        elif cm_type == "LINEAR":
            coeffs = self.coeffs_linear
            if coeffs is None:
                raise exceptions.StructuralError("'LINEAR' requires coefficients (COEFFS_LINEAR).")
            self.evaluator = Linear(coeffs)
        elif cm_type == "RAT_FUNC":
            coeffs = self.coeffs
            if coeffs is None:
                raise exceptions.StructuralError("'RAT_FUNC' requires coefficients (COEFFS).")
            self.evaluator = RatFunc(coeffs)
        elif cm_type in ("TAB_INTP", "TAB_NOINTP"):
            klass = InterpolatedTable if self.tab.interpolation else LookupTable
            pairs = zip(self.tab.in_values, self.tab.out_values)
            default = self.tab.default_value
            self.evaluator = klass(pairs, default)
        elif cm_type == "TAB_VERB":
            if self.tab_verb is not None:
                pairs = zip(self.tab_verb.in_values, self.tab_verb.text_values)
                self.evaluator = LookupTable(pairs, self.tab_verb.default_value)
            else:
                triples = zip(
                    self.tab_verb_ranges.lower_values,
                    self.tab_verb_ranges.upper_values,
                    self.tab_verb_ranges.text_values,
                )
                self.evaluator = LookupTableWithRanges(triples, self.tab_verb_ranges.default_value)
        else:
            raise ValueError(f"Unknown conversation type '{cm_type}'.")

    def int_to_physical(self, i: Union[int, float, Any]) -> Any:
        """Convert internal value to physical value.

        Parameters
        ----------
        i : Union[int, float, Any]
            Internal value (can be scalar or array)

        Returns
        -------
        Any
            Physical value
        """
        return self.evaluator.int_to_physical(i)

    def physical_to_int(self, p: Union[int, float, Any]) -> Any:
        """Convert physical value to internal value.

        Parameters
        ----------
        p : Union[int, float, Any]
            Physical value (can be scalar or array)

        Returns
        -------
        Any
            Internal value
        """
        return self.evaluator.physical_to_int(p)

    @classmethod
    def get(
        cls, session: Any, name: Optional[str] = None, module_name: Optional[str] = None
    ) -> Union["CompuMethod", NoCompuMethod]:
        """Get a CompuMethod instance, using cache if available.

        Parameters
        ----------
        session : Any
            SQLAlchemy session object
        name : Optional[str], optional
            Name of the computation method to retrieve, by default None
        module_name : Optional[str], optional
            Name of the module, by default None

        Returns
        -------
        Union[CompuMethod, NoCompuMethod]
            CompuMethod instance or NoCompuMethod instance if name is "NO_COMPU_METHOD"
        """
        if name == "NO_COMPU_METHOD":
            return NoCompuMethod()
        else:
            return super(cls, CompuMethod).get(session, name, module_name)


@dataclass
class MemoryLayout:
    """
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
    """

    prgType: PrgTypeLayout
    address: int
    size: int
    offset_0: int
    offset_1: int
    offset_2: int
    offset_3: int
    offset_4: int
    if_data: List[Dict]


@dataclass
class MemorySegment:
    """
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
    """

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
    if_data: List[Dict]


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
        self.memoryLayouts = self._create_memory_layout(session, self.modpar.memory_layout)
        self.memorySegments = self._create_memory_segments(session, self.modpar.memory_segment)
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
    def _create_memory_layout(session, layouts) -> List[MemoryLayout]:
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
                    session.parse_ifdata(layout.if_data),
                )
                result.append(entry)
        return result

    @staticmethod
    def _create_memory_segments(session, segments) -> List[MemorySegment]:
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
                    session.parse_ifdata(segment.if_data),
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
        layout = session.query(model.RecordLayout).filter(model.RecordLayout.name == name)
        if module_name is not None:
            layout.join(model.Module).filter(model.Module.name == module_name)
        self.layout = layout.first()
        if self.layout is None:
            raise ValueError(f"RECORD_LAYOUT {name!r} does not exist.")
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
    result["variables"] = {}
    result["position"] = []
    if isinstance(parent, AxisPts):
        record_layout = parent.depositAttr
    elif isinstance(parent, Characteristic):
        record_layout = parent.deposit
    base_address = parent.address
    dynamic_record_layout = not record_layout.staticRecordLayout
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
            if "no_axis_pts" in axis_components and dynamic_record_layout:
                adjustable = True
            else:
                adjustable = False
            axis_info = AxisInfo(
                data_type=axis_pts.data_type,
                category="COM_AXIS",
                maximum_element_count=max_axis_points,
                reversed_storage=reversed_storage,
                addressing=axis_pts.addressing,
                adjustable=adjustable,
            )
        elif "axis_rescale" in axis_components:
            axis_rescale = axis_components.get("axis_rescale")
            index_incr = axis_rescale.indexIncr
            if index_incr == "INDEX_DECR":
                reversed_storage = True
            else:
                reversed_storage = False
            if "no_rescale" in axis_components and dynamic_record_layout:
                adjustable = True
            else:
                adjustable = False
            axis_info = AxisInfo(
                data_type=axis_rescale.data_type,
                category="RES_AXIS",
                maximum_element_count=axis_rescale.maxNumberOfRescalePairs,
                # NOTE: Element count here is number of *PAIRS*
                reversed_storage=reversed_storage,
                addressing=axis_rescale.addressing,
                adjustable=adjustable,
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
                maximum_element_count=axis_desc.maxAxisPoints,
                reversed_storage=False,
                addressing="DIRECT",
            )
        elif "fix_no_axis_pts" in axis_components:
            fix_no_axis_pts = axis_components.get("fix_no_axis_pts")
            axis_info = AxisInfo(
                data_type="-",
                category="COM_AXIS",
                maximum_element_count=fix_no_axis_pts.number,
                reversed_storage=False,
                addressing="DIRECT",
            )
        elif "no_axis_pts" in axis_components:
            axis_info = AxisInfo(
                data_type="-",
                category="COM_AXIS",
                maximum_element_count=axis_desc.maxAxisPoints,
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
        result["position"].append(
            (
                name,
                attr,
            )
        )
        if name in ("fix_no_axis_pts",):
            continue
        aligned_address = record_layout.alignment.align(attr.data_type, base_address)
        attr.address = aligned_address
        if name == "axis_pts":
            if "fix_no_axis_pts" in record_layout.axes[attr.axis]:
                max_axis_points = record_layout.axes[attr.axis].get("fix_no_axis_pts").number
            else:
                max_axis_points = result["axes"][attr.axis].maximum_element_count
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
    if_data: List[Dict]
    functionList: List[str]
    guardRails: bool
    monotony: Optional[str]
    physUnit: Optional[str]
    readOnly: bool
    refMemorySegment: Optional[str]
    stepSize: Optional[float]
    symbolLink: SymbolLink
    depositAttr: RecordLayout
    record_layout_components: Dict

    def __init__(self, session, name: str, module_name: str = None):
        axis = session.query(model.AxisPts).filter(model.AxisPts.name == name)
        if module_name is not None:
            axis.join(model.Module).filter(model.Module.name == module_name)
        self.axis = axis.first()
        if self.axis is None:
            raise ValueError(f"AXIS {name!r} does not exist.")
        self.name = name
        self.longIdentifier = self.axis.longIdentifier
        self.address = self.axis.address
        self.inputQuantity = self.axis.inputQuantity  # REF: Measurement
        self.depositAttr = RecordLayout.get(session, self.axis.depositAttr)
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
        self.record_layout_components = create_record_layout_components(self) if self.depositAttr else None
        self.if_data = session.parse_ifdata(self.axis.if_data)

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
            return SymbolLink(sym_link.symbolName, sym_link.offset)
        else:
            return SymbolLink()

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
    maxRefresh: MaxRefresh
    number: Optional[int]
    physUnit: Optional[str]
    readOnly: bool
    refMemorySegment: Optional[str]
    stepSize: Optional[float]
    symbolLink: Optional[str]
    virtual_characteristic: VirtualCharacteristic
    fnc_np_shape: tuple
    record_layout_components: Dict
    if_data: List[Dict]

    def __init__(self, session, name: str, module_name: str = None):
        characteristic = session.query(model.Characteristic).filter(model.Characteristic.name == name)
        if module_name is not None:
            characteristic.join(model.Module).filter(model.Module.name == module_name)
        self.characteristic = characteristic.first()
        if self.characteristic is None:
            raise ValueError(f"CHARACTERISTIC {name!r} does not exist.")
        self.name = name
        self.longIdentifier = self.characteristic.longIdentifier
        self.type = self.characteristic.type
        self.address = self.characteristic.address
        self.deposit = RecordLayout.get(session, self.characteristic.deposit, module_name)
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
        self.record_layout_components = create_record_layout_components(self) if self.deposit else None
        self.fnc_np_shape: tuple = ()
        if self.matrixDim.valid():
            self.fnc_np_shape = fnc_np_shape(self.matrixDim)
        elif self.number is not None:
            self.fnc_np_shape = (self.number,)
        elif self.axisDescriptions:
            self.fnc_np_shape = tuple([ax.maxAxisPoints for ax in self.axisDescriptions])
        self.if_data = session.parse_ifdata(self.characteristic.if_data)

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
    def fnc_allocated_memory(self) -> int:
        """Statically allocated memory by function value(s)."""

        dim = self.dim
        element_size = self.fnc_element_size
        if self.type == "VALUE":
            return element_size  # Scalar Characteristic
        elif self.type == "ASCII":
            return dim["x"]  # Chars are always 8bit quantities.
        else:
            element_count = reduce(mul, [a.maxAxisPoints for a in self.axisDescriptions], 1)
            return element_count * element_size

    @property
    def axes_allocated_memory(self) -> int:
        """Statically allocated memory by axes (including meta-data)."""
        allocated_memory: int = 0
        if self.type in ("VALUE", "ASCII", "VAL_BLK"):
            return 0
        else:
            for axis, deposit in zip(self.axisDescriptions, self.deposit.axes.values()):
                if axis.attribute not in (
                    "RES_AXIS",
                    "STD_AXIS",
                ):
                    continue
                element_count = axis.maxAxisPoints
                for attr_name, attr_value in deposit.items():
                    if attr_name == "axis_pts":
                        element_size = asam_type_size(deposit.get("axis_pts").data_type)
                        allocated_memory += element_count * element_size
                    elif attr_name == "axis_rescale":
                        element_size = asam_type_size(deposit.get("axis_rescale").data_type) * 2  # pairs.
                        allocated_memory += element_count * element_size
                    elif attr_name != "fix_no_axis_pts":
                        allocated_memory += asam_type_size(attr_value.data_type)
            return allocated_memory

    @property
    def other_allocated_memory(self) -> int:
        mem_size: int = 0
        deposit = self.deposit
        if deposit.identification.valid():
            mem_size += asam_type_size(deposit.identification.data_type)
        for reserved in deposit.reserved:
            mem_size += asam_type_size(reserved.data_type)
        return mem_size

    @property
    def total_allocated_memory(self) -> int:
        """Total amount of statically allocated memory by Characteristic."""
        return self.fnc_allocated_memory + self.axes_allocated_memory + self.other_allocated_memory

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
        return MatrixDim(matrix_dim)

    @staticmethod
    def _dissect_max_refresh(max_ref):
        if max_ref is not None:
            return MaxRefresh(max_ref.scalingUnit, max_ref.rate)
        else:
            return MaxRefresh()

    @staticmethod
    def _dissect_symbol_link(sym_link):
        if sym_link is not None:
            return SymbolLink(sym_link.symbolName, sym_link.offset)
        else:
            return SymbolLink()


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
    maxRefresh: MaxRefresh
    physUnit: Optional[str]
    readWrite: bool
    refMemorySegment: Optional[str]
    symbolLink: SymbolLink
    virtual: List[str]
    compuMethod: CompuMethod
    fnc_np_shape: tuple
    if_data: List[Dict]

    def __init__(self, session, name: str, module_name: str = None):
        measurement = session.query(model.Measurement).filter(model.Measurement.name == name)
        if module_name is not None:
            measurement.join(model.Module).filter(model.Module.name == module_name)
        self.measurement = measurement.first()
        if self.measurement is None:
            raise ValueError(f"MEASUREMENT {name!r} does not exist.")
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
        self.if_data = session.parse_ifdata(self.measurement.if_data)

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
        return MatrixDim(matrix_dim)

    @staticmethod
    def _dissect_max_refresh(max_ref):
        if max_ref is not None:
            return MaxRefresh(max_ref.scalingUnit, max_ref.rate)
        else:
            MaxRefresh()

    @staticmethod
    def _dissect_symbol_link(sym_link):
        if sym_link is not None:
            return SymbolLink(sym_link.symbolName, sym_link.offset)
        else:
            return SymbolLink()


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
    if_data: List[Dict]
    inMeasurements: List[str]
    locMeasurements: List[str]
    outMeasurements: List[str]
    defCharacteristics: List[str]
    refCharacteristics: List[str]
    subFunctions: List[str]

    def __init__(self, session, name=None, module_name: str = None):
        self.session = session
        function = session.query(model.Function).filter(model.Function.name == name)
        if module_name is not None:
            function.join(model.Module).filter(model.Module.name == module_name)
        self.function = function.first()
        if self.function is None:
            raise ValueError(f"FUNCTION {name!r} does not exist.")
        self.name = self.function.name
        self.longIdentifier = self.function.longIdentifier
        self.annotations = _annotations(session, self.function.annotation)
        self.functionVersion = self.function.function_version.versionIdentifier if self.function.function_version else None
        self.if_data = session.parse_ifdata(self.function.if_data)
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
    if_data: List[Dict]
    characteristics: List[Any]
    measurements: List[Any]
    functions: List[Any]
    subgroups: List[Any]

    def __init__(self, session, name=None, module_name: str = None):
        self.session = session
        group = session.query(model.Group).filter(model.Group.groupName == name)
        if module_name is not None:
            group.join(model.Module).filter(model.Module.name == module_name)
        self.group = group.first()
        if self.group is None:
            raise ValueError(f"GROUP {name!r} does not exist.")
        self.name = self.group.groupName
        self.longIdentifier = self.group.groupLongIdentifier
        self.annotations = _annotations(session, self.group.annotation)
        self.root = False if self.group.root is None else True
        self.if_data = session.parse_ifdata(self.group.if_data)
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

    type_ref: Any

    offset: int
    """

    session: Any = field(repr=False)
    component: model.StructureComponent = field(repr=False)
    name: str
    type_ref: Any
    offset: int

    def __init__(self, session, name=None, module_name: str = None, parent=None, *args):
        self.session = session
        component = session.query(model.StructureComponent).filter(model.StructureComponent.name == name)
        if module_name is not None:
            component.join(model.Module).filter(model.Module.name == module_name)
        self.component = component.first()
        if self.component is None:
            raise ValueError(f"STRUCTURE_COMPONENT {name!r} does not exist.")
        self.name = self.component.name
        self.type_ref = self.component.type_ref
        self.offset = self.component.offset
        self.component.matrix_dim
        # self.component.symbol_type_link


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
    """

    session: Any = field(repr=False)
    typedef: model.TypedefStructure = field(repr=False)
    name: str
    longIdentifier: Optional[str]
    size: int
    components: List[StructureComponent]

    def __init__(self, session, name=None, module_name: str = None):
        self.session = session
        typedef = session.query(model.TypedefStructure).filter(model.TypedefStructure.name == name)
        if module_name is not None:
            typedef.join(model.Module).filter(model.Module.name == module_name)
        self.typedef = typedef.first()
        if self.typedef is None:
            raise ValueError(f"TYPEDEF_STRUCTURE {name!r} does not exist.")
        print("TS", self.typedef, self.typedef.symbol_type_link_id, dir(self.typedef))
        self.name = self.typedef.name
        self.longIdentifier = self.typedef.longIdentifier
        self.size = self.typedef.size
        # symbol_type_link
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
        instance = session.query(model.Instance).filter(model.Instance.name == name)
        if module_name is not None:
            instance.join(model.Module).filter(model.Module.name == module_name)
        self.instance = instance.first()
        if self.instance is None:
            raise ValueError(f"INSTANCE {name!r} does not exist.")
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
        typedef = session.query(model.TypedefMeasurement).filter(model.TypedefMeasurement.name == name)
        if module_name is not None:
            typedef.join(model.Module).filter(model.Module.name == module_name)
        self.typedef = typedef.first()
        if self.typedef is None:
            raise ValueError(f"TYPEDEF_MEASUREMENT {name!r} does not exist.")
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
        typedef = session.query(model.TypedefCharacteristic).filter(model.TypedefCharacteristic.name == name)
        if module_name is not None:
            typedef.join(model.Module).filter(model.Module.name == module_name)
        self.typedef = typedef.first()
        if self.typedef is None:
            raise ValueError(f"TYPEDEF_CHARACTERISTIC {name!r} does not exist.")
        self.name = name
        self.longIdentifier = self.typedef.longIdentifier
        self.type = self.typedef.type
        self._conversionRef = self.typedef.conversion
        self.deposit = RecordLayout.get(session, self.typedef.deposit, module_name)
        self.maxDiff = self.typedef.maxDiff
        self.lowerLimit = self.typedef.lowerLimit
        self.upperLimit = self.typedef.upperLimit
        self.compuMethod = (
            CompuMethod.get(session, self._conversionRef) if self._conversionRef != "NO_COMPU_METHOD" else "NO_COMPU_METHOD"
        )


@dataclass
class Frame(CachedBase):
    """"""

    session: Any = field(repr=False)
    frame: model.Frame = field(repr=False)
    name: str
    longIdentifier: Optional[str]
    scalingUnit: int
    rate: int
    frame_measurement: List[str]
    if_data: List[Dict]

    def __init__(self, session, name: str, module_name: str = None):
        frame = session.query(model.Frame).filter(model.Frame.name == name)
        if module_name is not None:
            frame.join(model.Module).filter(model.Module.name == module_name)
        self.frame = frame.first()
        if self.frame is None:
            raise ValueError(f"TYPEDEF_CHARACTERISTIC {name!r} does not exist.")
        self.name = name
        self.longIdentifier = self.frame.longIdentifier
        self.scalingUnit = self.frame.scalingUnit
        self.rate = self.frame.rate
        self.frame_measurement = [f.identifier for f in self.frame.frame_measurement]
        self.if_data = session.parse_ifdata(self.frame.if_data)


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
            variant_coding.join(model.Module).filter(model.Module.name == module_name)
        variant_coding = variant_coding.first()
        self.session = session
        self.naming = None
        self.separator = None
        self.criterions = []
        self.characteristics = []
        self.forbidden_combs = []
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


@dataclass
class AMLSection(CachedBase):
    session: Any = field(repr=False)
    aml_section: model.AMLSection = field(repr=False)
    text: Optional[str]
    parsed: Optional[bytes]

    def __init__(self, session):
        self.session = session
        self.aml_section = session.query(model.AMLSection).first()
        self.text = self.aml_section.text
        self.parsed = self.aml_section.parsed


@dataclass
class SiExponents:
    length: int
    mass: int
    time: int
    electricCurrent: int
    temperature: int
    amountOfSubstance: int
    luminousIntensity: int


@dataclass
class UnitConversion:
    gradient: float
    offset: float


@dataclass
class Unit(CachedBase):
    """"""

    session: Any = field(repr=False)
    unit: model.Unit = field(repr=False)
    name: str
    longIdentifier: str
    display: str
    type: str
    si_exponents: Optional[SiExponents]
    unit_conversion: Optional[UnitConversion]
    ref_unit: Optional[str]

    def __init__(self, session, name: str, module_name: Optional[str] = None):
        self.session = session
        unit = session.query(model.Unit).filter(model.Unit.name == name)
        if module_name is not None:
            unit.join(model.Module).filter(model.Module.name == module_name)
        self.unit = unit.first()
        if self.unit is None:
            raise ValueError(f"UNIT {name!r} does not exist.")
        self.name = self.unit.name
        self.longIdentifier = self.unit.longIdentifier
        self.display = self.unit.display
        self.type = self.unit.type
        self.si_exponents = self._create_si_exponents(self.unit.si_exponents)
        self.unit_conversion = self._create_unit_conversion(self.unit.unit_conversion)
        self.ref_unit = self.unit.ref_unit.unit if self.unit.ref_unit else None

    @staticmethod
    def _create_si_exponents(si_exponents: model.SiExponents) -> Optional[SiExponents]:
        if si_exponents is not None:
            return SiExponents(
                si_exponents.length,
                si_exponents.mass,
                si_exponents.time,
                si_exponents.electricCurrent,
                si_exponents.temperature,
                si_exponents.amountOfSubstance,
                si_exponents.luminousIntensity,
            )
        else:
            return None

    @staticmethod
    def _create_unit_conversion(unit_conversion: model.UnitConversion) -> Optional[UnitConversion]:
        if unit_conversion is not None:
            return UnitConversion(unit_conversion.gradient, unit_conversion.offset)
        else:
            return None


@dataclass
class Blob(CachedBase):
    session: Any = field(repr=False)
    blob: model.Blob = field(repr=False)
    name: str
    longIdentifier: str
    address: int
    length: int
    calibration_access: Optional[str]

    def __init__(self, session, name: str, module_name: Optional[str] = None):
        self.session = session
        blob = session.query(model.Blob).filter(model.Blob.name == name)
        if module_name is not None:
            blob.join(model.Module).filter(model.Module.name == module_name)
        self.blob = blob.first()
        if self.blob is None:
            raise ValueError(f"BLOB {name!r} does not exist.")
        self.name = self.blob.name
        self.longIdentifier = self.blob.longIdentifier
        self.address = self.blob.address
        self.length = self.blob.length
        if self.blob.calibration_access is not None:
            self.calibration_access = self.blob.calibration_access.type
        else:
            self.calibration_access = None


@dataclass
class Transformer(CachedBase):
    session: Any = field(repr=False)
    transformer: model.Transformer = field(repr=False)
    name: str
    version: str
    dllname32: str
    dllname64: str
    timeout: int
    trigger: str
    reverse: str
    transformer_in_objects: List[str]
    transformer_out_objects: List[str]

    def __init__(self, session, name: str, module_name: Optional[str] = None):
        self.session = session
        transformer = session.query(model.Transformer).filter(model.Transformer.name == name)
        if module_name is not None:
            transformer.join(model.Module).filter(model.Module.name == module_name)
        self.transformer = transformer.first()
        if self.transformer is None:
            raise ValueError(f"TRANSFORMER {name!r} does not exist.")
        self.name = self.transformer.name
        self.version = self.transformer.version
        self.dllname32 = self.transformer.dllname32
        self.dllname64 = self.transformer.dllname64
        self.timeout = self.transformer.timeout
        self.trigger = self.transformer.trigger
        self.reverse = self.transformer.reverse
        self.transformer_in_objects = self.transformer.transformer_in_objects.identifier
        self.transformer_out_objects = self.transformer.transformer_out_objects.identifier


@dataclass
class UserRights(CachedBase):
    """"""

    session: Any = field(repr=False)
    user_rights: model.UserRights = field(repr=False)
    userLevelId: str
    readOnly: bool
    ref_group: List[str]

    def __init__(self, session, userLevelId: str, module_name: Optional[str] = None):
        self.session = session
        user_rights = session.query(model.UserRights).filter(model.UserRights.userLevelId == userLevelId)
        if module_name is not None:
            user_rights.filter(model.UserRights.module.name == module_name)
        self.user_rights = user_rights.first()
        if self.user_rights is None:
            raise ValueError(f"USER_RIGHTS {userLevelId!r} does not exist.")
        self.userLevelId = self.user_rights.userLevelId
        self.readOnly = self.user_rights.readOnly
        self.ref_group = self.user_rights.ref_group.identifier


@dataclass
class Module(CachedBase):
    """
    *** Element("A2ml", "A2ML", False),
            Element("AxisPts", "AXIS_PTS", True),
            Element("Blob", "BLOB", True),
            Element("Characteristic", "CHARACTERISTIC", True),
            Element("CompuMethod", "COMPU_METHOD", True),
            Element("CompuTab", "COMPU_TAB", True),
            Element("CompuVtab", "COMPU_VTAB", True),
            Element("CompuVtabRange", "COMPU_VTAB_RANGE", True),
            *** Element("Frame", "FRAME", False),
            Element("Function", "FUNCTION", True),
            Element("Group", "GROUP", True),
            Element("IfData", "IF_DATA", True),
    Element("Instance", "INSTANCE", True),
            Element("Measurement", "MEASUREMENT", True),
            *** Element("ModCommon", "MOD_COMMON", False),
            *** Element("ModPar", "MOD_PAR", False),
            Element("RecordLayout", "RECORD_LAYOUT", True),
            Element("Transformer", "TRANSFORMER", True),
    Element("TypedefAxis", "TYPEDEF_AXIS", True),
    Element("TypedefCharacteristic", "TYPEDEF_CHARACTERISTIC", True),
    Element("TypedefMeasurement", "TYPEDEF_MEASUREMENT", True),
    Element("TypedefStructure", "TYPEDEF_STRUCTURE", True),
            Element("Unit", "UNIT", True),
            Element("UserRights", "USER_RIGHTS", True),
            *** Element("VariantCoding", "VARIANT_CODING", False),
    """

    session: Any = field(repr=False)
    module: model.Module = field(repr=False)
    name: str
    longIdentifier: str
    axis_pts: FilteredList[AxisPts]
    blob: FilteredList[Blob]
    characteristic: FilteredList[Characteristic]
    compu_method: FilteredList[CompuMethod]
    compu_tab: FilteredList[CompuTab]
    compu_tab_verb: FilteredList[CompuTabVerb]
    compu_tab_verb_ranges: FilteredList[CompuTabVerbRanges]
    frame: FilteredList[Frame]
    function: FilteredList[Function]
    group: FilteredList[Group]
    if_data: List[Dict[str, Any]]
    measurement: FilteredList[Measurement]
    mod_common: Optional[ModCommon]
    mod_par: Optional[ModPar]
    record_layout: FilteredList[RecordLayout]
    transformer: FilteredList[Transformer]
    unit: FilteredList[Unit]
    user_rights: FilteredList[UserRights]
    variant_coding: Optional[VariantCoding]

    def __init__(self, session, name: Optional[str] = None):
        self.session = session
        if name is not None:
            self.module = self.session.query(model.Module).filter(model.Module.name == name).first()
        else:
            self.module = self.session.query(model.Module).first()
        self.name = self.module.name
        self.longIdentifier = self.module.longIdentifier

        self.axis_pts = FilteredList(self.session, self.module.axis_pts, AxisPts)
        self.blob = FilteredList(self.session, self.module.blob, Blob)

        self.characteristic = FilteredList(self.session, self.module.characteristic, Characteristic)
        self.compu_method = FilteredList(self.session, self.module.compu_method, CompuMethod)
        self.compu_tab = FilteredList(self.session, self.module.compu_tab, CompuTab)
        self.compu_tab_verb = FilteredList(self.session, self.module.compu_vtab, CompuTabVerb)
        self.compu_tab_verb_ranges = FilteredList(self.session, self.module.compu_vtab_range, CompuTabVerbRanges)

        self.frame = FilteredList(self.session, self.module.frame, Frame)
        self.function = FilteredList(self.session, self.module.function, Function)
        self.group = FilteredList(self.session, self.module.group, Group, "groupName")
        self.if_data = self.session.parse_ifdata(self.module.if_data)

        self.measurement = FilteredList(self.session, self.module.measurement, Measurement)
        self.mod_common = ModCommon.get(self.session, self.name, module_name=self.module.name)
        self.mod_par = ModPar.get(self.session, self.name, module_name=self.module.name)

        self.record_layout = FilteredList(self.session, self.module.record_layout, RecordLayout)
        self.transformer = FilteredList(self.session, self.module.transformer, Transformer)

        self.typedef_structure = FilteredList(self.session, self.module.typedef_structure, TypedefStructure)

        self.unit = FilteredList(self.session, self.module.unit, Unit)
        self.user_rights = FilteredList(self.session, self.module.user_rights, UserRights, "userLevelId")

        self.variant_coding = VariantCoding.get(self.session, module_name=self.module.name)


@dataclass
class Project:
    """"""

    session: Any = field(repr=False)
    project: model.Project = field(repr=False)
    name: str
    longIdentifier: str
    comment: Optional[str]
    projectNumber: Optional[str]
    version: Optional[str]
    module: List[Module]

    def __init__(self, session, file_name: str = ""):
        self.session = session
        project = session.query(model.Project).first()
        self.project = project
        self.name = project.name
        self.longIdentifier = project.longIdentifier
        if project.header:
            self.comment = project.header.comment
            if project.header.project_no:
                self.projectNumber = project.header.project_no.projectNumber
            else:
                self.projectNumber = None
            if project.header.version:
                self.version = project.header.version.versionIdentifier
            else:
                self.version = None
        else:
            self.comment = None
            self.projectNumber = None
            self.version = None
        self.module = []
        for mod in project.module:
            self.module.append(Module(self.session, mod.name))
