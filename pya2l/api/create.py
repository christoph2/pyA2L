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

   (C) 2020-2025 by Christoph Schueler <cpu12.gems@googlemail.com>

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
        self, name: str, long_identifier: str, conversion_type: str, format_str: str, unit: str, module_name: Optional[str] = None
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
            compu_method.module = module

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

    def add_formula(self, compu_method: model.CompuMethod, formula_str: str, formula_inv: Optional[str] = None) -> model.Formula:
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


class MeasurementCreator(Creator):
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
        module_name: Optional[str] = None,
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
            measurement.module = module

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

    def add_bit_operation(
        self,
        measurement: model.Measurement,
        left_shift: Optional[int] = None,
        right_shift: Optional[int] = None,
        sign_extend: Optional[bool] = None,
    ) -> model.BitOperation:
        """Add BitOperation to a Measurement.

        Parameters
        ----------
        measurement : model.Measurement
            The Measurement to add BitOperation to
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
        bit_operation.measurement = measurement
        self.session.add(bit_operation)

        # Add left shift if provided
        if left_shift is not None:
            left_shift_obj = model.LeftShift(bitCount=left_shift)
            left_shift_obj.bit_operation = bit_operation
            self.session.add(left_shift_obj)

        # Add right shift if provided
        if right_shift is not None:
            right_shift_obj = model.RightShift(bitCount=right_shift)
            right_shift_obj.bit_operation = bit_operation
            self.session.add(right_shift_obj)

        # Add sign extend if provided
        if sign_extend is not None:
            sign_extend_obj = model.SignExtend()
            sign_extend_obj.bit_operation = bit_operation
            self.session.add(sign_extend_obj)

        return bit_operation

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

    def add_matrix_dim(
        self, measurement: model.Measurement, x_dim: int, y_dim: Optional[int] = None, z_dim: Optional[int] = None
    ) -> model.MatrixDim:
        """Add MatrixDim to a Measurement.

        Parameters
        ----------
        measurement : model.Measurement
            The Measurement to add MatrixDim to
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
        matrix_dim = model.MatrixDim(xDim=x_dim, yDim=y_dim if y_dim is not None else 0, zDim=z_dim if z_dim is not None else 0)
        matrix_dim.measurement = measurement
        self.session.add(matrix_dim)
        return matrix_dim

    def add_format(self, measurement: model.Measurement, format_string: str) -> model.Format:
        """Add Format to a Measurement.

        Parameters
        ----------
        measurement : model.Measurement
            The Measurement to add Format to
        format_string : str
            The format string

        Returns
        -------
        model.Format
            The newly created Format instance
        """
        format_obj = model.Format(formatString=format_string)
        format_obj.measurement = measurement
        self.session.add(format_obj)
        return format_obj

    def add_phys_unit(self, measurement: model.Measurement, unit: str) -> model.PhysUnit:
        """Add PhysUnit to a Measurement.

        Parameters
        ----------
        measurement : model.Measurement
            The Measurement to add PhysUnit to
        unit : str
            The physical unit

        Returns
        -------
        model.PhysUnit
            The newly created PhysUnit instance
        """
        phys_unit = model.PhysUnit(unit=unit)
        phys_unit.measurement = measurement
        self.session.add(phys_unit)
        return phys_unit

    def add_symbol_link(self, measurement: model.Measurement, symbol_name: str, offset: Optional[int] = None) -> model.SymbolLink:
        """Add SymbolLink to a Measurement.

        Parameters
        ----------
        measurement : model.Measurement
            The Measurement to add SymbolLink to
        symbol_name : str
            The symbol name
        offset : Optional[int], optional
            The offset, by default None

        Returns
        -------
        model.SymbolLink
            The newly created SymbolLink instance
        """
        symbol_link = model.SymbolLink(symbolName=symbol_name, offset=offset if offset is not None else 0)
        symbol_link.measurement = measurement
        self.session.add(symbol_link)
        return symbol_link

    def add_virtual(self, measurement: model.Measurement, measuring_channel: Optional[List[str]] = None) -> model.Virtual:
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
        virtual = model.Virtual()
        virtual.measurement = measurement
        self.session.add(virtual)

        # Add measuring channels if provided
        if measuring_channel:
            for channel in measuring_channel:
                channel_obj = model.VirtualMeasuringChannels(measuringChannel=channel)
                channel_obj.virtual = virtual
                self.session.add(channel_obj)

        return virtual


