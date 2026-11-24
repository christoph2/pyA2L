from unittest.mock import Mock

import pytest

from pya2l.aml.ifdata_lexer import IfDataToken, IfDataTokenType
from pya2l.aml.ifdata_parser import (
    PDT,
    AMLPredefinedTypeEnum,
    IfDataParser,
    Member,
    ParsingError,
    Referrer,
    ReferrerType,
    Struct,
    TaggedStruct,
    TaggedStructDefinition,
    TaggedStructMember,
)


@pytest.mark.parametrize(
    ("pdt_type", "array", "token_type", "value", "valid"),
    [
        (AMLPredefinedTypeEnum.INT, [], IfDataTokenType.INT, 0, True),
        (AMLPredefinedTypeEnum.LONG, [], IfDataTokenType.INT, -1, True),
        (AMLPredefinedTypeEnum.UCHAR, [], IfDataTokenType.INT, 1, True),
        (AMLPredefinedTypeEnum.UINT, [], IfDataTokenType.INT, 1, True),
        (AMLPredefinedTypeEnum.ULONG, [], IfDataTokenType.INT, 1, True),
        (AMLPredefinedTypeEnum.INT64, [], IfDataTokenType.INT, 1, True),
        (AMLPredefinedTypeEnum.UINT64, [], IfDataTokenType.INT, 1, True),
        (AMLPredefinedTypeEnum.UINT, [], IfDataTokenType.FLOAT, 1.0, False),
        (AMLPredefinedTypeEnum.FLOAT16, [], IfDataTokenType.FLOAT, 1.5, True),
        (AMLPredefinedTypeEnum.FLOAT, [], IfDataTokenType.INT, 1, True),
        (AMLPredefinedTypeEnum.DOUBLE, [], IfDataTokenType.FLOAT, 1.5, True),
        (AMLPredefinedTypeEnum.DOUBLE, [], IfDataTokenType.IDENT, "BAD", False),
        (AMLPredefinedTypeEnum.CHAR, [], IfDataTokenType.INT, 65, True),
        (AMLPredefinedTypeEnum.CHAR, [], IfDataTokenType.STRING, "A", True),
        (AMLPredefinedTypeEnum.CHAR, [], IfDataTokenType.STRING, "AB", False),
        (AMLPredefinedTypeEnum.CHAR, [256], IfDataTokenType.STRING, "", True),
        (AMLPredefinedTypeEnum.CHAR, [256], IfDataTokenType.STRING, "abc", True),
        (AMLPredefinedTypeEnum.CHAR, [256], IfDataTokenType.INT, 65, False),
        (AMLPredefinedTypeEnum.UCHAR, [], IfDataTokenType.END, "/end", False),
    ],
)
def test_validate_pdt(pdt_type, array, token_type, value, valid):
    parser = IfDataParser.__new__(IfDataParser)
    parser.syntax_stack = [PDT(pdt_type, array)]

    assert parser.validate_pdt(IfDataToken(token_type, value)) is valid


@pytest.fixture
def nested_parser():
    parser = IfDataParser.__new__(IfDataParser)
    parser.logger = Mock()
    parser.root = object()
    parser.syntax_stack = [
        TaggedStruct(
            members={
                "EMPTY": TaggedStructMember(TaggedStructDefinition(TaggedStruct(), False), False),
                "VALUE": TaggedStructMember(TaggedStructDefinition(PDT(AMLPredefinedTypeEnum.INT, []), False), False),
            }
        )
    ]
    parser.ref_dict = {}
    return parser


def test_empty_result_is_distinct_from_failed_nested_parse(nested_parser):
    parser = nested_parser
    root = parser.syntax_tos

    assert parser.parse("/begin IF_DATA EMPTY /end IF_DATA") == {"EMPTY": {}}
    with pytest.raises(ParsingError, match="Expected INT value, got END"):
        parser.parse("/begin IF_DATA VALUE /end IF_DATA")
    assert parser.syntax_stack == [root]
    assert parser.level == 0
    assert parser.parse("/begin IF_DATA EMPTY VALUE 0 /end IF_DATA") == {"EMPTY": {}, "VALUE": 0}


def test_nested_exception_is_preserved_and_parser_can_be_reused(nested_parser, monkeypatch):
    parser = nested_parser
    root = parser.syntax_tos
    cause = RuntimeError("nested failure")

    def fail():
        raise cause

    with monkeypatch.context() as patch:
        patch.setattr(parser, "pdt", fail)
        with pytest.raises(ParsingError, match="nested failure") as exc:
            parser.parse("/begin IF_DATA EMPTY VALUE 1 /end IF_DATA")

    assert exc.value.__cause__ is cause
    assert parser.syntax_stack == [root]
    assert parser.level == 0
    assert parser.parse("/begin IF_DATA VALUE 1 /end IF_DATA") == {"VALUE": 1}


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("/begin IF_DATA 7 /end IF_DATA", [{}, 7, {}]),
        ("/begin IF_DATA FIRST 2 7 /end IF_DATA", [{"FIRST": 2}, 7, {}]),
        ("/begin IF_DATA 7 LAST 3 /end IF_DATA", [{}, 7, {"LAST": 3}]),
        ("/begin IF_DATA FIRST 2 0 LAST 3 /end IF_DATA", [{"FIRST": 2}, 0, {"LAST": 3}]),
    ],
)
def test_struct_preserves_empty_tagged_struct_positions(nested_parser, raw, expected):
    parser = nested_parser
    integer = PDT(AMLPredefinedTypeEnum.INT, [])
    first = TaggedStruct(members={"FIRST": TaggedStructMember(TaggedStructDefinition(integer, False), False)})
    last = TaggedStruct(members={"LAST": TaggedStructMember(TaggedStructDefinition(integer, False), False)})
    parser.ref_dict = {ReferrerType.TaggedStructType: {"first": first}}
    parser.syntax_stack = [
        Struct(
            members=[
                Member(Referrer(ReferrerType.TaggedStructType, "first"), False),
                Member(integer, False),
                Member(last, False),
            ]
        )
    ]

    assert parser.parse(raw) == expected
