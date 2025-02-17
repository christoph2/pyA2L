#!/usr/bin/env python

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2025 by Christoph Schueler <cpu12.gems.googlemail.com>

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

import sys
import typing
from io import TextIOWrapper

from rich.traceback import install

import pya2l.model as model
from pya2l.a2lparser import A2LParser, path_components
from pya2l.logger import Logger
from pya2l.templates import doTemplateFromText


install(show_locals=True, max_frames=3)  # Install custom exception handler.
pyver = sys.version_info


class InvalidA2LDatabase(Exception):
    """"""

    pass


a2l_logger = Logger("A2LDB", "INFO")

if pyver.major == 3 and pyver.minor <= 9:
    import pkg_resources

    A2L_TEMPLATE = str(pkg_resources.resource_string("pya2l.cgen.templates", "a2l.tmpl"), encoding="utf8")
else:
    import importlib.resources

    with (importlib.resources.files("pya2l.cgen.templates") / "a2l.tmpl").open(encoding="utf8") as data:
        A2L_TEMPLATE = data.read()


def import_a2l(
    file_name: str,
    debug: bool = False,
    in_memory: bool = False,
    remove_existing: bool = False,
    local: bool = False,
    encoding: str = "latin-1",
    loglevel: str = "INFO",
    progress_bar: bool = True,
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

    progress_bar: bool
        Disable progress bar.

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

    a2l_parser = A2LParser()
    db = a2l_parser.parse(
        file_name=file_name,
        local=local,
        in_memory=in_memory,
        encoding=encoding,
        remove_existing=remove_existing,
        loglevel=loglevel,
        progress_bar=progress_bar,
    )
    session = db.session

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
    session.commit()
    return session


def open_existing(file_name: str, loglevel: str = "INFO"):
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
    _, db_fn = path_components(in_memory=False, file_name=file_name)

    if not db_fn.exists():
        raise OSError(f"file {db_fn!r} does not exists.")
    else:
        db = model.A2LDatabase(str(db_fn))
        session = db.session
        res = session.query(model.MetaData).first()
        if res:
            return session
        else:
            raise InvalidA2LDatabase("Database seems to be corrupted. No meta-data found.")
        return session


def open_create(file_name: str, local: bool = False, encoding: str = "latin-1", loglevel: str = "INFO"):
    """Open or create an A2LDB."""

    a2l_fn, db_fn = path_components(in_memory=False, file_name=file_name)
    if not db_fn.exists():
        return import_a2l(a2l_fn, local=local, encoding=encoding, loglevel=loglevel)
    else:
        return open_existing(db_fn, loglevel)


def export_a2l(db_name: str, output: typing.Union[TextIOWrapper, str, typing.Any] = sys.stdout, encoding="latin1"):  # noqa: UP007
    """
    Parameters
    ----------
    file_name: str
        Name of the A2L exported.

    encoding: str
        File encoding like "latin-1" or "utf-8".
    """
    session = open_existing(db_name)
    namespace = dict(session=session, model=model)
    data = doTemplateFromText(A2L_TEMPLATE, namespace, formatExceptions=False, encoding=encoding)
    if isinstance(output, TextIOWrapper):
        output.write(data)
    else:
        with open(file=output, mode="w", encoding=encoding) as outf:
            outf.write(data)


class DB:
    """"""

    def __init__(self, loglevel: str = "") -> None:
        if loglevel:
            a2l_logger.setLevel(loglevel)

    @staticmethod
    def import_a2l(
        file_name: str,
        debug: bool = False,
        in_memory: bool = False,
        remove_existing: bool = False,
        local: bool = False,
        encoding: str = "latin-1",
        loglevel: str = "INFO",
        progress_bar: bool = True,
    ):
        return import_a2l(file_name, debug, in_memory, remove_existing, local, encoding, loglevel, progress_bar)

    @staticmethod
    def open_existing(file_name: str, loglevel: str = "INFO"):
        return open_existing(file_name, loglevel)

    @staticmethod
    def open_create(file_name: str, local: bool = False, encoding: str = "latin-1", loglevel: str = "INFO"):
        return open_create(file_name, local, encoding, loglevel)

    @staticmethod
    def export_a2l(
        db_name: str, output: typing.Union[TextIOWrapper, str, typing.Any] = sys.stdout, encoding: str = "latin1"  # noqa: UP007
    ):
        export_a2l(db_name, output, encoding)
