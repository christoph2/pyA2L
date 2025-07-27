import re
from dataclasses import dataclass
from enum import IntEnum
from typing import Any, List, Optional


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


PAT_WS = re.compile(r"\s+")
PAT_BEGIN = re.compile("/begin")
PAT_END = re.compile("/end")

PAT_COMMENT = re.compile(r"(/\*.*?\*/)|(//.*?)")
PAT_STRING = re.compile(r'"[^"]*"')

PAT_FLOAT = re.compile(r"[+\-]?(\d+([.]\d*)?([eE][+\-]?\d+)?|[.]\d+([eE][+\-]?\d+)?)")

PAT_INT = re.compile(r"(0x[0-9a-fA-F]+)|([+\-]?[0-9]+)")
PAT_IDENT = re.compile(r"([a-zA-Z_][a-zA-Z_0-9.]*)\b")


def identity(value: Any) -> Any:
    return value


def stripper(text: str) -> str:
    return text.strip('"')


def convert_to_float(value: str) -> float:
    return float(value)


def convert_to_int(value: str) -> int:
    base = 16 if value.lower().startswith("0x") else 10
    return int(value, base)


EXPRESSIONS = [
    (IfDataTokenType.WS, PAT_WS, identity),
    (IfDataTokenType.COMMENT, PAT_COMMENT, identity),
    (IfDataTokenType.STRING, PAT_STRING, stripper),
    (IfDataTokenType.INT, PAT_INT, convert_to_int),
    (IfDataTokenType.FLOAT, PAT_FLOAT, convert_to_float),
    (IfDataTokenType.BEGIN, PAT_BEGIN, identity),
    (IfDataTokenType.END, PAT_END, identity),
    (IfDataTokenType.IDENT, PAT_IDENT, identity),
]


class IfDataLexer:

    def __init__(self, section: str, skip_list: list[IfDataTokenType] = [IfDataTokenType.WS, IfDataTokenType.COMMENT]):
        self.section = section
        self.section_length = len(section)
        self.skip_list = skip_list
        self.pos = 0

    def run(self) -> List[IfDataToken]:
        result = []
        while self.pos < self.section_length:
            token = self.get_token()
            if token is not None:
                result.append(token)
        return result

    def get_token(self) -> Optional[IfDataToken]:
        for code, expr, converter in EXPRESSIONS:
            match = expr.match(self.section, self.pos)
            if match:
                self.pos += match.end() - match.start()
                text = match.group()
                if code in self.skip_list:
                    return None
                return IfDataToken(code, converter(text))
        print(f"Invalid char {self.section[self.pos]!r}")
        self.pos += 1
        return None


def ifdata_lexer(
    section: str, skip_list: list[IfDataTokenType] = [IfDataTokenType.WS, IfDataTokenType.COMMENT]
) -> List[IfDataToken]:
    length = len(section)
    pos = 0
    result = []

    while pos < length:
        found = False
        for code, expr in EXPRESSIONS:
            match = expr.match(section, pos)
            if match:
                pos += match.end() - match.start()
                if pos > 60:
                    print()
                text = match.group()
                if code in skip_list:
                    continue
                print(code.name, text)
                found = True
                result.append(IfDataToken(code, text))
                continue
        if not found:
            print(f"Invalid char {section[pos]!r}")
            pos += 1
    return result
