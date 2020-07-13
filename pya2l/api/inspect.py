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


class Measurement:
    """Convenient access (read-only) to MEASUREMENT objects.

    Parameters
    ----------
    session: Sqlite3 session object

    name: str
        name of one existing MEASUREMENT object.

    Attributes
    ----------
    measurement
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

    arraySize: int
        If not `None`, Measurement is an one dimensional array; higher order objects are using :attr:`matrixDim`.

    bitMask: int
        Mask out bits.

    bitOperation: dict
        - left_shift: int
        - right_shift: int
        - sign_extend: bool

        perform `<<` and `>>` operations.

    byteOrder: ["LITTLE_ENDIAN" | "BIG_ENDIAN" | "MSB_LAST" | "MSB_FIRST"]

    discrete: bool
        If True, value should not be interpolated.

    displayIdentifier: str
        Can be used as a display name (alternative to the `name` attribute).

    ecuAddress: int
        Address of the measurement in the memory of the CU.

    ecuAddressExtension: int
        Additional address information, e.g. paging.

    errorMask: int
        Mask out bits  which indicate that the value is in error.

    format: str
        C printf like format string.

    functionList: list of strings.
        Used to specify a list of 'functions' to which this measurement object has been allocated.

    layout: ["ROW_DIR" | "COLUMN_DIR"]
        Describes the layout of a multi-dimensional measurement array.

    matrixDim: dict
        - x: int
        - y: int
        - z: int

        Shows the size and dimension of a multidimensional measurement.

    maxRefresh: dict
        - scalingUnit: int
            basic scaling unit (s. `Table Codes for scaling (CSE)`)

        - rate: int
            the maximum refresh rate of the concerning measurement object in the control unit.

    physUnit: str
        Physical unit for Measurement.

    readWrite: bool
        if True, mark this measurement object as writeable.

    refMemorySegment: str
        Reference to the memory segment which is needed if the address is not unique.

    symbolLink: dict
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

    def __init__(self, session, name: str):
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
        result = {}
        if bit_op is not None:
            if bit_op.left_shift is None:
                result['left_shift'] = 0
            else:
                result['left_shift'] = bit_op.left_shift.bitcount
            if bit_op.right_shift is None:
                result['right_shift'] = 0
            else:
                result['right_shift'] = bit_op.right_shift.bitcount
            result['sign_extend'] = False if bit_op.sign_extend is None else True
        return result

    @staticmethod
    def _dissect_matrix_dim(matrix_dim):
        result = {}
        if matrix_dim is not None:
            result["x"] = matrix_dim.xDim
            result["y"] = matrix_dim.yDim
            result["z"] = matrix_dim.zDim
        return result

    @staticmethod
    def _dissect_max_refresh(max_ref):
        result = {}
        if max_ref is not None:
            result["scalingUnit"] = max_ref.scalingUnit
            result["rate"] = max_ref.rate
        return result

    @staticmethod
    def _dissect_symbol_link(sym_link):
        result = {}
        if sym_link is not None:
            result["symbolName"] = sym_link.symbolName
            result["offset"] = sym_link.offset
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
