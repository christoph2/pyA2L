#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2020 by Christoph Schueler <cpu12.gems.googlemail.com>

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
from decimal import Decimal as D

import antlr4


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


def createEnumeration(name, enumerators):
    class Enumeration:
        def __init__(self, name, enumerators):
            self.name = name
            self.enumerators = enumerators
            self._renumber_constants()

        def __repr__(self):
            return "Enumeration(name = {}, enumerators = {})".format(
                self.name, self.enumerators
            )

        def _renumber_constants(self):
            """ISO C/C++ like enumerator numbering.

            Note
            ----
            Descending orderered ``enum``s are not supported yet.
            """
            last_idx = 0
            for enumerator in self.enumerators:
                if enumerator.constant is None:
                    enumerator.constant = last_idx
                    last_idx += 1
                else:
                    last_idx = enumerator.constant + 1

    res = Enumeration(name, enumerators)
    return res


def createEnumerator(tag, constant):
    class Enumerator:
        def __init__(self, tag, constant):
            self.tag = tag
            self.constant = constant

        def __repr__(self):
            return "Enumerator(tag = {}, constant = {})".format(self.tag, self.constant)

    return Enumerator(tag, constant)


def createTaggedUnion(name, members):
    class TaggedUnion:
        def __init__(self, name, members):
            self.name = name
            self.members = members

        def __repr__(self):
            return "TaggedUnion(name = {}, members = {})".format(
                self.name, self.members
            )

    res = TaggedUnion(name, members)
    return res


def createTaggedUnionMember(tag, member, block_definition):
    class TaggedUnionMember:
        def __init__(self, tag, member, block_definition):
            self.tag = tag
            self.member = member
            self.block_definition = block_definition

        def __repr__(self):
            return "TaggedUnionMember(tag = {}, member = {}, block_definition = {})".format(
                self.tag, self.member, self.block_definition
            )

    res = TaggedUnionMember(tag, member, block_definition)
    return res


def createMember(type_name, array_specifier):
    class Member:
        def __init__(self, type_name, array_specifier):
            self.type_name = type_name
            self.array_specifier = array_specifier

        def __repr__(self):
            return "Member(type_name = {}{})".format(
                self.type_name, self.array_specifier or ""
            )

    res = Member(type_name, array_specifier)
    return res


def createTypeName(tag, name, type_):
    class TypeName:
        def __init__(self, tag, name, type_):
            self.tag = tag
            self.name = name
            self.type_ = type_

        def __repr__(self):
            return "TypeName(tag = {}, name = {}, type = {})".format(
                self.tag, self.name, self.type_
            )

    res = TypeName(tag, name, type_)
    return res


def createPredefinedType(name):
    class PredefinedType:
        def __init__(self, type_):
            self.type_ = type_

        def __repr__(self):
            return "PredefinedType(type = {})".format(self.type_.name)

    res = PredefinedType(map_predefined_type(name))
    return res


def createStructType(name, members):
    class StructType:
        def __init__(self, name, members):
            self.name = name
            self.members = members

        def __repr__(self):
            return "StructType(name = {}, members = {})".format(self.name, self.members)

    res = StructType(name, members)
    return res


def createTaggedStructType(name, members):
    class TaggedStructType:
        def __init__(self, name, members):
            self.name = name
            self.members = members

        def __repr__(self):
            return "TaggedStructType(name = {}, members = {})".format(
                self.name, self.members
            )

    res = TaggedStructType(name, members)
    return res


def createTaggedStructDefinition(tag, member, multiple):
    class TaggedStructDefinition:
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

    res = TaggedStructDefinition(tag, member, multiple)
    return res


def createStructMember(value, multiple):
    class StructMember:
        def __init__(self, value, multiple):
            self.value = value
            self.multiple = multiple

        def __repr__(self):
            return "StructMember(value = {}, multiple = {})".format(
                self.value, self.multiple
            )

    res = StructMember(value, multiple)
    return res


