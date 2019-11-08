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

DB_EXTENSION    = "a2ldb"

CACHE_SIZE      = 4 # MB
PAGE_SIZE       = mmap.PAGESIZE


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
        for name, value in [(n, getattr(self, n)) for n in columns]:
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

class AlignmentByteAssociation(Base):

    __tablename__ = "alignment_byte_association"

    discriminator = Column(types.String)
    __mapper_args__ = {"polymorphic_on": discriminator}


class AlignmentByte(Base):
    """
    """
    association_id = Column(types.Integer, ForeignKey("alignment_byte_association.rid"))
    association = relationship("AlignmentByteAssociation", backref="alignment_bytes")
    parent = association_proxy("association", "parent")

    alignmentBorder = StdUShort()


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

        cls.alignment_bytes = association_proxy(
            "alignment_byte_association",
            "alignment_bytes",
            creator = lambda alignment_bytes: assoc_cls(alignment_bytes = alignment_bytes),
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
    association_id = Column(types.Integer, ForeignKey("alignment_float32_ieee_association.rid"))
    association = relationship("AlignmentFloat32IeeeAssociation", backref="alignment_float32_ieees")
    parent = association_proxy("association", "parent")

    alignmentBorder = StdUShort()


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

        cls.alignment_float32_ieees = association_proxy(
            "alignment_float32_ieee_association",
            "alignment_float32_ieees",
            creator = lambda alignment_float32_ieees: assoc_cls(alignment_float32_ieees = alignment_float32_ieees),
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
    association_id = Column(types.Integer, ForeignKey("alignment_float64_ieee_association.rid"))
    association = relationship("AlignmentFloat64IeeeAssociation", backref="alignment_float64_ieees")
    parent = association_proxy("association", "parent")

    alignmentBorder = StdUShort()


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

        cls.alignment_float64_ieees = association_proxy(
            "alignment_float64_ieee_association",
            "alignment_float64_ieees",
            creator = lambda alignment_float64_ieees: assoc_cls(alignment_float64_ieees = alignment_float64_ieees),
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
    association_id = Column(types.Integer, ForeignKey("alignment_int64_association.rid"))
    association = relationship("AlignmentInt64Association", backref="alignment_int64s")
    parent = association_proxy("association", "parent")

    alignmentBorder = StdUShort()


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

        cls.alignment_int64s = association_proxy(
            "alignment_int64_association",
            "alignment_int64s",
            creator = lambda alignment_int64s: assoc_cls(alignment_int64s = alignment_int64s),
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
    association_id = Column(types.Integer, ForeignKey("alignment_long_association.rid"))
    association = relationship("AlignmentLongAssociation", backref="alignment_longs")
    parent = association_proxy("association", "parent")

    alignmentBorder = StdUShort()


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

        cls.alignment_longs = association_proxy(
            "alignment_long_association",
            "alignment_longs",
            creator = lambda alignment_longs: assoc_cls(alignment_longs = alignment_longs),
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
    association_id = Column(types.Integer, ForeignKey("alignment_word_association.rid"))
    association = relationship("AlignmentWordAssociation", backref="alignment_words")
    parent = association_proxy("association", "parent")

    alignmentBorder = StdUShort()


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

        cls.alignment_words = association_proxy(
            "alignment_word_association",
            "alignment_words",
            creator = lambda alignment_words: assoc_cls(alignment_words = alignment_words),
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
    association_id = Column(types.Integer, ForeignKey("annotation_association.rid"))
    association = relationship("AnnotationAssociation", backref="annotations")
    parent = association_proxy("association", "parent")


    annotation_label = relationship("AnnotationLabel", back_populates = "annotation", uselist = False)
    annotation_origin = relationship("AnnotationOrigin", back_populates = "annotation", uselist = False)
    annotation_text = relationship("AnnotationText", back_populates = "annotation", uselist = False)


class AnnotationLabel(Base):
    """
    """
    __tablename__ = "annotation_label"

    label = StdString()
    _annotation_rid = Column(types.Integer, ForeignKey("annotation.rid"))
    annotation = relationship("Annotation", back_populates = "annotation_label")


class AnnotationOrigin(Base):
    """
    """
    __tablename__ = "annotation_origin"

    origin = StdString()
    _annotation_rid = Column(types.Integer, ForeignKey("annotation.rid"))
    annotation = relationship("Annotation", back_populates = "annotation_origin")


class AnnotationText(Base):
    """
    """
    __tablename__ = "annotation_text"

    text = StdString()
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

        cls.annotations = association_proxy(
            "annotation_association",
            "annotations",
            creator = lambda annotations: assoc_cls(annotations = annotations),
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
    association_id = Column(types.Integer, ForeignKey("bit_mask_association.rid"))
    association = relationship("BitMaskAssociation", backref="bit_masks")
    parent = association_proxy("association", "parent")

    mask = StdULong()


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

        cls.bit_masks = association_proxy(
            "bit_mask_association",
            "bit_masks",
            creator = lambda bit_masks: assoc_cls(bit_masks = bit_masks),
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
    association_id = Column(types.Integer, ForeignKey("byte_order_association.rid"))
    association = relationship("ByteOrderAssociation", backref="byte_orders")
    parent = association_proxy("association", "parent")

    byteOrder = StdString()


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

        cls.byte_orders = association_proxy(
            "byte_order_association",
            "byte_orders",
            creator = lambda byte_orders: assoc_cls(byte_orders = byte_orders),
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
    association_id = Column(types.Integer, ForeignKey("calibration_access_association.rid"))
    association = relationship("CalibrationAccessAssociation", backref="calibration_access")
    parent = association_proxy("association", "parent")

    type = StdString()


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
    association_id = Column(types.Integer, ForeignKey("default_value_association.rid"))
    association = relationship("DefaultValueAssociation", backref="default_values")
    parent = association_proxy("association", "parent")

    display_String = StdString()


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

        cls.default_values = association_proxy(
            "default_value_association",
            "default_values",
            creator = lambda default_values: assoc_cls(default_values = default_values),
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
    association_id = Column(types.Integer, ForeignKey("deposit_association.rid"))
    association = relationship("DepositAssociation", backref="deposits")
    parent = association_proxy("association", "parent")

    mode = StdString()


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

        cls.deposits = association_proxy(
            "deposit_association",
            "deposits",
            creator = lambda deposits: assoc_cls(deposits = deposits),
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
    association_id = Column(types.Integer, ForeignKey("discrete_association.rid"))
    association = relationship("DiscreteAssociation", backref="discretes")
    parent = association_proxy("association", "parent")



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

        cls.discretes = association_proxy(
            "discrete_association",
            "discretes",
            creator = lambda discretes: assoc_cls(discretes = discretes),
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
    association_id = Column(types.Integer, ForeignKey("display_identifier_association.rid"))
    association = relationship("DisplayIdentifierAssociation", backref="display_identifiers")
    parent = association_proxy("association", "parent")

    display_Name = StdIdent()


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

        cls.display_identifiers = association_proxy(
            "display_identifier_association",
            "display_identifiers",
            creator = lambda display_identifiers: assoc_cls(display_identifiers = display_identifiers),
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
    association_id = Column(types.Integer, ForeignKey("ecu_address_extension_association.rid"))
    association = relationship("EcuAddressExtensionAssociation", backref="ecu_address_extensions")
    parent = association_proxy("association", "parent")

    extension = StdShort()


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

        cls.ecu_address_extensions = association_proxy(
            "ecu_address_extension_association",
            "ecu_address_extensions",
            creator = lambda ecu_address_extensions: assoc_cls(ecu_address_extensions = ecu_address_extensions),
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
    association_id = Column(types.Integer, ForeignKey("extended_limits_association.rid"))
    association = relationship("ExtendedLimitsAssociation", backref="extended_limits")
    parent = association_proxy("association", "parent")

    lowerLimit = StdFloat()
    upperLimit = StdFloat()


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
    association_id = Column(types.Integer, ForeignKey("format_association.rid"))
    association = relationship("FormatAssociation", backref="formats")
    parent = association_proxy("association", "parent")

    formatString = StdString()


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

        cls.formats = association_proxy(
            "format_association",
            "formats",
            creator = lambda formats: assoc_cls(formats = formats),
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
    association_id = Column(types.Integer, ForeignKey("function_list_association.rid"))
    association = relationship("FunctionListAssociation", backref="function_lists")
    parent = association_proxy("association", "parent")

    name = StdIdent()


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

        cls.function_lists = association_proxy(
            "function_list_association",
            "function_lists",
            creator = lambda function_lists: assoc_cls(function_lists = function_lists),
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
    association_id = Column(types.Integer, ForeignKey("guard_rails_association.rid"))
    association = relationship("GuardRailsAssociation", backref="guard_rails")
    parent = association_proxy("association", "parent")



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
    association_id = Column(types.Integer, ForeignKey("if_data_association.rid"))
    association = relationship("IfDataAssociation", backref="if_datas")
    parent = association_proxy("association", "parent")

    name = StdIdent()


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

        cls.if_datas = association_proxy(
            "if_data_association",
            "if_datas",
            creator = lambda if_datas: assoc_cls(if_datas = if_datas),
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
    association_id = Column(types.Integer, ForeignKey("matrix_dim_association.rid"))
    association = relationship("MatrixDimAssociation", backref="matrix_dims")
    parent = association_proxy("association", "parent")

    xDim = StdUShort()
    yDim = StdUShort()
    zDim = StdUShort()


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

        cls.matrix_dims = association_proxy(
            "matrix_dim_association",
            "matrix_dims",
            creator = lambda matrix_dims: assoc_cls(matrix_dims = matrix_dims),
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
    association_id = Column(types.Integer, ForeignKey("max_refresh_association.rid"))
    association = relationship("MaxRefreshAssociation", backref="max_refreshs")
    parent = association_proxy("association", "parent")

    scalingUnit = StdUShort()
    rate = StdULong()


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

        cls.max_refreshs = association_proxy(
            "max_refresh_association",
            "max_refreshs",
            creator = lambda max_refreshs: assoc_cls(max_refreshs = max_refreshs),
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
    association_id = Column(types.Integer, ForeignKey("monotony_association.rid"))
    association = relationship("MonotonyAssociation", backref="monotonys")
    parent = association_proxy("association", "parent")

    monotony = StdString()


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

        cls.monotonys = association_proxy(
            "monotony_association",
            "monotonys",
            creator = lambda monotonys: assoc_cls(monotonys = monotonys),
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
    association_id = Column(types.Integer, ForeignKey("phys_unit_association.rid"))
    association = relationship("PhysUnitAssociation", backref="phys_units")
    parent = association_proxy("association", "parent")

    unit = StdString()


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

        cls.phys_units = association_proxy(
            "phys_unit_association",
            "phys_units",
            creator = lambda phys_units: assoc_cls(phys_units = phys_units),
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
    association_id = Column(types.Integer, ForeignKey("read_only_association.rid"))
    association = relationship("ReadOnlyAssociation", backref="read_onlys")
    parent = association_proxy("association", "parent")



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

        cls.read_onlys = association_proxy(
            "read_only_association",
            "read_onlys",
            creator = lambda read_onlys: assoc_cls(read_onlys = read_onlys),
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
    association_id = Column(types.Integer, ForeignKey("ref_characteristic_association.rid"))
    association = relationship("RefCharacteristicAssociation", backref="ref_characteristics")
    parent = association_proxy("association", "parent")

    identifier = StdIdent()


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

        cls.ref_characteristics = association_proxy(
            "ref_characteristic_association",
            "ref_characteristics",
            creator = lambda ref_characteristics: assoc_cls(ref_characteristics = ref_characteristics),
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
    association_id = Column(types.Integer, ForeignKey("ref_memory_segment_association.rid"))
    association = relationship("RefMemorySegmentAssociation", backref="ref_memory_segments")
    parent = association_proxy("association", "parent")

    name = StdIdent()


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

        cls.ref_memory_segments = association_proxy(
            "ref_memory_segment_association",
            "ref_memory_segments",
            creator = lambda ref_memory_segments: assoc_cls(ref_memory_segments = ref_memory_segments),
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
    association_id = Column(types.Integer, ForeignKey("ref_unit_association.rid"))
    association = relationship("RefUnitAssociation", backref="ref_units")
    parent = association_proxy("association", "parent")

    unit = StdIdent()


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

        cls.ref_units = association_proxy(
            "ref_unit_association",
            "ref_units",
            creator = lambda ref_units: assoc_cls(ref_units = ref_units),
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
    association_id = Column(types.Integer, ForeignKey("step_size_association.rid"))
    association = relationship("StepSizeAssociation", backref="step_sizes")
    parent = association_proxy("association", "parent")

    stepSize = StdFloat()


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

        cls.step_sizes = association_proxy(
            "step_size_association",
            "step_sizes",
            creator = lambda step_sizes: assoc_cls(step_sizes = step_sizes),
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
    association_id = Column(types.Integer, ForeignKey("symbol_link_association.rid"))
    association = relationship("SymbolLinkAssociation", backref="symbol_links")
    parent = association_proxy("association", "parent")

    symbolName = StdString()
    offset = StdLong()


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

        cls.symbol_links = association_proxy(
            "symbol_link_association",
            "symbol_links",
            creator = lambda symbol_links: assoc_cls(symbol_links = symbol_links),
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
    association_id = Column(types.Integer, ForeignKey("version_association.rid"))
    association = relationship("VersionAssociation", backref="versions")
    parent = association_proxy("association", "parent")

    versionIdentifier = StdString()


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

        cls.versions = association_proxy(
            "version_association",
            "versions",
            creator = lambda versions: assoc_cls(versions = versions),
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


class A2mlVersion(Base):
    """
    """
    __tablename__ = "a2ml_version"

    versionNo = StdUShort()
    upgradeNo = StdUShort()


class Project(Base):
    """
    """
    __tablename__ = "project"

    name = StdIdent()
    longIdentifier = StdString()
    # optional part
    header = relationship("Header", back_populates = "project", uselist = False)
    modules = relationship("Module", back_populates = "project", uselist = True)


class Header(Base, HasVersions):
    """
    """
    __tablename__ = "header"

    comment = StdString()
    # optional part
    project_no = relationship("ProjectNo", back_populates = "header", uselist = False)
    _project_rid = Column(types.Integer, ForeignKey("project.rid"))
    project = relationship("Project", back_populates = "header")


class ProjectNo(Base):
    """
    """
    __tablename__ = "project_no"

    projectNumber = StdIdent()
    _header_rid = Column(types.Integer, ForeignKey("header.rid"))
    header = relationship("Header", back_populates = "project_no")


class Module(Base, HasIfDatas):
    """
    """
    __tablename__ = "module"

    name = StdIdent()
    longIdentifier = StdString()
    # optional part
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
    # optional part
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
    # optional part
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
    # optional part
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
    _axis_descr_rid = Column(types.Integer, ForeignKey("axis_descr.rid"))
    axis_descr = relationship("AxisDescr", back_populates = "axis_pts_ref")


class CurveAxisRef(Base):
    """
    """
    __tablename__ = "curve_axis_ref"

    curveAxis = StdIdent()
    _axis_descr_rid = Column(types.Integer, ForeignKey("axis_descr.rid"))
    axis_descr = relationship("AxisDescr", back_populates = "curve_axis_ref")


class FixAxisPar(Base):
    """
    """
    __tablename__ = "fix_axis_par"

    offset = StdShort()
    shift = StdShort()
    numberapo = StdUShort()
    _axis_descr_rid = Column(types.Integer, ForeignKey("axis_descr.rid"))
    axis_descr = relationship("AxisDescr", back_populates = "fix_axis_par")


class FixAxisParDist(Base):
    """
    """
    __tablename__ = "fix_axis_par_dist"

    offset = StdShort()
    distance = StdShort()
    numberapo = StdUShort()
    _axis_descr_rid = Column(types.Integer, ForeignKey("axis_descr.rid"))
    axis_descr = relationship("AxisDescr", back_populates = "fix_axis_par_dist")


class FixAxisParList(Base):
    """
    """
    __tablename__ = "fix_axis_par_list"

    axisPts_Value = StdFloat()
    _axis_descr_rid = Column(types.Integer, ForeignKey("axis_descr.rid"))
    axis_descr = relationship("AxisDescr", back_populates = "fix_axis_par_list")


class MaxGrad(Base):
    """
    """
    __tablename__ = "max_grad"

    maxGradient = StdFloat()
    _axis_descr_rid = Column(types.Integer, ForeignKey("axis_descr.rid"))
    axis_descr = relationship("AxisDescr", back_populates = "max_grad")


class ComparisonQuantity(Base):
    """
    """
    __tablename__ = "comparison_quantity"

    name = StdIdent()
    _characteristic_rid = Column(types.Integer, ForeignKey("characteristic.rid"))
    characteristic = relationship("Characteristic", back_populates = "comparison_quantity")


class DependentCharacteristic(Base):
    """
    """
    __tablename__ = "dependent_characteristic"

    formula = StdString()
    characteristic = StdIdent()
    _characteristic_rid = Column(types.Integer, ForeignKey("characteristic.rid"))
    characteristic = relationship("Characteristic", back_populates = "dependent_characteristic")


class MapList(Base):
    """
    """
    __tablename__ = "map_list"

    name = StdIdent()
    _characteristic_rid = Column(types.Integer, ForeignKey("characteristic.rid"))
    characteristic = relationship("Characteristic", back_populates = "map_list")


class Number(Base):
    """
    """
    __tablename__ = "number"

    number = StdUShort()
    _characteristic_rid = Column(types.Integer, ForeignKey("characteristic.rid"))
    characteristic = relationship("Characteristic", back_populates = "number")


class VirtualCharacteristic(Base):
    """
    """
    __tablename__ = "virtual_characteristic"

    formula = StdString()
    characteristic = StdIdent()
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
    # optional part
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
    _compu_method_rid = Column(types.Integer, ForeignKey("compu_method.rid"))
    compu_method = relationship("CompuMethod", back_populates = "coeffs")


class CoeffsLinear(Base):
    """
    """
    __tablename__ = "coeffs_linear"

    a = StdFloat()
    b = StdFloat()
    _compu_method_rid = Column(types.Integer, ForeignKey("compu_method.rid"))
    compu_method = relationship("CompuMethod", back_populates = "coeffs_linear")


class CompuTabRef(Base):
    """
    """
    __tablename__ = "compu_tab_ref"

    conversionTable = StdIdent()
    _compu_method_rid = Column(types.Integer, ForeignKey("compu_method.rid"))
    compu_method = relationship("CompuMethod", back_populates = "compu_tab_ref")


class Formula(Base):
    """
    """
    __tablename__ = "formula"

    f_x = StdString()
    # optional part
    formula_inv = relationship("FormulaInv", back_populates = "formula", uselist = False)
    _compu_method_rid = Column(types.Integer, ForeignKey("compu_method.rid"))
    compu_method = relationship("CompuMethod", back_populates = "formula")


class FormulaInv(Base):
    """
    """
    __tablename__ = "formula_inv"

    g_x = StdString()
    _formula_rid = Column(types.Integer, ForeignKey("formula.rid"))
    formula = relationship("Formula", back_populates = "formula_inv")


class StatusStringRef(Base):
    """
    """
    __tablename__ = "status_string_ref"

    conversionTable = StdIdent()
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
    # optional part
    default_value_numeric = relationship("DefaultValueNumeric", back_populates = "compu_tab", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "compu_tabs")


class DefaultValueNumeric(Base):
    """
    """
    __tablename__ = "default_value_numeric"

    display_Value = StdFloat()
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
    # optional part
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "compu_vtabs")


class CompuVtabRange(Base, HasDefaultValues):
    """
    """
    __tablename__ = "compu_vtab_range"

    name = StdIdent()
    longIdentifier = StdString()
    numberValueTriples = StdUShort()
    # optional part
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
    # optional part
    frame_measurement = relationship("FrameMeasurement", back_populates = "frame", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "frame")


class FrameMeasurement(Base):
    """
    """
    __tablename__ = "frame_measurement"

    identifier = StdIdent()
    _frame_rid = Column(types.Integer, ForeignKey("frame.rid"))
    frame = relationship("Frame", back_populates = "frame_measurement")


class Function(Base, HasAnnotations, HasIfDatas, HasRefCharacteristics):
    """
    """
    __tablename__ = "function"

    name = StdIdent()
    longIdentifier = StdString()
    # optional part
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

    identifier = StdIdent()
    _function_rid = Column(types.Integer, ForeignKey("function.rid"))
    function = relationship("Function", back_populates = "def_characteristic")


class FunctionVersion(Base):
    """
    """
    __tablename__ = "function_version"

    versionIdentifier = StdString()
    _function_rid = Column(types.Integer, ForeignKey("function.rid"))
    function = relationship("Function", back_populates = "function_version")


class InMeasurement(Base):
    """
    """
    __tablename__ = "in_measurement"

    identifier = StdIdent()
    _function_rid = Column(types.Integer, ForeignKey("function.rid"))
    function = relationship("Function", back_populates = "in_measurement")


class LocMeasurement(Base):
    """
    """
    __tablename__ = "loc_measurement"

    identifier = StdIdent()
    _function_rid = Column(types.Integer, ForeignKey("function.rid"))
    function = relationship("Function", back_populates = "loc_measurement")


class OutMeasurement(Base):
    """
    """
    __tablename__ = "out_measurement"

    identifier = StdIdent()
    _function_rid = Column(types.Integer, ForeignKey("function.rid"))
    function = relationship("Function", back_populates = "out_measurement")


class SubFunction(Base):
    """
    """
    __tablename__ = "sub_function"

    identifier = StdIdent()
    _function_rid = Column(types.Integer, ForeignKey("function.rid"))
    function = relationship("Function", back_populates = "sub_function")


class Group(Base, HasAnnotations, HasFunctionLists, HasIfDatas, HasRefCharacteristics):
    """
    """
    __tablename__ = "group"

    groupName = StdIdent()
    groupLongIdentifier = StdString()
    # optional part
    ref_measurement = relationship("RefMeasurement", back_populates = "group", uselist = False)
    root = relationship("Root", back_populates = "group", uselist = False)
    sub_group = relationship("SubGroup", back_populates = "group", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "groups")


class RefMeasurement(Base):
    """
    """
    __tablename__ = "ref_measurement"

    identifier = StdIdent()
    _group_rid = Column(types.Integer, ForeignKey("group.rid"))
    group = relationship("Group", back_populates = "ref_measurement")


class Root(Base):
    """
    """
    __tablename__ = "root"

    _group_rid = Column(types.Integer, ForeignKey("group.rid"))
    group = relationship("Group", back_populates = "root")


class SubGroup(Base):
    """
    """
    __tablename__ = "sub_group"

    identifier = StdIdent()
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
    # optional part
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
    _measurement_rid = Column(types.Integer, ForeignKey("measurement.rid"))
    measurement = relationship("Measurement", back_populates = "array_size")


class BitOperation(Base):
    """
    """
    __tablename__ = "bit_operation"

    # optional part
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
    _bit_operation_rid = Column(types.Integer, ForeignKey("bit_operation.rid"))
    bit_operation = relationship("BitOperation", back_populates = "left_shift")


class RightShift(Base):
    """
    """
    __tablename__ = "right_shift"

    bitcount = StdULong()
    _bit_operation_rid = Column(types.Integer, ForeignKey("bit_operation.rid"))
    bit_operation = relationship("BitOperation", back_populates = "right_shift")


class SignExtend(Base):
    """
    """
    __tablename__ = "sign_extend"

    _bit_operation_rid = Column(types.Integer, ForeignKey("bit_operation.rid"))
    bit_operation = relationship("BitOperation", back_populates = "sign_extend")


class EcuAddress(Base):
    """
    """
    __tablename__ = "ecu_address"

    address = StdULong()
    _measurement_rid = Column(types.Integer, ForeignKey("measurement.rid"))
    measurement = relationship("Measurement", back_populates = "ecu_address")


class ErrorMask(Base):
    """
    """
    __tablename__ = "error_mask"

    mask = StdULong()
    _measurement_rid = Column(types.Integer, ForeignKey("measurement.rid"))
    measurement = relationship("Measurement", back_populates = "error_mask")


class Layout(Base):
    """
    """
    __tablename__ = "layout"

    indexMode = StdString()
    _measurement_rid = Column(types.Integer, ForeignKey("measurement.rid"))
    measurement = relationship("Measurement", back_populates = "layout")


class ReadWrite(Base):
    """
    """
    __tablename__ = "read_write"

    _measurement_rid = Column(types.Integer, ForeignKey("measurement.rid"))
    measurement = relationship("Measurement", back_populates = "read_write")


class Virtual(Base):
    """
    """
    __tablename__ = "virtual"

    measuringChannel = StdIdent()
    _measurement_rid = Column(types.Integer, ForeignKey("measurement.rid"))
    measurement = relationship("Measurement", back_populates = "virtual")


class ModCommon(Base, HasAlignmentBytes, HasAlignmentFloat32Ieees, HasAlignmentFloat64Ieees, HasAlignmentInt64s, HasAlignmentLongs, HasAlignmentWords, HasByteOrders, HasDeposits):
    """
    """
    __tablename__ = "mod_common"

    comment = StdString()
    # optional part
    data_size = relationship("DataSize", back_populates = "mod_common", uselist = False)
    s_rec_layout = relationship("SRecLayout", back_populates = "mod_common", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "mod_common")


class DataSize(Base):
    """
    """
    __tablename__ = "data_size"

    size = StdUShort()
    _mod_common_rid = Column(types.Integer, ForeignKey("mod_common.rid"))
    mod_common = relationship("ModCommon", back_populates = "data_size")


class SRecLayout(Base):
    """
    """
    __tablename__ = "s_rec_layout"

    name = StdIdent()
    _mod_common_rid = Column(types.Integer, ForeignKey("mod_common.rid"))
    mod_common = relationship("ModCommon", back_populates = "s_rec_layout")


class ModPar(Base, HasVersions):
    """
    """
    __tablename__ = "mod_par"

    comment = StdString()
    # optional part
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
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "addr_epks")


class CalibrationMethod(Base):
    """
    """
    __tablename__ = "calibration_method"

    method = StdString()
    version = StdULong()
    # optional part
    calibration_handles = relationship("CalibrationHandle", back_populates = "calibration_method", uselist = True)
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "calibration_methods")


class CalibrationHandle(Base):
    """
    """
    __tablename__ = "calibration_handle"

    handle = StdLong()
    # optional part
    calibration_handle_text = relationship("CalibrationHandleText", back_populates = "calibration_handle", uselist = False)
    _calibration_method_rid = Column(types.Integer, ForeignKey("calibration_method.rid"))
    calibration_method = relationship("CalibrationMethod", back_populates = "calibration_handles")


class CalibrationHandleText(Base):
    """
    """
    __tablename__ = "calibration_handle_text"

    text = StdString()
    _calibration_handle_rid = Column(types.Integer, ForeignKey("calibration_handle.rid"))
    calibration_handle = relationship("CalibrationHandle", back_populates = "calibration_handle_text")


class CpuType(Base):
    """
    """
    __tablename__ = "cpu_type"

    cPU = StdString()
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "cpu_type")


class Customer(Base):
    """
    """
    __tablename__ = "customer"

    customer = StdString()
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "customer")


class CustomerNo(Base):
    """
    """
    __tablename__ = "customer_no"

    number = StdString()
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "customer_no")


class Ecu(Base):
    """
    """
    __tablename__ = "ecu"

    controlUnit = StdString()
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "ecu")


class EcuCalibrationOffset(Base):
    """
    """
    __tablename__ = "ecu_calibration_offset"

    offset = StdLong()
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "ecu_calibration_offset")


class Epk(Base):
    """
    """
    __tablename__ = "epk"

    identifier = StdString()
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "epk")


class MemoryLayout(Base, HasIfDatas):
    """
    """
    __tablename__ = "memory_layout"

    prgType = StdString()
    address = StdULong()
    size = StdULong()
    offset0 = StdLong()
    offset1 = StdLong()
    offset2 = StdLong()
    offset3 = StdLong()
    offset4 = StdLong()
    # optional part
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
    offset0 = StdLong()
    offset1 = StdLong()
    offset2 = StdLong()
    offset3 = StdLong()
    offset4 = StdLong()
    # optional part
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "memory_segments")


class NoOfInterfaces(Base):
    """
    """
    __tablename__ = "no_of_interfaces"

    num = StdUShort()
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "no_of_interfaces")


class PhoneNo(Base):
    """
    """
    __tablename__ = "phone_no"

    telnum = StdString()
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "phone_no")


class Supplier(Base):
    """
    """
    __tablename__ = "supplier"

    manufacturer = StdString()
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "supplier")


class SystemConstant(Base):
    """
    """
    __tablename__ = "system_constant"

    name = StdString()
    value = StdString()
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "system_constants")


class User(Base):
    """
    """
    __tablename__ = "user"

    userName = StdString()
    _mod_par_rid = Column(types.Integer, ForeignKey("mod_par.rid"))
    mod_par = relationship("ModPar", back_populates = "user")


class RecordLayout(Base, HasAlignmentBytes, HasAlignmentFloat32Ieees, HasAlignmentFloat64Ieees, HasAlignmentInt64s, HasAlignmentLongs, HasAlignmentWords):
    """
    """
    __tablename__ = "record_layout"

    name = StdIdent()
    # optional part
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
    adressing = StdIdent()
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
    adressing = StdIdent()
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
    adressing = StdIdent()
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
    adressing = StdIdent()
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
    adressing = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "axis_rescale_5")


class DistOpX(Base):
    """
    """
    __tablename__ = "dist_op_x"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "dist_op_x")


class DistOpY(Base):
    """
    """
    __tablename__ = "dist_op_y"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "dist_op_y")


class DistOpZ(Base):
    """
    """
    __tablename__ = "dist_op_z"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "dist_op_z")


class DistOp4(Base):
    """
    """
    __tablename__ = "dist_op_4"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "dist_op_4")


class DistOp5(Base):
    """
    """
    __tablename__ = "dist_op_5"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "dist_op_5")


class FixNoAxisPtsX(Base):
    """
    """
    __tablename__ = "fix_no_axis_pts_x"

    numberOfAxisPoints = StdUShort()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "fix_no_axis_pts_x")


class FixNoAxisPtsY(Base):
    """
    """
    __tablename__ = "fix_no_axis_pts_y"

    numberOfAxisPoints = StdUShort()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "fix_no_axis_pts_y")


class FixNoAxisPtsZ(Base):
    """
    """
    __tablename__ = "fix_no_axis_pts_z"

    numberOfAxisPoints = StdUShort()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "fix_no_axis_pts_z")


class FixNoAxisPts4(Base):
    """
    """
    __tablename__ = "fix_no_axis_pts_4"

    numberOfAxisPoints = StdUShort()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "fix_no_axis_pts_4")


class FixNoAxisPts5(Base):
    """
    """
    __tablename__ = "fix_no_axis_pts_5"

    numberOfAxisPoints = StdUShort()
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
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "fnc_values")


class Identification(Base):
    """
    """
    __tablename__ = "identification"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "identification")


class NoAxisPtsX(Base):
    """
    """
    __tablename__ = "no_axis_pts_x"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_axis_pts_x")


class NoAxisPtsY(Base):
    """
    """
    __tablename__ = "no_axis_pts_y"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_axis_pts_y")


class NoAxisPtsZ(Base):
    """
    """
    __tablename__ = "no_axis_pts_z"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_axis_pts_z")


class NoAxisPts4(Base):
    """
    """
    __tablename__ = "no_axis_pts_4"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_axis_pts_4")


class NoAxisPts5(Base):
    """
    """
    __tablename__ = "no_axis_pts_5"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_axis_pts_5")


class StaticRecordLayout(Base):
    """
    """
    __tablename__ = "static_record_layout"

    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "static_record_layout")


class NoRescaleX(Base):
    """
    """
    __tablename__ = "no_rescale_x"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_rescale_x")


class NoRescaleY(Base):
    """
    """
    __tablename__ = "no_rescale_y"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_rescale_y")


class NoRescaleZ(Base):
    """
    """
    __tablename__ = "no_rescale_z"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_rescale_z")


class NoRescale4(Base):
    """
    """
    __tablename__ = "no_rescale_4"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_rescale_4")


class NoRescale5(Base):
    """
    """
    __tablename__ = "no_rescale_5"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "no_rescale_5")


