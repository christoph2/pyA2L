#!/usr/bin/env python

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2024 by Christoph Schueler <cpu12.gems.googlemail.com>

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

import logging

from rich.logging import RichHandler


class Logger:

    LOGGER_BASE_NAME = "pya2l"
    FORMAT = "[%(levelname)s (%(name)s)]: %(message)s"

    def __init__(self, name, level="INFO"):
        if not logging.getLogger().handlers:
            self.logger = logging.getLogger(f"{self.LOGGER_BASE_NAME}.{name}")
            # self.logger.setLevel(level.upper())
            self.setLevel(level)
            # handler = logging.StreamHandler()
            handler = RichHandler()
            # handler.setLevel(level.upper())
            formatter = logging.Formatter(self.FORMAT)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.logger = logging.getLogger("rich")
        self.lastMessage = None
        self.lastSeverity = None

    def getLastError(self):
        result = (self.lastSeverity, self.lastMessage)
        self.lastSeverity = self.lastMessage = None
        return result

    def log(self, message, level):
        self.lastSeverity = level
        self.lastMessage = message
        self.logger.log(level, f"{message}")
        # print("{0}{1}".format(level, message))

    def info(self, message):
        self.log(message, logging.INFO)

    def warn(self, message):
        self.log(message, logging.WARN)

    def debug(self, message):
        self.log(message, logging.DEBUG)

    def error(self, message):
        self.log(message, logging.ERROR)

    def critical(self, message):
        self.log(message, logging.CRITICAL)

    def verbose(self):
        self.logger.setLevel(logging.DEBUG)

    def silent(self):
        self.logger.setLevel(logging.CRITICAL)

    def setLevel(self, level):
        LEVEL_MAP = {
            "INFO": logging.INFO,
            "WARN": logging.WARN,
            "DEBUG": logging.DEBUG,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        if isinstance(level, str):
            level = LEVEL_MAP.get(level.upper(), logging.WARN)
        self.logger.setLevel(level)
