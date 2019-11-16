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

import six
import antlr4
import antlr4.tree

from pydbc.logger import Logger


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


class BaseListener(antlr4.ParseTreeListener):
    """
    """

    value = []
    logger = Logger(__name__)

    def getList(self, attr):
        return [x.value for x in attr] if attr else []

    def getTerminal(self, attr):
        return attr().getText() if attr() else ''

    def exitIntegerValue(self, ctx):
        if ctx.i:
            ctx.value = int(ctx.i.text, 10)
        elif ctx.h:
            ctx.value = int(ctx.h.text, 16)
        else:
            ctx.value = None

    def exitFloatValue(self, ctx):
        if ctx.f:
            ctx.value = float(ctx.f.text)
        elif ctx.i:
            ctx.value = float(ctx.i.text)
        else:
            ctx.value = None

    def exitNumber(self, ctx):
        if ctx.i:
            value = ctx.i.value
        elif ctx.f:
            value = ctx.f.value
        else:
            value = None
        ctx.value = value
        #print("NUM", ctx.value)

    def exitStringValue(self, ctx):
        ctx.value = ctx.s.text.strip('"') if ctx.s else None
        #print("STR", ctx.value)

    def exitIdentifierValue(self, ctx):
        ctx.value = ctx.i.text if ctx.i else None
        #print("ID", ctx.value)

    def _formatMessage(self, msg, location):
        return "[{0}:{1}] {2}".format(location.start.line, location.start.column + 1, msg)

    def _log(self, method, msg, location = None):
        if location:
            method(self._formatMessage(msg, location))
        else:
            method(msg)

    def info(self, msg, location = None):
        self._log(self.info.warn, msg, location)

    def warn(self, msg, location = None):
        self._log(self.logger.warn, msg, location)

    def error(self, msg, location = None):
        self._log(self.logger.warn, msg, location)

    def debug(self, msg, location = None):
        self._log(self.logger.warn, msg, location)


class ParserWrapper(object):
    """
    """
    def __init__(self, grammarName, startSymbol, listener = None):
        self.grammarName = grammarName
        self.startSymbol = startSymbol
        self.lexerModule, self.lexerClass = self._load('Lexer')
        self.parserModule, self.parserClass = self._load('Parser')
        self.listener = listener

    def _load(self, name):
        className = '{0}{1}'.format(self.grammarName, name)
        moduleName = 'pya2l.py{0}.{1}'.format(2 if six.PY2 else 3, className)
        module = importlib.import_module(moduleName)
        klass = getattr(module, className)
        return (module, klass, )

    def parse(self, input, trace = False):
        lexer = self.lexerClass(input)
        tokenStream = antlr4.CommonTokenStream(lexer)
        parser = self.parserClass(tokenStream)
        parser.setTrace(trace)
        meth = getattr(parser, self.startSymbol)
        self._syntaxErrors = parser._syntaxErrors
        tree = meth()
        if self.listener:
            listener = self.listener()
            walker = antlr4.ParseTreeWalker()
            walker.walk(listener, tree)
            return listener.value
        else:
            return tree

    def parseFromFile(self, fileName, encoding = 'latin-1', trace = False):
        return self.parse(ParserWrapper.stringStream(fileName, encoding), trace)

    def parseFromString(self, buf, encoding = 'latin-1', trace = False):
        return self.parse(antlr4.InputStream(buf), trace)

    @staticmethod
    def stringStream(fname, encoding = 'latin-1'):
        return antlr4.InputStream(codecs.open(fname, encoding = encoding).read())

    def _getNumberOfSyntaxErrors(self):
        return self._syntaxErrors

    numberOfSyntaxErrors = property(_getNumberOfSyntaxErrors)