class OffsetX(Base):
    """
    """
    __tablename__ = "offset_x"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "offset_x")


class OffsetY(Base):
    """
    """
    __tablename__ = "offset_y"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "offset_y")


class OffsetZ(Base):
    """
    """
    __tablename__ = "offset_z"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "offset_z")


class Offset4(Base):
    """
    """
    __tablename__ = "offset_4"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "offset_4")


class Offset5(Base):
    """
    """
    __tablename__ = "offset_5"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "offset_5")


class Reserved(Base):
    """
    """
    __tablename__ = "reserved"

    position = StdUShort()
    dataSize = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "reserveds")


class RipAddrW(Base):
    """
    """
    __tablename__ = "rip_addr_w"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "rip_addr_w")


class RipAddrX(Base):
    """
    """
    __tablename__ = "rip_addr_x"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "rip_addr_x")


class RipAddrY(Base):
    """
    """
    __tablename__ = "rip_addr_y"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "rip_addr_y")


class RipAddrZ(Base):
    """
    """
    __tablename__ = "rip_addr_z"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "rip_addr_z")


class RipAddr4(Base):
    """
    """
    __tablename__ = "rip_addr_4"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "rip_addr_4")


class RipAddr5(Base):
    """
    """
    __tablename__ = "rip_addr_5"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "rip_addr_5")


