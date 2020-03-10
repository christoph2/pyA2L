#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2019 by Christoph Schueler <cpu12.gems.googlemail.com>

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

   s. FLOSS-EXCEPTION.txt
"""
__author__  = 'Christoph Schueler'
__version__ = "0.10.2"

import bisect

try:
    import numpy
    import scipy
except ImportError:
    fastMath = False
else:
    fastMath = True

if fastMath:
    from .math_fast import Interpolate1D
else:
    from .math_slow import Interpolate1D


class Lookup:
    """
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

