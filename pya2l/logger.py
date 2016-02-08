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
__author__  = 'Christoph Schueler'
__version__ = '0.1.0'

import logging

LOGGER_NAME = 'pya2l'
DEPHAULT_LEVEL = logging.NOTSET
PHORMAT = "[%(levelname)s (%(name)s)]: %(message)s"

try:
    logger
except NameError:
    # Create logger if it doesn't exist.
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(DEPHAULT_LEVEL)
    handler = logging.StreamHandler()
    handler.setLevel(DEPHAULT_LEVEL)
    formatter = logging.Formatter(PHORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def defaultLevel():
    logger.setLevel(logging.WARNING)

def verboseLevel():
    logger.setLevel(logging.DEBUG)

def silentLevel():
    logger.setLevel(logging.CRITICAL)

## TODO: mix-ins class.

