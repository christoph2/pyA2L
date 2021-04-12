#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2021 by Christoph Schueler <cpu12.gems.googlemail.com>

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
__author__ = "Christoph Schueler"
__version__ = "0.1.0"

import os
import importlib
import sys

import antlr4
from antlr4.error.ErrorListener import ErrorListener

from pya2l import model


class MyErrorListener(ErrorListener):
    """ """

    def __init__(self, line_map = None):
        super().__init__()
        self.line_map = line_map

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        if self.line_map:
            file_name, line = self.line_map.lookup(line)
            print(file_name + "::" +  "line " + str(line) + ":" + str(column) + " " + msg, file = sys.stderr)
        else:
            print("line " + str(line) + ":" + str(column) + " " + msg, file = sys.stderr)


class ParserWrapper:
    """"""

    def __init__(
        self, grammarName, startSymbol, listener=None, useDatabase=True, debug=False, line_map=None
    ):
        self.debug = debug
        self.grammarName = grammarName
        self.startSymbol = startSymbol
        self.line_map = line_map
        self.lexerModule, self.lexerClass = self._load("Lexer")
        self.parserModule, self.parserClass = self._load("Parser")
        self.listener = listener
        self.useDatabase = useDatabase

    def _load(self, name):
        className = "{0}{1}".format(self.grammarName, name)
        moduleName = "pya2l.{0}".format(className)
        module = importlib.import_module(moduleName)
        klass = getattr(module, className)
        return (
            module,
            klass,
        )

    def parse(self, input, trace=False):
        if self.useDatabase:
            self.db = model.A2LDatabase(self.fnbase, debug=self.debug)
        lexer = self.lexerClass(input)
        lexer.removeErrorListeners()
        lexer.addErrorListener(MyErrorListener(self.line_map))
        tokenStream = antlr4.CommonTokenStream(lexer)
        parser = self.parserClass(tokenStream)
        parser.removeErrorListeners()
        parser.addErrorListener(MyErrorListener(self.line_map))
        parser.setTrace(trace)
        meth = getattr(parser, self.startSymbol)
        self._syntaxErrors = parser._syntaxErrors
        tree = meth()
        if self.listener:
            if self.useDatabase:
                self.listener.db = self.db
            listener = self.listener()
            walker = antlr4.ParseTreeWalker()
            result = walker.walk(listener, tree)
        if self.useDatabase:
            self.db.session.commit()
            return self.db
        else:
            return listener

    def parseFromFile(self, filename, encoding="latin-1", trace=False):
        if filename == ":memory:":
            self.fnbase = ":memory:"
        else:
            pth, fname = os.path.split(filename)
            self.fnbase = os.path.splitext(fname)[0]
        return self.parse(ParserWrapper.stringStream(filename, encoding), trace)

    def parseFromString(self, buf, encoding="latin-1", trace=False, dbname=":memory:"):
        self.fnbase = dbname
        return self.parse(antlr4.InputStream(buf), trace)

    @staticmethod
    def stringStream(fname, encoding="latin-1"):
        return antlr4.InputStream(open(fname, encoding = encoding).read())

    def _getNumberOfSyntaxErrors(self):
        return self._syntaxErrors

    numberOfSyntaxErrors = property(_getNumberOfSyntaxErrors)
