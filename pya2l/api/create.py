#!/usr/bin/env python
"""Classes for creating new instances of A2L database entities.

This module provides classes and functions to create new instances of entities
defined in the A2L database, such as Measurement, AxisPts, CompuMethod, etc.
It complements the inspect.py module, which provides read-only access to the database.

The module includes creator classes for all major A2L entities, with methods to
create instances and set their properties. Each creator class follows a consistent
pattern with a main creation method and additional methods to set optional attributes.
"""

__copyright__ = """
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2020-2026 by Christoph Schueler <cpu12.gems@googlemail.com>

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

import json
from typing import Any, Dict, List, Optional, Tuple, Union

import pya2l.model as model
from pya2l import exceptions
from pya2l.api.inspect import (  # Project, Header, Annotation
    AxisDescr,
    AxisPts,
    Characteristic,
    CompuMethod,
    Function,
    Group,
    Instance,
    Measurement,
    ModCommon,
    ModPar,
    NoCompuMethod,
    RecordLayout,
    StructureComponent,
    TypedefCharacteristic,
    TypedefMeasurement,
    TypedefStructure,
    VariantCoding,
)


class HasAnnotation:
    """Base class for entities that have annotations."""

    def add_annotation(self, obj: Any, text: str, label: str | None = None, origin: str | None = None) -> model.Annotation:
        """Add Annotation to a Measurement."""
        annotation = model.Annotation(
            annotation_label=model.AnnotationLabel(label=label),
            annotation_origin=model.AnnotationOrigin(origin=origin),
            annotation_text=model.AnnotationText(text=text.splitlines()),
        )
        self.session.add(annotation)
        obj.annotation = [annotation]
        return annotation


class HasAddressType:
    def add_address_type(self, obj: Any, type_name: str) -> model.AddressType:
        """Add AddressType to a Measurement."""
        address_type = model.AddressType(addressType=type_name)
        address_type.measurement = obj
        self.session.add(address_type)
        return address_type


class HasBitMask:
    def add_bit_mask(self, obj: Any, mask: int) -> model.BitMask:
        """Add BitMask to a Characteristic.

        Parameters
        ----------
        obj : Any model object
            The object to add BitMask to
        mask : int
            The bit mask

        Returns
        -------
        model.BitMask
            The newly created BitMask instance
        """
        bit_mask = model.BitMask(mask=mask)
        bit_mask.characteristic = obj
        self.session.add(bit_mask)
        return bit_mask


class HasBitOperation:
    def add_bit_operation(
        self,
        obj: Any,
        left_shift: int | None = None,
        right_shift: int | None = None,
        sign_extend: bool | None = None,
    ) -> model.BitOperation:
        """Add BitOperation to a Measurement.

        Parameters
        ----------
        obj : Any model object
            The Object to add BitOperation to
        left_shift : Optional[int], optional
            Left shift value, by default None
        right_shift : Optional[int], optional
            Right shift value, by default None
        sign_extend : Optional[bool], optional
            Sign extend flag, by default None

        Returns
        -------
        model.BitOperation
            The newly created BitOperation instance
        """
        bit_operation = model.BitOperation()
        bit_operation.measurement = obj
        self.session.add(bit_operation)

        # Add left shift if provided
        if left_shift is not None:
            left_shift_obj = model.LeftShift(bitcount=left_shift)
            left_shift_obj.bit_operation = bit_operation
            self.session.add(left_shift_obj)

        # Add right shift if provided
        if right_shift is not None:
            right_shift_obj = model.RightShift(bitcount=right_shift)
            right_shift_obj.bit_operation = bit_operation
            self.session.add(right_shift_obj)

        # Add sign extend if provided
        if sign_extend is not None:
            sign_extend_obj = model.SignExtend()
            sign_extend_obj.bit_operation = bit_operation
            self.session.add(sign_extend_obj)

        return bit_operation


class HasByteOrder:
    def add_byte_order(self, obj: Any, byte_order: str) -> model.ByteOrder:
        """Add ByteOrder to an object.

        Parameters
        ----------
        obj : Any model object
            The object to add ByteOrder to
        byte_order : str
            The byte order (e.g., "MSB_FIRST", "MSB_LAST")

        Returns
        -------
        model.ByteOrder
            The newly created ByteOrder instance
        """
        byte_order_obj = model.ByteOrder(byteOrder=byte_order)
        obj.byte_order = byte_order_obj
        self.session.add(byte_order_obj)
        return byte_order_obj


class HasCalibrationAccess:
    def add_calibration_access(self, obj: Any, calibration_access: str) -> model.CalibrationAccess:
        calibration_access_obj = model.CalibrationAccess(type=calibration_access)
        obj.calibration_access = calibration_access_obj
        self.session.add(calibration_access_obj)
        return calibration_access_obj


class HasDisplayIdentifier:
    def add_display_identifier(self, obj: Any, text: str) -> model.DisplayIdentifier:
        """Add DisplayIdentifier to an object."""
        display_identifier = model.DisplayIdentifier(display_name=text)
        obj.display_identifier = display_identifier
        self.session.add(display_identifier)
        return display_identifier


class HasDeposit:
    def add_deposit(self, obj: model.AxisPts, mode: str) -> model.Deposit:
        deposit = model.Deposit(mode=mode)
        obj.deposit = deposit
        self.session.add(deposit)
        return deposit


class HasDiscrete:
    def set_discrete(self, obj: Any, value: bool) -> bool:
        """Add Discrete to a Measurement."""
        obj.discrete = value
        return value


class HasEcuAddressExtension:
    def add_ecu_address_extension(self, obj: Any, extension: int) -> model.EcuAddressExtension:
        """Add EcuAddressExtension to a Measurement."""
        address_extension = model.EcuAddressExtension(extension=extension)
        obj.ecu_address_extension = address_extension
        self.session.add(address_extension)
        return address_extension


class HasEncoding:
    def add_encoding(self, obj: Any, encoding: str) -> model.Encoding:
        """Add Encoding to an object."""
        encoding_obj = model.Encoding(encoding=encoding)
        obj.encoding = encoding_obj
        self.session.add(encoding_obj)
        return encoding_obj


class HasErrorMask:
    def add_error_mask(self, obj: Any, mask: int) -> model.ErrorMask:
        """Add ErrorMask to an object."""
        error_mask = model.ErrorMask(mask=mask)
        obj.error_mask = error_mask
        self.session.add(error_mask)
        return error_mask


class HasExtendedLimits:
    def add_extended_limits(self, obj: Any, lower_limit: float, upper_limit: float) -> model.ExtendedLimits:
        extended_limits = model.ExtendedLimits(lowerLimit=lower_limit, upperLimit=upper_limit)
        obj.extended_limits = extended_limits
        self.session.add(extended_limits)
        return extended_limits


class HasFormat:
    def add_format(self, obj: Any, format_string: str) -> model.Format:
        """Add Format to a Measurement.

        Parameters
        ----------
        obj : Any model object
            The object to add Format to
        format_string : str
            The format string

        Returns
        -------
        model.Format
            The newly created Format instance
        """
        format_obj = model.Format(formatString=format_string)
        format_obj.measurement = obj
        self.session.add(format_obj)
        return format_obj


class HasFunctionList:
    def add_function_list(self, obj: Any, function_names: list[str]) -> model.FunctionList:
        """Add FunctionList to a Group.

        Parameters
        ----------
        obj : Any model object
            The object to add FunctionList to
        function_names : List[str]
            List of function names

        Returns
        -------
        model.FunctionList
            The newly created FunctionList instance
        """
        function_list = model.FunctionList(name=function_names)
        obj.function_list = function_list
        self.session.add(function_list)
        return function_list


class HasGuardRails:
    def set_discrete(self, obj: Any, value: bool) -> bool:
        """Add GuardRails to a Measurement."""
        obj.guard_rails = value
        return value


class HasIfData:
    """Base class for entities that have IF_DATA."""

    def add_if_data(self, obj: Any, if_data: str | dict[str, Any]) -> model.IfData:
        if isinstance(if_data, dict):
            if_data = json.dumps(if_data)
        entry = model.IfData(raw=if_data)
        self.session.add(entry)
        obj.if_data = [entry]
        return entry


class HasLayout:
    def add_layout(self, obj: Any, indexMode: str) -> model.Layout:
        """Add Layout to an object."""
        layout = model.Layout(indexMode=indexMode)
        obj.layout = layout
        self.session.add(layout)
        return layout


class HasMatrixDim:
    def add_matrix_dim(self, obj: Any, x_dim: int, y_dim: int | None = None, z_dim: int | None = None) -> model.MatrixDim:
        """Add MatrixDim to a Measurement.

        Parameters
        ----------
        obj : Any model object
            The object to add MatrixDim to
        x_dim : int
            X dimension
        y_dim : Optional[int], optional
            Y dimension, by default None
        z_dim : Optional[int], optional
            Z dimension, by default None

        Returns
        -------
        model.MatrixDim
            The newly created MatrixDim instance
        """
        numbers = [x_dim]
        if y_dim is not None:
            numbers.append(y_dim)
        if z_dim is not None:
            numbers.append(z_dim)

        matrix_dim = model.MatrixDim(numbers=numbers)
        matrix_dim.measurement = obj
        self.session.add(matrix_dim)
        return matrix_dim


class HasMaxRefresh:
    def add_max_refresh(self, obj: Any, scaling_unit: int, rate: int) -> model.MaxRefresh:
        """Add MaxRefresh to an object."""
        max_refresh = model.MaxRefresh(scalingUnit=scaling_unit, rate=rate)
        obj.max_refresh = max_refresh
        self.session.add(max_refresh)
        return max_refresh


class HasModelLink:
    def add_model_link(self, obj: Any, link: str) -> model.ModelLink:
        model_link = model.ModelLink(link=link)
        obj.model_link = model_link
        self.session.add(model_link)
        return model_link


class HasMonotony:
    def add_monotony(self, obj: Any, monotony: str) -> model.Monotony:
        monotony_obj = model.Monotony(monotony=monotony)
        obj.monotony = monotony_obj
        self.session.add(monotony_obj)
        return monotony_obj


class HasPhysUnit:
    def add_phys_unit(self, obj: Any, unit: str) -> model.PhysUnit:
        """Add PhysUnit to a object.

        Parameters
        ----------
        obj : Any model object
            The object to add PhysUnit to
        unit : str
            The physical unit

        Returns
        -------
        model.PhysUnit
            The newly created PhysUnit instance
        """
        phys_unit = model.PhysUnit(unit=unit)
        phys_unit.measurement = obj
        self.session.add(phys_unit)
        return phys_unit


class HasReadOnly:
    def set_read_only(self, obj: Any, value: bool) -> bool:
        """Add read_only to a Measurement."""
        obj.read_only = value
        return value


class HasReadWrite:
    def set_read_write(self, obj: Any, value: bool) -> bool:
        """Add read_write to a Measurement."""
        obj.read_write = value
        return value


class HasRefMemorySegment:
    def add_ref_memory_segment(self, obj: Any, name: str) -> model.RefMemorySegment:
        ref_memory_segment = model.RefMemorySegment(name=name)
        obj.ref_memory_segment = ref_memory_segment
        self.session.add(ref_memory_segment)
        return ref_memory_segment


class HasStepSize:
    def add_step_size(self, obj: Any, step_size: float) -> model.StepSize:
        step_size_obj = model.StepSize(stepSize=step_size)
        obj.step_size = step_size_obj
        self.session.add(step_size_obj)
        return step_size_obj


class HasSymbolLink:
    def add_symbol_link(self, obj: Any, symbol_name: str, offset: int | None = None) -> model.SymbolLink:
        """Add SymbolLink to a Measurement.

        Parameters
        ----------
        obj : Any model obj
            The object to add SymbolLink to
        symbol_name : str
            The symbol name
        offset : Optional[int], optional
            The offset, by default None

        Returns
        -------
        model.SymbolLink
            The newly created SymbolLink instance
        """
        symbol_link = model.SymbolLink(symbolName=symbol_name, offset=offset)
        symbol_link.measurement = obj
        self.session.add(symbol_link)
        return symbol_link


class Creator:
    """Base class for all creator classes in this module.

    This class provides common functionality for creating new instances of
    database entities.

    Attributes
    ----------
    session : Any
        SQLAlchemy session object used to interact with the database
    """

    def __init__(self, session: Any):
        """Initialize a Creator instance.

        Parameters
        ----------
        session : Any
            SQLAlchemy session object used to interact with the database
        """
        self.session = session

    def commit(self):
        """Commit the current transaction to the database."""
        self.session.commit()

    def rollback(self):
        """Rollback the current transaction."""
        self.session.rollback()


class AxisPtsCreator(
    Creator,
    HasAnnotation,
    HasByteOrder,
    HasCalibrationAccess,
    HasDeposit,
    HasDisplayIdentifier,
    HasEcuAddressExtension,
    HasExtendedLimits,
    HasFormat,
    HasFunctionList,
    HasGuardRails,
    HasIfData,
    HasMaxRefresh,
    HasModelLink,
    HasMonotony,
    HasPhysUnit,
    HasReadOnly,
    HasRefMemorySegment,
    HasStepSize,
):
    """Creator class for AxisPts entities.

    This class provides methods to create new AxisPts instances and
    their related entities.

    Attributes
    ----------
    session : Any
        SQLAlchemy session object used to interact with the database
    """

    def create_axis_pts(
        self,
        name: str,
        long_identifier: str,
        address: int,
        input_quantity: str,
        deposit_attr: str,
        max_diff: float,
        conversion: str,
        max_axis_points: int,
        lower_limit: float,
        upper_limit: float,
        module_name: str | None = None,
    ) -> model.AxisPts:
        """Create a new AxisPts instance.

        Parameters
        ----------
        name : str
            Name of the axis points
        long_identifier : str
            Description of the axis points
        address : int
            Address of the axis points
        input_quantity : str
            Input quantity of the axis points
        deposit_attr : str
            Deposit attribute of the axis points
        max_diff : float
            Maximum difference of the axis points
        conversion : str
            Name of the computation method for conversion
        max_axis_points : int
            Maximum number of axis points
        lower_limit : float
            Lower limit of the axis points
        upper_limit : float
            Upper limit of the axis points
        module_name : Optional[str], optional
            Name of the module to associate with this AxisPts, by default None

        Returns
        -------
        model.AxisPts
            The newly created AxisPts instance
        """
        # Find the module if module_name is provided
        module = None
        if module_name:
            module = self.session.query(model.Module).filter(model.Module.name == module_name).first()
            if not module:
                raise exceptions.StructuralError(f"Module '{module_name}' not found")

        # Create the AxisPts instance
        axis_pts = model.AxisPts(
            name=name,
            longIdentifier=long_identifier,
            address=address,
            inputQuantity=input_quantity,
            depositAttr=deposit_attr,
            maxDiff=max_diff,
            conversion=conversion,
            maxAxisPoints=max_axis_points,
            lowerLimit=lower_limit,
            upperLimit=upper_limit,
        )

        # Associate with module if provided
        if module:
            module.axis_pts.append(axis_pts)

        # Add to session
        self.session.add(axis_pts)

        return axis_pts


class BlobCreator(
    Creator,
    HasAddressType,
    HasAnnotation,
    HasCalibrationAccess,
    HasDisplayIdentifier,
    HasEcuAddressExtension,
    HasIfData,
    HasMaxRefresh,
    HasModelLink,
    HasSymbolLink,
):
    """Creator class for Blob entities.

    This class provides methods to create new Blob instances and
    their related entities.

    Attributes
    ----------
    session : Any
        SQLAlchemy session object used to interact with the database
    """

    def create_blob(
        self, name: str, long_identifier: str, address: int, size: int, module_name: str | None = None
    ) -> model.Blob:
        """Create a new Blob instance.

        Parameters
        ----------
        name : str
            Name of the blob
        long_identifier : str
            Description of the blob
        address : int
            Address of the blob
        size : int
            Size of the blob
        module_name : Optional[str], optional
            Name of the module to associate with this Blob, by default None

        Returns
        -------
        model.Blob
            The newly created Blob instance
        """
        # Find the module if module_name is provided
        module = None
        if module_name:
            module = self.session.query(model.Module).filter(model.Module.name == module_name).first()
            if not module:
                raise exceptions.StructuralError(f"Module '{module_name}' not found")

        # Create the Blob instance
        blob = model.Blob(name=name, longIdentifier=long_identifier, address=address, size=size)

        # Associate with module if provided
        if module:
            module.blob.append(blob)

        # Add to session
        self.session.add(blob)

        return blob


class CharacteristicCreator(
    Creator,
    HasAnnotation,
    HasBitMask,
    HasByteOrder,
    HasCalibrationAccess,
    HasDiscrete,
    HasDisplayIdentifier,
    HasEcuAddressExtension,
    HasEncoding,
    HasExtendedLimits,
    HasFormat,
    HasFunctionList,
    HasGuardRails,
    HasIfData,
    HasMaxRefresh,
    HasModelLink,
):
    """Creator class for Characteristic entities.

    This class provides methods to create new Characteristic instances and
    their related entities.

    Attributes
    ----------
    session : Any
        SQLAlchemy session object used to interact with the database
    """

    def create_characteristic(
        self,
        name: str,
        long_identifier: str,
        char_type: str,
        address: int,
        deposit: str,
        max_diff: float,
        conversion: str,
        lower_limit: float,
        upper_limit: float,
        module_name: str | None = None,
    ) -> model.Characteristic:
        """Create a new Characteristic instance.

        Parameters
        ----------
        name : str
            Name of the characteristic
        long_identifier : str
            Description of the characteristic
        char_type : str
            Type of the characteristic (e.g., "VALUE", "CURVE", "MAP", "CUBOID")
        address : int
            Address of the characteristic
        deposit : str
            Deposit attribute of the characteristic
        max_diff : float
            Maximum difference of the characteristic
        conversion : str
            Name of the computation method for conversion
        lower_limit : float
            Lower limit of the characteristic
        upper_limit : float
            Upper limit of the characteristic
        module_name : Optional[str], optional
            Name of the module to associate with this Characteristic, by default None

        Returns
        -------
        model.Characteristic
            The newly created Characteristic instance
        """
        # Find the module if module_name is provided
        module = None
        if module_name:
            module = self.session.query(model.Module).filter(model.Module.name == module_name).first()
            if not module:
                raise exceptions.StructuralError(f"Module '{module_name}' not found")

        # Create the Characteristic instance
        characteristic = model.Characteristic(
            name=name,
            longIdentifier=long_identifier,
            type=char_type,
            address=address,
            deposit=deposit,
            maxDiff=max_diff,
            conversion=conversion,
            lowerLimit=lower_limit,
            upperLimit=upper_limit,
        )

        # Associate with module if provided
        if module:
            module.characteristic.append(characteristic)

        # Add to session
        self.session.add(characteristic)

        return characteristic

    def add_axis_descr(
        self,
        characteristic: model.Characteristic,
        attribute: str,
        input_quantity: str,
        conversion: str,
        max_axis_points: int,
        lower_limit: float,
        upper_limit: float,
    ) -> model.AxisDescr:
        """Add AxisDescr to a Characteristic.

        Parameters
        ----------
        characteristic : model.Characteristic
            The Characteristic to add AxisDescr to
        attribute : str
            The attribute (e.g., "STD_AXIS", "FIX_AXIS", "COM_AXIS")
        input_quantity : str
            The input quantity
        conversion : str
            Name of the computation method for conversion
        max_axis_points : int
            Maximum number of axis points
        lower_limit : float
            Lower limit of the axis
        upper_limit : float
            Upper limit of the axis

        Returns
        -------
        model.AxisDescr
            The newly created AxisDescr instance
        """
        axis_descr = model.AxisDescr(
            attribute=attribute,
            inputQuantity=input_quantity,
            conversion=conversion,
            maxAxisPoints=max_axis_points,
            lowerLimit=lower_limit,
            upperLimit=upper_limit,
        )
        characteristic.axis_descr.append(axis_descr)
        self.session.add(axis_descr)
        return axis_descr

    def add_dependent_characteristic(
        self, characteristic: model.Characteristic, formula: str, characteristic_names: list[str]
    ) -> model.DependentCharacteristic:
        """Add DependentCharacteristic to a Characteristic.

        Parameters
        ----------
        characteristic : model.Characteristic
            The Characteristic to add DependentCharacteristic to
        formula : str
            The formula
        characteristic_names : List[str]
            List of characteristic names

        Returns
        -------
        model.DependentCharacteristic
            The newly created DependentCharacteristic instance
        """
        dependent_characteristic = model.DependentCharacteristic(formula=formula, characteristic_id=characteristic_names)
        dependent_characteristic.characteristic = characteristic
        self.session.add(dependent_characteristic)
        return dependent_characteristic

    def add_virtual_characteristic(
        self, characteristic: model.Characteristic, formula: str, characteristic_names: list[str]
    ) -> model.VirtualCharacteristic:
        """Add VirtualCharacteristic to a Characteristic.

        Parameters
        ----------
        characteristic : model.Characteristic
            The Characteristic to add VirtualCharacteristic to
        formula : str
            The formula
        characteristic_names : List[str]
            List of characteristic names

        Returns
        -------
        model.VirtualCharacteristic
            The newly created VirtualCharacteristic instance
        """
        virtual_characteristic = model.VirtualCharacteristic(formula=formula, characteristic_id=characteristic_names)
        virtual_characteristic.characteristic = characteristic
        self.session.add(virtual_characteristic)
        return virtual_characteristic


class CompuMethodCreator(Creator):
    """Creator class for CompuMethod entities.

    This class provides methods to create new CompuMethod instances and
    their related entities (Coeffs, CoeffsLinear, Formula, etc.).

    Attributes
    ----------
    session : Any
        SQLAlchemy session object used to interact with the database
    """

    def create_compu_method(
        self, name: str, long_identifier: str, conversion_type: str, format_str: str, unit: str, module_name: str | None = None
    ) -> model.CompuMethod:
        """Create a new CompuMethod instance.

        Parameters
        ----------
        name : str
            Name of the computation method
        long_identifier : str
            Description of the computation method
        conversion_type : str
            Type of conversion (e.g., "IDENTICAL", "LINEAR", "RAT_FUNC", "TAB_INTP")
        format_str : str
            Format string for displaying physical values
        unit : str
            Physical unit of the values
        module_name : Optional[str], optional
            Name of the module to associate with this CompuMethod, by default None

        Returns
        -------
        model.CompuMethod
            The newly created CompuMethod instance
        """
        # Find the module if module_name is provided
        module = None
        if module_name:
            module = self.session.query(model.Module).filter(model.Module.name == module_name).first()
            if not module:
                raise exceptions.StructuralError(f"Module '{module_name}' not found")

        # Create the CompuMethod instance
        compu_method = model.CompuMethod(
            name=name, longIdentifier=long_identifier, conversionType=conversion_type, format=format_str, unit=unit
        )

        # Associate with module if provided
        if module:
            module.compu_method.append(compu_method)

        # Add to session
        self.session.add(compu_method)

        return compu_method

    def add_coeffs(
        self, compu_method: model.CompuMethod, a: float, b: float, c: float, d: float, e: float, f: float
    ) -> model.Coeffs:
        """Add Coeffs to a CompuMethod.

        Parameters
        ----------
        compu_method : model.CompuMethod
            The CompuMethod to add Coeffs to
        a : float
            Coefficient a
        b : float
            Coefficient b
        c : float
            Coefficient c
        d : float
            Coefficient d
        e : float
            Coefficient e
        f : float
            Coefficient f

        Returns
        -------
        model.Coeffs
            The newly created Coeffs instance
        """
        coeffs = model.Coeffs(a=a, b=b, c=c, d=d, e=e, f=f)
        coeffs.compu_method = compu_method
        self.session.add(coeffs)
        return coeffs

    def add_coeffs_linear(self, compu_method: model.CompuMethod, a: float, b: float) -> model.CoeffsLinear:
        """Add CoeffsLinear to a CompuMethod.

        Parameters
        ----------
        compu_method : model.CompuMethod
            The CompuMethod to add CoeffsLinear to
        a : float
            Coefficient a
        b : float
            Coefficient b

        Returns
        -------
        model.CoeffsLinear
            The newly created CoeffsLinear instance
        """
        coeffs_linear = model.CoeffsLinear(a=a, b=b)
        coeffs_linear.compu_method = compu_method
        self.session.add(coeffs_linear)
        return coeffs_linear

    def add_compu_tab_ref(self, compu_method: model.CompuMethod, conversion_table: str) -> model.CompuTabRef:
        """Add CompuTabRef to a CompuMethod.

        Parameters
        ----------
        compu_method : model.CompuMethod
            The CompuMethod to add CompuTabRef to
        conversion_table : str
            Name of the conversion table

        Returns
        -------
        model.CompuTabRef
            The newly created CompuTabRef instance
        """
        compu_tab_ref = model.CompuTabRef(conversionTable=conversion_table)
        compu_tab_ref.compu_method = compu_method
        self.session.add(compu_tab_ref)
        return compu_tab_ref

    def add_formula(self, compu_method: model.CompuMethod, formula_str: str, formula_inv: str | None = None) -> model.Formula:
        """Add Formula to a CompuMethod.

        Parameters
        ----------
        compu_method : model.CompuMethod
            The CompuMethod to add Formula to
        formula_str : str
            The formula string (f_x)
        formula_inv : Optional[str], optional
            The inverse formula string, by default None

        Returns
        -------
        model.Formula
            The newly created Formula instance
        """
        formula = model.Formula(f_x=formula_str)
        formula.compu_method = compu_method
        self.session.add(formula)

        # Add inverse formula if provided
        if formula_inv:
            formula_inv_obj = model.FormulaInv(g_x=formula_inv)
            formula_inv_obj.formula = formula
            self.session.add(formula_inv_obj)

        return formula

    def add_ref_unit(self, compu_method: model.CompuMethod, unit: str) -> model.RefUnit:
        """Add RefUnit to a CompuMethod.

        Parameters
        ----------
        compu_method : model.CompuMethod
            The CompuMethod to add RefUnit to
        unit : str
            The reference unit

        Returns
        -------
        model.RefUnit
            The newly created RefUnit instance
        """
        ref_unit = model.RefUnit(unit=unit)
        ref_unit.compu_method = compu_method
        self.session.add(ref_unit)
        return ref_unit

    def add_status_string_ref(self, compu_method: model.CompuMethod, conversion_table: str) -> model.StatusStringRef:
        """Add StatusStringRef to a CompuMethod.

        Parameters
        ----------
        compu_method : model.CompuMethod
            The CompuMethod to add StatusStringRef to
        conversion_table : str
            Name of the conversion table

        Returns
        -------
        model.StatusStringRef
            The newly created StatusStringRef instance
        """
        status_string_ref = model.StatusStringRef(conversionTable=conversion_table)
        status_string_ref.compu_method = compu_method
        self.session.add(status_string_ref)
        return status_string_ref


class MeasurementCreator(
    Creator,
    HasAddressType,
    HasAnnotation,
    HasBitMask,
    HasBitOperation,
    HasByteOrder,
    HasDisplayIdentifier,
    HasDiscrete,
    HasFormat,
    HasEcuAddressExtension,
    HasErrorMask,
    HasFunctionList,
    HasIfData,
    HasLayout,
    HasMatrixDim,
    HasMaxRefresh,
    HasModelLink,
    HasPhysUnit,
    HasReadWrite,
    HasRefMemorySegment,
    HasSymbolLink,
):
    """Creator class for Measurement entities.

    This class provides methods to create new Measurement instances and
    their related entities (ArraySize, BitOperation, etc.).

    Attributes
    ----------
    session : Any
        SQLAlchemy session object used to interact with the database
    """

    def create_measurement(
        self,
        name: str,
        long_identifier: str,
        datatype: str,
        conversion: str,
        resolution: int,
        accuracy: float,
        lower_limit: float,
        upper_limit: float,
        module_name: str | None = None,
    ) -> model.Measurement:
        """Create a new Measurement instance.

        Parameters
        ----------
        name : str
            Name of the measurement
        long_identifier : str
            Description of the measurement
        datatype : str
            Data type of the measurement (e.g., "UBYTE", "SWORD", "FLOAT32_IEEE")
        conversion : str
            Name of the computation method for conversion
        resolution : int
            Resolution of the measurement
        accuracy : float
            Accuracy of the measurement
        lower_limit : float
            Lower limit of the measurement
        upper_limit : float
            Upper limit of the measurement
        module_name : Optional[str], optional
            Name of the module to associate with this Measurement, by default None

        Returns
        -------
        model.Measurement
            The newly created Measurement instance
        """
        # Find the module if module_name is provided
        module = None
        if module_name:
            module = self.session.query(model.Module).filter(model.Module.name == module_name).first()
            if not module:
                raise exceptions.StructuralError(f"Module '{module_name}' not found")

        # Create the Measurement instance
        measurement = model.Measurement(
            name=name,
            longIdentifier=long_identifier,
            datatype=datatype,
            conversion=conversion,
            resolution=resolution,
            accuracy=accuracy,
            lowerLimit=lower_limit,
            upperLimit=upper_limit,
        )

        # Associate with module if provided
        if module:
            module.measurement.append(measurement)

        # Add to session
        self.session.add(measurement)

        return measurement

    def add_array_size(self, measurement: model.Measurement, number: int) -> model.ArraySize:
        """Add ArraySize to a Measurement.

        Parameters
        ----------
        measurement : model.Measurement
            The Measurement to add ArraySize to
        number : int
            The array size

        Returns
        -------
        model.ArraySize
            The newly created ArraySize instance
        """
        array_size = model.ArraySize(number=number)
        array_size.measurement = measurement
        self.session.add(array_size)
        return array_size

    def add_ecu_address(self, measurement: model.Measurement, address: int) -> model.EcuAddress:
        """Add EcuAddress to a Measurement.

        Parameters
        ----------
        measurement : model.Measurement
            The Measurement to add EcuAddress to
        address : int
            The ECU address

        Returns
        -------
        model.EcuAddress
            The newly created EcuAddress instance
        """
        ecu_address = model.EcuAddress(address=address)
        ecu_address.measurement = measurement
        self.session.add(ecu_address)
        return ecu_address

    def add_virtual(self, measurement: model.Measurement, measuring_channel: list[str] | None = None) -> model.Virtual:
        """Add Virtual to a Measurement.

        Parameters
        ----------
        measurement : model.Measurement
            The Measurement to add Virtual to
        measuring_channel : Optional[List[str]], optional
            List of measuring channels, by default None

        Returns
        -------
        model.Virtual
            The newly created Virtual instance
        """
        virtual = model.Virtual(measuringChannel=measuring_channel if measuring_channel is not None else [])
        virtual.measurement = measurement
        self.session.add(virtual)
        return virtual


class ProjectCreator(Creator):
    """Creator class for Project entities.

    This class provides methods to create new Project instances and
    their related entities (Header, Module, etc.).

    Attributes
    ----------
    session : Any
        SQLAlchemy session object used to interact with the database
    """

    def create_project(self, name: str, long_identifier: str) -> model.Project:
        """Create a new Project instance.

        Parameters
        ----------
        name : str
            Name of the project
        long_identifier : str
            Description of the project

        Returns
        -------
        model.Project
            The newly created Project instance
        """
        # Create the Project instance
        project = model.Project(name=name, longIdentifier=long_identifier)

        # Add to session
        self.session.add(project)

        return project

    def add_header(self, project: model.Project, comment: str) -> model.Header:
        """Add Header to a Project.

        Parameters
        ----------
        project : model.Project
            The Project to add Header to
        comment : str
            The comment for the header

        Returns
        -------
        model.Header
            The newly created Header instance
        """
        header = model.Header(comment=comment)
        header.project = project
        self.session.add(header)
        return header

    def add_project_no(self, header: model.Header, project_number: str) -> model.ProjectNo:
        """Add ProjectNo to a Header.

        Parameters
        ----------
        header : model.Header
            The Header to add ProjectNo to
        project_number : str
            The project number

        Returns
        -------
        model.ProjectNo
            The newly created ProjectNo instance
        """
        project_no = model.ProjectNo(projectNumber=project_number)
        project_no.header = header
        self.session.add(project_no)
        return project_no


class ModuleCreator(Creator, HasIfData):
    """Creator class for Module entities.

    This class provides methods to create new Module instances and
    their related entities. It includes methods to create and associate
    various entities with a Module, such as measurements, characteristics,
    axis points, computation methods, etc.

    Attributes
    ----------
    session : Any
        SQLAlchemy session object used to interact with the database
    """

    def create_module(self, name: str, long_identifier: str, project: model.Project | None = None) -> model.Module:
        """Create a new Module instance.

        Parameters
        ----------
        name : str
            Name of the module
        long_identifier : str
            Description of the module
        project : Optional[model.Project], optional
            The Project to associate with this Module, by default None

        Returns
        -------
        model.Module
            The newly created Module instance
        """
        # Create the Module instance
        module = model.Module(name=name, longIdentifier=long_identifier if long_identifier is not None else "")

        # Associate with project if provided
        if project:
            project.module.append(module)

        # Add to session
        self.session.add(module)

        return module

    def add_if_data(self, module: model.Module, if_data_text: str | dict[str, Any]) -> model.IfData:
        return super().add_if_data(module, if_data_text)

    def add_variant_coding(
        self, module: model.Module, var_separator: str | None = None, var_naming: str | None = None
    ) -> model.VariantCoding:
        """Add VariantCoding to a Module.

        Parameters
        ----------
        module : model.Module
            The Module to add VariantCoding to
        var_separator : Optional[str], optional
            The variant separator, by default None
        var_naming : Optional[str], optional
            The variant naming convention, by default None

        Returns
        -------
        model.VariantCoding
            The newly created VariantCoding instance
        """
        variant_coding = model.VariantCoding()
        variant_coding.module = module
        self.session.add(variant_coding)

        # Add var_separator if provided
        if var_separator:
            var_separator_obj = model.VarSeparator(separator=var_separator)
            var_separator_obj.variant_coding = variant_coding
            self.session.add(var_separator_obj)

        # Add var_naming if provided
        if var_naming:
            var_naming_obj = model.VarNaming(naming=var_naming)
            var_naming_obj.variant_coding = variant_coding
            self.session.add(var_naming_obj)

        return variant_coding

    def add_var_characteristic(
        self, variant_coding: model.VariantCoding, name: str, criterion_name: str, criterion_value: str
    ) -> model.VarCharacteristic:
        """Add VarCharacteristic to a VariantCoding.

        Parameters
        ----------
        variant_coding : model.VariantCoding
            The VariantCoding to add VarCharacteristic to
        name : str
            The name of the characteristic
        criterion_name : str
            The name of the criterion
        criterion_value : str
            The value of the criterion

        Returns
        -------
        model.VarCharacteristic
            The newly created VarCharacteristic instance
        """
        var_characteristic = model.VarCharacteristic(name=name)
        var_characteristic.variant_coding = variant_coding
        self.session.add(var_characteristic)

        # Add criterion
        criterion = model.VarCriterion(name=criterion_name, value=criterion_value)
        criterion.var_characteristic = var_characteristic
        self.session.add(criterion)

        return var_characteristic

    def add_user_rights(
        self, module: model.Module, user_level_id: str, read_only: bool = False, ref_group: str | None = None
    ) -> model.UserRights:
        """Add UserRights to a Module.

        Parameters
        ----------
        module : model.Module
            The Module to add UserRights to
        user_level_id : str
            The user level ID
        read_only : bool, optional
            Whether the user rights are read-only, by default False
        ref_group : Optional[str], optional
            The reference group, by default None

        Returns
        -------
        model.UserRights
            The newly created UserRights instance
        """
        user_rights = model.UserRights(userLevelId=user_level_id, readOnly=read_only)
        user_rights.module = module
        self.session.add(user_rights)

        # Add ref_group if provided
        if ref_group:
            ref_group_obj = model.RefGroup(identifier=ref_group)
            ref_group_obj.user_rights = user_rights
            self.session.add(ref_group_obj)

        return user_rights

    def add_group(self, module: model.Module, group_name: str, long_identifier: str, root: bool = False) -> model.Group:
        """Add Group to a Module.

        Parameters
        ----------
        module : model.Module
            The Module to add Group to
        group_name : str
            The name of the group
        long_identifier : str
            The description of the group
        root : bool, optional
            Whether this is a root group, by default False

        Returns
        -------
        model.Group
            The newly created Group instance
        """
        group = model.Group(groupName=group_name, groupLongIdentifier=long_identifier)
        group.module = module
        self.session.add(group)

        # Add root if true
        if root:
            root_obj = model.Root()
            root_obj.group = group
            self.session.add(root_obj)

        return group

    def add_sub_group(self, group: model.Group, sub_group_name: str) -> model.SubGroup:
        """Add SubGroup to a Group.

        Parameters
        ----------
        group : model.Group
            The Group to add SubGroup to
        sub_group_name : str
            The name of the sub-group

        Returns
        -------
        model.SubGroup
            The newly created SubGroup instance
        """
        sub_group = model.SubGroup(identifier=sub_group_name)
        sub_group.group = group
        self.session.add(sub_group)
        return sub_group

    def add_unit(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        display: str,
        type_str: str | None = None,
        ref_unit: str | None = None,
        unit_conversion: dict[str, float] | None = None,
    ) -> model.Unit:
        """Add Unit to a Module.

        Parameters
        ----------
        module : model.Module
            The Module to add Unit to
        name : str
            The name of the unit
        long_identifier : str
            The description of the unit
        display : str
            The display string for the unit
        type_str : Optional[str], optional
            The type of the unit, by default None
        ref_unit : Optional[str], optional
            The reference unit, by default None
        unit_conversion : Optional[Dict[str, float]], optional
            The unit conversion parameters (gradient, offset), by default None

        Returns
        -------
        model.Unit
            The newly created Unit instance
        """
        unit = model.Unit(name=name, longIdentifier=long_identifier, display=display, type=type_str)
        module.unit.append(unit)
        self.session.add(unit)

        # Add ref_unit if provided
        if ref_unit:
            ref_unit_obj = model.RefUnit(unit=ref_unit)
            unit.ref_unit = ref_unit_obj
            self.session.add(ref_unit_obj)

        # Add unit_conversion if provided
        if unit_conversion:
            si_exponents = model.SiExponents()
            si_exponents.unit = unit
            self.session.add(si_exponents)

            unit_conversion_obj = model.UnitConversion(
                gradient=unit_conversion.get("gradient", 1.0), offset=unit_conversion.get("offset", 0.0)
            )
            unit_conversion_obj.unit = unit
            self.session.add(unit_conversion_obj)

        return unit

    def add_compu_tab(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        conversion_type: str,
        pairs: list[tuple[float, float]],
        default_numeric: float | None = None,
    ) -> model.CompuTab:
        """Add a numeric COMPU_TAB to a Module.

        Parameters
        ----------
        module : model.Module
            Module owning the table
        name : str
            Table name
        long_identifier : str
            Description
        conversion_type : str
            One of TAB_INTP, TAB_NOINTP
        pairs : List[Tuple[float, float]]
            List of (inVal, outVal) numeric pairs
        default_numeric : Optional[float]
            Optional default numeric display value
        """
        ct = model.CompuTab(
            name=name,
            longIdentifier=long_identifier,
            conversionType=conversion_type,
            numberValuePairs=len(pairs),
        )
        ct.module = module
        self.session.add(ct)
        # add pairs in order
        for idx, (inp, outp) in enumerate(pairs):
            p = model.CompuTabPair()
            p.position = idx
            p.inVal = float(inp)
            p.outVal = float(outp)
            p.parent = ct
            self.session.add(p)
        if default_numeric is not None:
            d = model.DefaultValueNumeric(display_value=float(default_numeric))
            d.compu_tab = ct
            self.session.add(d)
        return ct

    def add_compu_vtab(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        conversion_type: str,
        pairs: list[tuple[float, str]],
        default_value: str | None = None,
    ) -> model.CompuVtab:
        """Add a COMPU_VTAB (verbal table) to a Module."""
        vt = model.CompuVtab(
            name=name,
            longIdentifier=long_identifier,
            conversionType=conversion_type,
            numberValuePairs=len(pairs),
        )
        vt.module = module
        self.session.add(vt)
        for idx, (inp, outp) in enumerate(pairs):
            p = model.CompuVtabPair()
            p.position = idx
            p.inVal = float(inp)
            p.outVal = str(outp)
            p.parent = vt
            self.session.add(p)
        if default_value is not None:
            dv = model.DefaultValue(display_string=str(default_value))
            vt.default_value = dv
            self.session.add(dv)
        return vt

    def add_compu_vtab_range(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        triples: list[tuple[float, float, str]],
        default_value: str | None = None,
    ) -> model.CompuVtabRange:
        """Add a COMPU_VTAB_RANGE (verbal ranges) to a Module."""
        vr = model.CompuVtabRange(
            name=name,
            longIdentifier=long_identifier,
            numberValueTriples=len(triples),
        )
        vr.module = module
        self.session.add(vr)
        for idx, (vmin, vmax, outp) in enumerate(triples):
            t = model.CompuVtabRangeTriple()
            t.position = idx
            t.inValMin = float(vmin)
            t.inValMax = float(vmax)
            t.outVal = str(outp)
            t.parent = vr
            self.session.add(t)
        if default_value is not None:
            dv = model.DefaultValue(display_string=str(default_value))
            vr.default_value = dv
            self.session.add(dv)
        return vr

    def add_blob(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        address: int,
        length: int,
        calibration_access: str | None = None,
    ) -> model.Blob:
        """Add BLOB to a Module."""
        blob = model.Blob(
            name=name,
            longIdentifier=long_identifier,
            address=address,
            length=length,
        )
        blob.module = module
        self.session.add(blob)
        if calibration_access:
            ca = model.CalibrationAccess(access=calibration_access)
            ca.blob = blob
            self.session.add(ca)
        return blob

    def add_transformer(
        self,
        module: model.Module,
        name: str,
        version: str,
        dllname32: str,
        dllname64: str,
        timeout: int,
        trigger: str,
        reverse: str,
        in_objects: list[str] | None = None,
        out_objects: list[str] | None = None,
    ) -> model.Transformer:
        """Add TRANSFORMER to a Module."""
        tr = model.Transformer(
            name=name,
            version=version,
            executable32=dllname32,
            executable64=dllname64,
            timeout=timeout,
            trigger=trigger,
            inverseTransformer=reverse,
        )
        tr.module = module
        self.session.add(tr)
        if in_objects is not None:
            ino = model.TransformerInObjects()
            self.session.add(ino)
            for ident in in_objects:
                ino._identifier.append(model.TransformerInObjectsIdentifiers(ident))
            tr.transformer_in_objects = ino
        if out_objects is not None:
            outo = model.TransformerOutObjects()
            self.session.add(outo)
            for ident in out_objects:
                outo._identifier.append(model.TransformerOutObjectsIdentifiers(ident))
            tr.transformer_out_objects = outo
        return tr

    def add_frame(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        scaling_unit: int,
        rate: int,
        measurements: list[str] | None = None,
        if_data_texts: list[str] | None = None,
    ) -> model.Frame:
        """Add FRAME to a Module."""
        fr = model.Frame(
            name=name,
            longIdentifier=long_identifier,
            scalingUnit=scaling_unit,
            rate=rate,
        )
        fr.module = module
        self.session.add(fr)
        if measurements:
            fm = model.FrameMeasurement()
            self.session.add(fm)
            for m in measurements:
                fm._identifier.append(model.FrameMeasurementIdentifiers(m))
            fr.frame_measurement = fm
        if if_data_texts:
            for txt in if_data_texts:
                entry = model.IfData(raw=txt)
                entry.frame = fr
                self.session.add(entry)
        return fr

    def add_typedef_structure(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        size: int,
    ) -> model.TypedefStructure:
        """Add TYPEDEF_STRUCTURE to a Module."""
        ts = model.TypedefStructure(
            name=name,
            longIdentifier=long_identifier,
            size=size,
        )
        ts.module = module
        self.session.add(ts)
        return ts

    def add_structure_component(
        self,
        typedef_structure: model.TypedefStructure,
        name: str,
        type_ref: str,
        offset: int,
    ) -> model.StructureComponent:
        """Add STRUCTURE_COMPONENT to a TypedefStructure."""
        sc = model.StructureComponent(
            name=name,
            typedefName=type_ref,
            addressOffset=offset,
        )
        typedef_structure.structure_component.append(sc)
        self.session.add(sc)
        return sc

    def add_typedef_axis(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        input_quantity: str,
        deposit_attr: str,
        max_diff: float,
        conversion: str,
        max_axis_points: int,
        lower_limit: float,
        upper_limit: float,
        byte_order: str | None = None,
        deposit_mode: str | None = None,
        extended_limits: tuple[float, float] | None = None,
        format_string: str | None = None,
        monotony: str | None = None,
        phys_unit: str | None = None,
        step_size: float | None = None,
    ) -> model.TypedefAxis:
        """Add TYPEDEF_AXIS to a Module."""
        axis = model.TypedefAxis(
            name=name,
            longIdentifier=long_identifier,
            inputQuantity=input_quantity,
            depositAttr=deposit_attr,
            maxDiff=max_diff,
            conversion=conversion,
            maxAxisPoints=max_axis_points,
            lowerLimit=lower_limit,
            upperLimit=upper_limit,
        )
        axis.module = module
        self.session.add(axis)

        if byte_order:
            bo = model.ByteOrder(byteOrder=byte_order)
            axis.byte_order = bo
            self.session.add(bo)
        if deposit_mode:
            dep = model.Deposit(mode=deposit_mode)
            axis.deposit = dep
            self.session.add(dep)
        if extended_limits:
            el = model.ExtendedLimits(lowerLimit=extended_limits[0], upperLimit=extended_limits[1])
            axis.extended_limits = el
            self.session.add(el)
        if format_string:
            fmt = model.Format(formatString=format_string)
            axis.format = fmt
            self.session.add(fmt)
        if monotony:
            mono = model.Monotony(monotony=monotony)
            axis.monotony = mono
            self.session.add(mono)
        if phys_unit:
            pu = model.PhysUnit(unit=phys_unit)
            axis.phys_unit = pu
            self.session.add(pu)
        if step_size is not None:
            ss = model.StepSize(step_size=step_size)
            axis.step_size = ss
            self.session.add(ss)

        return axis

    def add_typedef_blob(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        size: int,
        address_type: str | None = None,
    ) -> model.TypedefBlob:
        """Add TYPEDEF_BLOB to a Module."""
        tb = model.TypedefBlob(
            name=name,
            longIdentifier=long_identifier,
            size=size,
        )
        tb.module = module
        self.session.add(tb)
        if address_type:
            at = model.AddressType(addressType=address_type)
            tb.address_type = at
            self.session.add(at)
        return tb

    def add_a2ml(self, module: model.Module) -> model.A2ml:
        """Add A2ML block to a Module."""
        a2ml = model.A2ml()
        a2ml.module = module
        self.session.add(a2ml)
        return a2ml

    def add_typedef_measurement(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        datatype: str,
        conversion: str,
        resolution: int,
        accuracy: float,
        lower_limit: float,
        upper_limit: float,
    ) -> model.TypedefMeasurement:
        """Add TYPEDEF_MEASUREMENT to a Module."""
        tm = model.TypedefMeasurement(
            name=name,
            longIdentifier=long_identifier,
            datatype=datatype,
            conversion=conversion,
            resolution=resolution,
            accuracy=accuracy,
            lowerLimit=lower_limit,
            upperLimit=upper_limit,
        )
        tm.module = module
        self.session.add(tm)
        return tm

    def add_typedef_characteristic(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        char_type: str,
        deposit: str,
        max_diff: float,
        conversion: str,
        lower_limit: float,
        upper_limit: float,
    ) -> model.TypedefCharacteristic:
        """Add TYPEDEF_CHARACTERISTIC to a Module."""
        tc = model.TypedefCharacteristic(
            name=name,
            longIdentifier=long_identifier,
            type=char_type,
            deposit=deposit,
            maxDiff=max_diff,
            conversion=conversion,
            lowerLimit=lower_limit,
            upperLimit=upper_limit,
        )
        tc.module = module
        self.session.add(tc)
        return tc

    def add_instance(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        type_name: str,
        address: int,
    ) -> model.Instance:
        """Add INSTANCE to a Module."""
        inst = model.Instance(
            name=name,
            longIdentifier=long_identifier,
            typeName=type_name,
            address=address,
        )
        inst.module = module
        self.session.add(inst)
        return inst

    def add_mod_common(
        self,
        module: model.Module,
        comment: str | None = None,
        byte_order: str | None = None,
        data_size: int | None = None,
        deposit: str | None = None,
        s_rec_layout: str | None = None,
    ) -> model.ModCommon:
        """Add ModCommon to a Module.

        Parameters
        ----------
        module : model.Module
            The Module to add ModCommon to
        comment : Optional[str], optional
            The comment, by default None
        byte_order : Optional[str], optional
            The byte order (e.g., "MSB_FIRST", "MSB_LAST"), by default None
        data_size : Optional[int], optional
            The data size, by default None
        deposit : Optional[str], optional
            The deposit mode (e.g., "ABSOLUTE", "DIFFERENCE"), by default None
        s_rec_layout : Optional[str], optional
            The standard record layout, by default None

        Returns
        -------
        model.ModCommon
            The newly created ModCommon instance
        """
        mod_common = model.ModCommon(comment=comment if comment is not None else "")
        mod_common.module = module
        self.session.add(mod_common)

        # Add byte order if provided
        if byte_order:
            byte_order_obj = model.ByteOrder(byteOrder=byte_order)
            mod_common.byte_order = byte_order_obj
            self.session.add(byte_order_obj)

        # Add data size if provided
        if data_size:
            data_size_obj = model.DataSize(size=data_size)
            mod_common.data_size = data_size_obj
            self.session.add(data_size_obj)

        # Add deposit if provided
        if deposit:
            deposit_obj = model.Deposit(mode=deposit)
            mod_common.deposit = deposit_obj
            self.session.add(deposit_obj)

        # Add s_rec_layout if provided
        if s_rec_layout:
            s_rec_layout_obj = model.SRecLayout(name=s_rec_layout)
            mod_common.s_rec_layout = s_rec_layout_obj
            self.session.add(s_rec_layout_obj)

        return mod_common

    def add_mod_par(
        self,
        module: model.Module,
        comment: str | None = None,
        cpu_type: str | None = None,
        customer: str | None = None,
        customer_no: str | None = None,
        ecu: str | None = None,
        ecu_calibration_offset: int | None = None,
        epk: str | None = None,
        phone_no: str | None = None,
        supplier: str | None = None,
        user: str | None = None,
        version: str | None = None,
        no_of_interfaces: int | None = None,
    ) -> model.ModPar:
        """Add ModPar to a Module.

        Parameters
        ----------
        module : model.Module
            The Module to add ModPar to
        comment : Optional[str], optional
            The comment, by default None
        cpu_type : Optional[str], optional
            The CPU type, by default None
        customer : Optional[str], optional
            The customer name, by default None
        customer_no : Optional[str], optional
            The customer number, by default None
        ecu : Optional[str], optional
            The ECU name, by default None
        ecu_calibration_offset : Optional[int], optional
            The ECU calibration offset, by default None
        epk : Optional[str], optional
            The EPK, by default None
        phone_no : Optional[str], optional
            The phone number, by default None
        supplier : Optional[str], optional
            The supplier name, by default None
        user : Optional[str], optional
            The user name, by default None
        version : Optional[str], optional
            The version, by default None

        Returns
        -------
        model.ModPar
            The newly created ModPar instance
        """
        mod_par = model.ModPar(comment=comment if comment is not None else "")
        mod_par.module = module
        self.session.add(mod_par)

        # Add cpu_type if provided
        if cpu_type:
            cpu_type_obj = model.CpuType(cPU=cpu_type)
            cpu_type_obj.mod_par = mod_par
            self.session.add(cpu_type_obj)

        # Add customer if provided
        if customer:
            customer_obj = model.Customer(customer=customer)
            customer_obj.mod_par = mod_par
            self.session.add(customer_obj)

        # Add customer_no if provided
        if customer_no:
            customer_no_obj = model.CustomerNo(number=customer_no)
            customer_no_obj.mod_par = mod_par
            self.session.add(customer_no_obj)

        # Add ecu if provided
        if ecu:
            ecu_obj = model.Ecu(controlUnit=ecu)
            ecu_obj.mod_par = mod_par
            self.session.add(ecu_obj)

        # Add ecu_calibration_offset if provided
        if ecu_calibration_offset is not None:
            ecu_calibration_offset_obj = model.EcuCalibrationOffset(offset=ecu_calibration_offset)
            ecu_calibration_offset_obj.mod_par = mod_par
            self.session.add(ecu_calibration_offset_obj)

        # Add epk if provided
        if epk:
            epk_obj = model.Epk(identifier=epk)
            epk_obj.mod_par = mod_par
            self.session.add(epk_obj)

        # Add phone_no if provided
        if phone_no:
            phone_no_obj = model.PhoneNo(telnum=phone_no)
            phone_no_obj.mod_par = mod_par
            self.session.add(phone_no_obj)

        # Add supplier if provided
        if supplier:
            supplier_obj = model.Supplier(manufacturer=supplier)
            supplier_obj.mod_par = mod_par
            self.session.add(supplier_obj)

        # Add user if provided
        if user:
            user_obj = model.User(userName=user)
            user_obj.mod_par = mod_par
            self.session.add(user_obj)

        # Add version if provided
        if version:
            version_obj = model.Version(versionIdentifier=version)
            version_obj.mod_par = mod_par
            self.session.add(version_obj)

        if no_of_interfaces is not None:
            noi_obj = model.NoOfInterfaces(num=no_of_interfaces)
            noi_obj.mod_par = mod_par
            self.session.add(noi_obj)

        return mod_par


class InstanceCreator(
    Creator,
    HasAddressType,
    HasAnnotation,
    HasCalibrationAccess,
    HasDisplayIdentifier,
    HasEcuAddressExtension,
    HasIfData,
    HasLayout,
    HasMatrixDim,
    HasMaxRefresh,
    HasModelLink,
    HasReadWrite,
    HasSymbolLink,
):
    """Creator class for Instance entities."""

    def create_instance(
        self,
        name: str,
        long_identifier: str,
        type_name: str,
        address: int,
        module_name: str | None = None,
    ) -> model.Instance:
        module = None
        if module_name:
            module = self.session.query(model.Module).filter(model.Module.name == module_name).first()
            if not module:
                raise exceptions.StructuralError(f"Module '{module_name}' not found")

        inst = model.Instance(
            name=name,
            longIdentifier=long_identifier,
            typeName=type_name,
            address=address,
        )
        if module:
            module.instance.append(inst)
        self.session.add(inst)
        return inst

    def add_addr_epk(self, mod_par: model.ModPar, address: int) -> model.AddrEpk:
        addr = model.AddrEpk(address=address)
        addr.mod_par = mod_par
        self.session.add(addr)
        return addr

    def add_memory_layout(
        self,
        mod_par: model.ModPar,
        prg_type: str,
        address: int,
        size: int,
        offsets: tuple[int, int, int, int, int],
        if_data: str | dict[str, Any] | None = None,
    ) -> model.MemoryLayout:
        ml = model.MemoryLayout(
            prgType=prg_type,
            address=address,
            size=size,
            offset_0=offsets[0],
            offset_1=offsets[1],
            offset_2=offsets[2],
            offset_3=offsets[3],
            offset_4=offsets[4],
        )
        ml.mod_par = mod_par
        self.session.add(ml)
        if if_data is not None:
            self.add_if_data(ml, if_data)
        return ml

    def add_memory_segment(
        self,
        mod_par: model.ModPar,
        name: str,
        long_identifier: str,
        prg_type: str,
        memory_type: str,
        attribute: str,
        address: int,
        size: int,
        offsets: tuple[int, int, int, int, int],
        if_data: str | dict[str, Any] | None = None,
    ) -> model.MemorySegment:
        ms = model.MemorySegment(
            name=name,
            longIdentifier=long_identifier,
            prgType=prg_type,
            memoryType=memory_type,
            attribute=attribute,
            address=address,
            size=size,
            offset_0=offsets[0],
            offset_1=offsets[1],
            offset_2=offsets[2],
            offset_3=offsets[3],
            offset_4=offsets[4],
        )
        ms.mod_par = mod_par
        self.session.add(ms)
        if if_data is not None:
            self.add_if_data(ms, if_data)
        return ms

    def add_system_constant(self, mod_par: model.ModPar, name: str, value: str) -> model.SystemConstant:
        sc = model.SystemConstant(name=name, value=value)
        sc.mod_par = mod_par
        self.session.add(sc)
        return sc

    def add_calibration_method(
        self,
        mod_par: model.ModPar,
        method: str,
        version: int,
        handles: list[int] | None = None,
        handle_text: str | None = None,
    ) -> model.CalibrationMethod:
        cm = model.CalibrationMethod(method=method, version=version)
        cm.mod_par = mod_par
        self.session.add(cm)
        if handles is not None:
            ch = model.CalibrationHandle()
            self.session.add(ch)
            for handle in handles:
                ch._handle.append(model.CalHandles(handle))
            if handle_text is not None:
                cht = model.CalibrationHandleText(text=handle_text)
                cht.calibration_handle = ch
                self.session.add(cht)
            cm.calibration_handle.append(ch)
        return cm


class FunctionCreator(Creator, HasAnnotation, HasIfData):
    """Creator class for Function entities.

    This class provides methods to create new Function instances and
    their related entities (DefCharacteristic, FunctionVersion, etc.).

    Attributes
    ----------
    session : Any
        SQLAlchemy session object used to interact with the database
    """

    def create_function(self, name: str, long_identifier: str, module_name: str | None = None) -> model.Function:
        """Create a new Function instance.

        Parameters
        ----------
        name : str
            Name of the function
        long_identifier : str
            Description of the function
        module_name : Optional[str], optional
            Name of the module to associate with this Function, by default None

        Returns
        -------
        model.Function
            The newly created Function instance
        """
        # Find the module if module_name is provided
        module = None
        if module_name:
            module = self.session.query(model.Module).filter(model.Module.name == module_name).first()
            if not module:
                raise exceptions.StructuralError(f"Module '{module_name}' not found")

        # Create the Function instance
        function = model.Function(name=name, longIdentifier=long_identifier)

        # Associate with module if provided
        if module:
            module.function.append(function)

        # Add to session
        self.session.add(function)

        return function

    def add_def_characteristic(self, function: model.Function, characteristic_names: list[str]) -> model.DefCharacteristic:
        """Add DefCharacteristic to a Function.

        Parameters
        ----------
        function : model.Function
            The Function to add DefCharacteristic to
        characteristic_names : List[str]
            List of characteristic names

        Returns
        -------
        model.DefCharacteristic
            The newly created DefCharacteristic instance
        """
        def_characteristic = model.DefCharacteristic(identifier=characteristic_names)
        def_characteristic.function = function
        self.session.add(def_characteristic)
        return def_characteristic

    def add_function_version(self, function: model.Function, version_identifier: str) -> model.FunctionVersion:
        """Add FunctionVersion to a Function.

        Parameters
        ----------
        function : model.Function
            The Function to add FunctionVersion to
        version_identifier : str
            The version identifier

        Returns
        -------
        model.FunctionVersion
            The newly created FunctionVersion instance
        """
        function_version = model.FunctionVersion(versionIdentifier=version_identifier)
        function_version.function = function
        self.session.add(function_version)
        return function_version

    def add_in_measurement(self, function: model.Function, measurement_names: list[str]) -> model.InMeasurement:
        """Add InMeasurement to a Function.

        Parameters
        ----------
        function : model.Function
            The Function to add InMeasurement to
        measurement_names : List[str]
            List of measurement names

        Returns
        -------
        model.InMeasurement
            The newly created InMeasurement instance
        """
        in_measurement = model.InMeasurement()
        in_measurement.function = function
        self.session.add(in_measurement)

        # Add measurement identifiers
        for meas_name in measurement_names:
            meas_id = model.InMeasurementIdentifiers(identifier=meas_name)
            meas_id.parent = in_measurement
            self.session.add(meas_id)

        return in_measurement

    def add_loc_measurement(self, function: model.Function, measurement_names: list[str]) -> model.LocMeasurement:
        """Add LocMeasurement to a Function.

        Parameters
        ----------
        function : model.Function
            The Function to add LocMeasurement to
        measurement_names : List[str]
            List of measurement names

        Returns
        -------
        model.LocMeasurement
            The newly created LocMeasurement instance
        """
        loc_measurement = model.LocMeasurement()
        loc_measurement.function = function
        self.session.add(loc_measurement)

        # Add measurement identifiers
        for meas_name in measurement_names:
            meas_id = model.LocMeasurementIdentifiers(identifier=meas_name)
            meas_id.parent = loc_measurement
            self.session.add(meas_id)

        return loc_measurement

    def add_out_measurement(self, function: model.Function, measurement_names: list[str]) -> model.OutMeasurement:
        """Add OutMeasurement to a Function.

        Parameters
        ----------
        function : model.Function
            The Function to add OutMeasurement to
        measurement_names : List[str]
            List of measurement names

        Returns
        -------
        model.OutMeasurement
            The newly created OutMeasurement instance
        """
        out_measurement = model.OutMeasurement()
        out_measurement.function = function
        self.session.add(out_measurement)

        # Add measurement identifiers
        for meas_name in measurement_names:
            meas_id = model.OutMeasurementIdentifiers(identifier=meas_name)
            meas_id.parent = out_measurement
            self.session.add(meas_id)

        return out_measurement

    def add_sub_function(self, function: model.Function, function_names: list[str]) -> model.SubFunction:
        """Add SubFunction to a Function.

        Parameters
        ----------
        function : model.Function
            The Function to add SubFunction to
        function_names : List[str]
            List of function names

        Returns
        -------
        model.SubFunction
            The newly created SubFunction instance
        """
        sub_function = model.SubFunction()
        sub_function.function = function
        self.session.add(sub_function)

        # Add function identifiers
        for func_name in function_names:
            func_id = model.SubFunctionIdentifiers(identifier=func_name)
            func_id.parent = sub_function
            self.session.add(func_id)

        return sub_function


class GroupCreator(Creator, HasAnnotation, HasFunctionList, HasIfData):
    """Creator class for Group entities.

    This class provides methods to create new Group instances and
    their related entities (RefMeasurement, RefCharacteristic, etc.).

    Attributes
    ----------
    session : Any
        SQLAlchemy session object used to interact with the database
    """

    def create_group(self, group_name: str, group_long_identifier: str, module_name: str | None = None) -> model.Group:
        """Create a new Group instance.

        Parameters
        ----------
        group_name : str
            Name of the group
        group_long_identifier : str
            Description of the group
        module_name : Optional[str], optional
            Name of the module to associate with this Group, by default None

        Returns
        -------
        model.Group
            The newly created Group instance
        """
        # Find the module if module_name is provided
        module = None
        if module_name:
            module = self.session.query(model.Module).filter(model.Module.name == module_name).first()
            if not module:
                raise exceptions.StructuralError(f"Module '{module_name}' not found")

        # Create the Group instance
        group = model.Group(groupName=group_name, groupLongIdentifier=group_long_identifier)

        # Associate with module if provided
        if module:
            module.group.append(group)

        # Add to session
        self.session.add(group)

        return group

    def add_ref_measurement(self, group: model.Group, measurement_names: list[str]) -> model.RefMeasurement:
        """Add RefMeasurement to a Group.

        Parameters
        ----------
        group : model.Group
            The Group to add RefMeasurement to
        measurement_names : List[str]
            List of measurement names

        Returns
        -------
        model.RefMeasurement
            The newly created RefMeasurement instance
        """
        ref_measurement = model.RefMeasurement(identifier=measurement_names)
        ref_measurement.group = group
        self.session.add(ref_measurement)
        return ref_measurement

    def add_ref_characteristic(self, group: model.Group, characteristic_names: list[str]) -> model.RefCharacteristic:
        """Add RefCharacteristic to a Group.

        Parameters
        ----------
        group : model.Group
            The Group to add RefCharacteristic to
        characteristic_names : List[str]
            List of characteristic names

        Returns
        -------
        model.RefCharacteristic
            The newly created RefCharacteristic instance
        """
        ref_characteristic = model.RefCharacteristic(identifier=characteristic_names)
        ref_characteristic.group = group
        self.session.add(ref_characteristic)
        return ref_characteristic

    def add_sub_group(self, group: model.Group, group_names: list[str]) -> model.SubGroup:
        """Add SubGroup to a Group.

        Parameters
        ----------
        group : model.Group
            The Group to add SubGroup to
        group_names : List[str]
            List of group names

        Returns
        -------
        model.SubGroup
            The newly created SubGroup instance
        """
        sub_group = model.SubGroup(identifier=group_names)
        sub_group.group = group
        self.session.add(sub_group)
        return sub_group

    def add_root(self, group: model.Group) -> model.Root:
        """Add Root to a Group.

        Parameters
        ----------
        group : model.Group
            The Group to add Root to

        Returns
        -------
        model.Root
            The newly created Root instance
        """
        root = model.Root()
        group.root.append(root)
        self.session.add(root)
        return root


class RecordLayoutCreator(Creator):
    """Creator class for RecordLayout entities.

    This class provides methods to create new RecordLayout instances and
    their related entities (AlignmentByte, FncValues, etc.).

    Attributes
    ----------
    session : Any
        SQLAlchemy session object used to interact with the database
    """

    def create_record_layout(self, name: str, module_name: str | None = None) -> model.RecordLayout:
        """Create a new RecordLayout instance.

        Parameters
        ----------
        name : str
            Name of the record layout
        module_name : Optional[str], optional
            Name of the module to associate with this RecordLayout, by default None

        Returns
        -------
        model.RecordLayout
            The newly created RecordLayout instance
        """
        # Find the module if module_name is provided
        module = None
        if module_name:
            module = self.session.query(model.Module).filter(model.Module.name == module_name).first()
            if not module:
                raise exceptions.StructuralError(f"Module '{module_name}' not found")

        # Create the RecordLayout instance
        record_layout = model.RecordLayout(name=name)

        # Associate with module if provided
        if module:
            module.record_layout.append(record_layout)

        # Add to session
        self.session.add(record_layout)

        return record_layout

    @staticmethod
    def _add_position_datatype(record_layout: model.RecordLayout, cls: Any, position: int, data_type: str) -> Any:
        obj = cls(position=position, datatype=data_type)
        obj.record_layout = record_layout
        return obj

    def _add_and_attach(self, record_layout: model.RecordLayout, obj: Any) -> Any:
        obj.record_layout = record_layout
        self.session.add(obj)
        return obj

    def add_alignment_byte(self, record_layout: model.RecordLayout, alignment_border: int) -> model.AlignmentByte:
        """Add AlignmentByte to a RecordLayout.

        Parameters
        ----------
        record_layout : model.RecordLayout
            The RecordLayout to add AlignmentByte to
        alignment_border : int
            The alignment border

        Returns
        -------
        model.AlignmentByte
            The newly created AlignmentByte instance
        """
        alignment_byte = model.AlignmentByte(alignmentBorder=alignment_border)
        alignment_byte.record_layout = record_layout
        self.session.add(alignment_byte)
        return alignment_byte

    def add_alignment_word(self, record_layout: model.RecordLayout, alignment_border: int) -> model.AlignmentWord:
        """Add AlignmentWord to a RecordLayout.

        Parameters
        ----------
        record_layout : model.RecordLayout
            The RecordLayout to add AlignmentWord to
        alignment_border : int
            The alignment border

        Returns
        -------
        model.AlignmentWord
            The newly created AlignmentWord instance
        """
        alignment_word = model.AlignmentWord(alignmentBorder=alignment_border)
        alignment_word.record_layout = record_layout
        self.session.add(alignment_word)
        return alignment_word

    def add_alignment_long(self, record_layout: model.RecordLayout, alignment_border: int) -> model.AlignmentLong:
        """Add AlignmentLong to a RecordLayout.

        Parameters
        ----------
        record_layout : model.RecordLayout
            The RecordLayout to add AlignmentLong to
        alignment_border : int
            The alignment border

        Returns
        -------
        model.AlignmentLong
            The newly created AlignmentLong instance
        """
        alignment_long = model.AlignmentLong(alignmentBorder=alignment_border)
        alignment_long.record_layout = record_layout
        self.session.add(alignment_long)
        return alignment_long

    def add_alignment_float32_ieee(self, record_layout: model.RecordLayout, alignment_border: int) -> model.AlignmentFloat32Ieee:
        """Add AlignmentFloat32Ieee to a RecordLayout.

        Parameters
        ----------
        record_layout : model.RecordLayout
            The RecordLayout to add AlignmentFloat32Ieee to
        alignment_border : int
            The alignment border

        Returns
        -------
        model.AlignmentFloat32Ieee
            The newly created AlignmentFloat32Ieee instance
        """
        alignment_float32_ieee = model.AlignmentFloat32Ieee(alignmentBorder=alignment_border)
        alignment_float32_ieee.record_layout = record_layout
        self.session.add(alignment_float32_ieee)
        return alignment_float32_ieee

    def add_alignment_float64_ieee(self, record_layout: model.RecordLayout, alignment_border: int) -> model.AlignmentFloat64Ieee:
        """Add AlignmentFloat64Ieee to a RecordLayout.

        Parameters
        ----------
        record_layout : model.RecordLayout
            The RecordLayout to add AlignmentFloat64Ieee to
        alignment_border : int
            The alignment border

        Returns
        -------
        model.AlignmentFloat64Ieee
            The newly created AlignmentFloat64Ieee instance
        """
        alignment_float64_ieee = model.AlignmentFloat64Ieee(alignmentBorder=alignment_border)
        alignment_float64_ieee.record_layout = record_layout
        self.session.add(alignment_float64_ieee)
        return alignment_float64_ieee

    def add_alignment_float16_ieee(self, record_layout: model.RecordLayout, alignment_border: int) -> model.AlignmentFloat16Ieee:
        """Add AlignmentFloat16Ieee to a RecordLayout."""
        obj = model.AlignmentFloat16Ieee(alignmentBorder=alignment_border)
        obj.record_layout = record_layout
        self.session.add(obj)
        return obj

    def add_alignment_int64(self, record_layout: model.RecordLayout, alignment_border: int) -> model.AlignmentInt64:
        """Add AlignmentInt64 to a RecordLayout."""
        obj = model.AlignmentInt64(alignmentBorder=alignment_border)
        obj.record_layout = record_layout
        self.session.add(obj)
        return obj

    def add_fnc_values(
        self,
        record_layout: model.RecordLayout,
        position: int,
        data_type: str,
        index_mode: str | None = None,
        address_type: str | None = None,
    ) -> model.FncValues:
        """Add FncValues to a RecordLayout.

        Parameters
        ----------
        record_layout : model.RecordLayout
            The RecordLayout to add FncValues to
        position : int
            The position
        data_type : str
            The data type
        index_mode : Optional[str], optional
            The index mode, by default None
        address_type : Optional[str], optional
            The address type, by default None

        Returns
        -------
        model.FncValues
            The newly created FncValues instance
        """
        fnc_values = model.FncValues(position=position, datatype=data_type)
        if index_mode:
            fnc_values.indexMode = index_mode
        if address_type:
            fnc_values.addresstype = address_type
        fnc_values.record_layout = record_layout
        self.session.add(fnc_values)
        return fnc_values

    def add_axis_pts_x(
        self,
        record_layout: model.RecordLayout,
        position: int,
        data_type: str,
        index_incr: str | None = None,
        addressing: str | None = None,
    ) -> model.AxisPtsX:
        """Add AxisPtsX to a RecordLayout.

        Parameters
        ----------
        record_layout : model.RecordLayout
            The RecordLayout to add AxisPtsX to
        position : int
            The position
        data_type : str
            The data type
        index_incr : Optional[str], optional
            The index increment, by default None
        addressing : Optional[str], optional
            The addressing, by default None

        Returns
        -------
        model.AxisPtsX
            The newly created AxisPtsX instance
        """
        axis_pts_x = model.AxisPtsX(position=position, datatype=data_type, indexIncr=index_incr, addressing=addressing)
        axis_pts_x.record_layout = record_layout
        self.session.add(axis_pts_x)
        return axis_pts_x

    def add_no_axis_pts_x(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.NoAxisPtsX:
        """Add NoAxisPtsX to a RecordLayout.

        Parameters
        ----------
        record_layout : model.RecordLayout
            The RecordLayout to add NoAxisPtsX to
        position : int
            The position
        data_type : str
            The data type

        Returns
        -------
        model.NoAxisPtsX
            The newly created NoAxisPtsX instance
        """
        no_axis_pts_x = model.NoAxisPtsX(position=position, datatype=data_type)
        no_axis_pts_x.record_layout = record_layout
        self.session.add(no_axis_pts_x)
        return no_axis_pts_x

    def add_fix_no_axis_pts_x(self, record_layout: model.RecordLayout, number: int) -> model.FixNoAxisPtsX:
        """Add FixNoAxisPtsX to a RecordLayout.

        Parameters
        ----------
        record_layout : model.RecordLayout
            The RecordLayout to add FixNoAxisPtsX to
        number : int
            The number of axis points

        Returns
        -------
        model.FixNoAxisPtsX
            The newly created FixNoAxisPtsX instance
        """
        fix_no_axis_pts_x = model.FixNoAxisPtsX(numberOfAxisPoints=number)
        fix_no_axis_pts_x.record_layout = record_layout
        self.session.add(fix_no_axis_pts_x)
        return fix_no_axis_pts_x

    def add_axis_pts_y(
        self,
        record_layout: model.RecordLayout,
        position: int,
        data_type: str,
        index_incr: str | None = None,
        addressing: str | None = None,
    ) -> model.AxisPtsY:
        """Add AxisPtsY to a RecordLayout."""
        obj = model.AxisPtsY(position=position, datatype=data_type, indexIncr=index_incr, addressing=addressing)
        return self._add_and_attach(record_layout, obj)

    def add_axis_pts_z(
        self,
        record_layout: model.RecordLayout,
        position: int,
        data_type: str,
        index_incr: str | None = None,
        addressing: str | None = None,
    ) -> model.AxisPtsZ:
        """Add AxisPtsZ to a RecordLayout."""
        obj = model.AxisPtsZ(position=position, datatype=data_type, indexIncr=index_incr, addressing=addressing)
        return self._add_and_attach(record_layout, obj)

    def add_axis_pts_4(
        self,
        record_layout: model.RecordLayout,
        position: int,
        data_type: str,
        index_incr: str | None = None,
        addressing: str | None = None,
    ) -> model.AxisPts4:
        """Add AxisPts4 to a RecordLayout."""
        obj = model.AxisPts4(position=position, datatype=data_type, indexIncr=index_incr, addressing=addressing)
        return self._add_and_attach(record_layout, obj)

    def add_axis_pts_5(
        self,
        record_layout: model.RecordLayout,
        position: int,
        data_type: str,
        index_incr: str | None = None,
        addressing: str | None = None,
    ) -> model.AxisPts5:
        """Add AxisPts5 to a RecordLayout."""
        obj = model.AxisPts5(position=position, datatype=data_type, indexIncr=index_incr, addressing=addressing)
        return self._add_and_attach(record_layout, obj)

    def add_axis_rescale_x(
        self,
        record_layout: model.RecordLayout,
        position: int,
        data_type: str,
        max_pairs: int,
        index_incr: str | None = None,
        addressing: str | None = None,
    ) -> model.AxisRescaleX:
        """Add AxisRescaleX to a RecordLayout."""
        obj = model.AxisRescaleX(
            position=position,
            datatype=data_type,
            maxNumberOfRescalePairs=max_pairs,
            indexIncr=index_incr,
            addressing=addressing,
        )
        return self._add_and_attach(record_layout, obj)

    def add_axis_rescale_y(
        self,
        record_layout: model.RecordLayout,
        position: int,
        data_type: str,
        max_pairs: int,
        index_incr: str | None = None,
        addressing: str | None = None,
    ) -> model.AxisRescaleY:
        """Add AxisRescaleY to a RecordLayout."""
        obj = model.AxisRescaleY(
            position=position,
            datatype=data_type,
            maxNumberOfRescalePairs=max_pairs,
            indexIncr=index_incr,
            addressing=addressing,
        )
        return self._add_and_attach(record_layout, obj)

    def add_axis_rescale_z(
        self,
        record_layout: model.RecordLayout,
        position: int,
        data_type: str,
        max_pairs: int,
        index_incr: str | None = None,
        addressing: str | None = None,
    ) -> model.AxisRescaleZ:
        """Add AxisRescaleZ to a RecordLayout."""
        obj = model.AxisRescaleZ(
            position=position,
            datatype=data_type,
            maxNumberOfRescalePairs=max_pairs,
            indexIncr=index_incr,
            addressing=addressing,
        )
        return self._add_and_attach(record_layout, obj)

    def add_axis_rescale_4(
        self,
        record_layout: model.RecordLayout,
        position: int,
        data_type: str,
        max_pairs: int,
        index_incr: str | None = None,
        addressing: str | None = None,
    ) -> model.AxisRescale4:
        """Add AxisRescale4 to a RecordLayout."""
        obj = model.AxisRescale4(
            position=position,
            datatype=data_type,
            maxNumberOfRescalePairs=max_pairs,
            indexIncr=index_incr,
            addressing=addressing,
        )
        return self._add_and_attach(record_layout, obj)

    def add_axis_rescale_5(
        self,
        record_layout: model.RecordLayout,
        position: int,
        data_type: str,
        max_pairs: int,
        index_incr: str | None = None,
        addressing: str | None = None,
    ) -> model.AxisRescale5:
        """Add AxisRescale5 to a RecordLayout."""
        obj = model.AxisRescale5(
            position=position,
            datatype=data_type,
            maxNumberOfRescalePairs=max_pairs,
            indexIncr=index_incr,
            addressing=addressing,
        )
        return self._add_and_attach(record_layout, obj)

    def add_dist_op_x(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.DistOpX:
        """Add DistOpX to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.DistOpX, position, data_type)
        self.session.add(obj)
        return obj

    def add_dist_op_y(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.DistOpY:
        """Add DistOpY to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.DistOpY, position, data_type)
        self.session.add(obj)
        return obj

    def add_dist_op_z(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.DistOpZ:
        """Add DistOpZ to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.DistOpZ, position, data_type)
        self.session.add(obj)
        return obj

    def add_dist_op_4(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.DistOp4:
        """Add DistOp4 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.DistOp4, position, data_type)
        self.session.add(obj)
        return obj

    def add_dist_op_5(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.DistOp5:
        """Add DistOp5 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.DistOp5, position, data_type)
        self.session.add(obj)
        return obj

    def add_fix_no_axis_pts_y(self, record_layout: model.RecordLayout, number: int) -> model.FixNoAxisPtsY:
        """Add FixNoAxisPtsY to a RecordLayout."""
        obj = model.FixNoAxisPtsY(numberOfAxisPoints=number)
        return self._add_and_attach(record_layout, obj)

    def add_fix_no_axis_pts_z(self, record_layout: model.RecordLayout, number: int) -> model.FixNoAxisPtsZ:
        """Add FixNoAxisPtsZ to a RecordLayout."""
        obj = model.FixNoAxisPtsZ(numberOfAxisPoints=number)
        return self._add_and_attach(record_layout, obj)

    def add_fix_no_axis_pts_4(self, record_layout: model.RecordLayout, number: int) -> model.FixNoAxisPts4:
        """Add FixNoAxisPts4 to a RecordLayout."""
        obj = model.FixNoAxisPts4(numberOfAxisPoints=number)
        return self._add_and_attach(record_layout, obj)

    def add_fix_no_axis_pts_5(self, record_layout: model.RecordLayout, number: int) -> model.FixNoAxisPts5:
        """Add FixNoAxisPts5 to a RecordLayout."""
        obj = model.FixNoAxisPts5(numberOfAxisPoints=number)
        return self._add_and_attach(record_layout, obj)

    def add_identification(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.Identification:
        """Add Identification to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.Identification, position, data_type)
        self.session.add(obj)
        return obj

    def add_no_axis_pts_y(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.NoAxisPtsY:
        """Add NoAxisPtsY to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.NoAxisPtsY, position, data_type)
        self.session.add(obj)
        return obj

    def add_no_axis_pts_z(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.NoAxisPtsZ:
        """Add NoAxisPtsZ to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.NoAxisPtsZ, position, data_type)
        self.session.add(obj)
        return obj

    def add_no_axis_pts_4(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.NoAxisPts4:
        """Add NoAxisPts4 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.NoAxisPts4, position, data_type)
        self.session.add(obj)
        return obj

    def add_no_axis_pts_5(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.NoAxisPts5:
        """Add NoAxisPts5 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.NoAxisPts5, position, data_type)
        self.session.add(obj)
        return obj

    def add_no_rescale_x(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.NoRescaleX:
        """Add NoRescaleX to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.NoRescaleX, position, data_type)
        self.session.add(obj)
        return obj

    def add_no_rescale_y(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.NoRescaleY:
        """Add NoRescaleY to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.NoRescaleY, position, data_type)
        self.session.add(obj)
        return obj

    def add_no_rescale_z(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.NoRescaleZ:
        """Add NoRescaleZ to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.NoRescaleZ, position, data_type)
        self.session.add(obj)
        return obj

    def add_no_rescale_4(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.NoRescale4:
        """Add NoRescale4 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.NoRescale4, position, data_type)
        self.session.add(obj)
        return obj

    def add_no_rescale_5(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.NoRescale5:
        """Add NoRescale5 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.NoRescale5, position, data_type)
        self.session.add(obj)
        return obj

    def add_offset_x(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.OffsetX:
        """Add OffsetX to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.OffsetX, position, data_type)
        self.session.add(obj)
        return obj

    def add_offset_y(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.OffsetY:
        """Add OffsetY to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.OffsetY, position, data_type)
        self.session.add(obj)
        return obj

    def add_offset_z(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.OffsetZ:
        """Add OffsetZ to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.OffsetZ, position, data_type)
        self.session.add(obj)
        return obj

    def add_offset_4(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.Offset4:
        """Add Offset4 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.Offset4, position, data_type)
        self.session.add(obj)
        return obj

    def add_offset_5(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.Offset5:
        """Add Offset5 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.Offset5, position, data_type)
        self.session.add(obj)
        return obj

    def add_reserved(self, record_layout: model.RecordLayout, position: int, data_size: str) -> model.Reserved:
        """Add Reserved to a RecordLayout."""
        obj = model.Reserved(position=position, dataSize=data_size)
        record_layout.reserved.append(obj)
        self.session.add(obj)
        return obj

    def add_rip_addr_w(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.RipAddrW:
        """Add RipAddrW to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.RipAddrW, position, data_type)
        self.session.add(obj)
        return obj

    def add_rip_addr_x(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.RipAddrX:
        """Add RipAddrX to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.RipAddrX, position, data_type)
        self.session.add(obj)
        return obj

    def add_rip_addr_y(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.RipAddrY:
        """Add RipAddrY to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.RipAddrY, position, data_type)
        self.session.add(obj)
        return obj

    def add_rip_addr_z(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.RipAddrZ:
        """Add RipAddrZ to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.RipAddrZ, position, data_type)
        self.session.add(obj)
        return obj

    def add_rip_addr_4(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.RipAddr4:
        """Add RipAddr4 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.RipAddr4, position, data_type)
        self.session.add(obj)
        return obj

    def add_rip_addr_5(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.RipAddr5:
        """Add RipAddr5 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.RipAddr5, position, data_type)
        self.session.add(obj)
        return obj

    def add_shift_op_x(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.ShiftOpX:
        """Add ShiftOpX to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.ShiftOpX, position, data_type)
        self.session.add(obj)
        return obj

    def add_shift_op_y(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.ShiftOpY:
        """Add ShiftOpY to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.ShiftOpY, position, data_type)
        self.session.add(obj)
        return obj

    def add_shift_op_z(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.ShiftOpZ:
        """Add ShiftOpZ to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.ShiftOpZ, position, data_type)
        self.session.add(obj)
        return obj

    def add_shift_op_4(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.ShiftOp4:
        """Add ShiftOp4 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.ShiftOp4, position, data_type)
        self.session.add(obj)
        return obj

    def add_shift_op_5(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.ShiftOp5:
        """Add ShiftOp5 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.ShiftOp5, position, data_type)
        self.session.add(obj)
        return obj

    def add_src_addr_x(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.SrcAddrX:
        """Add SrcAddrX to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.SrcAddrX, position, data_type)
        self.session.add(obj)
        return obj

    def add_src_addr_y(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.SrcAddrY:
        """Add SrcAddrY to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.SrcAddrY, position, data_type)
        self.session.add(obj)
        return obj

    def add_src_addr_z(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.SrcAddrZ:
        """Add SrcAddrZ to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.SrcAddrZ, position, data_type)
        self.session.add(obj)
        return obj

    def add_src_addr_4(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.SrcAddr4:
        """Add SrcAddr4 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.SrcAddr4, position, data_type)
        self.session.add(obj)
        return obj

    def add_src_addr_5(self, record_layout: model.RecordLayout, position: int, data_type: str) -> model.SrcAddr5:
        """Add SrcAddr5 to a RecordLayout."""
        obj = self._add_position_datatype(record_layout, model.SrcAddr5, position, data_type)
        self.session.add(obj)
        return obj

    def set_static_record_layout(self, record_layout: model.RecordLayout, enabled: bool = True) -> bool:
        """Set STATIC_RECORD_LAYOUT flag on a RecordLayout."""
        record_layout.static_record_layout = enabled
        return enabled

    def set_static_address_offsets(self, record_layout: model.RecordLayout, enabled: bool = True) -> bool:
        """Set STATIC_ADDRESS_OFFSETS flag on a RecordLayout."""
        record_layout.static_address_offsets = enabled
        return enabled
