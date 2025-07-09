from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Optional

import pya2l.a2lparser_ext as ext
import pya2l.model as model


NodeType = ext.NodeType
AmlType = ext.AmlType


class AMLPredefinedTypeEnum(IntEnum):
    CHAR = 0
    INT = 1
    LONG = 2
    UCHAR = 3
    UINT = 4
    ULONG = 5
    INT64 = 6
    UINT64 = 7
    DOUBLE = 8
    FLOAT = 9
    FLOAT16 = 10


# AMLPredefinedTypeEnum = ext.AMLPredefinedTypeEnum


class ReferrerType(IntEnum):
    Enumeration = 0
    StructType = 1
    TaggedStructType = 2
    TaggedUnionType = 3


@dataclass
class Root:
    members: list[Any] = field(default_factory=list)


@dataclass
class Referrer:
    category: ReferrerType
    identifier: str


@dataclass
class Struct:
    name: Optional[str] = field(default=None)
    members: list[Any] = field(default_factory=list)


@dataclass
class Member:
    node: Any
    is_block: bool


@dataclass
class TaggedStruct:
    name: Optional[str] = field(default=None)
    members: dict[Any] = field(default_factory=dict)


@dataclass
class TaggedStructMember:
    definition: Any
    multiple: bool


@dataclass
class TaggedStructDefinition:
    member: Any
    multiple: bool


@dataclass
class TaggedUnion:
    name: Optional[str] = field(default=None)
    members: dict[Any] = field(default_factory=dict)


@dataclass
class Enumeration:
    name: Optional[str] = field(default=None)
    values: dict[Any] = field(default_factory=dict)


@dataclass
class PDT:
    type: AMLPredefinedTypeEnum
    arr_spec: list[int]


@dataclass
class Block:
    tag: Optional[str]
    type: Any


EOF = -1


class EOFReached(Exception):
    """Signals end of token stream."""


class IfDataParser:

    def __init__(self, session):
        aml_section = session.query(model.AMLSection).first()
        if aml_section:
            aml_root = ext.unmarshal(aml_section.parsed)
            self.root = self.traverse(aml_root)
            self.syntax_stack = [self.root]
        else:
            self.root = None

    def parse(self, data):
        self.tokens = ext.ifdata_lexer(data)
        print("TOKENS", self.tokens)
        self.token_idx = 0
        self.level = 0
        self.num_tokens = len(self.tokens)

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

    def traverse(self, node):
        result = None
        if node.aml_type == AmlType.ROOT:
            result = Root()
            members = node.map.get("MEMBERS").list
            for mem in members:
                result.members.append(self.traverse(mem))
        elif node.aml_type == AmlType.STRUCT:
            result = Struct()
            mp = node.map
            name = mp.get("NAME")
            result.name = name.value
            members = mp.get("MEMBERS").list
            for mem in members:
                result.members.append(self.traverse(mem))
        elif node.aml_type == AmlType.MEMBER:
            mp = node.map
            if "IS_BLOCK" not in mp:
                print()
            is_block = bool(mp.get("IS_BLOCK").value)
            tmp_node = self.traverse(mp.get("NODE"))
            result = Member(tmp_node, is_block)
        elif node.aml_type == AmlType.STRUCT_MEMBER:
            member = node.map.get("MEMBER")
            is_block = bool(member.map.get("IS_BLOCK").value)
            tmp_node = self.traverse(member.map.get("NODE"))
            result = Member(tmp_node, is_block)
        elif node.aml_type == AmlType.MEMBERS:
            result = []
            for mem in node.list:
                result.append(self.traverse(mem))
        elif node.aml_type == AmlType.PDT:
            mp = node.map
            result = PDT(AMLPredefinedTypeEnum(mp.get("TYPE").value), [a.value for a in mp.get("ARR_SPEC").list])
        elif node.aml_type == AmlType.ENUMERATION:
            result = Enumeration()
            mp = node.map
            name = mp.get("NAME")
            result.name = name.value
            values = mp.get("VALUES").list
            for value in values:
                result.values[value.map.get("NAME").value] = value.map.get("VALUE").value
        elif node.aml_type == AmlType.TAGGED_STRUCT:
            result = TaggedStruct()
            mp = node.map
            name = mp.get("NAME")
            result.name = name.value
            members = mp.get("MEMBERS").list
            for mem in members:
                tag = mem.map["TAG"].value
                result.members[tag] = self.traverse(mem.map["MEMBER"])
        elif node.aml_type == AmlType.TAGGED_STRUCT_MEMBER:
            mp = node.map
            result = TaggedStructMember(self.traverse(mp.get("DEFINITION")), bool(mp.get("MULTIPLE").value))
        elif node.aml_type == AmlType.TAGGED_STRUCT_DEFINITION:
            mp = node.map
            result = TaggedStructDefinition(self.traverse(mp.get("MEMBER")), bool(mp.get("MULTIPLE").value))
        elif node.aml_type == AmlType.TAGGED_UNION:
            result = TaggedUnion()
            mp = node.map
            name = mp.get("NAME")
            result.name = name.value
            members = mp.get("MEMBERS").list
            for mem in members:
                tag = mem.map["TAG"].value
                result.members[tag] = self.traverse(mem.map["MEMBER"])
        elif node.aml_type == AmlType.TAGGED_UNION_MEMBER:
            mp = node.map
            tag = mp.get("TAG").value
            member = mp.get("MEMBER")
        elif node.aml_type == AmlType.BLOCK:
            mp = node.map
            tag = mp.get("TAG").value
            tp = self.traverse(mp.get("TYPE"))
            result = Block(tag, tp)
        elif node.aml_type == AmlType.REFERRER:
            result = Referrer(ReferrerType(node.map.get("CATEGORY").value), node.map.get("IDENTIFIER").value)
        elif node.aml_type == AmlType.NONE:
            result = None
        else:
            print(node)
        return result
