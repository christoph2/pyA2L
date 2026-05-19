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
import json
import logging
import sys
import traceback
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

from pya2l import import_a2l
from pya2l.a2lparser import path_components
from pya2l.imex import (
    export_a2l_db,
    export_json_dict,
    open_a2l_database,
    open_json_database,
)
from pya2l.version import __version__


_logger = logging.getLogger(__name__)
_console = Console(stderr=True)


def main():
    parser = argparse.ArgumentParser(description="Import/export from/to a2l(db) files.")

    group = parser.add_argument_group()
    group.add_argument(
        "-o",
        "--output",
        help="output file when exporting (defaults to stdout)",
        dest="output",
        type=str,
        metavar="output_file",
    )
    parser.add_argument(
        "-m",
        "--module",
        help="Optional: export only this module",
        dest="module",
        type=str,
        metavar="module_name",
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
        "-q",
        "--quiet",
        help="Suppress all output except errors (sets log level to CRITICAL, disables progress bar)",
        action="store_true",
        default=False,
        dest="quiet",
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
    parser.add_argument(
        "--json",
        help="Export to JSON instead of A2L",
        action="store_true",
        dest="json_export",
    )
    parser.add_argument(
        "--pretty",
        help="Pretty-print JSON export",
        action="store_true",
        dest="pretty",
    )

    parser.add_argument(
        "-f",
        "--force-overwrite",
        help="Overwrite existing .a2ldb without prompting",
        default=False,
        action="store_true",
        dest="force_overwrite",
    )

    args = parser.parse_args()
    if args.version:
        _console.print(f"pya2ldb version: {__version__}")
        sys.exit(0)
    if not (args.ifn or args.efn):
        _console.print("[red]Either -i or -e option is required.[/red]")
        parser.print_usage(sys.stderr)
        sys.exit(2)

    # --quiet overrides -l
    if args.quiet:
        args.loglevel = "critical"
        args.no_progress_bar = True

    if args.efn:
        db_path = Path(args.efn)
        if args.json_export:
            db_json = open_json_database(db_path, args.loglevel)
            try:
                payload = export_json_dict(db_json, args.module)
            finally:
                try:
                    db_json.close()
                except Exception:
                    _logger.debug("Error closing JSON database.", exc_info=True)

            out = args.output
            json_kwargs = {"ensure_ascii": False}
            if args.pretty:
                json_kwargs["indent"] = 4
            else:
                json_kwargs["separators"] = (",", ":")
            if out:
                with Path(out).open("w", encoding="utf-8") as fh:
                    json.dump(payload, fh, **json_kwargs)
            else:
                json.dump(payload, sys.stdout, **json_kwargs)
                sys.stdout.write("\n")
        else:
            db_export = open_a2l_database(db_path, args.loglevel)
            try:
                target = sys.stdout if not args.output else Path(args.output)
                export_a2l_db(db_export, target, args.module)
            finally:
                try:
                    db_export.close()
                except Exception:
                    _logger.debug("Error closing A2L database.", exc_info=True)
    else:
        ifn = Path(args.ifn)
        force = args.force_overwrite
        if not force:
            _, db_fn = path_components(in_memory=False, file_name=ifn, local=args.local)
            if db_fn.exists():
                force = Confirm.ask(f"[yellow]Database [bold]{db_fn}[/bold] already exists. Overwrite?[/yellow]")
                if not force:
                    sys.exit(0)
        try:
            session = import_a2l(
                ifn,
                encoding=args.encoding,
                loglevel=args.loglevel,
                local=args.local,
                progress_bar=not args.no_progress_bar,
                force_overwrite=force,
            )
            session.close()
        except OSError as exc:
            _console.print(Panel(str(exc), title="[bold red]Import failed[/bold red]", border_style="red"))
            sys.exit(1)
        except Exception as exc:
            _console.print(
                Panel(
                    f"[red]{exc}[/red]\n\n[dim]{traceback.format_exc()}[/dim]",
                    title="[bold red]Import failed[/bold red]",
                    border_style="red",
                )
            )
            sys.exit(1)


if __name__ == "__main__":
    main()
