#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2019 by Christoph Schueler <cpu12.gems.googlemail.com>

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
import importlib
from pprint import pprint
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
        className = '{0}{1}'.format(self.grammarName, name)
        moduleName = 'pya2l.{0}'.format(className)
        module = importlib.import_module(moduleName)
        klass = getattr(module, className)
        return (module, klass, )

    def parse(self, input, trace = False):
        lexer = self.lexerClass(input)
        tokenStream = antlr4.CommonTokenStream(lexer)
        parser = self.parserClass(tokenStream)
        parser.setTrace(True if trace else False)
        meth = getattr(parser, self.startSymbol)
        self._syntaxErrors = parser._syntaxErrors
        tree = meth()
        listener = amllib.Listener()
        walker = antlr4.ParseTreeWalker()
        walker.walk(listener, tree)
        return tree

    def parseFromFile(self, fileName, encoding = "utf8", trace = False):
        return self.parse(ParserWrapper.stringStream(fileName, encoding), trace)

    def parseFromString(self, buffer, trace = False):
        return self.parse(antlr4.InputStream(buffer), trace)

    @staticmethod
    def stringStream(fname, encoding = "utf-8"):
        return antlr4.InputStream(codecs.open(fname, encoding = encoding).read())

    def _getNumberOfSyntaxErrors(self):
        return self._syntaxErrors

    numberOfSyntaxErrors = property(_getNumberOfSyntaxErrors)


class LexerWrapper(object):
    def __init__(self, grammarName, startSymbol):
        self.grammarName = grammarName
        self.startSymbol = startSymbol
        self.lexerModule, self.lexerClass = self._load('Lexer')

    def _load(self, name):
        className = '{0}'.format(self.grammarName, name)
        moduleName = 'pya2l.{0}'.format(className)
        print("LexerWraper", className, moduleName)
        module = importlib.import_module(moduleName)
        klass = getattr(module, className)
        return (module, klass, )

    def lex(self, input, trace = False):
        lexer = self.lexerClass(input)
        tokenStream = antlr4.CommonTokenStream(lexer)
        return tokenStream

    def lexFromFile(self, fileName, encoding = "utf8", trace = False):
        return self.lex(ParserWrapper.stringStream(fileName, encoding), trace)

    def lexFromString(self, buffer, trace = False):
        return self.lex(antlr4.InputStream(buffer), trace)

    @staticmethod
    def stringStream(fname, encoding = "utf-8"):
        return antlr4.InputStream(codecs.open(fname, encoding = encoding).read())

    def _getNumberOfSyntaxErrors(self):
        return self._syntaxErrors

    numberOfSyntaxErrors = property(_getNumberOfSyntaxErrors)
