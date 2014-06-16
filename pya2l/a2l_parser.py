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

from collections import OrderedDict

import pya2l.classes as classes
from pya2l.a2l_lexer import Tokenizer
from pya2l.utils import slicer

VERSION = 'ASAM MCD-2MC V1.6'

MAX_IDENT           = 1024
MAX_PARTIAL_IDENT   = 128
MAX_STRING          = 255

IDENT_EXPR = r'^(?:[a-zA-Z_][a-zA-Z_0-9]*\.?)+(?:\[(?:\d+ | [a-zA-Z_][a-zA-Z_0-9]*)\])?'

BEGIN       = r'BEGIN'
END         = r'END'
KEYWORD     = r'KEYWORD'

STATE_NORMAL                = 1
STATE_COLLECT               = 2
STATE_A2ML                  = 3

from collections import namedtuple

Token = namedtuple('Token', 'lineNo tokenType lexem')

def a2lParser(fname):
    keywords = classes.KEYWORD_MAP.keys()
    fp = file(fname)

    tokenizer = Tokenizer(''.join(uncomment(fp)), keywords)

    state = STATE_NORMAL
    a2mlSyntax = []
    stack = []
    stack.append(classes.RootElement)
    end = False

    while tokenizer.tokenAvailable():
        lineno, (tokenType, lexem) = tokenizer.getToken()

        print "[%s]%s:%s" % (tokenType, lexem, lineno)

        if tokenType == BEGIN:
            lineno, (tokenType, lexem) = tokenizer.getToken()   # Move on.
            handler = classes.KEYWORD_MAP.get(lexem)
            stack.append(handler)
        elif tokenType == END:
            lineno, (tokenType, lexem) = tokenizer.getToken()   # Move on.
            stack.pop()
            continue
        elif tokenType == KEYWORD:
            handler = classes.KEYWORD_MAP.get(lexem)

        if stack:
            tos = stack[-1]
        if tokenType in (BEGIN, KEYWORD):
            fixedAttributes =  handler.fixedAttributes
            variableAttribute =  handler.variableAttribute

            numParameters = len(fixedAttributes)

            parameters = [tokenizer.getToken() for _ in range(numParameters)]
            attributeValues = [x[1][1] for x in parameters]
            inst = classes.instanceFactory(lexem.title(), **OrderedDict(zip(fixedAttributes, attributeValues)))
            if variableAttribute:
                attr = handler[variableAttribute]
                result = []
                while True:
                    lineno, (tokenType, lexem) = tokenizer.getToken()
                    print (tokenType, lexem)
                    if tokenType in (KEYWORD, END):
                        tokenizer.stepBack()
                        break
                    result.append(lexem)
                setattr(inst, attr[1], result)
                inst.attrs.append(attr[1])
            elif tokenType == KEYWORD and lexem in ('COMPU_TAB', 'COMPU_VTAB', 'COMPU_VTAB_RANGE'):
                #
                # COMPU_TAB / COMPU_VTAB / COMPU_VTAB_RANGE require special attention.
                #
                if lexem == 'COMPU_VTAB_RANGE':
                    sliceLength = 3
                    valueClass = classes.CompuTriplet
                    variablePart = [tokenizer.getToken() for _ in range(inst.NumberValueTriples * sliceLength)]
                else:
                    valueClass = classes.CompuPair
                    sliceLength = 2
                    variablePart = [tokenizer.getToken() for _ in range(inst.NumberValuePairs * sliceLength)]
                variablePartValues = [v[1][1] for v in variablePart]
                result = slicer(variablePartValues, sliceLength, valueClass)
                inst.attrs.append(attr[1])
                setattr(inst, attr[1], result)
            print inst


def uncomment(fp): # Nested comments are not supported!
    result = []
    multiLineComment = False

    for lineNo, line in enumerate(fp):
        # Bad style state-machine...
        if not multiLineComment:
            if '//' in line:
                cmtPos = line.index('//')
                line = line[ : cmtPos].strip()
                if line:
                    result.append(line)
            elif '/*' in line:
                cmtPos = line.index('/*')
                startLineNo = lineNo
                if not '*/' in line:
                    multiLineComment = True
                line = line[ : cmtPos].strip()
                if line:
                    result.append(line)
            else:
                if line:
                    result.append(line)
        else:
            if '*/' in line:
                cmtPos = line.index('*/')
                result.append(line[cmtPos + 2: ].strip())
                multiLineComment = False
    return result


