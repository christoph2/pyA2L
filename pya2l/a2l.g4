/*
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2021 by Christoph Schueler <cpu12.gems@googlemail.com>

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
*/


//
//  AUTOMATICALLY GENERATED FILE -- DO NOT MODIFY !!!
//

grammar a2l;


a2lFile:
    asap2Version?
    a2mlVersion?
    project
    ;

alignmentByte:
     'ALIGNMENT_BYTE'
    alignmentBorder = integerValue
    ;

alignmentFloat16Ieee:
     'ALIGNMENT_FLOAT16_IEEE'
    alignmentBorder = integerValue
    ;

alignmentFloat32Ieee:
     'ALIGNMENT_FLOAT32_IEEE'
    alignmentBorder = integerValue
    ;

alignmentFloat64Ieee:
     'ALIGNMENT_FLOAT64_IEEE'
    alignmentBorder = integerValue
    ;

alignmentInt64:
     'ALIGNMENT_INT64'
    alignmentBorder = integerValue
    ;

alignmentLong:
     'ALIGNMENT_LONG'
    alignmentBorder = integerValue
    ;

alignmentWord:
     'ALIGNMENT_WORD'
    alignmentBorder = integerValue
    ;

annotation:
    BEGIN 'ANNOTATION'
    /* optional part */

    (
        v_annotationLabel += annotationLabel |
        v_annotationOrigin += annotationOrigin |
        v_annotationText += annotationText
    )*
    END 'ANNOTATION'
    ;

annotationLabel:
     'ANNOTATION_LABEL'
    label = stringValue
    ;

annotationOrigin:
     'ANNOTATION_ORIGIN'
    origin = stringValue
    ;

annotationText:
    BEGIN 'ANNOTATION_TEXT'
    (text += stringValue)*
    END 'ANNOTATION_TEXT'
    ;

bitMask:
     'BIT_MASK'
    mask = integerValue
    ;

byteOrder:
     'BYTE_ORDER'
    byteOrder_ = byteOrderValue
    ;

calibrationAccess:
     'CALIBRATION_ACCESS'
    
    type_ =
    (
        'CALIBRATION' |
        'NO_CALIBRATION' |
        'NOT_IN_MCD_SYSTEM' |
        'OFFLINE_CALIBRATION'
    )

    ;

defaultValue:
     'DEFAULT_VALUE'
    display_string = stringValue
    ;

deposit:
     'DEPOSIT'
    
    mode_ =
    (
        'ABSOLUTE' |
        'DIFFERENCE'
    )

    ;

discrete:
     'DISCRETE'
    ;

displayIdentifier:
     'DISPLAY_IDENTIFIER'
    display_name = identifierValue
    ;

ecuAddressExtension:
     'ECU_ADDRESS_EXTENSION'
    extension = integerValue
    ;

extendedLimits:
     'EXTENDED_LIMITS'
    lowerLimit = numericValue
    upperLimit = numericValue
    ;

format_:
     'FORMAT'
    formatString = stringValue
    ;

functionList:
    BEGIN 'FUNCTION_LIST'
    (name += identifierValue)*
    END 'FUNCTION_LIST'
    ;

guardRails:
     'GUARD_RAILS'
    ;

ifData:
    BEGIN 'IF_DATA'
    name = identifierValue
    END 'IF_DATA'
    ;

matrixDim:
     'MATRIX_DIM'
    xDim = integerValue
    (yDim = integerValue)?
    (zDim = integerValue)?
    ;

maxRefresh:
     'MAX_REFRESH'
    scalingUnit = integerValue
    rate = integerValue
    ;

monotony:
     'MONOTONY'
    
    monotony_ =
    (
        'MON_DECREASE' |
        'MON_INCREASE' |
        'STRICT_DECREASE' |
        'STRICT_INCREASE' |
        'MONOTONOUS' |
        'STRICT_MON' |
        'NOT_MON'
    )

    ;

physUnit:
     'PHYS_UNIT'
    unit_ = stringValue
    ;

readOnly:
     'READ_ONLY'
    ;

refCharacteristic:
    BEGIN 'REF_CHARACTERISTIC'
    (identifier += identifierValue)*
    END 'REF_CHARACTERISTIC'
    ;

refMemorySegment:
     'REF_MEMORY_SEGMENT'
    name = identifierValue
    ;

refUnit:
     'REF_UNIT'
    unit_ = identifierValue
    ;

stepSize:
     'STEP_SIZE'
    stepSize_ = numericValue
    ;

symbolLink:
     'SYMBOL_LINK'
    symbolName = stringValue
    offset = integerValue
    ;

version:
     'VERSION'
    versionIdentifier = stringValue
    ;

asap2Version:
     'ASAP2_VERSION'
    versionNo = integerValue
    upgradeNo = integerValue
    ;

a2mlVersion:
     'A2ML_VERSION'
    versionNo = integerValue
    upgradeNo = integerValue
    ;

project:
    BEGIN 'PROJECT'
    name = identifierValue
    longIdentifier = stringValue
    /* optional part */

    (
        v_header += header |
        v_module += module
    )*
    END 'PROJECT'
    ;

header:
    BEGIN 'HEADER'
    comment = stringValue
    /* optional part */

    (
        v_projectNo += projectNo |
        v_version += version
    )*
    END 'HEADER'
    ;

