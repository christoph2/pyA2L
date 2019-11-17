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
from decimal import Decimal as D
import importlib
from pprint import pprint
import sys

import six
import antlr4
from antlr4.BufferedTokenStream import BufferedTokenStream

from pya2l.logger import Logger
import pya2l.model as model


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
    #logger = Logger(__name__)

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
            ctx.value = D(ctx.f.text)
        elif ctx.i:
            ctx.value = D(ctx.i.text)
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
#        tokenStream = BufferedTokenStream(lexer)
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
        alignmentBorder = ctx.alignmentBorder.value
        ctx.value = alignmentBorder

    def exitAlignmentFloat32Ieee(self, ctx):
        alignmentBorder = ctx.alignmentBorder.value
        ctx.value = alignmentBorder

    def exitAlignmentFloat64Ieee(self, ctx):
        alignmentBorder = ctx.alignmentBorder.value
        ctx.value = alignmentBorder

    def exitAlignmentInt64(self, ctx):
        alignmentBorder = ctx.alignmentBorder.value
        ctx.value = alignmentBorder

    def exitAlignmentLong(self, ctx):
        alignmentBorder = ctx.alignmentBorder.value
        ctx.value = alignmentBorder

    def exitAlignmentWord(self, ctx):
        alignmentBorder = ctx.alignmentBorder.value
        ctx.value = alignmentBorder

    def exitAnnotation(self, ctx):
        v_annotationLabel = self.getList(ctx.v_annotationLabel)
        v_annotationOrigin = self.getList(ctx.v_annotationOrigin)
        v_annotationText = self.getList(ctx.v_annotationText)
        print("ANNO", v_annotationLabel, v_annotationOrigin, v_annotationText)
        ctx.value = (v_annotationLabel, v_annotationOrigin, v_annotationText)

    def exitAnnotationLabel(self, ctx):
        label = ctx.label.value
        ctx.value = label

    def exitAnnotationOrigin(self, ctx):
        origin = ctx.origin.value
        ctx.value = origin

    def exitAnnotationText(self, ctx):
        text = self.getList(ctx.text)
        ctx.value = text

    def exitBitMask(self, ctx):
        mask = ctx.mask.value
        ctx.value = mask

    def exitByteOrder(self, ctx):
        byteOrder_ = ctx.byteOrder_.value
        ctx.value = byteOrder_

    def exitCalibrationAccess(self, ctx):
        type_ = ctx.type_.text
        ctx.value = type_

    def exitDefaultValue(self, ctx):
        display_String = ctx.display_String.value
        ctx.value = display_String

    def exitDeposit(self, ctx):
        mode_ = ctx.mode_.text
        ctx.value = mode_

    def exitDiscrete(self, ctx):
        ctx.value = True

    def exitDisplayIdentifier(self, ctx):
        display_Name = ctx.display_Name.value
        ctx.value = display_Name

    def exitEcuAddressExtension(self, ctx):
        extension = ctx.extension.value
        ctx.value = extension

    def exitExtendedLimits(self, ctx):
        lowerLimit = ctx.lowerLimit.value
        upperLimit = ctx.upperLimit.value
        print("E-LIMITS:", (lowerLimit, upperLimit))
        ctx.value = (lowerLimit, upperLimit)

    def exitFormat_(self, ctx):
        formatString = ctx.formatString.value
        print("FORMAT", formatString)
        ctx.value = formatString

    def exitFunctionList(self, ctx):
        name = self.getList(ctx.name)
        print("FL:", name)

    def exitGuardRails(self, ctx):
        ctx.value = True

    def exitIfData(self, ctx):
        ctx.value = ""

    def exitMatrixDim(self, ctx):
        xDim = ctx.xDim.value
        yDim = ctx.yDim.value
        zDim = ctx.zDim.value
        print("M-DIM", (xDim, yDim, zDim))
        ctx.value = (xDim, yDim, zDim)

    def exitMaxRefresh(self, ctx):
        scalingUnit = ctx.scalingUnit.value
        rate  = ctx.rate.value
        ctx.value = (scalingUnit, rate)

    def exitMonotony(self, ctx):
        monotony_ = ctx.monotony_.text
        ctx.value = monotony_
        print("MONO", monotony_)

    def exitPhysUnit(self, ctx):
        unit_ = ctx.unit_.value
        print("UNIT", unit_)
        ctx.value = unit_

    def exitReadOnly(self, ctx):
        ctx.value = True

    def exitRefCharacteristic(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = identifier

    def exitRefMemorySegment(self, ctx):
        name = ctx.name.value
        ctx.value = name

    def exitRefUnit(self, ctx):
        unit_ = ctx.unit_.value
        ctx.value = unit_

    def exitStepSize(self, ctx):
        stepSize_ = ctx.stepSize_.value
        ctx.value = stepSize_

    def exitSymbolLink(self, ctx):
        symbolName = ctx.symbolName.value
        offset = ctx.offset.value
        print("SYM-LNK:", (symbolName, offset))
        ctx.value = (symbolName, offset)

    def exitVersion(self, ctx):
        versionIdentifier = ctx.versionIdentifier.value
        ctx.value = versionIdentifier

    def exitAsap2Version(self, ctx):
        versionNo = ctx.versionNo.value
        upgradeNo = ctx.upgradeNo.value
        ctx.value = (versionNo, upgradeNo)

    def exitA2mlVersion(self, ctx):
        versionNo = ctx.versionNo.value
        upgradeNo = ctx.upgradeNo.value
        ctx.value = (versionNo, upgradeNo)

    def exitProject(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        #v_header = self.getList(ctx.v_header)
        #v_module = self.getList(ctx.v_module)

    def exitHeader(self, ctx):
        comment = ctx.comment.value
        v_projectNo = self.getList(ctx.v_projectNo)
        v_version = self.getList(ctx.v_version)
        print("HEADER", comment, v_projectNo, v_version)

    def exitProjectNo(self, ctx):
        projectNumber = ctx.projectNumber.value
        ctx.value = projectNumber

    def exitModule(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value

        v_a2ml = self.getList(ctx.v_a2ml)
        v_axisPts = self.getList(ctx.v_axisPts)
        v_characteristic = self.getList(ctx.v_characteristic)
        v_compuMethod = self.getList(ctx.v_compuMethod)
        v_compuTab = self.getList(ctx.v_compuTab)
        v_compuVtab = self.getList(ctx.v_compuVtab)
        v_compuVtabRange = self.getList(ctx.v_compuVtabRange)
        v_frame = self.getList(ctx.v_frame)
        v_function = self.getList(ctx.v_function)
        v_group = self.getList(ctx.v_group)
        v_ifData = self.getList(ctx.v_ifData)
        v_measurement = self.getList(ctx.v_measurement)
        v_modCommon = self.getList(ctx.v_modCommon)
        v_modPar = self.getList(ctx.v_modPar)
        v_recordLayout = self.getList(ctx.v_recordLayout)
        v_unit = self.getList(ctx.v_unit)
        v_userRights = self.getList(ctx.v_userRights)
        v_variantCoding = self.getList(ctx.v_variantCoding)

    def exitA2ml(self, ctx):
        ctx.value = ""

    def exitAxisPts(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        address = ctx.address.value
        inputQuantity = ctx.inputQuantity.value
        deposit_ = ctx.deposit_.value
        maxDiff = ctx.maxDiff.value
        conversion = ctx.conversion.value
        maxAxisPoints = ctx.maxAxisPoints.value
        lowerLimit = ctx.lowerLimit.value
        upperLimit = ctx.upperLimit.value
        v_annotation = self.getList(ctx.v_annotation)
        v_byteOrder = self.getList(ctx.v_byteOrder)
        v_calibrationAccess = self.getList(ctx.v_calibrationAccess)
        v_deposit = self.getList(ctx.v_deposit)
        v_displayIdentifier = self.getList(ctx.v_displayIdentifier)
        v_ecuAddressExtension = self.getList(ctx.v_ecuAddressExtension)
        v_extendedLimits = self.getList(ctx.v_extendedLimits)
        v_format_ = self.getList(ctx.v_format_)
        v_functionList = self.getList(ctx.v_functionList)
        v_guardRails = self.getList(ctx.v_guardRails)
        v_ifData = self.getList(ctx.v_ifData)
        v_monotony = self.getList(ctx.v_monotony)
        v_physUnit = self.getList(ctx.v_physUnit)
        v_readOnly = self.getList(ctx.v_readOnly)
        v_refMemorySegment = self.getList(ctx.v_refMemorySegment)
        v_stepSize = self.getList(ctx.v_stepSize)
        v_symbolLink = self.getList(ctx.v_symbolLink)

    def exitCharacteristic(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        type_ = ctx.type_.text
        address = ctx.address.value
        deposit_ = ctx.deposit_.value
        maxDiff = ctx.maxDiff.value
        conversion = ctx.conversion.value
        lowerLimit = ctx.lowerLimit.value
        upperLimit = ctx.upperLimit.value

        v_annotation = self.getList(ctx.v_annotation)
        v_axisDescr = self.getList(ctx.v_axisDescr)
        v_bitMask = self.getList(ctx.v_bitMask)
        v_byteOrder = self.getList(ctx.v_byteOrder)
        v_calibrationAccess = self.getList(ctx.v_calibrationAccess)
        v_comparisonQuantity = self.getList(ctx.v_comparisonQuantity)
        v_dependentCharacteristic = self.getList(ctx.v_dependentCharacteristic)
        v_discrete = self.getList(ctx.v_discrete)
        v_displayIdentifier = self.getList(ctx.v_displayIdentifier)
        v_ecuAddressExtension = self.getList(ctx.v_ecuAddressExtension)
        v_extendedLimits = self.getList(ctx.v_extendedLimits)
        v_format_ = self.getList(ctx.v_format_)
        v_functionList = self.getList(ctx.v_functionList)
        v_guardRails = self.getList(ctx.v_guardRails)
        v_ifData = self.getList(ctx.v_ifData)
        v_mapList = self.getList(ctx.v_mapList)
        v_matrixDim = self.getList(ctx.v_matrixDim)
        v_maxRefresh = self.getList(ctx.v_maxRefresh)
        v_number = self.getList(ctx.v_number)
        v_physUnit = self.getList(ctx.v_physUnit)
        v_readOnly = self.getList(ctx.v_readOnly)
        v_refMemorySegment = self.getList(ctx.v_refMemorySegment)
        v_stepSize = self.getList(ctx.v_stepSize)
        v_symbolLink = self.getList(ctx.v_symbolLink)
        v_virtualCharacteristic = self.getList(ctx.v_virtualCharacteristic)

    def exitAxisDescr(self, ctx):
        attribute = ctx.attribute.text
        inputQuantity = ctx.inputQuantity.value
        conversion = ctx.conversion.value
        maxAxisPoints = ctx.maxAxisPoints.value
        lowerLimit = ctx.lowerLimit.value
        upperLimit = ctx.upperLimit.value

        v_annotation = self.getList(ctx.v_annotation)
        v_axisPtsRef = self.getList(ctx.v_axisPtsRef)
        v_byteOrder = self.getList(ctx.v_byteOrder)
        v_curveAxisRef = self.getList(ctx.v_curveAxisRef)
        v_deposit = self.getList(ctx.v_deposit)
        v_extendedLimits = self.getList(ctx.v_extendedLimits)
        v_fixAxisPar = self.getList(ctx.v_fixAxisPar)
        v_fixAxisParDist = self.getList(ctx.v_fixAxisParDist)
        v_fixAxisParList = self.getList(ctx.v_fixAxisParList)
        v_format_ = self.getList(ctx.v_format_)
        v_maxGrad = self.getList(ctx.v_maxGrad)
        v_monotony = self.getList(ctx.v_monotony)
        v_physUnit = self.getList(ctx.v_physUnit)
        v_readOnly = self.getList(ctx.v_readOnly)
        v_stepSize = self.getList(ctx.v_stepSize)

    def exitAxisPtsRef(self, ctx):
        axisPoints = ctx.axisPoints.value
        ctx.value = axisPoints

    def exitCurveAxisRef(self, ctx):
        curveAxis = ctx.curveAxis.value

    def exitFixAxisPar(self, ctx):
        offset = ctx.offset.value
        shift = ctx.shift.value
        numberapo = ctx.numberapo.value
        ctx.value = (offset, shift, numberapo)

    def exitFixAxisParDist(self, ctx):
        offset = ctx.offset.value
        distance = ctx.distance.value
        numberapo = ctx.numberapo.value
        ctx.value = (offset, distance, numberapo)

    def exitFixAxisParList(self, ctx):
        axisPts_Value = self.getList(ctx.axisPts_Value)
        ctx.value = axisPts_Value

    def exitMaxGrad(self, ctx):
        maxGradient = ctx.maxGradient.value
        ctx.value = maxGradient

    def exitComparisonQuantity(self, ctx):
        name = ctx.name.value
        ctx.value = name

    def exitDependentCharacteristic(self, ctx):
        formula_ = ctx.formula_.value
        characteristic_ = self.getList(ctx.characteristic_)
        ctx.value = (formula_, characteristic_)

    def exitMapList(self, ctx):
        name = self.getList(ctx.name)
        ctx.value = name

    def exitNumber(self, ctx):
        number_ = ctx.number_.value
        ctx.value = number_

    def exitVirtualCharacteristic(self, ctx):
        formula_ = ctx.formula_.value
        characteristic_ = self.getList(ctx.characteristic_)
        ctx.value = (formula_, characteristic_)

    def exitCompuMethod(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        conversionType = ctx.conversionType.text
        format__ = ctx.format__.value
        unit_ = ctx.unit_.value
        v_coeffs = self.getList(ctx.v_coeffs)
        v_coeffsLinear = self.getList(ctx.v_coeffsLinear)
        v_compuTabRef = self.getList(ctx.v_compuTabRef)
        v_formula = self.getList(ctx.v_formula)
        v_refUnit = self.getList(ctx.v_refUnit)
        v_statusStringRef = self.getList(ctx.v_statusStringRef)
        print("COMPU_M:", name, longIdentifier, conversionType, format__, unit_)

    def exitCoeffs(self, ctx):
        a = ctx.a.value
        b = ctx.b.value
        c = ctx.c.value
        d = ctx.d.value
        e = ctx.e.value
        f = ctx.f.value
        ctx.value = (a, b, c, d, e, f)

    def exitCoeffsLinear(self, ctx):
        a = ctx.a.value
        b = ctx.b.value
        ctx.value = (a, b)

    def exitCompuTabRef(self, ctx):
        conversionTable = ctx.conversionTable.value
        ctx.value = conversionTable

    def exitFormula(self, ctx):
        f_x = ctx.f_x.value
        v_formulaInv = self.getList(ctx.v_formulaInv)
        ctx.value = (f_x, v_formulaInv)

    def exitFormulaInv(self, ctx):
        g_x = ctx.g_x.value
        ctx.value = g_x

    def exitStatusStringRef(self, ctx):
        conversionTable = ctx.conversionTable.value
        ctx.value = conversionTable

    def exitCompuTab(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        conversionType = ctx.conversionType.text
        numberValuePairs = ctx.numberValuePairs.value    # TODO: check length of following pairs.
        inVal = self.getList(ctx.inVal)
        outVal = self.getList(ctx.outVal)
        pairs = zip(inVal, outVal)

        print("C-TAB-pairs", list(pairs))

        v_defaultValue = self.getList(ctx.v_defaultValue)
        v_defaultValueNumeric = self.getList(ctx.v_defaultValueNumeric)

    def exitDefaultValueNumeric(self, ctx):
        display_Value = ctx.display_Value.value
        ctx.value = display_Value

    def exitCompuVtab(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        conversionType = 'TAB_VERB'    # Fixed by Std.
        numberValuePairs = ctx.numberValuePairs.value       # TODO: check length of following pairs.
        inVal = self.getList(ctx.inVal)
        outVal = self.getList(ctx.outVal)
        pairs = zip(inVal, outVal)
        print("C-V-TAB-pairs", list(pairs))
        v_defaultValue = self.getList(ctx.v_defaultValue)

    def exitCompuVtabRange(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        numberValueTriples = ctx.numberValueTriples.value # TODO: check length of following triples
        inValMin = self.getList(ctx.inValMin)
        inValMax = self.getList(ctx.inValMax)
        outVal = self.getList(ctx.outVal)
        triples = zip(inValMin, inValMax, outVal)
        print("C-V-TAB-RANGE-triples", list(triples))
        v_defaultValue = self.getList(ctx.v_defaultValue)

    def exitFrame(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        scalingUnit = ctx.scalingUnit.value
        rate = ctx.rate.value
        v_frameMeasurement = self.getList(ctx.v_frameMeasurement)
        v_ifData = self.getList(ctx.v_ifData)

    def exitFrameMeasurement(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = identifier

    def exitFunction(self, ctx):
        pass

    def exitDefCharacteristic(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = identifier

    def exitFunctionVersion(self, ctx):
        versionIdentifier = ctx.versionIdentifier.value
        ctx.value = versionIdentifier

    def exitInMeasurement(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = identifier

    def exitLocMeasurement(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = identifier

    def exitOutMeasurement(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = identifier

    def exitSubFunction(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = identifier

    def exitGroup(self, ctx):
        groupName = ctx.groupName.value
        groupLongIdentifier = ctx.groupLongIdentifier.value
        v_annotation = self.getList(ctx.v_annotation)
        v_functionList = self.getList(ctx.v_functionList)
        v_ifData = self.getList(ctx.v_ifData)
        v_refCharacteristic = self.getList(ctx.v_refCharacteristic)
        v_refMeasurement = self.getList(ctx.v_refMeasurement)
        v_root = self.getList(ctx.v_root)
        v_subGroup = self.getList(ctx.v_subGroup)

    def exitRefMeasurement(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = identifier

    def exitRoot(self, ctx):
        ctx.value = True

    def exitSubGroup(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = identifier

    def exitMeasurement(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        datatype = ctx.datatype.value
        conversion = ctx.conversion.value
        resolution = ctx.resolution.value
        accuracy = ctx.accuracy.value
        lowerLimit = ctx.lowerLimit.value
        upperLimit = ctx.upperLimit.value

        v_annotation = self.getList(ctx.v_annotation)
        v_arraySize = self.getList(ctx.v_arraySize)
        v_bitMask = self.getList(ctx.v_bitMask)
        v_bitOperation = self.getList(ctx.v_bitOperation)
        v_byteOrder = self.getList(ctx.v_byteOrder)
        v_discrete = self.getList(ctx.v_discrete)
        v_displayIdentifier = self.getList(ctx.v_displayIdentifier)
        v_ecuAddress = self.getList(ctx.v_ecuAddress)
        v_ecuAddressExtension = self.getList(ctx.v_ecuAddressExtension)
        v_errorMask = self.getList(ctx.v_errorMask)
        v_format_ = self.getList(ctx.v_format_)
        v_functionList = self.getList(ctx.v_functionList)
        v_ifData = self.getList(ctx.v_ifData)
        v_layout = self.getList(ctx.v_layout)
        v_matrixDim = self.getList(ctx.v_matrixDim)
        v_maxRefresh = self.getList(ctx.v_maxRefresh)
        v_physUnit = self.getList(ctx.v_physUnit)
        v_readWrite = self.getList(ctx.v_readWrite)
        v_refMemorySegment = self.getList(ctx.v_refMemorySegment)
        v_symbolLink = self.getList(ctx.v_symbolLink)
        v_virtual = self.getList(ctx.v_virtual)

    def exitArraySize(self, ctx):
        number_ = ctx.number_.value
        ctx.value = number_

    def exitBitOperation(self, ctx):
        v_leftShift = self.getList(ctx.v_leftShift)
        v_rightShift = self.getList(ctx.v_rightShift)
        v_signExtend = self.getList(ctx.v_signExtend)
        ctx.value = (v_leftShift, v_rightShift, v_signExtend)

    def exitLeftShift(self, ctx):
        bitcount = ctx.bitcount.value

    def exitRightShift(self, ctx):
        bitcount = ctx.bitcount.value

    def exitSignExtend(self, ctx):
        ctx.value = True

    def exitEcuAddress(self, ctx):
        address = ctx.address.value
        ctx.value = address

    def exitErrorMask(self, ctx):
        mask = ctx.mask.value
        ctx.value = mask

    def exitLayout(self, ctx):
        indexMode = ctx.indexMode.text

    def exitReadWrite(self, ctx):
        ctx.value = True

    def exitVirtual(self, ctx):
        measuringChannel = self.getList(ctx.measuringChannel)
        ctx.value = measuringChannel

    def exitModCommon(self, ctx):
        comment = ctx.comment.value

        v_alignmentByte = self.getList(ctx.v_alignmentByte)
        v_alignmentFloat32Ieee = self.getList(ctx.v_alignmentFloat32Ieee)
        v_alignmentFloat64Ieee = self.getList(ctx.v_alignmentFloat64Ieee)
        v_alignmentInt64 = self.getList(ctx.v_alignmentInt64)
        v_alignmentLong = self.getList(ctx.v_alignmentLong)
        v_alignmentWord = self.getList(ctx.v_alignmentWord)
        v_byteOrder = self.getList(ctx.v_byteOrder)
        v_dataSize = self.getList(ctx.v_dataSize)
        v_deposit = self.getList(ctx.v_deposit)
        v_sRecLayout = self.getList(ctx.v_sRecLayout)

    def exitDataSize(self, ctx):
        size = ctx.size.value
        ctx.value = size

    def exitSRecLayout(self, ctx):
        name = ctx.name.value
        ctx.value = name

    def exitModPar(self, ctx):
        comment = ctx.comment.value

        v_addrEpk = self.getList(ctx.v_addrEpk)
        v_calibrationMethod = self.getList(ctx.v_calibrationMethod)
        v_cpuType = self.getList(ctx.v_cpuType)
        v_customer = self.getList(ctx.v_customer)
        v_customerNo = self.getList(ctx.v_customerNo)
        v_ecu = self.getList(ctx.v_ecu)
        v_ecuCalibrationOffset = self.getList(ctx.v_ecuCalibrationOffset)
        v_epk = self.getList(ctx.v_epk)
        v_memoryLayout = self.getList(ctx.v_memoryLayout)
        v_memorySegment = self.getList(ctx.v_memorySegment)
        v_noOfInterfaces = self.getList(ctx.v_noOfInterfaces)
        v_phoneNo = self.getList(ctx.v_phoneNo)
        v_supplier = self.getList(ctx.v_supplier)
        v_systemConstant = self.getList(ctx.v_systemConstant)
        v_user = self.getList(ctx.v_user)
        v_version = self.getList(ctx.v_version)

    def exitAddrEpk(self, ctx):
        address = ctx.address.value
        ctx.value = address

    def exitCalibrationMethod(self, ctx):
        method = ctx.method.value
        version_ = ctx.version_.value
        v_calibrationHandle = self.getList(ctx.v_calibrationHandle)
        ctx.value = (method, version_, v_calibrationHandle)
        print("CAL_METH", (method, version_, v_calibrationHandle))

    def exitCalibrationHandle(self, ctx):
        handle = self.getList(ctx.handle)
        v_calibrationHandleText = self.getList(ctx.v_calibrationHandleText)
        ctx.value = (handle, v_calibrationHandleText)

    def exitCalibrationHandleText(self, ctx):
        text = ctx.text.value
        ctx.value = text

    def exitCpuType(self, ctx):
        cPU = ctx.cPU.value
        ctx.value = cPU

    def exitCustomer(self, ctx):
        customer_ = ctx.customer_.value
        ctx.value = customer_

    def exitCustomerNo(self, ctx):
        number_ = ctx.number_.value
        ctx.value = number_

    def exitEcu(self, ctx):
        controlUnit = ctx.controlUnit.value
        ctx.value = controlUnit

    def exitEcuCalibrationOffset(self, ctx):
        offset = ctx.offset.value
        ctx.value = offset

    def exitEpk(self, ctx):
        identifier = ctx.identifier.value
        ctx.value = identifier

    def exitMemoryLayout(self, ctx):
        prgType = ctx.prgType.text
        address = ctx.address.value
        size = ctx.size.value
        offset_0 = ctx.offset_0.value
        offset_1 = ctx.offset_1.value
        offset_2 = ctx.offset_2.value
        offset_3 = ctx.offset_3.value
        offset_4 = ctx.offset_4.value
        v_ifData = self.getList(self.v_ifData)

    def exitMemorySegment(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        prgType = ctx.prgType.text
        memoryType = ctx.memoryType.text
        attribute = ctx.attribute.text
        address = ctx.address.value
        size = ctx.size.value
        offset_0 = ctx.offset_0.value
        offset_1 = ctx.offset_1.value
        offset_2 = ctx.offset_2.value
        offset_3 = ctx.offset_3.value
        offset_4 = ctx.offset_4.value

        v_ifData = self.getList(ctx.v_ifData)

    def exitNoOfInterfaces(self, ctx):
        num = ctx.num.value
        ctx.value = num

    def exitPhoneNo(self, ctx):
        telnum = ctx.telnum.value
        ctx.value = telnum

    def exitSupplier(self, ctx):
        manufacturer = ctx.manufacturer.value
        ctx.value = manufacturer

    def exitSystemConstant(self, ctx):
        name = ctx.name.value
        value_ = ctx.value_.value
        ctx.value = (name, value_)
        print("SYSTEM-CONSTANT:", (name, value_))

    def exitUser(self, ctx):
        userName = ctx.userName.value
        ctx.value = userName

    def exitRecordLayout(self, ctx):
        name = ctx.name.value

        v_alignmentByte = self.getList(ctx.v_alignmentByte)
        v_alignmentFloat32Ieee = self.getList(ctx.v_alignmentFloat32Ieee)
        v_alignmentFloat64Ieee = self.getList(ctx.v_alignmentFloat64Ieee)
        v_alignmentInt64 = self.getList(ctx.v_alignmentInt64)
        v_alignmentLong = self.getList(ctx.v_alignmentLong)
        v_alignmentWord = self.getList(ctx.v_alignmentWord)
        v_axisPtsX = self.getList(ctx.v_axisPtsX)
        v_axisPtsY = self.getList(ctx.v_axisPtsY)
        v_axisPtsZ = self.getList(ctx.v_axisPtsZ)
        v_axisPts4 = self.getList(ctx.v_axisPts4)
        v_axisPts5 = self.getList(ctx.v_axisPts5)
        v_axisRescaleX = self.getList(ctx.v_axisRescaleX)
        v_axisRescaleY = self.getList(ctx.v_axisRescaleY)
        v_axisRescaleZ = self.getList(ctx.v_axisRescaleZ)
        v_axisRescale4 = self.getList(ctx.v_axisRescale4)
        v_axisRescale5 = self.getList(ctx.v_axisRescale5)
        v_distOpX = self.getList(ctx.v_distOpX)
        v_distOpY = self.getList(ctx.v_distOpY)
        v_distOpZ = self.getList(ctx.v_distOpZ)
        v_distOp4 = self.getList(ctx.v_distOp4)
        v_distOp5 = self.getList(ctx.v_distOp5)
        v_fixNoAxisPtsX = self.getList(ctx.v_fixNoAxisPtsX)
        v_fixNoAxisPtsY = self.getList(ctx.v_fixNoAxisPtsY)
        v_fixNoAxisPtsZ = self.getList(ctx.v_fixNoAxisPtsZ)
        v_fixNoAxisPts4 = self.getList(ctx.v_fixNoAxisPts4)
        v_fixNoAxisPts5 = self.getList(ctx.v_fixNoAxisPts5)
        v_fncValues = self.getList(ctx.v_fncValues)
        v_identification = self.getList(ctx.v_identification)
        v_noAxisPtsX = self.getList(ctx.v_noAxisPtsX)
        v_noAxisPtsY = self.getList(ctx.v_noAxisPtsY)
        v_noAxisPtsZ = self.getList(ctx.v_noAxisPtsZ)
        v_noAxisPts4 = self.getList(ctx.v_noAxisPts4)
        v_noAxisPts5 = self.getList(ctx.v_noAxisPts5)
        v_staticRecordLayout = self.getList(ctx.v_staticRecordLayout)
        v_noRescaleX = self.getList(ctx.v_noRescaleX)
        v_noRescaleY = self.getList(ctx.v_noRescaleY)
        v_noRescaleZ = self.getList(ctx.v_noRescaleZ)
        v_noRescale4 = self.getList(ctx.v_noRescale4)
        v_noRescale5 = self.getList(ctx.v_noRescale5)
        v_offsetX = self.getList(ctx.v_offsetX)
        v_offsetY = self.getList(ctx.v_offsetY)
        v_offsetZ = self.getList(ctx.v_offsetZ)
        v_offset4 = self.getList(ctx.v_offset4)
        v_offset5 = self.getList(ctx.v_offset5)
        v_reserved = self.getList(ctx.v_reserved)
        v_ripAddrW = self.getList(ctx.v_ripAddrW)
        v_ripAddrX = self.getList(ctx.v_ripAddrX)
        v_ripAddrY = self.getList(ctx.v_ripAddrY)
        v_ripAddrZ = self.getList(ctx.v_ripAddrZ)
        v_ripAddr4 = self.getList(ctx.v_ripAddr4)
        v_ripAddr5 = self.getList(ctx.v_ripAddr5)
        v_shiftOpX = self.getList(ctx.v_shiftOpX)
        v_shiftOpY = self.getList(ctx.v_shiftOpY)
        v_shiftOpZ = self.getList(ctx.v_shiftOpZ)
        v_shiftOp4 = self.getList(ctx.v_shiftOp4)
        v_shiftOp5 = self.getList(ctx.v_shiftOp5)
        v_srcAddrX = self.getList(ctx.v_srcAddrX)
        v_srcAddrY = self.getList(ctx.v_srcAddrY)
        v_srcAddrZ = self.getList(ctx.v_srcAddrZ)
        v_srcAddr4 = self.getList(ctx.v_srcAddr4)
        v_srcAddr5 = self.getList(ctx.v_srcAddr5)

    def exitAxisPtsX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        print("PtsX", position, datatype, indexIncr, addressing)


    def exitAxisPtsY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        print("PtsY", position, datatype, indexIncr, addressing)


    def exitAxisPtsZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        print("PtsZ", position, datatype, indexIncr, addressing)


    def exitAxisPts4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        print("Pts4", position, datatype, indexIncr, addressing)


    def exitAxisPts5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        print("Pts5", position, datatype, indexIncr, addressing)

    def exitAxisRescaleX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        maxNumberOfRescalePairs = ctx.maxNumberOfRescalePairs.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        print("RescaleX", position, datatype, maxNumberOfRescalePairs, indexIncr, addressing)

    def exitAxisRescaleY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        maxNumberOfRescalePairs = ctx.maxNumberOfRescalePairs.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        print("RescaleY", position, datatype, maxNumberOfRescalePairs, indexIncr, addressing)

    def exitAxisRescaleZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        maxNumberOfRescalePairs = ctx.maxNumberOfRescalePairs.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        print("RescaleZ", position, datatype, maxNumberOfRescalePairs, indexIncr, addressing)

    def exitAxisRescale4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        maxNumberOfRescalePairs = ctx.maxNumberOfRescalePairs.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        print("Rescale4", position, datatype, maxNumberOfRescalePairs, indexIncr, addressing)

    def exitAxisRescale5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        maxNumberOfRescalePairs = ctx.maxNumberOfRescalePairs.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        print("Rescale5", position, datatype, maxNumberOfRescalePairs, indexIncr, addressing)

    def exitDistOpX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitDistOpY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitDistOpZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitDistOp4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitDistOp5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitFixNoAxisPtsX(self, ctx):
        numberOfAxisPoints = ctx.numberOfAxisPoints.value
        ctx.value = numberOfAxisPoints

    def exitFixNoAxisPtsY(self, ctx):
        numberOfAxisPoints = ctx.numberOfAxisPoints.value
        ctx.value = numberOfAxisPoints

    def exitFixNoAxisPtsZ(self, ctx):
        numberOfAxisPoints = ctx.numberOfAxisPoints.value
        ctx.value = numberOfAxisPoints

    def exitFixNoAxisPts4(self, ctx):
        numberOfAxisPoints = ctx.numberOfAxisPoints.value
        ctx.value = numberOfAxisPoints

    def exitFixNoAxisPts5(self, ctx):
        numberOfAxisPoints = ctx.numberOfAxisPoints.value
        ctx.value = numberOfAxisPoints

    def exitFncValues(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        indexMode = ctx.indexMode.text
        addresstype = ctx.addresstype.value
        ctx.value = (position, datatype, indexMode, addresstype)

    def exitIdentification(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitNoAxisPtsX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitNoAxisPtsY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitNoAxisPtsZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitNoAxisPts4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitNoAxisPts5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitStaticRecordLayout(self, ctx):
        ctx.value = True

    def exitNoRescaleX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitNoRescaleY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitNoRescaleZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitNoRescale4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitNoRescale5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitOffsetX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitOffsetY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitOffsetZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitOffset4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitOffset5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitReserved(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitRipAddrW(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitRipAddrX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitRipAddrY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitRipAddrZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitRipAddr4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitRipAddr5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitShiftOpX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitShiftOpY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitShiftOpZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitShiftOp4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitShiftOp5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitSrcAddrX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitSrcAddrY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitSrcAddrZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitSrcAddr4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitSrcAddr5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = (position, datatype)

    def exitUnit(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        display = ctx.display.value
        type_ = ctx.type_.text

        v_siExponents = self.getList(ctx.v_siExponents)
        v_refUnit = self.getList(ctx.v_refUnit)
        v_unitConversion = self.getList(ctx.v_unitConversion)

    def exitSiExponents(self, ctx):
        length = ctx.length.value
        mass = ctx.mass.value
        time = ctx.time.value
        electricCurrent = ctx.electricCurrent.value
        temperature = ctx.temperature.value
        amountOfSubstance = ctx.amountOfSubstance.value
        luminousIntensity = ctx.luminousIntensity.value
        ctx.value = (length, mass, time, electricCurrent, temperature, amountOfSubstance, luminousIntensity)

    def exitUnitConversion(self, ctx):
        gradient = ctx.gradient.value
        offset = ctx.offset.value
        ctx.value = (gradient, offset)

    def exitUserRights(self, ctx):
        userLevelId = ctx.userLevelId.value

        v_readOnly = self.getList(ctx.v_readOnly)
        v_refGroup = self.getList(ctx.v_refGroup)

    def exitRefGroup(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = identifier

    def exitVariantCoding(self, ctx):
        v_varCharacteristic = self.getList(ctx.v_varCharacteristic)
        v_varCriterion = self.getList(ctx.v_varCriterion)
        v_varForbiddenComb = self.getList(ctx.v_varForbiddenComb)
        v_varNaming = self.getList(ctx.v_varNaming)
        v_varSeparator = self.getList(ctx.v_varSeparator)

    def exitVarCharacteristic(self, ctx):
        name = ctx.name.value
        criterionName = self.getList(ctx.criterionName)
        v_varAddress = self.getList(ctx.v_varAddress)

    def exitVarAddress(self, ctx):
        address = self.getList(ctx.address)
        ctx.value = address

    def exitVarCriterion(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        value_ = self.getList(ctx.value_)

        v_varMeasurement = self.getList(ctx.v_varMeasurement)
        v_varSelectionCharacteristic = self.getList(ctx.v_varSelectionCharacteristic)

    def exitVarMeasurement(self, ctx):
        name = ctx.name.value
        ctx.value = name

    def exitVarSelectionCharacteristic(self, ctx):
        name = ctx.name.value
        ctx.value = name

    def exitVarForbiddenComb(self, ctx):
        criterionName = self.getList(ctx.criterionName)
        criterionValue = self.getList(ctx.criterionValue)
        pairs = zip(criterionName, criterionValue)
        ctx.value = pairs

    def exitVarNaming(self, ctx):
        tag = ctx.tag.text
        ctx.value = tag

    def exitVarSeparator(self, ctx):
        separator = ctx.separator.value
        ctx.value = separator

    def exitDataType(self, ctx):
        ctx.value = ctx.v.text if ctx.v else None

    def exitIndexorder(self, ctx):
        ctx.value = ctx.v.text if ctx.v else None

    def exitByteOrderValue(self, ctx):
        ctx.value = ctx.v.text if ctx.v else None

    def exitDatasize(self, ctx):
        ctx.value = ctx.v.text if ctx.v else None

    def exitAddrtype(self, ctx):
        ctx.value = ctx.v.text if ctx.v else None

