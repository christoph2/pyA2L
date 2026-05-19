#!/usr/bin/env python

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

import enum
from collections import Counter, namedtuple
from logging import getLogger

import pya2l.model as model
from pya2l.api.inspect import AxisDescr, Characteristic, Measurement, ModCommon, ModPar


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
    MISSING_COMPU_METHOD = 11
    MISSING_RECORD_LAYOUT = 12


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
        self._session = session
        self._diagnostics = []
        self._identifier = {}

    def __call__(self):
        """Run validation and return an iterable of diagnostics (Message)."""
        # reset previous diagnostics for repeated runs
        self._diagnostics = []
        self.check_top_level_structure()
        self._traverse_db()
        return tuple(self.diagnostics)

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
            # Keep modules for subsequent checks
            pass

    @property
    def session(self):
        return self._session

    def _traverse_db(self):
        """Run all per-module validation checks."""
        for module in self.modules:
            self._validate_mod_common(module)
            self._validate_mod_par(module)
            self._check_namespace_uniqueness(module)
            self._check_compu_method_refs(module)
            self._check_record_layout_refs(module)
            self._check_c_identifier_lengths(module)

    def _validate_mod_common(self, module):
        if module.mod_common is None:
            return
        mod_common = ModCommon(self.session, module.name)
        if mod_common.byteOrder is None:
            self.emit_diagnostic(
                Level.WARNING,
                Category.MISSING,
                Diagnostics.MISSING_BYTE_ORDER,
                f"{module.name}::ModCommon: Missing BYTE_ORDER.",
            )
        # Check raw ORM fields to detect genuinely missing alignment keywords.
        raw = module.mod_common
        ALIGNMENT_FIELDS = {
            "ALIGNMENT_BYTE": raw.alignment_byte,
            "ALIGNMENT_WORD": raw.alignment_word,
            "ALIGNMENT_LONG": raw.alignment_long,
            "ALIGNMENT_INT64": raw.alignment_int64,
            "ALIGNMENT_FLOAT32_IEEE": raw.alignment_float32_ieee,
            "ALIGNMENT_FLOAT64_IEEE": raw.alignment_float64_ieee,
        }
        missing_alignments = [name for name, val in ALIGNMENT_FIELDS.items() if val is None]
        if missing_alignments:
            self.emit_diagnostic(
                Level.WARNING,
                Category.MISSING,
                Diagnostics.MISSING_ALIGNMENT,
                f"{module.name}::ModCommon: Missing ALIGNMENT(s): {missing_alignments}.",
            )

    def _validate_mod_par(self, module):
        if not ModPar.exists(self.session, module.name):
            return
        mod_par = ModPar(self.session, module.name)
        if mod_par.epk is None:
            self.emit_diagnostic(
                Level.WARNING,
                Category.MISSING,
                Diagnostics.MISSING_EPK,
                f"{module.name}::ModPar: Missing EPK.",
            )
        elif not mod_par.addrEpk:
            self.emit_diagnostic(
                Level.WARNING,
                Category.MISSING,
                Diagnostics.MISSING_ADDR_EPK,
                f"{module.name}::ModPar: Missing ADDR_EPK.",
            )
        if mod_par.memoryLayouts:
            self.emit_diagnostic(
                Level.WARNING,
                Category.MISSING,
                Diagnostics.DEPRECATED,
                f"{module.name}::ModPar: MEMORY_LAYOUTs are deprecated, use MEMORY_SEGMENTs instead.",
            )
        # memorySegments

    def _check_namespace_uniqueness(self, module):
        """Check that identifiers are unique within each ASAP2 namespace.

        Namespace 1 (measurement space): axis_pts, characteristic, measurement.
        Namespace 2 (conversion table space): compu_tab, compu_vtab, compu_vtab_range.

        Emits MULTIPLE_DEFINITIONS_IN_NAMESPACE when a name appears more than once
        inside the same namespace. Emits DEFINITION_IN_MULTIPLE_NAMESPACES when the
        same name appears in both namespaces.
        """
        ns1_groups = {
            "axis_pts": names(module.axis_pts),
            "characteristic": names(module.characteristic),
            "measurement": names(module.measurement),
        }
        ns2_groups = {
            "compu_tab": names(module.compu_tab),
            "compu_vtab": names(module.compu_vtab),
            "compu_vtab_range": names(module.compu_vtab_range),
        }

        for ns_label, groups in (("measurement_space", ns1_groups), ("conversion_space", ns2_groups)):
            all_names: list[str] = []
            for table_names in groups.values():
                all_names.extend(table_names)
            cnt = Counter(all_names)
            for name, count in cnt.items():
                if count > 1:
                    self.emit_diagnostic(
                        Level.ERROR,
                        Category.DUPLICATE,
                        Diagnostics.MULTIPLE_DEFINITIONS_IN_NAMESPACE,
                        f"{module.name}: Identifier '{name}' defined {count} times in namespace '{ns_label}'.",
                    )

        ns1_all = set(n for lst in ns1_groups.values() for n in lst)
        ns2_all = set(n for lst in ns2_groups.values() for n in lst)
        cross = ns1_all & ns2_all
        for name in sorted(cross):
            self.emit_diagnostic(
                Level.WARNING,
                Category.DUPLICATE,
                Diagnostics.DEFINITION_IN_MULTIPLE_NAMESPACES,
                f"{module.name}: Identifier '{name}' appears in both the measurement and conversion namespaces.",
            )

    def _check_compu_method_refs(self, module):
        """Verify that every conversion reference points to an existing COMPU_METHOD."""
        valid_names = {cm.name for cm in module.compu_method}
        NO_REF = "NO_COMPU_METHOD"

        def _check(obj_type: str, obj_name: str, conversion: str) -> None:
            if conversion and conversion != NO_REF and conversion not in valid_names:
                self.emit_diagnostic(
                    Level.ERROR,
                    Category.MISSING,
                    Diagnostics.MISSING_COMPU_METHOD,
                    f"{module.name}: {obj_type} '{obj_name}' references unknown COMPU_METHOD '{conversion}'.",
                )

        for meas in module.measurement:
            _check("MEASUREMENT", meas.name, meas.conversion)
        for char in module.characteristic:
            _check("CHARACTERISTIC", char.name, char.conversion)
        for apts in module.axis_pts:
            _check("AXIS_PTS", apts.name, apts.conversion)

    def _check_record_layout_refs(self, module):
        """Verify that every DEPOSIT/RECORD_LAYOUT reference is resolvable."""
        valid_names = {rl.name for rl in module.record_layout}

        for char in module.characteristic:
            if char.deposit and char.deposit not in valid_names:
                self.emit_diagnostic(
                    Level.ERROR,
                    Category.MISSING,
                    Diagnostics.MISSING_RECORD_LAYOUT,
                    f"{module.name}: CHARACTERISTIC '{char.name}' references unknown RECORD_LAYOUT '{char.deposit}'.",
                )
        for apts in module.axis_pts:
            if apts.depositAttr and apts.depositAttr not in valid_names:
                self.emit_diagnostic(
                    Level.ERROR,
                    Category.MISSING,
                    Diagnostics.MISSING_RECORD_LAYOUT,
                    f"{module.name}: AXIS_PTS '{apts.name}' references unknown RECORD_LAYOUT '{apts.depositAttr}'.",
                )

    def _check_c_identifier_lengths(self, module):
        """Emit INVALID_C_IDENTIFIER for any name exceeding MAX_C_IDENTIFIER_LEN (ISO C90)."""
        named_collections = [
            ("MEASUREMENT", module.measurement),
            ("CHARACTERISTIC", module.characteristic),
            ("AXIS_PTS", module.axis_pts),
            ("COMPU_METHOD", module.compu_method),
            ("COMPU_TAB", module.compu_tab),
            ("COMPU_VTAB", module.compu_vtab),
            ("COMPU_VTAB_RANGE", module.compu_vtab_range),
            ("RECORD_LAYOUT", module.record_layout),
        ]
        for obj_type, collection in named_collections:
            for obj in collection:
                if obj.name and len(obj.name) > MAX_C_IDENTIFIER_LEN:
                    self.emit_diagnostic(
                        Level.WARNING,
                        Category.MISSING,
                        Diagnostics.INVALID_C_IDENTIFIER,
                        f"{module.name}: {obj_type} '{obj.name}' exceeds {MAX_C_IDENTIFIER_LEN} chars (ISO C90 limit).",
                    )

    def emit_diagnostic(self, level: Level, category: Category, diag: Diagnostics, message: str | None = None):
        self.logger.warning("%s - %s", level.name, message)
        self._diagnostics.append(Message(level, category, diag, message))

    @property
    def diagnostics(self):
        return self._diagnostics