projectNo:
     'PROJECT_NO'
    projectNumber = identifierValue
    ;

module:
    BEGIN 'MODULE'
    name = identifierValue
    longIdentifier = stringValue
    /* optional part */

    (
        v_a2ml += a2ml |
        v_axisPts += axisPts |
        v_characteristic += characteristic |
        v_compuMethod += compuMethod |
        v_compuTab += compuTab |
        v_compuVtab += compuVtab |
        v_compuVtabRange += compuVtabRange |
        v_frame += frame |
        v_function += function |
        v_group += group |
        v_ifData += ifData |
        v_instance += instance |
        v_measurement += measurement |
        v_modCommon += modCommon |
        v_modPar += modPar |
        v_recordLayout += recordLayout |
        v_typedefMeasurement += typedefMeasurement |
        v_typedefStructure += typedefStructure |
        v_unit += unit |
        v_userRights += userRights |
        v_variantCoding += variantCoding
    )*
    END 'MODULE'
    ;

a2ml:
    BEGIN 'A2ML'
    END 'A2ML'
    ;

axisPts:
    BEGIN 'AXIS_PTS'
    name = identifierValue
    longIdentifier = stringValue
    address = integerValue
    inputQuantity = identifierValue
    depositAttr = identifierValue
    maxDiff = numericValue
    conversion = identifierValue
    maxAxisPoints = integerValue
    lowerLimit = numericValue
    upperLimit = numericValue
    /* optional part */

    (
        v_annotation += annotation |
        v_byteOrder += byteOrder |
        v_calibrationAccess += calibrationAccess |
        v_deposit += deposit |
        v_displayIdentifier += displayIdentifier |
        v_ecuAddressExtension += ecuAddressExtension |
        v_extendedLimits += extendedLimits |
        v_format_ += format_ |
        v_functionList += functionList |
        v_guardRails += guardRails |
        v_ifData += ifData |
        v_monotony += monotony |
        v_physUnit += physUnit |
        v_readOnly += readOnly |
        v_refMemorySegment += refMemorySegment |
        v_stepSize += stepSize |
        v_symbolLink += symbolLink
    )*
    END 'AXIS_PTS'
    ;

characteristic:
    BEGIN 'CHARACTERISTIC'
    name = identifierValue
    longIdentifier = stringValue
    
    type_ =
    (
        'ASCII' |
        'CURVE' |
        'MAP' |
        'CUBOID' |
        'CUBE_4' |
        'CUBE_5' |
        'VAL_BLK' |
        'VALUE'
    )

    address = integerValue
    deposit_ = identifierValue
    maxDiff = numericValue
    conversion = identifierValue
    lowerLimit = numericValue
    upperLimit = numericValue
    /* optional part */

    (
        v_annotation += annotation |
        v_axisDescr += axisDescr |
        v_bitMask += bitMask |
        v_byteOrder += byteOrder |
        v_calibrationAccess += calibrationAccess |
        v_comparisonQuantity += comparisonQuantity |
        v_dependentCharacteristic += dependentCharacteristic |
        v_discrete += discrete |
        v_displayIdentifier += displayIdentifier |
        v_ecuAddressExtension += ecuAddressExtension |
        v_extendedLimits += extendedLimits |
        v_format_ += format_ |
        v_functionList += functionList |
        v_guardRails += guardRails |
        v_ifData += ifData |
        v_mapList += mapList |
        v_matrixDim += matrixDim |
        v_maxRefresh += maxRefresh |
        v_number += number |
        v_physUnit += physUnit |
        v_readOnly += readOnly |
        v_refMemorySegment += refMemorySegment |
        v_stepSize += stepSize |
        v_symbolLink += symbolLink |
        v_virtualCharacteristic += virtualCharacteristic
    )*
    END 'CHARACTERISTIC'
    ;

axisDescr:
    BEGIN 'AXIS_DESCR'
    
    attribute =
    (
        'CURVE_AXIS' |
        'COM_AXIS' |
        'FIX_AXIS' |
        'RES_AXIS' |
        'STD_AXIS'
    )

    inputQuantity = identifierValue
    conversion = identifierValue
    maxAxisPoints = integerValue
    lowerLimit = numericValue
    upperLimit = numericValue
    /* optional part */

    (
        v_annotation += annotation |
        v_axisPtsRef += axisPtsRef |
        v_byteOrder += byteOrder |
        v_curveAxisRef += curveAxisRef |
        v_deposit += deposit |
        v_extendedLimits += extendedLimits |
        v_fixAxisPar += fixAxisPar |
        v_fixAxisParDist += fixAxisParDist |
        v_fixAxisParList += fixAxisParList |
        v_format_ += format_ |
        v_maxGrad += maxGrad |
        v_monotony += monotony |
        v_physUnit += physUnit |
        v_readOnly += readOnly |
        v_stepSize += stepSize
    )*
    END 'AXIS_DESCR'
    ;

axisPtsRef:
     'AXIS_PTS_REF'
    axisPoints = identifierValue
    ;

curveAxisRef:
     'CURVE_AXIS_REF'
    curveAxis = identifierValue
    ;

fixAxisPar:
     'FIX_AXIS_PAR'
    offset = integerValue
    shift = integerValue
    numberapo = integerValue
    ;

