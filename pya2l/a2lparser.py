#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__="""
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2017 by Christoph Schueler <github.com/Christoph2,
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
import enum
import itertools
import io
import re
from pprint import pprint

import antlr4

from pya2l import aml
from pya2l import classes
from pya2l.logger import Logger



AML = re.compile(r"""
/begin\s+A[23]ML
.*?
/end\s+A[23]ML
""", re.VERBOSE | re.DOTALL | re.MULTILINE)


class ValueType(enum.IntEnum):

    INT = 0
    FLOAT = 2
    STRING = 3
    IDENT = 4


class ValueObject(object):

    def __init__(self, value, typ):
        self._value = value
        self._type = typ

    @property
    def value(self):
        return self._value

    @property
    def type(self):
        return self._type

    def __str__(self):
        return "<ValueObject: '{}' [{}]>".format(self._value, str(self._type))

    __repr__ = __str__


class BlockObject(object):

    def __init__(self, keyword, children):
        self._keyword = keyword
        self._children = children

    @property
    def keyword(self):
        return self._keyword

    @property
    def children(self):
        return self._children


class A2LWalker(object):

    def __init__(self, tree):
        self.logger = Logger(self, 'A2LParser')
        self.tree = tree
        self.parser = tree.parser
        self.level = 0
        self.blockStack = []

    def run(self):
        a2lFile = self.tree
        for child in a2lFile.children:
            self.traverseBlock(child)

    def isPrimitiveType(self, value):
        return isinstance(value, (self.parser.ValueStringContext, self.parser.ValueIntContext,
            self.parser.ValueHexContext, self.parser.ValueFloatContext))

    def isPrimitiveTypeOrIdent(self, value):
        return isinstance(value, (self.parser.ValueStringContext, self.parser.ValueIntContext,
            self.parser.ValueHexContext, self.parser.ValueFloatContext, self.parser.ValueIdentContext))

    def getValue(self, ctx):
        CONTEXTS = {
            self.parser.ValueIdentContext: lambda x: ValueObject(x.IDENT().getText(), ValueType.IDENT),
            self.parser.ValueStringContext: lambda x: ValueObject(x.STRING().getText().strip('"'), ValueType.STRING),
            self.parser.ValueIntContext: lambda x: ValueObject(int(x.INT().getText()), ValueType.INT),
            self.parser.ValueHexContext: lambda x: ValueObject(int(x.HEX().getText(), 16), ValueType.INT),
            self.parser.ValueFloatContext: lambda x: ValueObject(float(x.FLOAT().getText()), ValueType.FLOAT),
        }
        fkt = CONTEXTS[type(ctx)]
        return fkt(ctx)

    def traverseBlock(self, tree, level = 0):
        if isinstance(tree, self.parser.VersionContext):
            return

        level += 1
        spaces = "  " * level
        startTag, endTag = tree.kw0.text, tree.kw1.text
        print("{}{}".format(spaces, startTag))

        if startTag == 'IF_DATA':
            return

        klass = classes.KEYWORD_MAP.get(startTag)

        # Untersuchen: AXIS_DESCR

        fixedParameters =  klass.fixedAttributes
        variableParameters =  klass.variableAttribute
        optionalParameters = klass.children
        numParameters = len(fixedParameters)

        children = iter(tree.children[2 : -2])

        # TODO: COMPU_VTAB

        if startTag == 'ANNOTATION':
            pass

        args = []
        optArgs = []
        varArgs = []
        fetchAttrs = True if numParameters else False
        argCount = 0
        for child in children:
            if fetchAttrs:
                if self.isPrimitiveTypeOrIdent(child):
                    #print(self.getValue(child))
                    args.append((fixedParameters[argCount], self.getValue(child)))
                else:
                    print("att error")
                argCount += 1
                if argCount >= numParameters:
                    fetchAttrs = False
            else:
                if isinstance(child, self.parser.ValueBlockContext):
                    self.traverseBlock(child.children[0], level)
                else:
                    param = child.getText()
                    if param in optionalParameters:
                        optArgs.append((param, self.fetchOptionallArgument(param, children)))
                    else:
                        if variableParameters:
                            vparams = [self.getValue(child)]
                            res = self.fetchVariableParameters(param, vparams[0].type, children)
                            vparams.extend(res)
                            #print("   VParams: {}".format(vparams))
                        else:
                            print("      *", param)
        inst = classes.instanceFactory(startTag, **OrderedDict(args))
        return inst


    def fetchOptionallArgument(self, name, iter):
        klass = classes.KEYWORD_MAP.get(name)
        parameters = klass.fixedAttributes
        args = []
        for idx in range(len(klass.fixedAttributes)):
            child = next(iter)
            if self.isPrimitiveTypeOrIdent(child):
                value = self.getValue(child)
                args.append(value)
            else:
                print("error")
        inst = classes.instanceFactory(name, **OrderedDict(zip(parameters, args)))
        print(inst)
        return inst

    def fetchVariableParameters(self, name, type_, iter):
        result  = [self.getValue(x) for x in list(iter)]
        return result


def parse(filename):

    pa = aml.ParserWrapper('a2l', 'a2lFile')

    data = io.open(filename, encoding = "latin1").read()

    match = AML.search(data)
    if match:
        header = data[0 : match.start()]
        amlS = data[match.start() : match.end()]
        lineCount = amlS.count('\n')
        footer = data[match.end() : -1]
        data = header + '\n' * lineCount + footer

    tree = pa.parseFromString(data)
    print("Finished ANTLR parsing.")

    walker = A2LWalker(tree)
    walker.run()
    print("Finished walking.")




