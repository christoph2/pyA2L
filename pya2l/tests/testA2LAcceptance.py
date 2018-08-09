#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2017 by Christoph Schueler <cpu12.gems.googlemail.com>

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
__version__ = '0.1.0'

import unittest
from pya2l.a2lparser import A2LParser


TEST_A2L = """
/************************************************************************************/
/*                                                                                  */
/*   ASAP2 v1.6.1 language example                                                  */
/*                                                                                  */
/*   2013-02-13                                                                     */
/*   File: example-a2l-file.a2l                                                     */
/*   Version: 1.0                                                                   */
/*                                                                                  */
/*   ASAM e.V.                                                                      */
/*   Altlaufstr. 40                                                                 */
/*   85635 Hoehenkirchen                                                            */
/*                                                                                  */
/************************************************************************************/

ASAP2_VERSION 1 61

/begin PROJECT
   ASAM
   "_default_Project"
   /begin HEADER
      "default_Header"
      PROJECT_NO ASAM2013
   /end HEADER
   /begin MODULE
      Module_01
      "default_Module"

      /begin MOD_PAR "default_ModPar"
         ADDR_EPK 0x100100FF
         EPK "EPROM_ID_01"
         /begin MEMORY_SEGMENT MemorySegment_01
            "MemorySegment_01"
            DATA
            FLASH
            EXTERN
            0x1000FFFF
            0xf0000
            0xFFFFFFFF 0xFFFFFFFF 0xFFFFFFFF 0xFFFFFFFF 0xFFFFFFFF
         /end MEMORY_SEGMENT
      /end MOD_PAR

      /begin MOD_COMMON "default_ModCommon"
         DEPOSIT ABSOLUTE
         BYTE_ORDER MSB_FIRST
         ALIGNMENT_BYTE 1
         ALIGNMENT_WORD 2
         ALIGNMENT_LONG 4
         ALIGNMENT_FLOAT32_IEEE 4
         ALIGNMENT_FLOAT64_IEEE 8
      /end MOD_COMMON

      /begin MEASUREMENT Measurement_01
         "Preasure_chamber_01"
         UBYTE
         CompuMethod_02
         1
         0.
         0.
         255.
         DISPLAY_IDENTIFIER Measurement_01
         ECU_ADDRESS 0xE0010000
         BIT_MASK 0x1F
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_02
         "Preasure_chamber_02"
         UBYTE
         CompuMethod_02
         1
         0.
         0.
         255.
         DISPLAY_IDENTIFIER Measurement_02
         ECU_ADDRESS 0xE0020000
         BIT_MASK 0x1F
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_03
         "Preasure_chamber_03"
         UWORD
         CompuMethod_03
         1
         0.
         0.
         65535.
         DISPLAY_IDENTIFIER Measurement_03
         ECU_ADDRESS 0xE0030000
         FORMAT "%6.0"
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_04
         "Preasure_chamber_04"
         UWORD
         CompuMethod_05
         1
         0.
         0.
         359.999
         DISPLAY_IDENTIFIER Measurement_04
         ECU_ADDRESS 0xE0040000
         FORMAT "%6.3"
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_05
         "Preasure_chamber_05"
         UWORD
         CompuMethod_01
         1
         0.
         0.
         65535.
         DISPLAY_IDENTIFIER Measurement_05
         ECU_ADDRESS 0xE0050000
         FORMAT "%6.0"
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_06
         "Preasure_chamber_06"
         UWORD
         CompuMethod_01
         1
         0.
         0.
         65535.
         DISPLAY_IDENTIFIER Measurement_06
         ECU_ADDRESS 0xE0060000
         FORMAT "%6.0"
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_07
         "Preasure_chamber_07"
         UBYTE
         CompuMethod_02
         1
         0.
         0.
         255.
         DISPLAY_IDENTIFIER Measurement_07
         ECU_ADDRESS 0xE0070000
         BIT_MASK 0x1F
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_08
         "Preasure_chamber_08"
         UWORD
         CompuMethod_05
         1
         0.
         0.
         359.999
         DISPLAY_IDENTIFIER Measurement_08
         ECU_ADDRESS 0xE0080000
         FORMAT "%6.3"
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_09
         "Preasure_chamber_09"
         UWORD
         CompuMethod_03
         1
         0.
         0.
         65535.
         DISPLAY_IDENTIFIER Measurement_09
         ECU_ADDRESS 0xE0090000
         FORMAT "%6.0"
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_10
         "Preasure_chamber_10"
         UWORD
         CompuMethod_03
         1
         0.
         0.
         65535.
         DISPLAY_IDENTIFIER Measurement_10
         ECU_ADDRESS 0xE00A0000
         FORMAT "%6.0"
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_11
         "Preasure_chamber_11"
         UWORD
         CompuMethod_03
         1
         0.
         0.
         65535.
         DISPLAY_IDENTIFIER Measurement_11
         ECU_ADDRESS 0xE00B0000
         FORMAT "%6.0"
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_12
         "Preasure_chamber_12"
         UWORD
         CompuMethod_05
         1
         0.
         0.
         359.999
         DISPLAY_IDENTIFIER Measurement_12
         ECU_ADDRESS 0xE00C0000
         FORMAT "%6.3"
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_13
         "Preasure_chamber_13"
         UBYTE
         CompuMethod_02
         1
         0.
         0.
         255.
         DISPLAY_IDENTIFIER Measurement_13
         ECU_ADDRESS 0xE00D0000
         BIT_MASK 0x1F
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_14
         "Preasure_chamber_14"
         UBYTE
         CompuMethod_02
         1
         0.
         0.
         255.
         DISPLAY_IDENTIFIER Measurement_14
         ECU_ADDRESS 0xE00E0000
         BIT_MASK 0x1F
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_15
         "Preasure_chamber_15"
         UBYTE
         CompuMethod_02
         1
         0.
         0.
         255.
         DISPLAY_IDENTIFIER Measurement_15
         ECU_ADDRESS 0xE00F0000
         BIT_MASK 0x1F
      /end MEASUREMENT

      /begin MEASUREMENT Measurement_16
         "Preasure_chamber_16"
         UWORD
         CompuMethod_06
         1
         0.
         0.
         359.999
         DISPLAY_IDENTIFIER Measurement_16
         ECU_ADDRESS 0xE0100000
         FORMAT "%6.3"
      /end MEASUREMENT

      /begin CHARACTERISTIC Characteristic_01
         "regulator_01"
         VALUE
         0x1100FF00
         RecordLayout_01
         1.
         CompuMethod_02
         0.
         1.
         DISPLAY_IDENTIFIER Characteristic_01
         BIT_MASK 0x1F
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_02
         "regulator_02"
         VALUE
         0x1200FF00
         RecordLayout_02
         359.999
         CompuMethod_05
         0.
         359.999
         DISPLAY_IDENTIFIER Characteristic_02
         FORMAT "%6.3"
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_03
         "regulator_03"
         VALUE
         0x1300FF00
         RecordLayout_02
         359.999
         CompuMethod_05
         0.
         359.999
         DISPLAY_IDENTIFIER Characteristic_03
         FORMAT "%6.3"
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_04
         "regulator_04"
         VALUE
         0x1400FF00
         RecordLayout_02
         359.999
         CompuMethod_05
         0.
         359.999
         DISPLAY_IDENTIFIER Characteristic_04
         FORMAT "%6.3"
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_05
         "regulator_05"
         VALUE
         0x1500FF00
         RecordLayout_02
         65535.
         CompuMethod_03
         0.
         65535.
         DISPLAY_IDENTIFIER Characteristic_05
         FORMAT "%6.0"
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_06
         "regulator_06"
         VALUE
         0x1600FF00
         RecordLayout_02
         65535.
         CompuMethod_03
         0.
         65535.
         DISPLAY_IDENTIFIER Characteristic_06
         FORMAT "%6.0"
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_07
         "regulator_07"
         VALUE
         0x1700FF00
         RecordLayout_02
         65535.
         CompuMethod_03
         0.
         65535.
         DISPLAY_IDENTIFIER Characteristic_07
         FORMAT "%6.0"
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_08
         "regulator_08"
         VALUE
         0x1800FF00
         RecordLayout_01
         255.
         CompuMethod_03
         0.
         255.
         DISPLAY_IDENTIFIER Characteristic_08
         FORMAT "%5.0"
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_09
         "regulator_09"
         VALUE
         0x1900FF00
         RecordLayout_02
         1000.9
         CompuMethod_04
         2.e-002
         1001.
         DISPLAY_IDENTIFIER Characteristic_09
         FORMAT "%6.2"
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_10
         "regulator_10"
         VALUE
         0x1A00FF00
         RecordLayout_02
         65535.
         CompuMethod_03
         0.
         65535.
         DISPLAY_IDENTIFIER Characteristic_10
         FORMAT "%5.0"
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_11
         "regulator_11"
         VALUE
         0x1B00FF00
         RecordLayout_02
         65535.
         CompuMethod_03
         0.
         65535.
         DISPLAY_IDENTIFIER Characteristic_11
         FORMAT "%5.0"
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_12
         "regulator_12"
         VALUE
         0x1C00FF00
         RecordLayout_02
         1000.9
         CompuMethod_04
         0.
         1000.9
         DISPLAY_IDENTIFIER Characteristic_12
         FORMAT "%5.1"
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_13
         "regulator_13"
         VALUE
         0x1D00FF00
         RecordLayout_02
         1000.9
         CompuMethod_04
         0.
         1000.9
         DISPLAY_IDENTIFIER Characteristic_13
         FORMAT "%5.1"
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_14
         "regulator_14"
         VALUE
         0x1E00FF00
         RecordLayout_02
         359.999
         CompuMethod_05
         0.
         359.999
         DISPLAY_IDENTIFIER Characteristic_14
         FORMAT "%6.3"
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_15
         "regulator_15"
         MAP
         0x1F00FF00
         RecordLayout_03
         1000.99
         CompuMethod_04
         2.e-002
         1001.
         DISPLAY_IDENTIFIER Characteristic_15
         FORMAT "%6.2"
         /begin AXIS_DESCR
            STD_AXIS
            NO_INPUT_QUANTITY
            CompuMethod_03
            100
            0.
            255.
            FORMAT "%4.0"
         /end AXIS_DESCR
         /begin AXIS_DESCR
            STD_AXIS
            Measurement_16
            CompuMethod_07
            100
            0.
            1000.9
            FORMAT "%5.1"
         /end AXIS_DESCR
      /end CHARACTERISTIC

      /begin CHARACTERISTIC Characteristic_16
         "regulator_16"
         CURVE
         0x2000FF00
         RecordLayout_05
         40.
         CompuMethod_09
         -19.
         20.
         DISPLAY_IDENTIFIER Characteristic_16
         FORMAT "%7.2"
         /begin AXIS_DESCR
            COM_AXIS
            NO_INPUT_QUANTITY
            CompuMethod_08
            20
            0.
            50.
            FORMAT "%4.4"
            AXIS_PTS_REF AxisPts_01
         /end AXIS_DESCR
      /end CHARACTERISTIC

      /begin COMPU_METHOD CompuMethod_01
         ""
         RAT_FUNC
         "%2.2"
         "-"
         COEFFS 0 1. 0. 0 0 2
      /end COMPU_METHOD

      /begin COMPU_METHOD CompuMethod_02
         ""
         TAB_VERB
         "%2.2"
         "-"
         COMPU_TAB_REF CompuVtab_01
      /end COMPU_METHOD

      /begin COMPU_METHOD CompuMethod_03
         "RATIONALFUNCTION_[0;1;0;0;0;1]"
         RAT_FUNC
         "%2.2"
         "-"
         COEFFS 0. 1. 0. 0. 0. 1.
      /end COMPU_METHOD

      /begin COMPU_METHOD CompuMethod_04
         "RATIONALFUNCTION_[0;1;0;0;0;0.02]"
         RAT_FUNC
         "%2.2"
         "s"
         COEFFS 0. 1. 0. 0. 0. 2.e-002
      /end COMPU_METHOD

      /begin COMPU_METHOD CompuMethod_05
         "RATIONALFUNCTION_[0;1;0;0;0;0.1]"
         RAT_FUNC
         "%2.2"
         "%"
         COEFFS 0. 1. 0. 0. 0. 2.5e-003
      /end COMPU_METHOD

      /begin COMPU_METHOD CompuMethod_06
         ""
         RAT_FUNC
         "%2.2"
         "rpm"
         COEFFS 0 4. 0. 0 0 1
      /end COMPU_METHOD

      /begin COMPU_METHOD CompuMethod_07
         "RATIONALFUNCTION_[0;1;0;0;0;0.205]"
         RAT_FUNC
         "%2.2"
         "U/min"
         COEFFS 0. 1. 0. 0. 0. 0.205
      /end COMPU_METHOD

      /begin COMPU_METHOD CompuMethod_08
         ""
         RAT_FUNC
         "%2.2"
         "V"
         COEFFS 0 819. 0. 0 0 1
      /end COMPU_METHOD

      /begin COMPU_METHOD CompuMethod_09
         ""
         RAT_FUNC
         "%4.4"
         "bar"
         COEFFS 0 100. 0. 0 0 1
      /end COMPU_METHOD

      /begin COMPU_VTAB CompuVtab_01
         ""
         TAB_VERB
         2
         0 "FALSE"
         1 "TRUE"
      /end COMPU_VTAB

      /begin RECORD_LAYOUT RecordLayout_01
         FNC_VALUES 1 UBYTE COLUMN_DIR PLONG
      /end RECORD_LAYOUT

      /begin RECORD_LAYOUT RecordLayout_02
         FNC_VALUES 1 UWORD COLUMN_DIR PLONG
      /end RECORD_LAYOUT

      /begin RECORD_LAYOUT RecordLayout_03
         NO_AXIS_PTS_X 1 UBYTE
         AXIS_PTS_X 2 UBYTE INDEX_INCR DIRECT
         NO_AXIS_PTS_Y 3 UWORD
         AXIS_PTS_Y 4 UWORD INDEX_INCR DIRECT
         FNC_VALUES 5 UWORD COLUMN_DIR DIRECT
      /end RECORD_LAYOUT

      /begin RECORD_LAYOUT RecordLayout_04
         NO_AXIS_PTS_X 1 UWORD
         AXIS_PTS_X 2 UWORD INDEX_DECR DIRECT
      /end RECORD_LAYOUT

      /begin RECORD_LAYOUT RecordLayout_05
         FNC_VALUES 1 SWORD COLUMN_DIR PLONG
      /end RECORD_LAYOUT

      /begin AXIS_PTS AxisPts_01
         ""
         0xEE001134
         NO_INPUT_QUANTITY
         RecordLayout_04
         5.
         CompuMethod_08
         2
         0.
         5.
         FORMAT "%4.4"
      /end AXIS_PTS

      /begin FUNCTION Function_01
         "FunctionList_01"
         FUNCTION_VERSION "2.2"
         /begin DEF_CHARACTERISTIC
            Characteristic_01
            Characteristic_02
            Characteristic_03
            Characteristic_04
            Characteristic_05
            Characteristic_06
            Characteristic_07
            Characteristic_08
            Characteristic_09
            Characteristic_10
            Characteristic_11
            Characteristic_12
            Characteristic_13
            Characteristic_14
         /end DEF_CHARACTERISTIC
         /begin OUT_MEASUREMENT
            Measurement_01
            Measurement_02
            Measurement_03
            Measurement_04
         /end OUT_MEASUREMENT
         /begin IN_MEASUREMENT
            Measurement_05
            Measurement_06
            Measurement_07
            Measurement_08
            Measurement_09
            Measurement_10
            Measurement_11
            Measurement_12
            Measurement_13
         /end IN_MEASUREMENT
         /begin LOC_MEASUREMENT
            Measurement_14
            Measurement_15
         /end LOC_MEASUREMENT
      /end FUNCTION
   /end MODULE
/end PROJECT
"""

class TestComment(unittest.TestCase):

    def setUp(self):
        self.parser = A2LParser()

    def testShallAcceptValidA2L(self):
        self.parser.parseFromString(TEST_A2L)
        self.assertEqual(self.parser.logger.getLastError(), (None, None))

if __name__ == '__main__':
    unittest.main()

