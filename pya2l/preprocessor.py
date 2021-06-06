#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Do preprocessing of files:

    - Removal of comments.
    - '/include' mechanism.
    - Extract AML and IF_DATA sections.
"""

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


from bisect import bisect
from collections import defaultdict, namedtuple
from logging import getLogger
from os import getenv
from os.path import pathsep
from pathlib import Path
import re
import string


CPP_COMMENT = re.compile(r'(?://)(?P<cmt>.*)$', re.DOTALL | re.UNICODE | re.VERBOSE)
MULTILINE_START = re.compile(r'(?:/\*)(?P<cmt>.*?)', re.DOTALL | re.UNICODE | re.VERBOSE)
MULTILINE_END = re.compile(r'(?:\*/)(?P<text>.*)', re.DOTALL | re.UNICODE | re.VERBOSE)
INCLUDE = re.compile(r'^\s*/include\s+"(?P<phile>[^"]*)"', re.DOTALL | re.UNICODE | re.VERBOSE)

AML_START = re.compile(r'^\s*/begin\s+A[23]ML(?P<section>.*?)', re.VERBOSE | re.DOTALL | re.MULTILINE)
AML_END = re.compile(r'^\s*/end\s+A[23]ML', re.VERBOSE | re.DOTALL | re.MULTILINE)

IF_DATA_START = re.compile(r'\s*/begin\s+IF_DATA(?P<section>.*?)$', re.VERBOSE | re.DOTALL | re.MULTILINE)
IF_DATA_END = re.compile(r'^\s*/end\s+IF_DATA', re.VERBOSE | re.DOTALL | re.MULTILINE)

PreprocessorResult = namedtuple("PreprocessorResult", "a2l_data aml_section if_data_sections line_map")
IfDataSection = namedtuple("IfDataSection", "start_line end_line data")


class LineMap:
    """Preprocessor creates a single file from included files.
    `LineMap` is a means to associate to original file names and line numbers.
    """
    def __init__(self, line_map):
        self.line_map = line_map
        offsets = dict.fromkeys(line_map, 1)
        items = {}
        self.start_offsets = []
        for k, v in line_map.items():
            for ent in v:
                items[ent] = k
        items = sorted(items.items(), key = lambda v: v[0][0])
        for idx in range(len(items)):
            tp, name = items[idx]
            start, end = tp
            self.start_offsets.append(start)
            length = end - start
            offset = offsets[name]
            entry = (start, end, offset, length + offset)
            offsets[name] = length + offset + 1
            items[idx] = (entry, name)
        self.items = items
        self.last_line_no = end

    def lookup(self, line_no):
        """
        Parameter
        ---------
        line_no: int

        Returns
        -------
            (file_name, original_file_number)
        """
        if not 1 <= line_no <= self.last_line_no:
            raise ValueError("Line number [{}] out of range.".format(line_no))
        idx = bisect(self.start_offsets, line_no) - 1
        (abs_start, abs_end, rel_start, rel_end), name = self.items[idx]
        offset = abs_start - rel_start
        return (name, line_no - offset + 1)

    def __str__(self):
        result = ["LineMap("]
        for k, v in self.line_map.items():
            result.append("    '{}': {}".format(k, v))
        result.append(")")
        return "\n".join(result)

    __repr__ = __str__


def blank_out(text, span):
    """Cut out section of text and replace it with a single space.

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
    if end == -1:
        result = text[ : start]
    else:
        result = text[ : start] + text[end : ]
    return result.rstrip()


