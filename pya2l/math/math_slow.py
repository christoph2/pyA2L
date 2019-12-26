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

import bisect


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
        self.xs = xs
        self.ys = ys
        self.saturate = saturate
        intervals = zip(xs, xs[1 : ], ys, ys[1 : ])
        self.slopes = [(y1 - y0) / (x1 -x0) for x0, x1, y0, y1 in intervals]

    def __call__(self, x):
        """Interpolate a single value.

        Parameters
        ----------
        x: float
        """
        if self.saturate:
            if x <= self.min_x:
                return self.ys[0]
            elif x >= self.max_x:
                return self.ys[-1]
        else:
            if not (self.xs[0] <= x <= self.xs[-1]):
                raise ValueError("x out of bounds")
        i = bisect.bisect_right(self.xs, x) - 1
        return self.ys[i] + self.slopes[i] * (x -self.xs[i])

