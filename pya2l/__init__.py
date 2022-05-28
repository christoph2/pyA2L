#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2022 by Christoph Schueler <cpu12.gems.googlemail.com>

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
__version__ = "0.10.2"


import pickle
import pkgutil
import sys
from time import perf_counter
from pathlib import Path
import warnings


import pya2l.model as model
from pya2l.logger import Logger
from pya2l.templates import doTemplateFromText
from pya2l.utils import detect_encoding


class InvalidA2LDatabase(Exception):
    """"""

    pass


class DB(object):
    """"""

    A2L_TEMPLATE = pkgutil.get_data("pya2l.cgen.templates", "a2l.tmpl")

    def import_a2l(
        self,
        file_name,
        debug=False,
        in_memory=False,
        remove_existing=False,
        local=False,
        encoding=None,
        loglevel="INFO",
    ):
        """Import `.a2l` file to `.a2ldb` database.


        Parameters
        ----------
        file_name: str
            Name of the A2L to be imported. If you don't specify an extension ``.a2l`` is added.

        debug: bool
            Additional debugging output.

        in_memory: bool
            Create non-persistent in-memory database.

        remove_existing: bool
            ** DANGER ZONE **: Remove existing database.

        local: bool
            If `True` create A2LDB in current working directory else in A2L source directory.

        encoding: str
            File encoding like "latin-1" or "utf-8" or None to auto-detect.

        loglevel: str
            "INFO" | "WARN" | "DEBUG" | "ERROR" | "CRITICAL"

        Returns
        -------
        SQLAlchemy session object.

        Raises
        ------
        OSError
            If database already exists.

        Note
        ----
        ``AML`` and ``IF_DATA`` sections are currently not processed.
        """
        from os import unlink

        from pya2l.a2l_listener import A2LListener
        from pya2l import parsers
        from pya2l.preprocessor import Preprocessor
        from pya2l.aml.db import Importer

        start_time = perf_counter()
        self.logger = Logger(self.__class__.__name__, loglevel)
        self.in_memory = in_memory

        self._set_path_components(file_name, local)
        if not in_memory:
            if remove_existing:
                try:
                    unlink(str(self._dbfn))
                except Exception:
                    pass
            elif self._dbfn.exists():
                raise OSError("file '{}' already exists.".format(self._dbfn))
        prepro = Preprocessor(loglevel=loglevel)

        encoding = encoding or detect_encoding(file_name=self._a2lfn)
        prepro_result = prepro.process(self._a2lfn, encoding=encoding)
        a2l_parser = parsers.a2l(debug=debug, prepro_result=prepro_result)
        self.logger.info("Parsing pre-processed data ...")
        self.db, listener_result = a2l_parser.parseFromString(prepro_result.a2l_data, dbname=str(self._dbfn), encoding=encoding)
        self.session = self.db.session
        aml_section = prepro_result.aml_section
        if aml_section:
            self.logger.info("Parsing AML section ...")
            aml_parser = parsers.aml(prepro_result=prepro_result)
            aml_result = aml_parser.parseFromString(aml_section, encoding=encoding).listener_result
            aml_parsed = pickle.dumps(aml_result)
            self.session.add(model.AMLSection(text=aml_section, parsed=aml_parsed))
            for item in self.session.query(model.IfData).all():
                ip = parsers.if_data(aml_result)
                parsed_if_data = pickle.dumps(ip.parse(item.raw))
                item.parsed = parsed_if_data
                self.session.add(item)
            self.session.commit()
        self.logger.info("Done [elapsed time {:.2f}s].".format(perf_counter() - start_time))
        return self.session

    def export_a2l(self, file_name=sys.stdout, encoding="utf-8"):
        """"""
        namespace = dict(session=self.db.session, model=model)
        data = doTemplateFromText(self.A2L_TEMPLATE, namespace, formatExceptions=False, encoding=encoding)
        result = []
        for line in data.splitlines():
            line = line.rstrip()
            if not line:
                continue
            else:
                result.append(line)
        result = "\n".join(result)
        print(result)
        # with io.open("{}.render".format(file_name), "w", encoding = encoding, newline = "\r\n") as outf:
        #    outf.write(res)

    def open_create(self, file_name, local=False, encoding=None, loglevel="INFO"):
        """Open or create an A2LDB."""
        self.in_memory = False
        self._set_path_components(file_name)
        if not self._dbfn.exists():
            return self.import_a2l(self._a2lfn, local=local, encoding=encoding, loglevel=loglevel)
        else:
            return self.open_existing(self._dbfn)

    def open_existing(self, file_name):
        """Open an existing `.a2ldb` database.

        Parameters
        ----------
        file_name: str
            Name of your database file, resulting from :meth:`import_a2l`.
            Extension `.a2ldb` not needed.

        Returns
        -------
        SQLAlchemy session object.

        Raises
        ------
        OSError
            If database already exists.
        """
        self.in_memory = False
        self._set_path_components(file_name)
        if not self._dbfn.exists():
            raise OSError("file '{}' does not exists.".format(self._dbfn))
        else:
            self.db = model.A2LDatabase(str(self._dbfn))
            self.session = self.db.session
            res = self.session.query(model.MetaData).first()
            if res:
                return self.session
            else:
                raise InvalidA2LDatabase("Database seems to be corrupted. No meta-data found.")

    def close(self):
        self.db.close()

    def _set_path_components(self, file_name, local=False):
        """"""
        if hasattr(self, "_dbfn"):
            return
        file_path = Path(file_name)
        if self.in_memory:
            self._dbfn = ":memory:"
        else:
            if local:
                self._dbfn = Path(file_path.stem).with_suffix(".a2ldb")
            else:
                self._dbfn = (file_path.parent / file_path.stem).with_suffix(".a2ldb")
        if not file_path.suffix:
            self._a2lfn = (file_path.parent / file_path.stem).with_suffix(".a2l")
        else:
            self._a2lfn = (file_path.parent / file_path.stem).with_suffix(file_path.suffix)
