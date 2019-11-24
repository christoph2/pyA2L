#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__="""
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2019 by Christoph Schueler <github.com/Christoph2,
                                        cpu12.gems@googlemail.com>

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

from functools import partial
import mmap
import re
import sqlite3

from sqlalchemy import (MetaData, schema, types, orm, event,
    create_engine, Column, ForeignKey, ForeignKeyConstraint, func,
    PassiveDefault, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declared_attr, as_declarative
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.orm import relationship, backref
from sqlalchemy.engine import Engine
from sqlalchemy.sql import exists

from pya2l.utils import SingletonBase

DB_EXTENSION    = "a2ldb"

CACHE_SIZE      = 4 # MB
PAGE_SIZE       = mmap.PAGESIZE


class MULTIPLE(SingletonBase): pass
class Uint(SingletonBase): pass
class Int(SingletonBase): pass
class Ulong(SingletonBase): pass
class Long(SingletonBase): pass
class Float(SingletonBase): pass
class String(SingletonBase): pass
class Enum(SingletonBase): pass
class Ident(SingletonBase): pass

class Datatype(SingletonBase):
    enum_values = ('UBYTE', 'SBYTE', 'UWORD', 'SWORD', 'ULONG', 'SLONG',
        'A_UINT64', 'A_INT64', 'FLOAT32_IEEE' ,'FLOAT64_IEEE'
    )

class Datasize(SingletonBase):
    enum_values = ('BYTE', 'WORD', 'LONG')

class Addrtype(SingletonBase):
    enum_values = ('PBYTE', 'PWORD', 'PLONG', 'DIRECT')

class Byteorder(SingletonBase):
    enum_values = ('LITTLE_ENDIAN', 'BIG_ENDIAN', 'MSB_LAST', 'MSB_FIRST')

class Indexorder(SingletonBase):
    enum_values = ('INDEX_INCR', 'INDEX_DECR')

class Parameter(object):
    """
    """
    def __init__(self, name, type_, multiple):
        self._name = name
        self._type = type_
        self._multiple = multiple

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def multiple(self):
        return self._multiple

    def __repr__(self):
        return "{}('{}' {} {})".format(self.__class__.__name__, self.name, self.type, "MULTIPLE" if self.multiple else "")

    __str__ = __repr__


class Element(object):
    """
    """
    def __init__(self, name, keyword_name, multiple):
        self._name = name
        self._keyword_name = keyword_name
        self._multiple = multiple

    @property
    def name(self):
        return self._name

    @property
    def keyword_name(self):
        return self._keyword_name

    @property
    def multiple(self):
        return self._multiple

    def __repr__(self):
        return "{}('{}' {} {})".format(self.__class__.__name__, self.name, self.keyword_name, "MULTIPLE" if self.multiple else "")

    __str__ = __repr__


def calculateCacheSize(value):
    return -(value // PAGE_SIZE)

def regexer(expr, value):
    return re.match(expr, value, re.UNICODE) is not None


@event.listens_for(Engine, "connect")
def set_sqlite3_pragmas(dbapi_connection, connection_record):
    dbapi_connection.create_function("REGEXP", 2, regexer)
    cursor = dbapi_connection.cursor()
    #cursor.execute("PRAGMA jornal_mode=WAL")
    cursor.execute("PRAGMA FOREIGN_KEYS=ON")
    cursor.execute("PRAGMA PAGE_SIZE={}".format(PAGE_SIZE))
    cursor.execute("PRAGMA CACHE_SIZE={}".format(calculateCacheSize(CACHE_SIZE * 1024 * 1024)))
    cursor.execute("PRAGMA SYNCHRONOUS=OFF") # FULL
    cursor.execute("PRAGMA LOCKING_MODE=EXCLUSIVE") # NORMAL
    cursor.execute("PRAGMA TEMP_STORE=MEMORY")  # FILE
    cursor.close()

@as_declarative()
class Base(object):

    rid = Column("rid", types.Integer, primary_key = True)

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    def __repr__(self):
        columns = [c.name for c in self.__class__.__table__.c]
        result = []
        for name, value in [(n, getattr(self, n)) for n in columns if not n.startswith("_")]:
            if isinstance(value, str):
                result.append("{} = '{}'".format(name, value))
            else:
                result.append("{} = {}".format(name, value))
        return "{}({})".format(self.__class__.__name__, ", ".join(result))

def StdFloat(default = 0.0):
    return Column(types.Float, default = default, nullable = False)

def StdShort(default = 0, primary_key = False, unique = False):
    return Column(types.Integer, default = default, nullable = False,
        primary_key = primary_key, unique = unique,
        #CheckClause('BETWEEN (-32768, 32767)')
    )

def StdUShort(default = 0, primary_key = False, unique = False):
    return Column(types.Integer, default = default, nullable = False,
        primary_key = primary_key, unique = unique,
        #CheckClause('BETWEEN (0, 65535)')
    )

def StdLong(default = 0, primary_key = False, unique = False):
    return Column(types.Integer, default = default, nullable = False,
        primary_key = primary_key, unique = unique,
        #CheckClause('BETWEEN (-2147483648, 2147483647)')
    )

def StdULong(default = 0, primary_key = False, unique = False):
    return Column(types.Integer, default = default, nullable = False,
        primary_key = primary_key, unique = unique,
        #CheckClause('BETWEEN (0, 4294967295)')
    )

def StdString(default = 0, primary_key = False, unique = False):
    return Column(types.VARCHAR(256), default = default, nullable = False,
        primary_key = primary_key, unique = unique,
    )

def StdIdent(default = 0, primary_key = False, unique = False):
    return Column(types.VARCHAR(1025), default = default, nullable = False,
        primary_key = primary_key, unique = unique,
    )


class DefCharacteristicIdentifiers(Base):

    __tablename__ = "def_characteristic_identifiers"

    dci_rid = Column(types.Integer, ForeignKey("def_characteristic.rid"))
    identifier = StdIdent()

    def __init__(self, identifier):
        self.identifier = identifier

class OutMeasurementIdentifiers(Base):

    __tablename__ = "out_measurement_identifiers"

    om_rid = Column(types.Integer, ForeignKey("out_measurement.rid"))
    identifier = StdIdent()

    def __init__(self, identifier):
        self.identifier = identifier

class InMeasurementIdentifiers(Base):

    __tablename__ = "in_measurement_identifiers"

    im_rid = Column(types.Integer, ForeignKey("in_measurement.rid"))
    identifier = StdIdent()

    def __init__(self, identifier):
        self.identifier = identifier

class LocMeasurementIdentifiers(Base):

    __tablename__ = "loc_measurement_identifiers"

    lm_rid = Column(types.Integer, ForeignKey("loc_measurement.rid"))
    identifier = StdIdent()

    def __init__(self, identifier):
        self.identifier = identifier

class RefMeasurementIdentifiers(Base):

    __tablename__ = "ref_measurement_identifiers"

    rm_rid = Column(types.Integer, ForeignKey("ref_measurement.rid"))
    identifier = StdIdent()

    def __init__(self, identifier):
        self.identifier = identifier

class FrameMeasurementIdentifiers(Base):

    __tablename__ = "frame_measurement_identifiers"

    rm_rid = Column(types.Integer, ForeignKey("frame_measurement.rid"))
    identifier = StdIdent()

    def __init__(self, identifier):
        self.identifier = identifier

class SubGroupIdentifiers(Base):

    __tablename__ = "sub_group_identifiers"

    rm_rid = Column(types.Integer, ForeignKey("sub_group.rid"))
    identifier = StdIdent()

    def __init__(self, identifier):
        self.identifier = identifier

class SubFunctionIdentifiers(Base):

    __tablename__ = "sub_function_identifiers"

    rm_rid = Column(types.Integer, ForeignKey("sub_function.rid"))
    identifier = StdIdent()

    def __init__(self, identifier):
        self.identifier = identifier

class RefGroupIdentifiers(Base):

    __tablename__ = "ref_group_identifiers"

    rm_rid = Column(types.Integer, ForeignKey("ref_group.rid"))
    identifier = StdIdent()

    def __init__(self, identifier):
        self.identifier = identifier

class MapListIdentifiers(Base):

    __tablename__ = "map_list_identifiers"

    rm_rid = Column(types.Integer, ForeignKey("map_list.rid"))
    name = StdIdent()

    def __init__(self, name):
        self.name = name

class VarCharacteristicIdentifiers(Base):

    __tablename__ = "var_characteristic_identifiers"

    rm_rid = Column(types.Integer, ForeignKey("var_characteristic.rid"))
    criterionName = StdIdent()

    def __init__(self, criterionName):
        self.criterionName = criterionName

class VarCriterionIdentifiers(Base):

    __tablename__ = "var_criterion_identifiers"

    rm_rid = Column(types.Integer, ForeignKey("var_criterion.rid"))
    value = StdIdent()

    def __init__(self, value):
        self.value = value

class FunctionListIdentifiers(Base):

    __tablename__ = "function_list_identifiers"

    rm_rid = Column(types.Integer, ForeignKey("functionlist.rid"))
    name = StdIdent()

    def __init__(self, name):
        self.name = name

class RefCharacteristicIdentifiers(Base):

    __tablename__ = "ref_characteristic_identifiers"

    rm_rid = Column(types.Integer, ForeignKey("refcharacteristic.rid"))
    identifier = StdIdent()

    def __init__(self, identifier):
        self.identifier = identifier

class DependentCharacteristicIdentifiers(Base):

    __tablename__ = "dependent_characteristic_identifiers"

    rm_rid = Column(types.Integer, ForeignKey("dependent_characteristic.rid"))
    characteristic = StdIdent()

    def __init__(self, characteristic):
        self.characteristic = characteristic

class VirtualCharacteristicIdentifiers(Base):

    __tablename__ = "virtual_characteristic_identifiers"

    rm_rid = Column(types.Integer, ForeignKey("virtual_characteristic.rid"))
    characteristic = StdIdent()

    def __init__(self, characteristic):
        self.characteristic = characteristic


class CompuTabPair(Base):

    __tablename__ = "compu_tab_pair"

    ct_rid = Column(types.Integer, ForeignKey("compu_tab.rid"))

    inVal = StdFloat()
    outVal = StdFloat()

class CompuVtabPair(Base):

    __tablename__ = "compu_vtab_pair"

    ct_rid = Column(types.Integer, ForeignKey("compu_vtab.rid"))

    inVal = StdFloat()
    outVal = StdString()

class CompuVtabRangeTriple(Base):

    __tablename__ = "compu_vtab_range_triple"

    ct_rid = Column(types.Integer, ForeignKey("compu_vtab_range.rid"))

    inValMin = StdFloat()
    inValMax = StdFloat()
    outVal   = StdString()

class CalHandles(Base):

    __tablename__ = "calhandles"

    ch_rid = Column(types.Integer, ForeignKey("calibration_handle.rid"))
    handle = StdLong()

    def __init__(self, handle):
        self.handle = handle

class VirtualMeasuringChannels(Base):

    __tablename__ = "virtual_measuring_channel"

    vmc_rid = Column(types.Integer, ForeignKey("virtual.rid"))
    measuringChannel = StdIdent()

    def __init__(self, measuringChannel):
        self.measuringChannel = measuringChannel

class FixAxisParListValues(Base):

    __tablename__ = "fix_axis_par_list_value"

    faplv_rid = Column(types.Integer, ForeignKey("fix_axis_par_list.rid"))
    axisPts_Value = StdFloat()

    def __init__(self, axisPts_Value):
        self.axisPts_Value = axisPts_Value


class VarAddressValues(Base):

    __tablename__ = "var_address_values"

    va_rid = Column(types.Integer, ForeignKey("var_address.rid"))
    address = StdULong()

    def __init__(self, address):
        self.address = address

class AnnotationTextValues(Base):

    __tablename__ = "annotation_text_values"

    at_rid = Column(types.Integer, ForeignKey("annotation_text.rid"))
    text = StdString()

    def __init__(self, text):
        self.text = text

class FunctionListValues(Base):

    __tablename__ = "function_list_values"

    flv_rid = Column(types.Integer, ForeignKey("functionlist.rid"))
    name = StdString()

    def __init__(self, name):
        self.name = name


class VarForbiddedCombPair(Base):

    __tablename__ = "var_forbidden_comb_pair"

    vfc_rid = Column(types.Integer, ForeignKey("var_forbidden_comb.rid"))

    criterionName = StdIdent()
    criterionValue = StdIdent()

class AlignmentByteAssociation(Base):

    __tablename__ = "alignment_byte_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class AlignmentByte(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("alignment_byte_association.rid"))
    association = relationship("AlignmentByteAssociation", backref="alignment_byte")
    parent = association_proxy("association", "parent")

    alignmentBorder = StdUShort()

    __required_parameters__ = (
        Parameter("alignmentBorder", Uint, False),
    )

    __optional_elements__ = ( )

class HasAlignmentBytes(object):

    @declared_attr
    def alignment_byte_association_id(cls):
        return Column(types.Integer, ForeignKey("alignment_byte_association.rid"))

    @declared_attr
    def alignment_byte_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sAlignmentByteAssociation" % name, (AlignmentByteAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.alignment_byte = association_proxy(
            "alignment_byte_association",
            "alignment_byte",
            creator = lambda alignment_byte: assoc_cls(alignment_byte = alignment_byte),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class AlignmentFloat32IeeeAssociation(Base):

    __tablename__ = "alignment_float32_ieee_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class AlignmentFloat32Ieee(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("alignment_float32_ieee_association.rid"))
    association = relationship("AlignmentFloat32IeeeAssociation", backref="alignment_float32_ieee")
    parent = association_proxy("association", "parent")

    alignmentBorder = StdUShort()

    __required_parameters__ = (
        Parameter("alignmentBorder", Uint, False),
    )

    __optional_elements__ = ( )

class HasAlignmentFloat32Ieees(object):

    @declared_attr
    def alignment_float32_ieee_association_id(cls):
        return Column(types.Integer, ForeignKey("alignment_float32_ieee_association.rid"))

    @declared_attr
    def alignment_float32_ieee_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sAlignmentFloat32IeeeAssociation" % name, (AlignmentFloat32IeeeAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.alignment_float32_ieee = association_proxy(
            "alignment_float32_ieee_association",
            "alignment_float32_ieee",
            creator = lambda alignment_float32_ieee: assoc_cls(alignment_float32_ieee = alignment_float32_ieee),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class AlignmentFloat64IeeeAssociation(Base):

    __tablename__ = "alignment_float64_ieee_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class AlignmentFloat64Ieee(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("alignment_float64_ieee_association.rid"))
    association = relationship("AlignmentFloat64IeeeAssociation", backref="alignment_float64_ieee")
    parent = association_proxy("association", "parent")

    alignmentBorder = StdUShort()

    __required_parameters__ = (
        Parameter("alignmentBorder", Uint, False),
    )

    __optional_elements__ = ( )

class HasAlignmentFloat64Ieees(object):

    @declared_attr
    def alignment_float64_ieee_association_id(cls):
        return Column(types.Integer, ForeignKey("alignment_float64_ieee_association.rid"))

    @declared_attr
    def alignment_float64_ieee_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sAlignmentFloat64IeeeAssociation" % name, (AlignmentFloat64IeeeAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.alignment_float64_ieee = association_proxy(
            "alignment_float64_ieee_association",
            "alignment_float64_ieee",
            creator = lambda alignment_float64_ieee: assoc_cls(alignment_float64_ieee = alignment_float64_ieee),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class AlignmentInt64Association(Base):

    __tablename__ = "alignment_int64_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class AlignmentInt64(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("alignment_int64_association.rid"))
    association = relationship("AlignmentInt64Association", backref="alignment_int64")
    parent = association_proxy("association", "parent")

    alignmentBorder = StdUShort()

    __required_parameters__ = (
        Parameter("alignmentBorder", Uint, False),
    )

    __optional_elements__ = ( )

class HasAlignmentInt64s(object):

    @declared_attr
    def alignment_int64_association_id(cls):
        return Column(types.Integer, ForeignKey("alignment_int64_association.rid"))

    @declared_attr
    def alignment_int64_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sAlignmentInt64Association" % name, (AlignmentInt64Association,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.alignment_int64 = association_proxy(
            "alignment_int64_association",
            "alignment_int64",
            creator = lambda alignment_int64: assoc_cls(alignment_int64 = alignment_int64),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class AlignmentLongAssociation(Base):

    __tablename__ = "alignment_long_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class AlignmentLong(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("alignment_long_association.rid"))
    association = relationship("AlignmentLongAssociation", backref="alignment_long")
    parent = association_proxy("association", "parent")

    alignmentBorder = StdUShort()

    __required_parameters__ = (
        Parameter("alignmentBorder", Uint, False),
    )

    __optional_elements__ = ( )

class HasAlignmentLongs(object):

    @declared_attr
    def alignment_long_association_id(cls):
        return Column(types.Integer, ForeignKey("alignment_long_association.rid"))

    @declared_attr
    def alignment_long_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sAlignmentLongAssociation" % name, (AlignmentLongAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.alignment_long = association_proxy(
            "alignment_long_association",
            "alignment_long",
            creator = lambda alignment_long: assoc_cls(alignment_long = alignment_long),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class AlignmentWordAssociation(Base):

    __tablename__ = "alignment_word_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class AlignmentWord(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("alignment_word_association.rid"))
    association = relationship("AlignmentWordAssociation", backref="alignment_word")
    parent = association_proxy("association", "parent")

    alignmentBorder = StdUShort()

    __required_parameters__ = (
        Parameter("alignmentBorder", Uint, False),
    )

    __optional_elements__ = ( )

class HasAlignmentWords(object):

    @declared_attr
    def alignment_word_association_id(cls):
        return Column(types.Integer, ForeignKey("alignment_word_association.rid"))

    @declared_attr
    def alignment_word_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sAlignmentWordAssociation" % name, (AlignmentWordAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.alignment_word = association_proxy(
            "alignment_word_association",
            "alignment_word",
            creator = lambda alignment_word: assoc_cls(alignment_word = alignment_word),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class AnnotationAssociation(Base):

    __tablename__ = "annotation_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class Annotation(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("annotation_association.rid"))
    association = relationship("AnnotationAssociation", backref="annotation")
    parent = association_proxy("association", "parent")

    __required_parameters__ = ( )

    __optional_elements__ = (
        Element("AnnotationLabel", "ANNOTATION_LABEL", False),
        Element("AnnotationOrigin", "ANNOTATION_ORIGIN", False),
        Element("AnnotationText", "ANNOTATION_TEXT", False),
    )
    annotation_label = relationship("AnnotationLabel", back_populates = "annotation", uselist = False)
    annotation_origin = relationship("AnnotationOrigin", back_populates = "annotation", uselist = False)
    annotation_text = relationship("AnnotationText", back_populates = "annotation", uselist = False)


class AnnotationLabel(Base):
    """
    """
    __tablename__ = "annotation_label"

    label = StdString()

    __required_parameters__ = (
        Parameter("label", String, False),
    )

    __optional_elements__ = ( )
    _annotation_rid = Column(types.Integer, ForeignKey("annotation.rid"))
    annotation = relationship("Annotation", back_populates = "annotation_label")


class AnnotationOrigin(Base):
    """
    """
    __tablename__ = "annotation_origin"

    origin = StdString()

    __required_parameters__ = (
        Parameter("origin", String, False),
    )

    __optional_elements__ = ( )
    _annotation_rid = Column(types.Integer, ForeignKey("annotation.rid"))
    annotation = relationship("Annotation", back_populates = "annotation_origin")


class AnnotationText(Base):
    """
    """
    __tablename__ = "annotation_text"
    _text = relationship("AnnotationTextValues", backref = "parent")
    text = association_proxy("_text", "text")

    __required_parameters__ = ( )

    __optional_elements__ = ( )
    _annotation_rid = Column(types.Integer, ForeignKey("annotation.rid"))
    annotation = relationship("Annotation", back_populates = "annotation_text")

class HasAnnotations(object):

    @declared_attr
    def annotation_association_id(cls):
        return Column(types.Integer, ForeignKey("annotation_association.rid"))

    @declared_attr
    def annotation_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sAnnotationAssociation" % name, (AnnotationAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.annotation = association_proxy(
            "annotation_association",
            "annotation",
            creator = lambda annotation: assoc_cls(annotation = annotation),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class BitMaskAssociation(Base):

    __tablename__ = "bit_mask_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class BitMask(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("bit_mask_association.rid"))
    association = relationship("BitMaskAssociation", backref="bit_mask")
    parent = association_proxy("association", "parent")

    mask = StdULong()

    __required_parameters__ = (
        Parameter("mask", Ulong, False),
    )

    __optional_elements__ = ( )

class HasBitMasks(object):

    @declared_attr
    def bit_mask_association_id(cls):
        return Column(types.Integer, ForeignKey("bit_mask_association.rid"))

    @declared_attr
    def bit_mask_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sBitMaskAssociation" % name, (BitMaskAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.bit_mask = association_proxy(
            "bit_mask_association",
            "bit_mask",
            creator = lambda bit_mask: assoc_cls(bit_mask = bit_mask),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class ByteOrderAssociation(Base):

    __tablename__ = "byte_order_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class ByteOrder(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("byte_order_association.rid"))
    association = relationship("ByteOrderAssociation", backref="byte_order")
    parent = association_proxy("association", "parent")

    byteOrder = StdString()

    __required_parameters__ = (
        Parameter("byteOrder", Byteorder, False),
    )

    __optional_elements__ = ( )

class HasByteOrders(object):

    @declared_attr
    def byte_order_association_id(cls):
        return Column(types.Integer, ForeignKey("byte_order_association.rid"))

    @declared_attr
    def byte_order_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sByteOrderAssociation" % name, (ByteOrderAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.byte_order = association_proxy(
            "byte_order_association",
            "byte_order",
            creator = lambda byte_order: assoc_cls(byte_order = byte_order),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class CalibrationAccessAssociation(Base):

    __tablename__ = "calibration_access_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class CalibrationAccess(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("calibration_access_association.rid"))
    association = relationship("CalibrationAccessAssociation", backref="calibration_access")
    parent = association_proxy("association", "parent")

    type = StdString()

    __required_parameters__ = (
        Parameter("type", Enum, False),
    )

    __optional_elements__ = ( )

class HasCalibrationAccess(object):

    @declared_attr
    def calibration_access_association_id(cls):
        return Column(types.Integer, ForeignKey("calibration_access_association.rid"))

    @declared_attr
    def calibration_access_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sCalibrationAccessAssociation" % name, (CalibrationAccessAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.calibration_access = association_proxy(
            "calibration_access_association",
            "calibration_access",
            creator = lambda calibration_access: assoc_cls(calibration_access = calibration_access),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class DefaultValueAssociation(Base):

    __tablename__ = "default_value_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class DefaultValue(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("default_value_association.rid"))
    association = relationship("DefaultValueAssociation", backref="default_value")
    parent = association_proxy("association", "parent")

    display_string = StdString()

    __required_parameters__ = (
        Parameter("display_string", String, False),
    )

    __optional_elements__ = ( )

class HasDefaultValues(object):

    @declared_attr
    def default_value_association_id(cls):
        return Column(types.Integer, ForeignKey("default_value_association.rid"))

    @declared_attr
    def default_value_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sDefaultValueAssociation" % name, (DefaultValueAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.default_value = association_proxy(
            "default_value_association",
            "default_value",
            creator = lambda default_value: assoc_cls(default_value = default_value),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class DepositAssociation(Base):

    __tablename__ = "deposit_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class Deposit(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("deposit_association.rid"))
    association = relationship("DepositAssociation", backref="deposit")
    parent = association_proxy("association", "parent")

    mode = StdString()

    __required_parameters__ = (
        Parameter("mode", Enum, False),
    )

    __optional_elements__ = ( )

class HasDeposits(object):

    @declared_attr
    def deposit_association_id(cls):
        return Column(types.Integer, ForeignKey("deposit_association.rid"))

    @declared_attr
    def deposit_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sDepositAssociation" % name, (DepositAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.deposit = association_proxy(
            "deposit_association",
            "deposit",
            creator = lambda deposit: assoc_cls(deposit = deposit),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class DiscreteAssociation(Base):

    __tablename__ = "discrete_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class Discrete(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("discrete_association.rid"))
    association = relationship("DiscreteAssociation", backref="discrete")
    parent = association_proxy("association", "parent")

    __required_parameters__ = ( )

    __optional_elements__ = ( )

class HasDiscretes(object):

    @declared_attr
    def discrete_association_id(cls):
        return Column(types.Integer, ForeignKey("discrete_association.rid"))

    @declared_attr
    def discrete_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sDiscreteAssociation" % name, (DiscreteAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.discrete = association_proxy(
            "discrete_association",
            "discrete",
            creator = lambda discrete: assoc_cls(discrete = discrete),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class DisplayIdentifierAssociation(Base):

    __tablename__ = "display_identifier_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class DisplayIdentifier(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("display_identifier_association.rid"))
    association = relationship("DisplayIdentifierAssociation", backref="display_identifier")
    parent = association_proxy("association", "parent")

    display_name = StdIdent()

    __required_parameters__ = (
        Parameter("display_name", Ident, False),
    )

    __optional_elements__ = ( )

class HasDisplayIdentifiers(object):

    @declared_attr
    def display_identifier_association_id(cls):
        return Column(types.Integer, ForeignKey("display_identifier_association.rid"))

    @declared_attr
    def display_identifier_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sDisplayIdentifierAssociation" % name, (DisplayIdentifierAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.display_identifier = association_proxy(
            "display_identifier_association",
            "display_identifier",
            creator = lambda display_identifier: assoc_cls(display_identifier = display_identifier),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class EcuAddressExtensionAssociation(Base):

    __tablename__ = "ecu_address_extension_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class EcuAddressExtension(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("ecu_address_extension_association.rid"))
    association = relationship("EcuAddressExtensionAssociation", backref="ecu_address_extension")
    parent = association_proxy("association", "parent")

    extension = StdShort()

    __required_parameters__ = (
        Parameter("extension", Int, False),
    )

    __optional_elements__ = ( )

class HasEcuAddressExtensions(object):

    @declared_attr
    def ecu_address_extension_association_id(cls):
        return Column(types.Integer, ForeignKey("ecu_address_extension_association.rid"))

    @declared_attr
    def ecu_address_extension_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sEcuAddressExtensionAssociation" % name, (EcuAddressExtensionAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.ecu_address_extension = association_proxy(
            "ecu_address_extension_association",
            "ecu_address_extension",
            creator = lambda ecu_address_extension: assoc_cls(ecu_address_extension = ecu_address_extension),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class ExtendedLimitsAssociation(Base):

    __tablename__ = "extended_limits_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class ExtendedLimits(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("extended_limits_association.rid"))
    association = relationship("ExtendedLimitsAssociation", backref="extended_limits")
    parent = association_proxy("association", "parent")

    lowerLimit = StdFloat()

    upperLimit = StdFloat()

    __required_parameters__ = (
        Parameter("lowerLimit", Float, False),
        Parameter("upperLimit", Float, False),
    )

    __optional_elements__ = ( )

class HasExtendedLimits(object):

    @declared_attr
    def extended_limits_association_id(cls):
        return Column(types.Integer, ForeignKey("extended_limits_association.rid"))

    @declared_attr
    def extended_limits_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sExtendedLimitsAssociation" % name, (ExtendedLimitsAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.extended_limits = association_proxy(
            "extended_limits_association",
            "extended_limits",
            creator = lambda extended_limits: assoc_cls(extended_limits = extended_limits),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class FormatAssociation(Base):

    __tablename__ = "format_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class Format(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("format_association.rid"))
    association = relationship("FormatAssociation", backref="format")
    parent = association_proxy("association", "parent")

    formatString = StdString()

    __required_parameters__ = (
        Parameter("formatString", String, False),
    )

    __optional_elements__ = ( )

class HasFormats(object):

    @declared_attr
    def format_association_id(cls):
        return Column(types.Integer, ForeignKey("format_association.rid"))

    @declared_attr
    def format_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sFormatAssociation" % name, (FormatAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.format = association_proxy(
            "format_association",
            "format",
            creator = lambda format: assoc_cls(format = format),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class FunctionListAssociation(Base):

    __tablename__ = "function_list_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class FunctionList(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("function_list_association.rid"))
    association = relationship("FunctionListAssociation", backref="function_list")
    parent = association_proxy("association", "parent")
    _name = relationship("FunctionListValues", backref = "parent")
    name = association_proxy("_name", "name")

    __required_parameters__ = ( )

    __optional_elements__ = ( )

class HasFunctionLists(object):

    @declared_attr
    def function_list_association_id(cls):
        return Column(types.Integer, ForeignKey("function_list_association.rid"))

    @declared_attr
    def function_list_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sFunctionListAssociation" % name, (FunctionListAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.function_list = association_proxy(
            "function_list_association",
            "function_list",
            creator = lambda function_list: assoc_cls(function_list = function_list),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class GuardRailsAssociation(Base):

    __tablename__ = "guard_rails_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class GuardRails(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("guard_rails_association.rid"))
    association = relationship("GuardRailsAssociation", backref="guard_rails")
    parent = association_proxy("association", "parent")

    __required_parameters__ = ( )

    __optional_elements__ = ( )

class HasGuardRails(object):

    @declared_attr
    def guard_rails_association_id(cls):
        return Column(types.Integer, ForeignKey("guard_rails_association.rid"))

    @declared_attr
    def guard_rails_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sGuardRailsAssociation" % name, (GuardRailsAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.guard_rails = association_proxy(
            "guard_rails_association",
            "guard_rails",
            creator = lambda guard_rails: assoc_cls(guard_rails = guard_rails),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class IfDataAssociation(Base):

    __tablename__ = "if_data_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class IfData(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("if_data_association.rid"))
    association = relationship("IfDataAssociation", backref="if_data")
    parent = association_proxy("association", "parent")

    name = StdIdent()

    __required_parameters__ = (
        Parameter("name", Ident, False),
    )

    __optional_elements__ = ( )

class HasIfDatas(object):

    @declared_attr
    def if_data_association_id(cls):
        return Column(types.Integer, ForeignKey("if_data_association.rid"))

    @declared_attr
    def if_data_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sIfDataAssociation" % name, (IfDataAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.if_data = association_proxy(
            "if_data_association",
            "if_data",
            creator = lambda if_data: assoc_cls(if_data = if_data),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class MatrixDimAssociation(Base):

    __tablename__ = "matrix_dim_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class MatrixDim(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("matrix_dim_association.rid"))
    association = relationship("MatrixDimAssociation", backref="matrix_dim")
    parent = association_proxy("association", "parent")

    xDim = StdUShort()

    yDim = StdUShort()

    zDim = StdUShort()

    __required_parameters__ = (
        Parameter("xDim", Uint, False),
        Parameter("yDim", Uint, False),
        Parameter("zDim", Uint, False),
    )

    __optional_elements__ = ( )

class HasMatrixDims(object):

    @declared_attr
    def matrix_dim_association_id(cls):
        return Column(types.Integer, ForeignKey("matrix_dim_association.rid"))

    @declared_attr
    def matrix_dim_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sMatrixDimAssociation" % name, (MatrixDimAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.matrix_dim = association_proxy(
            "matrix_dim_association",
            "matrix_dim",
            creator = lambda matrix_dim: assoc_cls(matrix_dim = matrix_dim),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class MaxRefreshAssociation(Base):

    __tablename__ = "max_refresh_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class MaxRefresh(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("max_refresh_association.rid"))
    association = relationship("MaxRefreshAssociation", backref="max_refresh")
    parent = association_proxy("association", "parent")

    scalingUnit = StdUShort()

    rate = StdULong()

    __required_parameters__ = (
        Parameter("scalingUnit", Uint, False),
        Parameter("rate", Ulong, False),
    )

    __optional_elements__ = ( )

class HasMaxRefreshs(object):

    @declared_attr
    def max_refresh_association_id(cls):
        return Column(types.Integer, ForeignKey("max_refresh_association.rid"))

    @declared_attr
    def max_refresh_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sMaxRefreshAssociation" % name, (MaxRefreshAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.max_refresh = association_proxy(
            "max_refresh_association",
            "max_refresh",
            creator = lambda max_refresh: assoc_cls(max_refresh = max_refresh),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class MonotonyAssociation(Base):

    __tablename__ = "monotony_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class Monotony(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("monotony_association.rid"))
    association = relationship("MonotonyAssociation", backref="monotony")
    parent = association_proxy("association", "parent")

    monotony = StdString()

    __required_parameters__ = (
        Parameter("monotony", Enum, False),
    )

    __optional_elements__ = ( )

class HasMonotonys(object):

    @declared_attr
    def monotony_association_id(cls):
        return Column(types.Integer, ForeignKey("monotony_association.rid"))

    @declared_attr
    def monotony_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sMonotonyAssociation" % name, (MonotonyAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.monotony = association_proxy(
            "monotony_association",
            "monotony",
            creator = lambda monotony: assoc_cls(monotony = monotony),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class PhysUnitAssociation(Base):

    __tablename__ = "phys_unit_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class PhysUnit(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("phys_unit_association.rid"))
    association = relationship("PhysUnitAssociation", backref="phys_unit")
    parent = association_proxy("association", "parent")

    unit = StdString()

    __required_parameters__ = (
        Parameter("unit", String, False),
    )

    __optional_elements__ = ( )

class HasPhysUnits(object):

    @declared_attr
    def phys_unit_association_id(cls):
        return Column(types.Integer, ForeignKey("phys_unit_association.rid"))

    @declared_attr
    def phys_unit_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sPhysUnitAssociation" % name, (PhysUnitAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.phys_unit = association_proxy(
            "phys_unit_association",
            "phys_unit",
            creator = lambda phys_unit: assoc_cls(phys_unit = phys_unit),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class ReadOnlyAssociation(Base):

    __tablename__ = "read_only_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class ReadOnly(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("read_only_association.rid"))
    association = relationship("ReadOnlyAssociation", backref="read_only")
    parent = association_proxy("association", "parent")

    __required_parameters__ = ( )

    __optional_elements__ = ( )

class HasReadOnlys(object):

    @declared_attr
    def read_only_association_id(cls):
        return Column(types.Integer, ForeignKey("read_only_association.rid"))

    @declared_attr
    def read_only_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sReadOnlyAssociation" % name, (ReadOnlyAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.read_only = association_proxy(
            "read_only_association",
            "read_only",
            creator = lambda read_only: assoc_cls(read_only = read_only),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class RefCharacteristicAssociation(Base):

    __tablename__ = "ref_characteristic_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class RefCharacteristic(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("ref_characteristic_association.rid"))
    association = relationship("RefCharacteristicAssociation", backref="ref_characteristic")
    parent = association_proxy("association", "parent")

    _identifier = relationship("RefCharacteristicIdentifiers", backref = "parent")
    identifier = association_proxy("_identifier", "identifier")

    __required_parameters__ = (
        Parameter("identifier", Ident, True),
    )

    __optional_elements__ = ( )

class HasRefCharacteristics(object):

    @declared_attr
    def ref_characteristic_association_id(cls):
        return Column(types.Integer, ForeignKey("ref_characteristic_association.rid"))

    @declared_attr
    def ref_characteristic_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sRefCharacteristicAssociation" % name, (RefCharacteristicAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.ref_characteristic = association_proxy(
            "ref_characteristic_association",
            "ref_characteristic",
            creator = lambda ref_characteristic: assoc_cls(ref_characteristic = ref_characteristic),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class RefMemorySegmentAssociation(Base):

    __tablename__ = "ref_memory_segment_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class RefMemorySegment(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("ref_memory_segment_association.rid"))
    association = relationship("RefMemorySegmentAssociation", backref="ref_memory_segment")
    parent = association_proxy("association", "parent")

    name = StdIdent()

    __required_parameters__ = (
        Parameter("name", Ident, False),
    )

    __optional_elements__ = ( )

class HasRefMemorySegments(object):

    @declared_attr
    def ref_memory_segment_association_id(cls):
        return Column(types.Integer, ForeignKey("ref_memory_segment_association.rid"))

    @declared_attr
    def ref_memory_segment_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sRefMemorySegmentAssociation" % name, (RefMemorySegmentAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.ref_memory_segment = association_proxy(
            "ref_memory_segment_association",
            "ref_memory_segment",
            creator = lambda ref_memory_segment: assoc_cls(ref_memory_segment = ref_memory_segment),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class RefUnitAssociation(Base):

    __tablename__ = "ref_unit_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class RefUnit(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("ref_unit_association.rid"))
    association = relationship("RefUnitAssociation", backref="ref_unit")
    parent = association_proxy("association", "parent")

    unit = StdIdent()

    __required_parameters__ = (
        Parameter("unit", Ident, False),
    )

    __optional_elements__ = ( )

class HasRefUnits(object):

    @declared_attr
    def ref_unit_association_id(cls):
        return Column(types.Integer, ForeignKey("ref_unit_association.rid"))

    @declared_attr
    def ref_unit_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sRefUnitAssociation" % name, (RefUnitAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.ref_unit = association_proxy(
            "ref_unit_association",
            "ref_unit",
            creator = lambda ref_unit: assoc_cls(ref_unit = ref_unit),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class StepSizeAssociation(Base):

    __tablename__ = "step_size_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class StepSize(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("step_size_association.rid"))
    association = relationship("StepSizeAssociation", backref="step_size")
    parent = association_proxy("association", "parent")

    stepSize = StdFloat()

    __required_parameters__ = (
        Parameter("stepSize", Float, False),
    )

    __optional_elements__ = ( )

class HasStepSizes(object):

    @declared_attr
    def step_size_association_id(cls):
        return Column(types.Integer, ForeignKey("step_size_association.rid"))

    @declared_attr
    def step_size_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sStepSizeAssociation" % name, (StepSizeAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.step_size = association_proxy(
            "step_size_association",
            "step_size",
            creator = lambda step_size: assoc_cls(step_size = step_size),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class SymbolLinkAssociation(Base):

    __tablename__ = "symbol_link_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class SymbolLink(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("symbol_link_association.rid"))
    association = relationship("SymbolLinkAssociation", backref="symbol_link")
    parent = association_proxy("association", "parent")

    symbolName = StdString()

    offset = StdLong()

    __required_parameters__ = (
        Parameter("symbolName", String, False),
        Parameter("offset", Long, False),
    )

    __optional_elements__ = ( )

class HasSymbolLinks(object):

    @declared_attr
    def symbol_link_association_id(cls):
        return Column(types.Integer, ForeignKey("symbol_link_association.rid"))

    @declared_attr
    def symbol_link_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sSymbolLinkAssociation" % name, (SymbolLinkAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.symbol_link = association_proxy(
            "symbol_link_association",
            "symbol_link",
            creator = lambda symbol_link: assoc_cls(symbol_link = symbol_link),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )

class VersionAssociation(Base):

    __tablename__ = "version_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class Version(Base):
    """
    """
    _association_id = Column(types.Integer, ForeignKey("version_association.rid"))
    association = relationship("VersionAssociation", backref="version")
    parent = association_proxy("association", "parent")

    versionIdentifier = StdString()

    __required_parameters__ = (
        Parameter("versionIdentifier", String, False),
    )

    __optional_elements__ = ( )

class HasVersions(object):

    @declared_attr
    def version_association_id(cls):
        return Column(types.Integer, ForeignKey("version_association.rid"))

    @declared_attr
    def version_association(cls):
        name = cls.__name__
        discriminator = name.lower()

        assoc_cls = type(
            "%sVersionAssociation" % name, (VersionAssociation,),
            dict(
                __tablename__ = None,
                __mapper_args__ = {"polymorphic_identity": discriminator},
            ),
        )

        cls.version = association_proxy(
            "version_association",
            "version",
            creator = lambda version: assoc_cls(version = version),
        )
        return relationship(
            assoc_cls, backref = backref("parent", uselist = False)
        )


class Asap2Version(Base):
    """
    """
    __tablename__ = "asap2_version"

    versionNo = StdUShort()

    upgradeNo = StdUShort()

    __required_parameters__ = (
        Parameter("versionNo", Uint, False),
        Parameter("upgradeNo", Uint, False),
    )

    __optional_elements__ = ( )


class A2mlVersion(Base):
    """
    """
    __tablename__ = "a2ml_version"

    versionNo = StdUShort()

    upgradeNo = StdUShort()

    __required_parameters__ = (
        Parameter("versionNo", Uint, False),
        Parameter("upgradeNo", Uint, False),
    )

    __optional_elements__ = ( )


class Project(Base):
    """
    """
    __tablename__ = "project"

    name = StdIdent()

    longIdentifier = StdString()

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
    )

    __optional_elements__ = (
        Element("Header", "HEADER", False),
        Element("Module", "MODULE", True),
    )
    header = relationship("Header", back_populates = "project", uselist = False)
    modules = relationship("Module", back_populates = "project", uselist = True)