fixAxisParDist:
     'FIX_AXIS_PAR_DIST'
    offset = integerValue
    distance = integerValue
    numberapo = integerValue
    ;

fixAxisParList:
    BEGIN 'FIX_AXIS_PAR_LIST'
    (axisPts_Value += numericValue)*
    END 'FIX_AXIS_PAR_LIST'
    ;

maxGrad:
     'MAX_GRAD'
    maxGradient = numericValue
    ;

comparisonQuantity:
     'COMPARISON_QUANTITY'
    name = identifierValue
    ;

dependentCharacteristic:
    BEGIN 'DEPENDENT_CHARACTERISTIC'
    formula_ = stringValue
    (characteristic_ += identifierValue)*
    END 'DEPENDENT_CHARACTERISTIC'
    ;

mapList:
    BEGIN 'MAP_LIST'
    (name += identifierValue)*
    END 'MAP_LIST'
    ;

number:
     'NUMBER'
    number_ = integerValue
    ;

virtualCharacteristic:
    BEGIN 'VIRTUAL_CHARACTERISTIC'
    formula_ = stringValue
    (characteristic_ += identifierValue)*
    END 'VIRTUAL_CHARACTERISTIC'
    ;

compuMethod:
    BEGIN 'COMPU_METHOD'
    name = identifierValue
    longIdentifier = stringValue
    
    conversionType =
    (
        'IDENTICAL' |
        'FORM' |
        'LINEAR' |
        'RAT_FUNC' |
        'TAB_INTP' |
        'TAB_NOINTP' |
        'TAB_VERB'
    )

    format__ = stringValue
    unit_ = stringValue
    /* optional part */

    (
        v_coeffs += coeffs |
        v_coeffsLinear += coeffsLinear |
        v_compuTabRef += compuTabRef |
        v_formula += formula |
        v_refUnit += refUnit |
        v_statusStringRef += statusStringRef
    )*
    END 'COMPU_METHOD'
    ;

coeffs:
     'COEFFS'
    a = numericValue
    b = numericValue
    c = numericValue
    d = numericValue
    e = numericValue
    f = numericValue
    ;

coeffsLinear:
     'COEFFS_LINEAR'
    a = numericValue
    b = numericValue
    ;

compuTabRef:
     'COMPU_TAB_REF'
    conversionTable = identifierValue
    ;

formula:
    BEGIN 'FORMULA'
    f_x = stringValue
    /* optional part */

    (
        v_formulaInv += formulaInv
    )*
    END 'FORMULA'
    ;

formulaInv:
     'FORMULA_INV'
    g_x = stringValue
    ;

statusStringRef:
     'STATUS_STRING_REF'
    conversionTable = identifierValue
    ;

compuTab:
    BEGIN 'COMPU_TAB'
    name = identifierValue
    longIdentifier = stringValue
    
    conversionType =
    (
        'TAB_INTP' |
        'TAB_NOINTP'
    )

    numberValuePairs = integerValue
    (inVal += numericValue outVal += numericValue)*
    /* optional part */

    (
        v_defaultValue += defaultValue |
        v_defaultValueNumeric += defaultValueNumeric
    )*
    END 'COMPU_TAB'
    ;

defaultValueNumeric:
     'DEFAULT_VALUE_NUMERIC'
    display_value = numericValue
    ;

compuVtab:
    BEGIN 'COMPU_VTAB'
    name = identifierValue
    longIdentifier = stringValue
    
    conversionType =
        'TAB_VERB'

    numberValuePairs = integerValue
    (inVal += numericValue outVal += stringValue)*
    /* optional part */

    (
        v_defaultValue += defaultValue
    )*
    END 'COMPU_VTAB'
    ;

compuVtabRange:
    BEGIN 'COMPU_VTAB_RANGE'
    name = identifierValue
    longIdentifier = stringValue
    numberValueTriples = integerValue
    (inValMin += numericValue inValMax += numericValue outVal += stringValue)*
    /* optional part */

    (
        v_defaultValue += defaultValue
    )*
    END 'COMPU_VTAB_RANGE'
    ;

frame:
    BEGIN 'FRAME'
    name = identifierValue
    longIdentifier = stringValue
    scalingUnit = integerValue
    rate = integerValue
    /* optional part */

    (
        v_frameMeasurement += frameMeasurement |
        v_ifData += ifData
    )*
    END 'FRAME'
    ;

frameMeasurement:
     'FRAME_MEASUREMENT'
    (identifier += identifierValue)*
    ;

function:
    BEGIN 'FUNCTION'
    name = identifierValue
    longIdentifier = stringValue
    /* optional part */

    (
        v_annotation += annotation |
        v_defCharacteristic += defCharacteristic |
        v_functionVersion += functionVersion |
        v_ifData += ifData |
        v_inMeasurement += inMeasurement |
        v_locMeasurement += locMeasurement |
        v_outMeasurement += outMeasurement |
        v_refCharacteristic += refCharacteristic |
        v_subFunction += subFunction
    )*
    END 'FUNCTION'
    ;

defCharacteristic:
    BEGIN 'DEF_CHARACTERISTIC'
    (identifier += identifierValue)*
    END 'DEF_CHARACTERISTIC'
    ;

