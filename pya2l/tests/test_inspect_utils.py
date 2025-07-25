#!/usr/bin/env python
"""Tests for utility functions in pya2l.api.inspect module."""

from typing import Dict, List, Optional, Tuple, Union

import pytest

from pya2l.api.inspect import (
    Annotation,
    MatrixDim,
    _annotations,
    all_axes_names,
    asam_type_size,
    fnc_np_order,
    fnc_np_shape,
    get_module,
)


class TestAsamTypeSize:
    """Tests for asam_type_size function."""

    def test_valid_types(self):
        """Test asam_type_size with valid data types."""
        assert asam_type_size("BYTE") == 1
        assert asam_type_size("UBYTE") == 1
        assert asam_type_size("SBYTE") == 1
        assert asam_type_size("WORD") == 2
        assert asam_type_size("UWORD") == 2
        assert asam_type_size("SWORD") == 2
        assert asam_type_size("LONG") == 4
        assert asam_type_size("ULONG") == 4
        assert asam_type_size("SLONG") == 4
        assert asam_type_size("A_UINT64") == 8
        assert asam_type_size("A_INT64") == 8
        assert asam_type_size("FLOAT16_IEEE") == 2
        assert asam_type_size("FLOAT32_IEEE") == 4
        assert asam_type_size("FLOAT64_IEEE") == 8

    def test_invalid_type(self):
        """Test asam_type_size with invalid data type."""
        with pytest.raises(KeyError):
            asam_type_size("INVALID_TYPE")


class TestAllAxesNames:
    """Tests for all_axes_names function."""

    def test_return_value(self):
        """Test all_axes_names returns the correct list."""
        expected = ["x", "y", "z", "4", "5"]
        assert all_axes_names() == expected


class TestFncNpShape:
    """Tests for fnc_np_shape function."""

    def test_valid_matrix_dim(self):
        """Test fnc_np_shape with valid MatrixDim."""
        matrix_dim = MatrixDim(x=2, y=3, z=4)
        assert fnc_np_shape(matrix_dim) == (2, 3, 4)

    def test_invalid_matrix_dim(self):
        """Test fnc_np_shape with invalid MatrixDim."""
        matrix_dim = MatrixDim(x=None, y=None, z=None)
        assert fnc_np_shape(matrix_dim) == ()

    def test_partial_matrix_dim(self):
        """Test fnc_np_shape with partially valid MatrixDim."""
        matrix_dim = MatrixDim(x=2, y=3, z=None)
        # Should still return empty tuple because valid() will return False
        assert fnc_np_shape(matrix_dim) == ()

    def test_zero_dimensions(self):
        """Test fnc_np_shape with zero dimensions."""
        matrix_dim = MatrixDim(x=0, y=0, z=0)
        # Should filter out dimensions < 1
        assert fnc_np_shape(matrix_dim) == ()


class TestFncNpOrder:
    """Tests for fnc_np_order function."""

    def test_column_dir(self):
        """Test fnc_np_order with COLUMN_DIR."""
        assert fnc_np_order("COLUMN_DIR") == "F"

    def test_row_dir(self):
        """Test fnc_np_order with ROW_DIR."""
        assert fnc_np_order("ROW_DIR") == "C"

    def test_none(self):
        """Test fnc_np_order with None."""
        assert fnc_np_order(None) is None

    def test_invalid(self):
        """Test fnc_np_order with invalid value."""
        assert fnc_np_order("INVALID") is None
