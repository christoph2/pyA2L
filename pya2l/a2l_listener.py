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


from decimal import Decimal as D
import re

import antlr4

import pya2l.model as model
from pya2l.logger import Logger

def delist(iterable, scalar=False):
    if len(iterable) == 0:
        if scalar:
            return None
        else:
            return []
    elif len(iterable) == 1:
        if scalar:
            return iterable[0]
        else:
            return [iterable[0]]
    elif len(iterable) > 1:
        if scalar:
            return iterable[0]
        else:
            return [iterable[0]]



class BaseListener(antlr4.ParseTreeListener):
    """"""

    value = []

    def __init__(self, *args, **kws):
        super(BaseListener, self).__init__(*args, **kws)
        self.logger = Logger(__name__)

    def getList(self, attr):
        return [x.value for x in attr] if attr else []

    def getTerminal(self, attr):
        return attr().getText() if attr() else ""

    def exitIntegerValue(self, ctx):
        if ctx.i:
            ctx.value = int(ctx.i.text, 10)
        elif ctx.h:
            ctx.value = int(ctx.h.text, 16)
        else:
            ctx.value = None

    def exitNumericValue(self, ctx):
        if ctx.f:
            ctx.value = D(ctx.f.text)
        elif ctx.i:
            ctx.value = D(ctx.i.text)
        else:
            ctx.value = None

    def exitStringValue(self, ctx):
        ctx.value = ctx.s.text.strip('"') if ctx.s else None

    def exitIdentifierValue(self, ctx):
        text = ".".join(self.getList(ctx.i))
        ctx.value = text

    def exitPartialIdentifier(self, ctx):
        text = ctx.i.text if ctx.i else ""
        result = ""
        for element in ctx.a:
            result += "[{}]".format(element.value)
        ctx.value = text + result

    def exitArraySpecifier(self, ctx):
        if ctx.i is not None:
            value = ctx.i.text
        elif ctx.n is not None:
            value = ctx.n.text
        else:
            value = None
        ctx.value = value

    def _formatMessage(self, msg, location):
        return "[{0}:{1}] {2}".format(
            location.start.line, location.start.column + 1, msg
        )

    def _log(self, method, msg, location=None):
        if location:
            method(self._formatMessage(msg, location))
        else:
            method(msg)

    def info(self, msg, location=None):
        self._log(self.logger.info, msg, location)

    def warn(self, msg, location=None):
        self._log(self.logger.warn, msg, location)

    def error(self, msg, location=None):
        self._log(self.logger.error, msg, location)

    def debug(self, msg, location=None):
        self._log(self.logger.debug, msg, location)


