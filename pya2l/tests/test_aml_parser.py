#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""These test-cases are based on the examples from ASAM MCD-2MC Version 1.6 specification.
"""

import pytest

from pya2l.aml_listener import ParserWrapper, AMLListener

def test_enum_without_tag():
    parser = ParserWrapper('aml', 'enum_type_name', AMLListener, useDatabase = False)
    DATA = """enum {
      "ADDRESS_GRANULARITY_BYTE" = 1,
      "ADDRESS_GRANULARITY_WORD" = 2,
      "ADDRESS_GRANULARITY_DWORD" = 4
    };"""
    res = parser.parseFromString(DATA)
    enums = res.enum_types
    assert len(enums) == 1
    enum = enums[0]
    assert enum.name is None
    assert len(enum.enumerators) == 3
    en0 = enum.enumerators[0]
    en1 = enum.enumerators[1]
    en2 = enum.enumerators[2]
    assert en0.tag == "ADDRESS_GRANULARITY_BYTE"
    assert en0.constant == 1
    assert en1.tag == "ADDRESS_GRANULARITY_WORD"
    assert en1.constant == 2
    assert en2.tag == "ADDRESS_GRANULARITY_DWORD"
    assert en2.constant == 4

def test_enum_with_tag():
    parser = ParserWrapper('aml', 'enum_type_name', AMLListener, useDatabase = False)
    DATA = """enum checksum {
          "XCP_ADD_11" = 1,
          "XCP_ADD_12" = 2,
          "XCP_ADD_14" = 3,
          "XCP_ADD_22" = 4,
          "XCP_ADD_24" = 5,
          "XCP_ADD_44" = 6,
          "XCP_CRC_16" = 7,
          "XCP_CRC_16_CITT" = 8,
          "XCP_CRC_32" = 9,
          "XCP_USER_DEFINED" = 255
    };"""
    res = parser.parseFromString(DATA)
    enums = res.enum_types
    assert len(enums) == 1
    enum = enums[0]
    assert enum.name == "checksum"
    assert len(enum.enumerators) == 10
    en0 = enum.enumerators[0]
    en1 = enum.enumerators[1]
    en2 = enum.enumerators[2]
    en3 = enum.enumerators[3]
    en4 = enum.enumerators[4]
    en5 = enum.enumerators[5]
    en6 = enum.enumerators[6]
    en7 = enum.enumerators[7]
    en8 = enum.enumerators[8]
    en9 = enum.enumerators[9]
    assert en0.tag == "XCP_ADD_11"
    assert en0.constant == 1
    assert en1.tag == "XCP_ADD_12"
    assert en1.constant == 2
    assert en2.tag == "XCP_ADD_14"
    assert en2.constant == 3
    assert en3.tag == "XCP_ADD_22"
    assert en3.constant == 4
    assert en4.tag == "XCP_ADD_24"
    assert en4.constant == 5
    assert en5.tag == "XCP_ADD_44"
    assert en5.constant == 6
    assert en6.tag == "XCP_CRC_16"
    assert en6.constant == 7
    assert en7.tag == "XCP_CRC_16_CITT"
    assert en7.constant == 8
    assert en8.tag == "XCP_CRC_32"
    assert en8.constant == 9
    assert en9.tag == "XCP_USER_DEFINED"
    assert en9.constant == 255
