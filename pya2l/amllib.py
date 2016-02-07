#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2016 by Christoph Schueler <cpu12.gems.googlemail.com>

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


from collections import namedtuple
import json
from pprint import pprint

import antlr4

Enumerator = namedtuple('Enumerator', 'tag constant')
Enumeration = namedtuple('Enumeration', 'tag enumerators')
TaggedUnion = namedtuple('TaggedUnion', 'name members')
TaggedUnionMember = namedtuple('TaggedUnionMember', 'tag member blockDefinition')
Member = namedtuple('Member', 'typeName arraySpecifier')
TypeName = namedtuple('TypeName', 'tag name')
PredefinedType = namedtuple('PredefinedType', 'name')
StructType = namedtuple('StructType', 'name member')
TaggedStructType = namedtuple('TaggedStructType', 'name member')
TaggedStructDefinition = namedtuple('TaggedStructDefinition', 'tag member')
TaggedStructMember = namedtuple('TaggedStructMember', 'taggedstructDefinition blockDefinition')
Declaration = namedtuple('Declaration', 'blockDefinition typeDefinition')
BlockDefinition = namedtuple('BlockDefinition', 'tag typeName')
TypeDefinition = namedtuple('TypeDefinition', 'typename')

class Listener(antlr4.ParseTreeListener):

    def exitType_name(self, ctx):
        name = ctx.name.value
        tag = ctx.TAG()
        #pprint("NAME: {0}".format(name), indent = 3)
        ctx.value = TypeName(tag, name)

    def exitPredefined_type_name(self, ctx):
        ctx.value =  PredefinedType(ctx.name.text)

    def exitStruct_type_name(self, ctx):
        name = ctx.ID().text if ctx.ID() else None
        member = [m.value for m in ctx.struct_member()]
        ctx.value = StructType(name, member)

    def exitStruct_member(self, ctx):
        member = ctx.member()
        ctx.value = member.value

    def exitTaggedstruct_type_name(self, ctx):
        name = ctx.ID().text if ctx.ID() else None
        member = [m.value for m in ctx.taggedstruct_member()]
        ctx.value = TaggedStructType(name, member)

    def exitTaggedstruct_member(self, ctx):
        # TODO: '*'!!!
        # TODO: Check variants!!!
        taggedstructDefinition = ctx.taggedstruct_definition().value if ctx.taggedstruct_definition() else None
        blockDefinition = ctx.block_definition().value if ctx.block_definition() else None
        #print("TSD: {0} BD: {1}\n".format(taggedstructDefinition, blockDefinition))
        ctx.value = TaggedStructMember(taggedstructDefinition, blockDefinition)

    def exitTaggedstruct_definition(self, ctx):
        # TODO: '*'!!!
        # TODO: Check variants!!!
        tag = ctx.TAG().getText()
        member = ctx.member().value if ctx.member() else None
        #print("TAG: {0} MEMBER: {1}\n".format(tag, member))
        ctx.value = TaggedStructDefinition(tag, member)

    def exitEnumerator(self, ctx):
        tag = ctx.TAG().getText().replace('"', '')
        constant = ctx.constant().value
        ctx.value = Enumerator(tag, constant)

    def exitArray_specifier(self, ctx):
        size = ctx.constant().value
        ctx.value = size

    def exitEnumerator_list(self, ctx):
        ctx.value =[e.value for e in ctx.enumerator()]

    def exitEnum_type_name(self, ctx):
        elements = ctx.enumerator_list().value
        id_ = ctx.ID()
        ctx.value = Enumeration(id_, elements)

    def exitType_definition(self, ctx):
        ctx.value = TypeDefinition(ctx.type_name().value)

    def exitMember(self, ctx):
        typeName = ctx.type_name().value
        arraySpecifier = [a.value for a in ctx.array_specifier()]
        ctx.value = Member(typeName, arraySpecifier)

    def exitTagged_union_member(self, ctx):
        # TODO: '*'!!!
        # TODO: Check variants!!!
        tag = ctx.TAG().getText() if ctx.TAG() else None
        member = ctx.member().value if ctx.member() else None
        blockDefinition = ctx.block_definition().value if ctx.block_definition() else None
        ctx.value = TaggedUnionMember(tag, member, blockDefinition)

    def exitTaggedunion_type_name(self, ctx):
        name = ctx.ID().getText() if ctx.ID() else None   # TODO: FIXME!!!
        members = [m.value for m in ctx.tagged_union_member()]
        #print("NAME: {0} MEMBERS: {1}\n".format(name, members))
        ctx.value = TaggedUnion(name, members)

    def exitBlock_definition(self, ctx):
        tag = ctx.TAG().getText()
        typeName = ctx.type_name().value
        ctx.value = BlockDefinition(tag, typeName)

    def exitDeclaration(self, ctx):
        blockDefinition = ctx.block_definition().value
        typeDefinition = ctx.type_definition()  # .value
        ctx.value = Declaration(blockDefinition, typeDefinition)

    def exitAmlFile(self, ctx):
        declaration = [d.value for d in ctx.declaration()]
        ctx.value = declaration

