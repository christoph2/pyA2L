#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2018 by Christoph Schueler <cpu12.gems.googlemail.com>

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


from collections import namedtuple, OrderedDict
import enum
import json
from pprint import pprint
import re

import antlr4


class AMLDict(OrderedDict):

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

    def getRule(self, attr):
        return attr().value if attr() else None

    def getList(self, attr):
        return [x for x in attr()] if attr() else []

    def getTerminal(self, attr):
        return attr().getText() if attr() else ''

    def exitType_name(self, ctx):
        if ctx.predefined_type_name():
            tp = ctx.predefined_type_name().value
        elif ctx.struct_type_name():
            tp = ctx.struct_type_name().value
        elif ctx.taggedstruct_type_name():
            tp = ctx.taggedstruct_type_name().value
        elif ctx.taggedunion_type_name():
            tp = ctx.taggedunion_type_name().value
        elif ctx.enum_type_name():
            tp = ctx.enum_type_name().value
            #print("TAG",tp.tag)
        else:
            #print()
            pass
        try:
            name = tp.name
        except:
            name = "???"

        tag = self.getTerminal(ctx.TAG).replace('"', '')
        #print("tag: {:10s} name: {:20s} class: {}".format(tag, name, str(tp)))
        ctx.value = createTypeName(tag, name, tp)

    def exitPredefined_type_name(self, ctx):
        ctx.value =  createPredefinedType(ctx.name.text)

    def exitStruct_type_name(self, ctx):
        name = self.getTerminal(ctx.ID)
        members = [m.value for m in self.getList(ctx.struct_member)]
        value = createStructType(name, members)
        ctx.value = value

    def exitStruct_member(self, ctx):
        member = ctx.member()
        ctx.value = member.value

    def exitTaggedstruct_type_name(self, ctx):
        name = self.getTerminal(ctx.ID)
        members = [m.value for m in self.getList(ctx.taggedstruct_member)]
        ctx.value = createTaggedStructType(name, members)

    def exitTaggedstruct_member(self, ctx):
        mult = len(ctx.children) == 5 and ctx.children[3].getText() == '*'
        taggedstructDefinition = self.getRule(ctx.taggedstruct_definition)
        blockDefinition = self.getRule(ctx.block_definition)
        ctx.value = createTaggedStructMember(taggedstructDefinition, blockDefinition, mult)

    def exitTaggedstruct_definition(self, ctx):
        mult = len(ctx.children) == 5 and ctx.children[4].getText() == '*'
        tag = ctx.TAG().getText().replace('"', '') if ctx.TAG() else None
        #print("TAG: {} MULT: {}".format(tag, mult))
        member = self.getRule(ctx.member)
        ctx.value = createTaggedStructDefinition(tag, member, mult)

    def exitEnumerator(self, ctx):
        tag = self.getTerminal(ctx.TAG).replace('"', '')
        constant = ctx.constant().value if ctx.constant() else None
        ctx.value = createEnumerator(tag, constant)

    def exitArray_specifier(self, ctx):
        size = ctx.constant().value
        ctx.value = size

    def exitEnumerator_list(self, ctx):
        ctx.value = [e.value for e in self.getList(ctx.enumerator)]

    def exitEnum_type_name(self, ctx):
        elements = self.getRule(ctx.enumerator_list)
        name = self.getTerminal(ctx.ID)
        ctx.value = createEnumeration(name, elements)

    def exitType_definition(self, ctx):
        ctx.value = createTypeDefinition(ctx.type_name().value)

    def exitMember(self, ctx):
        typename = ctx.type_name().value
        arraySpecifier = [a.value for a in self.getList(ctx.array_specifier)]
        ctx.value = createMember(typename, arraySpecifier)

    def exitTagged_union_member(self, ctx):
        tag = self.getTerminal(ctx.TAG).replace('"', '')
        member = self.getRule(ctx.member)
        blockDefinition = self.getRule(ctx.block_definition)
        ctx.value = createTaggedUnionMember(tag, member, blockDefinition)

    def exitTaggedunion_type_name(self, ctx):
        name = self.getTerminal(ctx.ID)
        members = [m.value for m in self.getList(ctx.tagged_union_member)]
        ctx.value = createTaggedUnion(name, members)

    def enterBlock_definition(self, ctx):
        self.level += 1

    def exitBlock_definition(self, ctx):
        tag = ctx.TAG().getText().replace('"', '')
        self.level -= 1
        typename = self.getRule(ctx.type_name)
        member = self.getRule(ctx.member)
        ctx.value = createBlockDefinition(tag, typename, member)

    def exitDeclaration(self, ctx):
        blockDefinition = self.getRule(ctx.block_definition)
        typeDefinition = self.getRule(ctx.type_definition)
        ctx.value = createDeclaration(blockDefinition, typeDefinition)

    def exitAmlFile(self, ctx):
        declarations = [d.value for d in self.getList(ctx.declaration)]
        ctx.value = declarations

