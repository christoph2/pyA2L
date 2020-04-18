#!/usr/bin/env python
# -*- coding: latin-1 -*-

"""These test-cases are based on the examples from ASAM MCD-2MC Version 1.6 specification.
"""

import pytest

from pya2l.aml_listener import (
        ParserWrapper, AMLListener, map_predefined_type, AMLPredefinedTypes
    )


def test_type_mapping():
    assert map_predefined_type('char') == AMLPredefinedTypes.PDT_CHAR
    assert map_predefined_type('int') == AMLPredefinedTypes.PDT_INT
    assert map_predefined_type('long') == AMLPredefinedTypes.PDT_LONG
    assert map_predefined_type('uchar') == AMLPredefinedTypes.PDT_UCHAR
    assert map_predefined_type('uint') == AMLPredefinedTypes.PDT_UINT
    assert map_predefined_type('ulong') == AMLPredefinedTypes.PDT_ULONG
    assert map_predefined_type('double') == AMLPredefinedTypes.PDT_DOUBLE
    assert map_predefined_type('float') == AMLPredefinedTypes.PDT_FLOAT

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

def test_enum_without_constants():
    parser = ParserWrapper('aml', 'enum_type_name', AMLListener, useDatabase = False)
    DATA = """enum {
        "PARITY_NONE",
        "PARITY_ODD",
        "PARITY_EVEN"
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
    assert en0.tag == "PARITY_NONE"
    assert en0.constant == 0
    assert en1.tag == "PARITY_ODD"
    assert en1.constant == 1
    assert en2.tag == "PARITY_EVEN"
    assert en2.constant == 2

def test_enum_one_constant():
    parser = ParserWrapper('aml', 'enum_type_name', AMLListener, useDatabase = False)
    DATA = """enum {
        "NO_CHECKSUM" = 10,
        "CHECKSUM_BYTE",
        "CHECKSUM_WORD"
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
    assert en0.tag == "NO_CHECKSUM"
    assert en0.constant == 10
    assert en1.tag == "CHECKSUM_BYTE"
    assert en1.constant == 11
    assert en2.tag == "CHECKSUM_WORD"
    assert en2.constant == 12

@pytest.mark.skip
def test_enum_unsteady_constants():
    parser = ParserWrapper('aml', 'enum_type_name', AMLListener, useDatabase = False)
    DATA = """enum {
      "UNIT_1NS" = 0,
      "UNIT_10NS" = 1,
      "UNIT_100NS",
      "UNIT_1US" = 30,
      "UNIT_10US" = 4,
      "UNIT_100US" = 5,
      "UNIT_1MS" = 6,
      "UNIT_10MS" = 7,
      "UNIT_100MS" = 8,
      "UNIT_1S" = 9
    };"""
    res = parser.parseFromString(DATA)
    enums = res.enum_types
    assert len(enums) == 1
    enum = enums[0]
    assert enum.name is None
    assert len(enum.enumerators) == 10

def test_complex_struct():
    parser = ParserWrapper('aml', 'struct_type_name', AMLListener, useDatabase = False)
    DATA = """struct {
        char[101];  /* EVENT_CHANNEL_NAME       */
        char[9];    /* EVENT_CHANNEL_SHORT_NAME */
        uint;       /* EVENT_CHANNEL_NUMBER     */
        enum {
          "DAQ" = 1,
          "STIM" = 2,
          "DAQ_STIM" = 3
        };
        uchar;  /* MAX_DAQ_LIST */
        uchar;  /* TIME_CYCLE   */
        uchar;  /* TIME_UNIT    */
        uchar;  /* PRIORITY     */
    };"""
    res = parser.parseFromString(DATA)
    structs = res.struct_types
    assert len(structs) == 1
    struct = structs[0]
    assert struct.name is None
    members = struct.members
    assert len(members) == 8
    m0 = members[0]
    tn = m0.value.type_name
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_CHAR
    assert tn.tag is None
    assert tn.name is None
    assert m0.value.array_specifier == [101]
    assert m0.multiple == False
    m1 = members[1]
    tn = m1.value.type_name
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_CHAR
    assert tn.tag is None
    assert tn.name is None
    assert m1.value.array_specifier == [9]
    assert m1.multiple == False
    m2 = members[2]
    tn = m2.value.type_name
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_UINT
    assert tn.tag is None
    assert tn.name is None
    assert m2.value.array_specifier == []
    assert m2.multiple == False
    m3 = members[3]
    tn = m3.value.type_name
    assert tn.tag is None
    assert tn.name is None
    enum = tn.type_
    assert enum.name is None
    enumerators = enum.enumerators
    assert len(enumerators) == 3
    en0 = enumerators[0]
    assert en0.tag == "DAQ"
    assert en0.constant == 1
    en1 = enumerators[1]
    assert en1.tag == "STIM"
    assert en1.constant == 2
    en2 = enumerators[2]
    assert en2.tag == "DAQ_STIM"
    assert en2.constant == 3
    m4 = members[4]
    assert m4.multiple == False
    tn = m4.value.type_name
    assert tn.tag is None
    assert tn.name is None
    pdt = tn.type_
    assert pdt.type_ == AMLPredefinedTypes.PDT_UCHAR
    m5 = members[5]
    assert m5.multiple == False
    tn = m5.value.type_name
    assert tn.tag is None
    assert tn.name is None
    pdt = tn.type_
    assert pdt.type_ == AMLPredefinedTypes.PDT_UCHAR
    m6 = members[6]
    assert m6.multiple == False
    tn = m6.value.type_name
    assert tn.tag is None
    assert tn.name is None
    pdt = tn.type_
    assert pdt.type_ == AMLPredefinedTypes.PDT_UCHAR
    m7 = members[7]
    assert m7.multiple == False
    tn = m7.value.type_name
    assert tn.tag is None
    assert tn.name is None
    pdt = tn.type_
    assert pdt.type_ == AMLPredefinedTypes.PDT_UCHAR

def test_basic_tagged_struct():
    parser = ParserWrapper('aml', 'taggedstruct_type_name', AMLListener, useDatabase = False)
    DATA = """taggedstruct test {
        "SLAVE" ;
        "MASTER" struct {
            uchar;  /* MAX_BS_PGM */
            uchar;  /* MIN_ST_PGM */
        };
    };"""
    res = parser.parseFromString(DATA)
    tagged_structs = res.tagged_struct_types
    assert len(tagged_structs) == 1
    tagged_struct = tagged_structs[0]
    assert tagged_struct.name == "test"
    members = tagged_struct.members
    assert len(members) == 2
    m0 = members[0]
    assert m0.block_definition is None
    assert m0.multiple == False
    tsd = m0.taggedstruct_definition
    assert tsd.tag == "SLAVE"
    assert tsd.multiple == False
    assert tsd.member is None
    m1 = members[1]
    assert m1.block_definition is None
    tsd = m1.taggedstruct_definition
    assert tsd.tag == "MASTER"
    assert tsd.multiple == False
    member = tsd.member
    tn = member.type_name
    assert tn.tag is None
    assert tn.name is None
    struct = tn.type_
    assert struct.name is None
    members = struct.members
    assert len(members) == 2
    m0 = members[0]
    assert m0.multiple == False
    tn = m0.value.type_name
    assert tn.tag is None
    assert tn.name is None
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_UCHAR
    m1 = members[1]
    assert m1.multiple == False
    tn = m1.value.type_name
    assert tn.tag is None
    assert tn.name is None
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_UCHAR

def test_basic_tagged_union():
    parser = ParserWrapper('aml', 'taggedunion_type_name', AMLListener, useDatabase = False)
    DATA = """
    taggedunion Daq_Event {
        "FIXED_EVENT_LIST" taggedstruct {
            ("EVENT" uint)*;
        };
        "VARIABLE" taggedstruct {
            block "AVAILABLE_EVENT_LIST" taggedstruct {
                ("EVENT" uint)*;
            };
            block "DEFAULT_EVENT_LIST" taggedstruct {
                ("EVENT" uint)*;
            };
        };
    };
    """
    res = parser.parseFromString(DATA)
    tagged_unions = res.tagged_union_types
    assert len(tagged_unions) == 1
    tagged_union = tagged_unions[0]
    assert tagged_union.name == "Daq_Event"
    members = tagged_union.members
    assert len(members) == 2
    m0 = members[0]
    assert m0.tag == "FIXED_EVENT_LIST"
    assert m0.block_definition is None
    mem = m0.member
    tn = mem.type_name.type_
    assert tn.name is None
    assert len(tn.members) == 1
    mem = tn.members[0]
    assert mem.multiple == True
    assert mem.block_definition is None
    td = mem.taggedstruct_definition
    assert td.tag == "EVENT"
    assert td.multiple == False
    tn = td.member.type_name
    assert tn.tag is None
    assert tn.name is None
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_UINT
    m1 = members[1]
    assert m1.tag == "VARIABLE"
    member = m1.member
    tn = member.type_name
    assert tn.tag is None
    assert tn.name is None
    tp = tn.type_
    assert tp.name is None
    members = tp.members
    assert len(members) == 2
    m0 = members[0]
    assert m0.multiple == False
    assert m0.taggedstruct_definition is None
    bd = m0.block_definition
    assert bd.tag == "AVAILABLE_EVENT_LIST"
    assert bd.member is None
    tn = bd.type_name
    assert tn.tag is None
    assert tn.name is None
    tst = tn.type_
    assert tst.name is None
    ms = tst.members
    assert len(ms) == 1
    m = ms[0]
    assert m.block_definition is None
    assert m.multiple == True
    tsd = m.taggedstruct_definition
    assert tsd.multiple == False
    assert tsd.tag == "EVENT"
    tn = tsd.member.type_name
    assert tn.tag is None
    assert tn.name is None
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_UINT
    m1 = members[1]
    assert m1.multiple == False
    assert m1.taggedstruct_definition is None
    bd = m1.block_definition
    assert bd.tag == "DEFAULT_EVENT_LIST"
    assert bd.member is None
    tn = bd.type_name
    assert tn.tag is None
    assert tn.name is None
    tst = tn.type_
    assert tst.name is None
    ms = tst.members
    assert len(ms) == 1
    m = ms[0]
    assert m.block_definition is None
    assert m.multiple == True
    tsd = m.taggedstruct_definition
    assert tsd.multiple == False
    assert tsd.tag == "EVENT"
    tn = tsd.member.type_name
    assert tn.tag is None
    assert tn.name is None
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_UINT


def test_basic_block_definition():
    parser = ParserWrapper('aml', 'block_definition', AMLListener, useDatabase = False)
    DATA = """
    block "STIM" struct {
        enum {
          "GRANULARITY_ODT_ENTRY_SIZE_STIM_BYTE" = 1,
          "GRANULARITY_ODT_ENTRY_SIZE_STIM_WORD" = 2,
          "GRANULARITY_ODT_ENTRY_SIZE_STIM_DWORD" = 4,
          "GRANULARITY_ODT_ENTRY_SIZE_STIM_DLONG" = 8
        };
        uchar;  /* MAX_ODT_ENTRY_SIZE_STIM */
        taggedstruct {
          "BIT_STIM_SUPPORTED" ;
        };
    };"""
    res = parser.parseFromString(DATA)
    block_definitions = res.block_definitions
    assert len(block_definitions) == 1
    bd = block_definitions[0]
    assert bd.tag == "STIM"
    assert bd.member is None
    tn = bd.type_name
    assert tn.tag is None
    assert tn.name is None
    tp = bd.type_name
    assert tp.tag is None
    assert tp.name is None
    st = tp.type_
    assert st.name is None
    members = st.members
    assert len(members) == 3
    m0 = members[0].value
    tn = m0.type_name
    assert tn.tag is None
    assert tn.name is None
    enum = tn.type_
    assert enum.name is None
    enumerators = enum.enumerators
    assert len(enumerators) == 4
    en0 = enumerators[0]
    assert en0.tag == "GRANULARITY_ODT_ENTRY_SIZE_STIM_BYTE"
    assert en0.constant == 1
    en1 = enumerators[1]
    assert en1.tag == "GRANULARITY_ODT_ENTRY_SIZE_STIM_WORD"
    assert en1.constant == 2
    en2 = enumerators[2]
    assert en2.tag == "GRANULARITY_ODT_ENTRY_SIZE_STIM_DWORD"
    assert en2.constant == 4
    en3 = enumerators[3]
    assert en3.tag == "GRANULARITY_ODT_ENTRY_SIZE_STIM_DLONG"
    assert en3.constant == 8
    m1 = members[1].value
    tn = m1.type_name
    assert tn.tag is None
    assert tn.name is None
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_UCHAR
    m2 = members[2].value
    tn = m2.type_name
    assert tn.tag is None
    assert tn.name is None
    tp = tn.type_
    assert tp.name is None
    members = tp.members
    assert len(members) == 1
    mem = members[0]
    assert mem.block_definition is None
    assert mem.multiple == False
    tsd = mem.taggedstruct_definition
    assert tsd.tag == "BIT_STIM_SUPPORTED"
    assert tsd.member is None
    assert tsd.multiple == False
