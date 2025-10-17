#!/usr/bin/env python

__copyright__ = """
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2025 by Christoph Schueler <cpu12.gems@googlemail.com>

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

"""Functions adding semantics to model elements.
"""

import bisect
import re
import typing
from dataclasses import dataclass
from operator import itemgetter

import numexpr
import numpy as np
from scipy import interpolate
from scipy.interpolate import RegularGridInterpolator

from pya2l import exceptions


POW = re.compile(r"pow\s*\((?P<params>.*?)\s*\)", re.IGNORECASE)
SYSC = re.compile(r"sysc\s*\((?P<param>.*?)\s*\)", re.IGNORECASE)
HEX_INT = re.compile(r"0x[0-9a-fA-F]+")


@dataclass
class Coeffs:
    a: float
    b: float
    c: float
    d: float
    e: float
    f: float


@dataclass
class CoeffsLinear:
    a: float
    b: float


def fix_axis_par(offset: int, shift: int, num_apo: int) -> list:
    """"""  # noqa: DAR101, DAR201
    return np.array([offset + (i * (2**shift)) for i in range(num_apo)], dtype="float64")


def fix_axis_par_dist(offset: int, distance: int, num_apo: int) -> list:
    """"""  # noqa: DAR101, DAR201
    return np.array([offset + (i * distance) for i in range(num_apo)], dtype="float64")


class Interpolate1D:
    """1-D linear interpolation.

    Parameters
    ----------

    pairs: iterable of 2-tuples (x,y)
        x: float
            X values
        y: float
            Y values -- must be of equal length than xs.
    saturate: bool
        - ``True``
            - if X value is less then or equal to min(xs), the result is set to the Y value
              corresponding to the lowest X value
            - if X value is greater than or equal to the highest X value, the result is set to the Y value
              corresponding to the highest X value.
    default: float or None
        returned if x is out of boundaries.
    """

    def __init__(self, pairs, saturate=True):
        xs, ys = zip(*pairs)

        if any(x1 - x0 <= 0 for x0, x1 in zip(xs, xs[1:])):
            raise ValueError("'xs' must be in strictly increasing order.")
        self.min_x = min(xs)
        self.max_x = max(xs)

        if saturate:
            fill_value = (ys[0], ys[-1])
            bounds_error = False
        else:
            fill_value = None
            bounds_error = True

        self.interp = interpolate.interp1d(x=xs, y=ys, kind="linear", bounds_error=bounds_error, fill_value=fill_value)

    def __call__(self, x):
        """Interpolate a single value.

        Parameters
        ----------
        x: float
        """
        return self.interp(x)


'''
class Lookup:
    """Table lookup

    Parameters
    ----------

    """

    def __init__(self, xs, ys, saturate = False, y_low = None, y_high = None):
        if any(x1 -x0 <= 0 for x0, x1 in zip(xs, xs[1 : ])):
            raise ValueError("'xs' must be in strictly increasing order.")
        self.xs = xs
        self.ys = ys
        self.saturate = saturate
        self.y_low = y_low
        self.y_high = y_high

    def __call__(self, x):
        """
        """
        if self.saturate:
            if x <= self.min_x:
                return self.y_low or self.ys[0]
            elif x >= self.max_x:
                return self.y_high or self.ys[-1]
        else:
            if not (self.xs[0] <= x <= self.xs[-1]):
                raise ValueError("x out of bounds")
        pos = bisect.bisect_right(self.xs, x) - 1
        return self.ys[pos]
'''


def axis_rescale(no_rescale_x: int, no_axis_pts: int, axis, virtual):
    """
    Parameters
    ----------
    no_rescale_x: int

    no_axis_pts: int
        Number of axis-points to calculate; shall be a power of two plus one, e.g. 5, 17, 33...

    axis: list-like

    virtual: list-like


    Returns
    -------
    `numpy.array`
    """
    k = 1
    d = (virtual[-1] - virtual[0] + 1) // (no_axis_pts - 1)
    xs = [axis[0]]
    for idx in range(no_rescale_x - 1):
        while True:
            kdv = (k * d) + virtual[0]
            if kdv >= virtual[idx + 1]:
                break
            k += 1
            x = axis[idx] + (((k - 1) * d) - virtual[idx]) * (axis[idx + 1] - axis[idx]) / (virtual[idx + 1] - virtual[idx])
            xs.append(x)
    xs.append(axis[no_rescale_x - 1])
    return np.array(xs)


class NormalizationAxes:
    """
    Appendix C: Using Reference Curves as Normalization Axes for Maps

    Parameters
    ----------
    x_norm:

    y_norm:

    z_map
    """

    def __init__(self, x_norm, y_norm, z_map):
        self.xn = np.array(x_norm)
        self.yn = np.array(y_norm)
        self.zm = np.array(z_map)
        self.ip_x = Interpolate1D(pairs=zip(self.xn[:, 0], self.xn[:, 1]))
        self.ip_y = Interpolate1D(pairs=zip(self.yn[:, 0], self.yn[:, 1]))
        x_size, y_size = self.zm.shape
        self.ip_m = RegularGridInterpolator((np.arange(x_size), np.arange(y_size)), self.zm, method="linear")

    def __call__(self, x, y):
        """
        Parameters
        ----------
        x: float

        y: float

        Returns
        -------
        float
        """
        x_new = self.ip_x(x)
        y_new = self.ip_y(y)
        return self.ip_m((y_new, x_new))


class RatFunc:
    """Evaluate rational function.

    Parameters
    ----------
    coeffs: Coeffs
        a, b, c, d, e, f - coefficients for the specified formula:
        f(x) = (axx + bx + c) / (dxx + ex + f)

        INT = f(PHYS)

        When using :method:`int_to_physical`: Restrictions have to be defined
        because this general equation cannot always be inverted.

    Note
    ----
        `Linear` is PHYS = f(INT)!!!
    """

    def __init__(self, coeffs: Coeffs):
        a, b, c, d, e, f = (coeffs.a, coeffs.b, coeffs.c, coeffs.d, coeffs.e, coeffs.f)
        self.p = np.poly1d([a, b, c])
        self.q = np.poly1d([d, e, f])
        if self.p.order == 1 and self.q.order == 0:
            self.p_inv = np.poly1d([(f / b), -((f * c) / (b * f))])
        else:
            self.p_inv = None
        self.coeffs = coeffs

    def physical_to_int(self, p):
        """Evaluate function PHYS ==> INT

        Parameters
        ----------
        p: int or float, scalar or numpy.ndarray
        """
        return self.p(p) / self.q(p)

    def int_to_physical(self, value):
        """Evaluate function INT ==> PHYS

        Parameters
        ----------
        i: int or float, scalar or numpy.ndarray

        Note
        ----
        Currently inversion of quadratic functions isn't supported, only linear ones.
        """
        if self.p.order == 1 and self.q.order == 0:
            return self.p_inv(value)
        elif self.p.order == 0 and self.q.order == 1:
            return self.physical_to_int(value)  # Inverse functions are already inverted...
        elif self.p.order == 0 and self.q.order == 0:
            raise exceptions.MathError("Cannot invert constant function.")
        else:
            raise NotImplementedError("Cannot invert quadratic function.")

    def __str__(self) -> str:
        return f"RatFunc(coeffs=(a={self.coeffs.a}, b={self.coeffs.b}, c={self.coeffs.c}, d={self.coeffs.d}, e={self.coeffs.e}, f={self.coeffs.f}))"

    __repr__ = __str__


class Identical:
    """Identity function."""

    def __init__(self):
        pass

    def int_to_physical(self, i):
        if isinstance(i, np.ndarray):
            return i.copy()
        return i

    def physical_to_int(self, p):
        return p

    def __str__(self) -> str:
        return "Identical()"

    __repr__ = __str__


class Linear:
    """Evaluate linear function.

    Parameters
    ----------
    coeffs: CoeffsLinear
        a, b - coefficients for the specified formula:
        coefficients for the specified formula:
        f(x) = ax + b

        PHYS = f(INT)

    Note
    ----
        `RatFunc` is INT = f(PHYS)!!!
    """

    def __init__(self, coeffs: CoeffsLinear):
        a, b = coeffs.a, coeffs.b
        self.p = np.poly1d([a, b])
        self.a = a
        self.b = b

    def int_to_physical(self, i):
        """"""  # noqa: DAR101, DAR201
        return self.p(i)

    def _eval_pti(self, p):
        return (self.p - p).roots[0]

    def physical_to_int(self, p):
        """"""  # noqa: DAR101, DAR201
        if hasattr(p, "__iter__"):
            return np.array([self._eval_pti(i) for i in p])
        else:
            return self._eval_pti(p)

    def __str__(self) -> str:
        return f"Linear(coeffs=(a={self.a}, b={self.b}))"

    __repr__ = __str__


class LookupTable:
    """Basic lookup table.
    An integer value is mapped to an integer or display string.

    Parameters
    ----------
        mapping: iterable of 2-tuples (key, value)
            - keys can be either floats or ints (internaly converted to int)
            - values are either integers or strings.

        default: int or str
            returned if value is not in mapping.
    """

    def __init__(self, mapping, default=None):
        mapping = ((int(item[0]), item[1]) for item in mapping)
        self.mapping = dict(mapping)
        self.mapping_inv = {v: k for k, v in self.mapping.items()}
        self.default = default
        self.map_internal_to_phys_vec = np.vectorize(self.map_internal_to_phys)

    def map_internal_to_phys(self, value):
        return self.mapping.get(value, self.default)

    def int_to_physical(self, value):
        """"""  # noqa: DAR101, DAR201
        if hasattr(value, "__iter__"):
            return self.map_internal_to_phys_vec(value)
        else:
            return self.map_internal_to_phys(value)

    def physical_to_int(self, p):
        """"""  # noqa: DAR101, DAR201
        if hasattr(p, "__iter__") and not isinstance(p, str):
            return [self.mapping_inv.get(r) for r in p]
        else:
            return self.mapping_inv.get(p)


class InterpolatedTable:
    """Table with linear interpolation."""

    def __init__(self, pairs, default=None):
        self.interp = Interpolate1D(pairs, saturate=False)
        self.default = default

    def int_to_physical(self, i):
        """"""  # noqa: DAR101, DAR201
        try:
            return self.interp(i)
        except ValueError:
            return self.default

    def physical_to_int(self, p):
        """"""  # noqa: DAR101, DAR201, DAR401
        raise NotImplementedError()

    def __str__(self) -> str:
        return f"InterpolatedTable(x={self.interp.interp.x}, y={self.interp.interp.y}, max_x={self.interp.max_x}, max_y={self.interp.max_y})"

    __repr__ = __str__


class LookupTableWithRanges:
    """Lookup table where keys define numerical ranges.

    A value range is mapped to a display string.

    Parameters
    ----------
        mapping: iterable of 3-tuples (key_min, key_max, value)
            - keys can be either floats or ints (s. `dtype`).
            - values are strings.

        default: str
            returned if value is out of any declared range.

        dtype: int | float
            Datatype of keys.
    """

    def __init__(self, mapping, default=None, dtype=int):
        if not (dtype is int or dtype is float):
            raise ValueError("dtype must be either int or float")
        mapping = ((dtype(item[0]), dtype(item[1]), item[2]) for item in mapping)
        self.mapping = sorted(mapping, key=itemgetter(0))
        self.min_values = [item[0] for item in self.mapping]
        self.max_values = [item[1] for item in self.mapping]
        self.minimum = min(self.min_values)
        self.maximum = max(self.max_values)
        self.display_values = [item[2] for item in self.mapping]
        self.dict_inv = dict(zip(self.display_values, self.min_values))  # min_value, according to spec.
        self.default = default
        # For integer ranges we include both endpoints. For floating-point ranges we use
        # left-closed/right-open intervals, except that the very last range includes the
        # global maximum on the right to avoid dropping the upper boundary to default.
        if isinstance(dtype, int):
            self.in_range = lambda x, left, right: left <= x <= right
        else:
            max_right = self.maximum
            self.in_range = lambda x, left, right, m=max_right: (left <= x < right) or (x == m and right == m)

    def _lookup(self, x):
        """"""  # noqa: DAR101, DAR201
        if not (self.minimum <= x <= self.maximum):
            return self.default
        pos = bisect.bisect_right(self.min_values, x) - 1
        display_value = self.display_values[pos]
        min_value = self.min_values[pos]
        max_value = self.max_values[pos]
        if self.in_range(x, min_value, max_value):
            return display_value
        else:
            return self.default

    def int_to_physical(self, i):
        """"""  # noqa: DAR101, DAR201
        if hasattr(i, "__iter__"):
            return np.array([self._lookup(r) for r in i])
        else:
            return self._lookup(i)

    def physical_to_int(self, p):
        """"""  # noqa: DAR101, DAR201
        if hasattr(p, "__iter__") and not isinstance(p, str):
            return [self.dict_inv.get(r, None) for r in p]
        else:
            return self.dict_inv.get(p, None)


class FormulaBase:
    """Base class for formula interpreters.

    Parameters
    ----------

    formula: str
        function to calculate the physical value from the control unit internal value.

    inverse_formula: str
        function for calculation of the control unit internal value from the physical value.

    system_constants: list of 2-tuples (name, value)

    legacy: bool
        whether to use legacy formula syntax (before ASAM MCD-2 MC 1.6) (default: False)
    """

    def __init__(
        self,
        formula: str,
        inverse_formula: typing.Optional[str] = None,
        system_constants: typing.Optional[typing.Dict] = None,
        legacy: bool = False,
    ):
        if not formula:
            raise ValueError("Formula cannot be None or empty.")
        if system_constants:
            self.system_constants = system_constants
        else:
            self.system_constants = {}
        self.legacy = legacy
        self.formula = self._replace_special_symbols(formula) if formula is not None else None
        self.inverse_formula = self._replace_special_symbols(inverse_formula) if inverse_formula else None

    def sysc(self, key):
        return self.system_constants[key]

    def _build_namespace(self, *args):
        if len(args) == 0:
            raise ValueError("Formula called with no paramters.")
        xs = {f"X{i}": v for i, v in enumerate(args, 1)}
        if len(args) == 1:  # In this case...
            xs["X"] = xs.get("X1")  # ... create an alias.
        namespace = self.MATH_FUNCS
        namespace.update(xs)
        namespace.update(self.system_constants)
        namespace["sysc"] = self.sysc
        return namespace

    @staticmethod
    def names_tolower(text):
        MATH_FUNCTIONS = re.compile("abs|acos|asin|atan|cos|cosh|exp|log|log10|pow|sin|sinh|sqrt|tan|tanh", re.IGNORECASE)
        return MATH_FUNCTIONS.sub(lambda m: m.group(0).lower(), text)


class Formula(FormulaBase):
    """ASAP2 formula interpreter based on *numexpr*.

    Parameters
    ----------

    formula: str
        function to calculate the physical value from the control unit internal value.

    inverse_formula: str
        function for calculation of the control unit internal value from the physical value.

    system_constants: list of 2-tuples (name, value)
    """

    MATH_FUNCS = {}

    def _replace_special_symbols(self, text):
        if text is None:
            return None
        # normalize case for known math function names first
        result = FormulaBase.names_tolower(text)

        if self.legacy:
            # legacy: &, |, ~ are logical; ^ is power; XOR is exclusive OR keyword; &&, ||, ! are not supported
            if ("&&" in result) or ("||" in result) or ("!" in result):
                raise ValueError("Legacy formula does not support '&&', '||', or '!' operators.")
            # function names: accept legacy spellings; ensure numpy names
            # arcos (legacy) -> arccos (numpy); arcsin/arctan are already numpy-compatible
            result = re.sub(r"\barcos\b", "arccos", result, flags=re.IGNORECASE)
            # current short names also accepted in legacy, normalize to numpy long names
            result = re.sub(r"\bacos\b", "arccos", result)
            result = re.sub(r"\basin\b", "arcsin", result)
            result = re.sub(r"\batan\b", "arctan", result)
            # power: '^' => '**' (must be before XOR keyword replacement to avoid converting that caret)
            result = result.replace("^", "**")
            # XOR keyword => boolean inequality (logical XOR semantics without using '^')
            result = re.sub(r"\bxor\b", " != ", result, flags=re.IGNORECASE)
            # Do not replace &, |, ~ — numexpr uses these for logical ops over boolean arrays/scalars
        else:
            # current: &&, ||, ! are logical; &, |, ~ are bitwise; ^ is bitwise XOR; XOR keyword is not supported
            if re.search(r"\bxor\b", result, flags=re.IGNORECASE):
                raise ValueError("Current formula does not support 'XOR' keyword.")
            # map current short names to numpy long names
            result = result.replace("acos", "arccos").replace("asin", "arcsin").replace("atan", "arctan")
            # logical tokens for numexpr must use bitwise forms
            result = result.replace("&&", "&").replace("||", "|").replace("!", "~")

        # normalize hex integer literals to decimal for numexpr
        result = HEX_INT.sub(lambda m: str(int(m.group(0), 16)), result)

        # replace 'pow(a, b)' with '(a ** b)'
        while True:
            match = POW.search(result)
            if match:
                params = [p.strip() for p in match.group("params").split(",")]
                pow_expr = "({} ** {})".format(*params)
                head = result[: match.start()]
                tail = result[match.end() :]
                result = f"{head}{pow_expr}{tail}"
            else:
                break
        # replace 'sysc(a)' with concrete value
        while True:
            match = SYSC.search(result)
            if match:
                param = match.group("param").strip()
                value = self.sysc(param)
                head = result[: match.start()]
                tail = result[match.end() :]
                result = f"{head}{value}{tail}"
            else:
                break
        return result.strip()

    def int_to_physical(self, *args):
        """"""  # noqa: DAR101, DAR201
        try:
            res = numexpr.evaluate(self.formula, local_dict=self._build_namespace(*args))
            if isinstance(res, np.ndarray):
                return res.item() if res.shape == () else res
            try:
                return res.item()
            except Exception:
                return res
        except Exception as e:
            print(f"Error evaluating formula: {e!r})")
            return np.array([])

    def physical_to_int(self, *args):
        """"""  # noqa: DAR101, DAR201, DAR401
        if self.inverse_formula is None:
            raise NotImplementedError("Formula: physical_to_int() requires inverse_formula.")
        try:
            res = numexpr.evaluate(self.inverse_formula, local_dict=self._build_namespace(*args))
            if isinstance(res, np.ndarray):
                return res.item() if res.shape == () else res
            try:
                return res.item()
            except Exception:
                return res
        except Exception as e:
            print(f"Error evaluating inverse formula: {e!r})")
            return np.array([])
