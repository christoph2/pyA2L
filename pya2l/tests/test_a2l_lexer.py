
import pytest

from pya2l.a2lparser import A2LTokenType
from pya2l.aml import LexerWrapper

import pytest


@pytest.mark.parametrize("test_input, expected", [
    ("47", A2LTokenType.INT),
    ("-47", A2LTokenType.INT),
    ("0xdeadaffe", A2LTokenType.HEX),
    ("0xCAFFEBABE", A2LTokenType.HEX),

    ("0.345457754", A2LTokenType.FLOAT),
    ("-0.345457754", A2LTokenType.FLOAT),
    (".345457754", A2LTokenType.FLOAT),
    ("-.345457754", A2LTokenType.FLOAT),
    ("34534.6764", A2LTokenType.FLOAT),
    ("-34534.6764", A2LTokenType.FLOAT),
    ("1e24", A2LTokenType.FLOAT),
    ("-1e24", A2LTokenType.FLOAT),
    ("1E24", A2LTokenType.FLOAT),
    ("-1E24", A2LTokenType.FLOAT),
    ("23.42e32", A2LTokenType.FLOAT),
    ("-23.42e32", A2LTokenType.FLOAT),
    ("23.42E32", A2LTokenType.FLOAT),
    ("-23.42E32", A2LTokenType.FLOAT),

    ('/begin', A2LTokenType.BEGIN),
    ('/end', A2LTokenType.END),

    ('"Hello"', A2LTokenType.STRING),
    ('"Hello World"', A2LTokenType.STRING),
    ('"/begin"', A2LTokenType.STRING),
    ('"/end"', A2LTokenType.STRING),
    ('"0815"', A2LTokenType.STRING),

    ("MEASUREMENT", A2LTokenType.IDENT),
    ("measurement", A2LTokenType.IDENT),
])
def test_tokenization(test_input, expected):
    lexer = LexerWrapper('a2l', 'a2lFile')
    res = list(lexer.lexFromString(test_input))
    assert len(res) == 1
    assert res[0].type == expected


lexer = LexerWrapper('a2l', 'a2lFile')
res = list(lexer.lexFromString("XCCV"))

print(res[0])
