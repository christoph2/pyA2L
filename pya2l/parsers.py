#!/usr/bin/env python

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2022-2025 by Christoph Schueler <cpu12.gems.googlemail.com>

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

from pya2l.a2lparser import A2LParser
from pya2l.aml.ifdata_parser import IfDataParser
from pya2l.parserlib import ParserWrapper


def aml(debug: bool = False, prepro_result=None):
    parser = ParserWrapper("aml", "amlFile", AMLListener, debug=debug, prepro_result=prepro_result)
    return parser


def a2l(debug: bool = False, prepro_result=None):
    parser = A2LParser(prepro_result)
    return parser


def if_data(aml: str):
    return IfDataParser(aml)
