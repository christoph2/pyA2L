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
import enum
import json
from pprint import pprint
import re

import antlr4

TYPE_NAME = re.compile(r"^<class\s'pya2l\.amllib\.(?P<klass>.*?)(?:Type)?'>$", re.DOTALL)


class ASTType(object):
    attrs = []
    children = []
    block = False


class Enumeration(ASTType):

    attrs = ('tag', )
    children = ('enumerators', )

    def __init__(self, tag, enumerators):
        self.tag = tag
        self.enumerators = enumerators


class Enumerator(ASTType):

    attrs = ('tag', 'constant')

    def __init__(self, tag, constant):
        self.tag = tag
        self.constant = constant


class TaggedUnion(ASTType):

    attrs = ('name', )
    children = ('members', )

    def __init__(self, name, members):
        self.name = name
        self.members = members


class TaggedUnionMember(ASTType):

     attrs = ('tag', )
     children = ('member', 'blockDefinition')

     def __init__(self, tag, member, blockDefinition):
         self.tag = tag
         self.member = member
         self.blockDefinition = blockDefinition


class Member(ASTType):

     attrs = ('arraySpecifier', )
     children = ('typeName', )

     def __init__(self, typeName, arraySpecifier):
         self.typeName = typeName
         self.arraySpecifier = arraySpecifier


class TypeName(ASTType):

    attrs = ('tag', )
    children = ('name', )

    def __init__(self, tag, name, type):
        if tag:
            print("TAG: ", tag)
        self.tag = tag
        self.name = name
        self.type = type


class PredefinedType(ASTType):

    attrs = ('name', )

    def __init__(self, name):
        self.name = name


class StructType(ASTType):

     attrs = ('name', )
     children = ('member', )

     def __init__(self, name, members):
         self.name = name
         self.members = members


class TaggedStructType(ASTType):

     attrs = ('name', )
     children = ('member', )

     def __init__(self, name, members):
         self.name = name
         self.members = members


class TaggedStructDefinition(ASTType):

     attrs = ('tag', 'mult')
     children = ('member',)

     def __init__(self, tag, member, mult):
        #print("TAG: {0}".format(tag))
        self.tag = tag
        self.member = member
        self.mult = mult


class TaggedStructMember(ASTType):

    atrs = ('mult', )
    children = ('taggedstructDefinition', 'blockDefinition')

    def __init__(self, taggedstructDefinition, blockDefinition, mult):
        self.taggedstructDefinition = taggedstructDefinition
        self.blockDefinition = blockDefinition
        self.mult = mult


class Declaration(ASTType):

     children = ('blockDefinition', 'typeDefinition')

     def __init__(self, blockDefinition, typeDefinition):
         self.blockDefinition = blockDefinition
         self.typeDefinition = typeDefinition

class BlockDefinition(ASTType):

    block = True
    attrs = ('tag', )
    children = ('typeName', )

    def __init__(self, tag, typeName):
        self.tag  = tag
        self.typeName = typeName

class TypeDefinition(ASTType):

    children = ('typename', )

    def __init__(self, typename):
        self.typename = typename


class DefinitionType(enum.IntEnum):
    BLOCK           = 0
    STRUCT          = 1
    TAGGEDSTRUCT    = 2
    TAGGEDUNION     = 3
    ENUM            = 4


class TypeDefinitions(object):

    def __init__(self):
        self.definitions = {}

    def append(self, name, type_, definition):
        print("APPENDING: {0} {1} {2}".format(name, type_, definition))
        print()


class Listener(antlr4.ParseTreeListener):

    typeDefinitions = TypeDefinitions()
    level = 0

    def getRule(self, attr):
        return attr().value if attr() else None

    def getList(self, attr):
        return [x for x in attr()] if attr() else []

    def getTerminal(self, attr):
        return attr().getText() if attr() else ''

    def exitType_name(self, ctx):
        name = ctx.name.value
        tag = self.getTerminal(ctx.TAG)
        match = TYPE_NAME.match("{0!r}".format(type(name)))
        if match:
            tn = match.group('klass')
        else:
            tn = None
        ctx.value = TypeName(tag, name, tn)

    def exitPredefined_type_name(self, ctx):
        ctx.value =  PredefinedType(ctx.name.text)

    def exitStruct_type_name(self, ctx):
        name = self.getTerminal(ctx.ID)
        members = self.getList(ctx.struct_member)
        value = StructType(name, members)
        ctx.value = value

    def exitStruct_member(self, ctx):
        member = ctx.member()
        ctx.value = member.value

    def exitTaggedstruct_type_name(self, ctx):
        name = self.getTerminal(ctx.ID)
        members = self.getList(ctx.taggedstruct_member)
        ctx.value = TaggedStructType(name, members)

    def exitTaggedstruct_member(self, ctx):
        mult = len(ctx.children) == 5 and ctx.children[3].getText() == '*'
        taggedstructDefinition = self.getRule(ctx.taggedstruct_definition)
        blockDefinition = self.getRule(ctx.block_definition)
        ctx.value = TaggedStructMember(taggedstructDefinition, blockDefinition, mult)

    def exitTaggedstruct_definition(self, ctx):
        mult = len(ctx.children) == 6 and ctx.children[4].getText() == '*'
        tag = ctx.TAG().getText()
        member = self.getRule(ctx.member)
        ctx.value = TaggedStructDefinition(tag, member, mult)

    def exitEnumerator(self, ctx):
        tag = self.getTerminal(ctx.TAG).replace('"', '')
        constant = ctx.constant().value
        ctx.value = Enumerator(tag, constant)

    def exitArray_specifier(self, ctx):
        size = ctx.constant().value
        ctx.value = size

    def exitEnumerator_list(self, ctx):
        ctx.value = self.getList(ctx.enumerator)

    def exitEnum_type_name(self, ctx):
        elements = self.getRule(ctx.enumerator_list)
        id_ = ctx.ID()
        ctx.value = Enumeration(id_, elements)

    def exitType_definition(self, ctx):
        ctx.value = TypeDefinition(ctx.type_name().value)

    def exitMember(self, ctx):
        typeName = ctx.type_name().value
        arraySpecifier = self.getList(ctx.array_specifier)
        ctx.value = Member(typeName, arraySpecifier)

    def exitTagged_union_member(self, ctx):
        tag = self.getTerminal(ctx.TAG)
        member = self.getRule(ctx.member)
        blockDefinition = self.getRule(ctx.block_definition)
        ctx.value = TaggedUnionMember(tag, member, blockDefinition)

    def exitTaggedunion_type_name(self, ctx):
        name = self.getTerminal(ctx.ID)   # TODO: FIXME!!!
        members = self.getList(ctx.tagged_union_member)
        ctx.value = TaggedUnion(name, members)

    def enterBlock_definition(self, ctx):
        print("{0}Enter block".format("  " * self.level))
        self.level += 1

    def exitBlock_definition(self, ctx):

        tag = ctx.TAG().getText()

        print("{0}Exit block: '{1}'".format("  " * self.level, tag))
        self.level -= 1

        typeName = ctx.type_name().value
        ctx.value = BlockDefinition(tag, typeName)

    def exitDeclaration(self, ctx):
        blockDefinition = self.getRule(ctx.block_definition)
        typeDefinition = ctx.type_definition()  # .value
        ctx.value = Declaration(blockDefinition, typeDefinition)

    def exitAmlFile(self, ctx):
        declarations = self.getList(ctx.declaration)
        ctx.value = declarations