class AxisPtsCreator(Creator):
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
        module_name: Optional[str] = None,
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
            axis_pts.module = module

        # Add to session
        self.session.add(axis_pts)

        return axis_pts

    def add_byte_order(self, axis_pts: model.AxisPts, byte_order: str) -> model.ByteOrder:
        """Add ByteOrder to an AxisPts.

        Parameters
        ----------
        axis_pts : model.AxisPts
            The AxisPts to add ByteOrder to
        byte_order : str
            The byte order (e.g., "MSB_FIRST", "MSB_LAST")

        Returns
        -------
        model.ByteOrder
            The newly created ByteOrder instance
        """
        byte_order_obj = model.ByteOrder(byteOrder=byte_order)
        byte_order_obj.axis_pts = axis_pts
        self.session.add(byte_order_obj)
        return byte_order_obj

    def add_calibration_access(self, axis_pts: model.AxisPts, calibration_access: str) -> model.CalibrationAccess:
        """Add CalibrationAccess to an AxisPts.

        Parameters
        ----------
        axis_pts : model.AxisPts
            The AxisPts to add CalibrationAccess to
        calibration_access : str
            The calibration access (e.g., "CALIBRATION", "NO_CALIBRATION")

        Returns
        -------
        model.CalibrationAccess
            The newly created CalibrationAccess instance
        """
        calibration_access_obj = model.CalibrationAccess(type=calibration_access)
        calibration_access_obj.axis_pts = axis_pts
        self.session.add(calibration_access_obj)
        return calibration_access_obj

    def add_deposit(self, axis_pts: model.AxisPts, mode: str) -> model.Deposit:
        """Add Deposit to an AxisPts.

        Parameters
        ----------
        axis_pts : model.AxisPts
            The AxisPts to add Deposit to
        mode : str
            The deposit mode (e.g., "ABSOLUTE", "DIFFERENCE")

        Returns
        -------
        model.Deposit
            The newly created Deposit instance
        """
        deposit = model.Deposit(mode=mode)
        deposit.axis_pts = axis_pts
        self.session.add(deposit)
        return deposit

    def add_extended_limits(self, axis_pts: model.AxisPts, lower_limit: float, upper_limit: float) -> model.ExtendedLimits:
        """Add ExtendedLimits to an AxisPts.

        Parameters
        ----------
        axis_pts : model.AxisPts
            The AxisPts to add ExtendedLimits to
        lower_limit : float
            The lower limit
        upper_limit : float
            The upper limit

        Returns
        -------
        model.ExtendedLimits
            The newly created ExtendedLimits instance
        """
        extended_limits = model.ExtendedLimits(lowerLimit=lower_limit, upperLimit=upper_limit)
        extended_limits.axis_pts = axis_pts
        self.session.add(extended_limits)
        return extended_limits

    def add_format(self, axis_pts: model.AxisPts, format_string: str) -> model.Format:
        """Add Format to an AxisPts.

        Parameters
        ----------
        axis_pts : model.AxisPts
            The AxisPts to add Format to
        format_string : str
            The format string

        Returns
        -------
        model.Format
            The newly created Format instance
        """
        format_obj = model.Format(formatString=format_string)
        format_obj.axis_pts = axis_pts
        self.session.add(format_obj)
        return format_obj

    def add_monotony(self, axis_pts: model.AxisPts, monotony: str) -> model.Monotony:
        """Add Monotony to an AxisPts.

        Parameters
        ----------
        axis_pts : model.AxisPts
            The AxisPts to add Monotony to
        monotony : str
            The monotony (e.g., "MON_INCREASE", "MON_DECREASE", "STRICT_INCREASE", "STRICT_DECREASE")

        Returns
        -------
        model.Monotony
            The newly created Monotony instance
        """
        monotony_obj = model.Monotony(monotony=monotony)
        monotony_obj.axis_pts = axis_pts
        self.session.add(monotony_obj)
        return monotony_obj

    def add_phys_unit(self, axis_pts: model.AxisPts, unit: str) -> model.PhysUnit:
        """Add PhysUnit to an AxisPts.

        Parameters
        ----------
        axis_pts : model.AxisPts
            The AxisPts to add PhysUnit to
        unit : str
            The physical unit

        Returns
        -------
        model.PhysUnit
            The newly created PhysUnit instance
        """
        phys_unit = model.PhysUnit(unit=unit)
        phys_unit.axis_pts = axis_pts
        self.session.add(phys_unit)
        return phys_unit

    def add_step_size(self, axis_pts: model.AxisPts, step_size: float) -> model.StepSize:
        """Add StepSize to an AxisPts.

        Parameters
        ----------
        axis_pts : model.AxisPts
            The AxisPts to add StepSize to
        step_size : float
            The step size

        Returns
        -------
        model.StepSize
            The newly created StepSize instance
        """
        step_size_obj = model.StepSize(stepSize=step_size)
        step_size_obj.axis_pts = axis_pts
        self.session.add(step_size_obj)
        return step_size_obj

    def add_symbol_link(self, axis_pts: model.AxisPts, symbol_name: str, offset: Optional[int] = None) -> model.SymbolLink:
        """Add SymbolLink to an AxisPts.

        Parameters
        ----------
        axis_pts : model.AxisPts
            The AxisPts to add SymbolLink to
        symbol_name : str
            The symbol name
        offset : Optional[int], optional
            The offset, by default None

        Returns
        -------
        model.SymbolLink
            The newly created SymbolLink instance
        """
        symbol_link = model.SymbolLink(symbolName=symbol_name, offset=offset if offset is not None else 0)
        symbol_link.axis_pts = axis_pts
        self.session.add(symbol_link)
        return symbol_link


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


