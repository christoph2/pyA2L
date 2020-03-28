#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__="""
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2020 by Christoph Schueler <cpu12.gems@googlemail.com>

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
from collections import OrderedDict
from operator import itemgetter

try:
    import numpy as np
except ImportError:
    pass

try:
    from scipy.interpolate import RegularGridInterpolator
    from scipy import interpolate
except ImportError:
    pass

from pya2l import exceptions
from pya2l import model


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
    def __init__(self, pairs, saturate = True):
        xs, ys = zip(*pairs)

        if any(x1 -x0 <= 0 for x0, x1 in zip(xs, xs[1 : ])):
            raise ValueError("'xs' must be in strictly increasing order.")
        self.min_x = min(xs)
        self.max_x = max(xs)

        if saturate:
            fill_value = (ys[0], ys[-1])
            bounds_error = False
        else:
            fill_value = None
            bounds_error = True

        self.interp = interpolate.interp1d(x = xs, y = ys, kind = "linear", bounds_error = bounds_error, fill_value = fill_value)

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


def axis_rescale(no_rescale_x : int, no_axis_pts : int, axis, virtual):
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
    list
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
    return xs


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
        self.ip_x = Interpolate1D(pairs = zip(self.xn[:, 0], self.xn[:, 1]))
        self.ip_y = Interpolate1D(pairs = zip(self.yn[:, 0], self.yn[:, 1]))
        x_size, y_size = self.zm.shape
        self.ip_m = RegularGridInterpolator((np.arange(x_size), np.arange(y_size)), self.zm, method = "linear")

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
    coeffs: object containing coefficients.
        a, b, c, d, e, f - coefficients for the specified formula:
        f(x) = (axx + bx + c) / (dxx + ex + f)

        When using :method:`inv`: Restrictions have to be defined
        because this general equation cannot always be inverted.
    """

    def __init__(self, coeffs):
        a, b, c, d, e, f = coeffs.a, coeffs.b, coeffs.c, coeffs.d, coeffs.e, coeffs.f
        self.p = np.poly1d([a, b, c])
        self.q = np.poly1d([d, e, f])
        if self.p.order == 1 and self.q.order == 0:
            self.p_inv = np.poly1d([(f / b), -((f * c) / (b * f))])
        else:
            self.p_inv = None

    def __call__(self, x):
        """Evaluate function.

        Parameters
        ----------
        x: int or float, scalar or numpy.ndarray
        """
        return self.p(x) / self.q(x)

    def inv(self, y):
        """Calculate inverse of function
        i.e. inv(y = f(x)) ==> x = f_inv(y)

        Parameters
        ----------
        y: int or float, scalar or numpy.ndarray

        Note
        ----
        Currently inversion of quadratic functions isn't supported, only linear ones.
        """
        if self.p.order == 1 and self.q.order == 0:
            return self.p_inv(y)
        elif self.p.order == 0 and self.q.order == 0:
            raise exceptions.MathError("Cannot invert constant function.")
        else:
            raise NotImplementedError("Inversion of this kind of polynoms isn't supported yet.")


class Identical:
    """Identity function.
    """

    def __init__(self):
        pass

    def __call__(self, x):
        """Evaluate function.

        Parameters
        ----------
        y: int or float
        """
        return x

    def inv(self, y):
        """
        """
        return y


class Linear:
    """Evaluate linear function.

    Parameters
    ----------
    coeffs: object containing coefficients.
        a, b - coefficients for the specified formula:
        coefficients for the specified formula:
        f(x) = ax + b
    """

    def __init__(self, coeffs):
        a, b = coeffs.a, coeffs.b
        self.p = np.poly1d([a, b])

    def __call__(self, x):
        """
        """
        return self.p(x)

    def _eval_inv(self, y):
        return (self.p - y).roots[0]

    def inv(self, y):
        """
        """
        if isinstance(y, np.ndarray):
            return [self._eval_inv(i) for i in y]
        else:
            return self._eval_inv(y)


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

    def __init__(self, mapping, default = None):
        mapping = ((int(item[0]), item[1]) for item in mapping)
        self.mapping = dict(mapping)
        self.mapping_inv = {v: k for k, v in self.mapping.items()}
        self.default = default

    def __call__(self, x):
        """
        """
        return self.mapping.get(x, self.default)

    def inv(self, y):
        """
        """
        return self.mapping_inv.get(y)


class InterpolatedTable:
    """Table with linear interpolation.
    """

    def __init__(self, pairs, default = None):
        self.interp = Interpolate1D(pairs, saturate = False)
        self.default = default

    def __call__(self, x):
        """
        """
        try:
            return self.interp(x)
        except ValueError:
            return self.default

    def inv(self, y):
        """
        """
        raise NotImplementedError()


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

    def __init__(self, mapping, default = None, dtype = int):
        if not (dtype is int or dtype is float):
            raise ValueError("dtype must be either int or float")
        mapping = ((dtype(item[0]), dtype(item[1]), item[2]) for item in mapping)
        self.mapping = sorted(mapping, key = itemgetter(0))
        self.min_values = [item[0] for item in self.mapping]
        self.max_values = [item[1] for item in self.mapping]
        self.minimum = min(self.min_values)
        self.maximum = max(self.max_values)
        self.display_values = [item[2] for item in self.mapping]
        self.dict_inv = dict(zip(self.display_values, self.min_values)) # min_value, according to spec.
        self.default = default
        if dtype == int:
            self.in_range = lambda x, l, r: l <= x <= r
        else:
            self.in_range = lambda x, l, r: l <= x < r

    def __call__(self, x):
        """
        """
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

    def inv(self, y):
        """
        """
        return self.dict_inv.get(y, None)


class CompuMethod:
    """
    Parameters
    ----------

    session: Sqlite3 session object
        Needed for further investigations.

    compu_method: CompuMethod
    """

    EVALUATORS = {
        'IDENTICAL' : Identical,
        'FORM'      : None,
        'LINEAR'    : Linear,
        'RAT_FUNC'  : RatFunc,
        'TAB_INTP'  : None,
        'TAB_NOINTP': None,
        'TAB_VERB'  : LookupTable,
    }

    def __init__(self, session, compu_method: model.CompuMethod):
        conversionType = compu_method.conversionType
        if conversionType == "IDENTICAL":
            self.evaluator = Identical()
        elif conversionType == "FORM":
            pass
        elif conversionType == "LINEAR":
            coeffs = compu_method.coeffs_linear
            if coeffs is None:
                raise exceptions.StructuralError("'LINEAR' requires coefficients (COEFFS_LINEAR).")
            self.evaluator = Linear(coeffs)
        elif conversionType == "RAT_FUNC":
            coeffs = compu_method.coeffs
            if coeffs is None:
                raise exceptions.StructuralError("'RAT_FUNC' requires coefficients (COEFFS).")
            self.evaluator = RatFunc(coeffs)
        elif conversionType == "TAB_INTP":
            table_name = compu_method.compu_tab_ref.conversionTable
            table = session.query(model.CompuTab).filter(model.CompuTab.name == table_name).first()
            if table is None:
                raise exceptions.StructuralError("'TAB_NOINTP' requires a conversation table.")
            pairs = [(p.inVal, p.outVal) for p in table.pairs]
            default_numeric = table.default_value_numeric.display_value if table.default_value_numeric else None
            default = table.default_value.display_string if table.default_value else None
            if default_numeric and default:
                raise exceptions.StructuralError("Cannot use both DEFAULT_VALUE and DEFAULT_VALUE_NUMERIC.")
            default = default_numeric if not default_numeric is None else default
            self.evaluator = InterpolatedTable(pairs, default)
        elif conversionType == "TAB_NOINTP":
            table_name = compu_method.compu_tab_ref.conversionTable
            table = session.query(model.CompuTab).filter(model.CompuTab.name == table_name).first()
            if table is None:
                raise exceptions.StructuralError("'TAB_NOINTP' requires a conversation table.")
            pairs = [(p.inVal, p.outVal) for p in table.pairs]
            default_numeric = table.default_value_numeric.display_value if table.default_value_numeric else None
            default = table.default_value.display_string if table.default_value else None
            if default_numeric and default:
                raise exceptions.StructuralError("Cannot use both DEFAULT_VALUE and DEFAULT_VALUE_NUMERIC.")
            default = default_numeric if not default_numeric is None else default
            self.evaluator = LookupTable(pairs, default)

        elif conversionType == "TAB_VERB":
            table_name = compu_method.compu_tab_ref.conversionTable
            table = session.query(model.CompuVtab).filter(model.CompuVtab.name == table_name).first()
            if table is None:
                table = session.query(model.CompuVtabRange).filter(model.CompuVtabRange.name == table_name).first()
                if table is None:
                    raise exceptions.StructuralError("'TAB_VERB' requires a conversation table.")
                triples = [(p.inValMin, p.inValMax, p.outVal) for p in table.triples]
                default = table.default_value.display_string if table.default_value else None
                # TODO: datatype !?
                self.evaluator = LookupTableWithRanges(triples, default)
            else:
                pairs = [(p.inVal, p.outVal) for p in table.pairs]
                default = table.default_value.display_string if table.default_value else None
                self.evaluator = LookupTable(pairs, default)
        else:
            raise ValueError("Unknown conversation type '{}'.".format(conversionType))

    def __call__(self, x):
        """Evaluate computation method.

        Parameters
        ----------
            x: int or float, scalar or array
        """
        return self.evaluator(x)

    def inv(self, y):
        """Inverse computation method.

        Parameters
        ----------
            y: int or float, scalar or array
        """
        return self.evaluator.inv(y)
