#!/usr/bin/env python
# -*- coding: utf-8 -*-

__copyright__="""
    pySART - Simplified AUTOSAR-Toolkit for Python.

   (C) 2009-2016 by Christoph Schueler <github.com/Christoph2,
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

from collections import defaultdict
from pprint import pprint
from operator import attrgetter, itemgetter
import re

from pya2l import templates
import pya2l.classes as classes

"""
'char'
'int'
'long'
'uchar'
'uint'
'ulong'
'double'
'float'
"""

"""
taggedstruct {
    "TIMESTAMP_FIXED" ;
};
"""

TYPE_NAME = re.compile(r"^<class\s'pya2l\.classes\.(?P<klass>.*?)(?:Type)?'>$", re.DOTALL)

HEADER = """
/begin A2ML


    enum datatype {
        "UBYTE"         = 0,
        "SBYTE"         = 1,
        "UWORD""        = 2,
        "SWORD"         = 3,
        "ULONG"         = 4,
        "SLONG"         = 5,
        "A_UINT64"      = 6,
        "A_INT64"       = 7,
        "FLOAT32_IEEE"  = 8,
        "FLOAT64_IEEE"  = 9
    };

    enum datasize {
        "BYTE"          = 0,
        "WORD"          = 1,
        "LONG"          = 2
    };

    enum addrtype {
        "PBYTE"         = 0,
        "PWORD"         = 1,
        "PLONG"         = 2,
        "DIRECT"        = 3
    };

    enum byteorder {
        "LITTLE_ENDIAN" = 0,
        "BIG_ENDIAN"    = 1,
        "MSB_LAST"      = 2,
        "MSB_FIRST"     = 3
    };

    enum indexorder {
        "INDEX_INCR"    = 0,
        "INDEX_DECR"    = 1
    };


"""

FOOTER = """

/end A2ML"""


##  (block "ADDRESS_MAPPING" struct {
##    ulong;
##    ulong;
##    ulong;
##  })*;

STRUCTURE = """<%
import pya2l.classes as classes

def camelCase(name):
    splitty = [n.lower() for n in name.split('_')]
    result = []
    result.append(splitty[0])
    if len(splitty) > 1:
        for part in splitty[1 : ]:
            xxx = "{0}{1}".format(part[0].upper(), part[1: ])
            result.append(xxx)
    return ''.join(result)

def mapType(attr):
    TYPES = {
        classes.Uint:   "uint",
        classes.Int:    "int",
        classes.Ulong:  "ulong",
        classes.Long:   "long",
        classes.Float:  "float",
        classes.String: "char[256]",
        #classes.Enum:   "",
        classes.Ident:  "char[1025]",
    }
    if attr in TYPES:
        mappedType = TYPES[attr]
        return mappedType
    else:
        return None

%>
${"(" if item.multiple else ""}${"block " if item.block else ""}"${tag}" struct ${camelCase(tag)} {
%for attr in item.attrs:
    %if 'Enum' in str(attr[0]):
    enum {  /* ${attr[1]} */
    %for idx, en in enumerate(attr[2]):
        "${en}" = ${idx},
    %endfor
    };
    %else:
    ${mapType(attr[0])}; /* ${attr[1]} */
    %endif
%endfor
%for child in item.children:
${utils.structure(child, utils, level + 1)}
%endfor
${"})*;" if item.multiple else ");"}
"""

class AMLBuilder(object):

    def __init__(self):
        self.values = [c for c in classes.KEYWORD_MAP.values()]
        self.positions = {}
        self.referencedBy = defaultdict(set)
        for idx, val in enumerate(self.values):
            self.positions[idx] = val
        self.inv()

    def inv(self):
        self.positions_inv = {v:k for k, v in self.positions.items()}

    def swap(self, l, r):

        tmp = self.positions[self.positions_inv[l]]
        self.positions[self.positions_inv[l]] = self.positions[self.positions_inv[r]]
        self.positions[self.positions_inv[r]] = tmp
        self.inv()

    def run(self):
        iterations = 0
        swaps = None
        while swaps != 0:
            swaps = 0
            for k, v in self.positions.items():
                for c in v.children:
                    child = classes.KEYWORD_MAP[c]
                    self.referencedBy[child].add(v)
                    childPos = self.positions_inv[child]
                    elemPos = self.positions_inv[v]
                    if elemPos < childPos:
                        self.swap(v, child)
                        swaps += 1
            iterations += 1

ab = AMLBuilder()
ab.run()
toFactorOut = sorted(list(x for x in ab.referencedBy.items() if len(x[1]) > 1), key = lambda o: repr(o))
restOfUs = list(x for x in ab.referencedBy.items() if len(x[1]) <= 1)
toFactorOutClasses = {k for k, v in toFactorOut}
print(toFactorOutClasses)

toProcess = [x[1] for x in ab.positions.items() if x[1] not in toFactorOutClasses]

def structure(name, utils, level = 1):
    item = classes.KEYWORD_MAP[name]
    namespace = {"item": item, "level": level, "tag": name, "utils": utils}
    return templates.doTemplateFromText(STRUCTURE, namespace, level * 4)


class Dummy(object): pass

utils = Dummy()
utils.structure = structure

for item in [x[0] for x in toFactorOut]:
    match = TYPE_NAME.match(str(item))
    tag = match.group(1)
    print(structure(tag, utils, 1))
    print("-" * 60)

print("/" * 80)

for child in classes.RootElement.children:
    print(structure(child, utils, 1))

print(templates.doTemplateFromText(FOOTER, {}, 0))

