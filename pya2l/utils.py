#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2021 by Christoph Schueler <cpu12.gems.googlemail.com>

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

import ctypes
import pathlib
import subprocess
import sys
import threading
from unicodedata import normalize

from chardet.universaldetector import UniversalDetector

def slicer(iterable, sliceLength, converter=None):
    if converter is None:
        converter = type(iterable)
    length = len(iterable)
    return [
        converter(*(iterable[item : item + sliceLength]))
        for item in range(0, length, sliceLength)
    ]


if sys.version_info.major == 3:
    from io import BytesIO as StringIO
else:
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO


def createStringBuffer(*args):
    """Create a string with file-like behaviour (StringIO on Python 2.x)."""
    return StringIO(*args)


CYG_PREFIX = "/cygdrive/"


def cygpathToWin(path):
    if path.startswith(CYG_PREFIX):
        path = path[len(CYG_PREFIX) :]
        driveLetter = "{0}:\\".format(path[0])
        path = path[2:].replace("/", "\\")
        path = "{0}{1}".format(driveLetter, path)
    return path


class SingletonBase(object):
    _lock = threading.Lock()

    def __new__(cls):
        # Double-Checked Locking
        if not hasattr(cls, "_instance"):
            try:
                cls._lock.acquire()
                if not hasattr(cls, "_instance"):
                    cls._instance = super(cls.__class__, cls).__new__(cls)
            finally:
                cls._lock.release()
        return cls._instance


class NotAvailable(SingletonBase):
    """Pseudo numeric, needed for sorting stuff (`None` is unordered)."""

    def __lt__(self, other):
        return True

    def __gt__(self, other):
        return False

    def __str__(self):
        return "n/a"

    __repr__ = __str__


class StructureWithEnums(ctypes.Structure):
    """Add missing enum feature to ctypes Structures."""

    _map = {}

    def __getattribute__(self, name):
        _map = ctypes.Structure.__getattribute__(self, "_map")
        value = ctypes.Structure.__getattribute__(self, name)
        if name in _map:
            EnumClass = _map[name]
            if isinstance(value, ctypes.Array):
                return [EnumClass(x) for x in value]
            else:
                return EnumClass(value)
        else:
            return value

    def __str__(self):
        result = []
        result.append("struct {0} {{".format(self.__class__.__name__))
        for field in self._fields_:
            attr, attrType = field
            if attr in self._map:
                attrType = self._map[attr]
            value = getattr(self, attr)
            result.append(
                "    {0} [{1}] = {2!r};".format(attr, attrType.__name__, value)
            )
        result.append("};")
        return "\n".join(result)

    __repr__ = __str__


class Tristate(object):
    def __init__(self, value=None):
        if any(value is v for v in (True, False, None)):
            self.value = value
        else:
            raise ValueError("Tristate value must be True, False, or None")

    def __eq__(self, other):
        return (
            self.value is other.value
            if isinstance(other, Tristate)
            else self.value is other
        )

    def __ne__(self, other):
        return not self == other

    def __nonzero__(self):  # Python 3: __bool__()
        raise TypeError("Tristate object may not be used as a Boolean")

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "Tristate(%s)" % self.value


class Bunch(dict):
    """"""

    def __init__(self, *args, **kwds):
        super(Bunch, self).__init__(*args, **kwds)
        self.__dict__ = self


class CommandError(Exception):
    pass


def runCommand(cmd):
    proc = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    result = proc.communicate()
    proc.wait()
    if proc.returncode:
        raise CommandError("{0}".format(result[1]))
    return result[0]


def nfc_equal(str1, str2):
    return normalize("NFC", str1) == normalize("NFC", str2)


def fold_equal(str1, str2):
    return normalize("NFC", str1).casefold() == normalize("NFC", str2).casefold()


def align_as(offset: int, boundary: int):
    """Align `offset` to `boundary` bytes.

    Parameters
    ----------
    offset: int

    boundary: int

    Returns
    -------
    int
        Aligned offset.
    """
    return (offset + (boundary - 1)) & -boundary


def padding(offset: int, boundary: int):
    """Calculate number of padding bytes for a given `offset` and `boundary`

    Parameters
    ----------
    offset: int

    boundary: int

    Returns
    -------
    int
        Number of padding bytes.
    """
    return -offset & (boundary - 1)

def ffs(v: int) -> int:
    """Find first set bit (pure Python)."""
    return (v & (-v)).bit_length() - 1

def detect_encoding(file_name: str) -> str:
    """Detect encoding of a text file.

    Parameters
    ----------
    file_name: str

    Returns
    -------
    str: Useable as `encoding` paramter to `open`.
    """
    detector = UniversalDetector()
    if isinstance(file_name, pathlib.WindowsPath):
        file_name = str(file_name)
    for line in open(file_name, "rb"):
        detector.feed(line)
        if detector.done:
            break
    result = detector.result['encoding'] if detector.done else "ascii"
    detector.close()
    return result

