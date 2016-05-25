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


class BaseType(object):

    def __repr__(self):
        keys = [k for k in self.__dict__ if not (k.startswith('__') and k.endswith('__'))]
        result = []
        result.append("%s {" % self.__class__.__name__)
        for key in keys:
            value = getattr(self, key)
            line = "    {0} = {1!r}".format(key, value)
            result.append(line)
        result.append("}")
        return '\n'.join(result)

    __str__ = __repr__


class Block(BaseType):

    def __init__(self, tag, typeName, mult = None):
        self.tag = tag
        self.typeName = typeName
        self.mult = mult


class Enumeration(BaseType):

    def __init__(self, tag, enumerators):
        self.tag = tag
        self.enumerators = enumerators


class Enumerator(BaseType):

    def __init__(self, tag, constant):
        self.tag = tag
        self.constant = constant


class Predefined(BaseType):

    def __init__(self, name):
        self.name = name


class Struct(BaseType):

    def __init__(self, name, members):
        self.name = name
        self.members = members


class TaggedStruct(BaseType):

    def __init__(self, name, members, blocks, mult):
        self.name = name
        self.members = members
        self.blocks = blocks
        self.mult = mult


class TaggedUnion(BaseType):

    def __init__(self, name, members, blocks):
        self.name = name
        self.members = members
        self.blocks = blocks

class Member(BaseType):

    def __init__(self, typeName, arraySpecifier, mult):
        self.typeName = typeName
        self.arraySpecifier = arraySpecifier
        self.mult = mult


class Parser(object):

    def __init__(self, tree):
        self.tree = tree

    def doMember(self, tree, mult = None):
        return Member(self.doTypeName(tree.typeName), tree.arraySpecifier, mult)

    def doTaggedUnion(self, tree):
        members = []
        blocks = []
        for member in tree.members:
            member = member.value
            if member.blockDefinition:
                blocks.append(self.doBlockDefinition(member.blockDefinition))
            else:
                if member.member:
                    members.append(self.doMember(member.member))
        return TaggedUnion(tree.name, members, blocks)

    def doTaggedStruct(self, tree):
        members = []
        blocks = []
        for member in tree.members:
            member = member.value
            mult = member.mult
            if member.blockDefinition:
                blocks.append(self.doBlockDefinition(member.blockDefinition, mult))
            if member.taggedstructDefinition:
                if member.taggedstructDefinition.member:
                    members.append(self.doMember(member.taggedstructDefinition.member, mult))
        return TaggedStruct(tree.name, members, blocks, member.mult)

    def doStruct(self, tree):
        members = []
        for member in tree.members:
            member = member.value
            if member:
                members.append(self.doMember(member))
        return Struct(tree.name, members)

    def doPredefined(self, tree):
        return Predefined(tree.name)

    def doEnumeration(self, tree):
        enumerators = []
        for enumerator in tree.enumerators:
            enumerators.append(Enumerator(enumerator.value.tag, enumerator.value.constant))
        return Enumeration(tree.tag, enumerators)

    def doTypeName(self, tree):
        TYPES = {
            "Enumeration": "doEnumeration",
            "Predefined": "doPredefined",
            "Struct": "doStruct",
            "TaggedStruct": "doTaggedStruct",
            "TaggedUnion": "doTaggedUnion",
        }
        method = TYPES.get(tree.type)
        return getattr(self, method)(tree.name)

    def doBlockDefinition(self, tree, mult = None):
        return Block(tree.tag, self.doTypeName(tree.typeName), mult)

    def build(self):
        declarations = []
        for declaration in self.tree.value:
            declaration = declaration.value
            if declaration.blockDefinition:
                decl = declaration.blockDefinition.typeName
                block = self.doBlockDefinition(declaration.blockDefinition)
                declarations.append(block)
            if declaration.typeDefinition:
                td = declaration.typeDefinition
                print(td)
        return declarations