functionVersion:
     'FUNCTION_VERSION'
    versionIdentifier = stringValue
    ;

inMeasurement:
    BEGIN 'IN_MEASUREMENT'
    (identifier += identifierValue)*
    END 'IN_MEASUREMENT'
    ;

locMeasurement:
    BEGIN 'LOC_MEASUREMENT'
    (identifier += identifierValue)*
    END 'LOC_MEASUREMENT'
    ;

outMeasurement:
    BEGIN 'OUT_MEASUREMENT'
    (identifier += identifierValue)*
    END 'OUT_MEASUREMENT'
    ;

subFunction:
    BEGIN 'SUB_FUNCTION'
    (identifier += identifierValue)*
    END 'SUB_FUNCTION'
    ;

group:
    BEGIN 'GROUP'
    groupName = identifierValue
    groupLongIdentifier = stringValue
    /* optional part */

    (
        v_annotation += annotation |
        v_functionList += functionList |
        v_ifData += ifData |
        v_refCharacteristic += refCharacteristic |
        v_refMeasurement += refMeasurement |
        v_root += root |
        v_subGroup += subGroup
    )*
    END 'GROUP'
    ;

refMeasurement:
    BEGIN 'REF_MEASUREMENT'
    (identifier += identifierValue)*
    END 'REF_MEASUREMENT'
    ;

root:
     'ROOT'
    ;

subGroup:
    BEGIN 'SUB_GROUP'
    (identifier += identifierValue)*
    END 'SUB_GROUP'
    ;

instance:
    BEGIN 'INSTANCE'
    name = identifierValue
    longIdentifier = stringValue
    typeName = identifierValue
    address = integerValue
    /* optional part */

    (
        v_ifData += ifData
    )*
    END 'INSTANCE'
    ;

measurement:
    BEGIN 'MEASUREMENT'
    name = identifierValue
    longIdentifier = stringValue
    datatype = dataType
    conversion = identifierValue
    resolution = integerValue
    accuracy = numericValue
    lowerLimit = numericValue
    upperLimit = numericValue
    /* optional part */

    (
        v_annotation += annotation |
        v_arraySize += arraySize |
        v_bitMask += bitMask |
        v_bitOperation += bitOperation |
        v_byteOrder += byteOrder |
        v_discrete += discrete |
        v_displayIdentifier += displayIdentifier |
        v_ecuAddress += ecuAddress |
        v_ecuAddressExtension += ecuAddressExtension |
        v_errorMask += errorMask |
        v_format_ += format_ |
        v_functionList += functionList |
        v_ifData += ifData |
        v_layout += layout |
        v_matrixDim += matrixDim |
        v_maxRefresh += maxRefresh |
        v_physUnit += physUnit |
        v_readWrite += readWrite |
        v_refMemorySegment += refMemorySegment |
        v_symbolLink += symbolLink |
        v_virtual += virtual
    )*
    END 'MEASUREMENT'
    ;

arraySize:
     'ARRAY_SIZE'
    number_ = integerValue
    ;

bitOperation:
    BEGIN 'BIT_OPERATION'
    /* optional part */

    (
        v_leftShift += leftShift |
        v_rightShift += rightShift |
        v_signExtend += signExtend
    )*
    END 'BIT_OPERATION'
    ;

leftShift:
     'LEFT_SHIFT'
    bitcount = integerValue
    ;

rightShift:
     'RIGHT_SHIFT'
    bitcount = integerValue
    ;

signExtend:
     'SIGN_EXTEND'
    ;

ecuAddress:
     'ECU_ADDRESS'
    address = integerValue
    ;

errorMask:
     'ERROR_MASK'
    mask = integerValue
    ;

layout:
     'LAYOUT'
    
    indexMode =
    (
        'ROW_DIR' |
        'COLUMN_DIR'
    )

    ;

readWrite:
     'READ_WRITE'
    ;

virtual:
    BEGIN 'VIRTUAL'
    (measuringChannel += identifierValue)*
    END 'VIRTUAL'
    ;

modCommon:
    BEGIN 'MOD_COMMON'
    comment = stringValue
    /* optional part */

    (
        v_alignmentByte += alignmentByte |
        v_alignmentFloat16Ieee += alignmentFloat16Ieee |
        v_alignmentFloat32Ieee += alignmentFloat32Ieee |
        v_alignmentFloat64Ieee += alignmentFloat64Ieee |
        v_alignmentInt64 += alignmentInt64 |
        v_alignmentLong += alignmentLong |
        v_alignmentWord += alignmentWord |
        v_byteOrder += byteOrder |
        v_dataSize += dataSize |
        v_deposit += deposit |
        v_sRecLayout += sRecLayout
    )*
    END 'MOD_COMMON'
    ;

dataSize:
     'DATA_SIZE'
    size = integerValue
    ;

sRecLayout:
     'S_REC_LAYOUT'
    name = identifierValue
    ;