class Header(Base, HasVersions):
    """
    """
    __tablename__ = "header"

    comment = StdString()

    __required_parameters__ = (
        Parameter("comment", String, False),
    )

    __optional_elements__ = (
        Element("ProjectNo", "PROJECT_NO", False),
        Element("Version", "VERSION", False),
    )
    project_no = relationship("ProjectNo", back_populates = "header", uselist = False)
    _project_rid = Column(types.Integer, ForeignKey("project.rid"))
    project = relationship("Project", back_populates = "header")


class ProjectNo(Base):
    """
    """
    __tablename__ = "project_no"

    projectNumber = StdIdent()

    __required_parameters__ = (
        Parameter("projectNumber", Ident, False),
    )

    __optional_elements__ = ( )
    _header_rid = Column(types.Integer, ForeignKey("header.rid"))
    header = relationship("Header", back_populates = "project_no")


class Module(Base, HasIfDatas):
    """
    """
    __tablename__ = "module"

    name = StdIdent()

    longIdentifier = StdString()

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
    )

    __optional_elements__ = (
        Element("A2ml", "A2ML", False),
        Element("AxisPts", "AXIS_PTS", True),
        Element("Characteristic", "CHARACTERISTIC", True),
        Element("CompuMethod", "COMPU_METHOD", True),
        Element("CompuTab", "COMPU_TAB", True),
        Element("CompuVtab", "COMPU_VTAB", True),
        Element("CompuVtabRange", "COMPU_VTAB_RANGE", True),
        Element("Frame", "FRAME", False),
        Element("Function", "FUNCTION", True),
        Element("Group", "GROUP", True),
        Element("IfData", "IF_DATA", True),
        Element("Measurement", "MEASUREMENT", True),
        Element("ModCommon", "MOD_COMMON", False),
        Element("ModPar", "MOD_PAR", False),
        Element("RecordLayout", "RECORD_LAYOUT", True),
        Element("Unit", "UNIT", True),
        Element("UserRights", "USER_RIGHTS", True),
        Element("VariantCoding", "VARIANT_CODING", False),
    )
    a2ml = relationship("A2ml", back_populates = "module", uselist = False)
    axis_pts = relationship("AxisPts", back_populates = "module", uselist = True)
    characteristics = relationship("Characteristic", back_populates = "module", uselist = True)
    compu_methods = relationship("CompuMethod", back_populates = "module", uselist = True)
    compu_tabs = relationship("CompuTab", back_populates = "module", uselist = True)
    compu_vtabs = relationship("CompuVtab", back_populates = "module", uselist = True)
    compu_vtab_ranges = relationship("CompuVtabRange", back_populates = "module", uselist = True)
    frame = relationship("Frame", back_populates = "module", uselist = False)
    functions = relationship("Function", back_populates = "module", uselist = True)
    groups = relationship("Group", back_populates = "module", uselist = True)
    measurements = relationship("Measurement", back_populates = "module", uselist = True)
    mod_common = relationship("ModCommon", back_populates = "module", uselist = False)
    mod_par = relationship("ModPar", back_populates = "module", uselist = False)
    record_layouts = relationship("RecordLayout", back_populates = "module", uselist = True)
    units = relationship("Unit", back_populates = "module", uselist = True)
    user_rights = relationship("UserRights", back_populates = "module", uselist = True)
    variant_coding = relationship("VariantCoding", back_populates = "module", uselist = False)
    _project_rid = Column(types.Integer, ForeignKey("project.rid"))
    project = relationship("Project", back_populates = "modules")


