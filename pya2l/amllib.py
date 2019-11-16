#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2019 by Christoph Schueler <cpu12.gems.googlemail.com>

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
__author__  = 'Christoph Schueler'
__version__ = '0.1.0'


from decimal import Decimal as D
import enum
import json
from pprint import pprint
import re

import antlr4


class AMLDict(dict):

    def __getattr__(self, attr):
        return self[attr]


def createDict(classname):
    return AMLDict(classname = classname)

def createEnumeration(name, enumerators):
    res = createDict('Enumeration')
    res['name'] = name
    res['enumerators'] = enumerators
    return res

def createEnumerator(tag, constant):
    res = createDict('Enumerator')
    res['tag'] = tag
    res['constant'] = constant
    return res

def createTaggedUnion(name, members):
    res = createDict('TaggedUnion')
    res['name'] = name
    res['members'] = members
    return res

def createTaggedUnionMember(tag, member, blockDefinition):
    res = createDict('TaggedUnionMember')
    res['tag'] = tag
    res['member'] = member
    res['blockDefinition'] = blockDefinition
    return res

def createMember(typename, arraySpecifier):
    res = createDict('Member')
    res['typename'] = typename
    res['arraySpecifier'] = arraySpecifier
    return res

def createTypeName(tag, name, _type):
    res = createDict('TypeName')
    res['tag'] = tag
    res['name'] = name
    res['type'] = _type
    return res

def createPredefinedType(name):
    res = createDict('PredefinedType')
    res['name'] = name
    return res

def createStructType(name, members):
    res = createDict('StructType')
    res['name'] = name
    res['members'] = members
    return res

def createTaggedStructType(name, members):
    res = createDict('TaggedStructType')
    res['name'] = name
    res['members'] = members
    return res

def createTaggedStructDefinition(tag, member, mult):
    res = createDict('TaggedStructDefinition')
    res['tag'] = tag
    res['member'] = member
    res['mult'] = mult
    return res

def createStructMember(value, mult):
    res = createDict('StructMember')
    res['value'] = value
    res['mult'] = mult
    return res

def createTaggedStructMember(taggedstructDefinition, blockDefinition, mult):
    res = createDict('TaggedStructMember')
    res['taggedstructDefinition'] = taggedstructDefinition
    res['blockDefinition'] = blockDefinition
    res['mult'] = mult
    return res

def createDeclaration(blockDefinition, typeDefinition):
    res = createDict('Declaration')
    res['blockDefinition'] = blockDefinition
    res['typeDefinition'] = typeDefinition
    return res

def createBlockDefinition(tag, typename, member):
    res = createDict('BlockDefinition')
    res['tag']  = tag
    res['typename'] = typename
    res['member'] = member
    return res

def createTypeDefinition(typename):
    res = createDict('TypeDefinition')
    res['typename'] = typename
    return res


class Listener(antlr4.ParseTreeListener):

    level = 0

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
            #print("TAG",tp.tag)
        else:
            #print()
            pass
        try:
            name = tp.name
        except:
            name = "???"
        tag = ctx.t.value if ctx.t else None
        ctx.value = createTypeName(tag, name, tp)

    def exitPredefined_type_name(self, ctx):
        ctx.value =  createPredefinedType(ctx.name.text)

    def exitStruct_type_name(self, ctx):
        if ctx.t0:
            name = ctx.t0.value
        elif ctx.t1:
            name = ctx.t1.value
        else:
            name = None
        members = [l.value for l in ctx.l]
        value = createStructType(name, members)
        ctx.value = value

    def exitStruct_member(self, ctx):
        if ctx.m:
            value = ctx.m.value
            multiple = False
        else:
            value = ctx.mstar.value
            multiple = True
        ctx.value = createStructMember(value, multiple)

    def exitTaggedstruct_type_name(self, ctx):
        if ctx.t0:
            name = ctx.t0.value
        elif ctx.t1:
            name = ctx.t1.value
        else:
            name = None
        members = [l.value for l in ctx.l]
        ctx.value = createTaggedStructType(name, members)

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
        ctx.value = createTaggedStructMember(taggedstructDefinition, blockDefinition, mult)

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

    def exitType_definition(self, ctx):
        ctx.value = createTypeDefinition(ctx.type_name().value)

    def exitMember(self, ctx):
        typename = ctx.t.value
        arraySpecifier = [a.value for a in ctx.a]
        ctx.value = createMember(typename, arraySpecifier)

    def exitTagged_union_member(self, ctx):
        tag = ctx.t.value if ctx.t else None
        member = ctx.m.value if ctx.m else None
        blockDefinition = ctx.b.value  if ctx.b else None
        ctx.value = createTaggedUnionMember(tag, member, blockDefinition)

    def exitTaggedunion_type_name(self, ctx):
        if ctx.t0:
            name = ctx.t0.value
        elif ctx.t1:
            name = ctx.t1.value
        else:
            name = None
        members = [l.value for l in ctx.l]
        ctx.value = createTaggedUnion(name, members)

    def enterBlock_definition(self, ctx):
        self.level += 1

    def exitBlock_definition(self, ctx):
        tag = ctx.tag.value
        self.level -= 1
        typename = ctx.tn.value if ctx.tn else None
        member = ctx.mem.value if ctx.mem else None
        ctx.value = createBlockDefinition(tag, typename, member)

    def exitDeclaration(self, ctx):
        blockDefinition = ctx.b.value if ctx.b else None
        typeDefinition = ctx.t.value if ctx.t else None
        ctx.value = createDeclaration(blockDefinition, typeDefinition)

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
        ctx.value = ctx.s.text.replace('"', '') if ctx.s else None

    def exitIdentifierValue(self, ctx):
        ctx.value = ctx.i.text if ctx.i else None

    def exitConstant(self, ctx):
        if ctx.i:
            value = int(ctx.i.text)
        elif ctx.h:
            value = int(ctx.h.text, 16)
        elif ctx.f:
            value = D(ctx.f.text)
        ctx.value = value

