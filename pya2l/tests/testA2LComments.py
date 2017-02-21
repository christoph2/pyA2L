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

class TestComment(unittest.TestCase):

    COMMENT = """/***********************************************************************************
*                                                                                  *
*   ASAP2 v1.6.1 language example                                                  *
*                                                                                  *
*   2013-02-13                                                                     *
*   File: example-a2l-file.a2l                                                     *
*   Version: 1.0                                                                   *
*                                                                                  *
*   ASAM e.V.                                                                      *
*   Altlaufstr. 40                                                                 *
*   85635 Hoehenkirchen                                                            *
*                                                                                  *
************************************************************************************/"""
    NESTED_COMMENT = """/************************************************************************************
*                                                                                  *
*   ASAP2 v1.6.1 language example                                                  *
*                                                                                  *
*   2013-02-13                                                                     *
*   File: example-a2l-file.a2l        /* I am a nested comment! */                 *
*   Version: 1.0                                                                   *
*                                                                                  *
*   ASAM e.V.                                                                      *
*   Altlaufstr. 40                                                                 *
*   85635 Hoehenkirchen                                                            *
*                                                                                  *
************************************************************************************/"""
    UNCLOSED_COMMENT = """/************************************************************************************
*                                                                                  *
*   ASAP2 v1.6.1 language example                                                  *
*                                                                                  *
*   2013-02-13                                                                     *
*   File: example-a2l-file.a2l                                                     *
*   Version: 1.0                                                                   *
*                                                                                  *
*   ASAM e.V.                                                                      *
*   Altlaufstr. 40                                                                 *
*   85635 Hoehenkirchen                                                            *
*                                                                                  *
************************************************************************************"""

    def setUp(self):
        self.parser = A2LParser()

    def testShallAcceptValidComment(self):
        self.parser.parseFromString(self.COMMENT)
        self.assertEqual(self.parser.logger.getLastError(), (None, None))

    #def testShallRejectNestedComment(self):
    #    self.parser.parseFromString(self.NESTED_COMMENT)
    #    _, msg = self.parser.logger.getLastError()
    #    self.assertEqual(msg, "Nested comments are not allowed.")

    @unittest.skip("skip-me")
    def testShallDetectNotClosedComment(self):
        self.parser.parseFromString(self.UNCLOSED_COMMENT)
        _, msg = self.parser.logger.getLastError()
        self.assertEqual(msg, "Premature end-of-file while processing comment.")

def main():
  unittest.main()

if __name__ == '__main__':
  main()

