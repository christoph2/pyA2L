#!/usr/bin/env python
"""Tests for the pya2l.api.create module."""

import os
import tempfile
import unittest

import sqlalchemy

import pya2l.model as model
from pya2l.api.create import (
    AxisPtsCreator,
    CharacteristicCreator,
    CompuMethodCreator,
    Creator,
    MeasurementCreator,
)
from pya2l.model import DB_EXTENSION


class TestCreator(unittest.TestCase):
    """Tests for the Creator base class."""

    def setUp(self):
        """Set up test fixture."""
        # Create a temporary database
        fd, self.db_filename = tempfile.mkstemp(suffix=f".{DB_EXTENSION}")
        os.close(fd)

        # Create engine and session
        self.engine = sqlalchemy.create_engine(f"sqlite:///{self.db_filename}")
        model.Base.metadata.create_all(self.engine)
        Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = Session()

        # Create a module
        self.module = model.Module(name="TEST_MODULE", longIdentifier="Test Module")
        self.session.add(self.module)
        self.session.commit()

        # Create a creator
        self.creator = Creator(self.session)

    def tearDown(self):
        """Tear down test fixture."""
        self.session.close()
        os.unlink(self.db_filename)

    def test_commit(self):
        """Test commit method."""
        # Add a new object to the session
        obj = model.Unit(name="TEST_UNIT", longIdentifier="Test Unit")
        self.session.add(obj)

        # Commit the session
        self.creator.commit()

        # Check that the object was committed
        self.session.close()
        Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        session = Session()
        unit = session.query(model.Unit).filter(model.Unit.name == "TEST_UNIT").first()
        self.assertIsNotNone(unit)
        self.assertEqual(unit.longIdentifier, "Test Unit")
        session.close()

    def test_rollback(self):
        """Test rollback method."""
        # Add a new object to the session
        obj = model.Unit(name="TEST_UNIT", longIdentifier="Test Unit")
        self.session.add(obj)

        # Rollback the session
        self.creator.rollback()

        # Check that the object was not committed
        self.session.close()
        Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        session = Session()
        unit = session.query(model.Unit).filter(model.Unit.name == "TEST_UNIT").first()
        self.assertIsNone(unit)
        session.close()


class TestCompuMethodCreator(unittest.TestCase):
    """Tests for the CompuMethodCreator class."""

    def setUp(self):
        """Set up test fixture."""
        # Create a temporary database
        fd, self.db_filename = tempfile.mkstemp(suffix=f".{DB_EXTENSION}")
        os.close(fd)

        # Create engine and session
        self.engine = sqlalchemy.create_engine(f"sqlite:///{self.db_filename}")
        model.Base.metadata.create_all(self.engine)
        Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = Session()

        # Create a module
        self.module = model.Module(name="TEST_MODULE", longIdentifier="Test Module")
        self.session.add(self.module)
        self.session.commit()

        # Create a creator
        self.creator = CompuMethodCreator(self.session)

    def tearDown(self):
        """Tear down test fixture."""
        self.session.close()
        os.unlink(self.db_filename)

    def test_create_compu_method(self):
        """Test create_compu_method method."""
        # Create a computation method
        compu_method = self.creator.create_compu_method(
            name="TEST_CM",
            long_identifier="Test Computation Method",
            conversion_type="LINEAR",
            format_str="%.2f",
            unit="m/s",
            module_name="TEST_MODULE",
        )
        self.creator.commit()

        # Check that the computation method was created
        self.assertIsNotNone(compu_method)
        self.assertEqual(compu_method.name, "TEST_CM")
        self.assertEqual(compu_method.longIdentifier, "Test Computation Method")
        self.assertEqual(compu_method.conversionType, "LINEAR")
        self.assertEqual(compu_method.format, "%.2f")
        self.assertEqual(compu_method.unit, "m/s")
        self.assertEqual(compu_method.module[0], self.module)

    def test_add_coeffs_linear(self):
        """Test add_coeffs_linear method."""
        # Create a computation method
        compu_method = self.creator.create_compu_method(
            name="TEST_CM", long_identifier="Test Computation Method", conversion_type="LINEAR", format_str="%.2f", unit="m/s"
        )

        # Add coefficients
        coeffs_linear = self.creator.add_coeffs_linear(compu_method=compu_method, a=2.0, b=1.0)
        self.creator.commit()

        # Check that the coefficients were added
        self.assertIsNotNone(coeffs_linear)
        self.assertEqual(coeffs_linear.a, 2.0)
        self.assertEqual(coeffs_linear.b, 1.0)
        self.assertEqual(coeffs_linear.compu_method, compu_method)


