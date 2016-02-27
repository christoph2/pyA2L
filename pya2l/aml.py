#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2015 by Christoph Schueler <cpu12.gems.googlemail.com>

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

   s. FLOSS-EXCEPTION.txt
"""
__author__  = 'Christoph Schueler'
__version__ = '0.1.0'

import codecs
import sys
import antlr4
import antlr4.tree
import pya2l.parserlib
import pya2l.amllib as amllib


def indent(level):
    print(" " * level,)

def dump(tree, level = 0):
    indent(level)
    if isinstance(tree, antlr4.TerminalNode):
        print(tree.symbol.text)
    else:
        print("({}".format(tree.value))
        level += 1
        for child in tree.children:
            dump(child, level)
        level -= 1
    indent(level)
    print(")")


class ParserWrapper(object):
    def __init__(self, grammarName, startSymbol):
        self.grammarName = grammarName
        self.startSymbol = startSymbol
        self.lexerModule, self.lexerClass = self._load('Lexer')
        self.parserModule, self.parserClass = self._load('Parser')

    def _load(self, name):
        moduleName = '%s%s' % (self.grammarName, name)
        className = '%s%s' % (self.grammarName, name)
        module = __import__(moduleName, globals(), locals())
        cls = getattr(module, className)
        return (module, cls, )

    def parse(self, input):
        lexer = self.lexerClass(input)
        tokenStream = antlr4.CommonTokenStream(lexer)
        parser = self.parserClass(tokenStream)
        meth = getattr(parser, self.startSymbol)
        tree = meth()
        listener = amllib.Listener()
        walker = antlr4.ParseTreeWalker()
        walker.walk(listener, tree)
        return tree

    def parseFromFile(self, fileName):
        return self.parse(ParserWrapper.stringStream(fileName))

    def parseFromString(self, buffer):
        return self.parse(antlr4.InputStream(buffer))

    @staticmethod
    def stringStream(fname):
        return antlr4.InputStream(codecs.open(fname, encoding = 'UTF-8').read())

