#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Do preprocessing of files:
- Removal of comments.
- '/include' mechanism.
"""

__copyright__ = """
   pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2010-2020 by Christoph Schueler <cpu12.gems.googlemail.com>

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


import re
import string

CPP_COMMENT = re.compile(r"""(?://)(?P<cmt>.*)""", re.DOTALL | re.UNICODE | re.VERBOSE)
MULTILINE_START = re.compile(
    r"""(?:/\*)(?P<cmt>[^*]*)(?P<close>\*/)?""", re.DOTALL | re.UNICODE | re.VERBOSE
)
MULTILINE_END = re.compile(
    r"""(?:\*/)(?P<text>.*)""", re.DOTALL | re.UNICODE | re.VERBOSE
)

PRINTABLES = string.printable[: string.printable.find(" ")]
TR_PRINTABLES = str.maketrans(PRINTABLES, " " * len(PRINTABLES))


def blank_out(text, span):
    """Cut out section and replace with spaces.

    Parameters
    ----------
    text: str

    span: 2-tuple, range to blank out.
        - Element 0 => start
        - Element 1 => end

    Returns
    -------
    str
    """
    start, end = span

    header = text[0:start]
    section = text[start:end]
    section = section.translate(TR_PRINTABLES)
    footer = text[end:]
    text = header + section + footer
    return text


class Preprocessor:
    """"""

    def __init__(self):
        pass

    def __call__(self, lines):
        result = []
        multiline = False
        for num, line in enumerate(lines):
            line = line.rstrip("\n")
            if multiline:
                match = MULTILINE_END.search(line)
                if match:
                    rl = line[match.end() :]
                    result.append(match.group("text"))
                    multiline = False
                    continue
                else:
                    result.append("")
                    continue
            cpp_match = CPP_COMMENT.search(line)
            c_match = MULTILINE_START.search(line)
            use_c_match = use_cpp_match = False
            if cpp_match and c_match:
                if cpp_match.start() < c_match.start():
                    use_cpp_match = True
                else:
                    use_c_match = True
            elif c_match:
                use_c_match = True
            elif cpp_match:
                use_cpp_match = True
            if use_cpp_match:
                rl = blank_out(line, cpp_match.span())
                result.append(rl)
            elif use_c_match:
                multiline = c_match.group("close") is None
                rl = blank_out(line, c_match.span())
                result.append(rl)
            else:
                result.append(line)
        return "\n".join(result)

    def uncomment(self):
        pass

    def escape_quotes(self, line):
        """"""
        pass
