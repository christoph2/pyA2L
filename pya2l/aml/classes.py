#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Classes and factories regarding AML abstract syntax tree."""

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2021 by Christoph Schueler <cpu12.gems.googlemail.com>

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

   s. FLOSS-EXCEPTION.txt
"""
__author__ = "Christoph Schueler"
__version__ = "0.1.0"


import enum
import json

##
## Model Classes.
##
class Element:

    def __init__(self):
        pass


class Referrer:

    def __init__(self, category, identifier):
        self.category = category
        self.identifier = identifier

    def __str__(self):
        return "Referrer(category = '{}', identifier = '{}')".format(self.category, self.identifier)

    __repr__ = __str__


class Sequence:

    def __init__(self, elements: list):
        self._current_pos = 0
        self.elements = elements

    @property
    def current_pos(self):
        return self._current_pos


class AMLPredefinedTypes(enum.IntEnum):
    """"""

    PDT_CHAR = 0
    PDT_INT = 1
    PDT_LONG = 2
    PDT_UCHAR = 3
    PDT_UINT = 4
    PDT_ULONG = 5
    PDT_DOUBLE = 6
    PDT_FLOAT = 7


def map_predefined_type(name):
    MAP = {
        "char": AMLPredefinedTypes.PDT_CHAR,
        "int": AMLPredefinedTypes.PDT_INT,
        "long": AMLPredefinedTypes.PDT_LONG,
        "uchar": AMLPredefinedTypes.PDT_UCHAR,
        "uint": AMLPredefinedTypes.PDT_UINT,
        "ulong": AMLPredefinedTypes.PDT_ULONG,
        "double": AMLPredefinedTypes.PDT_DOUBLE,
        "float": AMLPredefinedTypes.PDT_FLOAT,
    }
    return MAP.get(name)


class BaseType:
    """

    """

    _is_block = False

    @staticmethod
    def _try(o):
        try:
            return o.__dict__
        except:
            return str(o)

    @property
    def is_block(self):
        return self._is_block

    def to_json(self):
        return json.dumps(self, default = lambda o: self._try(o), sort_keys=True, indent = 4,
            separators=(',',':')).replace('\n', '')


class Enumeration(BaseType):

    def __init__(self, name, enumerators):
        self.name = name
        self.enumerators = {e.tag: e.constant for e in enumerators}
        self._renumber_constants()

    def __repr__(self):
        return "Enumeration(name = '{}', enumerators = {})".format(
            self.name,
            self.enumerators
        )

    def __contains__(self, name):
        return name in self.enumerators

    def _renumber_constants(self):
        """ISO C/C++ like enumerator numbering.

        Note
        ----
        Descending orderered ``enum``s are not supported yet.
        """
        last_idx = 0
        for tag, value in sorted(self.enumerators.items(), key = lambda e: e[1] if not e[1] is None else 0):
            if value is None:
                self.enumerators[tag] = last_idx
                last_idx += 1
            else:
                last_idx = value + 1


class Enumerator(BaseType):
    def __init__(self, tag, constant):
        self.tag = tag
        self.constant = constant

    def __repr__(self):
        return "Enumerator(tag = {}, constant = {})".format(self.tag, self.constant)


class TaggedUnion(BaseType):
    def __init__(self, name, members):
        self.name = name
        self.members = members
        self.tags = {}
        for mem in members:
            if mem.member:
                key = mem.tag
                value = mem.member
            elif mem.block_definition:
                key = mem.block_definition.tag
                value = mem.block_definition
            self.tags[key] = value

    def __repr__(self):
        return "TaggedUnion(name = '{}', tags = {}, members = {})".format(
            self.name,
            sorted(list(self.tags)),
            self.members
        )


class TaggedUnionMember(BaseType):
    def __init__(self, tag, member, block_definition):
        self.tag = tag
        self.member = member
        self.block_definition = block_definition

    def __repr__(self):
        return "TaggedUnionMember(tag = {}, member = {}, block_definition = {})".format(
            self.tag, self.member, self.block_definition
        )


class Member(BaseType):
    def __init__(self, type_name, array_specifier):
        self.type_name = type_name
        self.array_specifier = array_specifier
        if type_name.type_.__class__.__name__ == "PredefinedType":
            self.type_name.type_.array_specifier = array_specifier

    def __repr__(self):
        return "Member(type_name = {}{})".format(
            self.type_name, self.array_specifier or ""
        )


class TypeName(BaseType):
    def __init__(self, tag, name, type_):
        self.tag = tag
        self.name = name
        self.type_ = type_

    def __repr__(self):
        return "TypeName(tag = {}, name = {}, type = {})".format(
            self.tag, self.name, self.type_
        )


class PredefinedType(BaseType):
    def __init__(self, type_):
        self.type_ = type_

    def __repr__(self):
        return "PredefinedType(type = {})".format(self.type_.name)


class StructType(BaseType):
    def __init__(self, name, members):
        self.name = name
        self.members = members

    def __repr__(self):
        return "StructType(name = '{}', members = {})".format(self.name, self.members)


class TaggedStructType(BaseType):
    def __init__(self, name, members):
        self.name = name
        self.members = members
        self.tags = {}
        for mem in members:
            if mem.taggedstruct_definition:
                self.tags[mem.taggedstruct_definition.tag] = mem
            elif mem.block_definition:
                self.tags[mem.block_definition.tag] = mem

    def __repr__(self):
        return "TaggedStructType(name = '{}', tags = {}, members = {})".format(
            self.name,
            list(sorted(self.tags.keys())),
            self.members
        )


class TaggedStructDefinition(BaseType):
    def __init__(self, tag, member, multiple):
        self.tag = tag
        self.member = member
        self.multiple = multiple

    def __repr__(self):
        return (
            "TaggedStructDefinition(tag = {}, member = {}, multiple = {})".format(
                self.tag, self.member, self.multiple
            )
        )


class StructMember(BaseType):
    def __init__(self, value, multiple):
        self.value = value
        self.multiple = multiple

    def __repr__(self):
        return "StructMember(value = {}, multiple = {})".format(
            self.value, self.multiple
        )


class TaggedStructMember(BaseType):
    def __init__(self, taggedstruct_definition, block_definition, multiple):
        self.taggedstruct_definition = taggedstruct_definition
        self.block_definition = block_definition
        self.multiple = multiple

    def __repr__(self):
        return "TaggedStructMember(taggedstruct_definition = {}, block_definition = {}, multiple = {})".format(
            self.taggedstruct_definition, self.block_definition, self.multiple
        )


class Declaration(BaseType):
    def __init__(self, block_definition, type_definition):
        self.block_definition = block_definition
        self.type_definition = type_definition

    def __repr__(self):
        return "Declaration(block_definition = {}, type_definition = {})".format(
            self.block_definition, self.type_definition
        )


class BlockDefinition(BaseType):

    _is_block = True

    def __init__(self, tag, type_name, member, multiple):
        self.tag = tag
        self.type_name = type_name
        self.member = member
        self.multiple = multiple

    @property
    def type_(self):
        return self.type_name.type_.__class__.__name__

    @property
    def definition(self):
        return self.type_name.type_

    def __repr__(self):
        return "BlockDefinition(tag = {}, type_name = {}, member = {} multiple = {})".format(
            self.tag, self.type_name, self.member, self.multiple
        )


class TypeDefinition(BaseType):
    def __init__(self, type_name):
        self.type_name = type_name

    def __repr__(self):
        return "TypeDefinition(type_name = {})".format(self.type_name)

##
## Factories.
##
def createEnumeration(name, enumerators, is_referrer = False):
    if is_referrer:
        return Referrer("Enumeration", name)
    else:
        return Enumeration(name, enumerators)


def createEnumerator(tag, constant):
    return Enumerator(tag, constant)


def createTaggedUnion(name, members, is_referrer = False):
    if is_referrer:
        return Referrer("TaggedUnion", name)
    else:
        return TaggedUnion(name, members)


def createTaggedUnionMember(tag, member, block_definition):
    return TaggedUnionMember(tag, member, block_definition)


def createMember(type_name, array_specifier):
    return Member(type_name, array_specifier)


def createTypeName(tag, name, type_):
    return TypeName(tag, name, type_)


def createPredefinedType(name):
    return PredefinedType(map_predefined_type(name))


def createStructType(name, members, is_referrer = False):
    if is_referrer:
        return Referrer("StructType", name)
    else:
        return StructType(name, members)


def createTaggedStructType(name, members, is_referrer = False):
    if is_referrer:
        return Referrer("TaggedStructType", name)
    else:
        return TaggedStructType(name, members)


def createTaggedStructDefinition(tag, member, multiple):
    return TaggedStructDefinition(tag, member, multiple)


def createStructMember(value, multiple):
    return StructMember(value, multiple)


def createTaggedStructMember(taggedstruct_definition, block_definition, multiple):
    return TaggedStructMember(taggedstruct_definition, block_definition, multiple)


def createDeclaration(block_definition, type_definition):
    return Declaration(block_definition, type_definition)


def createBlockDefinition(tag, type_name, member, multiple):
    return BlockDefinition(tag, type_name, member, multiple)


def createTypeDefinition(type_name):
    return TypeDefinition(type_name)