class A2ml(Base):
    """
    """
    __tablename__ = "a2ml"

    __required_parameters__ = ( )

    __optional_elements__ = ( )
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "a2ml")


class AxisPts(Base, HasAnnotations, HasByteOrders, HasCalibrationAccess, HasDeposits, HasDisplayIdentifiers, HasEcuAddressExtensions, HasExtendedLimits, HasFormats, HasFunctionLists, HasGuardRails, HasIfDatas, HasMonotonys, HasPhysUnits, HasReadOnlys, HasRefMemorySegments, HasStepSizes, HasSymbolLinks):
    """
    """
    __tablename__ = "axis_pts"

    name = StdIdent()

    longIdentifier = StdString()

    address = StdULong()

    inputQuantity = StdIdent()

    deposit = StdIdent()

    maxDiff = StdFloat()

    conversion = StdIdent()

    maxAxisPoints = StdUShort()

    lowerLimit = StdFloat()

    upperLimit = StdFloat()

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
        Parameter("address", Ulong, False),
        Parameter("inputQuantity", Ident, False),
        Parameter("deposit", Ident, False),
        Parameter("maxDiff", Float, False),
        Parameter("conversion", Ident, False),
        Parameter("maxAxisPoints", Uint, False),
        Parameter("lowerLimit", Float, False),
        Parameter("upperLimit", Float, False),
    )

    __optional_elements__ = (
        Element("Annotation", "ANNOTATION", True),
        Element("ByteOrder", "BYTE_ORDER", False),
        Element("CalibrationAccess", "CALIBRATION_ACCESS", False),
        Element("Deposit", "DEPOSIT", False),
        Element("DisplayIdentifier", "DISPLAY_IDENTIFIER", False),
        Element("EcuAddressExtension", "ECU_ADDRESS_EXTENSION", False),
        Element("ExtendedLimits", "EXTENDED_LIMITS", False),
        Element("Format", "FORMAT", False),
        Element("FunctionList", "FUNCTION_LIST", False),
        Element("GuardRails", "GUARD_RAILS", False),
        Element("IfData", "IF_DATA", True),
        Element("Monotony", "MONOTONY", False),
        Element("PhysUnit", "PHYS_UNIT", False),
        Element("ReadOnly", "READ_ONLY", False),
        Element("RefMemorySegment", "REF_MEMORY_SEGMENT", False),
        Element("StepSize", "STEP_SIZE", False),
        Element("SymbolLink", "SYMBOL_LINK", False),
    )
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "axis_pts")


