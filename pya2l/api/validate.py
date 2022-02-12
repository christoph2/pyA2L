#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2021 by Christoph Schueler <cpu12.gems@googlemail.com>

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

"""Validate A2L database according to ASAP2 rules (and more...).
"""

from collections import Counter, namedtuple
import enum
from itertools import combinations, filterfalse
from logging import getLogger

from pya2l import DB
from pya2l.api.inspect import Characteristic, AxisDescr, ModPar, ModCommon, Measurement
import pya2l.model as model


# *** Validator generated no diagnostic messages ***

Message = namedtuple("Message", "type category diag_code text")


class Level(enum.IntEnum):
    INFORMATION = 1
    WARNING = 2
    ERROR = 3


class Category(enum.IntEnum):
    DUPLICATE = 1
    MISSING = 2
    OBSOLETE = 3


class Diagnostics(enum.IntEnum):
    MULTIPLE_DEFINITIONS_IN_NAMESPACE = 1
    DEFINITION_IN_MULTIPLE_NAMESPACES = 2
    INVALID_C_IDENTIFIER = 3
    MISSING_BYTE_ORDER = 4
    MISSING_ALIGNMENT = 5
    MISSING_EPK = 6
    MISSING_ADDR_EPK = 7
    MISSING_MODULE = 8
    DEPRECATED = 9
    OVERLAPPING_MEMORY = 10


MAX_C_IDENTIFIER_LEN = 32  # ISO C90.


# any(len(e) > MAX_C_IDENTIFIER_LEN for e in 'CM.VTAB_RANGE.DEFAULT_VALUE.REF'.split("."))
# Some part of '{}' are longer than 32 chars (ISO C90 limit).


def names(objs):
    """ """
    return [o.name for o in objs]


class Validator:
    """
    Paramaters
    ----------
    session: Sqlite3 database object.
    """

    def __init__(self, session, loglevel="INFO"):
        self.logger = getLogger(self.__class__.__name__)
        # self.logger.setLevel("INFO")
        self._session = session
        self._diagnostics = []
        self._identifier = {}

    def __call__(self):
        """Run validation."""
        self.check_top_level_structure()
        self._traverse_db()
        print(self.diagnostics)

    def check_top_level_structure(self):
        self.modules = self.session.query(model.Module).all()
        if not self.modules:
            self.emit_diagnostic(
                Level.WARNING,
                Category.MISSING,
                Diagnostics.MISSING_MODULE,
                "A2l file requires at least one /MODULE.",
            )
        else:
            for module in self.modules:
                print(module)

    @property
    def session(self):
        return self._session

    def _traverse_db(self):
        """ """

        """
        'a2ml', 'axis_pts', 'characteristic', 'compu_method',
        'compu_tab', 'compu_vtab', 'compu_vtab_range', 'frame', 'function', 'group', 'if_data', 'if_data_association',
        'longIdentifier', 'measurement', 'mod_common', 'mod_par', 'name', 'project', 'record_layout', 'unit',
        'user_rights', 'variant_coding'
        """
        for module in self.modules:
            self._validate_mod_common(module)
            self._validate_mod_par(module)

    def _validate_mod_common(self, module):
        mod_common = mod_common = ModCommon(self.session, module.name)
        if mod_common.byteOrder is None:
            self.emit_diagnostic(
                Level.WARNING,
                Category.MISSING,
                Diagnostics.MISSING_BYTE_ORDER,
                "{}::ModCommon: Missing BYTE_ORDER.".format(module.name),
            )
        missing_alignments = [e for e in mod_common.alignment.items() if e[1] is None]
        if missing_alignments:
            self.emit_diagnostic(
                Level.WARNING,
                Category.MISSING,
                Diagnostics.MISSING_ALIGNMENT,
                "{}::ModCommon: Missing ALIGNMENT(s): {}.".format(module.name, [e[0] for e in missing_alignments]),
            )

    def _validate_mod_par(self, module):
        if not ModPar.exists(self.session, module.name):
            return
        mod_par = ModPar(self.session, module.name)
        print(mod_par, end="\n\n")
        if mod_par.epk is None:
            self.emit_diagnostic(
                Level.WARNING,
                Category.MISSING,
                Diagnostics.MISSING_EPK,
                "{}::ModPar: Missing EPK.".format(module.name),
            )
        elif not mod_par.adrEpk:
            self.emit_diagnostic(
                Level.WARNING,
                Category.MISSING,
                Diagnostics.MISSING_ADDR_EPK,
                "{}::ModPar: Missing ADDR_EPK.".format(module.name),
            )
        if mod_par.memoryLayouts:
            self.emit_diagnostic(
                Level.WARNING,
                Category.MISSING,
                Diagnostics.DEPRECATED,
                "{}::ModPar: MEMORY_LAYOUTs are deprecated, use MEMORY_SEGMENTs instead.".format(module.name),
            )
        # memorySegments

    '''
    def duplicate_ids(self, objs):
        """
        """
        cnt = Counter(names(objs))
        #cnt["CM.TAB_NOINTP.NO_DEFAULT_VALUE.REF"] = 3
        dups = filterfalse(lambda x: x[1] == 1, cnt.items())
        print(list(names(objs)), end = "\n\n")
        return list(dups)

    def _load_module_identifiers(self):
        TABLES = ("axis_pts", "characteristic", "compu_method", "compu_tab", "compu_vtab", "compu_vtab_range",
            "frame", "function", "group", "measurement", "mod_common", "mod_par", "record_layout", "unit",
            "user_rights", "variant_coding",
        )

    def check_uniqueness(self, module, tables):
        table_combinations = combinations(tables,2 )    # Pairwise.
        print("TC:", list(table_combinations))

    def check_namespaces(self):
        """
        """
        modules = self.session.query(model.Module).all()
        for module in modules:
            print(module)
            self.check_uniqueness(module, ("compu_vtab", "compu_vtab_range", "compu_tab"))
            self.check_uniqueness(module, ("axis_pts", "characteristic", "measurement"))
            dups = self.duplicate_ids(module.compu_tab)
            if dups:
                for dup, cnt in dups:
                    print("COMPU_TAB: multiple occurrences of identifier '{}'.".format(dup))
            print("TAB:", names(module.compu_tab), end = "\n\n")
            print("VTAB:", names(module.compu_vtab), end = "\n\n")
            print("VTAB-RANGE:", names(module.compu_vtab_range), end = "\n\n")
    '''

    def emit_diagnostic(self, level: Level, category: Category, diag: Diagnostics, message: str = None):
        self.logger.warn("{} - {}".format(level.name, message))
        self._diagnostics.append(Message(level, category, diag, message))

    @property
    def diagnostics(self):
        return self._diagnostics


"""

class MODULE(Keyword):
    multiple = True
    block = True
    children = [
        "A2ML",
        "AXIS_PTS",
        "CHARACTERISTIC",
        "COMPU_METHOD",
        "COMPU_TAB",
        "COMPU_VTAB",
        "COMPU_VTAB_RANGE",
        "FRAME",
        "FUNCTION",
        "GROUP",
        "IF_DATA",
        "INSTANCE",
        "MEASUREMENT",
        "MOD_COMMON",
        "MOD_PAR",
        "RECORD_LAYOUT",
        "STRUCTURE_COMPONENT",
        "TYPEDEF_MEASUREMENT",
        "TYPEDEF_STRUCTURE",
        "UNIT",
        "USER_RIGHTS",
        "VARIANT_CODING",
    ]
"""