class A2LListener(BaseListener):
    """"""

    def exitAlignmentByte(self, ctx):
        alignmentBorder = ctx.alignmentBorder.value
        ctx.value = model.AlignmentByte(alignmentBorder=alignmentBorder)
        self.db.session.add(ctx.value)

    def exitAlignmentFloat32Ieee(self, ctx):
        alignmentBorder = ctx.alignmentBorder.value
        ctx.value = model.AlignmentFloat32Ieee(alignmentBorder=alignmentBorder)
        self.db.session.add(ctx.value)

    def exitAlignmentFloat64Ieee(self, ctx):
        alignmentBorder = ctx.alignmentBorder.value
        ctx.value = model.AlignmentFloat64Ieee(alignmentBorder=alignmentBorder)
        self.db.session.add(ctx.value)

    def exitAlignmentInt64(self, ctx):
        alignmentBorder = ctx.alignmentBorder.value
        ctx.value = model.AlignmentInt64(alignmentBorder=alignmentBorder)
        self.db.session.add(ctx.value)

    def exitAlignmentLong(self, ctx):
        alignmentBorder = ctx.alignmentBorder.value
        ctx.value = model.AlignmentLong(alignmentBorder=alignmentBorder)
        self.db.session.add(ctx.value)

    def exitAlignmentWord(self, ctx):
        alignmentBorder = ctx.alignmentBorder.value
        ctx.value = model.AlignmentWord(alignmentBorder=alignmentBorder)
        self.db.session.add(ctx.value)

    def exitAnnotation(self, ctx):
        v_annotationLabel = delist(self.getList(ctx.v_annotationLabel), True)
        v_annotationOrigin = delist(self.getList(ctx.v_annotationOrigin), True)
        v_annotationText = delist(self.getList(ctx.v_annotationText), True)
        ctx.value = model.Annotation(
            annotation_label=v_annotationLabel,
            annotation_origin=v_annotationOrigin,
            annotation_text=v_annotationText,
        )
        self.db.session.add(ctx.value)

    def exitAnnotationLabel(self, ctx):
        label = ctx.label.value
        ctx.value = model.AnnotationLabel(label=label)
        self.db.session.add(ctx.value)

    def exitAnnotationOrigin(self, ctx):
        origin = ctx.origin.value
        ctx.value = model.AnnotationOrigin(origin=origin)
        self.db.session.add(ctx.value)

    def exitAnnotationText(self, ctx):
        text = self.getList(ctx.text)
        ctx.value = model.AnnotationText(text=text)
        self.db.session.add(ctx.value)

    def exitBitMask(self, ctx):
        mask = ctx.mask.value
        ctx.value = model.BitMask(mask=mask)
        self.db.session.add(ctx.value)

    def exitByteOrder(self, ctx):
        byteOrder_ = ctx.byteOrder_.value
        ctx.value = model.ByteOrder(byteOrder=byteOrder_)
        self.db.session.add(ctx.value)

    def exitCalibrationAccess(self, ctx):
        type_ = ctx.type_.text
        ctx.value = model.CalibrationAccess(type=type_)
        self.db.session.add(ctx.value)

    def exitDefaultValue(self, ctx):
        display_string = ctx.display_string.value
        ctx.value = model.DefaultValue(display_string=display_string)
        self.db.session.add(ctx.value)

    def exitDeposit(self, ctx):
        mode_ = ctx.mode_.text
        ctx.value = model.Deposit(mode=mode_)

        self.db.session.add(ctx.value)

    def exitDiscrete(self, ctx):
        ctx.value = True
        # self.db.session.add(ctx.value)

    def exitDisplayIdentifier(self, ctx):
        display_name = ctx.display_name.value
        ctx.value = model.DisplayIdentifier(display_name=display_name)
        self.db.session.add(ctx.value)

    def exitEcuAddressExtension(self, ctx):
        extension = ctx.extension.value
        ctx.value = model.EcuAddressExtension(extension=extension)
        self.db.session.add(ctx.value)

    def exitExtendedLimits(self, ctx):
        lowerLimit = ctx.lowerLimit.value
        upperLimit = ctx.upperLimit.value
        ctx.value = model.ExtendedLimits(lowerLimit=lowerLimit, upperLimit=upperLimit)
        self.db.session.add(ctx.value)

    def exitFormat_(self, ctx):
        formatString = ctx.formatString.value
        ctx.value = model.Format(formatString=formatString)
        self.db.session.add(ctx.value)

    def exitFunctionList(self, ctx):
        name = self.getList(ctx.name)
        ctx.value = model.FunctionList(name=name)
        self.db.session.add(ctx.value)

    def exitGuardRails(self, ctx):
        ctx.value = True
        # self.db.session.add(ctx.value)

    def exitIfData(self, ctx):
        ctx.value = model.IfData(name="")
        self.db.session.add(ctx.value)
        #print("IfData:", ctx.start, ctx.stop)

    def exitMatrixDim(self, ctx):
        xDim = ctx.xDim.value
        yDim = ctx.yDim.value if ctx.yDim else None
        zDim = ctx.zDim.value if ctx.zDim else None
        ctx.value = model.MatrixDim(xDim = xDim, yDim = yDim, zDim = zDim)
        self.db.session.add(ctx.value)

    def exitMaxRefresh(self, ctx):
        scalingUnit = ctx.scalingUnit.value
        rate = ctx.rate.value
        ctx.value = model.MaxRefresh(scalingUnit=scalingUnit, rate=rate)
        self.db.session.add(ctx.value)

    def exitMonotony(self, ctx):
        monotony_ = ctx.monotony_.text
        ctx.value = model.Monotony(monotony=monotony_)
        self.db.session.add(ctx.value)

    def exitPhysUnit(self, ctx):
        unit_ = ctx.unit_.value
        ctx.value = model.PhysUnit(unit=unit_)
        self.db.session.add(ctx.value)

    def exitReadOnly(self, ctx):
        ctx.value = True
        # self.db.session.add(ctx.value)

    def exitRefCharacteristic(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = model.RefCharacteristic(identifier=identifier)
        self.db.session.add(ctx.value)

    def exitRefMemorySegment(self, ctx):
        name = ctx.name.value
        ctx.value = model.RefMemorySegment(name=name)
        self.db.session.add(ctx.value)

    def exitRefUnit(self, ctx):
        unit_ = ctx.unit_.value
        ctx.value = model.RefUnit(unit=unit_)
        self.db.session.add(ctx.value)

    def exitStepSize(self, ctx):
        stepSize_ = ctx.stepSize_.value
        ctx.value = model.StepSize(stepSize=stepSize_)
        self.db.session.add(ctx.value)

    def exitSymbolLink(self, ctx):
        symbolName = ctx.symbolName.value
        offset = ctx.offset.value
        ctx.value = model.SymbolLink(symbolName=symbolName, offset=offset)
        self.db.session.add(ctx.value)

    def exitVersion(self, ctx):
        versionIdentifier = ctx.versionIdentifier.value
        ctx.value = model.Version(versionIdentifier=versionIdentifier)
        self.db.session.add(ctx.value)

    def exitAsap2Version(self, ctx):
        versionNo = ctx.versionNo.value
        upgradeNo = ctx.upgradeNo.value

        if versionNo > 1 or (versionNo == 1 and upgradeNo < 60):
            self.error(
                "ASAP2 Version '{}.{}' may not parsed correctly.".format(
                    versionNo, upgradeNo
                )
            )

        ctx.value = model.Asap2Version(versionNo=versionNo, upgradeNo=upgradeNo)
        self.db.session.add(ctx.value)

    def exitA2mlVersion(self, ctx):
        versionNo = ctx.versionNo.value
        upgradeNo = ctx.upgradeNo.value
        ctx.value = model.A2mlVersion(versionNo=versionNo, upgradeNo=upgradeNo)
        self.db.session.add(ctx.value)

    def exitProject(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        v_header = delist(self.getList(ctx.v_header), True)
        v_module = self.getList(ctx.v_module)
        ctx.value = model.Project(
            name=name, longIdentifier=longIdentifier, header=v_header, module=v_module
        )
        self.db.session.add(ctx.value)

    def exitHeader(self, ctx):
        comment = ctx.comment.value
        v_projectNo = delist(self.getList(ctx.v_projectNo), True)
        v_version = delist(self.getList(ctx.v_version), True)
        ctx.value = model.Header(
            comment=comment, project_no=v_projectNo, version=v_version
        )
        self.db.session.add(ctx.value)

    def exitProjectNo(self, ctx):
        projectNumber = ctx.projectNumber.value
        ctx.value = model.ProjectNo(projectNumber=projectNumber)
        self.db.session.add(ctx.value)

    def exitModule(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value

        v_a2ml = delist(self.getList(ctx.v_a2ml), True)
        v_axisPts = self.getList(ctx.v_axisPts)
        v_characteristic = self.getList(ctx.v_characteristic)
        v_compuMethod = self.getList(ctx.v_compuMethod)
        v_compuTab = self.getList(ctx.v_compuTab)
        v_compuVtab = self.getList(ctx.v_compuVtab)
        v_compuVtabRange = self.getList(ctx.v_compuVtabRange)
        v_frame = delist(self.getList(ctx.v_frame), True)
        v_function = self.getList(ctx.v_function)
        v_group = self.getList(ctx.v_group)
        # v_ifData = self.getList(ctx.v_ifData)
        v_measurement = self.getList(ctx.v_measurement)
        v_modCommon = delist(self.getList(ctx.v_modCommon), True)
        v_modPar = delist(self.getList(ctx.v_modPar), True)
        v_recordLayout = self.getList(ctx.v_recordLayout)
        v_unit = self.getList(ctx.v_unit)
        v_userRights = self.getList(ctx.v_userRights)
        v_variantCoding = delist(self.getList(ctx.v_variantCoding), True)

        ctx.value = model.Module(
            name=name,
            longIdentifier=longIdentifier,
            a2ml=v_a2ml,
            axis_pts=v_axisPts,
            characteristic=v_characteristic,
            compu_method=v_compuMethod,
            compu_tab=v_compuTab,
            compu_vtab=v_compuVtab,
            compu_vtab_range=v_compuVtabRange,
            frame=v_frame,
            function=v_function,
            group=v_group,
            measurement=v_measurement,
            mod_common=v_modCommon,
            mod_par=v_modPar,
            record_layout=v_recordLayout,
            unit=v_unit,
            user_rights=v_userRights,
            variant_coding=v_variantCoding,
        )
        self.db.session.add(ctx.value)

    def exitA2ml(self, ctx):
        ctx.value = model.A2ml()
        self.db.session.add(ctx.value)

    def exitAxisPts(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        address = ctx.address.value
        inputQuantity = ctx.inputQuantity.value
        depositAttr = ctx.depositAttr.value
        maxDiff = ctx.maxDiff.value
        conversion = ctx.conversion.value
        maxAxisPoints = ctx.maxAxisPoints.value
        lowerLimit = ctx.lowerLimit.value
        upperLimit = ctx.upperLimit.value

        v_annotation = self.getList(ctx.v_annotation)
        v_byteOrder = delist(self.getList(ctx.v_byteOrder), True)
        v_calibrationAccess = delist(self.getList(ctx.v_calibrationAccess), True)
        v_deposit = delist(self.getList(ctx.v_deposit), True)
        v_displayIdentifier = delist(self.getList(ctx.v_displayIdentifier), True)
        v_ecuAddressExtension = delist(self.getList(ctx.v_ecuAddressExtension), True)
        v_extendedLimits = delist(self.getList(ctx.v_extendedLimits), True)
        v_format_ = delist(self.getList(ctx.v_format_), True)
        v_functionList = delist(self.getList(ctx.v_functionList), True)
        v_guardRails = delist(self.getList(ctx.v_guardRails), True)
        v_ifData = self.getList(ctx.v_ifData)
        v_monotony = delist(self.getList(ctx.v_monotony), True)
        v_physUnit = delist(self.getList(ctx.v_physUnit), True)
        v_readOnly = delist(self.getList(ctx.v_readOnly), True)
        v_refMemorySegment = delist(self.getList(ctx.v_refMemorySegment), True)
        v_stepSize = delist(self.getList(ctx.v_stepSize), True)
        v_symbolLink = delist(self.getList(ctx.v_symbolLink), True)

        ctx.value = model.AxisPts(
            name=name,
            longIdentifier=longIdentifier,
            address=address,
            inputQuantity=inputQuantity,
            maxDiff=maxDiff,
            conversion=conversion,
            maxAxisPoints=maxAxisPoints,
            lowerLimit=lowerLimit,
            upperLimit=upperLimit,
            annotation=v_annotation,
            byte_order=v_byteOrder,
            calibration_access=v_calibrationAccess,
            deposit=v_deposit,
            depositAttr=depositAttr,
            display_identifier=v_displayIdentifier,
            ecu_address_extension=v_ecuAddressExtension,
            extended_limits=v_extendedLimits,
            format=v_format_,
            function_list=v_functionList,
            guard_rails=v_guardRails,
            if_data=v_ifData,
            monotony=v_monotony,
            phys_unit=v_physUnit,
            read_only=v_readOnly,
            ref_memory_segment=v_refMemorySegment,
            step_size=v_stepSize,
            symbol_link=v_symbolLink,
        )
        self.db.session.add(ctx.value)

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
        v_bitMask = delist(self.getList(ctx.v_bitMask), True)
        v_byteOrder = delist(self.getList(ctx.v_byteOrder), True)
        v_calibrationAccess = delist(self.getList(ctx.v_calibrationAccess), True)
        v_comparisonQuantity = delist(self.getList(ctx.v_comparisonQuantity), True)
        v_dependentCharacteristic = delist(
            self.getList(ctx.v_dependentCharacteristic), True
        )
        v_discrete = delist(self.getList(ctx.v_discrete), True)
        v_displayIdentifier = delist(self.getList(ctx.v_displayIdentifier), True)
        v_ecuAddressExtension = delist(self.getList(ctx.v_ecuAddressExtension), True)
        v_extendedLimits = delist(self.getList(ctx.v_extendedLimits), True)
        v_format_ = delist(self.getList(ctx.v_format_), True)
        v_functionList = delist(self.getList(ctx.v_functionList), True)
        v_guardRails = delist(self.getList(ctx.v_guardRails), True)
        v_ifData = self.getList(ctx.v_ifData)
        v_mapList = delist(self.getList(ctx.v_mapList), True)
        v_matrixDim = delist(self.getList(ctx.v_matrixDim), True)
        v_maxRefresh = delist(self.getList(ctx.v_maxRefresh), True)
        v_number = delist(self.getList(ctx.v_number), True)
        v_physUnit = delist(self.getList(ctx.v_physUnit), True)
        v_readOnly = delist(self.getList(ctx.v_readOnly), True)
        v_refMemorySegment = delist(self.getList(ctx.v_refMemorySegment), True)
        v_stepSize = delist(self.getList(ctx.v_stepSize), True)
        v_symbolLink = delist(self.getList(ctx.v_symbolLink), True)
        v_virtualCharacteristic = delist(
            self.getList(ctx.v_virtualCharacteristic), True
        )

        ctx.value = model.Characteristic(
            name=name,
            longIdentifier=longIdentifier,
            type=type_,
            address=address,
            deposit=deposit_,
            maxDiff=maxDiff,
            conversion=conversion,
            lowerLimit=lowerLimit,
            upperLimit=upperLimit,
            annotation=v_annotation,
            axis_descr=v_axisDescr,
            bit_mask=v_bitMask,
            byte_order=v_byteOrder,
            calibration_access=v_calibrationAccess,
            comparison_quantity=v_comparisonQuantity,
            dependent_characteristic=v_dependentCharacteristic,
            discrete=v_discrete,
            display_identifier=v_displayIdentifier,
            ecu_address_extension=v_ecuAddressExtension,
            extended_limits=v_extendedLimits,
            format=v_format_,
            function_list=v_functionList,
            guard_rails=v_guardRails,
            if_data=v_ifData,
            map_list=v_mapList,
            matrix_dim=v_matrixDim,
            max_refresh=v_maxRefresh,
            number=v_number,
            phys_unit=v_physUnit,
            read_only=v_readOnly,
            ref_memory_segment=v_refMemorySegment,
            step_size=v_stepSize,
            symbol_link=v_symbolLink,
            virtual_characteristic=v_virtualCharacteristic,
        )
        self.db.session.add(ctx.value)

    def exitAxisDescr(self, ctx):
        attribute = ctx.attribute.text
        inputQuantity = ctx.inputQuantity.value
        conversion = ctx.conversion.value
        maxAxisPoints = ctx.maxAxisPoints.value
        lowerLimit = ctx.lowerLimit.value
        upperLimit = ctx.upperLimit.value

        v_annotation = self.getList(ctx.v_annotation)
        v_axisPtsRef = delist(self.getList(ctx.v_axisPtsRef), True)
        v_byteOrder = delist(self.getList(ctx.v_byteOrder), True)
        v_curveAxisRef = delist(self.getList(ctx.v_curveAxisRef), True)
        v_deposit = delist(self.getList(ctx.v_deposit), True)
        v_extendedLimits = delist(self.getList(ctx.v_extendedLimits), True)
        v_fixAxisPar = delist(self.getList(ctx.v_fixAxisPar), True)
        v_fixAxisParDist = delist(self.getList(ctx.v_fixAxisParDist), True)
        v_fixAxisParList = delist(self.getList(ctx.v_fixAxisParList), True)
        v_format_ = delist(self.getList(ctx.v_format_), True)
        v_maxGrad = delist(self.getList(ctx.v_maxGrad), True)
        v_monotony = delist(self.getList(ctx.v_monotony), True)
        v_physUnit = delist(self.getList(ctx.v_physUnit), True)
        v_readOnly = delist(self.getList(ctx.v_readOnly), True)
        v_stepSize = delist(self.getList(ctx.v_stepSize), True)

        ctx.value = model.AxisDescr(
            attribute=attribute,
            inputQuantity=inputQuantity,
            conversion=conversion,
            maxAxisPoints=maxAxisPoints,
            lowerLimit=lowerLimit,
            upperLimit=upperLimit,
            annotation=v_annotation,
            axis_pts_ref=v_axisPtsRef,
            byte_order=v_byteOrder,
            curve_axis_ref=v_curveAxisRef,
            deposit=v_deposit,
            extended_limits=v_extendedLimits,
            fix_axis_par=v_fixAxisPar,
            fix_axis_par_dist=v_fixAxisParDist,
            fix_axis_par_list=v_fixAxisParList,
            format=v_format_,
            max_grad=v_maxGrad,
            monotony=v_monotony,
            phys_unit=v_physUnit,
            read_only=v_readOnly,
            step_size=v_stepSize,
        )
        self.db.session.add(ctx.value)

    def exitAxisPtsRef(self, ctx):
        axisPoints = ctx.axisPoints.value
        ctx.value = model.AxisPtsRef(axisPoints=axisPoints)
        self.db.session.add(ctx.value)

    def exitCurveAxisRef(self, ctx):
        curveAxis = ctx.curveAxis.value
        ctx.value = model.CurveAxisRef(curveAxis=curveAxis)
        self.db.session.add(ctx.value)

    def exitFixAxisPar(self, ctx):
        offset = ctx.offset.value
        shift = ctx.shift.value
        numberapo = ctx.numberapo.value
        ctx.value = model.FixAxisPar(offset=offset, shift=shift, numberapo=numberapo)
        self.db.session.add(ctx.value)

    def exitFixAxisParDist(self, ctx):
        offset = ctx.offset.value
        distance = ctx.distance.value
        numberapo = ctx.numberapo.value
        ctx.value = model.FixAxisParDist(
            offset=offset, distance=distance, numberapo=numberapo
        )
        self.db.session.add(ctx.value)

    def exitFixAxisParList(self, ctx):
        axisPts_Value = self.getList(ctx.axisPts_Value)
        ctx.value = model.FixAxisParList(axisPts_Value=axisPts_Value)
        self.db.session.add(ctx.value)

    def exitMaxGrad(self, ctx):
        maxGradient = ctx.maxGradient.value
        ctx.value = model.MaxGrad(maxGradient=maxGradient)
        self.db.session.add(ctx.value)

    def exitComparisonQuantity(self, ctx):
        name = ctx.name.value
        ctx.value = model.ComparisonQuantity(name=name)
        self.db.session.add(ctx.value)

    def exitDependentCharacteristic(self, ctx):
        formula_ = ctx.formula_.value
        characteristic_ = self.getList(ctx.characteristic_)
        ctx.value = model.DependentCharacteristic(
            formula=formula_, characteristic_id=characteristic_
        )
        self.db.session.add(ctx.value)

    def exitMapList(self, ctx):
        name = self.getList(ctx.name)
        ctx.value = model.MapList(name=name)
        self.db.session.add(ctx.value)

    def exitNumber(self, ctx):
        number_ = ctx.number_.value
        ctx.value = model.Number(number=number_)
        self.db.session.add(ctx.value)

    def exitVirtualCharacteristic(self, ctx):
        formula_ = ctx.formula_.value
        characteristic_ = self.getList(ctx.characteristic_)
        ctx.value = model.VirtualCharacteristic(
            formula=formula_, characteristic_id=characteristic_
        )
        self.db.session.add(ctx.value)

    def exitCompuMethod(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        conversionType = ctx.conversionType.text
        format__ = ctx.format__.value
        unit_ = ctx.unit_.value

        v_coeffs = delist(self.getList(ctx.v_coeffs), True)
        v_coeffsLinear = delist(self.getList(ctx.v_coeffsLinear), True)
        v_compuTabRef = delist(self.getList(ctx.v_compuTabRef), True)
        v_formula = delist(self.getList(ctx.v_formula), True)
        v_refUnit = delist(self.getList(ctx.v_refUnit), True)
        v_statusStringRef = delist(self.getList(ctx.v_statusStringRef), True)

        ctx.value = model.CompuMethod(
            name=name,
            longIdentifier=longIdentifier,
            conversionType=conversionType,
            format=format__,
            unit=unit_,
            coeffs=v_coeffs,
            coeffs_linear=v_coeffsLinear,
            compu_tab_ref=v_compuTabRef,
            formula=v_formula,
            ref_unit=v_refUnit,
            status_string_ref=v_statusStringRef,
        )
        self.db.session.add(ctx.value)

    def exitCoeffs(self, ctx):
        a = ctx.a.value
        b = ctx.b.value
        c = ctx.c.value
        d = ctx.d.value
        e = ctx.e.value
        f = ctx.f.value
        ctx.value = model.Coeffs(a=a, b=b, c=c, d=d, e=e, f=f)
        self.db.session.add(ctx.value)

    def exitCoeffsLinear(self, ctx):
        a = ctx.a.value
        b = ctx.b.value
        ctx.value = model.CoeffsLinear(a=a, b=b)
        self.db.session.add(ctx.value)

    def exitCompuTabRef(self, ctx):
        conversionTable = ctx.conversionTable.value
        ctx.value = model.CompuTabRef(conversionTable=conversionTable)
        self.db.session.add(ctx.value)

    def exitFormula(self, ctx):
        f_x = ctx.f_x.value
        v_formulaInv = delist(self.getList(ctx.v_formulaInv), True)
        ctx.value = model.Formula(f_x=f_x, formula_inv=v_formulaInv)
        self.db.session.add(ctx.value)

    def exitFormulaInv(self, ctx):
        g_x = ctx.g_x.value
        ctx.value = model.FormulaInv(g_x=g_x)
        self.db.session.add(ctx.value)

    def exitStatusStringRef(self, ctx):
        conversionTable = ctx.conversionTable.value
        ctx.value = model.StatusStringRef(conversionTable=conversionTable)
        self.db.session.add(ctx.value)

    def exitCompuTab(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        conversionType = ctx.conversionType.text
        numberValuePairs = ctx.numberValuePairs.value
        # TODO: check length of following pairs.

        inVal = self.getList(ctx.inVal)
        outVal = self.getList(ctx.outVal)
        pairs = zip(inVal, outVal)

        v_defaultValue = delist(self.getList(ctx.v_defaultValue), True)
        v_defaultValueNumeric = delist(self.getList(ctx.v_defaultValueNumeric), True)

        ctx.value = model.CompuTab(
            name=name,
            longIdentifier=longIdentifier,
            conversionType=conversionType,
            numberValuePairs=numberValuePairs,
            default_value=v_defaultValue,
            default_value_numeric=v_defaultValueNumeric,
        )
        for inVal, outVal in pairs:
            pair = model.CompuTabPair(inVal=inVal, outVal=outVal)
            self.db.session.add(pair)
            ctx.value.pairs.append(pair)
        self.db.session.add(ctx.value)

    def exitDefaultValueNumeric(self, ctx):
        display_value = ctx.display_value.value
        ctx.value = model.DefaultValueNumeric(display_value=display_value)
        self.db.session.add(ctx.value)

    def exitCompuVtab(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        conversionType = "TAB_VERB"
        # Fixed value by Std.

        numberValuePairs = ctx.numberValuePairs.value
        # TODO: check length of following pairs.
        inVal = self.getList(ctx.inVal)
        outVal = self.getList(ctx.outVal)
        pairs = zip(inVal, outVal)
        v_defaultValue = delist(self.getList(ctx.v_defaultValue), True)

        ctx.value = model.CompuVtab(
            name=name,
            longIdentifier=longIdentifier,
            conversionType=conversionType,
            numberValuePairs=numberValuePairs,
            default_value=v_defaultValue,
        )
        for inVal, outVal in pairs:
            pair = model.CompuVtabPair(inVal=inVal, outVal=outVal)
            self.db.session.add(pair)
            ctx.value.pairs.append(pair)
        self.db.session.add(ctx.value)

    def exitCompuVtabRange(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        numberValueTriples = (
            ctx.numberValueTriples.value
        )  # TODO: check length of following triples

        inValMin = self.getList(ctx.inValMin)
        inValMax = self.getList(ctx.inValMax)
        outVal = self.getList(ctx.outVal)
        triples = zip(inValMin, inValMax, outVal)
        v_defaultValue = delist(self.getList(ctx.v_defaultValue), True)

        ctx.value = model.CompuVtabRange(
            name=name,
            longIdentifier=longIdentifier,
            numberValueTriples=numberValueTriples,
            default_value=v_defaultValue,
        )
        for inValMin, inValMax, outVal in triples:
            triple = model.CompuVtabRangeTriple(
                inValMin=inValMin, inValMax=inValMax, outVal=outVal
            )
            self.db.session.add(triple)
            ctx.value.triples.append(triple)
        self.db.session.add(ctx.value)

    def exitFrame(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        scalingUnit = ctx.scalingUnit.value
        rate = ctx.rate.value

        v_frameMeasurement = delist(self.getList(ctx.v_frameMeasurement), True)
        v_ifData = self.getList(ctx.v_ifData)
        ctx.value = model.Frame(
            name=name,
            longIdentifier=longIdentifier,
            scalingUnit=scalingUnit,
            rate=rate,
            frame_measurement=v_frameMeasurement,
            if_data=v_ifData,
        )
        self.db.session.add(ctx.value)

    def exitFrameMeasurement(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = model.FrameMeasurement(identifier=identifier)
        self.db.session.add(ctx.value)

    def exitFunction(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value

        v_annotation = self.getList(ctx.v_annotation)
        v_defCharacteristic = delist(self.getList(ctx.v_defCharacteristic), True)
        v_functionVersion = delist(self.getList(ctx.v_functionVersion), True)
        v_ifData = self.getList(ctx.v_ifData)
        v_inMeasurement = delist(self.getList(ctx.v_inMeasurement), True)
        v_locMeasurement = delist(self.getList(ctx.v_locMeasurement), True)
        v_outMeasurement = delist(self.getList(ctx.v_outMeasurement), True)
        v_refCharacteristic = delist(self.getList(ctx.v_refCharacteristic), True)
        v_subFunction = delist(self.getList(ctx.v_subFunction), True)

        ctx.value = model.Function(
            name=name,
            longIdentifier=longIdentifier,
            annotation=v_annotation,
            def_characteristic=v_defCharacteristic,
            function_version=v_functionVersion,
            if_data=v_ifData,
            in_measurement=v_inMeasurement,
            loc_measurement=v_locMeasurement,
            out_measurement=v_outMeasurement,
            ref_characteristic=v_refCharacteristic,
            sub_function=v_subFunction,
        )
        self.db.session.add(ctx.value)

    def exitDefCharacteristic(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = model.DefCharacteristic(identifier=identifier)
        self.db.session.add(ctx.value)

    def exitFunctionVersion(self, ctx):
        versionIdentifier = ctx.versionIdentifier.value
        ctx.value = model.FunctionVersion(versionIdentifier=versionIdentifier)
        self.db.session.add(ctx.value)

    def exitInMeasurement(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = model.InMeasurement(identifier=identifier)
        self.db.session.add(ctx.value)

    def exitLocMeasurement(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = model.LocMeasurement(identifier=identifier)
        self.db.session.add(ctx.value)

    def exitOutMeasurement(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = model.OutMeasurement(identifier=identifier)
        self.db.session.add(ctx.value)

    def exitSubFunction(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = model.SubFunction(identifier=identifier)
        self.db.session.add(ctx.value)

    def exitGroup(self, ctx):
        groupName = ctx.groupName.value
        groupLongIdentifier = ctx.groupLongIdentifier.value

        v_annotation = self.getList(ctx.v_annotation)
        v_functionList = delist(self.getList(ctx.v_functionList), True)
        v_ifData = self.getList(ctx.v_ifData)
        v_refCharacteristic = delist(self.getList(ctx.v_refCharacteristic), True)
        v_refMeasurement = delist(self.getList(ctx.v_refMeasurement), True)
        v_root = delist(self.getList(ctx.v_root), True)
        v_subGroup = delist(self.getList(ctx.v_subGroup), True)

        ctx.value = model.Group(
            groupName=groupName,
            groupLongIdentifier=groupLongIdentifier,
            annotation=v_annotation,
            function_list=v_functionList,
            if_data=v_ifData,
            ref_characteristic=v_refCharacteristic,
            ref_measurement=v_refMeasurement,
            root=v_root,
            sub_group=v_subGroup,
        )
        self.db.session.add(ctx.value)

    def exitRefMeasurement(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = model.RefMeasurement(identifier=identifier)
        self.db.session.add(ctx.value)

    def exitRoot(self, ctx):
        ctx.value = model.Root()
        self.db.session.add(ctx.value)

    def exitSubGroup(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = model.SubGroup(identifier=identifier)
        self.db.session.add(ctx.value)

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
        v_arraySize = delist(self.getList(ctx.v_arraySize), True)
        v_bitMask = delist(self.getList(ctx.v_bitMask), True)
        v_bitOperation = delist(self.getList(ctx.v_bitOperation), True)
        v_byteOrder = delist(self.getList(ctx.v_byteOrder), True)
        v_discrete = delist(self.getList(ctx.v_discrete), True)
        v_displayIdentifier = delist(self.getList(ctx.v_displayIdentifier), True)
        v_ecuAddress = delist(self.getList(ctx.v_ecuAddress), True)
        v_ecuAddressExtension = delist(self.getList(ctx.v_ecuAddressExtension), True)
        v_errorMask = delist(self.getList(ctx.v_errorMask), True)
        v_format_ = delist(self.getList(ctx.v_format_), True)
        v_functionList = delist(self.getList(ctx.v_functionList), True)
        v_ifData = self.getList(ctx.v_ifData)
        v_layout = delist(self.getList(ctx.v_layout), True)
        v_matrixDim = delist(self.getList(ctx.v_matrixDim), True)
        v_maxRefresh = delist(self.getList(ctx.v_maxRefresh), True)
        v_physUnit = delist(self.getList(ctx.v_physUnit), True)
        v_readWrite = delist(self.getList(ctx.v_readWrite), True)
        v_refMemorySegment = delist(self.getList(ctx.v_refMemorySegment), True)
        v_symbolLink = delist(self.getList(ctx.v_symbolLink), True)
        v_virtual = delist(self.getList(ctx.v_virtual), True)
        ctx.value = model.Measurement(
            name=name,
            longIdentifier=longIdentifier,
            datatype=datatype,
            conversion=conversion,
            resolution=resolution,
            accuracy=accuracy,
            lowerLimit=lowerLimit,
            upperLimit=upperLimit,
            annotation=v_annotation,
            array_size=v_arraySize,
            bit_mask=v_bitMask,
            bit_operation=v_bitOperation,
            byte_order=v_byteOrder,
            discrete=v_discrete,
            display_identifier=v_displayIdentifier,
            ecu_address=v_ecuAddress,
            ecu_address_extension=v_ecuAddressExtension,
            error_mask=v_errorMask,
            format=v_format_,
            function_list=v_functionList,
            if_data=v_ifData,
            layout=v_layout,
            matrix_dim=v_matrixDim,
            max_refresh=v_maxRefresh,
            phys_unit=v_physUnit,
            read_write=v_readWrite,
            ref_memory_segment=v_refMemorySegment,
            symbol_link=v_symbolLink,
            virtual=v_virtual,
        )
        self.db.session.add(ctx.value)

    def exitArraySize(self, ctx):
        number_ = ctx.number_.value
        ctx.value = model.ArraySize(number=number_)
        self.db.session.add(ctx.value)

    def exitBitOperation(self, ctx):
        v_leftShift = delist(self.getList(ctx.v_leftShift), True)
        v_rightShift = delist(self.getList(ctx.v_rightShift), True)
        v_signExtend = delist(self.getList(ctx.v_signExtend), True)
        ctx.value = model.BitOperation(
            left_shift=v_leftShift, right_shift=v_rightShift, sign_extend=v_signExtend
        )
        self.db.session.add(ctx.value)

    def exitLeftShift(self, ctx):
        bitcount = ctx.bitcount.value
        ctx.value = model.LeftShift(bitcount=bitcount)
        self.db.session.add(ctx.value)

    def exitRightShift(self, ctx):
        bitcount = ctx.bitcount.value
        ctx.value = model.RightShift(bitcount=bitcount)
        self.db.session.add(ctx.value)

    def exitSignExtend(self, ctx):
        ctx.value = model.SignExtend()
        self.db.session.add(ctx.value)

    def exitEcuAddress(self, ctx):
        address = ctx.address.value
        ctx.value = model.EcuAddress(address=address)
        self.db.session.add(ctx.value)

    def exitErrorMask(self, ctx):
        mask = ctx.mask.value
        ctx.value = model.ErrorMask(mask=mask)
        self.db.session.add(ctx.value)

    def exitLayout(self, ctx):
        indexMode = ctx.indexMode.text
        ctx.value = model.Layout(indexMode=indexMode)
        self.db.session.add(ctx.value)

    def exitReadWrite(self, ctx):
        ctx.value = model.ReadWrite()
        self.db.session.add(ctx.value)

    def exitVirtual(self, ctx):
        measuringChannel = self.getList(ctx.measuringChannel)
        ctx.value = model.Virtual(measuringChannel=measuringChannel)
        self.db.session.add(ctx.value)

    def exitModCommon(self, ctx):
        comment = ctx.comment.value

        v_alignmentByte = delist(self.getList(ctx.v_alignmentByte), True)
        v_alignmentFloat32Ieee = delist(self.getList(ctx.v_alignmentFloat32Ieee), True)
        v_alignmentFloat64Ieee = delist(self.getList(ctx.v_alignmentFloat64Ieee), True)
        v_alignmentInt64 = delist(self.getList(ctx.v_alignmentInt64), True)
        v_alignmentLong = delist(self.getList(ctx.v_alignmentLong), True)
        v_alignmentWord = delist(self.getList(ctx.v_alignmentWord), True)
        v_byteOrder = delist(self.getList(ctx.v_byteOrder), True)
        v_dataSize = delist(self.getList(ctx.v_dataSize), True)
        v_deposit = delist(self.getList(ctx.v_deposit), True)
        v_sRecLayout = delist(self.getList(ctx.v_sRecLayout), True)

        ctx.value = model.ModCommon(
            comment=comment,
            alignment_byte=v_alignmentByte,
            alignment_float32_ieee=v_alignmentFloat32Ieee,
            alignment_float64_ieee=v_alignmentFloat64Ieee,
            alignment_int64=v_alignmentInt64,
            alignment_long=v_alignmentLong,
            alignment_word=v_alignmentWord,
            byte_order=v_byteOrder,
            data_size=v_dataSize,
            deposit=v_deposit,
            s_rec_layout=v_sRecLayout,
        )
        self.db.session.add(ctx.value)

    def exitDataSize(self, ctx):
        size = ctx.size.value
        ctx.value = model.DataSize(size=size)
        self.db.session.add(ctx.value)

    def exitSRecLayout(self, ctx):
        name = ctx.name.value
        ctx.value = model.SRecLayout(name=name)
        self.db.session.add(ctx.value)

    def exitModPar(self, ctx):
        comment = ctx.comment.value

        v_addrEpk = self.getList(ctx.v_addrEpk)
        v_calibrationMethod = self.getList(ctx.v_calibrationMethod)
        v_cpuType = delist(self.getList(ctx.v_cpuType), True)
        v_customer = delist(self.getList(ctx.v_customer), True)
        v_customerNo = delist(self.getList(ctx.v_customerNo), True)
        v_ecu = delist(self.getList(ctx.v_ecu), True)
        v_ecuCalibrationOffset = delist(self.getList(ctx.v_ecuCalibrationOffset), True)
        v_epk = delist(self.getList(ctx.v_epk), True)
        v_memoryLayout = self.getList(ctx.v_memoryLayout)
        v_memorySegment = self.getList(ctx.v_memorySegment)
        v_noOfInterfaces = delist(self.getList(ctx.v_noOfInterfaces), True)
        v_phoneNo = delist(self.getList(ctx.v_phoneNo), True)
        v_supplier = delist(self.getList(ctx.v_supplier), True)
        v_systemConstant = self.getList(ctx.v_systemConstant)
        v_user = delist(self.getList(ctx.v_user), True)
        v_version = delist(self.getList(ctx.v_version), True)

        ctx.value = model.ModPar(
            comment=comment,
            addr_epk=v_addrEpk,
            calibration_method=v_calibrationMethod,
            cpu_type=v_cpuType,
            customer=v_customer,
            customer_no=v_customerNo,
            ecu=v_ecu,
            ecu_calibration_offset=v_ecuCalibrationOffset,
            epk=v_epk,
            memory_layout=v_memoryLayout,
            memory_segment=v_memorySegment,
            no_of_interfaces=v_noOfInterfaces,
            phone_no=v_phoneNo,
            supplier=v_supplier,
            system_constant=v_systemConstant,
            user=v_user,
            version=v_version,
        )
        self.db.session.add(ctx.value)

    def exitAddrEpk(self, ctx):
        address = ctx.address.value
        ctx.value = model.AddrEpk(address=address)
        self.db.session.add(ctx.value)

    def exitCalibrationMethod(self, ctx):
        method = ctx.method.value
        version_ = ctx.version_.value
        v_calibrationHandle = self.getList(ctx.v_calibrationHandle)
        ctx.value = model.CalibrationMethod(
            method=method, version=version_, calibration_handle=v_calibrationHandle
        )
        self.db.session.add(ctx.value)

    def exitCalibrationHandle(self, ctx):
        handle = self.getList(ctx.handle)
        v_calibrationHandleText = delist(
            self.getList(ctx.v_calibrationHandleText), True
        )
        ctx.value = model.CalibrationHandle(
            handle=handle, calibration_handle_text=v_calibrationHandleText
        )
        self.db.session.add(ctx.value)

    def exitCalibrationHandleText(self, ctx):
        text = ctx.text.value
        ctx.value = model.CalibrationHandleText(text=text)
        self.db.session.add(ctx.value)

    def exitCpuType(self, ctx):
        cPU = ctx.cPU.value
        ctx.value = model.CpuType(cPU=cPU)
        self.db.session.add(ctx.value)

    def exitCustomer(self, ctx):
        customer_ = ctx.customer_.value
        ctx.value = model.Customer(customer=customer_)
        self.db.session.add(ctx.value)

    def exitCustomerNo(self, ctx):
        number_ = ctx.number_.value
        ctx.value = model.CustomerNo(number=number_)
        self.db.session.add(ctx.value)

    def exitEcu(self, ctx):
        controlUnit = ctx.controlUnit.value
        ctx.value = model.Ecu(controlUnit=controlUnit)
        self.db.session.add(ctx.value)

    def exitEcuCalibrationOffset(self, ctx):
        offset = ctx.offset.value
        ctx.value = model.EcuCalibrationOffset(offset=offset)
        self.db.session.add(ctx.value)

    def exitEpk(self, ctx):
        identifier = ctx.identifier.value
        ctx.value = model.Epk(identifier=identifier)
        self.db.session.add(ctx.value)

    def exitMemoryLayout(self, ctx):
        prgType = ctx.prgType.text
        address = ctx.address.value
        size = ctx.size.value
        offset_0 = ctx.offset_0.value
        offset_1 = ctx.offset_1.value
        offset_2 = ctx.offset_2.value
        offset_3 = ctx.offset_3.value
        offset_4 = ctx.offset_4.value

        v_ifData = self.getList(ctx.v_ifData)

        ctx.value = model.MemoryLayout(
            prgType=prgType,
            address=address,
            size=size,
            offset_0=offset_0,
            offset_1=offset_1,
            offset_2=offset_2,
            offset_3=offset_3,
            offset_4=offset_4,
            if_data=v_ifData,
        )
        self.db.session.add(ctx.value)

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

        ctx.value = model.MemorySegment(
            name=name,
            longIdentifier=longIdentifier,
            prgType=prgType,
            memoryType=memoryType,
            attribute=attribute,
            address=address,
            size=size,
            offset_0=offset_0,
            offset_1=offset_1,
            offset_2=offset_2,
            offset_3=offset_3,
            offset_4=offset_4,
            if_data=v_ifData,
        )
        self.db.session.add(ctx.value)

    def exitNoOfInterfaces(self, ctx):
        num = ctx.num.value
        ctx.value = model.NoOfInterfaces(num=num)
        self.db.session.add(ctx.value)

    def exitPhoneNo(self, ctx):
        telnum = ctx.telnum.value
        ctx.value = model.PhoneNo(telnum=telnum)
        self.db.session.add(ctx.value)

    def exitSupplier(self, ctx):
        manufacturer = ctx.manufacturer.value
        ctx.value = model.Supplier(manufacturer=manufacturer)
        self.db.session.add(ctx.value)

    def exitSystemConstant(self, ctx):
        name = ctx.name.value
        value_ = ctx.value_.value
        ctx.value = model.SystemConstant(name=name, value=value_)
        self.db.session.add(ctx.value)

    def exitUser(self, ctx):
        userName = ctx.userName.value
        ctx.value = model.User(userName=userName)
        self.db.session.add(ctx.value)

    def exitRecordLayout(self, ctx):
        name = ctx.name.value

        v_alignmentByte = delist(self.getList(ctx.v_alignmentByte), True)
        v_alignmentFloat32Ieee = delist(self.getList(ctx.v_alignmentFloat32Ieee), True)
        v_alignmentFloat64Ieee = delist(self.getList(ctx.v_alignmentFloat64Ieee), True)
        v_alignmentInt64 = delist(self.getList(ctx.v_alignmentInt64), True)
        v_alignmentLong = delist(self.getList(ctx.v_alignmentLong), True)
        v_alignmentWord = delist(self.getList(ctx.v_alignmentWord), True)
        v_axisPtsX = delist(self.getList(ctx.v_axisPtsX), True)
        v_axisPtsY = delist(self.getList(ctx.v_axisPtsY), True)
        v_axisPtsZ = delist(self.getList(ctx.v_axisPtsZ), True)
        v_axisPts4 = delist(self.getList(ctx.v_axisPts4), True)
        v_axisPts5 = delist(self.getList(ctx.v_axisPts5), True)
        v_axisRescaleX = delist(self.getList(ctx.v_axisRescaleX), True)
        v_axisRescaleY = delist(self.getList(ctx.v_axisRescaleY), True)
        v_axisRescaleZ = delist(self.getList(ctx.v_axisRescaleZ), True)
        v_axisRescale4 = delist(self.getList(ctx.v_axisRescale4), True)
        v_axisRescale5 = delist(self.getList(ctx.v_axisRescale5), True)
        v_distOpX = delist(self.getList(ctx.v_distOpX), True)
        v_distOpY = delist(self.getList(ctx.v_distOpY), True)
        v_distOpZ = delist(self.getList(ctx.v_distOpZ), True)
        v_distOp4 = delist(self.getList(ctx.v_distOp4), True)
        v_distOp5 = delist(self.getList(ctx.v_distOp5), True)
        v_fixNoAxisPtsX = delist(self.getList(ctx.v_fixNoAxisPtsX), True)
        v_fixNoAxisPtsY = delist(self.getList(ctx.v_fixNoAxisPtsY), True)
        v_fixNoAxisPtsZ = delist(self.getList(ctx.v_fixNoAxisPtsZ), True)
        v_fixNoAxisPts4 = delist(self.getList(ctx.v_fixNoAxisPts4), True)
        v_fixNoAxisPts5 = delist(self.getList(ctx.v_fixNoAxisPts5), True)
        v_fncValues = delist(self.getList(ctx.v_fncValues), True)
        v_identification = delist(self.getList(ctx.v_identification), True)
        v_noAxisPtsX = delist(self.getList(ctx.v_noAxisPtsX), True)
        v_noAxisPtsY = delist(self.getList(ctx.v_noAxisPtsY), True)
        v_noAxisPtsZ = delist(self.getList(ctx.v_noAxisPtsZ), True)
        v_noAxisPts4 = delist(self.getList(ctx.v_noAxisPts4), True)
        v_noAxisPts5 = delist(self.getList(ctx.v_noAxisPts5), True)
        v_staticRecordLayout = delist(self.getList(ctx.v_staticRecordLayout), True)
        v_noRescaleX = delist(self.getList(ctx.v_noRescaleX), True)
        v_noRescaleY = delist(self.getList(ctx.v_noRescaleY), True)
        v_noRescaleZ = delist(self.getList(ctx.v_noRescaleZ), True)
        v_noRescale4 = delist(self.getList(ctx.v_noRescale4), True)
        v_noRescale5 = delist(self.getList(ctx.v_noRescale5), True)
        v_offsetX = delist(self.getList(ctx.v_offsetX), True)
        v_offsetY = delist(self.getList(ctx.v_offsetY), True)
        v_offsetZ = delist(self.getList(ctx.v_offsetZ), True)
        v_offset4 = delist(self.getList(ctx.v_offset4), True)
        v_offset5 = delist(self.getList(ctx.v_offset5), True)
        v_reserved = self.getList(ctx.v_reserved)
        v_ripAddrW = delist(self.getList(ctx.v_ripAddrW), True)
        v_ripAddrX = delist(self.getList(ctx.v_ripAddrX), True)
        v_ripAddrY = delist(self.getList(ctx.v_ripAddrY), True)
        v_ripAddrZ = delist(self.getList(ctx.v_ripAddrZ), True)
        v_ripAddr4 = delist(self.getList(ctx.v_ripAddr4), True)
        v_ripAddr5 = delist(self.getList(ctx.v_ripAddr5), True)
        v_shiftOpX = delist(self.getList(ctx.v_shiftOpX), True)
        v_shiftOpY = delist(self.getList(ctx.v_shiftOpY), True)
        v_shiftOpZ = delist(self.getList(ctx.v_shiftOpZ), True)
        v_shiftOp4 = delist(self.getList(ctx.v_shiftOp4), True)
        v_shiftOp5 = delist(self.getList(ctx.v_shiftOp5), True)
        v_srcAddrX = delist(self.getList(ctx.v_srcAddrX), True)
        v_srcAddrY = delist(self.getList(ctx.v_srcAddrY), True)
        v_srcAddrZ = delist(self.getList(ctx.v_srcAddrZ), True)
        v_srcAddr4 = delist(self.getList(ctx.v_srcAddr4), True)
        v_srcAddr5 = delist(self.getList(ctx.v_srcAddr5), True)

        ctx.value = model.RecordLayout(
            name=name,
            alignment_byte=v_alignmentByte,
            alignment_float32_ieee=v_alignmentFloat32Ieee,
            alignment_float64_ieee=v_alignmentFloat64Ieee,
            alignment_int64=v_alignmentInt64,
            alignment_long=v_alignmentLong,
            alignment_word=v_alignmentWord,
            axis_pts_x=v_axisPtsX,
            axis_pts_y=v_axisPtsY,
            axis_pts_z=v_axisPtsZ,
            axis_pts_4=v_axisPts4,
            axis_pts_5=v_axisPts5,
            axis_rescale_x=v_axisRescaleX,
            axis_rescale_y=v_axisRescaleY,
            axis_rescale_z=v_axisRescaleZ,
            axis_rescale_4=v_axisRescale4,
            axis_rescale_5=v_axisRescale5,
            dist_op_x=v_distOpX,
            dist_op_y=v_distOpY,
            dist_op_z=v_distOpZ,
            dist_op_4=v_distOp4,
            dist_op_5=v_distOp5,
            fix_no_axis_pts_x=v_fixNoAxisPtsX,
            fix_no_axis_pts_y=v_fixNoAxisPtsY,
            fix_no_axis_pts_z=v_fixNoAxisPtsZ,
            fix_no_axis_pts_4=v_fixNoAxisPts4,
            fix_no_axis_pts_5=v_fixNoAxisPts5,
            fnc_values=v_fncValues,
            identification=v_identification,
            no_axis_pts_x=v_noAxisPtsX,
            no_axis_pts_y=v_noAxisPtsY,
            no_axis_pts_z=v_noAxisPtsZ,
            no_axis_pts_4=v_noAxisPts4,
            no_axis_pts_5=v_noAxisPts5,
            static_record_layout=v_staticRecordLayout,
            no_rescale_x=v_noRescaleX,
            no_rescale_y=v_noRescaleY,
            no_rescale_z=v_noRescaleZ,
            no_rescale_4=v_noRescale4,
            no_rescale_5=v_noRescale5,
            offset_x=v_offsetX,
            offset_y=v_offsetY,
            offset_z=v_offsetZ,
            offset_4=v_offset4,
            offset_5=v_offset5,
            reserved=v_reserved,
            rip_addr_w=v_ripAddrW,
            rip_addr_x=v_ripAddrX,
            rip_addr_y=v_ripAddrY,
            rip_addr_z=v_ripAddrZ,
            rip_addr_4=v_ripAddr4,
            rip_addr_5=v_ripAddr5,
            shift_op_x=v_shiftOpX,
            shift_op_y=v_shiftOpY,
            shift_op_z=v_shiftOpZ,
            shift_op_4=v_shiftOp4,
            shift_op_5=v_shiftOp5,
            src_addr_x=v_srcAddrX,
            src_addr_y=v_srcAddrY,
            src_addr_z=v_srcAddrZ,
            src_addr_4=v_srcAddr4,
            src_addr_5=v_srcAddr5,
        )
        self.db.session.add(ctx.value)

    def exitAxisPtsX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        ctx.value = model.AxisPtsX(
            position=position,
            datatype=datatype,
            indexIncr=indexIncr,
            addressing=addressing,
        )
        self.db.session.add(ctx.value)

    def exitAxisPtsY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        ctx.value = model.AxisPtsY(
            position=position,
            datatype=datatype,
            indexIncr=indexIncr,
            addressing=addressing,
        )
        self.db.session.add(ctx.value)

    def exitAxisPtsZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        ctx.value = model.AxisPtsZ(
            position=position,
            datatype=datatype,
            indexIncr=indexIncr,
            addressing=addressing,
        )
        self.db.session.add(ctx.value)

    def exitAxisPts4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        ctx.value = model.AxisPts4(
            position=position,
            datatype=datatype,
            indexIncr=indexIncr,
            addressing=addressing,
        )
        self.db.session.add(ctx.value)

    def exitAxisPts5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        ctx.value = model.AxisPts5(
            position=position,
            datatype=datatype,
            indexIncr=indexIncr,
            addressing=addressing,
        )
        self.db.session.add(ctx.value)

    def exitAxisRescaleX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        maxNumberOfRescalePairs = ctx.maxNumberOfRescalePairs.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        ctx.value = model.AxisRescaleX(
            position=position,
            datatype=datatype,
            maxNumberOfRescalePairs=maxNumberOfRescalePairs,
            indexIncr=indexIncr,
            addressing=addressing,
        )
        self.db.session.add(ctx.value)

    def exitAxisRescaleY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        maxNumberOfRescalePairs = ctx.maxNumberOfRescalePairs.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        ctx.value = model.AxisRescaleY(
            position=position,
            datatype=datatype,
            maxNumberOfRescalePairs=maxNumberOfRescalePairs,
            indexIncr=indexIncr,
            addressing=addressing,
        )
        self.db.session.add(ctx.value)

    def exitAxisRescaleZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        maxNumberOfRescalePairs = ctx.maxNumberOfRescalePairs.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        ctx.value = model.AxisRescaleZ(
            position=position,
            datatype=datatype,
            maxNumberOfRescalePairs=maxNumberOfRescalePairs,
            indexIncr=indexIncr,
            addressing=addressing,
        )
        self.db.session.add(ctx.value)

    def exitAxisRescale4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        maxNumberOfRescalePairs = ctx.maxNumberOfRescalePairs.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        ctx.value = model.AxisRescale4(
            position=position,
            datatype=datatype,
            maxNumberOfRescalePairs=maxNumberOfRescalePairs,
            indexIncr=indexIncr,
            addressing=addressing,
        )
        self.db.session.add(ctx.value)

    def exitAxisRescale5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        maxNumberOfRescalePairs = ctx.maxNumberOfRescalePairs.value
        indexIncr = ctx.indexIncr.value
        addressing = ctx.addressing.value
        ctx.value = model.AxisRescale5(
            position=position,
            datatype=datatype,
            maxNumberOfRescalePairs=maxNumberOfRescalePairs,
            indexIncr=indexIncr,
            addressing=addressing,
        )
        self.db.session.add(ctx.value)

    def exitDistOpX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.DistOpX(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitDistOpY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.DistOpY(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitDistOpZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.DistOpZ(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitDistOp4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.DistOp4(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitDistOp5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.DistOp5(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitFixNoAxisPtsX(self, ctx):
        numberOfAxisPoints = ctx.numberOfAxisPoints.value
        ctx.value = model.FixNoAxisPtsX(numberOfAxisPoints=numberOfAxisPoints)
        self.db.session.add(ctx.value)

    def exitFixNoAxisPtsY(self, ctx):
        numberOfAxisPoints = ctx.numberOfAxisPoints.value
        ctx.value = model.FixNoAxisPtsY(numberOfAxisPoints=numberOfAxisPoints)
        self.db.session.add(ctx.value)

    def exitFixNoAxisPtsZ(self, ctx):
        numberOfAxisPoints = ctx.numberOfAxisPoints.value
        ctx.value = model.FixNoAxisPtsZ(numberOfAxisPoints=numberOfAxisPoints)
        self.db.session.add(ctx.value)

    def exitFixNoAxisPts4(self, ctx):
        numberOfAxisPoints = ctx.numberOfAxisPoints.value
        ctx.value = model.FixNoAxisPts4(numberOfAxisPoints=numberOfAxisPoints)
        self.db.session.add(ctx.value)

    def exitFixNoAxisPts5(self, ctx):
        numberOfAxisPoints = ctx.numberOfAxisPoints.value
        ctx.value = model.FixNoAxisPts5(numberOfAxisPoints=numberOfAxisPoints)
        self.db.session.add(ctx.value)

    def exitFncValues(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        indexMode = ctx.indexMode.text
        addresstype = ctx.addresstype.value
        ctx.value = model.FncValues(
            position=position,
            datatype=datatype,
            indexMode=indexMode,
            addresstype=addresstype,
        )
        self.db.session.add(ctx.value)

    def exitIdentification(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.Identification(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitNoAxisPtsX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.NoAxisPtsX(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitNoAxisPtsY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.NoAxisPtsY(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitNoAxisPtsZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.NoAxisPtsZ(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitNoAxisPts4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.NoAxisPts4(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitNoAxisPts5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.NoAxisPts5(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitStaticRecordLayout(self, ctx):
        ctx.value = model.StaticRecordLayout()
        self.db.session.add(ctx.value)

    def exitNoRescaleX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.NoRescaleX(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitNoRescaleY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.NoRescaleY(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitNoRescaleZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.NoRescaleZ(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitNoRescale4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.NoRescale4(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitNoRescale5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.NoRescale5(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitOffsetX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.OffsetX(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitOffsetY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.OffsetY(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitOffsetZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.OffsetZ(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitOffset4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.Offset4(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitOffset5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.Offset5(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitReserved(self, ctx):
        position = ctx.position.value
        dataSize = ctx.dataSize_.value
        ctx.value = model.Reserved(position=position, dataSize=dataSize)
        self.db.session.add(ctx.value)

    def exitRipAddrW(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.RipAddrW(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitRipAddrX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.RipAddrX(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitRipAddrY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.RipAddrY(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitRipAddrZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.RipAddrZ(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitRipAddr4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.RipAddr4(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitRipAddr5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.RipAddr5(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitShiftOpX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.ShiftOpX(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitShiftOpY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.ShiftOpY(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitShiftOpZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.ShiftOpZ(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitShiftOp4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.ShiftOp4(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitShiftOp5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.ShiftOp5(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitSrcAddrX(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.SrcAddrX(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitSrcAddrY(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.SrcAddrY(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitSrcAddrZ(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.SrcAddrZ(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitSrcAddr4(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.SrcAddr4(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitSrcAddr5(self, ctx):
        position = ctx.position.value
        datatype = ctx.datatype.value
        ctx.value = model.SrcAddr5(position=position, datatype=datatype)
        self.db.session.add(ctx.value)

    def exitUnit(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        display = ctx.display.value
        type_ = ctx.type_.text

        v_siExponents = delist(self.getList(ctx.v_siExponents), True)
        v_refUnit = delist(self.getList(ctx.v_refUnit), True)
        v_unitConversion = delist(self.getList(ctx.v_unitConversion), True)

        ctx.value = model.Unit(
            name=name,
            longIdentifier=longIdentifier,
            display=display,
            type=type_,
            si_exponents=v_siExponents,
            ref_unit=v_refUnit,
            unit_conversion=v_unitConversion,
        )
        self.db.session.add(ctx.value)

    def exitSiExponents(self, ctx):
        length = ctx.length.value
        mass = ctx.mass.value
        time = ctx.time.value
        electricCurrent = ctx.electricCurrent.value
        temperature = ctx.temperature.value
        amountOfSubstance = ctx.amountOfSubstance.value
        luminousIntensity = ctx.luminousIntensity.value
        ctx.value = model.SiExponents(
            length=length,
            mass=mass,
            time=time,
            electricCurrent=electricCurrent,
            temperature=temperature,
            amountOfSubstance=amountOfSubstance,
            luminousIntensity=luminousIntensity,
        )
        self.db.session.add(ctx.value)

    def exitUnitConversion(self, ctx):
        gradient = ctx.gradient.value
        offset = ctx.offset.value
        ctx.value = model.UnitConversion(gradient=gradient, offset=offset)
        self.db.session.add(ctx.value)

    def exitUserRights(self, ctx):
        userLevelId = ctx.userLevelId.value

        v_readOnly = delist(self.getList(ctx.v_readOnly), True)
        v_refGroup = self.getList(ctx.v_refGroup)

        ctx.value = model.UserRights(
            userLevelId=userLevelId, read_only=v_readOnly, ref_group=v_refGroup
        )
        self.db.session.add(ctx.value)

    def exitRefGroup(self, ctx):
        identifier = self.getList(ctx.identifier)
        ctx.value = model.RefGroup(identifier=identifier)
        self.db.session.add(ctx.value)

    def exitVariantCoding(self, ctx):
        v_varCharacteristic = self.getList(ctx.v_varCharacteristic)
        v_varCriterion = self.getList(ctx.v_varCriterion)
        v_varForbiddenComb = self.getList(ctx.v_varForbiddenComb)
        v_varNaming = delist(self.getList(ctx.v_varNaming), True)
        v_varSeparator = delist(self.getList(ctx.v_varSeparator), True)

        """
        var_characteristics = relationship("VarCharacteristic", back_populates = "variant_coding", uselist = True)
        var_criterions = relationship("VarCriterion", back_populates = "variant_coding", uselist = True)
        var_forbidden_comb = relationship("VarForbiddenComb", back_populates = "variant_coding", uselist = False)
        var_naming = relationship("VarNaming", back_populates = "variant_coding", uselist = False)
        var_separator = relationship("VarSeparator", back_populates = "variant_coding", uselist = False)
        """
        ctx.value = model.VariantCoding(
            var_characteristic=v_varCharacteristic,
            var_criterion=v_varCriterion,
            var_forbidden_comb=v_varForbiddenComb,
            var_naming=v_varNaming,
            var_separator=v_varSeparator,
        )
        self.db.session.add(ctx.value)

    def exitVarCharacteristic(self, ctx):
        name = ctx.name.value
        criterionName = self.getList(ctx.criterionName)

        v_varAddress = delist(self.getList(ctx.v_varAddress), True)

        ctx.value = model.VarCharacteristic(
            name=name, criterionName=criterionName, var_address=v_varAddress
        )
        self.db.session.add(ctx.value)

    def exitVarAddress(self, ctx):
        address = self.getList(ctx.address)
        ctx.value = model.VarAddress(address=address)
        self.db.session.add(ctx.value)

    def exitVarCriterion(self, ctx):
        name = ctx.name.value
        longIdentifier = ctx.longIdentifier.value
        value_ = self.getList(ctx.value_)

        v_varMeasurement = delist(self.getList(ctx.v_varMeasurement), True)
        v_varSelectionCharacteristic = delist(
            self.getList(ctx.v_varSelectionCharacteristic), True
        )

        ctx.value = model.VarCriterion(
            name=name,
            longIdentifier=longIdentifier,
            value=value_,
            var_measurement=v_varMeasurement,
            var_selection_characteristic=v_varSelectionCharacteristic,
        )
        self.db.session.add(ctx.value)

    def exitVarMeasurement(self, ctx):
        name = ctx.name.value
        ctx.value = model.VarMeasurement(name=name)
        self.db.session.add(ctx.value)

    def exitVarSelectionCharacteristic(self, ctx):
        name = ctx.name.value
        ctx.value = model.VarSelectionCharacteristic(name=name)
        self.db.session.add(ctx.value)

    def exitVarForbiddenComb(self, ctx):
        criterionName = self.getList(ctx.criterionName)
        criterionValue = self.getList(ctx.criterionValue)
        pairs = zip(criterionName, criterionValue)
        ctx.value = model.VarForbiddenComb()
        for name, value in pairs:
            pair = model.VarForbiddedCombPair(criterionName=name, criterionValue=value)
            self.db.session.add(pair)
            ctx.value.pairs.append(pair)
        self.db.session.add(ctx.value)

    def exitVarNaming(self, ctx):
        tag = ctx.tag.text
        ctx.value = model.VarNaming(tag=tag)
        self.db.session.add(ctx.value)

    def exitVarSeparator(self, ctx):
        separator = ctx.separator.value
        ctx.value = model.VarSeparator(separator=separator)
        self.db.session.add(ctx.value)

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