class Characteristic(Base, HasAnnotations, HasBitMasks, HasByteOrders, HasCalibrationAccess, HasDiscretes, HasDisplayIdentifiers, HasEcuAddressExtensions, HasExtendedLimits, HasFormats, HasFunctionLists, HasGuardRails, HasIfDatas, HasMatrixDims, HasMaxRefreshs, HasPhysUnits, HasReadOnlys, HasRefMemorySegments, HasStepSizes, HasSymbolLinks):
    """
    """
    __tablename__ = "characteristic"

    name = StdIdent()

    longIdentifier = StdString()

    type = StdString()

    address = StdULong()

    deposit = StdIdent()

    maxDiff = StdFloat()

    conversion = StdIdent()

    lowerLimit = StdFloat()

    upperLimit = StdFloat()

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
        Parameter("type", Enum, False),
        Parameter("address", Ulong, False),
        Parameter("deposit", Ident, False),
        Parameter("maxDiff", Float, False),
        Parameter("conversion", Ident, False),
        Parameter("lowerLimit", Float, False),
        Parameter("upperLimit", Float, False),
    )

    __optional_elements__ = (
        Element("Annotation", "ANNOTATION", True),
        Element("AxisDescr", "AXIS_DESCR", True),
        Element("BitMask", "BIT_MASK", False),
        Element("ByteOrder", "BYTE_ORDER", False),
        Element("CalibrationAccess", "CALIBRATION_ACCESS", False),
        Element("ComparisonQuantity", "COMPARISON_QUANTITY", False),
        Element("DependentCharacteristic", "DEPENDENT_CHARACTERISTIC", False),
        Element("Discrete", "DISCRETE", False),
        Element("DisplayIdentifier", "DISPLAY_IDENTIFIER", False),
        Element("EcuAddressExtension", "ECU_ADDRESS_EXTENSION", False),
        Element("ExtendedLimits", "EXTENDED_LIMITS", False),
        Element("Format", "FORMAT", False),
        Element("FunctionList", "FUNCTION_LIST", False),
        Element("GuardRails", "GUARD_RAILS", False),
        Element("IfData", "IF_DATA", True),
        Element("MapList", "MAP_LIST", False),
        Element("MatrixDim", "MATRIX_DIM", False),
        Element("MaxRefresh", "MAX_REFRESH", False),
        Element("Number", "NUMBER", False),
        Element("PhysUnit", "PHYS_UNIT", False),
        Element("ReadOnly", "READ_ONLY", False),
        Element("RefMemorySegment", "REF_MEMORY_SEGMENT", False),
        Element("StepSize", "STEP_SIZE", False),
        Element("SymbolLink", "SYMBOL_LINK", False),
        Element("VirtualCharacteristic", "VIRTUAL_CHARACTERISTIC", False),
    )
    axis_descrs = relationship("AxisDescr", back_populates = "characteristic", uselist = True)
    comparison_quantity = relationship("ComparisonQuantity", back_populates = "characteristic", uselist = False)
    dependent_characteristic = relationship("DependentCharacteristic", back_populates = "characteristic", uselist = False)
    map_list = relationship("MapList", back_populates = "characteristic", uselist = False)
    number = relationship("Number", back_populates = "characteristic", uselist = False)
    virtual_characteristic = relationship("VirtualCharacteristic", back_populates = "characteristic", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "characteristics")


class AxisDescr(Base, HasAnnotations, HasByteOrders, HasDeposits, HasExtendedLimits, HasFormats, HasMonotonys, HasPhysUnits, HasReadOnlys, HasStepSizes):
    """
    """
    __tablename__ = "axis_descr"

    attribute = StdString()

    inputQuantity = StdIdent()

    conversion = StdIdent()

    maxAxisPoints = StdUShort()

    lowerLimit = StdFloat()

    upperLimit = StdFloat()

    __required_parameters__ = (
        Parameter("attribute", Enum, False),
        Parameter("inputQuantity", Ident, False),
        Parameter("conversion", Ident, False),
        Parameter("maxAxisPoints", Uint, False),
        Parameter("lowerLimit", Float, False),
        Parameter("upperLimit", Float, False),
    )

    __optional_elements__ = (
        Element("Annotation", "ANNOTATION", True),
        Element("AxisPtsRef", "AXIS_PTS_REF", False),
        Element("ByteOrder", "BYTE_ORDER", False),
        Element("CurveAxisRef", "CURVE_AXIS_REF", False),
        Element("Deposit", "DEPOSIT", False),
        Element("ExtendedLimits", "EXTENDED_LIMITS", False),
        Element("FixAxisPar", "FIX_AXIS_PAR", False),
        Element("FixAxisParDist", "FIX_AXIS_PAR_DIST", False),
        Element("FixAxisParList", "FIX_AXIS_PAR_LIST", False),
        Element("Format", "FORMAT", False),
        Element("MaxGrad", "MAX_GRAD", False),
        Element("Monotony", "MONOTONY", False),
        Element("PhysUnit", "PHYS_UNIT", False),
        Element("ReadOnly", "READ_ONLY", False),
        Element("StepSize", "STEP_SIZE", False),
    )
    axis_pts_ref = relationship("AxisPtsRef", back_populates = "axis_descr", uselist = False)
    curve_axis_ref = relationship("CurveAxisRef", back_populates = "axis_descr", uselist = False)
    fix_axis_par = relationship("FixAxisPar", back_populates = "axis_descr", uselist = False)
    fix_axis_par_dist = relationship("FixAxisParDist", back_populates = "axis_descr", uselist = False)
    fix_axis_par_list = relationship("FixAxisParList", back_populates = "axis_descr", uselist = False)
    max_grad = relationship("MaxGrad", back_populates = "axis_descr", uselist = False)
    _characteristic_rid = Column(types.Integer, ForeignKey("characteristic.rid"))
    characteristic = relationship("Characteristic", back_populates = "axis_descrs")


class AxisPtsRef(Base):
    """
    """
    __tablename__ = "axis_pts_ref"

    axisPoints = StdIdent()

    __required_parameters__ = (
        Parameter("axisPoints", Ident, False),
    )

    __optional_elements__ = ( )
    _axis_descr_rid = Column(types.Integer, ForeignKey("axis_descr.rid"))
    axis_descr = relationship("AxisDescr", back_populates = "axis_pts_ref")


class CurveAxisRef(Base):
    """
    """
    __tablename__ = "curve_axis_ref"

    curveAxis = StdIdent()

    __required_parameters__ = (
        Parameter("curveAxis", Ident, False),
    )

    __optional_elements__ = ( )
    _axis_descr_rid = Column(types.Integer, ForeignKey("axis_descr.rid"))
    axis_descr = relationship("AxisDescr", back_populates = "curve_axis_ref")


class FixAxisPar(Base):
    """
    """
    __tablename__ = "fix_axis_par"

    offset = StdShort()

    shift = StdShort()

    numberapo = StdUShort()

    __required_parameters__ = (
        Parameter("offset", Int, False),
        Parameter("shift", Int, False),
        Parameter("numberapo", Uint, False),
    )

    __optional_elements__ = ( )
    _axis_descr_rid = Column(types.Integer, ForeignKey("axis_descr.rid"))
    axis_descr = relationship("AxisDescr", back_populates = "fix_axis_par")


class FixAxisParDist(Base):
    """
    """
    __tablename__ = "fix_axis_par_dist"

    offset = StdShort()

    distance = StdShort()

    numberapo = StdUShort()

    __required_parameters__ = (
        Parameter("offset", Int, False),
        Parameter("distance", Int, False),
        Parameter("numberapo", Uint, False),
    )

    __optional_elements__ = ( )
    _axis_descr_rid = Column(types.Integer, ForeignKey("axis_descr.rid"))
    axis_descr = relationship("AxisDescr", back_populates = "fix_axis_par_dist")


class FixAxisParList(Base):
    """
    """
    __tablename__ = "fix_axis_par_list"
    _axisPts_Value = relationship("FixAxisParListValues", backref = "parent")
    axisPts_Value = association_proxy("_axisPts_Value", "axisPts_Value")

    __required_parameters__ = ( )

    __optional_elements__ = ( )
    _axis_descr_rid = Column(types.Integer, ForeignKey("axis_descr.rid"))
    axis_descr = relationship("AxisDescr", back_populates = "fix_axis_par_list")


class MaxGrad(Base):
    """
    """
    __tablename__ = "max_grad"

    maxGradient = StdFloat()

    __required_parameters__ = (
        Parameter("maxGradient", Float, False),
    )

    __optional_elements__ = ( )
    _axis_descr_rid = Column(types.Integer, ForeignKey("axis_descr.rid"))
    axis_descr = relationship("AxisDescr", back_populates = "max_grad")


class ComparisonQuantity(Base):
    """
    """
    __tablename__ = "comparison_quantity"

    name = StdIdent()

    __required_parameters__ = (
        Parameter("name", Ident, False),
    )

    __optional_elements__ = ( )
    _characteristic_rid = Column(types.Integer, ForeignKey("characteristic.rid"))
    characteristic = relationship("Characteristic", back_populates = "comparison_quantity")


class DependentCharacteristic(Base):
    """
    """
    __tablename__ = "dependent_characteristic"

    formula = StdString()

    _characteristic_id = relationship("DependentCharacteristicIdentifiers", backref = "parent")
    characteristic_id = association_proxy("_characteristic_id", "characteristic")

    __required_parameters__ = (
        Parameter("formula", String, False),
        Parameter("characteristic", Ident, True),
    )

    __optional_elements__ = ( )
    _characteristic_rid = Column(types.Integer, ForeignKey("characteristic.rid"))
    characteristic = relationship("Characteristic", back_populates = "dependent_characteristic")


class MapList(Base):
    """
    """
    __tablename__ = "map_list"

    _name = relationship("MapListIdentifiers", backref = "parent")
    name = association_proxy("_name", "name")

    __required_parameters__ = (
        Parameter("name", Ident, True),
    )

    __optional_elements__ = ( )
    _characteristic_rid = Column(types.Integer, ForeignKey("characteristic.rid"))
    characteristic = relationship("Characteristic", back_populates = "map_list")


class Number(Base):
    """
    """
    __tablename__ = "number"

    number = StdUShort()

    __required_parameters__ = (
        Parameter("number", Uint, False),
    )

    __optional_elements__ = ( )
    _characteristic_rid = Column(types.Integer, ForeignKey("characteristic.rid"))
    characteristic = relationship("Characteristic", back_populates = "number")


class VirtualCharacteristic(Base):
    """
    """
    __tablename__ = "virtual_characteristic"

    formula = StdString()

    _characteristic_id = relationship("VirtualCharacteristicIdentifiers", backref = "parent")
    characteristic_id = association_proxy("_characteristic_id", "characteristic")

    __required_parameters__ = (
        Parameter("formula", String, False),
        Parameter("characteristic", Ident, True),
    )

    __optional_elements__ = ( )
    _characteristic_rid = Column(types.Integer, ForeignKey("characteristic.rid"))
    characteristic = relationship("Characteristic", back_populates = "virtual_characteristic")


class CompuMethod(Base, HasRefUnits):
    """
    """
    __tablename__ = "compu_method"

    name = StdIdent()

    longIdentifier = StdString()

    conversionType = StdString()

    format = StdString()

    unit = StdString()

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
        Parameter("conversionType", Enum, False),
        Parameter("format", String, False),
        Parameter("unit", String, False),
    )

    __optional_elements__ = (
        Element("Coeffs", "COEFFS", False),
        Element("CoeffsLinear", "COEFFS_LINEAR", False),
        Element("CompuTabRef", "COMPU_TAB_REF", False),
        Element("Formula", "FORMULA", False),
        Element("RefUnit", "REF_UNIT", False),
        Element("StatusStringRef", "STATUS_STRING_REF", False),
    )
    coeffs = relationship("Coeffs", back_populates = "compu_method", uselist = False)
    coeffs_linear = relationship("CoeffsLinear", back_populates = "compu_method", uselist = False)
    compu_tab_ref = relationship("CompuTabRef", back_populates = "compu_method", uselist = False)
    formula = relationship("Formula", back_populates = "compu_method", uselist = False)
    status_string_ref = relationship("StatusStringRef", back_populates = "compu_method", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "compu_methods")


class Coeffs(Base):
    """
    """
    __tablename__ = "coeffs"

    a = StdFloat()

    b = StdFloat()

    c = StdFloat()

    d = StdFloat()

    e = StdFloat()

    f = StdFloat()

    __required_parameters__ = (
        Parameter("a", Float, False),
        Parameter("b", Float, False),
        Parameter("c", Float, False),
        Parameter("d", Float, False),
        Parameter("e", Float, False),
        Parameter("f", Float, False),
    )

    __optional_elements__ = ( )
    _compu_method_rid = Column(types.Integer, ForeignKey("compu_method.rid"))
    compu_method = relationship("CompuMethod", back_populates = "coeffs")


class CoeffsLinear(Base):
    """
    """
    __tablename__ = "coeffs_linear"

    a = StdFloat()

    b = StdFloat()

    __required_parameters__ = (
        Parameter("a", Float, False),
        Parameter("b", Float, False),
    )

    __optional_elements__ = ( )
    _compu_method_rid = Column(types.Integer, ForeignKey("compu_method.rid"))
    compu_method = relationship("CompuMethod", back_populates = "coeffs_linear")


class CompuTabRef(Base):
    """
    """
    __tablename__ = "compu_tab_ref"

    conversionTable = StdIdent()

    __required_parameters__ = (
        Parameter("conversionTable", Ident, False),
    )

    __optional_elements__ = ( )
    _compu_method_rid = Column(types.Integer, ForeignKey("compu_method.rid"))
    compu_method = relationship("CompuMethod", back_populates = "compu_tab_ref")


class Formula(Base):
    """
    """
    __tablename__ = "formula"

    f_x = StdString()

    __required_parameters__ = (
        Parameter("f_x", String, False),
    )

    __optional_elements__ = (
        Element("FormulaInv", "FORMULA_INV", False),
    )
    formula_inv = relationship("FormulaInv", back_populates = "formula", uselist = False)
    _compu_method_rid = Column(types.Integer, ForeignKey("compu_method.rid"))
    compu_method = relationship("CompuMethod", back_populates = "formula")


class FormulaInv(Base):
    """
    """
    __tablename__ = "formula_inv"

    g_x = StdString()

    __required_parameters__ = (
        Parameter("g_x", String, False),
    )

    __optional_elements__ = ( )
    _formula_rid = Column(types.Integer, ForeignKey("formula.rid"))
    formula = relationship("Formula", back_populates = "formula_inv")


class StatusStringRef(Base):
    """
    """
    __tablename__ = "status_string_ref"

    conversionTable = StdIdent()

    __required_parameters__ = (
        Parameter("conversionTable", Ident, False),
    )

    __optional_elements__ = ( )
    _compu_method_rid = Column(types.Integer, ForeignKey("compu_method.rid"))
    compu_method = relationship("CompuMethod", back_populates = "status_string_ref")


class CompuTab(Base, HasDefaultValues):
    """
    """
    __tablename__ = "compu_tab"

    name = StdIdent()

    longIdentifier = StdString()

    conversionType = StdString()

    numberValuePairs = StdUShort()

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
        Parameter("conversionType", Enum, False),
        Parameter("numberValuePairs", Uint, False),
    )
    pairs = relationship("CompuTabPair", backref = "parent")

    __optional_elements__ = (
        Element("DefaultValue", "DEFAULT_VALUE", False),
        Element("DefaultValueNumeric", "DEFAULT_VALUE_NUMERIC", False),
    )
    default_value_numeric = relationship("DefaultValueNumeric", back_populates = "compu_tab", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "compu_tabs")


class DefaultValueNumeric(Base):
    """
    """
    __tablename__ = "default_value_numeric"

    display_value = StdFloat()

    __required_parameters__ = (
        Parameter("display_value", Float, False),
    )

    __optional_elements__ = ( )
    _compu_tab_rid = Column(types.Integer, ForeignKey("compu_tab.rid"))
    compu_tab = relationship("CompuTab", back_populates = "default_value_numeric")


class CompuVtab(Base, HasDefaultValues):
    """
    """
    __tablename__ = "compu_vtab"

    name = StdIdent()

    longIdentifier = StdString()

    conversionType = StdString()

    numberValuePairs = StdUShort()

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
        Parameter("conversionType", Enum, False),
        Parameter("numberValuePairs", Uint, False),
    )
    pairs = relationship("CompuVtabPair", backref = "parent")

    __optional_elements__ = (
        Element("DefaultValue", "DEFAULT_VALUE", False),
    )
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "compu_vtabs")


class CompuVtabRange(Base, HasDefaultValues):
    """
    """
    __tablename__ = "compu_vtab_range"

    name = StdIdent()

    longIdentifier = StdString()

    numberValueTriples = StdUShort()

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
        Parameter("numberValueTriples", Uint, False),
    )
    triples = relationship("CompuVtabRangeTriple", backref = "parent")

    __optional_elements__ = (
        Element("DefaultValue", "DEFAULT_VALUE", False),
    )
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "compu_vtab_ranges")


