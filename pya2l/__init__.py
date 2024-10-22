#!/usr/bin/env python

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2023 by Christoph Schueler <cpu12.gems.googlemail.com>

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


# import pickle  # nosec
import pkgutil
import sys
from pathlib import Path
from time import perf_counter

from rich.traceback import install

import pya2l.model as model
from pya2l.logger import Logger
from pya2l.templates import doTemplateFromText
from pya2l.utils import detect_encoding


install(show_locals=True, max_frames=3)  # Install custom exception handler.


class InvalidA2LDatabase(Exception):
    """"""

    pass


class DB:
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

        print("Enter importer...")

        from os import unlink

        from pya2l import parsers

        # from pya2l.aml.db import Importer
        from pya2l.preprocessor import Preprocessor

        start_time = perf_counter()
        self.logger = Logger(self.__class__.__name__, loglevel)
        self.in_memory = in_memory

        self._set_path_components(file_name, local)
        if not in_memory:
            if remove_existing:
                try:
                    unlink(str(self._dbfn))
                except Exception:
                    pass  # nosec
            elif self._dbfn.exists():
                raise OSError(f"file '{self._dbfn}' already exists.")  # Use 'open_create()' or 'open_existing()'.--

        print("Enter pre-processor...")

        prepro = Preprocessor(loglevel=loglevel)

        if encoding is None:
            self.logger.info("Detecting encoding...")
            encoding = detect_encoding(file_name=self._a2lfn)
        prepro_result = prepro.process(str(self._a2lfn), encoding=encoding)
        prepro.finalize()
        filenames, line_map, ifdata_reader = prepro_result
        a2l_parser = parsers.a2l(debug=debug, prepro_result=prepro_result)
        self.logger.info("Parsing pre-processed data ...")
        self.db = a2l_parser.parse(filename=filenames.a2l, dbname=str(self._dbfn), encoding=encoding)
        self.session = self.db.session

        # self.logger.info("Parsing AML section ...")

        def parse_aml(file_name: str) -> bytes:
            from pya2l import amlparser_ext

            text: bytes = open(file_name, "rb").read()
            result: bytes = amlparser_ext.parse_aml(text)
            return text, result

        # aml_text, aml_parsed = parse_aml(filenames.aml)
        # self.session.add(model.AMLSection(text=aml_text, parsed=aml_parsed))

        """

        self.session.add(model.AMLSection(text=aml_text, parsed=aml_parsed))
        self.logger.info("Parsing IF_DATA sections ...")

        ip = parsers.if_data(aml_result)
        for item in self.session.query(model.IfData).all():
            parsed_if_data = pickle.dumps(ip.parse(item.raw))
            item.parsed = parsed_if_data
            self.session.add(item)
        """
        self.session.commit()
        self.logger.info(f"Done [Elapsed time {perf_counter() - start_time:.2f}s].")
        a2l_parser.close()
        return self.session

    def export_a2l(self, file_name=sys.stdout, encoding="utf-8"):
        """
        Parameters
        ----------
        file_name: str
            Name of the A2L exported.

        encoding: str
            File encoding like "latin-1" or "utf-8".
        """
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
            raise OSError(f"file '{self._dbfn}' does not exists.")
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
        """
        Parameters
        ----------
        file_name: str

        local: bool
        """
        if hasattr(self, "_dbfn"):
            return
        file_path = Path(file_name)
        if self.in_memory:
            self._dbfn = ":memory:"
        else:
            if local:
                self._dbfn = enforce_suffix(Path(file_path.stem), ".a2ldb")
            else:
                self._dbfn = enforce_suffix((file_path.parent / file_path.stem), ".a2ldb")
        if not file_path.suffix:
            self._a2lfn = enforce_suffix((file_path.parent / file_path.stem), ".a2l")
        else:
            self._a2lfn = enforce_suffix((file_path.parent / file_path.stem), file_path.suffix)


def enforce_suffix(pth: Path, suffix: str):
    """Path.with_suffix() works not as expected, if filename contains dots."""
    if not str(pth).endswith(suffix):
        return Path(str(pth) + suffix)
    return pth