class A2LListener(BaseListener):


    def exitAlignmentByte(self, ctx):
        pass


    def exitAlignmentFloat32Ieee(self, ctx):
        pass


    def exitAlignmentFloat64Ieee(self, ctx):
        pass


    def exitAlignmentInt64(self, ctx):
        pass


    def exitAlignmentLong(self, ctx):
        pass


    def exitAlignmentWord(self, ctx):
        pass


    def exitAnnotation(self, ctx):
        pass


    def exitAnnotationLabel(self, ctx):
        pass


    def exitAnnotationOrigin(self, ctx):
        pass


    def exitAnnotationText(self, ctx):
        pass


    def exitBitMask(self, ctx):
        pass


    def exitByteOrder(self, ctx):
        pass


    def exitCalibrationAccess(self, ctx):
        pass


    def exitDefaultValue(self, ctx):
        pass


    def exitDeposit(self, ctx):
        pass


    def exitDiscrete(self, ctx):
        pass


    def exitDisplayIdentifier(self, ctx):
        pass


    def exitEcuAddressExtension(self, ctx):
        pass


    def exitExtendedLimits(self, ctx):
        pass


    def exitFormat(self, ctx):
        pass


    def exitFunctionList(self, ctx):
        pass


    def exitGuardRails(self, ctx):
        pass


    def exitIfData(self, ctx):
        pass


    def exitMatrixDim(self, ctx):
        pass


    def exitMaxRefresh(self, ctx):
        pass


    def exitMonotony(self, ctx):
        pass


    def exitPhysUnit(self, ctx):
        pass


    def exitReadOnly(self, ctx):
        pass


    def exitRefCharacteristic(self, ctx):
        pass


    def exitRefMemorySegment(self, ctx):
        pass


    def exitRefUnit(self, ctx):
        pass


    def exitStepSize(self, ctx):
        pass


    def exitSymbolLink(self, ctx):
        pass


    def exitVersion(self, ctx):
        pass


    def exitAsap2Version(self, ctx):
        pass


    def exitA2mlVersion(self, ctx):
        pass


    def exitProject(self, ctx):
        pass


    def exitHeader(self, ctx):
        pass


    def exitProjectNo(self, ctx):
        pass


    def exitModule(self, ctx):
        pass


    def exitA2ml(self, ctx):
        pass


    def exitAxisPts(self, ctx):
        pass


    def exitCharacteristic(self, ctx):
        pass


    def exitAxisDescr(self, ctx):
        pass


    def exitAxisPtsRef(self, ctx):
        pass


    def exitCurveAxisRef(self, ctx):
        pass


    def exitFixAxisPar(self, ctx):
        pass


    def exitFixAxisParDist(self, ctx):
        pass


    def exitFixAxisParList(self, ctx):
        pass


    def exitMaxGrad(self, ctx):
        pass


    def exitComparisonQuantity(self, ctx):
        pass


    def exitDependentCharacteristic(self, ctx):
        pass


    def exitMapList(self, ctx):
        pass


    def exitNumber(self, ctx):
        pass


    def exitVirtualCharacteristic(self, ctx):
        pass


    def exitCompuMethod(self, ctx):
        pass


    def exitCoeffs(self, ctx):
        pass


    def exitCoeffsLinear(self, ctx):
        pass


    def exitCompuTabRef(self, ctx):
        pass


    def exitFormula(self, ctx):
        pass


    def exitFormulaInv(self, ctx):
        pass


    def exitStatusStringRef(self, ctx):
        pass


    def exitCompuTab(self, ctx):
        pass


    def exitDefaultValueNumeric(self, ctx):
        pass


    def exitCompuVtab(self, ctx):
        pass


    def exitCompuVtabRange(self, ctx):
        pass


    def exitFrame(self, ctx):
        pass


    def exitFrameMeasurement(self, ctx):
        pass


    def exitFunction(self, ctx):
        pass


    def exitDefCharacteristic(self, ctx):
        pass


    def exitFunctionVersion(self, ctx):
        pass


    def exitInMeasurement(self, ctx):
        pass


    def exitLocMeasurement(self, ctx):
        pass


    def exitOutMeasurement(self, ctx):
        pass


    def exitSubFunction(self, ctx):
        pass


    def exitGroup(self, ctx):
        pass


    def exitRefMeasurement(self, ctx):
        pass


    def exitRoot(self, ctx):
        pass


    def exitSubGroup(self, ctx):
        pass


    def exitMeasurement(self, ctx):
        pass


    def exitArraySize(self, ctx):
        pass


    def exitBitOperation(self, ctx):
        pass


    def exitLeftShift(self, ctx):
        pass


    def exitRightShift(self, ctx):
        pass


    def exitSignExtend(self, ctx):
        pass


    def exitEcuAddress(self, ctx):
        pass


    def exitErrorMask(self, ctx):
        pass


    def exitLayout(self, ctx):
        pass


    def exitReadWrite(self, ctx):
        pass


    def exitVirtual(self, ctx):
        pass


    def exitModCommon(self, ctx):
        pass


    def exitDataSize(self, ctx):
        pass


    def exitSRecLayout(self, ctx):
        pass


    def exitModPar(self, ctx):
        pass


    def exitAddrEpk(self, ctx):
        pass


    def exitCalibrationMethod(self, ctx):
        pass


    def exitCalibrationHandle(self, ctx):
        pass


    def exitCalibrationHandleText(self, ctx):
        pass


    def exitCpuType(self, ctx):
        pass


    def exitCustomer(self, ctx):
        pass


    def exitCustomerNo(self, ctx):
        pass


    def exitEcu(self, ctx):
        pass


    def exitEcuCalibrationOffset(self, ctx):
        pass


    def exitEpk(self, ctx):
        pass


    def exitMemoryLayout(self, ctx):
        pass


    def exitMemorySegment(self, ctx):
        pass


    def exitNoOfInterfaces(self, ctx):
        pass


    def exitPhoneNo(self, ctx):
        pass


    def exitSupplier(self, ctx):
        pass


    def exitSystemConstant(self, ctx):
        pass


    def exitUser(self, ctx):
        pass


    def exitRecordLayout(self, ctx):
        pass


    def exitAxisPtsX(self, ctx):
        pass


    def exitAxisPtsY(self, ctx):
        pass


    def exitAxisPtsZ(self, ctx):
        pass


    def exitAxisPts4(self, ctx):
        pass


    def exitAxisPts5(self, ctx):
        pass


    def exitAxisRescaleX(self, ctx):
        pass


    def exitAxisRescaleY(self, ctx):
        pass


    def exitAxisRescaleZ(self, ctx):
        pass


    def exitAxisRescale4(self, ctx):
        pass


    def exitAxisRescale5(self, ctx):
        pass


    def exitDistOpX(self, ctx):
        pass


    def exitDistOpY(self, ctx):
        pass


    def exitDistOpZ(self, ctx):
        pass


    def exitDistOp4(self, ctx):
        pass


    def exitDistOp5(self, ctx):
        pass


    def exitFixNoAxisPtsX(self, ctx):
        pass


    def exitFixNoAxisPtsY(self, ctx):
        pass


    def exitFixNoAxisPtsZ(self, ctx):
        pass


    def exitFixNoAxisPts4(self, ctx):
        pass


    def exitFixNoAxisPts5(self, ctx):
        pass


    def exitFncValues(self, ctx):
        pass


    def exitIdentification(self, ctx):
        pass


    def exitNoAxisPtsX(self, ctx):
        pass


    def exitNoAxisPtsY(self, ctx):
        pass


    def exitNoAxisPtsZ(self, ctx):
        pass


    def exitNoAxisPts4(self, ctx):
        pass


    def exitNoAxisPts5(self, ctx):
        pass


    def exitStaticRecordLayout(self, ctx):
        pass


    def exitNoRescaleX(self, ctx):
        pass


    def exitNoRescaleY(self, ctx):
        pass


    def exitNoRescaleZ(self, ctx):
        pass


    def exitNoRescale4(self, ctx):
        pass


    def exitNoRescale5(self, ctx):
        pass


    def exitOffsetX(self, ctx):
        pass


    def exitOffsetY(self, ctx):
        pass


    def exitOffsetZ(self, ctx):
        pass


    def exitOffset4(self, ctx):
        pass


    def exitOffset5(self, ctx):
        pass


    def exitReserved(self, ctx):
        pass


    def exitRipAddrW(self, ctx):
        pass


    def exitRipAddrX(self, ctx):
        pass


    def exitRipAddrY(self, ctx):
        pass


    def exitRipAddrZ(self, ctx):
        pass


    def exitRipAddr4(self, ctx):
        pass


    def exitRipAddr5(self, ctx):
        pass


    def exitShiftOpX(self, ctx):
        pass


    def exitShiftOpY(self, ctx):
        pass


    def exitShiftOpZ(self, ctx):
        pass


    def exitShiftOp4(self, ctx):
        pass


    def exitShiftOp5(self, ctx):
        pass


    def exitSrcAddrX(self, ctx):
        pass


    def exitSrcAddrY(self, ctx):
        pass


    def exitSrcAddrZ(self, ctx):
        pass


    def exitSrcAddr4(self, ctx):
        pass


    def exitSrcAddr5(self, ctx):
        pass


    def exitUnit(self, ctx):
        pass


    def exitSiExponents(self, ctx):
        pass


    def exitUnitConversion(self, ctx):
        pass


    def exitUserRights(self, ctx):
        pass


    def exitRefGroup(self, ctx):
        pass


    def exitVariantCoding(self, ctx):
        pass


    def exitVarCharacteristic(self, ctx):
        pass


    def exitVarAddress(self, ctx):
        pass


    def exitVarCriterion(self, ctx):
        pass


    def exitVarMeasurement(self, ctx):
        pass


    def exitVarSelectionCharacteristic(self, ctx):
        pass


    def exitVarForbiddenComb(self, ctx):
        pass


    def exitVarNaming(self, ctx):
        pass


    def exitVarSeparator(self, ctx):
        pass