class Preprocessor:
    """"""

    def __init__(self, log_level = "WARN"):
        self.logger = getLogger(self.__class__.__name__)
        self.logger.setLevel(log_level)
        include_paths = getenv("ASAP_INCLUDE", "").split(pathsep)
        self.include_paths = [Path(p) for p in include_paths] if include_paths != [''] else []

    def process(self, file_name, encoding = "latin-1"):
        """
        Parameters
        ----------

        Returns
        -------
        """
        self.line_map = defaultdict(list)
        self.absolute_file_number = 0
        self.local_file_numbers = []
        self.aml_section = None
        self.if_datas = []
        data = self._process_file(file_name, join_lines = True, encoding = encoding)
        return PreprocessorResult(self._process_aml(data), self.aml_section, self.if_data_sections, LineMap(self.line_map))

    def _process_file(self, file_name, join_lines = True, encoding = "latin-1"):
        result = []
        start_line_number = self.absolute_file_number + 1
        multiline = False
        pth_obj = Path(file_name)
        f_obj = pth_obj.open("rt", encoding = encoding)
        abs_file_name = str(pth_obj.absolute())
        if abs_file_name in self.line_map:
            raise RuntimeError("Circular dependency to include file '{}'.".format(abs_file_name))
        self.logger.debug("Processing file '{}'.".format(abs_file_name))
        for num, line in enumerate(f_obj, 1):
            self.absolute_file_number += 1
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
            incl = None
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
                rl = line[ : cpp_match.start()]
                incl = INCLUDE.match(line)
                if not incl:
                    result.append(rl)
            elif use_c_match:
                end_match = MULTILINE_END.search(line)
                multiline = False if end_match else True
                if end_match:
                    rl = blank_out(line, (c_match.start(), end_match.end(), ))
                else:
                    rl = blank_out(line, (c_match.start(), -1, ))
                incl = INCLUDE.match(line)
                if not incl:
                    result.append(rl)
            else:
                incl = INCLUDE.match(line)
                if not incl:
                    result.append(line)
            if incl:
                include_file_name = incl.group("phile")
                where = self.locate_file(include_file_name, pth_obj.parent)
                if not where:
                    raise FileNotFoundError("No such file or directory: '{}'".format(include_file_name))
                else:
                    mapped_file_name = self.shorten_path(abs_file_name)
                    self.line_map[mapped_file_name].append((start_line_number, self.absolute_file_number, ))
                    self.logger.debug("Including file '{}'.".format(where))
                    res = self._process_file(where, join_lines = False)
                    result.extend(res)
                    start_line_number = self.absolute_file_number + 1
        mapped_file_name = self.shorten_path(abs_file_name)
        self.line_map[mapped_file_name].append((start_line_number, self.absolute_file_number, ))
        if join_lines:
            return "\n".join(result)
        else:
            return result

    def _process_aml(self, data):
        """Extract A2ML and IF_DATA sections.
        """
        result = []
        sections = []
        aml_section = []
        if_data_section = []
        in_aml = False
        in_if_data = False
        if_data_start = if_data_end = None
        for line_num, line in enumerate(data.splitlines(), 1):
            if not in_aml:
                match = AML_START.match(line)
                if match:
                    in_aml = True
                    aml_section.append("/begin A2ML")
                else:
                    if not in_if_data:
                        #match = IF_DATA_START.match(line)
                        match = IF_DATA_START.search(line)
                        if match:
                            in_if_data = True
                            if_data_start = line_num

                            start_pos, end_pos =  match.span()

                            ids = "/begin IF_DATA {}".format(match.group("section"))

                            #print("MATCH: '{}' '{}'".format(line[ : start_pos], ids))

                            if_data_section.append(ids)
                            #result.append(ids)
                            #result.append(line[start_pos : end_pos])
                            result.append(line[ : end_pos])
                        else:
                            result.append(line)
                    else:
                        if_data_section.append(line.strip())
                        match = IF_DATA_END.match(line)
                        if match:
                            if_data_end = line_num
                            section = IfDataSection(if_data_start - 1, if_data_end - 1, '\n'.join(if_data_section))
                            #print(section, end = "\n\n")    ###########################
                            sections.append(section)
                            in_if_data = False
                            if_data_section = []
                            result.append("/end IF_DATA")
                        else:
                            result.append("")
            else:
                match = AML_END.match(line)
                if match:
                    aml_section.append("/end A2ML ")
                    line = ""
                    in_aml = False
                else:
                    aml_section.append(line)
                result.append("")
        self.aml_section = "\n".join(aml_section)
        self.if_data_sections = sections
        #print("\n".join(result))    ###########################
        return "\n".join(result)

    def shorten_path(pth, file_name):
        """Remove path component if file is located in current working directory."""
        if Path(file_name).parent == Path.cwd().absolute():
            mapped_file_name = Path(file_name).parts[-1]
        else:
            mapped_file_name = file_name
        return mapped_file_name

    def escape_quotes(self, line):
        """"""
        pass

    def locate_file(self, file_name, additional_path):
        """
        Parameters
        ----------
        file_name: str

        additional_path: str

        Returns
        -------

        Note
        ----
        Lookup order is as follows:

        - Current working directory.
        - Directory containing the currently processed file.
        - Directories from environment variable `ASAP_INCLUDE`.
        """
        for pth in [Path.cwd(), additional_path] + self.include_paths:
            tfn = (pth / file_name)
            if tfn.exists():
                return tfn
