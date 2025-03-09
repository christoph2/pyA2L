__copyright__ = """
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2022-2025 by Christoph Schueler <github.com/Christoph2,
                                        cpu12.gems@googlemail.com>

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

import argparse
import sys
from pathlib import Path

from pya2l import DB
from pya2l.version import __version__


def main():
    parser = argparse.ArgumentParser(description="Import/export from/to a2l(db) files.")

    group = parser.add_argument_group()
    group.add_argument(
        "-o",
        "--output",
        help="output file when exporting",
        dest="output",
        type=str,
        metavar="output_file",
    )

    parser.add_argument(
        "-E",
        "--encoding",
        help="Import file encoding, like ascii, latin-1, utf-8, ...",
        dest="encoding",
        type=str,
        default=None,
    )
    parser.add_argument(
        "-L",
        "--local-directory",
        help="If option is used, create DB in current working directory, else use import path.",
        action="store_true",
        default=False,
        dest="local",
    )
    parser.add_argument(
        "-l",
        help="Verbosity of log messages",
        choices=["warn", "info", "error", "debug", "critical", "WARN", "INFO", "ERROR", "DEBUG", "CRITICAL"],
        dest="loglevel",
        type=str,
        default="info",
    )

    parser.add_argument(
        "-p",
        help="Disable progress bar",
        action="store_true",
        dest="no_progress_bar",
    )

    parser.add_argument(
        "-V",
        help="Print pya2ldb version information and exit.",
        action="store_true",
        dest="version",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-i",
        "--import",
        help="A2L file to import",
        dest="ifn",
        type=str,
        metavar="A2L_file",
    )
    group.add_argument(
        "-e",
        "--export",
        help="A2LDB file to export",
        dest="efn",
        type=str,
        metavar="DB_file",
    )

    # parser.add_argument("-f", "--force-overwrite", help = "Force overwrite of existing file",
    # default = False, action = "store_true")

    args = parser.parse_args()
    if args.version:
        print(f"pya2ldb version: {__version__}")
        sys.exit(1)
    if not (args.ifn or args.efn):
        print("Either -i or -e option is required.")
        sys.exit(2)
    db = DB()

    if args.efn:
        efn = Path(args.efn)
        db.export_a2l(efn, args.output or sys.stdout)
    else:
        ifn = Path(args.ifn)
        session = db.import_a2l(
            ifn, encoding=args.encoding, loglevel=args.loglevel, local=args.local, progress_bar=not args.no_progress_bar
        )
        session.close()


if __name__ == "__main__":
    main()
