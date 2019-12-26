#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
"""
__copyright__="""
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2019 by Christoph Schueler <github.com/Christoph2,
                                        cpu12.gems@googlemail.com>

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

from scipy import interpolate

class Interpolate1D:
    """1-D linear interpolation.

    Parameters
    ----------
    xs: iterable of floats
        X values
    ys: iterable of floats
        Y values -- must be of equal length than xs.
    saturate: bool
        - ``True``
            - if X value is less then or equal to min(xs), the result is set to the Y value
              corresponding to the lowest X value
            - if X value is greater than or equal to the highest X value, the result is set to the Y value
              corresponding to the highest X value.
    """
    def __init__(self, xs, ys, saturate = True):
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
        return float(self.interp(x))