class Frame(Base, HasIfDatas):
    """
    """
    __tablename__ = "frame"

    name = StdIdent()

    longIdentifier = StdString()

    scalingUnit = StdUShort()

    rate = StdULong()

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
        Parameter("scalingUnit", Uint, False),
        Parameter("rate", Ulong, False),
    )

    __optional_elements__ = (
        Element("FrameMeasurement", "FRAME_MEASUREMENT", False),
        Element("IfData", "IF_DATA", True),
    )
    frame_measurement = relationship("FrameMeasurement", back_populates = "frame", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "frame")


class FrameMeasurement(Base):
    """
    """
    __tablename__ = "frame_measurement"

    _identifier = relationship("FrameMeasurementIdentifiers", backref = "parent")
    identifier = association_proxy("_identifier", "identifier")

    __required_parameters__ = (
        Parameter("identifier", Ident, True),
    )

    __optional_elements__ = ( )
    _frame_rid = Column(types.Integer, ForeignKey("frame.rid"))
    frame = relationship("Frame", back_populates = "frame_measurement")


class Function(Base, HasAnnotations, HasIfDatas, HasRefCharacteristics):
    """
    """
    __tablename__ = "function"

    name = StdIdent()

    longIdentifier = StdString()

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
    )

    __optional_elements__ = (
        Element("Annotation", "ANNOTATION", True),
        Element("DefCharacteristic", "DEF_CHARACTERISTIC", False),
        Element("FunctionVersion", "FUNCTION_VERSION", False),
        Element("IfData", "IF_DATA", True),
        Element("InMeasurement", "IN_MEASUREMENT", False),
        Element("LocMeasurement", "LOC_MEASUREMENT", False),
        Element("OutMeasurement", "OUT_MEASUREMENT", False),
        Element("RefCharacteristic", "REF_CHARACTERISTIC", False),
        Element("SubFunction", "SUB_FUNCTION", False),
    )
    def_characteristic = relationship("DefCharacteristic", back_populates = "function", uselist = False)
    function_version = relationship("FunctionVersion", back_populates = "function", uselist = False)
    in_measurement = relationship("InMeasurement", back_populates = "function", uselist = False)
    loc_measurement = relationship("LocMeasurement", back_populates = "function", uselist = False)
    out_measurement = relationship("OutMeasurement", back_populates = "function", uselist = False)
    sub_function = relationship("SubFunction", back_populates = "function", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "functions")


class DefCharacteristic(Base):
    """
    """
    __tablename__ = "def_characteristic"

    _identifier = relationship("DefCharacteristicIdentifiers", backref = "parent")
    identifier = association_proxy("_identifier", "identifier")

    __required_parameters__ = (
        Parameter("identifier", Ident, True),
    )

    __optional_elements__ = ( )
    _function_rid = Column(types.Integer, ForeignKey("function.rid"))
    function = relationship("Function", back_populates = "def_characteristic")


class FunctionVersion(Base):
    """
    """
    __tablename__ = "function_version"

    versionIdentifier = StdString()

    __required_parameters__ = (
        Parameter("versionIdentifier", String, False),
    )

    __optional_elements__ = ( )
    _function_rid = Column(types.Integer, ForeignKey("function.rid"))
    function = relationship("Function", back_populates = "function_version")


class InMeasurement(Base):
    """
    """
    __tablename__ = "in_measurement"

    _identifier = relationship("InMeasurementIdentifiers", backref = "parent")
    identifier = association_proxy("_identifier", "identifier")

    __required_parameters__ = (
        Parameter("identifier", Ident, True),
    )

    __optional_elements__ = ( )
    _function_rid = Column(types.Integer, ForeignKey("function.rid"))
    function = relationship("Function", back_populates = "in_measurement")


class LocMeasurement(Base):
    """
    """
    __tablename__ = "loc_measurement"

    _identifier = relationship("LocMeasurementIdentifiers", backref = "parent")
    identifier = association_proxy("_identifier", "identifier")

    __required_parameters__ = (
        Parameter("identifier", Ident, True),
    )

    __optional_elements__ = ( )
    _function_rid = Column(types.Integer, ForeignKey("function.rid"))
    function = relationship("Function", back_populates = "loc_measurement")


class OutMeasurement(Base):
    """
    """
    __tablename__ = "out_measurement"

    _identifier = relationship("OutMeasurementIdentifiers", backref = "parent")
    identifier = association_proxy("_identifier", "identifier")

    __required_parameters__ = (
        Parameter("identifier", Ident, True),
    )

    __optional_elements__ = ( )
    _function_rid = Column(types.Integer, ForeignKey("function.rid"))
    function = relationship("Function", back_populates = "out_measurement")


class SubFunction(Base):
    """
    """
    __tablename__ = "sub_function"

    _identifier = relationship("SubFunctionIdentifiers", backref = "parent")
    identifier = association_proxy("_identifier", "identifier")

    __required_parameters__ = (
        Parameter("identifier", Ident, True),
    )

    __optional_elements__ = ( )
    _function_rid = Column(types.Integer, ForeignKey("function.rid"))
    function = relationship("Function", back_populates = "sub_function")


class Group(Base, HasAnnotations, HasFunctionLists, HasIfDatas, HasRefCharacteristics):
    """
    """
    __tablename__ = "group"

    groupName = StdIdent()

    groupLongIdentifier = StdString()

    __required_parameters__ = (
        Parameter("groupName", Ident, False),
        Parameter("groupLongIdentifier", String, False),
    )

    __optional_elements__ = (
        Element("Annotation", "ANNOTATION", True),
        Element("FunctionList", "FUNCTION_LIST", False),
        Element("IfData", "IF_DATA", True),
        Element("RefCharacteristic", "REF_CHARACTERISTIC", False),
        Element("RefMeasurement", "REF_MEASUREMENT", False),
        Element("Root", "ROOT", False),
        Element("SubGroup", "SUB_GROUP", False),
    )
    ref_measurement = relationship("RefMeasurement", back_populates = "group", uselist = False)
    root = relationship("Root", back_populates = "group", uselist = False)
    sub_group = relationship("SubGroup", back_populates = "group", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "groups")


class RefMeasurement(Base):
    """
    """
    __tablename__ = "ref_measurement"

    _identifier = relationship("RefMeasurementIdentifiers", backref = "parent")
    identifier = association_proxy("_identifier", "identifier")

    __required_parameters__ = (
        Parameter("identifier", Ident, True),
    )

    __optional_elements__ = ( )
    _group_rid = Column(types.Integer, ForeignKey("group.rid"))
    group = relationship("Group", back_populates = "ref_measurement")


class Root(Base):
    """
    """
    __tablename__ = "root"

    __required_parameters__ = ( )

    __optional_elements__ = ( )
    _group_rid = Column(types.Integer, ForeignKey("group.rid"))
    group = relationship("Group", back_populates = "root")


class SubGroup(Base):
    """
    """
    __tablename__ = "sub_group"

    _identifier = relationship("SubGroupIdentifiers", backref = "parent")
    identifier = association_proxy("_identifier", "identifier")

    __required_parameters__ = (
        Parameter("identifier", Ident, True),
    )

    __optional_elements__ = ( )
    _group_rid = Column(types.Integer, ForeignKey("group.rid"))
    group = relationship("Group", back_populates = "sub_group")


class Measurement(Base, HasAnnotations, HasBitMasks, HasByteOrders, HasDiscretes, HasDisplayIdentifiers, HasEcuAddressExtensions, HasFormats, HasFunctionLists, HasIfDatas, HasMatrixDims, HasMaxRefreshs, HasPhysUnits, HasRefMemorySegments, HasSymbolLinks):
    """
    """
    __tablename__ = "measurement"

    name = StdIdent()

    longIdentifier = StdString()

    datatype = StdIdent()

    conversion = StdIdent()

    resolution = StdUShort()

    accuracy = StdFloat()

    lowerLimit = StdFloat()

    upperLimit = StdFloat()

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
        Parameter("datatype", Datatype, False),
        Parameter("conversion", Ident, False),
        Parameter("resolution", Uint, False),
        Parameter("accuracy", Float, False),
        Parameter("lowerLimit", Float, False),
        Parameter("upperLimit", Float, False),
    )

    __optional_elements__ = (
        Element("Annotation", "ANNOTATION", True),
        Element("ArraySize", "ARRAY_SIZE", False),
        Element("BitMask", "BIT_MASK", False),
        Element("BitOperation", "BIT_OPERATION", False),
        Element("ByteOrder", "BYTE_ORDER", False),
        Element("Discrete", "DISCRETE", False),
        Element("DisplayIdentifier", "DISPLAY_IDENTIFIER", False),
        Element("EcuAddress", "ECU_ADDRESS", False),
        Element("EcuAddressExtension", "ECU_ADDRESS_EXTENSION", False),
        Element("ErrorMask", "ERROR_MASK", False),
        Element("Format", "FORMAT", False),
        Element("FunctionList", "FUNCTION_LIST", False),
        Element("IfData", "IF_DATA", True),
        Element("Layout", "LAYOUT", False),
        Element("MatrixDim", "MATRIX_DIM", False),
        Element("MaxRefresh", "MAX_REFRESH", False),
        Element("PhysUnit", "PHYS_UNIT", False),
        Element("ReadWrite", "READ_WRITE", False),
        Element("RefMemorySegment", "REF_MEMORY_SEGMENT", False),
        Element("SymbolLink", "SYMBOL_LINK", False),
        Element("Virtual", "VIRTUAL", False),
    )
    array_size = relationship("ArraySize", back_populates = "measurement", uselist = False)
    bit_operation = relationship("BitOperation", back_populates = "measurement", uselist = False)
    ecu_address = relationship("EcuAddress", back_populates = "measurement", uselist = False)
    error_mask = relationship("ErrorMask", back_populates = "measurement", uselist = False)
    layout = relationship("Layout", back_populates = "measurement", uselist = False)
    read_write = relationship("ReadWrite", back_populates = "measurement", uselist = False)
    virtual = relationship("Virtual", back_populates = "measurement", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "measurements")


class ArraySize(Base):
    """
    """
    __tablename__ = "array_size"

    number = StdUShort()

    __required_parameters__ = (
        Parameter("number", Uint, False),
    )

    __optional_elements__ = ( )
    _measurement_rid = Column(types.Integer, ForeignKey("measurement.rid"))
    measurement = relationship("Measurement", back_populates = "array_size")


class BitOperation(Base):
    """
    """
    __tablename__ = "bit_operation"

    __required_parameters__ = ( )

    __optional_elements__ = (
        Element("LeftShift", "LEFT_SHIFT", False),
        Element("RightShift", "RIGHT_SHIFT", False),
        Element("SignExtend", "SIGN_EXTEND", False),
    )
    left_shift = relationship("LeftShift", back_populates = "bit_operation", uselist = False)
    right_shift = relationship("RightShift", back_populates = "bit_operation", uselist = False)
    sign_extend = relationship("SignExtend", back_populates = "bit_operation", uselist = False)
    _measurement_rid = Column(types.Integer, ForeignKey("measurement.rid"))
    measurement = relationship("Measurement", back_populates = "bit_operation")


class LeftShift(Base):
    """
    """
    __tablename__ = "left_shift"

    bitcount = StdULong()

    __required_parameters__ = (
        Parameter("bitcount", Ulong, False),
    )

    __optional_elements__ = ( )
    _bit_operation_rid = Column(types.Integer, ForeignKey("bit_operation.rid"))
    bit_operation = relationship("BitOperation", back_populates = "left_shift")


class RightShift(Base):
    """
    """
    __tablename__ = "right_shift"

    bitcount = StdULong()

    __required_parameters__ = (
        Parameter("bitcount", Ulong, False),
    )

    __optional_elements__ = ( )
    _bit_operation_rid = Column(types.Integer, ForeignKey("bit_operation.rid"))
    bit_operation = relationship("BitOperation", back_populates = "right_shift")


class SignExtend(Base):
    """
    """
    __tablename__ = "sign_extend"

    __required_parameters__ = ( )

    __optional_elements__ = ( )
    _bit_operation_rid = Column(types.Integer, ForeignKey("bit_operation.rid"))
    bit_operation = relationship("BitOperation", back_populates = "sign_extend")


class EcuAddress(Base):
    """
    """
    __tablename__ = "ecu_address"

    address = StdULong()

    __required_parameters__ = (
        Parameter("address", Ulong, False),
    )

    __optional_elements__ = ( )
    _measurement_rid = Column(types.Integer, ForeignKey("measurement.rid"))
    measurement = relationship("Measurement", back_populates = "ecu_address")


class ErrorMask(Base):
    """
    """
    __tablename__ = "error_mask"

    mask = StdULong()

    __required_parameters__ = (
        Parameter("mask", Ulong, False),
    )

    __optional_elements__ = ( )
    _measurement_rid = Column(types.Integer, ForeignKey("measurement.rid"))
    measurement = relationship("Measurement", back_populates = "error_mask")


class Layout(Base):
    """
    """
    __tablename__ = "layout"

    indexMode = StdString()

    __required_parameters__ = (
        Parameter("indexMode", Enum, False),
    )

    __optional_elements__ = ( )
    _measurement_rid = Column(types.Integer, ForeignKey("measurement.rid"))
    measurement = relationship("Measurement", back_populates = "layout")


class ReadWrite(Base):
    """
    """
    __tablename__ = "read_write"

    __required_parameters__ = ( )

    __optional_elements__ = ( )
    _measurement_rid = Column(types.Integer, ForeignKey("measurement.rid"))
    measurement = relationship("Measurement", back_populates = "read_write")


class Virtual(Base):
    """
    """
    __tablename__ = "virtual"
    _measuringChannel = relationship("VirtualMeasuringChannels", backref = "parent")
    measuringChannel = association_proxy("_measuringChannel", "measuringChannel")

    __required_parameters__ = ( )

    __optional_elements__ = ( )
    _measurement_rid = Column(types.Integer, ForeignKey("measurement.rid"))
    measurement = relationship("Measurement", back_populates = "virtual")


class ModCommon(Base, HasAlignmentBytes, HasAlignmentFloat32Ieees, HasAlignmentFloat64Ieees, HasAlignmentInt64s, HasAlignmentLongs, HasAlignmentWords, HasByteOrders, HasDeposits):
    """
    """
    __tablename__ = "mod_common"

    comment = StdString()

    __required_parameters__ = (
        Parameter("comment", String, False),
    )

    __optional_elements__ = (
        Element("AlignmentByte", "ALIGNMENT_BYTE", False),
        Element("AlignmentFloat32Ieee", "ALIGNMENT_FLOAT32_IEEE", False),
        Element("AlignmentFloat64Ieee", "ALIGNMENT_FLOAT64_IEEE", False),
        Element("AlignmentInt64", "ALIGNMENT_INT64", False),
        Element("AlignmentLong", "ALIGNMENT_LONG", False),
        Element("AlignmentWord", "ALIGNMENT_WORD", False),
        Element("ByteOrder", "BYTE_ORDER", False),
        Element("DataSize", "DATA_SIZE", False),
        Element("Deposit", "DEPOSIT", False),
        Element("SRecLayout", "S_REC_LAYOUT", False),
    )
    data_size = relationship("DataSize", back_populates = "mod_common", uselist = False)
    s_rec_layout = relationship("SRecLayout", back_populates = "mod_common", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "mod_common")


class DataSize(Base):
    """
    """
    __tablename__ = "data_size"

    size = StdUShort()

    __required_parameters__ = (
        Parameter("size", Uint, False),
    )

    __optional_elements__ = ( )
    _mod_common_rid = Column(types.Integer, ForeignKey("mod_common.rid"))
    mod_common = relationship("ModCommon", back_populates = "data_size")


class SRecLayout(Base):
    """
    """
    __tablename__ = "s_rec_layout"

    name = StdIdent()

    __required_parameters__ = (
        Parameter("name", Ident, False),
    )

    __optional_elements__ = ( )
    _mod_common_rid = Column(types.Integer, ForeignKey("mod_common.rid"))
    mod_common = relationship("ModCommon", back_populates = "s_rec_layout")