class ShiftOpX(Base):
    """
    """
    __tablename__ = "shift_op_x"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "shift_op_x")


class ShiftOpY(Base):
    """
    """
    __tablename__ = "shift_op_y"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "shift_op_y")


class ShiftOpZ(Base):
    """
    """
    __tablename__ = "shift_op_z"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "shift_op_z")


class ShiftOp4(Base):
    """
    """
    __tablename__ = "shift_op_4"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "shift_op_4")


class ShiftOp5(Base):
    """
    """
    __tablename__ = "shift_op_5"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "shift_op_5")


class SrcAddrX(Base):
    """
    """
    __tablename__ = "src_addr_x"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "src_addr_x")


class SrcAddrY(Base):
    """
    """
    __tablename__ = "src_addr_y"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "src_addr_y")


class SrcAddrZ(Base):
    """
    """
    __tablename__ = "src_addr_z"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "src_addr_z")


class SrcAddr4(Base):
    """
    """
    __tablename__ = "src_addr_4"

    position = StdUShort()
    datatype = StdIdent()
    _record_layout_rid = Column(types.Integer, ForeignKey("record_layout.rid"))
    record_layout = relationship("RecordLayout", back_populates = "src_addr_4")


class SrcAddr5(Base):
    """
    """
    __tablename__ = "src_addr_5"

    position = StdUShort()
    datatype = StdIdent()
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
    # optional part
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
    _unit_rid = Column(types.Integer, ForeignKey("unit.rid"))
    unit = relationship("Unit", back_populates = "si_exponents")


