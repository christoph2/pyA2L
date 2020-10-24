#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2016 by Christoph Schueler <cpu12.gems.googlemail.com>

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
__author__ = "Christoph Schueler"
__version__ = "0.1.0"


import unittest

from pya2l import aml

"""
"""

AML = """
/begin A2ML
  enum mem_typ   { "INTERN" = 0, "EXTERN" = 1 };
  enum addr_typ  { "BYTE" = 1, "WORD" = 2, "LONG" = 4 };
  enum addr_mode  { "DIRECT" = 0, "INDIRECT" = 1 };

  taggedunion IF_DATA {
    "DIM" taggedstruct {
    (block "SOURCE" struct  {
        struct {
            char [101];
            int;
            long;
        };
        taggedstruct {
            block "QP_BLOB" struct  {
              ulong;
              int;
              ulong;
              long;
            };
        };
    })*;

    block "TP_BLOB" struct   {
        int;
    };

    block "KP_BLOB" struct {
        ulong;
        enum addr_typ;
    };

    block "DP_BLOB" struct {
        enum mem_typ;
    };

    block "PA_BLOB" struct {
        enum addr_mode;
    };
};
};
/end A2ML
"""


class TestAcceptance(unittest.TestCase):
    def setUp(self):
        self.parser = aml.ParserWrapper("aml", "amlFile")

    def testBasicAcceptance(self):
        tree = self.parser.parseFromString(AML)
        self.assertEqual(self.parser.numberOfSyntaxErrors, 0)


def main():
    unittest.main()


if __name__ == "__main__":
    main()
