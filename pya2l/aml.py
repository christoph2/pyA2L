#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2017 by Christoph Schueler <cpu12.gems.googlemail.com>

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
from pprint import pprint
import sys

import six
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
        className = '%s%s' % (self.grammarName, name)
        if six.PY2:
            moduleName = '%s%s' % (self.grammarName, name)
        else:
            moduleName = 'pya2l.%s%s' % (self.grammarName, name)
        module = __import__(moduleName, globals(), locals())
        if six.PY2:
            cls = getattr(module, className)
        else:
            mod = getattr(module, className)
            cls = getattr(mod, className)
        #print(module, className, cls)
        return (module, cls, )

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

        pprint(tree.toStringTree())
        """
        JavaLexer lexer = new JavaLexer(input);
        CommonTokenStream tokens = new CommonTokenStream(lexer);
        JavaParser parser = new JavaParser(tokens);

        ParseTree tree = parser.compilationUnit(); // parse
        ParseTreeWalker walker = new ParseTreeWalker(); // create standard walker
        ExtractInterfaceListener extractor = new ExtractInterfaceListener(parser);
        walker.walk(extractor, tree); // initiate walk of tree with listener
        """


        return tree

    def parseFromFile(self, fileName, trace = False):
        return self.parse(ParserWrapper.stringStream(fileName), trace)

    def parseFromString(self, buffer, trace = False):
        return self.parse(antlr4.InputStream(buffer), trace)

    @staticmethod
    def stringStream(fname):
        return antlr4.InputStream(codecs.open(fname, encoding = 'UTF-8').read())

    def _getNumberOfSyntaxErrors(self):
        return self._syntaxErrors

    numberOfSyntaxErrors = property(_getNumberOfSyntaxErrors)

