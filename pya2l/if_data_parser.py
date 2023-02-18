#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2022 by Christoph Schueler <cpu12.gems@googlemail.com>

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

"""Parse IF_DATA sections with dynamically created AML grammar.

Note
----
Currently there is no resonable error-handling / -recovery.
"""

from collections import defaultdict
from logging import getLogger

import antlr4
from antlr4.BufferedTokenStream import BufferedTokenStream
from antlr4.error.ErrorListener import ErrorListener

# import importlib as imp
# import pya2l
# imp.reload(pya2l)
# import pya2l.a2llg
# imp.reload(pya2l.a2llg)
# import pya2l.aml
# imp.reload(pya2l.aml)
# import pya2l.aml.classes
# imp.reload(pya2l.aml.classes)

from pya2l import a2llg
from pya2l.aml.classes import AMLPredefinedTypes, Referrer


EOF = -1


class EOFReached(Exception):
    """Signals end of token stream."""


IF_DATA_ELEMENTS = (
    "AXIS_PTS",
    "CHARACTERISTIC",
    "FRAME",
    "FUNCTION",
    "GROUP",
    "MEASUREMENT",
    "MEMORY_LAYOUT",
    "MEMORY_SEGMENT",
    "MODULE",
)


def token_to_int(token):
    """ """
    text = token.text
    if text.startswith(("0x", "0X")):
        return int(text, 16)
    else:
        return int(text, 10)


def token_to_float(token):
    """ """
    return float(token.text)