def createTaggedStructMember(taggedstruct_definition, block_definition, multiple):
    class TaggedStructMember:
        def __init__(self, taggedstruct_definition, block_definition, multiple):
            self.taggedstruct_definition = taggedstruct_definition
            self.block_definition = block_definition
            self.multiple = multiple

        def __repr__(self):
            return "TaggedStructMember(taggedstruct_definition = {}, block_definition = {}, multiple = {})".format(
                self.taggedstruct_definition, block_definition, self.multiple
            )

    res = TaggedStructMember(taggedstruct_definition, block_definition, multiple)
    return res


def createDeclaration(block_definition, type_definition):
    class Declaration:
        def __init__(self, block_definition, type_definition):
            self.block_definition = block_definition
            self.type_definition = type_definition

        def __repr__(self):
            return "Declaration(block_definition = {}, type_definition = {})".format(
                self.block_definition, self.type_definition
            )

    res = Declaration(block_definition, type_definition)
    return res


def createBlockDefinition(tag, type_name, member):
    class BlockDefinition:
        def __init__(self, tag, type_name, member):
            self.tag = tag
            self.type_name = type_name
            self.member = member

        def __repr__(self):
            return "BlockDefinition(tag = {}, type_name = {}, member = {})".format(
                self.tag, self.type_name, self.member
            )

    res = BlockDefinition(tag, type_name, member)
    return res


def createTypeDefinition(type_name):
    class TypeDefinition:
        def __init__(self, type_name):
            self.type_name = type_name

        def __repr__(self):
            return "TypeDefinition(type_name = {})".format(self.type_name)

    res = TypeDefinition(type_name)
    return res