class UnitConversion(Base):
    """
    """
    __tablename__ = "unit_conversion"

    gradient = StdFloat()
    offset = StdFloat()
    _unit_rid = Column(types.Integer, ForeignKey("unit.rid"))
    unit = relationship("Unit", back_populates = "unit_conversion")


class UserRights(Base, HasReadOnlys):
    """
    """
    __tablename__ = "user_rights"

    userLevelId = StdIdent()
    # optional part
    ref_groups = relationship("RefGroup", back_populates = "user_rights", uselist = True)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "user_rights")


class RefGroup(Base):
    """
    """
    __tablename__ = "ref_group"

    identifier = StdIdent()
    _user_rights_rid = Column(types.Integer, ForeignKey("user_rights.rid"))
    user_rights = relationship("UserRights", back_populates = "ref_groups")


class VariantCoding(Base):
    """
    """
    __tablename__ = "variant_coding"

    # optional part
    var_characteristics = relationship("VarCharacteristic", back_populates = "variant_coding", uselist = True)
    var_criterions = relationship("VarCriterion", back_populates = "variant_coding", uselist = True)
    var_forbidden_combs = relationship("VarForbiddenComb", back_populates = "variant_coding", uselist = True)
    var_naming = relationship("VarNaming", back_populates = "variant_coding", uselist = False)
    var_separator = relationship("VarSeparator", back_populates = "variant_coding", uselist = False)
    _module_rid = Column(types.Integer, ForeignKey("module.rid"))
    module = relationship("Module", back_populates = "variant_coding")


