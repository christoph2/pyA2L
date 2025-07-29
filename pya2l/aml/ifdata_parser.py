from collections import defaultdict
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Optional

import pya2l.model as model
from pya2l.a2lparser_ext import AmlType, unmarshal
from pya2l.aml.ifdata_lexer import IfDataLexer


class IfDataTokenType(IntEnum):
    NONE = 0
    IDENT = 1
    FLOAT = 2
    INT = 3
    COMMENT = 4
    STRING = 6
    BEGIN = 7
    END = 8
    WS = 9


@dataclass
class IfDataToken:
    type: IfDataTokenType
    value: Any


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


@dataclass
class NullObject:
    pass


EOF = -1


class EOFReached(Exception):
    """Signals end of token stream."""


def create_ref_dict(tree) -> defaultdict[ReferrerType, dict]:
    result: defaultdict[ReferrerType, dict] = defaultdict(dict)
    members = tree.members
    non_blocks = [m for m in members if not isinstance(m, (Block, NullObject))]
    for member in non_blocks:
        if isinstance(member, Struct):
            tp = ReferrerType.StructType
        elif isinstance(member, TaggedStruct):
            tp = ReferrerType.TaggedStructType
        elif isinstance(member, TaggedUnion):
            tp = ReferrerType.TaggedUnionType
        elif isinstance(member, Enumeration):
            tp = ReferrerType.Enumeration
        else:
            raise TypeError("Implement ME!!!")
        result[tp][member.name] = member
    return result


def toplevel_ifdata(tree) -> Any:
    members = [m for m in tree.members if m is not isinstance(m, NullObject)]
    blocks = [m for m in members if isinstance(m, Block)]
    if blocks:
        for member in blocks:
            if isinstance(member, Block):
                if member.tag == "IF_DATA":
                    return member.type
    else:
        if len(members) == 1:
            return members[0]
        else:
            raise ValueError("Dont know how to handle.")
        print(len(tree.members), type(members[0]), [t.members.keys() for t in members])
        raise TypeError("NO BLOCKS!!!")


