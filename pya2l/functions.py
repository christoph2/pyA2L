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

try:
    import numpy as np
except ImportError:
    pass

try:
    from scipy.interpolate import RegularGridInterpolator
except ImportError:
    pass

from pya2l import math

def compute(compu_method_name):
    pass

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
        self.ip_x = math.Interpolate1D(xs = self.xn[:, 0], ys = self.xn[:, 1])
        self.ip_y = math.Interpolate1D(xs = self.yn[:, 0], ys = self.yn[:, 1])
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



class CompuMethod:
    """
    Parameters
    ----------
    """

    def __init__(self, cm):
        pass

    def __call__(self):
        pass


class RatFunc:
    """Evaluate rational function.

    Parameters
    ----------
    coeffs: list-like of floats
        a, b, c, d, e, f - coefficients for the specified formula:
        f(x) = (axx + bx + c) / (dxx + ex + f)
    """

    def __init__(self, coeffs):
        if not (len(coeffs) == 6 and all([isinstance(c, (int, float)) for c in coeffs])):
            raise TypeError("coeffs must be exactly 6 ints/floats")

        self.p = np.poly1d(coeffs[ : 3])
        self.q = np.poly1d(coeffs[3 : ])

    def __call__(self, x):
        return self.p(x) / self.q(x)