class ModPar(Base, HasVersions):
    """
    """
    __tablename__ = "mod_par"

    comment = StdString()

    __required_parameters__ = (
        Parameter("comment", String, False),
    )

    __optional_elements__ = (
        Element("AddrEpk", "ADDR_EPK", True),
        Element("CalibrationMethod", "CALIBRATION_METHOD", True),
        Element("CpuType", "CPU_TYPE", False),
        Element("Customer", "CUSTOMER", False),
        Element("CustomerNo", "CUSTOMER_NO", False),
        Element("Ecu", "ECU", False),
        Element("EcuCalibrationOffset", "ECU_CALIBRATION_OFFSET", False),
        Element("Epk", "EPK", False),
        Element("MemoryLayout", "MEMORY_LAYOUT", True),
        Element("MemorySegment", "MEMORY_SEGMENT", True),
        Element("NoOfInterfaces", "NO_OF_INTERFACES", False),
        Element("PhoneNo", "PHONE_NO", False),
        Element("Supplier", "SUPPLIER", False),
        Element("SystemConstant", "SYSTEM_CONSTANT", True),
        Element("User", "USER", False),
        Element("Version", "VERSION", False),
    )
    addr_epks = relationship("AddrEpk", back_populates = "mod_par", uselist = True)
    calibration_methods = relationship("CalibrationMethod", back_populates = "mod_par", uselist = True)
    cpu_type = relationship("CpuType", back_populates = "mod_par", uselist = False)
    customer = relationship("Customer", back_populates = "mod_par", uselist = False)
    customer_no = relationship("CustomerNo", back_populates = "mod_par", uselist = False)
    ecu = relationship("Ecu", back_populates = "mod_par", uselist = False)
    ecu_calibration_offset = relationship("EcuCalibrationOffset", back_populates = "mod_par", uselist = False)
    epk = relationship("Epk", back_populates = "mod_par", uselist = False)
    memory_layouts = relationship("MemoryLayout", back_populates = "mod_par", uselist = True)
    memory_segments = relationship("MemorySegment", back_populates = "mod_par", uselist = True)
    no_of_interfaces = relationship("NoOfInterfaces", back_populates = "mod_par", uselist = False)
    phone_no = relationship("PhoneNo", back_populates = "mod_par", uselist = False)
    supplier = relationship("Supplier", back_populates = "mod_par", uselist = False)
    system_constants = relationship("SystemConstant", back_populates = "mod_par", uselist = True)
    user = relationship("User", back_populates = "mod_par", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "mod_par")


class AddrEpk(Base):
    """
    """
    __tablename__ = "addr_epk"

    address = StdULong()

    __required_parameters__ = (
        Parameter("address", Ulong, False),
    )

    __optional_elements__ = ( )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "addr_epks")


class CalibrationMethod(Base):
    """
    """
    __tablename__ = "calibration_method"

    method = StdString()

    version = StdULong()

    __required_parameters__ = (
        Parameter("method", String, False),
        Parameter("version", Ulong, False),
    )

    __optional_elements__ = (
        Element("CalibrationHandle", "CALIBRATION_HANDLE", True),
    )
    calibration_handles = relationship("CalibrationHandle", back_populates = "calibration_method", uselist = True)
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "calibration_methods")


class CalibrationHandle(Base):
    """
    """
    __tablename__ = "calibration_handle"
    _handle = relationship("CalHandles", backref = "parent")
    handle = association_proxy("_handle", "handle")

    __required_parameters__ = ( )

    __optional_elements__ = (
        Element("CalibrationHandleText", "CALIBRATION_HANDLE_TEXT", False),
    )
    calibration_handle_text = relationship("CalibrationHandleText", back_populates = "calibration_handle", uselist = False)
    _calibration_method_rid = Column(types.Integer, ForeignKey("calibration_method.rid"))
    calibration_method = relationship("CalibrationMethod", back_populates = "calibration_handles")


class CalibrationHandleText(Base):
    """
    """
    __tablename__ = "calibration_handle_text"

    text = StdString()

    __required_parameters__ = (
        Parameter("text", String, False),
    )

    __optional_elements__ = ( )
    _calibration_handle_rid = Column(types.Integer, ForeignKey("calibration_handle.rid"))
    calibration_handle = relationship("CalibrationHandle", back_populates = "calibration_handle_text")


class CpuType(Base):
    """
    """
    __tablename__ = "cpu_type"

    cPU = StdString()

    __required_parameters__ = (
        Parameter("cPU", String, False),
    )

    __optional_elements__ = ( )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "cpu_type")


class Customer(Base):
    """
    """
    __tablename__ = "customer"

    customer = StdString()

    __required_parameters__ = (
        Parameter("customer", String, False),
    )

    __optional_elements__ = ( )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "customer")


class CustomerNo(Base):
    """
    """
    __tablename__ = "customer_no"

    number = StdString()

    __required_parameters__ = (
        Parameter("number", String, False),
    )

    __optional_elements__ = ( )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "customer_no")


class Ecu(Base):
    """
    """
    __tablename__ = "ecu"

    controlUnit = StdString()

    __required_parameters__ = (
        Parameter("controlUnit", String, False),
    )

    __optional_elements__ = ( )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "ecu")


class EcuCalibrationOffset(Base):
    """
    """
    __tablename__ = "ecu_calibration_offset"

    offset = StdLong()

    __required_parameters__ = (
        Parameter("offset", Long, False),
    )

    __optional_elements__ = ( )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "ecu_calibration_offset")


class Epk(Base):
    """
    """
    __tablename__ = "epk"

    identifier = StdString()

    __required_parameters__ = (
        Parameter("identifier", String, False),
    )

    __optional_elements__ = ( )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "epk")


class MemoryLayout(Base, HasIfDatas):
    """
    """
    __tablename__ = "memory_layout"

    prgType = StdString()

    address = StdULong()

    size = StdULong()

    offset_0 = StdLong()

    offset_1 = StdLong()

    offset_2 = StdLong()

    offset_3 = StdLong()

    offset_4 = StdLong()

    __required_parameters__ = (
        Parameter("prgType", Enum, False),
        Parameter("address", Ulong, False),
        Parameter("size", Ulong, False),
        Parameter("offset_0", Long, False),
        Parameter("offset_1", Long, False),
        Parameter("offset_2", Long, False),
        Parameter("offset_3", Long, False),
        Parameter("offset_4", Long, False),
    )

    __optional_elements__ = (
        Element("IfData", "IF_DATA", True),
    )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "memory_layouts")


class MemorySegment(Base, HasIfDatas):
    """
    """
    __tablename__ = "memory_segment"

    name = StdIdent()

    longIdentifier = StdString()

    prgType = StdString()

    memoryType = StdString()

    attribute = StdString()

    address = StdULong()

    size = StdULong()

    offset_0 = StdLong()

    offset_1 = StdLong()

    offset_2 = StdLong()

    offset_3 = StdLong()

    offset_4 = StdLong()

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
        Parameter("prgType", Enum, False),
        Parameter("memoryType", Enum, False),
        Parameter("attribute", Enum, False),
        Parameter("address", Ulong, False),
        Parameter("size", Ulong, False),
        Parameter("offset_0", Long, False),
        Parameter("offset_1", Long, False),
        Parameter("offset_2", Long, False),
        Parameter("offset_3", Long, False),
        Parameter("offset_4", Long, False),
    )

    __optional_elements__ = (
        Element("IfData", "IF_DATA", True),
    )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "memory_segments")


class NoOfInterfaces(Base):
    """
    """
    __tablename__ = "no_of_interfaces"

    num = StdUShort()

    __required_parameters__ = (
        Parameter("num", Uint, False),
    )

    __optional_elements__ = ( )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "no_of_interfaces")


class PhoneNo(Base):
    """
    """
    __tablename__ = "phone_no"

    telnum = StdString()

    __required_parameters__ = (
        Parameter("telnum", String, False),
    )

    __optional_elements__ = ( )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "phone_no")


class Supplier(Base):
    """
    """
    __tablename__ = "supplier"

    manufacturer = StdString()

    __required_parameters__ = (
        Parameter("manufacturer", String, False),
    )

    __optional_elements__ = ( )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "supplier")


class SystemConstant(Base):
    """
    """
    __tablename__ = "system_constant"

    name = StdString()

    value = StdString()

    __required_parameters__ = (
        Parameter("name", String, False),
        Parameter("value", String, False),
    )

    __optional_elements__ = ( )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "system_constants")


class User(Base):
    """
    """
    __tablename__ = "user"

    userName = StdString()

    __required_parameters__ = (
        Parameter("userName", String, False),
    )

    __optional_elements__ = ( )
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "user")


class RecordLayout(Base, HasAlignmentBytes, HasAlignmentFloat32Ieees, HasAlignmentFloat64Ieees, HasAlignmentInt64s, HasAlignmentLongs, HasAlignmentWords):
    """
    """
    __tablename__ = "record_layout"

    name = StdIdent()

    __required_parameters__ = (
        Parameter("name", Ident, False),
    )

    __optional_elements__ = (
        Element("AlignmentByte", "ALIGNMENT_BYTE", False),
        Element("AlignmentFloat32Ieee", "ALIGNMENT_FLOAT32_IEEE", False),
        Element("AlignmentFloat64Ieee", "ALIGNMENT_FLOAT64_IEEE", False),
        Element("AlignmentInt64", "ALIGNMENT_INT64", False),
        Element("AlignmentLong", "ALIGNMENT_LONG", False),
        Element("AlignmentWord", "ALIGNMENT_WORD", False),
        Element("AxisPtsX", "AXIS_PTS_X", False),
        Element("AxisPtsY", "AXIS_PTS_Y", False),
        Element("AxisPtsZ", "AXIS_PTS_Z", False),
        Element("AxisPts4", "AXIS_PTS_4", False),
        Element("AxisPts5", "AXIS_PTS_5", False),
        Element("AxisRescaleX", "AXIS_RESCALE_X", False),
        Element("AxisRescaleY", "AXIS_RESCALE_Y", False),
        Element("AxisRescaleZ", "AXIS_RESCALE_Z", False),
        Element("AxisRescale4", "AXIS_RESCALE_4", False),
        Element("AxisRescale5", "AXIS_RESCALE_5", False),
        Element("DistOpX", "DIST_OP_X", False),
        Element("DistOpY", "DIST_OP_Y", False),
        Element("DistOpZ", "DIST_OP_Z", False),
        Element("DistOp4", "DIST_OP_4", False),
        Element("DistOp5", "DIST_OP_5", False),
        Element("FixNoAxisPtsX", "FIX_NO_AXIS_PTS_X", False),
        Element("FixNoAxisPtsY", "FIX_NO_AXIS_PTS_Y", False),
        Element("FixNoAxisPtsZ", "FIX_NO_AXIS_PTS_Z", False),
        Element("FixNoAxisPts4", "FIX_NO_AXIS_PTS_4", False),
        Element("FixNoAxisPts5", "FIX_NO_AXIS_PTS_5", False),
        Element("FncValues", "FNC_VALUES", False),
        Element("Identification", "IDENTIFICATION", False),
        Element("NoAxisPtsX", "NO_AXIS_PTS_X", False),
        Element("NoAxisPtsY", "NO_AXIS_PTS_Y", False),
        Element("NoAxisPtsZ", "NO_AXIS_PTS_Z", False),
        Element("NoAxisPts4", "NO_AXIS_PTS_4", False),
        Element("NoAxisPts5", "NO_AXIS_PTS_5", False),
        Element("StaticRecordLayout", "STATIC_RECORD_LAYOUT", False),
        Element("NoRescaleX", "NO_RESCALE_X", False),
        Element("NoRescaleY", "NO_RESCALE_Y", False),
        Element("NoRescaleZ", "NO_RESCALE_Z", False),
        Element("NoRescale4", "NO_RESCALE_4", False),
        Element("NoRescale5", "NO_RESCALE_5", False),
        Element("OffsetX", "OFFSET_X", False),
        Element("OffsetY", "OFFSET_Y", False),
        Element("OffsetZ", "OFFSET_Z", False),
        Element("Offset4", "OFFSET_4", False),
        Element("Offset5", "OFFSET_5", False),
        Element("Reserved", "RESERVED", True),
        Element("RipAddrW", "RIP_ADDR_W", False),
        Element("RipAddrX", "RIP_ADDR_X", False),
        Element("RipAddrY", "RIP_ADDR_Y", False),
        Element("RipAddrZ", "RIP_ADDR_Z", False),
        Element("RipAddr4", "RIP_ADDR_4", False),
        Element("RipAddr5", "RIP_ADDR_5", False),
        Element("ShiftOpX", "SHIFT_OP_X", False),
        Element("ShiftOpY", "SHIFT_OP_Y", False),
        Element("ShiftOpZ", "SHIFT_OP_Z", False),
        Element("ShiftOp4", "SHIFT_OP_4", False),
        Element("ShiftOp5", "SHIFT_OP_5", False),
        Element("SrcAddrX", "SRC_ADDR_X", False),
        Element("SrcAddrY", "SRC_ADDR_Y", False),
        Element("SrcAddrZ", "SRC_ADDR_Z", False),
        Element("SrcAddr4", "SRC_ADDR_4", False),
        Element("SrcAddr5", "SRC_ADDR_5", False),
    )
    axis_pts_x = relationship("AxisPtsX", back_populates = "record_layout", uselist = False)
    axis_pts_y = relationship("AxisPtsY", back_populates = "record_layout", uselist = False)
    axis_pts_z = relationship("AxisPtsZ", back_populates = "record_layout", uselist = False)
    axis_pts_4 = relationship("AxisPts4", back_populates = "record_layout", uselist = False)
    axis_pts_5 = relationship("AxisPts5", back_populates = "record_layout", uselist = False)
    axis_rescale_x = relationship("AxisRescaleX", back_populates = "record_layout", uselist = False)
    axis_rescale_y = relationship("AxisRescaleY", back_populates = "record_layout", uselist = False)
    axis_rescale_z = relationship("AxisRescaleZ", back_populates = "record_layout", uselist = False)
    axis_rescale_4 = relationship("AxisRescale4", back_populates = "record_layout", uselist = False)
    axis_rescale_5 = relationship("AxisRescale5", back_populates = "record_layout", uselist = False)
    dist_op_x = relationship("DistOpX", back_populates = "record_layout", uselist = False)
    dist_op_y = relationship("DistOpY", back_populates = "record_layout", uselist = False)
    dist_op_z = relationship("DistOpZ", back_populates = "record_layout", uselist = False)
    dist_op_4 = relationship("DistOp4", back_populates = "record_layout", uselist = False)
    dist_op_5 = relationship("DistOp5", back_populates = "record_layout", uselist = False)
    fix_no_axis_pts_x = relationship("FixNoAxisPtsX", back_populates = "record_layout", uselist = False)
    fix_no_axis_pts_y = relationship("FixNoAxisPtsY", back_populates = "record_layout", uselist = False)
    fix_no_axis_pts_z = relationship("FixNoAxisPtsZ", back_populates = "record_layout", uselist = False)
    fix_no_axis_pts_4 = relationship("FixNoAxisPts4", back_populates = "record_layout", uselist = False)
    fix_no_axis_pts_5 = relationship("FixNoAxisPts5", back_populates = "record_layout", uselist = False)
    fnc_values = relationship("FncValues", back_populates = "record_layout", uselist = False)
    identification = relationship("Identification", back_populates = "record_layout", uselist = False)
    no_axis_pts_x = relationship("NoAxisPtsX", back_populates = "record_layout", uselist = False)
    no_axis_pts_y = relationship("NoAxisPtsY", back_populates = "record_layout", uselist = False)
    no_axis_pts_z = relationship("NoAxisPtsZ", back_populates = "record_layout", uselist = False)
    no_axis_pts_4 = relationship("NoAxisPts4", back_populates = "record_layout", uselist = False)
    no_axis_pts_5 = relationship("NoAxisPts5", back_populates = "record_layout", uselist = False)
    static_record_layout = relationship("StaticRecordLayout", back_populates = "record_layout", uselist = False)
    no_rescale_x = relationship("NoRescaleX", back_populates = "record_layout", uselist = False)
    no_rescale_y = relationship("NoRescaleY", back_populates = "record_layout", uselist = False)
    no_rescale_z = relationship("NoRescaleZ", back_populates = "record_layout", uselist = False)
    no_rescale_4 = relationship("NoRescale4", back_populates = "record_layout", uselist = False)
    no_rescale_5 = relationship("NoRescale5", back_populates = "record_layout", uselist = False)
    offset_x = relationship("OffsetX", back_populates = "record_layout", uselist = False)
    offset_y = relationship("OffsetY", back_populates = "record_layout", uselist = False)
    offset_z = relationship("OffsetZ", back_populates = "record_layout", uselist = False)
    offset_4 = relationship("Offset4", back_populates = "record_layout", uselist = False)
    offset_5 = relationship("Offset5", back_populates = "record_layout", uselist = False)
    reserveds = relationship("Reserved", back_populates = "record_layout", uselist = True)
    rip_addr_w = relationship("RipAddrW", back_populates = "record_layout", uselist = False)
    rip_addr_x = relationship("RipAddrX", back_populates = "record_layout", uselist = False)
    rip_addr_y = relationship("RipAddrY", back_populates = "record_layout", uselist = False)
    rip_addr_z = relationship("RipAddrZ", back_populates = "record_layout", uselist = False)
    rip_addr_4 = relationship("RipAddr4", back_populates = "record_layout", uselist = False)
    rip_addr_5 = relationship("RipAddr5", back_populates = "record_layout", uselist = False)
    shift_op_x = relationship("ShiftOpX", back_populates = "record_layout", uselist = False)
    shift_op_y = relationship("ShiftOpY", back_populates = "record_layout", uselist = False)
    shift_op_z = relationship("ShiftOpZ", back_populates = "record_layout", uselist = False)
    shift_op_4 = relationship("ShiftOp4", back_populates = "record_layout", uselist = False)
    shift_op_5 = relationship("ShiftOp5", back_populates = "record_layout", uselist = False)
    src_addr_x = relationship("SrcAddrX", back_populates = "record_layout", uselist = False)
    src_addr_y = relationship("SrcAddrY", back_populates = "record_layout", uselist = False)
    src_addr_z = relationship("SrcAddrZ", back_populates = "record_layout", uselist = False)
    src_addr_4 = relationship("SrcAddr4", back_populates = "record_layout", uselist = False)
    src_addr_5 = relationship("SrcAddr5", back_populates = "record_layout", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "record_layouts")


