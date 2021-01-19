#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""Load/store AML abstract syntax trees from/to A2LDBs."""

__copyright__="""
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2021 by Christoph Schueler <cpu12.gems@googlemail.com>

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


from collections import defaultdict
from logging import getLogger

from pya2l import a2llg
from pya2l.aml import classes
from pya2l import model


class Importer:

    def __init__(self, session, ast):
        self.session = session
        self._ast = ast.value
        self.declarations(self.ast)
        self.session.commit()

    def declarations(self, top_level):
        decls = []
        for elem in top_level:
            decl = model.AMLDeclaration(
                block_definition = self.block_definition(elem.block_definition),
                type_definition = self.type_definition(elem.type_definition)
            )
            decls.append(decl)
        self.session.add_all(decls)
        self.session.flush()
        res = self.session.query(model.AMLDeclaration).all()

    def type_definition(self, tree):
        if tree:
            return model.AMLTypeDefinition(type_name = self.type_name(tree.type_name))

    def block_definition(self, tree):
        if tree:
            return model.AMLBlockDefinition(
                tag = tree.tag,
                member = self.member(tree.member),
                type_name = self.type_name(tree.type_name)
            )

    def type_name(self, tree):
        if tree:
            tp = None
            if isinstance(tree.type_, classes.PredefinedType):
                tp = self.predefined_type(tree.type_)
            elif isinstance(tree.type_, classes.StructType):
                tp = self.struct_type(tree.type_)
            elif isinstance(tree.type_, classes.TaggedStructType):
                tp = self.tagged_struct_type(tree.type_)
            elif isinstance(tree.type_, classes.TaggedUnion):
                tp = self.tagged_union(tree.type_)
            elif isinstance(tree.type_, classes.Enumeration):
                tp = self.enumeration(tree.type_)
            elif isinstance(tree.type_, classes.Referrer):
                tp = self.referrer(tree.type_)
            return model.AMLTypeName(tag = tree.tag, name = tree.name, type = tp)

    def member(self, tree):
        if tree:
            return model.AMLMember(
                type_name = self.type_name(tree.type_name),
                array_specifier = str(tree.array_specifier)
            )

    def referrer(self, tree):
        if tree:
            return model.AMLReferrer(category = tree.category, identifier = tree.identifier)

    def enumeration(self, tree):
        if tree:
            enumeration = model.AMLEnumeration(name = tree.name)
            self.session.add(enumeration)
            self.session.flush()
            for idx, (k, v) in enumerate(tree.enumerators.items(), 1):
                enu = model.AMLEnumerator(
                    tag = k,
                    constant = v,
                    enumeration_id = enumeration.base_type_id,
                    rid = idx
                )
                self.session.add(enu)
                enumeration.enumerators.append(enu)
            self.session.flush()
            return enumeration

    def predefined_type(self, tree):
        if tree:
            return model.AMLPredefinedType(typeid = tree.type_)

    def struct_type(self, tree):
        if tree:
            struct = model.AMLStructType(name = tree.name)
            self.session.add(struct)
            self.session.flush()
            for idx, mem in enumerate(tree.members, 1):
                sm = model.AMLStructMember(
                    member = self.member(mem.value),
                    multiple = mem.multiple,
                    struct_type_id = struct.base_type_id,
                    rid = idx
                )
                self.session.add(sm)
                struct.members.append(sm)
            self.session.flush()
            return struct

    def tagged_struct_type(self, tree):
        if tree:
            tstruct = model.AMLTaggedStructType(name = tree.name)
            self.session.add(tstruct)
            self.session.flush()
            for idx, tmem in enumerate(tree.members, 1):
                sm = model.AMLTaggedStructMember(
                    block_definition = self.block_definition(tmem.block_definition),
                    taggedstruct_definition = self.taggedstruct_definition(tmem.taggedstruct_definition),
                    multiple = tmem.multiple,
                    tagged_struct_type_id = tstruct.base_type_id,
                    rid = idx
                )
                self.session.add(sm)
                tstruct.members.append(sm)
            self.session.flush()
            return tstruct

    def taggedstruct_definition(self, tree):
        if tree:
            return model.AMLTaggedStructDefinition(
                tag = tree.tag,
                multiple = tree.multiple,
                member = self.member(tree.member)
            )

    def tagged_union(self, tree):
        if tree:
            tunion = model.AMLTaggedUnion(name = tree.name)
            for idx, mem in enumerate(tree.members, 1):
                tum = model.AMLTaggedUnionMember(
                    member = self.member(mem.member),
                    block_definition = self.block_definition(mem.block_definition),
                    tag = mem.tag,
                    tagged_union_id = tunion.base_type_id,
                    rid = idx
                )
                self.session.add(tum)
                tunion.members.append(tum)
            self.session.flush()
            return tunion

    @property
    def ast(self):
        return self._ast
