#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__="""
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2014 by Christoph Schueler <github.com/Christoph2,
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
import re
import sys

import pya2l.classes as classes

BEGIN_AML = re.compile(r'/begin\s+A2ML', re.M | re.S)
END_AML = re.compile(r'/end\s+A2ML', re.M | re.S)

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

    def __init__(self, content, keywords):
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
        #print "\n\nSTATISTICS: '%s'" % sorted(self.stats.items(), key = lambda x: x[1])

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
            #print "STRING: '%s'" % lexem
            tokenType = 'STRING'
            lexem = lexem.strip('"')

            #self.stats.setdefault('STRING', 0)  # TODO: Default-Dict!!!
            self.stats['STRING'] += 1
        elif lexem.isdigit():
            tokenType = 'NUMBER'
            lexem = long(lexem)

            #self.stats.setdefault('NUMBER', 0)
            self.stats['NUMBER'] += 1
        elif lexem.startswith('0x') or lexem.startswith('0X'):
            lexem = long(lexem[2: ], 16)
            tokenType = 'HEX_NUMBER'

            #self.stats.setdefault('HEX_NUMBER', 0)
            self.stats['HEX_NUMBER'] += 1
        elif lexem in self._keywords:
            tokenType = 'KEYWORD'

            #self.stats.setdefault('KEYWORD', 0)
            self.stats['KEYWORD'] += 1
        elif lexem in ('/begin', '/end'):
            tokenType = lexem[1 : ].upper()

            #self.stats.setdefault('DELIM', 0)
            self.stats['DELIM'] += 1
        else:
            if lexem[0].isdigit() or lexem[0] or ('+', '-'):
                try:
                    lexem = float(lexem)
                    tokenType = 'FLOAT'

                    #self.stats.setdefault('FLOAT', 0)
                    self.stats['FLOAT'] += 1
                except:
                    tokenType = 'IDENT' # TODO: Checken!!!

                    #self.stats.setdefault('IDENT', 0)
                    self.stats['IDENT'] += 1
        return (tokenType, lexem)

    def genTokens(self):
        self._lineNumber = 0
        lineEnumerator = enumerate(self._content.splitlines(), 1)
        for lineNumber, line in lineEnumerator:
            match = BEGIN_AML.search(line)
            if match:
                start, end = match.span()
                savedLine = line[ : start]
                result = [line[ start : end]]
                while True:
                    lineNumber, line = lineEnumerator.next()
                    result.append(line)
                    match = END_AML.search(line)
                    if match:
                        break
                aml = ''.join(result)
                self.tokens.append((lineNumber, ("AML", aml)))
                line = savedLine
            lexems = self.lexer(line.strip())
            if lexems == []:
                continue
            for lexem in lexems:
                token = self.makeToken(lexem)
                if token[0] == None:
                    print "*** '%s%u does not match'" % (lexem, lineNum)
                else:
                    pass
                self.tokens.append((lineNumber, token, ))

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