class AxisPtsX(Base):
    """
    """
    __tablename__ = "axis_pts_x"

    position = StdUShort()

    datatype = StdIdent()

    indexIncr = StdIdent()

    addressing = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
        Parameter("indexIncr", Indexorder, False),
        Parameter("addressing", Addrtype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "axis_pts_x")


class AxisPtsY(Base):
    """
    """
    __tablename__ = "axis_pts_y"

    position = StdUShort()

    datatype = StdIdent()

    indexIncr = StdIdent()

    addressing = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
        Parameter("indexIncr", Indexorder, False),
        Parameter("addressing", Addrtype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "axis_pts_y")


class AxisPtsZ(Base):
    """
    """
    __tablename__ = "axis_pts_z"

    position = StdUShort()

    datatype = StdIdent()

    indexIncr = StdIdent()

    addressing = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
        Parameter("indexIncr", Indexorder, False),
        Parameter("addressing", Addrtype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "axis_pts_z")


class AxisPts4(Base):
    """
    """
    __tablename__ = "axis_pts_4"

    position = StdUShort()

    datatype = StdIdent()

    indexIncr = StdIdent()

    addressing = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
        Parameter("indexIncr", Indexorder, False),
        Parameter("addressing", Addrtype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "axis_pts_4")


class AxisPts5(Base):
    """
    """
    __tablename__ = "axis_pts_5"

    position = StdUShort()

    datatype = StdIdent()

    indexIncr = StdIdent()

    addressing = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
        Parameter("indexIncr", Indexorder, False),
        Parameter("addressing", Addrtype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "axis_pts_5")


class AxisRescaleX(Base):
    """
    """
    __tablename__ = "axis_rescale_x"

    position = StdUShort()

    datatype = StdIdent()

    maxNumberOfRescalePairs = StdUShort()

    indexIncr = StdIdent()

    addressing = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
        Parameter("maxNumberOfRescalePairs", Uint, False),
        Parameter("indexIncr", Indexorder, False),
        Parameter("addressing", Addrtype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "axis_rescale_x")


class AxisRescaleY(Base):
    """
    """
    __tablename__ = "axis_rescale_y"

    position = StdUShort()

    datatype = StdIdent()

    maxNumberOfRescalePairs = StdUShort()

    indexIncr = StdIdent()

    addressing = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
        Parameter("maxNumberOfRescalePairs", Uint, False),
        Parameter("indexIncr", Indexorder, False),
        Parameter("addressing", Addrtype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "axis_rescale_y")


class AxisRescaleZ(Base):
    """
    """
    __tablename__ = "axis_rescale_z"

    position = StdUShort()

    datatype = StdIdent()

    maxNumberOfRescalePairs = StdUShort()

    indexIncr = StdIdent()

    addressing = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
        Parameter("maxNumberOfRescalePairs", Uint, False),
        Parameter("indexIncr", Indexorder, False),
        Parameter("addressing", Addrtype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "axis_rescale_z")


class AxisRescale4(Base):
    """
    """
    __tablename__ = "axis_rescale_4"

    position = StdUShort()

    datatype = StdIdent()

    maxNumberOfRescalePairs = StdUShort()

    indexIncr = StdIdent()

    addressing = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
        Parameter("maxNumberOfRescalePairs", Uint, False),
        Parameter("indexIncr", Indexorder, False),
        Parameter("addressing", Addrtype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "axis_rescale_4")


class AxisRescale5(Base):
    """
    """
    __tablename__ = "axis_rescale_5"

    position = StdUShort()

    datatype = StdIdent()

    maxNumberOfRescalePairs = StdUShort()

    indexIncr = StdIdent()

    addressing = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
        Parameter("maxNumberOfRescalePairs", Uint, False),
        Parameter("indexIncr", Indexorder, False),
        Parameter("addressing", Addrtype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "axis_rescale_5")


class DistOpX(Base):
    """
    """
    __tablename__ = "dist_op_x"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "dist_op_x")


class DistOpY(Base):
    """
    """
    __tablename__ = "dist_op_y"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "dist_op_y")


class DistOpZ(Base):
    """
    """
    __tablename__ = "dist_op_z"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "dist_op_z")


class DistOp4(Base):
    """
    """
    __tablename__ = "dist_op_4"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "dist_op_4")


class DistOp5(Base):
    """
    """
    __tablename__ = "dist_op_5"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "dist_op_5")


class FixNoAxisPtsX(Base):
    """
    """
    __tablename__ = "fix_no_axis_pts_x"

    numberOfAxisPoints = StdUShort()

    __required_parameters__ = (
        Parameter("numberOfAxisPoints", Uint, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "fix_no_axis_pts_x")


class FixNoAxisPtsY(Base):
    """
    """
    __tablename__ = "fix_no_axis_pts_y"

    numberOfAxisPoints = StdUShort()

    __required_parameters__ = (
        Parameter("numberOfAxisPoints", Uint, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "fix_no_axis_pts_y")


class FixNoAxisPtsZ(Base):
    """
    """
    __tablename__ = "fix_no_axis_pts_z"

    numberOfAxisPoints = StdUShort()

    __required_parameters__ = (
        Parameter("numberOfAxisPoints", Uint, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "fix_no_axis_pts_z")


class FixNoAxisPts4(Base):
    """
    """
    __tablename__ = "fix_no_axis_pts_4"

    numberOfAxisPoints = StdUShort()

    __required_parameters__ = (
        Parameter("numberOfAxisPoints", Uint, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "fix_no_axis_pts_4")


class FixNoAxisPts5(Base):
    """
    """
    __tablename__ = "fix_no_axis_pts_5"

    numberOfAxisPoints = StdUShort()

    __required_parameters__ = (
        Parameter("numberOfAxisPoints", Uint, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "fix_no_axis_pts_5")


class FncValues(Base):
    """
    """
    __tablename__ = "fnc_values"

    position = StdUShort()

    datatype = StdIdent()

    indexMode = StdString()

    addresstype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
        Parameter("indexMode", Enum, False),
        Parameter("addresstype", Addrtype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "fnc_values")


class Identification(Base):
    """
    """
    __tablename__ = "identification"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "identification")


class NoAxisPtsX(Base):
    """
    """
    __tablename__ = "no_axis_pts_x"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_axis_pts_x")


class NoAxisPtsY(Base):
    """
    """
    __tablename__ = "no_axis_pts_y"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_axis_pts_y")


class NoAxisPtsZ(Base):
    """
    """
    __tablename__ = "no_axis_pts_z"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_axis_pts_z")


class NoAxisPts4(Base):
    """
    """
    __tablename__ = "no_axis_pts_4"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_axis_pts_4")


class NoAxisPts5(Base):
    """
    """
    __tablename__ = "no_axis_pts_5"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_axis_pts_5")


class StaticRecordLayout(Base):
    """
    """
    __tablename__ = "static_record_layout"

    __required_parameters__ = ( )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "static_record_layout")


class NoRescaleX(Base):
    """
    """
    __tablename__ = "no_rescale_x"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_rescale_x")


class NoRescaleY(Base):
    """
    """
    __tablename__ = "no_rescale_y"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_rescale_y")


class NoRescaleZ(Base):
    """
    """
    __tablename__ = "no_rescale_z"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_rescale_z")


class NoRescale4(Base):
    """
    """
    __tablename__ = "no_rescale_4"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_rescale_4")


class NoRescale5(Base):
    """
    """
    __tablename__ = "no_rescale_5"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_rescale_5")


class OffsetX(Base):
    """
    """
    __tablename__ = "offset_x"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "offset_x")


class OffsetY(Base):
    """
    """
    __tablename__ = "offset_y"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "offset_y")


class OffsetZ(Base):
    """
    """
    __tablename__ = "offset_z"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "offset_z")


class Offset4(Base):
    """
    """
    __tablename__ = "offset_4"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "offset_4")


class Offset5(Base):
    """
    """
    __tablename__ = "offset_5"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "offset_5")


class Reserved(Base):
    """
    """
    __tablename__ = "reserved"

    position = StdUShort()

    dataSize = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("dataSize", Datasize, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "reserveds")


class RipAddrW(Base):
    """
    """
    __tablename__ = "rip_addr_w"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "rip_addr_w")


class RipAddrX(Base):
    """
    """
    __tablename__ = "rip_addr_x"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "rip_addr_x")


class RipAddrY(Base):
    """
    """
    __tablename__ = "rip_addr_y"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "rip_addr_y")


class RipAddrZ(Base):
    """
    """
    __tablename__ = "rip_addr_z"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "rip_addr_z")


class RipAddr4(Base):
    """
    """
    __tablename__ = "rip_addr_4"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "rip_addr_4")


class RipAddr5(Base):
    """
    """
    __tablename__ = "rip_addr_5"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "rip_addr_5")


class ShiftOpX(Base):
    """
    """
    __tablename__ = "shift_op_x"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "shift_op_x")


class ShiftOpY(Base):
    """
    """
    __tablename__ = "shift_op_y"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "shift_op_y")


class ShiftOpZ(Base):
    """
    """
    __tablename__ = "shift_op_z"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "shift_op_z")


class ShiftOp4(Base):
    """
    """
    __tablename__ = "shift_op_4"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "shift_op_4")


class ShiftOp5(Base):
    """
    """
    __tablename__ = "shift_op_5"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "shift_op_5")


class SrcAddrX(Base):
    """
    """
    __tablename__ = "src_addr_x"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "src_addr_x")


class SrcAddrY(Base):
    """
    """
    __tablename__ = "src_addr_y"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "src_addr_y")


class SrcAddrZ(Base):
    """
    """
    __tablename__ = "src_addr_z"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "src_addr_z")


class SrcAddr4(Base):
    """
    """
    __tablename__ = "src_addr_4"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "src_addr_4")


class SrcAddr5(Base):
    """
    """
    __tablename__ = "src_addr_5"

    position = StdUShort()

    datatype = StdIdent()

    __required_parameters__ = (
        Parameter("position", Uint, False),
        Parameter("datatype", Datatype, False),
    )

    __optional_elements__ = ( )
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "src_addr_5")


class Unit(Base, HasRefUnits):
    """
    """
    __tablename__ = "unit"

    name = StdIdent()

    longIdentifier = StdString()

    display = StdString()

    type = StdString()

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
        Parameter("display", String, False),
        Parameter("type", Enum, False),
    )

    __optional_elements__ = (
        Element("SiExponents", "SI_EXPONENTS", False),
        Element("RefUnit", "REF_UNIT", False),
        Element("UnitConversion", "UNIT_CONVERSION", False),
    )
    si_exponents = relationship("SiExponents", back_populates = "unit", uselist = False)
    unit_conversion = relationship("UnitConversion", back_populates = "unit", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "units")


class SiExponents(Base):
    """
    """
    __tablename__ = "si_exponents"

    length = StdShort()

    mass = StdShort()

    time = StdShort()

    electricCurrent = StdShort()

    temperature = StdShort()

    amountOfSubstance = StdShort()

    luminousIntensity = StdShort()

    __required_parameters__ = (
        Parameter("length", Int, False),
        Parameter("mass", Int, False),
        Parameter("time", Int, False),
        Parameter("electricCurrent", Int, False),
        Parameter("temperature", Int, False),
        Parameter("amountOfSubstance", Int, False),
        Parameter("luminousIntensity", Int, False),
    )

    __optional_elements__ = ( )
    _unit_rid = Column(types.Integer, ForeignKey("unit.rid"))
    unit = relationship("Unit", back_populates = "si_exponents")


class UnitConversion(Base):
    """
    """
    __tablename__ = "unit_conversion"

    gradient = StdFloat()

    offset = StdFloat()

    __required_parameters__ = (
        Parameter("gradient", Float, False),
        Parameter("offset", Float, False),
    )

    __optional_elements__ = ( )
    _unit_rid = Column(types.Integer, ForeignKey("unit.rid"))
    unit = relationship("Unit", back_populates = "unit_conversion")


class UserRights(Base, HasReadOnlys):
    """
    """
    __tablename__ = "user_rights"

    userLevelId = StdIdent()

    __required_parameters__ = (
        Parameter("userLevelId", Ident, False),
    )

    __optional_elements__ = (
        Element("ReadOnly", "READ_ONLY", False),
        Element("RefGroup", "REF_GROUP", True),
    )
    ref_groups = relationship("RefGroup", back_populates = "user_rights", uselist = True)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "user_rights")


class RefGroup(Base):
    """
    """
    __tablename__ = "ref_group"

    _identifier = relationship("RefGroupIdentifiers", backref = "parent")
    identifier = association_proxy("_identifier", "identifier")

    __required_parameters__ = (
        Parameter("identifier", Ident, True),
    )

    __optional_elements__ = ( )
    _user_rights_rid = Column(types.Integer, ForeignKey("user_rights.rid"))
    user_rights = relationship("UserRights", back_populates = "ref_groups")


class VariantCoding(Base):
    """
    """
    __tablename__ = "variant_coding"

    __required_parameters__ = ( )

    __optional_elements__ = (
        Element("VarCharacteristic", "VAR_CHARACTERISTIC", True),
        Element("VarCriterion", "VAR_CRITERION", True),
        Element("VarForbiddenComb", "VAR_FORBIDDEN_COMB", False),
        Element("VarNaming", "VAR_NAMING", False),
        Element("VarSeparator", "VAR_SEPARATOR", False),
    )
    var_characteristics = relationship("VarCharacteristic", back_populates = "variant_coding", uselist = True)
    var_criterions = relationship("VarCriterion", back_populates = "variant_coding", uselist = True)
    var_forbidden_comb = relationship("VarForbiddenComb", back_populates = "variant_coding", uselist = False)
    var_naming = relationship("VarNaming", back_populates = "variant_coding", uselist = False)
    var_separator = relationship("VarSeparator", back_populates = "variant_coding", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "variant_coding")


