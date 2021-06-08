#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2021 by Christoph Schueler <cpu12.gems.googlemail.com>

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


from decimal import Decimal as D

import antlr4

from pya2l.aml import classes

##
## Listener.
##
class AMLListener(antlr4.ParseTreeListener):

    def __init__(self):
        super().__init__()
        self.root_element = None
        self._types = dict(StructType = {}, TaggedUnion = {}, TaggedStructType = {}, Enumeration = {})

    def get_type(self, tp, name):
        tp_ = self._types.get(tp)
        if tp_:
            return tp_.get(name).type_
        else:
            return None

    def exitType_name(self, ctx):
        if ctx.pr:
            tp = ctx.pr.value   # Predefined type.
        elif ctx.st:
            tp = ctx.st.value   # Struct.
        elif ctx.ts:
            tp = ctx.ts.value   # TaggedStruct.
        elif ctx.tu:
            tp = ctx.tu.value   # TaggedUnion.
        elif ctx.en:
            tp = ctx.en.value   # Enum.
        else:
            pass
        try:
            name = tp.name
        except:
            name = None
        tag = ctx.t.value if ctx.t else None
        ctx.value = classes.createTypeName(tag, name, tp)

    def exitPredefined_type_name(self, ctx):
        ctx.value = classes.createPredefinedType(ctx.name.text)

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
        value = classes.createStructType(name, members, is_referrer)
        ctx.value = value

    def exitStruct_member(self, ctx):
        if ctx.m:
            value = ctx.m.value
            multiple = False
        else:
            value = ctx.mstar.value
            multiple = True
        ctx.value = classes.createStructMember(value, multiple)

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
        ctx.value = classes.createTaggedStructType(name, members, is_referrer)

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
        ctx.value = classes.createTaggedStructMember(
            taggedstructDefinition, blockDefinition, mult
        )

    def exitTaggedstruct_definition(self, ctx):
        mult = True if ctx.mult else False
        tag = ctx.tag.value if ctx.tag else None
        member = ctx.mem.value if ctx.mem else None
        ctx.value = classes.createTaggedStructDefinition(tag, member, mult)

    def exitEnumerator(self, ctx):
        tag = ctx.t.value
        constant = ctx.c.value if ctx.c else None
        ctx.value = classes.createEnumerator(tag, constant)

    def exitArray_specifier(self, ctx):
        ctx.value = ctx.c.value

    def exitEnumerator_list(self, ctx):
        ctx.value = [x.value for x in ctx.ids]

    def exitEnum_type_name(self, ctx):
        is_referrer = False
        elements = ctx.l.value if ctx.l else []
        if ctx.t0:
            name = ctx.t0.value
        elif ctx.t1:
            name = ctx.t1.value
            is_referrer = True
        else:
            name = None
        ctx.value = classes.createEnumeration(name, elements, is_referrer)

    def exitType_definition(self, ctx):
        ctx.value = classes.createTypeDefinition(ctx.type_name().value)
        tn = ctx.value.type_name
        self._types[tn.type_.__class__.__name__][tn.name] = tn

    def exitMember(self, ctx):
        typename = ctx.t.value
        arraySpecifier = [a.value for a in ctx.a]
        ctx.value = classes.createMember(typename, arraySpecifier)

    def exitTagged_union_member(self, ctx):
        tag = ctx.t.value if ctx.t else None
        member = ctx.m.value if ctx.m else None
        blockDefinition = ctx.b.value if ctx.b else None
        ctx.value = classes.createTaggedUnionMember(tag, member, blockDefinition)

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
        ctx.value = classes.createTaggedUnion(name, members, is_referrer)

    def exitBlock_definition(self, ctx):
        tag = ctx.tag.value
        typename = ctx.tn.value if ctx.tn else None
        member = ctx.mem.value if ctx.mem else None
        mult = True if ctx.mult else False
        ctx.value = classes.createBlockDefinition(tag, typename, member, mult)
        if tag == "IF_DATA":
            self.root_element = ctx.value

    def exitDeclaration(self, ctx):
        blockDefinition = ctx.b.value if ctx.b else None
        typeDefinition = ctx.t.value if ctx.t else None
        ctx.value = classes.createDeclaration(blockDefinition, typeDefinition)

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