class IfDataParser:

    def __init__(self, session) -> None:
        aml_section = session.query(model.AMLSection).first()
        if aml_section:
            aml_root = unmarshal(aml_section.parsed)
            self.root = self.traverse(aml_root)
            if self.root.members:
                self.syntax_stack = [toplevel_ifdata(self.root)]
                self.ref_dict: defaultdict[ReferrerType, dict] = create_ref_dict(self.root)
            else:
                self.root = None
        else:
            self.root = None

    def parse(self, data) -> dict:
        if self.root is None:
            return {}
        lexer = IfDataLexer(data)
        self.tokens = lexer.run()
        self.token_idx = 0
        self.level = 0
        self.num_tokens = len(self.tokens)

        self.match(IfDataTokenType.BEGIN)
        self.match(IfDataTokenType.IDENT, "IF_DATA")
        result = self.enter(self.syntax_tos)
        self.leave()
        self.match(IfDataTokenType.END)
        self.match(IfDataTokenType.IDENT, "IF_DATA")
        return result

    def block(self):
        self.match(IfDataTokenType.BEGIN)
        tk = self.current_token
        tk_type = tk.type
        tk_value = tk.value
        if tk_type == IfDataTokenType.IDENT:
            self.consume()
            result = self.enter(self.syntax_tos.type)
            self.leave()
            self.match(IfDataTokenType.END)
            self.match(IfDataTokenType.IDENT, tk_value)
            # return {tk_value: result}
            return result
        else:
            raise TypeError(f"Expected IDENT got {tk_type}[{tk_value!r}].")

    def tagged_struct(self):
        result = defaultdict(list)
        while True:
            if self.current_token.type == IfDataTokenType.END:
                break
            elif self.current_token.type == IfDataTokenType.BEGIN:
                tk = self.lookahead(1)
            else:
                tk = self.current_token
            tk_type = tk.type
            tk_value = tk.value
            if tk_value not in self.syntax_tos.members:
                break
            if tk_type == IfDataTokenType.IDENT:
                elem = self.syntax_tos.members.get(tk_value)
                if (
                    isinstance(elem, TaggedStructMember)
                    and not isinstance(elem.definition, Block)
                    and elem.definition.member is None
                ):
                    result[tk_value].append(True)  # Just a flag value with no further definition.
                    self.consume()
                else:
                    multiple = elem.multiple
                    while True:
                        tmp_value = self.enter(elem.definition)
                        if tmp_value:
                            result[tk_value].append(tmp_value)
                        self.leave()
                        if not multiple:
                            break
                        if self.current_token.value != tk_value:
                            break
                        if self.current_token.type == IfDataTokenType.END:
                            break
            else:
                print(f"Invalid token {tk.type} for tagged struct. Expected identifier.")
        return_value = {}
        for k, v in result.items():
            if isinstance(self.syntax_tos.members, dict):
                member = self.syntax_tos.members.get(k)
                if member is None:
                    return_value[k] = v
                else:
                    if not member.multiple:
                        return_value[k] = v[0]
                    else:
                        return_value[k] = v
            else:
                return_value[k] = v
        return return_value

    def tagged_union(self):
        if self.current_token.type == IfDataTokenType.BEGIN:
            tk = self.lookahead(1)
            self.consume()
        else:
            tk = self.current_token
        if tk.type != IfDataTokenType.IDENT:
            print(f"Invalid token {tk.type} for tagged union. Expected identifier.")
            return
        tk_value = tk.value
        self.consume()
        mem_dict = self.syntax_tos.members
        if tk_value in mem_dict:
            member = mem_dict[tk_value]
            if isinstance(member, Block):
                result = self.enter(member.type)
                self.leave()
                self.match(IfDataTokenType.END)
                self.match(IfDataTokenType.IDENT, tk_value)
                return {tk_value: result}
            else:
                if isinstance(member, NullObject):
                    result = True  # Just a flag value with no further definition.
                    # self.consume()
                else:
                    result = self.enter(member.node)
                self.leave()
                return {tk_value: result}
        else:
            raise ValueError(f"tag {tk_value} not found.")  # SyntaxError("Tag not found in struct")

    def struct(self):
        result: list = []
        for member in self.syntax_tos.members:
            result.append(self.enter(member.node))
            self.leave()
        return result

    def validate_pdt(self, token):
        pass

    def pdt(self):
        tk = self.current_token
        self.consume()
        arr_spec = self.syntax_tos.arr_spec
        if arr_spec:
            pass
        # TODO: Validate PDT
        return tk.value

    def enumeration(self):
        tk = self.current_token
        self.consume()
        if tk.value not in self.syntax_tos.values:
            pass
        return tk.value

    def member(self):
        result = self.enter(self.syntax_tos.node)
        self.leave()
        return result

    def tagged_struct_definition(self):
        result = None
        multiple = self.syntax_tos.multiple
        self.consume()
        if multiple:
            result = []
            while True:
                value = self.enter(self.syntax_tos.member)
                self.leave()
                result.append(value)
                if self.current_token.type in (IfDataTokenType.IDENT, IfDataTokenType.BEGIN, IfDataTokenType.END):
                    break
        else:
            result = self.enter(self.syntax_tos.member)
            self.leave()
        return result

    def enter(self, klass) -> Any:
        result: Any = None
        if isinstance(klass, Referrer):
            klass = self.ref_dict[klass.category][klass.identifier]
        self.syntax_stack.append(klass)
        if isinstance(klass, Block):
            result = self.block()
        elif isinstance(klass, TaggedStruct):
            result = self.tagged_struct()
        elif isinstance(klass, TaggedUnion):
            result = self.tagged_union()
        elif isinstance(klass, Struct):
            result = self.struct()
        elif isinstance(klass, Enumeration):
            result = self.enumeration()
        elif isinstance(klass, Member):
            result = self.member()
        elif isinstance(klass, TaggedStructDefinition):
            result = self.tagged_struct_definition()
        elif isinstance(klass, PDT):
            result = self.pdt()
        elif isinstance(klass, NullObject):
            result = {}
        else:
            print(f"Unsupported class {klass!r}")
        self.level += 1
        return result

    def leave(self) -> None:
        self.syntax_stack.pop()
        self.level -= 1

    @property
    def syntax_tos(self):
        return self.syntax_stack[-1]

    @property
    def current_token(self) -> IfDataToken:
        """Get the token at the current stream position."""
        return self.lookahead(0)

    def lookahead(self, n: int = 1) -> IfDataToken:
        """Get the token `n` elements ahead of current stream position."""
        index = self.token_idx + n
        if index < self.num_tokens:
            return self.tokens[index]
        else:
            raise EOFReached()

    def consume(self) -> None:
        """Increment token stream position by one."""
        self.token_idx += 1

    def match(self, token_type: IfDataTokenType, value: Optional[Any] = None) -> bool:
        ok = self.current_token.type == token_type
        token_value = self.current_token.value
        self.consume()
        if value is None:
            return ok
        else:
            if not ok:
                return False
            return token_value == value

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
        elif node.aml_type == AmlType.NULL_NODE:
            result = NullObject()
        elif node.aml_type == AmlType.NONE:
            result = None
        else:
            print(node)
        return result