class IfDataParser:
    """ """

    def __init__(self, syntax):
        self.logger = getLogger("pya2l.if_data_parser")
        self.syntax = syntax

    @property
    def current_element(self):
        return self.elements[-1]

    def push_element(self, element):
        self.elements.append(element)

    def pop_element(self):
        return self.elements.pop(-1)

    def empty_stack(self):
        self.elements = []

    def parse(self, buffer):
        """ """
        self.empty_stack()
        self.push_element(self.syntax.root_element)
        input_stream = antlr4.InputStream(buffer)
        self.lexer = a2llg.a2llg(input_stream)
        self.tokens = [t for t in self.lexer.getAllTokens() if t.channel != t.HIDDEN_CHANNEL]
        self.num_tokens = len(self.tokens)
        self.token_idx = 0
        self.level = 0
        if self.current_element.is_block:
            result = self.block()
        else:
            raise ValueError("Expected block statement.")
        return result

    def enter(self, name):
        self.level += 1

    def leave(self, name):
        self.level -= 1

    @property
    def current_token(self):
        """Get the token at the current stream position."""
        return self.lookahead(0)

    def lookahead(self, n=1):
        """Get the token `n` elements ahead of current stream position."""
        index = self.token_idx + n
        if index < self.num_tokens:
            return self.tokens[index]
        else:
            raise EOFReached()

    def value(self, token):
        """Convert token text to Python type."""
        value = None
        if token.type == self.lexer.INT:
            value = token_to_int(token)
        elif token.type == self.lexer.IDENT:
            value = token.text
        elif token.type == self.lexer.FLOAT:
            value = token_to_float(token)
        elif token.type == self.lexer.STRING:
            value = token.text[1:-1]
        return value

    def consume(self):
        """Increment token stream position by one."""
        self.token_idx += 1

    def match(self, token_type, value=None):
        ok = self.current_token.type == token_type
        token_value = self.value(self.current_token)
        self.consume()
        if value is None:
            return ok
        else:
            if not ok:
                return False
            return token_value == value

    def block(self):
        result = None
        self.enter("block")
        elem = self.current_element
        tag = elem.tag
        self.match(self.lexer.BEGIN)
        self.match(self.lexer.IDENT, elem.tag)
        tp = elem.type_name.type_
        if isinstance(tp, Referrer):
            entry = self.syntax.get_type(tp.category, tp.identifier)
        else:
            entry = elem.definition
        self.push_element(entry)
        class_name = entry.__class__.__name__
        if class_name == "TaggedUnion":
            result = {"tag": tag, "value": self.tagged_union()}
        elif class_name == "StructType":
            result = {"tag": tag, "value": self.struct()}
        elif class_name == "TaggedStructType":
            result = {"tag": tag, "value": self.tagged_struct()}
        elif class_name == "PredefinedType":
            result = {"tag": tag, "value": self.predefined_type()}
        elif class_name == "Enumeration":
            result = {"tag": tag, "value": self.enum()}
        else:
            raise NotImplementedError(entry.__class__.__name__)
        self.pop_element()
        self.match(self.lexer.END)
        self.match(self.lexer.IDENT, elem.tag)
        self.leave("block")
        return result

    def tagged_union(self):
        result = []
        self.enter("tagged_union")
        tag = self.current_token.text
        # name = self.current_element.name
        definition = self.current_element.tags.get(tag)
        if definition:
            tp = definition.type_name
            tn = tp.type_.__class__.__name__
            self.consume()
            self.push_element(tp.type_)
            if tn == "StructType":
                result = self.struct()
            elif tn == "TaggedStructType":
                result = self.tagged_struct()
            elif tn == "TaggedUnion":
                result = self.tagged_union()
            elif tn == "PredefinedType":
                result = self.predefined_type()
            elif tn == "Enumeration":
                result = self.enum()
            else:
                raise NotImplementedError(tn)
            self.pop_element()
        self.leave("tagged_union")
        return result

    def predefined_type(self):
        self.enter("predefined_type")
        arr = self.current_element.array_specifier
        tp = self.current_element.type_
        if arr:
            if tp in (AMLPredefinedTypes.PDT_CHAR, AMLPredefinedTypes.PDT_UCHAR):
                result = self.value(self.current_token)
                self.consume()
            else:
                result = []
                for _ in range(arr[0]):
                    result.append(self.value(self.current_token))
                    self.consume()
        else:
            result = self.value(self.current_token)
            self.consume()
        self.leave("predefined_type")
        return result

    def enum(self):
        self.enter("enum")
        enumerator = self.current_token.text
        self.match(self.lexer.IDENT)
        # ok = enumerator in self.current_element.enumerators
        self.leave("enum")
        return enumerator

    def struct(self):
        self.enter("struct")
        members = self.current_element.members
        # name = self.current_element.name
        # print("struct: ", name)
        result = []
        for mem in members:
            value = mem.value
            # multiple = mem.multiple
            entry = value.type_name.type_
            # idi = entry.identifier if hasattr(entry, "identifier") else "n/a"
            if isinstance(entry, Referrer):
                entry = self.syntax.get_type(entry.category, entry.identifier)
            self.push_element(entry)
            tn = entry.__class__.__name__
            if tn == "TaggedStructType":
                result.append(self.tagged_struct())
            elif tn == "StructType":
                result.append(self.struct())
            elif tn == "TaggedUnion":
                result.append(self.tagged_union())
            elif tn == "PredefinedType":
                result.append(self.predefined_type())
            elif tn == "Enumeration":
                result.append(self.enum())
            else:
                raise NotImplementedError(tn)
            self.pop_element()
        self.leave("struct")
        return result

    def block_or_tag(self):
        if self.current_token.type == self.lexer.BEGIN:
            return self.lookahead(1).text
        else:
            return self.current_token.text

    def tagged_struct(self):
        self.enter("tagged_struct")
        tag = self.block_or_tag()
        tags = self.current_element.tags.keys()
        counter = {k: False for k in tags}
        tag_dict = defaultdict(list)
        while True:
            definition = self.current_element.tags.get(tag)
            if definition:
                counter[tag] = True
                if definition.block_definition:
                    self.push_element(definition.block_definition)
                    block = self.block()
                    tag = block.pop("tag")
                    value = block.get("value")
                    if definition.multiple:
                        tag_dict[tag].append(value)
                    else:
                        tag_dict[tag] = value
                    self.pop_element()
                    if ((self.current_token.type != self.lexer.IDENT) or (self.current_token.text not in tags)) and (
                        self.current_token.type != self.lexer.BEGIN
                    ):
                        break
                elif definition.taggedstruct_definition.member:
                    self.consume()
                    if definition.taggedstruct_definition.__class__.__name__ == "TaggedStructDefinition":
                        self.push_element(definition.taggedstruct_definition)
                        tsm = self.tagged_struct_member()
                        tag = tsm.pop("tag")
                        value = tsm.get("value")
                        if definition.multiple:
                            tag_dict[tag].append(value)
                        else:
                            tag_dict[tag] = value
                        self.pop_element()
                        if ((self.current_token.type != self.lexer.IDENT) or (self.current_token.text not in tags)) and (
                            self.current_token.type != self.lexer.BEGIN
                        ):
                            break
                    else:
                        raise NotImplementedError(definition.taggedstruct_definition.__class__.__name__)
                else:
                    tag_dict[tag] = None  # just a tag.
                    self.consume()
                tag = self.block_or_tag()
            else:
                break
        self.leave("tagged_struct")
        return dict(tag_dict)

    def tagged_struct_member(self):
        tp = self.current_element.member.type_name.type_
        tag = self.current_element.tag
        self.push_element(tp)
        class_name = tp.__class__.__name__
        if class_name == "PredefinedType":
            result = {"value": self.predefined_type()}
        elif class_name == "StructType":
            result = {"type": "struct", "value": self.struct()}
        elif class_name == "Enumeration":
            result = {"value": self.enum()}
        elif class_name == "TaggedUnion":
            result = {"type": "tagged_union", "value": self.tagged_union()}
        elif class_name == "TaggedStructType":
            ts = self.tagged_struct()
            if ts:
                result = {"type": "tagged_struct", "value": ts}
        else:
            raise NotImplementedError(tp.__class__.__name__)
        self.pop_element()
        return_value = {"tag": tag}
        return_value.update(result)
        return return_value

    def type_as_str(self, type_):
        TYPE_MAP = {
            self.lexer.IDENT: "IDENT",
            self.lexer.FLOAT: "FLOAT",
            self.lexer.INT: "INT",
            self.lexer.COMMENT: "COMMENT",
            self.lexer.WS: "WS",
            self.lexer.STRING: "STRING",
            self.lexer.BEGIN: "BEGIN",
            self.lexer.END: "END",
        }
        return TYPE_MAP.get(type_)