modPar:
    BEGIN 'MOD_PAR'
    comment = stringValue
    /* optional part */

    (
        v_addrEpk += addrEpk |
        v_calibrationMethod += calibrationMethod |
        v_cpuType += cpuType |
        v_customer += customer |
        v_customerNo += customerNo |
        v_ecu += ecu |
        v_ecuCalibrationOffset += ecuCalibrationOffset |
        v_epk += epk |
        v_memoryLayout += memoryLayout |
        v_memorySegment += memorySegment |
        v_noOfInterfaces += noOfInterfaces |
        v_phoneNo += phoneNo |
        v_supplier += supplier |
        v_systemConstant += systemConstant |
        v_user += user |
        v_version += version
    )*
    END 'MOD_PAR'
    ;

addrEpk:
     'ADDR_EPK'
    address = integerValue
    ;

calibrationMethod:
    BEGIN 'CALIBRATION_METHOD'
    method = stringValue
    version_ = integerValue
    /* optional part */

    (
        v_calibrationHandle += calibrationHandle
    )*
    END 'CALIBRATION_METHOD'
    ;

calibrationHandle:
    BEGIN 'CALIBRATION_HANDLE'
    (handle += integerValue)*
    /* optional part */

    (
        v_calibrationHandleText += calibrationHandleText
    )*
    END 'CALIBRATION_HANDLE'
    ;

calibrationHandleText:
     'CALIBRATION_HANDLE_TEXT'
    text = stringValue
    ;

cpuType:
     'CPU_TYPE'
    cPU = stringValue
    ;

customer:
     'CUSTOMER'
    customer_ = stringValue
    ;

customerNo:
     'CUSTOMER_NO'
    number_ = stringValue
    ;

ecu:
     'ECU'
    controlUnit = stringValue
    ;

ecuCalibrationOffset:
     'ECU_CALIBRATION_OFFSET'
    offset = integerValue
    ;

epk:
     'EPK'
    identifier = stringValue
    ;

memoryLayout:
    BEGIN 'MEMORY_LAYOUT'
    
    prgType =
    (
        'PRG_CODE' |
        'PRG_DATA' |
        'PRG_RESERVED'
    )

    address = integerValue
    size = integerValue
    offset_0 = integerValue
    offset_1 = integerValue
    offset_2 = integerValue
    offset_3 = integerValue
    offset_4 = integerValue
    /* optional part */

    (
        v_ifData += ifData
    )*
    END 'MEMORY_LAYOUT'
    ;

memorySegment:
    BEGIN 'MEMORY_SEGMENT'
    name = identifierValue
    longIdentifier = stringValue
    
    prgType =
    (
        'CALIBRATION_VARIABLES' |
        'CODE' |
        'DATA' |
        'EXCLUDE_FROM_FLASH' |
        'OFFLINE_DATA' |
        'RESERVED' |
        'SERAM' |
        'VARIABLES'
    )

    
    memoryType =
    (
        'EEPROM' |
        'EPROM' |
        'FLASH' |
        'RAM' |
        'ROM' |
        'REGISTER'
    )

    
    attribute =
    (
        'INTERN' |
        'EXTERN'
    )

    address = integerValue
    size = integerValue
    offset_0 = integerValue
    offset_1 = integerValue
    offset_2 = integerValue
    offset_3 = integerValue
    offset_4 = integerValue
    /* optional part */

    (
        v_ifData += ifData
    )*
    END 'MEMORY_SEGMENT'
    ;

noOfInterfaces:
     'NO_OF_INTERFACES'
    num = integerValue
    ;

phoneNo:
     'PHONE_NO'
    telnum = stringValue
    ;

supplier:
     'SUPPLIER'
    manufacturer = stringValue
    ;

systemConstant:
     'SYSTEM_CONSTANT'
    name = stringValue
    value_ = stringValue
    ;

user:
     'USER'
    userName = stringValue
    ;

recordLayout:
    BEGIN 'RECORD_LAYOUT'
    name = identifierValue
    /* optional part */

    (
        v_alignmentByte += alignmentByte |
        v_alignmentFloat16Ieee += alignmentFloat16Ieee |
        v_alignmentFloat32Ieee += alignmentFloat32Ieee |
        v_alignmentFloat64Ieee += alignmentFloat64Ieee |
        v_alignmentInt64 += alignmentInt64 |
        v_alignmentLong += alignmentLong |
        v_alignmentWord += alignmentWord |
        v_axisPtsX += axisPtsX |
        v_axisPtsY += axisPtsY |
        v_axisPtsZ += axisPtsZ |
        v_axisPts4 += axisPts4 |
        v_axisPts5 += axisPts5 |
        v_axisRescaleX += axisRescaleX |
        v_axisRescaleY += axisRescaleY |
        v_axisRescaleZ += axisRescaleZ |
        v_axisRescale4 += axisRescale4 |
        v_axisRescale5 += axisRescale5 |
        v_distOpX += distOpX |
        v_distOpY += distOpY |
        v_distOpZ += distOpZ |
        v_distOp4 += distOp4 |
        v_distOp5 += distOp5 |
        v_fixNoAxisPtsX += fixNoAxisPtsX |
        v_fixNoAxisPtsY += fixNoAxisPtsY |
        v_fixNoAxisPtsZ += fixNoAxisPtsZ |
        v_fixNoAxisPts4 += fixNoAxisPts4 |
        v_fixNoAxisPts5 += fixNoAxisPts5 |
        v_fncValues += fncValues |
        v_identification += identification |
        v_noAxisPtsX += noAxisPtsX |
        v_noAxisPtsY += noAxisPtsY |
        v_noAxisPtsZ += noAxisPtsZ |
        v_noAxisPts4 += noAxisPts4 |
        v_noAxisPts5 += noAxisPts5 |
        v_staticRecordLayout += staticRecordLayout |
        v_noRescaleX += noRescaleX |
        v_noRescaleY += noRescaleY |
        v_noRescaleZ += noRescaleZ |
        v_noRescale4 += noRescale4 |
        v_noRescale5 += noRescale5 |
        v_offsetX += offsetX |
        v_offsetY += offsetY |
        v_offsetZ += offsetZ |
        v_offset4 += offset4 |
        v_offset5 += offset5 |
        v_reserved += reserved |
        v_ripAddrW += ripAddrW |
        v_ripAddrX += ripAddrX |
        v_ripAddrY += ripAddrY |
        v_ripAddrZ += ripAddrZ |
        v_ripAddr4 += ripAddr4 |
        v_ripAddr5 += ripAddr5 |
        v_shiftOpX += shiftOpX |
        v_shiftOpY += shiftOpY |
        v_shiftOpZ += shiftOpZ |
        v_shiftOp4 += shiftOp4 |
        v_shiftOp5 += shiftOp5 |
        v_srcAddrX += srcAddrX |
        v_srcAddrY += srcAddrY |
        v_srcAddrZ += srcAddrZ |
        v_srcAddr4 += srcAddr4 |
        v_srcAddr5 += srcAddr5
    )*
    END 'RECORD_LAYOUT'
    ;

