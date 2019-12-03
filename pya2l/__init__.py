#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2019 by Christoph Schueler <cpu12.gems.googlemail.com>

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
__version__ = "0.10.2"

#import pkg_resources
#pkg_resources.declare_namespace(__name__)

from os import path, unlink

from pya2l.a2l_listener import ParserWrapper, A2LListener, cut_a2ml
from pya2l.logger import Logger


class DB(object):
    """
    """

    logger = Logger(__name__)

    def import_a2l(self, file_name, debug = False):
        """
        """
        parser = ParserWrapper('a2l', 'a2lFile', A2LListener, debug = debug)

        self._set_path_components(file_name)
        try:
            unlink(self._dbfn)
        except Exception:
            pass

        #data = open(fname).read()
        #data, a2ml = cut_a2ml(data)

        #session = parser.parseFromString(data, dbname = dbfn)
        #return session

    def export_a2l(self, file_name):
        """
        """
        self._set_path_components(file_name)
        #raise NotImplementedError("Export functionality not implemented yet.")

    def open(self, file_name):
        """
        """
        self._set_path_components(file_name)

    def exists(self, file_name):
        """
        """
        self._set_path_components(file_name)

    def _set_path_components(self, file_name):
        """
        """
        self._pth, self._base = path.split(file_name)
        fbase, ext = path.splitext(self._base)
        self._dbfn = "{}.a2ldb".format(fbase)
        if not ext or ext.lower() == ".a2l" or ext.lower() == ".a2ldb":
            self._a2lfn = "{}.a2l".format(fbase)
        else:
            self._a2lfn = "{}{}".format(fbase, ext)

