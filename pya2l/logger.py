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
import traceback

try:
    from rich.logging import RichHandler

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class Logger:

    LOGGER_BASE_NAME = "pya2l"
    FORMAT = "[%(levelname)s (%(name)s)]: %(message)s"

    def __init__(self, name: str, level: str = "INFO") -> None:
        self.logger = logging.getLogger(f"{self.LOGGER_BASE_NAME}.{name}")
        self.setLevel(level)
        # Add a handler only when neither this logger nor the root logger has one,
        # so application-level logging configuration is respected.
        if not self.logger.handlers and not logging.getLogger().handlers:
            if RICH_AVAILABLE:
                handler: logging.Handler = RichHandler()
            else:
                handler = logging.StreamHandler()
            formatter = logging.Formatter(self.FORMAT)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        self.lastMessage: str | None = None
        self.lastSeverity: int | None = None

    def getLastError(self) -> tuple[int | None, str | None]:
        result = (self.lastSeverity, self.lastMessage)
        self.lastSeverity = self.lastMessage = None
        return result

    def log(self, message: str, level: int) -> None:
        self.lastSeverity = level
        self.lastMessage = message
        self.logger.log(level, f"{message}")

    def info(self, message: str) -> None:
        self.log(message, logging.INFO)

    def warn(self, message: str) -> None:
        self.log(message, logging.WARNING)

    def warning(self, message: str) -> None:
        self.log(message, logging.WARNING)

    def debug(self, message: str) -> None:
        self.log(message, logging.DEBUG)

    def error(self, message: str, exc_info: bool = False) -> None:
        self.log(message, logging.ERROR)
        if exc_info:
            self.logger.error(traceback.format_exc())

    def critical(self, message: str) -> None:
        self.log(message, logging.CRITICAL)

    def verbose(self) -> None:
        self.logger.setLevel(logging.DEBUG)

    def silent(self) -> None:
        self.logger.setLevel(logging.CRITICAL)

    def setLevel(self, level: str | int) -> None:
        LEVEL_MAP: dict[str, int] = {
            "INFO": logging.INFO,
            "WARN": logging.WARNING,
            "WARNING": logging.WARNING,
            "DEBUG": logging.DEBUG,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        if isinstance(level, str):
            level = LEVEL_MAP.get(level.upper(), logging.WARNING)
        self.logger.setLevel(level)