axisPtsX:
     'AXIS_PTS_X'
    position = integerValue
    datatype = dataType
    indexIncr = indexorder
    addressing = addrtype
    ;

axisPtsY:
     'AXIS_PTS_Y'
    position = integerValue
    datatype = dataType
    indexIncr = indexorder
    addressing = addrtype
    ;

axisPtsZ:
     'AXIS_PTS_Z'
    position = integerValue
    datatype = dataType
    indexIncr = indexorder
    addressing = addrtype
    ;

axisPts4:
     'AXIS_PTS_4'
    position = integerValue
    datatype = dataType
    indexIncr = indexorder
    addressing = addrtype
    ;

axisPts5:
     'AXIS_PTS_5'
    position = integerValue
    datatype = dataType
    indexIncr = indexorder
    addressing = addrtype
    ;

axisRescaleX:
     'AXIS_RESCALE_X'
    position = integerValue
    datatype = dataType
    maxNumberOfRescalePairs = integerValue
    indexIncr = indexorder
    addressing = addrtype
    ;

axisRescaleY:
     'AXIS_RESCALE_Y'
    position = integerValue
    datatype = dataType
    maxNumberOfRescalePairs = integerValue
    indexIncr = indexorder
    addressing = addrtype
    ;

axisRescaleZ:
     'AXIS_RESCALE_Z'
    position = integerValue
    datatype = dataType
    maxNumberOfRescalePairs = integerValue
    indexIncr = indexorder
    addressing = addrtype
    ;

axisRescale4:
     'AXIS_RESCALE_4'
    position = integerValue
    datatype = dataType
    maxNumberOfRescalePairs = integerValue
    indexIncr = indexorder
    addressing = addrtype
    ;

axisRescale5:
     'AXIS_RESCALE_5'
    position = integerValue
    datatype = dataType
    maxNumberOfRescalePairs = integerValue
    indexIncr = indexorder
    addressing = addrtype
    ;

distOpX:
     'DIST_OP_X'
    position = integerValue
    datatype = dataType
    ;

distOpY:
     'DIST_OP_Y'
    position = integerValue
    datatype = dataType
    ;

distOpZ:
     'DIST_OP_Z'
    position = integerValue
    datatype = dataType
    ;

distOp4:
     'DIST_OP_4'
    position = integerValue
    datatype = dataType
    ;

distOp5:
     'DIST_OP_5'
    position = integerValue
    datatype = dataType
    ;

fixNoAxisPtsX:
     'FIX_NO_AXIS_PTS_X'
    numberOfAxisPoints = integerValue
    ;

fixNoAxisPtsY:
     'FIX_NO_AXIS_PTS_Y'
    numberOfAxisPoints = integerValue
    ;

fixNoAxisPtsZ:
     'FIX_NO_AXIS_PTS_Z'
    numberOfAxisPoints = integerValue
    ;

fixNoAxisPts4:
     'FIX_NO_AXIS_PTS_4'
    numberOfAxisPoints = integerValue
    ;

fixNoAxisPts5:
     'FIX_NO_AXIS_PTS_5'
    numberOfAxisPoints = integerValue
    ;

fncValues:
     'FNC_VALUES'
    position = integerValue
    datatype = dataType
    
    indexMode =
    (
        'ALTERNATE_CURVES' |
        'ALTERNATE_WITH_X' |
        'ALTERNATE_WITH_Y' |
        'COLUMN_DIR' |
        'ROW_DIR'
    )

    addresstype = addrtype
    ;

identification:
     'IDENTIFICATION'
    position = integerValue
    datatype = dataType
    ;

noAxisPtsX:
     'NO_AXIS_PTS_X'
    position = integerValue
    datatype = dataType
    ;

