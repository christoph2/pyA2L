#!/usr/bin/env python
# -*- coding: latin-1 -*-

__copyright__ = """
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

"""Codes for scaling units (CSE)
"""

from collections import namedtuple
from enum import IntEnum

CSE_Type = namedtuple("CSE_Type", "code unit referred_to comment")


class Referer(IntEnum):
    """"""

    NONE = 0
    TIME = 1
    ANGLE = 2
    COMBUSTION = 3
    EVENT = 4


CSE = {
    0: CSE_Type(0, "1 µsec", Referer.TIME, ""),
    1: CSE_Type(1, "10 µsec", Referer.TIME, ""),
    2: CSE_Type(2, "100 µsec", Referer.TIME, ""),
    3: CSE_Type(3, "1 msec", Referer.TIME, ""),
    4: CSE_Type(4, "10 msec", Referer.TIME, ""),
    5: CSE_Type(5, "100 msec", Referer.TIME, ""),
    6: CSE_Type(6, "1 sec", Referer.TIME, ""),
    7: CSE_Type(7, "10 sec", Referer.TIME, ""),
    8: CSE_Type(8, "1 min", Referer.TIME, ""),
    9: CSE_Type(9, "1 hour", Referer.TIME, ""),
    10: CSE_Type(10, "1 day", Referer.TIME, ""),
    100: CSE_Type(100, "Angular degrees", Referer.ANGLE, ""),
    101: CSE_Type(101, "Revolutions 360 degrees", Referer.ANGLE, ""),
    102: CSE_Type(
        102, "Cycle 720 degrees", Referer.ANGLE, "e.g. in case of IC engines"
    ),
    103: CSE_Type(
        103, "Cylinder segment", Referer.COMBUSTION, "e.g. in case of IC engines"
    ),
    998: CSE_Type(
        998, "When frame available", Referer.EVENT, "Source defined in keyword Frame"
    ),
    999: CSE_Type(
        999,
        "Always if there is new value",
        Referer.NONE,
        """Calculation of a new
                     upper range limit after receiving a new partial value, e.g. when
                     calculating a complex trigger condition""",
    ),
    1000: CSE_Type(1000, "Non deterministic", Referer.NONE, "Without fixed scaling"),
}