class VarCharacteristic(Base):
    """
    """
    __tablename__ = "var_characteristic"

    name = StdIdent()

    _criterionName = relationship("VarCharacteristicIdentifiers", backref = "parent")
    criterionName = association_proxy("_criterionName", "criterionName")

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("criterionName", Ident, True),
    )

    __optional_elements__ = (
        Element("VarAddress", "VAR_ADDRESS", False),
    )
    var_address = relationship("VarAddress", back_populates = "var_characteristic", uselist = False)
    _variant_coding_rid = Column(types.Integer, ForeignKey("variant_coding.rid"))
    variant_coding = relationship("VariantCoding", back_populates = "var_characteristics")


class VarAddress(Base):
    """
    """
    __tablename__ = "var_address"

    address = StdULong()

    __required_parameters__ = (
        Parameter("address", Ulong, True),
    )

    __optional_elements__ = ( )
    _var_characteristic_rid = Column(types.Integer, ForeignKey("var_characteristic.rid"))
    var_characteristic = relationship("VarCharacteristic", back_populates = "var_address")


class VarCriterion(Base):
    """
    """
    __tablename__ = "var_criterion"

    name = StdIdent()

    longIdentifier = StdString()

    _value = relationship("VarCriterionIdentifiers", backref = "parent")
    value = association_proxy("_value", "value")

    __required_parameters__ = (
        Parameter("name", Ident, False),
        Parameter("longIdentifier", String, False),
        Parameter("value", Ident, True),
    )

    __optional_elements__ = (
        Element("VarMeasurement", "VAR_MEASUREMENT", False),
        Element("VarSelectionCharacteristic", "VAR_SELECTION_CHARACTERISTIC", False),
    )
    var_measurement = relationship("VarMeasurement", back_populates = "var_criterion", uselist = False)
    var_selection_characteristic = relationship("VarSelectionCharacteristic", back_populates = "var_criterion", uselist = False)
    _variant_coding_rid = Column(types.Integer, ForeignKey("variant_coding.rid"))
    variant_coding = relationship("VariantCoding", back_populates = "var_criterions")


class VarMeasurement(Base):
    """
    """
    __tablename__ = "var_measurement"

    name = StdIdent()

    __required_parameters__ = (
        Parameter("name", Ident, False),
    )

    __optional_elements__ = ( )
    _var_criterion_rid = Column(types.Integer, ForeignKey("var_criterion.rid"))
    var_criterion = relationship("VarCriterion", back_populates = "var_measurement")


class VarSelectionCharacteristic(Base):
    """
    """
    __tablename__ = "var_selection_characteristic"

    name = StdIdent()

    __required_parameters__ = (
        Parameter("name", Ident, False),
    )

    __optional_elements__ = ( )
    _var_criterion_rid = Column(types.Integer, ForeignKey("var_criterion.rid"))
    var_criterion = relationship("VarCriterion", back_populates = "var_selection_characteristic")


class VarForbiddenComb(Base):
    """
    """
    __tablename__ = "var_forbidden_comb"

    __required_parameters__ = ( )
    pairs = relationship("VarForbiddedCombPair", backref = "parent")

    __optional_elements__ = ( )
    _variant_coding_rid = Column(types.Integer, ForeignKey("variant_coding.rid"))
    variant_coding = relationship("VariantCoding", back_populates = "var_forbidden_comb")


class VarNaming(Base):
    """
    """
    __tablename__ = "var_naming"

    tag = StdString()

    __required_parameters__ = (
        Parameter("tag", Enum, False),
    )

    __optional_elements__ = ( )
    _variant_coding_rid = Column(types.Integer, ForeignKey("variant_coding.rid"))
    variant_coding = relationship("VariantCoding", back_populates = "var_naming")


class VarSeparator(Base):
    """
    """
    __tablename__ = "var_separator"

    separator = StdString()

    __required_parameters__ = (
        Parameter("separator", String, False),
    )

    __optional_elements__ = ( )
    _variant_coding_rid = Column(types.Integer, ForeignKey("variant_coding.rid"))
    variant_coding = relationship("VariantCoding", back_populates = "var_separator")

class A2LDatabase(object):

    def __init__(self, filename, debug = False, logLevel = 'INFO'):
        if filename == ':memory:':
            self.dbname = ""
        else:
            if not filename.lower().endswith(DB_EXTENSION):
               self.dbname = "{}.{}".format(filename, DB_EXTENSION)
            else:
               self.dbname = filename
            try:
                os.unlink(self.dbname)
            except:
                pass
        self._engine = create_engine("sqlite:///{}".format(self.dbname), echo = debug,
            connect_args={'detect_types': sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES},
        native_datetime = True)

        self._session = orm.Session(self._engine, autoflush = False, autocommit = False)
        self._metadata = Base.metadata
        #self._metadata = MetaData(self._engine, reflect = False)
        #self._metadata.create_all()
        #loadInitialData(Node)
        Base.metadata.create_all(self.engine)
        #print(model.Base.metadata.tables)
        self.session.flush()
        self.session.commit()

    @property
    def engine(self):
        return self._engine

    @property
    def metadata(self):
        return self._metadata

    @property
    def session(self):
        return self._session

    def begin_transaction(self):
        """
        """

    def commit_transaction(self):
        """
        """

    def rollback_transaction(self):
        """
        """

KEYWORD_MAP = {
    "A2ML" : A2ml,
    "A2ML_VERSION" : A2mlVersion,
    "ADDR_EPK" : AddrEpk,
    "ALIGNMENT_BYTE" : AlignmentByte,
    "ALIGNMENT_FLOAT32_IEEE" : AlignmentFloat32Ieee,
    "ALIGNMENT_FLOAT64_IEEE" : AlignmentFloat64Ieee,
    "ALIGNMENT_INT64" : AlignmentInt64,
    "ALIGNMENT_LONG" : AlignmentLong,
    "ALIGNMENT_WORD" : AlignmentWord,
    "ANNOTATION" : Annotation,
    "ANNOTATION_LABEL" : AnnotationLabel,
    "ANNOTATION_ORIGIN" : AnnotationOrigin,
    "ANNOTATION_TEXT" : AnnotationText,
    "ARRAY_SIZE" : ArraySize,
    "ASAP2_VERSION" : Asap2Version,
    "AXIS_DESCR" : AxisDescr,
    "AXIS_PTS" : AxisPts,
    "AXIS_PTS_REF" : AxisPtsRef,
    "AXIS_PTS_X" : AxisPtsX,
    "AXIS_PTS_Y" : AxisPtsY,
    "AXIS_PTS_Z" : AxisPtsZ,
    "AXIS_PTS_4" : AxisPts4,
    "AXIS_PTS_5" : AxisPts5,
    "AXIS_RESCALE_X" : AxisRescaleX,
    "AXIS_RESCALE_Y" : AxisRescaleY,
    "AXIS_RESCALE_Z" : AxisRescaleZ,
    "AXIS_RESCALE_4" : AxisRescale4,
    "AXIS_RESCALE_5" : AxisRescale5,
    "BIT_MASK" : BitMask,
    "BIT_OPERATION" : BitOperation,
    "BYTE_ORDER" : ByteOrder,
    "CALIBRATION_ACCESS" : CalibrationAccess,
    "CALIBRATION_HANDLE" : CalibrationHandle,
    "CALIBRATION_HANDLE_TEXT" : CalibrationHandleText,
    "CALIBRATION_METHOD" : CalibrationMethod,
    "CHARACTERISTIC" : Characteristic,
    "COEFFS" : Coeffs,
    "COEFFS_LINEAR" : CoeffsLinear,
    "COMPARISON_QUANTITY" : ComparisonQuantity,
    "COMPU_METHOD" : CompuMethod,
    "COMPU_TAB" : CompuTab,
    "COMPU_TAB_REF" : CompuTabRef,
    "COMPU_VTAB" : CompuVtab,
    "COMPU_VTAB_RANGE" : CompuVtabRange,
    "CPU_TYPE" : CpuType,
    "CURVE_AXIS_REF" : CurveAxisRef,
    "CUSTOMER" : Customer,
    "CUSTOMER_NO" : CustomerNo,
    "DATA_SIZE" : DataSize,
    "DEF_CHARACTERISTIC" : DefCharacteristic,
    "DEFAULT_VALUE" : DefaultValue,
    "DEFAULT_VALUE_NUMERIC" : DefaultValueNumeric,
    "DEPENDENT_CHARACTERISTIC" : DependentCharacteristic,
    "DEPOSIT" : Deposit,
    "DISCRETE" : Discrete,
    "DISPLAY_IDENTIFIER" : DisplayIdentifier,
    "DIST_OP_X" : DistOpX,
    "DIST_OP_Y" : DistOpY,
    "DIST_OP_Z" : DistOpZ,
    "DIST_OP_4" : DistOp4,
    "DIST_OP_5" : DistOp5,
    "ECU" : Ecu,
    "ECU_ADDRESS" : EcuAddress,
    "ECU_ADDRESS_EXTENSION" : EcuAddressExtension,
    "ECU_CALIBRATION_OFFSET" : EcuCalibrationOffset,
    "EPK" : Epk,
    "ERROR_MASK" : ErrorMask,
    "EXTENDED_LIMITS" : ExtendedLimits,
    "FIX_AXIS_PAR" : FixAxisPar,
    "FIX_AXIS_PAR_DIST" : FixAxisParDist,
    "FIX_AXIS_PAR_LIST" : FixAxisParList,
    "FIX_NO_AXIS_PTS_X" : FixNoAxisPtsX,
    "FIX_NO_AXIS_PTS_Y" : FixNoAxisPtsY,
    "FIX_NO_AXIS_PTS_Z" : FixNoAxisPtsZ,
    "FIX_NO_AXIS_PTS_4" : FixNoAxisPts4,
    "FIX_NO_AXIS_PTS_5" : FixNoAxisPts5,
    "FNC_VALUES" : FncValues,
    "FORMAT" : Format,
    "FORMULA" : Formula,
    "FORMULA_INV" : FormulaInv,
    "FRAME" : Frame,
    "FRAME_MEASUREMENT" : FrameMeasurement,
    "FUNCTION" : Function,
    "FUNCTION_LIST" : FunctionList,
    "FUNCTION_VERSION" : FunctionVersion,
    "GROUP" : Group,
    "GUARD_RAILS" : GuardRails,
    "HEADER" : Header,
    "IDENTIFICATION" : Identification,
    "IF_DATA" : IfData,
    "IN_MEASUREMENT" : InMeasurement,
    "LAYOUT" : Layout,
    "LEFT_SHIFT" : LeftShift,
    "LOC_MEASUREMENT" : LocMeasurement,
    "MAP_LIST" : MapList,
    "MATRIX_DIM" : MatrixDim,
    "MAX_GRAD" : MaxGrad,
    "MAX_REFRESH" : MaxRefresh,
    "MEASUREMENT" : Measurement,
    "MEMORY_LAYOUT" : MemoryLayout,
    "MEMORY_SEGMENT" : MemorySegment,
    "MOD_COMMON" : ModCommon,
    "MOD_PAR" : ModPar,
    "MODULE" : Module,
    "MONOTONY" : Monotony,
    "NO_AXIS_PTS_X" : NoAxisPtsX,
    "NO_AXIS_PTS_Y" : NoAxisPtsY,
    "NO_AXIS_PTS_Z" : NoAxisPtsZ,
    "NO_AXIS_PTS_4" : NoAxisPts4,
    "NO_AXIS_PTS_5" : NoAxisPts5,
    "NO_OF_INTERFACES" : NoOfInterfaces,
    "NO_RESCALE_X" : NoRescaleX,
    "NO_RESCALE_Y" : NoRescaleY,
    "NO_RESCALE_Z" : NoRescaleZ,
    "NO_RESCALE_4" : NoRescale4,
    "NO_RESCALE_5" : NoRescale5,
    "NUMBER" : Number,
    "OFFSET_X" : OffsetX,
    "OFFSET_Y" : OffsetY,
    "OFFSET_Z" : OffsetZ,
    "OFFSET_4" : Offset4,
    "OFFSET_5" : Offset5,
    "OUT_MEASUREMENT" : OutMeasurement,
    "PHONE_NO" : PhoneNo,
    "PHYS_UNIT" : PhysUnit,
    "PROJECT" : Project,
    "PROJECT_NO" : ProjectNo,
    "READ_ONLY" : ReadOnly,
    "READ_WRITE" : ReadWrite,
    "RECORD_LAYOUT" : RecordLayout,
    "REF_CHARACTERISTIC" : RefCharacteristic,
    "REF_GROUP" : RefGroup,
    "REF_MEASUREMENT" : RefMeasurement,
    "REF_MEMORY_SEGMENT" : RefMemorySegment,
    "REF_UNIT" : RefUnit,
    "RESERVED" : Reserved,
    "RIGHT_SHIFT" : RightShift,
    "RIP_ADDR_W" : RipAddrW,
    "RIP_ADDR_X" : RipAddrX,
    "RIP_ADDR_Y" : RipAddrY,
    "RIP_ADDR_Z" : RipAddrZ,
    "RIP_ADDR_4" : RipAddr4,
    "RIP_ADDR_5" : RipAddr5,
    "ROOT" : Root,
    "SHIFT_OP_X" : ShiftOpX,
    "SHIFT_OP_Y" : ShiftOpY,
    "SHIFT_OP_Z" : ShiftOpZ,
    "SHIFT_OP_4" : ShiftOp4,
    "SHIFT_OP_5" : ShiftOp5,
    "SIGN_EXTEND" : SignExtend,
    "SI_EXPONENTS" : SiExponents,
    "SRC_ADDR_X" : SrcAddrX,
    "SRC_ADDR_Y" : SrcAddrY,
    "SRC_ADDR_Z" : SrcAddrZ,
    "SRC_ADDR_4" : SrcAddr4,
    "SRC_ADDR_5" : SrcAddr5,
    "STATIC_RECORD_LAYOUT" : StaticRecordLayout,
    "STATUS_STRING_REF" : StatusStringRef,
    "STEP_SIZE" : StepSize,
    "SUB_FUNCTION" : SubFunction,
    "SUB_GROUP" : SubGroup,
    "SUPPLIER" : Supplier,
    "SYMBOL_LINK" : SymbolLink,
    "SYSTEM_CONSTANT" : SystemConstant,
    "S_REC_LAYOUT" : SRecLayout,
    "UNIT" : Unit,
    "UNIT_CONVERSION" : UnitConversion,
    "USER" : User,
    "USER_RIGHTS" : UserRights,
    "VAR_ADDRESS" : VarAddress,
    "VAR_CHARACTERISTIC" : VarCharacteristic,
    "VAR_CRITERION" : VarCriterion,
    "VAR_FORBIDDEN_COMB" : VarForbiddenComb,
    "VAR_MEASUREMENT" : VarMeasurement,
    "VAR_NAMING" : VarNaming,
    "VAR_SELECTION_CHARACTERISTIC" : VarSelectionCharacteristic,
    "VAR_SEPARATOR" : VarSeparator,
    "VARIANT_CODING" : VariantCoding,
    "VERSION" : Version,
    "VIRTUAL" : Virtual,
    "VIRTUAL_CHARACTERISTIC" : VirtualCharacteristic,
}

def instanceFactory(className, **kws):
    """Create an instance of a given class.
    """
    klass = KEYWORD_MAP.get(className)
    inst = klass()
    inst.attrs = []
    for k, v in kws.items():
        k = "{}{}".format(k[0].lower(), k[1 : ])
        setattr(inst, k, v.value)
        inst.attrs.append(k)
    inst.children = []
    return inst
