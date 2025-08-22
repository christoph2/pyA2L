"""
IF_DATA Parser Module

This module provides functionality for parsing IF_DATA sections in A2L files.
It uses a token-based approach with a syntax tree to interpret the structure
of IF_DATA sections according to AML definitions.

The main class is IfDataParser which handles the parsing of IF_DATA sections.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional, Union

import pya2l.model as model
from pya2l.a2lparser_ext import AmlType, unmarshal
from pya2l.aml.ifdata_lexer import IfDataLexer
from pya2l.logger import Logger


class IfDataTokenType(IntEnum):
    """Token types used by the IF_DATA parser."""

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
    """Represents a token in the IF_DATA section."""

    type: IfDataTokenType
    value: Any


class AMLPredefinedTypeEnum(IntEnum):
    """Predefined types in AML."""

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


class ReferrerType(IntEnum):
    """Types of referrers in AML."""

    Enumeration = 0
    StructType = 1
    TaggedStructType = 2
    TaggedUnionType = 3


@dataclass
class Root:
    """Root node of the AML tree."""

    members: List[Any] = field(default_factory=list)


@dataclass
class Referrer:
    """Reference to another node in the AML tree."""

    category: ReferrerType
    identifier: str


@dataclass
class Struct:
    """Represents a struct in AML."""

    name: Optional[str] = field(default=None)
    members: List[Any] = field(default_factory=list)


@dataclass
class Member:
    """Represents a member of a struct in AML."""

    node: Any
    is_block: bool


@dataclass
class TaggedStruct:
    """Represents a tagged struct in AML."""

    name: Optional[str] = field(default=None)
    members: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaggedStructMember:
    """Represents a member of a tagged struct in AML."""

    definition: Any
    multiple: bool


@dataclass
class TaggedStructDefinition:
    """Represents the definition of a tagged struct in AML."""

    member: Any
    multiple: bool


@dataclass
class TaggedUnion:
    """Represents a tagged union in AML."""

    name: Optional[str] = field(default=None)
    members: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Enumeration:
    """Represents an enumeration in AML."""

    name: Optional[str] = field(default=None)
    values: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PDT:
    """Represents a predefined type in AML."""

    type: AMLPredefinedTypeEnum
    arr_spec: List[int]


@dataclass
class Block:
    """Represents a block in AML."""

    tag: Optional[str]
    type: Any


@dataclass
class NullObject:
    """Represents a null object in AML."""

    pass


class EOFReached(Exception):
    """Signals end of token stream."""

    pass


class ParsingError(Exception):
    """Signals an error during parsing."""

    pass


def create_ref_dict(tree) -> defaultdict:
    """
    Create a dictionary of references from the AML tree.

    Args:
        tree: The AML tree root

    Returns:
        A dictionary mapping referrer types to dictionaries of named elements
    """
    result: defaultdict = defaultdict(dict)
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
            raise TypeError(f"Unsupported member type: {type(member).__name__}")

        result[tp][member.name] = member

    return result


def toplevel_ifdata(tree) -> Any:
    """
    Find the IF_DATA block in the AML tree.

    Args:
        tree: The AML tree root

    Returns:
        The IF_DATA block type

    Raises:
        ValueError: If the tree structure is not as expected
        TypeError: If no blocks are found
    """
    members = [m for m in tree.members if not isinstance(m, NullObject)]
    blocks = [m for m in members if isinstance(m, Block)]

    if blocks:
        for member in blocks:
            if isinstance(member, Block) and member.tag == "IF_DATA":
                return member.type
        raise ValueError("No IF_DATA block found in the AML tree")
    elif len(members) == 1:
        return members[0]
    else:
        raise ValueError("Invalid AML tree structure")


class IfDataParser:
    """
    Parser for IF_DATA sections in A2L files.

    This class parses IF_DATA sections according to AML definitions.
    It uses a token-based approach with a syntax tree to interpret
    the structure of IF_DATA sections.
    """

    def __init__(self, session, loglevel: str = "INFO") -> None:
        """
        Initialize the IF_DATA parser.

        Args:
            session: The database session containing AML definitions
            loglevel: The logging level
        """
        self.logger = Logger("IF_DATA", loglevel)
        self.root = None
        self.syntax_stack = []
        self.ref_dict = None
        self.tokens = []
        self.token_idx = 0
        self.level = 0
        self.num_tokens = 0

        # Initialize from session
        aml_section = session.query(model.AMLSection).first()
        if aml_section:
            aml_root = unmarshal(aml_section.parsed)
            self.root = self.traverse(aml_root)
            if self.root and self.root.members:
                try:
                    self.syntax_stack = [toplevel_ifdata(self.root)]
                    self.ref_dict = create_ref_dict(self.root)
                except (ValueError, TypeError) as e:
                    self.logger.error(f"Failed to initialize parser: {str(e)}")
                    self.root = None

    def parse(self, data) -> Dict:
        """
        Parse an IF_DATA section.

        Args:
            data: The IF_DATA section text

        Returns:
            A dictionary representing the parsed IF_DATA section

        Raises:
            ParsingError: If parsing fails
        """
        if self.root is None:
            self.logger.warn("Parser not initialized properly, returning empty result")
            return {}

        try:
            # Tokenize the input
            lexer = IfDataLexer(data)
            self.tokens = lexer.run()
            self.token_idx = 0
            self.level = 0
            self.num_tokens = len(self.tokens)

            # Parse the IF_DATA section
            self.match(IfDataTokenType.BEGIN)
            self.match(IfDataTokenType.IDENT, "IF_DATA")
            result = self.enter(self.syntax_tos)
            self.leave()
            self.match(IfDataTokenType.END)
            self.match(IfDataTokenType.IDENT, "IF_DATA")

            return result
        except EOFReached:
            self.logger.error("Unexpected end of input")
            raise ParsingError("Unexpected end of input")
        except Exception as e:
            self.logger.error(f"Error parsing IF_DATA: {str(e)}")
            raise ParsingError(f"Error parsing IF_DATA: {str(e)}")

    def block(self) -> Dict:
        """
        Parse a block in the IF_DATA section.

        Returns:
            A dictionary representing the parsed block

        Raises:
            TypeError: If the token type is not as expected
        """
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
            return result
        else:
            raise TypeError(f"Expected IDENT got {tk_type}[{tk_value!r}].")

    def tagged_struct(self) -> Dict:
        """
        Parse a tagged struct in the IF_DATA section.

        Returns:
            A dictionary representing the parsed tagged struct
        """
        result = defaultdict(list)

        while True:
            # Check for end of struct
            if self.current_token.type == IfDataTokenType.END:
                break

            # Get the token to check
            if self.current_token.type == IfDataTokenType.BEGIN:
                tk = self.lookahead(1)
            else:
                tk = self.current_token

            tk_type = tk.type
            tk_value = tk.value

            # Check if the token is a valid member
            if tk_value not in self.syntax_tos.members:
                break

            if tk_type == IfDataTokenType.IDENT:
                elem = self.syntax_tos.members.get(tk_value)

                # Handle flag values with no further definition
                if (
                    isinstance(elem, TaggedStructMember)
                    and not isinstance(elem.definition, Block)
                    and elem.definition.member is None
                ):
                    result[tk_value].append(True)
                    self.consume()
                else:
                    multiple = elem.multiple

                    # Handle multiple values
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
                token_type_name = IfDataTokenType(tk.type).name
                self.logger.error(f"Invalid token {token_type_name} for tagged struct. Expected IDENT.")

        # Process the results
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

    def tagged_union(self) -> Dict:
        """
        Parse a tagged union in the IF_DATA section.

        Returns:
            A dictionary representing the parsed tagged union
        """
        # Check if this is a block
        if self.current_token.type == IfDataTokenType.BEGIN:
            tk = self.lookahead(1)
            self.consume()
            block = True
        else:
            tk = self.current_token
            block = False

        # Validate token type
        if tk.type != IfDataTokenType.IDENT:
            token_type_name = IfDataTokenType(tk.type).name
            self.logger.error(f"Invalid token {token_type_name} for tagged union. Expected IDENT.")
            if block:
                self.rewind()
            return {}

        tk_value = tk.value
        self.consume()

        # Get the member
        mem_dict = self.syntax_tos.members
        if tk_value in mem_dict:
            member = mem_dict[tk_value]

            # Handle block members
            if isinstance(member, Block):
                result = self.enter(member.type)
                self.leave()
                self.match(IfDataTokenType.END)
                self.match(IfDataTokenType.IDENT, tk_value)
                return {tk_value: result}
            else:
                # Handle other members
                if isinstance(member, NullObject):
                    result = True  # Just a flag value with no further definition
                else:
                    result = self.enter(member.node)
                    self.leave()
                return {tk_value: result}
        else:
            self.logger.error(f"TAGGED_UNION has no member {tk_value!r}.")
            amount = 2 if block else 1
            self.rewind(amount)
            return {}

    def struct(self) -> List:
        """
        Parse a struct in the IF_DATA section.

        Returns:
            A list representing the parsed struct
        """
        result = []

        for member in self.syntax_tos.members:
            tmp_res = self.enter(member.node)
            if tmp_res != {}:
                result.append(tmp_res)
            self.leave()

        return result

    def validate_pdt(self, token: IfDataToken) -> bool:
        """
        Validate a predefined type token.

        Args:
            token: The token to validate

        Returns:
            True if the token is valid, False otherwise
        """
        pdt_type = self.syntax_tos.type

        # Validate token type against PDT type
        if pdt_type == AMLPredefinedTypeEnum.INT or pdt_type == AMLPredefinedTypeEnum.LONG:
            return token.type == IfDataTokenType.INT
        elif pdt_type == AMLPredefinedTypeEnum.FLOAT or pdt_type == AMLPredefinedTypeEnum.DOUBLE:
            return token.type in (IfDataTokenType.FLOAT, IfDataTokenType.INT)
        elif pdt_type == AMLPredefinedTypeEnum.CHAR:
            return token.type == IfDataTokenType.STRING and len(token.value) == 1

        # Default validation
        return True

    def pdt(self) -> Any:
        """
        Parse a predefined type in the IF_DATA section.

        Returns:
            The value of the predefined type
        """
        tk = self.current_token

        # Validate the token
        #
        # TODO: Add support for array types.
        # if not self.validate_pdt(tk):
        #    token_type_name = IfDataTokenType(tk.type).name
        #    pdt_type_name = AMLPredefinedTypeEnum(self.syntax_tos.type).name
        #    self.logger.warn(f"Token {token_type_name}[{tk.value}] may not be valid for PDT type {pdt_type_name}")

        self.consume()

        # Handle array specifications
        arr_spec = self.syntax_tos.arr_spec
        if arr_spec:
            # Array handling would go here
            pass

        return tk.value

    def enumeration(self) -> str:
        """
        Parse an enumeration in the IF_DATA section.

        Returns:
            The value of the enumeration
        """
        tk = self.current_token
        self.consume()

        # Validate the enumeration value
        if tk.value not in self.syntax_tos.values:
            self.logger.warn(f"Enumeration value {tk.value!r} not found in {self.syntax_tos.name}")

        return tk.value

    def member(self) -> Any:
        """
        Parse a member in the IF_DATA section.

        Returns:
            The parsed member
        """
        result = self.enter(self.syntax_tos.node)
        self.leave()
        return result

    def tagged_struct_definition(self) -> Union[List, Any]:
        """
        Parse a tagged struct definition in the IF_DATA section.

        Returns:
            The parsed tagged struct definition
        """
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
        """
        Enter a node in the syntax tree.

        Args:
            klass: The node to enter

        Returns:
            The parsed result

        Raises:
            TypeError: If the node type is not supported
        """
        # Resolve references
        if isinstance(klass, Referrer):
            klass = self.ref_dict[klass.category][klass.identifier]

        self.syntax_stack.append(klass)

        try:
            # Dispatch based on node type
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
                self.logger.error(f"Unsupported class {type(klass).__name__}")
                raise TypeError(f"Unsupported class {type(klass).__name__}")

            self.level += 1
            return result
        except Exception as e:
            self.logger.error(f"Error in enter({type(klass).__name__}): {str(e)}")
            self.level += 1
            return {}

    def leave(self) -> None:
        """Leave the current node in the syntax tree."""
        self.syntax_stack.pop()
        self.level -= 1

    @property
    def syntax_tos(self) -> Any:
        """
        Get the top of the syntax stack.

        Returns:
            The top element of the syntax stack
        """
        return self.syntax_stack[-1]

    @property
    def current_token(self) -> IfDataToken:
        """
        Get the token at the current stream position.

        Returns:
            The current token
        """
        return self.lookahead(0)

    def lookahead(self, n: int = 1) -> IfDataToken:
        """
        Get the token `n` elements ahead of current stream position.

        Args:
            n: The number of elements to look ahead

        Returns:
            The token at position current + n

        Raises:
            EOFReached: If the position is beyond the end of the token stream
        """
        index = self.token_idx + n
        if index < self.num_tokens:
            return self.tokens[index]
        else:
            raise EOFReached()

    def consume(self) -> None:
        """Increment token stream position by one."""
        self.token_idx += 1

    def rewind(self, n: int = 1) -> None:
        """
        Back up token stream position by `n` elements.

        Args:
            n: The number of elements to back up
        """
        self.token_idx = max(0, self.token_idx - n)

    def match(self, token_type: IfDataTokenType, value: Optional[Any] = None) -> bool:
        """
        Match the current token against the expected type and value.

        Args:
            token_type: The expected token type
            value: The expected token value (optional)

        Returns:
            True if the match succeeded, False otherwise
        """
        try:
            ok = self.current_token.type == token_type

            if not ok:
                expected_type_name = token_type.name
                actual_type_name = IfDataTokenType(self.current_token.type).name
                self.logger.error(f"{expected_type_name} not matched against {actual_type_name}")

                # Try to recover by finding the next token of the expected type
                recovery_limit = 10  # Limit recovery attempts to avoid infinite loops
                recovery_count = 0

                while recovery_count < recovery_limit:
                    self.consume()
                    recovery_count += 1

                    if self.current_token.type == token_type:
                        ok = True
                        break

                if not ok:
                    self.logger.error(f"Failed to recover from token mismatch after {recovery_count} attempts")

            token_value = self.current_token.value
            self.consume()

            if value is None:
                return ok
            else:
                if not ok:
                    return False

                value_match = token_value == value
                if not value_match:
                    self.logger.error(f"Value mismatch: expected {value!r}, got {token_value!r}")

                return value_match

        except EOFReached:
            self.logger.error("Unexpected end of input during token matching")
            return False

    def traverse(self, node) -> Any:
        """
        Traverse the AML tree and convert it to the internal representation.

        Args:
            node: The AML node to traverse

        Returns:
            The internal representation of the node
        """
        result = None

        try:
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
                # This case seems incomplete in the original code
                mp = node.map
                tag = mp.get("TAG").value
                member = mp.get("MEMBER")
                # Return a proper result for this case
                result = self.traverse(member)

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
                self.logger.warn(f"Unhandled AML type: {node.aml_type}")

        except Exception as e:
            self.logger.error(f"Error traversing node of type {getattr(node, 'aml_type', 'unknown')}: {str(e)}")

        return result
