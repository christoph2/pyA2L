#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2022 by Christoph Schueler <cpu12.gems.googlemail.com>

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

from collections import namedtuple
import os
import importlib
import sys

import antlr4
from antlr4.error.ErrorListener import ErrorListener

from pya2l import model


ResultType = namedtuple("ResultType", "db listener_result")


class MyErrorListener(ErrorListener):
    """ """

    def __init__(self, line_map=None):
        super().__init__()
        self.line_map = line_map

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        if self.line_map:
            file_name, line = self.line_map.lookup(line)
            print(
                file_name + "::" + "line " + str(line) + ":" + str(column) + " " + msg,
                file=sys.stderr,
            )
        else:
            print("line " + str(line) + ":" + str(column) + " " + msg, file=sys.stderr)


class LineMap:
    """ """

    def lookup(self, line):
        return ":memory:", line


class PPR:
    """ """

    def __init__(self):
        self.line_map = LineMap()
        self.aml_section = []
        self.a2l_data = []
        self.if_data_sections = []


class ParserWrapper:
    """"""

    def __init__(
        self,
        grammarName,
        startSymbol,
        listener=None,
        debug=False,
        prepro_result=None,
    ):
        self.debug = debug
        self.grammarName = grammarName
        self.startSymbol = startSymbol
        if prepro_result is None:
            prepro_result = PPR()
        self.line_map = prepro_result.line_map
        self.prepro_result = prepro_result
        self.lexerModule, self.lexerClass = self._load("Lexer")
        self.parserModule, self.parserClass = self._load("Parser")
        self.listener = listener

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
        listener_result = None
        if self.listener:
            self.listener.db = self.db
            listener = self.listener(self.prepro_result)
            walker = antlr4.ParseTreeWalker()
            walker.walk(listener, tree)
            listener_result = listener.result()
        self.db.session.commit()
        return ResultType(self.db, listener_result)

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
        return antlr4.InputStream(open(fname, encoding=encoding).read())

    def _getNumberOfSyntaxErrors(self):
        return self._syntaxErrors

    numberOfSyntaxErrors = property(_getNumberOfSyntaxErrors)