noAxisPtsY:
     'NO_AXIS_PTS_Y'
    position = integerValue
    datatype = dataType
    ;

noAxisPtsZ:
     'NO_AXIS_PTS_Z'
    position = integerValue
    datatype = dataType
    ;

noAxisPts4:
     'NO_AXIS_PTS_4'
    position = integerValue
    datatype = dataType
    ;

noAxisPts5:
     'NO_AXIS_PTS_5'
    position = integerValue
    datatype = dataType
    ;

staticRecordLayout:
     'STATIC_RECORD_LAYOUT'
    ;

noRescaleX:
     'NO_RESCALE_X'
    position = integerValue
    datatype = dataType
    ;

noRescaleY:
     'NO_RESCALE_Y'
    position = integerValue
    datatype = dataType
    ;

noRescaleZ:
     'NO_RESCALE_Z'
    position = integerValue
    datatype = dataType
    ;

noRescale4:
     'NO_RESCALE_4'
    position = integerValue
    datatype = dataType
    ;

noRescale5:
     'NO_RESCALE_5'
    position = integerValue
    datatype = dataType
    ;

offsetX:
     'OFFSET_X'
    position = integerValue
    datatype = dataType
    ;

offsetY:
     'OFFSET_Y'
    position = integerValue
    datatype = dataType
    ;

offsetZ:
     'OFFSET_Z'
    position = integerValue
    datatype = dataType
    ;

offset4:
     'OFFSET_4'
    position = integerValue
    datatype = dataType
    ;

offset5:
     'OFFSET_5'
    position = integerValue
    datatype = dataType
    ;

reserved:
     'RESERVED'
    position = integerValue
    dataSize_ = datasize
    ;

ripAddrW:
     'RIP_ADDR_W'
    position = integerValue
    datatype = dataType
    ;

ripAddrX:
     'RIP_ADDR_X'
    position = integerValue
    datatype = dataType
    ;

ripAddrY:
     'RIP_ADDR_Y'
    position = integerValue
    datatype = dataType
    ;

ripAddrZ:
     'RIP_ADDR_Z'
    position = integerValue
    datatype = dataType
    ;

ripAddr4:
     'RIP_ADDR_4'
    position = integerValue
    datatype = dataType
    ;

ripAddr5:
     'RIP_ADDR_5'
    position = integerValue
    datatype = dataType
    ;

shiftOpX:
     'SHIFT_OP_X'
    position = integerValue
    datatype = dataType
    ;

shiftOpY:
     'SHIFT_OP_Y'
    position = integerValue
    datatype = dataType
    ;

shiftOpZ:
     'SHIFT_OP_Z'
    position = integerValue
    datatype = dataType
    ;

shiftOp4:
     'SHIFT_OP_4'
    position = integerValue
    datatype = dataType
    ;

shiftOp5:
     'SHIFT_OP_5'
    position = integerValue
    datatype = dataType
    ;

srcAddrX:
     'SRC_ADDR_X'
    position = integerValue
    datatype = dataType
    ;

srcAddrY:
     'SRC_ADDR_Y'
    position = integerValue
    datatype = dataType
    ;

srcAddrZ:
     'SRC_ADDR_Z'
    position = integerValue
    datatype = dataType
    ;

srcAddr4:
     'SRC_ADDR_4'
    position = integerValue
    datatype = dataType
    ;

srcAddr5:
     'SRC_ADDR_5'
    position = integerValue
    datatype = dataType
    ;

typedefMeasurement:
    BEGIN 'TYPEDEF_MEASUREMENT'
    name = identifierValue
    longIdentifier = stringValue
    datatype = dataType
    conversion = identifierValue
    resolution = integerValue
    accuracy = numericValue
    lowerLimit = numericValue
    upperLimit = numericValue
    END 'TYPEDEF_MEASUREMENT'
    ;

typedefStructure:
    BEGIN 'TYPEDEF_STRUCTURE'
    name = identifierValue
    longIdentifier = stringValue
    size = integerValue
    link = linkType
    symbol = stringValue
    /* optional part */

    (
        v_structureComponent += structureComponent
    )*
    END 'TYPEDEF_STRUCTURE'
    ;

structureComponent:
    BEGIN 'STRUCTURE_COMPONENT'
    name = identifierValue
    deposit_ = identifierValue
    offset = integerValue
    link = linkType
    symbol = stringValue
    END 'STRUCTURE_COMPONENT'
    ;

unit:
    BEGIN 'UNIT'
    name = identifierValue
    longIdentifier = stringValue
    display = stringValue
    
    type_ =
    (
        'DERIVED' |
        'EXTENDED_SI'
    )

    /* optional part */

    (
        v_siExponents += siExponents |
        v_refUnit += refUnit |
        v_unitConversion += unitConversion
    )*
    END 'UNIT'
    ;

siExponents:
     'SI_EXPONENTS'
    length = integerValue
    mass = integerValue
    time = integerValue
    electricCurrent = integerValue
    temperature = integerValue
    amountOfSubstance = integerValue
    luminousIntensity = integerValue
    ;

unitConversion:
     'UNIT_CONVERSION'
    gradient = numericValue
    offset = numericValue
    ;