class TestMeasurementCreator(unittest.TestCase):
    """Tests for the MeasurementCreator class."""

    def setUp(self):
        """Set up test fixture."""
        # Create a temporary database
        fd, self.db_filename = tempfile.mkstemp(suffix=f".{DB_EXTENSION}")
        os.close(fd)

        # Create engine and session
        self.engine = sqlalchemy.create_engine(f"sqlite:///{self.db_filename}")
        model.Base.metadata.create_all(self.engine)
        Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = Session()

        # Create a module
        self.module = model.Module(name="TEST_MODULE", longIdentifier="Test Module")
        self.session.add(self.module)
        self.session.commit()

        # Create a creator
        self.creator = MeasurementCreator(self.session)

    def tearDown(self):
        """Tear down test fixture."""
        self.session.close()
        os.unlink(self.db_filename)

    def test_create_measurement(self):
        """Test create_measurement method."""
        # Create a measurement
        measurement = self.creator.create_measurement(
            name="TEST_MEAS",
            long_identifier="Test Measurement",
            datatype="UBYTE",
            conversion="TEST_CM",
            resolution=1,
            accuracy=0.1,
            lower_limit=0.0,
            upper_limit=255.0,
            module_name="TEST_MODULE",
        )
        self.creator.commit()

        # Check that the measurement was created
        self.assertIsNotNone(measurement)
        self.assertEqual(measurement.name, "TEST_MEAS")
        self.assertEqual(measurement.longIdentifier, "Test Measurement")
        self.assertEqual(measurement.datatype, "UBYTE")
        self.assertEqual(measurement.conversion, "TEST_CM")
        self.assertEqual(measurement.resolution, 1)
        self.assertEqual(measurement.accuracy, 0.1)
        self.assertEqual(measurement.lowerLimit, 0.0)
        self.assertEqual(measurement.upperLimit, 255.0)
        self.assertEqual(measurement.module[0], self.module)


class TestAxisPtsCreator(unittest.TestCase):
    """Tests for the AxisPtsCreator class."""

    def setUp(self):
        """Set up test fixture."""
        # Create a temporary database
        fd, self.db_filename = tempfile.mkstemp(suffix=f".{DB_EXTENSION}")
        os.close(fd)

        # Create engine and session
        self.engine = sqlalchemy.create_engine(f"sqlite:///{self.db_filename}")
        model.Base.metadata.create_all(self.engine)
        Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = Session()

        # Create a module
        self.module = model.Module(name="TEST_MODULE", longIdentifier="Test Module")
        self.session.add(self.module)
        self.session.commit()

        # Create a creator
        self.creator = AxisPtsCreator(self.session)

    def tearDown(self):
        """Tear down test fixture."""
        self.session.close()
        os.unlink(self.db_filename)

    def test_create_axis_pts(self):
        """Test create_axis_pts method."""
        # Create an axis points
        axis_pts = self.creator.create_axis_pts(
            name="TEST_AXIS",
            long_identifier="Test Axis Points",
            address=0x1000,
            input_quantity="INPUT_QUANTITY",
            deposit_attr="DEPOSIT_ATTR",
            max_diff=0.1,
            conversion="TEST_CM",
            max_axis_points=10,
            lower_limit=0.0,
            upper_limit=100.0,
            module_name="TEST_MODULE",
        )
        self.creator.commit()

        # Check that the axis points was created
        self.assertIsNotNone(axis_pts)
        self.assertEqual(axis_pts.name, "TEST_AXIS")
        self.assertEqual(axis_pts.longIdentifier, "Test Axis Points")
        self.assertEqual(axis_pts.address, 0x1000)
        self.assertEqual(axis_pts.inputQuantity, "INPUT_QUANTITY")
        self.assertEqual(axis_pts.depositAttr, "DEPOSIT_ATTR")
        self.assertEqual(axis_pts.maxDiff, 0.1)
        self.assertEqual(axis_pts.conversion, "TEST_CM")
        self.assertEqual(axis_pts.maxAxisPoints, 10)
        self.assertEqual(axis_pts.lowerLimit, 0.0)
        self.assertEqual(axis_pts.upperLimit, 100.0)
        self.assertEqual(axis_pts.module[0], self.module)