class ModuleCreator(Creator):
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

    def create_module(self, name: str, long_identifier: str, project: Optional[model.Project] = None) -> model.Module:
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
        module = model.Module(name=name, longIdentifier=long_identifier)

        # Associate with project if provided
        if project:
            module.project = project

        # Add to session
        self.session.add(module)

        return module

    def add_if_data(self, module: model.Module, if_data_text: str) -> model.IfData:
        """Add IF_DATA to a Module.

        Parameters
        ----------
        module : model.Module
            The Module to add IF_DATA to
        if_data_text : str
            The IF_DATA text content

        Returns
        -------
        model.IfData
            The newly created IfData instance
        """
        if_data = model.IfData(content=if_data_text)
        if_data.module = module
        self.session.add(if_data)
        return if_data

    def add_variant_coding(
        self, module: model.Module, var_separator: Optional[str] = None, var_naming: Optional[str] = None
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
        self, module: model.Module, user_level_id: str, read_only: bool = False, ref_group: Optional[str] = None
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
        type_str: Optional[str] = None,
        ref_unit: Optional[str] = None,
        unit_conversion: Optional[Dict[str, float]] = None,
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
        unit.module = module
        self.session.add(unit)

        # Add ref_unit if provided
        if ref_unit:
            ref_unit_obj = model.RefUnit(unit=ref_unit)
            ref_unit_obj.unit = unit
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
        pairs: List[Tuple[float, float]],
        default_numeric: Optional[float] = None,
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
        pairs: List[Tuple[float, str]],
        default_value: Optional[str] = None,
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
            dv = model.DefaultValue(value=str(default_value))
            dv.compu_vtab = vt
            self.session.add(dv)
        return vt

    def add_compu_vtab_range(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        triples: List[Tuple[float, float, str]],
        default_value: Optional[str] = None,
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
            dv = model.DefaultValue(value=str(default_value))
            dv.compu_vtab_range = vr
            self.session.add(dv)
        return vr

    def add_blob(
        self,
        module: model.Module,
        name: str,
        long_identifier: str,
        address: int,
        length: int,
        calibration_access: Optional[str] = None,
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
        in_objects: Optional[List[str]] = None,
        out_objects: Optional[List[str]] = None,
    ) -> model.Transformer:
        """Add TRANSFORMER to a Module."""
        tr = model.Transformer(
            name=name,
            version=version,
            dllname32=dllname32,
            dllname64=dllname64,
            timeout=timeout,
            trigger=trigger,
            reverse=reverse,
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
        measurements: Optional[List[str]] = None,
        if_data_texts: Optional[List[str]] = None,
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
                idata = model.IfData(content=txt)
                idata.frame = fr
                self.session.add(idata)
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
            type_ref=type_ref,
            offset=offset,
        )
        sc.typedef_structure = typedef_structure
        self.session.add(sc)
        return sc

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
        comment: Optional[str] = None,
        byte_order: Optional[str] = None,
        data_size: Optional[int] = None,
        deposit: Optional[str] = None,
        s_rec_layout: Optional[str] = None,
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
        mod_common = model.ModCommon(comment=comment)
        mod_common.module = module
        self.session.add(mod_common)

        # Add byte order if provided
        if byte_order:
            byte_order_obj = model.ByteOrder(byteOrder=byte_order)
            byte_order_obj.mod_common = mod_common
            self.session.add(byte_order_obj)

        # Add data size if provided
        if data_size:
            data_size_obj = model.DataSize(size=data_size)
            data_size_obj.mod_common = mod_common
            self.session.add(data_size_obj)

        # Add deposit if provided
        if deposit:
            deposit_obj = model.Deposit(mode=deposit)
            deposit_obj.mod_common = mod_common
            self.session.add(deposit_obj)

        # Add s_rec_layout if provided
        if s_rec_layout:
            s_rec_layout_obj = model.SRecLayout(name=s_rec_layout)
            s_rec_layout_obj.mod_common = mod_common
            self.session.add(s_rec_layout_obj)

        return mod_common

    def add_mod_par(
        self,
        module: model.Module,
        comment: Optional[str] = None,
        cpu_type: Optional[str] = None,
        customer: Optional[str] = None,
        customer_no: Optional[str] = None,
        ecu: Optional[str] = None,
        ecu_calibration_offset: Optional[int] = None,
        epk: Optional[str] = None,
        phone_no: Optional[str] = None,
        supplier: Optional[str] = None,
        user: Optional[str] = None,
        version: Optional[str] = None,
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
        mod_par = model.ModPar(comment=comment)
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

        return mod_par


class CharacteristicCreator(Creator):
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
        module_name: Optional[str] = None,
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
            characteristic.module = module

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
        axis_descr.characteristic = characteristic
        self.session.add(axis_descr)
        return axis_descr

    def add_bit_mask(self, characteristic: model.Characteristic, mask: int) -> model.BitMask:
        """Add BitMask to a Characteristic.

        Parameters
        ----------
        characteristic : model.Characteristic
            The Characteristic to add BitMask to
        mask : int
            The bit mask

        Returns
        -------
        model.BitMask
            The newly created BitMask instance
        """
        bit_mask = model.BitMask(mask=mask)
        bit_mask.characteristic = characteristic
        self.session.add(bit_mask)
        return bit_mask

    def add_byte_order(self, characteristic: model.Characteristic, byte_order: str) -> model.ByteOrder:
        """Add ByteOrder to a Characteristic.

        Parameters
        ----------
        characteristic : model.Characteristic
            The Characteristic to add ByteOrder to
        byte_order : str
            The byte order (e.g., "MSB_FIRST", "MSB_LAST")

        Returns
        -------
        model.ByteOrder
            The newly created ByteOrder instance
        """
        byte_order_obj = model.ByteOrder(byteOrder=byte_order)
        byte_order_obj.characteristic = characteristic
        self.session.add(byte_order_obj)
        return byte_order_obj

    def add_matrix_dim(
        self, characteristic: model.Characteristic, x_dim: int, y_dim: Optional[int] = None, z_dim: Optional[int] = None
    ) -> model.MatrixDim:
        """Add MatrixDim to a Characteristic.

        Parameters
        ----------
        characteristic : model.Characteristic
            The Characteristic to add MatrixDim to
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
        matrix_dim = model.MatrixDim(xDim=x_dim, yDim=y_dim if y_dim is not None else 0, zDim=z_dim if z_dim is not None else 0)
        matrix_dim.characteristic = characteristic
        self.session.add(matrix_dim)
        return matrix_dim

    def add_dependent_characteristic(
        self, characteristic: model.Characteristic, formula: str, characteristic_names: List[str]
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
        dependent_characteristic = model.DependentCharacteristic(formula=formula)
        dependent_characteristic.characteristic = characteristic
        self.session.add(dependent_characteristic)

        # Add characteristic identifiers
        for char_name in characteristic_names:
            char_id = model.DependentCharacteristicIdentifiers(characteristic=char_name)
            char_id.dependent_characteristic = dependent_characteristic
            self.session.add(char_id)

        return dependent_characteristic

    def add_virtual_characteristic(
        self, characteristic: model.Characteristic, formula: str, characteristic_names: List[str]
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
        virtual_characteristic = model.VirtualCharacteristic(formula=formula)
        virtual_characteristic.characteristic = characteristic
        self.session.add(virtual_characteristic)

        # Add characteristic identifiers
        for char_name in characteristic_names:
            char_id = model.VirtualCharacteristicIdentifiers(characteristic=char_name)
            char_id.virtual_characteristic = virtual_characteristic
            self.session.add(char_id)

        return virtual_characteristic

    def add_format(self, characteristic: model.Characteristic, format_string: str) -> model.Format:
        """Add Format to a Characteristic.

        Parameters
        ----------
        characteristic : model.Characteristic
            The Characteristic to add Format to
        format_string : str
            The format string

        Returns
        -------
        model.Format
            The newly created Format instance
        """
        format_obj = model.Format(formatString=format_string)
        format_obj.characteristic = characteristic
        self.session.add(format_obj)
        return format_obj

    def add_phys_unit(self, characteristic: model.Characteristic, unit: str) -> model.PhysUnit:
        """Add PhysUnit to a Characteristic.

        Parameters
        ----------
        characteristic : model.Characteristic
            The Characteristic to add PhysUnit to
        unit : str
            The physical unit

        Returns
        -------
        model.PhysUnit
            The newly created PhysUnit instance
        """
        phys_unit = model.PhysUnit(unit=unit)
        phys_unit.characteristic = characteristic
        self.session.add(phys_unit)
        return phys_unit

    def add_symbol_link(
        self, characteristic: model.Characteristic, symbol_name: str, offset: Optional[int] = None
    ) -> model.SymbolLink:
        """Add SymbolLink to a Characteristic.

        Parameters
        ----------
        characteristic : model.Characteristic
            The Characteristic to add SymbolLink to
        symbol_name : str
            The symbol name
        offset : Optional[int], optional
            The offset, by default None

        Returns
        -------
        model.SymbolLink
            The newly created SymbolLink instance
        """
        symbol_link = model.SymbolLink(symbolName=symbol_name, offset=offset if offset is not None else 0)
        symbol_link.characteristic = characteristic
        self.session.add(symbol_link)
        return symbol_link


class FunctionCreator(Creator):
    """Creator class for Function entities.

    This class provides methods to create new Function instances and
    their related entities (DefCharacteristic, FunctionVersion, etc.).

    Attributes
    ----------
    session : Any
        SQLAlchemy session object used to interact with the database
    """

    def create_function(self, name: str, long_identifier: str, module_name: Optional[str] = None) -> model.Function:
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
            function.module = module

        # Add to session
        self.session.add(function)

        return function

    def add_def_characteristic(self, function: model.Function, characteristic_names: List[str]) -> model.DefCharacteristic:
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
        def_characteristic = model.DefCharacteristic()
        def_characteristic.function = function
        self.session.add(def_characteristic)

        # Add characteristic identifiers
        for char_name in characteristic_names:
            char_id = model.DefCharacteristicIdentifiers(identifier=char_name)
            char_id.parent = def_characteristic
            self.session.add(char_id)

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

    def add_in_measurement(self, function: model.Function, measurement_names: List[str]) -> model.InMeasurement:
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

    def add_loc_measurement(self, function: model.Function, measurement_names: List[str]) -> model.LocMeasurement:
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

    def add_out_measurement(self, function: model.Function, measurement_names: List[str]) -> model.OutMeasurement:
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

    def add_sub_function(self, function: model.Function, function_names: List[str]) -> model.SubFunction:
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


class GroupCreator(Creator):
    """Creator class for Group entities.

    This class provides methods to create new Group instances and
    their related entities (RefMeasurement, RefCharacteristic, etc.).

    Attributes
    ----------
    session : Any
        SQLAlchemy session object used to interact with the database
    """

    def create_group(self, group_name: str, group_long_identifier: str, module_name: Optional[str] = None) -> model.Group:
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
            group.module = module

        # Add to session
        self.session.add(group)

        return group

    def add_ref_measurement(self, group: model.Group, measurement_names: List[str]) -> model.RefMeasurement:
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
        ref_measurement = model.RefMeasurement()
        ref_measurement.group = group
        self.session.add(ref_measurement)

        # Add measurement identifiers
        for meas_name in measurement_names:
            meas_id = model.RefMeasurementIdentifiers(identifier=meas_name)
            meas_id.parent = ref_measurement
            self.session.add(meas_id)

        return ref_measurement

    def add_ref_characteristic(self, group: model.Group, characteristic_names: List[str]) -> model.RefCharacteristic:
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
        ref_characteristic = model.RefCharacteristic()
        ref_characteristic.group = group
        self.session.add(ref_characteristic)

        # Add characteristic identifiers
        for char_name in characteristic_names:
            char_id = model.RefCharacteristicIdentifiers(identifier=char_name)
            char_id.parent = ref_characteristic
            self.session.add(char_id)

        return ref_characteristic

    def add_function_list(self, group: model.Group, function_names: List[str]) -> model.FunctionList:
        """Add FunctionList to a Group.

        Parameters
        ----------
        group : model.Group
            The Group to add FunctionList to
        function_names : List[str]
            List of function names

        Returns
        -------
        model.FunctionList
            The newly created FunctionList instance
        """
        function_list = model.FunctionList()
        function_list.group = group
        self.session.add(function_list)

        # Add function identifiers
        for func_name in function_names:
            func_id = model.FunctionListIdentifiers(name=func_name)
            func_id.parent = function_list
            self.session.add(func_id)

        return function_list

    def add_sub_group(self, group: model.Group, group_names: List[str]) -> model.SubGroup:
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
        sub_group = model.SubGroup()
        sub_group.group = group
        self.session.add(sub_group)

        # Add group identifiers
        for group_name in group_names:
            group_id = model.SubGroupIdentifiers(identifier=group_name)
            group_id.parent = sub_group
            self.session.add(group_id)

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
        root.group = group
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

    def create_record_layout(self, name: str, module_name: Optional[str] = None) -> model.RecordLayout:
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
            record_layout.module = module

        # Add to session
        self.session.add(record_layout)

        return record_layout

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

    def add_fnc_values(
        self,
        record_layout: model.RecordLayout,
        position: int,
        data_type: str,
        index_mode: Optional[str] = None,
        address_type: Optional[str] = None,
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
        fnc_values = model.FncValues(position=position, datatype=data_type, indexMode=index_mode, addresstype=address_type)
        fnc_values.record_layout = record_layout
        self.session.add(fnc_values)
        return fnc_values

    def add_axis_pts_x(
        self,
        record_layout: model.RecordLayout,
        position: int,
        data_type: str,
        index_incr: Optional[str] = None,
        addressing: Optional[str] = None,
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