userRights:
    BEGIN 'USER_RIGHTS'
    userLevelId = identifierValue
    /* optional part */

    (
        v_readOnly += readOnly |
        v_refGroup += refGroup
    )*
    END 'USER_RIGHTS'
    ;

refGroup:
    BEGIN 'REF_GROUP'
    (identifier += identifierValue)*
    END 'REF_GROUP'
    ;

variantCoding:
    BEGIN 'VARIANT_CODING'
    /* optional part */

    (
        v_varCharacteristic += varCharacteristic |
        v_varCriterion += varCriterion |
        v_varForbiddenComb += varForbiddenComb |
        v_varNaming += varNaming |
        v_varSeparator += varSeparator
    )*
    END 'VARIANT_CODING'
    ;

varCharacteristic:
    BEGIN 'VAR_CHARACTERISTIC'
    name = identifierValue
    (criterionName += identifierValue)*
    /* optional part */

    (
        v_varAddress += varAddress
    )*
    END 'VAR_CHARACTERISTIC'
    ;

varAddress:
    BEGIN 'VAR_ADDRESS'
    (address += integerValue)*
    END 'VAR_ADDRESS'
    ;

varCriterion:
    BEGIN 'VAR_CRITERION'
    name = identifierValue
    longIdentifier = stringValue
    (value_ += identifierValue)*
    /* optional part */

    (
        v_varMeasurement += varMeasurement |
        v_varSelectionCharacteristic += varSelectionCharacteristic
    )*
    END 'VAR_CRITERION'
    ;

varMeasurement:
     'VAR_MEASUREMENT'
    name = identifierValue
    ;

varSelectionCharacteristic:
     'VAR_SELECTION_CHARACTERISTIC'
    name = identifierValue
    ;

varForbiddenComb:
    BEGIN 'VAR_FORBIDDEN_COMB'
    (criterionName += identifierValue criterionValue += identifierValue)*
    END 'VAR_FORBIDDEN_COMB'
    ;

varNaming:
     'VAR_NAMING'
    
    tag =
    (
        'NUMERIC' |
        'APLHA'
    )

    ;

varSeparator:
     'VAR_SEPARATOR'
    separator = stringValue
    ;

integerValue:
    h = HEX | i = INT
    ;

numericValue:
    f = FLOAT | i = INT
    ;

stringValue:
    s = STRING
    ;

identifierValue:
    i += partialIdentifier ('.' i += partialIdentifier)*
    ;

partialIdentifier:
    i = IDENT (a += arraySpecifier)*
    ;

arraySpecifier:
    '[' (i = INT | n = IDENT) ']'
    ;

dataType:
    v = ('UBYTE' | 'SBYTE' | 'UWORD' | 'SWORD' | 'ULONG' | 'SLONG' |
    'A_UINT64' | 'A_INT64' | 'FLOAT16_IEEE' | 'FLOAT32_IEEE' | 'FLOAT64_IEEE')
    ;

datasize:
    v = ('BYTE' | 'WORD' | 'LONG')
    ;

addrtype:
    v = ('PBYTE' | 'PWORD' | 'PLONG' | 'DIRECT')
    ;

byteOrderValue:
    v = ('LITTLE_ENDIAN' | 'BIG_ENDIAN' | 'MSB_LAST' | 'MSB_FIRST')
    ;

indexorder:
    v = ('INDEX_INCR' | 'INDEX_DECR')
    ;

linkType:
    v = 'SYMBOL_TYPE_LINK'
    ;

BEGIN:
    '/begin'
    ;

END:
    '/end'
    ;

IDENT: [a-zA-Z_][a-zA-Z_0-9.]*;

fragment
EXPONENT : ('e'|'E') ('+'|'-')? ('0'..'9')+ ;

FLOAT:
   ('+' | '-')?
    (
        ('0'..'9')+ '.' ('0'..'9')* EXPONENT?
    |   '.' ('0'..'9')+ EXPONENT?
    |   ('0'..'9')+ EXPONENT
    )
    ;

INT: ('+' | '-')? '0'..'9'+
    ;

HEX:   '0'('x' | 'X') ('a' .. 'f' | 'A' .. 'F' | '0' .. '9')+
    ;

COMMENT:
    ('//' ~('\n'|'\r')* '\r'? '\n'
    |   '/*' .*? '*/')
        -> channel(HIDDEN)
    ;

WS  :   (' ' | '\t' | '\r' | '\n') -> skip
    ;

STRING:
    '"' ( ESC_SEQ | ~('\\'|'"') )* '"'
    ;

fragment
HEX_DIGIT : ('0'..'9'|'a'..'f'|'A'..'F') ;

fragment
ESC_SEQ
    :   '\\'
        (   // The standard escaped character set such as tab, newline, etc.
            [btnfr"'\\]
        |   // A Java style Unicode escape sequence
            UNICODE_ESC
        |   // Invalid escape
            .
        |   // Invalid escape at end of file
            EOF
        )
    ;

fragment
UNICODE_ESC
    :   'u' (HEX_DIGIT (HEX_DIGIT (HEX_DIGIT HEX_DIGIT?)?)?)?
;

fragment
OCTAL_ESC:
    '\\' ('0'..'3') ('0'..'7') ('0'..'7')
    |   '\\' ('0'..'7') ('0'..'7')
    |   '\\' ('0'..'7')
    ;