class AMLListener(antlr4.ParseTreeListener):

    level = 0

    def __init__(self):
        super().__init__()
        self.enum_types = []
        self.struct_types = []
        self.tagged_struct_types = []
        self.tagged_union_types = []
        self.block_definitions = []
        self.declarations = []
        self.type_definitions = []

    def exitType_name(self, ctx):
        if ctx.pr:
            tp = ctx.pr.value
        elif ctx.st:
            tp = ctx.st.value
        elif ctx.ts:
            tp = ctx.ts.value
        elif ctx.tu:
            tp = ctx.tu.value
        elif ctx.en:
            tp = ctx.en.value
        else:
            pass
        try:
            name = tp.name
        except:
            name = None
        tag = ctx.t.value if ctx.t else None
        ctx.value = createTypeName(tag, name, tp)

    def exitPredefined_type_name(self, ctx):
        ctx.value = createPredefinedType(ctx.name.text)

    def exitStruct_type_name(self, ctx):
        is_referrer = False
        if ctx.t0:
            name = ctx.t0.value
        elif ctx.t1:
            is_referrer = True
            name = ctx.t1.value
        else:
            name = None
        members = [l.value for l in ctx.l]
        value = createStructType(name, members)
        ctx.value = value
        if not is_referrer:
            self.struct_types.append(ctx.value)

    def exitStruct_member(self, ctx):
        if ctx.m:
            value = ctx.m.value
            multiple = False
        else:
            value = ctx.mstar.value
            multiple = True
        ctx.value = createStructMember(value, multiple)

    def exitTaggedstruct_type_name(self, ctx):
        is_referrer = False
        if ctx.t0:
            name = ctx.t0.value
        elif ctx.t1:
            is_referrer = True
            name = ctx.t1.value
        else:
            name = None
        members = [l.value for l in ctx.l]
        ctx.value = createTaggedStructType(name, members)
        if not is_referrer:
            self.tagged_struct_types.append(ctx.value)

    def exitTaggedstruct_member(self, ctx):
        if ctx.ts0:
            taggedstructDefinition = ctx.ts0.value
        elif ctx.ts1:
            taggedstructDefinition = ctx.ts1.value
        else:
            taggedstructDefinition = None
        if ctx.bl0:
            blockDefinition = ctx.bl0.value
        elif ctx.bl1:
            blockDefinition = ctx.bl1.value
        else:
            blockDefinition = None
        mult = True if ctx.m0 or ctx.m1 else False
        ctx.value = createTaggedStructMember(
            taggedstructDefinition, blockDefinition, mult
        )

    def exitTaggedstruct_definition(self, ctx):
        mult = True if ctx.mult else False
        tag = ctx.tag.value if ctx.tag else None
        member = ctx.mem.value if ctx.mem else None
        ctx.value = createTaggedStructDefinition(tag, member, mult)

    def exitEnumerator(self, ctx):
        tag = ctx.t.value
        constant = ctx.c.value if ctx.c else None
        ctx.value = createEnumerator(tag, constant)

    def exitArray_specifier(self, ctx):
        ctx.value = ctx.c.value

    def exitEnumerator_list(self, ctx):
        ctx.value = [x.value for x in ctx.ids]

    def exitEnum_type_name(self, ctx):
        elements = ctx.l.value if ctx.l else []
        if ctx.t0:
            name = ctx.t0.value
        elif ctx.t1:
            name = ctx.t1.value
        else:
            name = None
        ctx.value = createEnumeration(name, elements)
        self.enum_types.append(ctx.value)

    def exitType_definition(self, ctx):
        ctx.value = createTypeDefinition(ctx.type_name().value)
        self.type_definitions.append(ctx.value)

    def exitMember(self, ctx):
        typename = ctx.t.value
        arraySpecifier = [a.value for a in ctx.a]
        ctx.value = createMember(typename, arraySpecifier)

    def exitTagged_union_member(self, ctx):
        tag = ctx.t.value if ctx.t else None
        member = ctx.m.value if ctx.m else None
        blockDefinition = ctx.b.value if ctx.b else None
        ctx.value = createTaggedUnionMember(tag, member, blockDefinition)

    def exitTaggedunion_type_name(self, ctx):
        is_referrer = False
        if ctx.t0:
            name = ctx.t0.value
        elif ctx.t1:
            name = ctx.t1.value
            is_referrer = True
        else:
            name = None
        members = [l.value for l in ctx.l]
        ctx.value = createTaggedUnion(name, members)
        if not is_referrer:
            self.tagged_union_types.append(ctx.value)

    def enterBlock_definition(self, ctx):
        self.level += 1

    def exitBlock_definition(self, ctx):
        tag = ctx.tag.value
        self.level -= 1
        typename = ctx.tn.value if ctx.tn else None
        member = ctx.mem.value if ctx.mem else None
        ctx.value = createBlockDefinition(tag, typename, member)
        self.block_definitions.append(ctx.value)

    def exitDeclaration(self, ctx):
        blockDefinition = ctx.b.value if ctx.b else None
        typeDefinition = ctx.t.value if ctx.t else None
        ctx.value = createDeclaration(blockDefinition, typeDefinition)
        self.declarations.append(ctx.value)

    def exitAmlFile(self, ctx):
        declarations = [d.value for d in ctx.d]
        ctx.value = declarations
        self.value = declarations

    def exitIntValue(self, ctx):
        ctx.value = int(ctx.i.text) if ctx.i else None

    def exitFloatValue(self, ctx):
        ctx.value = float(ctx.f.text) if ctx.f else None

    def exitNumber(self, ctx):
        ctx.value = ctx.i.value if ctx.i else ctx.f.value

    def exitStringValue(self, ctx):
        ctx.value = ctx.s.text.strip('"') if ctx.s else None

    def exitTagValue(self, ctx):
        ctx.value = ctx.s.text.replace('"', "") if ctx.s else None

    def exitIdentifierValue(self, ctx):
        ctx.value = ctx.i.text if ctx.i else None

    def exitNumericValue(self, ctx):
        if ctx.i:
            value = int(ctx.i.text)
        elif ctx.h:
            value = int(ctx.h.text, 16)
        elif ctx.f:
            value = D(ctx.f.text)
        ctx.value = value
