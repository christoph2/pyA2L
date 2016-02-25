#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__="""
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2016 by Christoph Schueler <github.com/Christoph2,
                                        cpu12.gems@googlemail.com>

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

import collections
import enum
import re
import sys

import pya2l.classes as classes
from pya2l.logger import Logger

BEGIN_AML = re.compile(r'/begin\s+A2ML', re.M | re.S)
END_AML = re.compile(r'/end\s+A2ML', re.M | re.S)
HEX_NUMBER = re.compile(r'^[0-9a-fA-F]+$')
IDENTIFIER = re.compile(r'^[a-zA-Z_][a-zA-Z_0-9]*$')


class TokenType(enum.IntEnum):
    BEGIN       = 1
    END         = 2
    KEYWORD     = 3
    AML         = 4
    KEYWORD     = 5
    IDENT       = 6
    NUMBER      = 7
    HEX_NUMBER  = 8
    STRING      = 9
    FLOAT       = 10


class Tokenizer(object):


    TOKENS = re.compile(r"""
          \s*"(?P<STRING>[^"]*?)"
        | \s*(?P<IDENT>[a-zA-Z_][a-zA-Z_0-9.|]*)
        | \s*(?P<BEGIN>/begin)
        | \s*(?P<END>/end)
        | \s*(?P<NUMBER>
                  (0(x|X)?[0-9a-fA-F]+)
                | ((\+ | \-)?\d+)
             )
    """, re.VERBOSE | re.DOTALL)

    def __init__(self, filename, content, keywords):
        self.logger = Logger(self, 'lexer')
        self.filename = filename
        self._content = content
        self._lexems = []
        self._keywords = keywords
        self.stats = collections.defaultdict(int)
        self.tokens = []
        self.tokenIndex = 0
        self.genTokens()
        self.numTokens = len(self.tokens)

    def __del__(self):
        pass

    def lexer(self, line, stringDelimiter = '"', splitBy = None):
        """Split a line into tokens while considering delimited strings."""

        head, sep, tail = line.partition(stringDelimiter)
        if sep:
            result = []
            if head:
                result.extend(head.split(splitBy))
            head, sep, tail = tail.partition(stringDelimiter)
            result.extend(["%(sep)s%(value)s%(sep)s" % {'value': head, 'sep': stringDelimiter }])
            if tail:
                result.extend(self.lexer(tail))
            return result
        else:
            if head:
                result = head.split(splitBy)
            else:
                result = list()
            return result

    def makeToken(self, lexem):
        tokenType = None
        if lexem.startswith('"') and lexem.endswith('"'):
            tokenType = TokenType.STRING
            lexem = lexem.strip('"')

            self.stats[TokenType.STRING] += 1
        elif lexem.isdigit():
            tokenType = TokenType.NUMBER
            lexem = long(lexem)
            self.stats[TokenType.NUMBER] += 1
        elif lexem.startswith('0x') or lexem.startswith('0X'):
            if HEX_NUMBER.match(lexem[2 : ]):   # Look before you leap.
                tokenType = TokenType.HEX_NUMBER
                lexem = long(lexem[2: ], 16)
            else:
                tokenType = TokenType.IDENT
                self.checkIdentifier(lexem)
            self.stats[TokenType.HEX_NUMBER] += 1
        elif lexem.lower() == '/begin':
            tokenType = TokenType.BEGIN
        elif lexem.lower() == '/end':
            tokenType = TokenType.END
        elif lexem in self._keywords:
            tokenType = TokenType.KEYWORD
            self.stats[TokenType.KEYWORD] += 1
        else:
            if lexem[0].isdigit() or lexem[0] or ('+', '-'):
                try:
                    lexem = float(lexem)
                    tokenType = TokenType.FLOAT

                    self.stats[TokenType.FLOAT] += 1
                except:
                    tokenType = TokenType.IDENT
                    self.checkIdentifier(lexem)
        return (tokenType, lexem)

    def genTokens(self):
        lineEnumerator = enumerate(self._content.splitlines(), 1)
        for lineNo, line in lineEnumerator:
            self.lineNo = lineNo
            match = BEGIN_AML.search(line)
            if match:
                start, end = match.span()
                savedLine = line[ : start]
                result = [line[ start : end]]
                while True:
                    self.lineNo, line = lineEnumerator.next()
                    result.append(line)
                    match = END_AML.search(line)
                    if match:
                        break
                aml = ''.join(result)
                self.tokens.append((self.lineNo, (TokenType.AML, aml)))
                line = savedLine
            lexems = self.lexer(line.strip())
            if lexems == []:
                continue
            for lexem in lexems:
                token = self.makeToken(lexem)
                if token[0] == None:
                    print("*** '%s%u does not match'" % (lexem, self.lineNo))
                else:
                    pass
                self.tokens.append((self.lineNo, token, ))

    def tokenAvailable(self):
        return self.tokenIndex < self.numTokens

    def getToken(self):
        token = self.tokens[self.tokenIndex]
        self.tokenIndex += 1
        return token

    def peekToken(self):
        token = self.tokens[self.tokenIndex]
        return token

    def stepBack(self, count = 1):
        self.tokenIndex -= count

    def checkIdentifier(self, identifier):
        for item in identifier.split('.'):  # Identifiers can be hierarchically.
            if not IDENTIFIER.match(item):
                self.logger.warn("Part '{1}' of identifier '{0}' is not a valid C-identifier.".format(identifier, item))