class TestCharacteristicCreator(unittest.TestCase):
    """Tests for the CharacteristicCreator class."""

    def setUp(self):
        """Set up test fixture."""
        # Create a temporary database
        fd, self.db_filename = tempfile.mkstemp(suffix=f".{DB_EXTENSION}")
        os.close(fd)

        # Create engine and session
        self.engine = sqlalchemy.create_engine(f"sqlite:///{self.db_filename}")
        model.Base.metadata.create_all(self.engine)
        Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = Session()

        # Create a module
        self.module = model.Module(name="TEST_MODULE", longIdentifier="Test Module")
        self.session.add(self.module)
        self.session.commit()

        # Create a creator
        self.creator = CharacteristicCreator(self.session)

    def tearDown(self):
        """Tear down test fixture."""
        self.session.close()
        os.unlink(self.db_filename)

    def test_create_characteristic(self):
        """Test create_characteristic method."""
        # Create a characteristic
        characteristic = self.creator.create_characteristic(
            name="TEST_CHAR",
            long_identifier="Test Characteristic",
            char_type="VALUE",
            address=0x2000,
            deposit="DEPOSIT",
            max_diff=0.1,
            conversion="TEST_CM",
            lower_limit=0.0,
            upper_limit=100.0,
            module_name="TEST_MODULE",
        )
        self.creator.commit()

        # Check that the characteristic was created
        self.assertIsNotNone(characteristic)
        self.assertEqual(characteristic.name, "TEST_CHAR")
        self.assertEqual(characteristic.longIdentifier, "Test Characteristic")
        self.assertEqual(characteristic.type, "VALUE")
        self.assertEqual(characteristic.address, 0x2000)
        self.assertEqual(characteristic.deposit, "DEPOSIT")
        self.assertEqual(characteristic.maxDiff, 0.1)
        self.assertEqual(characteristic.conversion, "TEST_CM")
        self.assertEqual(characteristic.lowerLimit, 0.0)
        self.assertEqual(characteristic.upperLimit, 100.0)
        self.assertEqual(characteristic.module[0], self.module)

    def test_add_axis_descr(self):
        """Test add_axis_descr method."""
        # Create a characteristic
        characteristic = self.creator.create_characteristic(
            name="TEST_CHAR",
            long_identifier="Test Characteristic",
            char_type="CURVE",
            address=0x2000,
            deposit="DEPOSIT",
            max_diff=0.1,
            conversion="TEST_CM",
            lower_limit=0.0,
            upper_limit=100.0,
        )

        # Add axis description
        axis_descr = self.creator.add_axis_descr(
            characteristic=characteristic,
            attribute="STD_AXIS",
            input_quantity="INPUT_QUANTITY",
            conversion="TEST_CM",
            max_axis_points=10,
            lower_limit=0.0,
            upper_limit=100.0,
        )
        self.creator.commit()

        # Check that the axis description was added
        self.assertIsNotNone(axis_descr)
        self.assertEqual(axis_descr.attribute, "STD_AXIS")
        self.assertEqual(axis_descr.inputQuantity, "INPUT_QUANTITY")
        self.assertEqual(axis_descr.conversion, "TEST_CM")
        self.assertEqual(axis_descr.maxAxisPoints, 10)
        self.assertEqual(axis_descr.lowerLimit, 0.0)
        self.assertEqual(axis_descr.upperLimit, 100.0)
        self.assertEqual(axis_descr.characteristic, characteristic)


if __name__ == "__main__":
    unittest.main()