class VarCharacteristic(Base):
    """
    """
    __tablename__ = "var_characteristic"

    name = StdIdent()
    criterionName = StdIdent()
    # optional part
    var_address = relationship("VarAddress", back_populates = "var_characteristic", uselist = False)
    _variant_coding_rid = Column(types.Integer, ForeignKey("variant_coding.rid"))
    variant_coding = relationship("VariantCoding", back_populates = "var_characteristics")


class VarAddress(Base):
    """
    """
    __tablename__ = "var_address"

    address = StdULong()
    _var_characteristic_rid = Column(types.Integer, ForeignKey("var_characteristic.rid"))
    var_characteristic = relationship("VarCharacteristic", back_populates = "var_address")


class VarCriterion(Base):
    """
    """
    __tablename__ = "var_criterion"

    name = StdIdent()
    longIdentifier = StdString()
    value = StdIdent()
    # optional part
    var_measurement = relationship("VarMeasurement", back_populates = "var_criterion", uselist = False)
    var_selection_characteristic = relationship("VarSelectionCharacteristic", back_populates = "var_criterion", uselist = False)
    _variant_coding_rid = Column(types.Integer, ForeignKey("variant_coding.rid"))
    variant_coding = relationship("VariantCoding", back_populates = "var_criterions")


class VarMeasurement(Base):
    """
    """
    __tablename__ = "var_measurement"

    name = StdIdent()
    _var_criterion_rid = Column(types.Integer, ForeignKey("var_criterion.rid"))
    var_criterion = relationship("VarCriterion", back_populates = "var_measurement")


class VarSelectionCharacteristic(Base):
    """
    """
    __tablename__ = "var_selection_characteristic"

    name = StdIdent()
    _var_criterion_rid = Column(types.Integer, ForeignKey("var_criterion.rid"))
    var_criterion = relationship("VarCriterion", back_populates = "var_selection_characteristic")


class VarForbiddenComb(Base):
    """
    """
    __tablename__ = "var_forbidden_comb"

    criterionName = StdIdent()
    criterionValue = StdIdent()
    _variant_coding_rid = Column(types.Integer, ForeignKey("variant_coding.rid"))
    variant_coding = relationship("VariantCoding", back_populates = "var_forbidden_combs")


class VarNaming(Base):
    """
    """
    __tablename__ = "var_naming"

    tag = StdString()
    _variant_coding_rid = Column(types.Integer, ForeignKey("variant_coding.rid"))
    variant_coding = relationship("VariantCoding", back_populates = "var_naming")


class VarSeparator(Base):
    """
    """
    __tablename__ = "var_separator"

    separator = StdString()
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

