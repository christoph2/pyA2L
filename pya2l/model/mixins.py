#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__="""
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2020 by Christoph Schueler <github.com/Christoph2,
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

from collections import namedtuple
import bisect

from pya2l.logger import Logger

from sqlalchemy import (event, func)
from sqlalchemy import sql

class MixInBase:

    logger = Logger(__name__)

class AxisDescrMixIn(MixInBase):
    """
    """
    def check(self):
        if self.attribute == "CURVE_AXIS":
            if self.conversion != "NO_COMPU_METHOD":
                self.logger.error("CURVE_AXIS have no input conversion, use 'NO_COMPU_METHOD' for argument 'conversion'.")
                return False
#            meas =
        return True


class CompareByPositionMixIn(MixInBase):
    """
    Enable sortability in user code.

    Implements basic comparison.
    """

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.position < other.position


MIXIN_MAP = {
    "AXIS_DESCR": "AxisDescrMixIn",
}

