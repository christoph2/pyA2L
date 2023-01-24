#!/usr/bin/env python
# -*- coding: latin-1 -*-
import pytest

from pya2l.aml.classes import AMLPredefinedTypes
from pya2l.aml.classes import map_predefined_type
from pya2l.aml.listener import AMLListener
from pya2l.parserlib import ParserWrapper


def test_type_mapping():
    assert map_predefined_type("char") == AMLPredefinedTypes.PDT_CHAR
    assert map_predefined_type("int") == AMLPredefinedTypes.PDT_INT
    assert map_predefined_type("long") == AMLPredefinedTypes.PDT_LONG
    assert map_predefined_type("uchar") == AMLPredefinedTypes.PDT_UCHAR
    assert map_predefined_type("uint") == AMLPredefinedTypes.PDT_UINT
    assert map_predefined_type("ulong") == AMLPredefinedTypes.PDT_ULONG
    assert map_predefined_type("double") == AMLPredefinedTypes.PDT_DOUBLE
    assert map_predefined_type("float") == AMLPredefinedTypes.PDT_FLOAT


def test_enum_without_tag():
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    DATA = """
    /begin A2ML
    enum {
      "ADDRESS_GRANULARITY_BYTE" = 1,
      "ADDRESS_GRANULARITY_WORD" = 2,
      "ADDRESS_GRANULARITY_DWORD" = 4
    };
    /end A2ML
    """
    res = parser.parseFromString(DATA)
    enum = res.listener_result.declarations[0].type_definition.type_name.type_
    assert enum.name is None
    enumerators = sorted(enum.enumerators.items(), key = lambda t: t[1])
    assert len(enumerators) == 3
    en0_t, en0_c = enumerators[0]
    en1_t, en1_c = enumerators[1]
    en2_t, en2_c = enumerators[2]
    assert en0_t == "ADDRESS_GRANULARITY_BYTE"
    assert en0_c == 1
    assert en1_t == "ADDRESS_GRANULARITY_WORD"
    assert en1_c == 2
    assert en2_t == "ADDRESS_GRANULARITY_DWORD"
    assert en2_c == 4


def test_enum_with_tag():
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    DATA = """
    /begin A2ML
    enum checksum {
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
    };
    /end A2ML
    """
    res = parser.parseFromString(DATA)
    enum = res.listener_result.declarations[0].type_definition.type_name.type_
    assert enum.name == "checksum"
    enumerators = sorted(enum.enumerators.items(), key = lambda t: t[1])
    assert len(enumerators) == 10
    en0_t, en0_c = enumerators[0]
    en1_t, en1_c = enumerators[1]
    en2_t, en2_c = enumerators[2]
    en3_t, en3_c = enumerators[3]
    en4_t, en4_c = enumerators[4]
    en5_t, en5_c = enumerators[5]
    en6_t, en6_c = enumerators[6]
    en7_t, en7_c = enumerators[7]
    en8_t, en8_c = enumerators[8]
    en9_t, en9_c = enumerators[9]
    assert en0_t == "XCP_ADD_11"
    assert en0_c == 1
    assert en1_t == "XCP_ADD_12"
    assert en1_c == 2
    assert en2_t == "XCP_ADD_14"
    assert en2_c == 3
    assert en3_t == "XCP_ADD_22"
    assert en3_c == 4
    assert en4_t == "XCP_ADD_24"
    assert en4_c == 5
    assert en5_t == "XCP_ADD_44"
    assert en5_c == 6
    assert en6_t == "XCP_CRC_16"
    assert en6_c == 7
    assert en7_t == "XCP_CRC_16_CITT"
    assert en7_c == 8
    assert en8_t == "XCP_CRC_32"
    assert en8_c == 9
    assert en9_t == "XCP_USER_DEFINED"
    assert en9_c == 255


def test_enum_without_constants():
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    DATA = """
    /begin A2ML
    enum {
        "PARITY_NONE",
        "PARITY_ODD",
        "PARITY_EVEN"
    };
    /end A2ML
    """
    res = parser.parseFromString(DATA)
    enum = res.listener_result.declarations[0].type_definition.type_name.type_
    assert enum.name is None
    enumerators = sorted(enum.enumerators.items(), key = lambda t: t[1])
    assert len(enumerators) == 3
    en0_t, en0_c = enumerators[0]
    en1_t, en1_c = enumerators[1]
    en2_t, en2_c = enumerators[2]
    assert en0_t == "PARITY_NONE"
    assert en0_c == 0
    assert en1_t == "PARITY_ODD"
    assert en1_c == 1
    assert en2_t == "PARITY_EVEN"
    assert en2_c == 2


def test_enum_one_constant():
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    DATA = """
    /begin A2ML
    enum {
        "NO_CHECKSUM" = 10,
        "CHECKSUM_BYTE",
        "CHECKSUM_WORD"
    };
    /end A2ML
    """
    res = parser.parseFromString(DATA)
    enum = res.listener_result.declarations[0].type_definition.type_name.type_
    enumerators = sorted(enum.enumerators.items(), key = lambda t: t[1])
    assert enum.name is None
    assert len(enumerators) == 3
    en0_t, en0_c = enumerators[0]
    en1_t, en1_c = enumerators[1]
    en2_t, en2_c = enumerators[2]
    assert en0_t == "NO_CHECKSUM"
    assert en0_c == 10
    assert en1_t == "CHECKSUM_BYTE"
    assert en1_c == 11
    assert en2_t == "CHECKSUM_WORD"
    assert en2_c == 12


def test_enum_unsteady_constants():
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    DATA = """
    /begin A2ML
    enum {
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
    };
    /end A2ML
    """
    res = parser.parseFromString(DATA)
    enum = res.listener_result.declarations[0].type_definition.type_name.type_
    assert enum.name is None
    enumerators = sorted(enum.enumerators.items(), key = lambda t: t[1])
    assert len(enumerators) == 10
    en0_t, en0_c = enumerators[0]
    en1_t, en1_c = enumerators[1]
    en2_t, en2_c = enumerators[2]
    en3_t, en3_c = enumerators[3]
    en4_t, en4_c = enumerators[4]
    en5_t, en5_c = enumerators[5]
    en6_t, en6_c = enumerators[6]
    en7_t, en7_c = enumerators[7]
    en8_t, en8_c = enumerators[8]
    en9_t, en9_c = enumerators[9]
    assert en0_t == "UNIT_1NS"
    assert en0_c == 0
    assert en1_t == "UNIT_10NS"
    assert en1_c == 1
    assert en2_t == "UNIT_100NS"
    assert en2_c == 2
    assert en3_t == "UNIT_10US"
    assert en3_c == 4
    assert en4_t == "UNIT_100US"
    assert en4_c == 5
    assert en5_t == "UNIT_1MS"
    assert en5_c == 6
    assert en6_t == "UNIT_10MS"
    assert en6_c == 7
    assert en7_t == "UNIT_100MS"
    assert en7_c == 8
    assert en8_t == "UNIT_1S"
    assert en8_c == 9
    assert en9_t == "UNIT_1US"
    assert en9_c == 30


def struct(structs):
    assert structs.name is None
    members = structs.members
    assert len(members) == 8
    m0 = members[0]
    tn = m0.value.type_name
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_CHAR
    assert tn.tag is None
    assert tn.name is None
    assert m0.value.array_specifier == [101]
    assert m0.multiple is False
    m1 = members[1]
    tn = m1.value.type_name
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_CHAR
    assert tn.tag is None
    assert tn.name is None
    assert m1.value.array_specifier == [9]
    assert m1.multiple is False
    m2 = members[2]
    tn = m2.value.type_name
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_UINT
    assert tn.tag is None
    assert tn.name is None
    assert m2.value.array_specifier == []
    assert m2.multiple is False
    m3 = members[3]
    tn = m3.value.type_name
    assert tn.tag is None
    assert tn.name is None
    enum = tn.type_
    assert enum.name is None
    enumerators = sorted(enum.enumerators.items(), key = lambda t: t[1])
    assert len(enumerators) == 3
    en0_t, en0_c = enumerators[0]
    assert en0_t == "DAQ"
    assert en0_c == 1
    en1_t, en1_c = enumerators[1]
    assert en1_t == "STIM"
    assert en1_c == 2
    en2_t, en2_c = enumerators[2]
    assert en2_t == "DAQ_STIM"
    assert en2_c == 3
    m4 = members[4]
    assert m4.multiple is False
    tn = m4.value.type_name
    assert tn.tag is None
    assert tn.name is None
    pdt = tn.type_
    assert pdt.type_ == AMLPredefinedTypes.PDT_UCHAR
    m5 = members[5]
    assert m5.multiple is False
    tn = m5.value.type_name
    assert tn.tag is None
    assert tn.name is None
    pdt = tn.type_
    assert pdt.type_ == AMLPredefinedTypes.PDT_UCHAR
    m6 = members[6]
    assert m6.multiple is False
    tn = m6.value.type_name
    assert tn.tag is None
    assert tn.name is None
    pdt = tn.type_
    assert pdt.type_ == AMLPredefinedTypes.PDT_UCHAR
    m7 = members[7]
    assert m7.multiple is False
    tn = m7.value.type_name
    assert tn.tag is None
    assert tn.name is None
    pdt = tn.type_
    assert pdt.type_ == AMLPredefinedTypes.PDT_UCHAR


def test_complex_struct():
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    DATA = """
    /begin A2ML
    struct {
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
    };
    /end A2ML
    """
    res = parser.parseFromString(DATA)
    structs = res.listener_result.declarations[0].type_definition.type_name.type_
    struct(structs)


def test_basic_tagged_struct():
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    DATA = """
    /begin A2ML
    taggedstruct test {
        "SLAVE" ;
        "MASTER" struct {
            uchar;  /* MAX_BS_PGM */
            uchar;  /* MIN_ST_PGM */
        };
    };
    /end A2ML
    """
    res = parser.parseFromString(DATA)
    tagged_struct = struct = res.listener_result.declarations[0].type_definition.type_name.type_
    assert tagged_struct.name == "test"
    members = tagged_struct.members
    assert len(members) == 2
    m0 = members[0]
    assert m0.block_definition is None
    assert m0.multiple is False
    tsd = m0.taggedstruct_definition
    assert tsd.tag == "SLAVE"
    assert tsd.multiple is False
    assert tsd.member is None
    m1 = members[1]
    assert m1.block_definition is None
    tsd = m1.taggedstruct_definition
    assert tsd.tag == "MASTER"
    assert tsd.multiple is False
    member = tsd.member
    tn = member.type_name
    assert tn.tag is None
    assert tn.name is None
    struct = tn.type_
    assert struct.name is None
    members = struct.members
    assert len(members) == 2
    m0 = members[0]
    assert m0.multiple is False
    tn = m0.value.type_name
    assert tn.tag is None
    assert tn.name is None
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_UCHAR
    m1 = members[1]
    assert m1.multiple is False
    tn = m1.value.type_name
    assert tn.tag is None
    assert tn.name is None
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_UCHAR


def test_basic_tagged_union():
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    DATA = """
    /begin A2ML
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
    /end A2ML
    """
    res = parser.parseFromString(DATA)
    tagged_union = res.listener_result.declarations[0].type_definition.type_name.type_
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
    assert mem.multiple
    assert mem.block_definition is None
    td = mem.taggedstruct_definition
    assert td.tag == "EVENT"
    assert td.multiple is False
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
    assert m0.multiple is False
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
    assert m.multiple
    tsd = m.taggedstruct_definition
    assert tsd.multiple is False
    assert tsd.tag == "EVENT"
    tn = tsd.member.type_name
    assert tn.tag is None
    assert tn.name is None
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_UINT
    m1 = members[1]
    assert m1.multiple is False
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
    assert m.multiple
    tsd = m.taggedstruct_definition
    assert tsd.multiple is False
    assert tsd.tag == "EVENT"
    tn = tsd.member.type_name
    assert tn.tag is None
    assert tn.name is None
    assert tn.type_.type_ == AMLPredefinedTypes.PDT_UINT


def block_def(block_definitions):
    bd = block_definitions
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
    enumerators = sorted(enum.enumerators.items(), key = lambda t: t[1])
    assert len(enumerators) == 4
    en0_t, en0_c = enumerators[0]
    assert en0_t == "GRANULARITY_ODT_ENTRY_SIZE_STIM_BYTE"
    assert en0_c == 1
    en1_t, en1_c  = enumerators[1]
    assert en1_t == "GRANULARITY_ODT_ENTRY_SIZE_STIM_WORD"
    assert en1_c == 2
    en2_t, en2_c = enumerators[2]
    assert en2_t == "GRANULARITY_ODT_ENTRY_SIZE_STIM_DWORD"
    assert en2_c == 4
    en3_t, en3_c = enumerators[3]
    assert en3_t == "GRANULARITY_ODT_ENTRY_SIZE_STIM_DLONG"
    assert en3_c == 8
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
    assert mem.multiple is False
    tsd = mem.taggedstruct_definition
    assert tsd.tag == "BIT_STIM_SUPPORTED"
    assert tsd.member is None
    assert tsd.multiple is False


def test_basic_block_definition():
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    DATA = """
    /begin A2ML
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
    };
    /end A2ML
    """
    res = parser.parseFromString(DATA)
    block_definition = res.listener_result.declarations[0].block_definition
    block_def(block_definition)


def test_struct_referrers():
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    DATA = """
    /begin A2ML
    struct FLX_Parameters {
        taggedunion {
            block "INITIAL_CMD_BUFFER" struct buffer;
        };
        taggedunion {
            block "INITIAL_RES_ERR_BUFFER" struct buffer;
        };
        taggedstruct {
            (block "POOL_BUFFER" struct buffer)*;
        };
    };
    /end A2ML
    """
    res = parser.parseFromString(DATA)
    struct_t = res.listener_result.declarations[0].type_definition.type_name.type_
    assert struct_t.name == "FLX_Parameters"
    members = struct_t.members
    assert len(members) == 3
    m0 = members[0]
    assert m0.multiple is False
    tn = m0.value.type_name
    assert tn.tag is None
    assert tn.name is None
    tp = tn.type_
    assert tp.name is None
    ms = tp.members
    assert len(ms) == 1
    m = ms[0]
    assert m.tag is None
    assert m.member is None
    bd = m.block_definition
    assert bd.tag == "INITIAL_CMD_BUFFER"
    tn = bd.type_name
    assert tn.tag is None
    assert tn.name is None
    assert tn.type_.identifier == "buffer"
    assert tn.type_.category == "StructType"
    assert bd.member is None
    assert bd.multiple == False
    m1 = members[1]
    assert m1.multiple is False
    tn = m1.value.type_name
    assert tn.tag is None
    assert tn.name is None
    tp = tn.type_
    assert tp.name is None
    ms = tp.members
    assert len(ms) == 1
    m = ms[0]
    assert m.tag is None
    assert m.member is None
    bd = m.block_definition
    assert bd.tag == "INITIAL_RES_ERR_BUFFER"
    tn = bd.type_name
    assert tn.tag is None
    assert tn.type_.identifier == "buffer"
    assert tn.type_.category == "StructType"
    assert bd.member is None
    assert bd.multiple == False
    m2 = members[2]
    assert m2.multiple is False
    tn = m2.value.type_name
    assert tn.tag is None
    assert tn.name is None
    tst = tn.type_
    assert tst.name is None
    members = tst.members
    assert len(members) == 1
    mem = members[0]
    assert mem.multiple
    assert mem.taggedstruct_definition is None
    bd = mem.block_definition
    assert bd.tag == "POOL_BUFFER"
    assert bd.member is None
    tn = bd.type_name
    assert tn.tag is None
    assert tn.type_.identifier == "buffer"
    assert tn.type_.category == "StructType"
    assert bd.member is None
    assert bd.multiple == False

def test_taggedstruct_referrers():
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    DATA = """
    /begin A2ML
        struct {
            taggedstruct Common_Parameters;  /* default parameters */
            taggedstruct bus_systems {
                block "XCP_ON_CAN" struct {
                    struct CAN_Parameters;  /* specific for CAN */
                    taggedstruct Common_Parameters;  /* overruling of default */
                };
                block "XCP_ON_SxI" struct {
                    struct SxI_Parameters;  /* specific for SxI */
                    taggedstruct Common_Parameters;  /* overruling of default */
                };
                block "XCP_ON_TCP_IP" struct {
                    struct TCP_IP_Parameters;  /* specific for TCP_IP */
                    taggedstruct Common_Parameters;  /* overruling of default */
                };
                block "XCP_ON_UDP_IP" struct {
                    struct UDP_Parameters;  /* specific for UDP */
                    taggedstruct Common_Parameters;  /* overruling of default */
                };
                block "XCP_ON_USB" struct {
                    struct USB_Parameters;  /* specific for USB      */
                    taggedstruct Common_Parameters;  /* overruling of default */
                };
                block "XCP_ON_FLX" struct {
                    struct FLX_Parameters;  /* specific for FlexRay  */
                    taggedstruct Common_Parameters;  /* overruling of default */
                };
            };
        };
    /end A2ML
    """
    res = parser.parseFromString(DATA)
    tagged_struct = res.listener_result.declarations[0].type_definition.type_name.type_
    members = tagged_struct.members
    mem = members[0]
    assert mem.multiple == False
    mem = mem.value.type_name
    assert mem.tag is None
    assert mem.name is None
    assert mem.type_.category == "TaggedStructType"
    assert mem.type_.identifier == "Common_Parameters"

    mem = members[1]
    assert mem.multiple == False
    mem = mem.value.type_name

    assert mem.name == "bus_systems"
    assert mem.type_.name == "bus_systems"
    members = mem.type_.members
    assert len(members) == 6

    m0 = members[0]
    assert m0.multiple is False
    assert m0.taggedstruct_definition is None
    bd = m0.block_definition
    assert bd.tag == "XCP_ON_CAN"
    assert bd.member is None
    tn = bd.type_name
    assert tn.tag is None
    assert tn.name is None
    tp = tn.type_
    assert tp.name is None
    ms = members

    assert len(ms) == 6
    m00 = ms[0]


def test_taggedunion_referrers():
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    DATA = """
    /begin A2ML
    taggedstruct Common_Parameters {
        block "PROTOCOL_LAYER" struct Protocol_Layer;
        block "SEGMENT" struct Segment;
        block "DAQ" struct Daq;
        block "PAG" struct Pag;
        block "PGM" struct Pgm;
        block "DAQ_EVENT" taggedunion Daq_Event;
    };
    /end A2ML
    """
    res = parser.parseFromString(DATA)
    tagged_struct = res.listener_result.declarations[0].type_definition.type_name.type_
    ts = tagged_struct
    assert ts.name == "Common_Parameters"
    members = ts.members
    assert len(members) == 6
    m0 = members[0]
    assert m0.multiple is False
    assert m0.taggedstruct_definition is None

    bd = m0.block_definition
    assert bd.member is None
    assert bd.tag == "PROTOCOL_LAYER"
    tn = bd.type_name
    assert tn.tag is None
    assert tn.type_.identifier == "Protocol_Layer"
    m1 = members[1]
    assert m1.multiple is False
    assert m1.taggedstruct_definition is None

    bd = m1.block_definition
    assert bd.member is None
    assert bd.tag == "SEGMENT"
    tn = bd.type_name
    assert tn.type_.identifier == "Segment"
    m2 = members[2]
    assert m2.multiple is False
    assert m2.taggedstruct_definition is None

    bd = m2.block_definition
    assert bd.member is None
    assert bd.tag == "DAQ"
    tn = bd.type_name
    assert tn.type_.identifier == "Daq"
    m3 = members[3]
    assert m3.multiple is False
    assert m3.taggedstruct_definition is None

    bd = m3.block_definition
    assert bd.member is None
    assert bd.tag == "PAG"
    tn = bd.type_name
    assert tn.type_.identifier == "Pag"
    m4 = members[4]
    assert m4.multiple is False
    assert m4.taggedstruct_definition is None

    bd = m4.block_definition
    assert bd.member is None
    assert bd.tag == "PGM"
    tn = bd.type_name
    assert tn.tag is None
    assert tn.type_.identifier == "Pgm"
    m5 = members[5]
    assert m5.multiple is False
    assert m5.taggedstruct_definition is None

    bd = m5.block_definition
    assert bd.member is None
    assert bd.tag == "DAQ_EVENT"
    tn = bd.type_name
    assert tn.tag is None
    assert tn.type_.identifier == "Daq_Event"

def test_aml_13():
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    DATA = """/begin A2ML
block "IF_DATA" taggedunion if_data {
"ASAP1B_Bypass" taggedstruct {
(block "SOURCE" struct {
struct {
char[101];
int;
long;
};
taggedstruct {
block "QP_BLOB" struct {
uint;
};
};
})*;
block "TP_BLOB" struct {
uint;
uint;
};
block "DP_BLOB" struct {
};
block "PA_BLOB" struct {
};
block "KP_BLOB" struct {
taggedstruct {
"BUFFER_OFFSET"    char[256];
"SOURCE_ID"        char[256];
"BIT_OFFSET"       char[256];
"POSSIBLE_SOURCES" ( uint )*;
};
};
};
"ASAP1B_CCP" taggedstruct {
(block "SOURCE" struct {
struct {
char [101];
int;
long;
};
taggedstruct {
"DISPLAY_IDENTIFIER" char[32];
block "QP_BLOB" struct {
uint;
taggedstruct {
"LENGTH" uint;
"CAN_ID_VARIABLE";
"CAN_ID_FIXED" ulong;
("RASTER" uchar; )*;
("EXCLUSIVE" int; )*;
"REDUCTION_ALLOWED";
"FIRST_PID" uchar;
};
};
};
}; )*;
(block "RASTER" struct {
char [101];
char [9];
uchar;
int;
long;
taggedstruct {
("EXCLUSIVE" uchar; )*;
};
}; )*;
(block "EVENT_GROUP" struct {
char [101];
char [9];
taggedstruct {
("RASTER" uchar; )*;
};
}; )*;
block "SEED_KEY" struct {
char[256];
char[256];
char[256];
};
block "CHECKSUM" struct {
char[256];
};
block "TP_BLOB" struct {
uint;
uint;
ulong;
ulong;
uint;
uint;
taggedstruct {
block "CAN_PARAM" struct {
uint;
uchar;
uchar;
};
"BAUDRATE" ulong;
"SAMPLE_POINT" uchar;
"SAMPLE_RATE" uchar;
"BTL_CYCLES" uchar;
"SJW" uchar;
"SYNC_EDGE" enum {
"SINGLE" = 0,
"DUAL" = 1
};
"DAQ_MODE" enum {
"ALTERNATING" = 0,
"BURST" = 1
};
"BYTES_ONLY";
"RESUME_SUPPORTED";
"STORE_SUPPORTED";
"CONSISTENCY" enum {
"DAQ" = 0,
"ODT" = 1
};
"ADDRESS_EXTENSION" enum {
"DAQ" = 0,
"ODT" = 1
};
block "CHECKSUM_PARAM" struct {
uint;
ulong;
taggedstruct {
"CHECKSUM_CALCULATION" enum {
"ACTIVE_PAGE" = 0,
"BIT_OR_WITH_OPT_PAGE" = 1
};
};
};
(block "DEFINED_PAGES" struct {
struct {
uint;
char[101];
uint;
ulong;
ulong;
};
taggedstruct {
"RAM";
"ROM";
"FLASH";
"EEPROM";
"RAM_INIT_BY_ECU";
"RAM_INIT_BY_TOOL";
"AUTO_FLASH_BACK";
"FLASH_BACK";
"DEFAULT";
};
}; ) *;
( "OPTIONAL_CMD"  uint; )*;
};
};
"DP_BLOB" struct {
uint;
ulong;
ulong;
};
"KP_BLOB" struct {
uint;
ulong;
ulong;
taggedstruct {
("RASTER" uchar; )*;
};
};
};
"ETK" taggedstruct
{
("ADDRESS_MAPPING" struct
{
ulong;
ulong;
ulong;
}
)*;
(block "SOURCE" struct
{
struct
{
char [100];
int;
long;
};
taggedstruct
{
"QP_BLOB" struct
{
uint;
uint;
ulong;
ulong;
ulong;
uint;
uint;
ulong;
};
};
})*;
block "TP_BLOB" struct
{
ulong;
ulong;
ulong;
block "DISTAB_CFG" struct {
uint;
uint;
uint;
ulong;
ulong;
taggedstruct {
"TRG_MOD" ( uchar; )*;
};
};
taggedstruct {
"CODE_CHK" struct {
ulong;
uint;
ulong;
uint;
};
"ETK_CFG" ( uchar; )*;
( "EMU_DATA" struct {
ulong;
ulong;
enum {
"INTERN"  = 0,
"EXTERN"  = 1
};
ulong;
ulong;
ulong;
ulong;
ulong;
})*;
( "EMU_CODE" struct {
ulong;
ulong;
enum {
"INTERN"  = 0,
"EXTERN"  = 1
};
ulong;
ulong;
ulong;
ulong;
ulong;
})*;
( "EMU_RAM" struct {
ulong;
ulong;
enum {
"INTERN"  = 0,
"EXTERN"  = 1
};
ulong;
ulong;
ulong;
ulong;
ulong;
})*;
( "RESERVED" struct {
ulong;
ulong;
enum {
"INTERN"  = 0,
"EXTERN"  = 1
};
ulong;
ulong;
ulong;
ulong;
ulong;
})*;
"ETK_MAILBOX" struct {
ulong;
enum {
"CODE"  = 1,
"DATA"  = 2,
"EXRAM" = 3
};
ulong;
ulong;
enum {
"CODE"  = 1,
"DATA"  = 2,
"EXRAM" = 3
};
ulong;
ulong;
};
}
};
"DP_BLOB" struct
{
ulong;
ulong;
};
"KP_BLOB" struct
{
ulong;
uint;
uint;
};
};
"ASAP1B_KWP2000"  taggedstruct {
("ADDRESS_MAPPING" struct
{
ulong;
ulong;
ulong;
}
)*;
( "SEED_KEY"
char[256]
)*;
(block "SOURCE" struct {
struct {
char [100];
int;
long;
};
taggedstruct {
"QP_BLOB" struct {
uint;
enum {
"ADDRESSMODE"  = 1,
"BLOCKMODE"    = 2
};
uint;
uint;
uint;
};
};
}
)*;
block "TP_BLOB" struct {
uint;
uint;
uint;
enum {
"WuP"   = 1,
"5Baud" = 2
};
enum {
"MSB_FIRST" = 1,
"MSB_LAST"  = 2
};
uint;
taggedstruct {
"DATA_ACCESS" struct {
ulong;
ulong;
uint;
uint;
uint;
uint;
};
block "CHECKSUM" struct {
ulong;
uint;
uint;
enum {
"RequestRoutineResults" = 0,
"StartRoutine"          = 1,
"CodedResult"			  = 2
};
taggedstruct {
"RNC_RESULT" ( uchar )*;
};
};
block "FLASH_COPY" struct {
enum {
"NOFLASHBACK"   = 0x00,
"AUTOFLASHBACK" = 0x40,
"TOOLFLASHBACK" = 0x80
};
uint;
enum {
"RequestRoutineResults" = 0,
"StartRoutine"          = 1,
"CodedResult"			  = 2
};
enum {
"RAM_InitByECU"  = 0x10,
"RAM_InitByTool" = 0x20
};
uint;
taggedstruct {
"COPY_FRAME" ( uchar )*;
"RNC_RESULT" ( uchar )*;
"COPY_PARA" ( uchar )*;
};
};
( block "DIAG_BAUD" struct {
ulong;
uint;
taggedstruct {
"BD_PARA" ( uchar )*;
};
}
)*;
( "TIME_DEF" struct {
uint;
uint;
uint;
uint;
uint;
uint;
}
)*;
( "SECURITY_ACCESS" struct {
uint;
uint;
uint;
}
)*;
block "PAGE_SWITCH" struct {
enum {
"ESCAPE_CODE"   = 0x80,
"LOCAL_ROUTINE" = 0x31
};
taggedstruct {
"ESCAPE_CODE_PARA"  ( uchar )*;
block "ROUTINE_PARA" struct {
uint;
enum {
"RequestRoutineResults" = 0,
"StartRoutine"          = 1,
"CodedResult" 	      = 2
};
taggedstruct {
"RNC_RESULT" ( uchar )*;
};
};
"PAGE_CODE" ( uchar )*;
};
};
};
};
"DP_BLOB" struct {
ulong;
ulong;
};
"KP_BLOB" struct {
ulong;
enum {
"INTERN"  = 0,
"EXTERN"  = 1
};
uint;
};
};
"ASAP1B_MCMESS" taggedstruct
{
(block "SOURCE" struct
{
struct
{
char [100];
int;
long;
};
taggedstruct
{
"QP_BLOB" struct
{
enum
{
"HANDSHAKE" = 0x00,
"ANGLE"     = 0x08,
"TIME"      = 0x0C
};
uint;
};
};
}
)*;
block "TP_BLOB" struct
{
uint;
taggedstruct
{
"KOMKEN"      uint;
"MCTGT"       long;
"MCINI"       enum
{
"MASSE"  = 0,
"KW2000" = 1
};
"WFSIDLE0"    uint;
"WFSIDLE1"    uint;
"WFS5B"       uint;
"NOOFCYL"     uint;
"CYLCNAME"    char[20];
"CYLSEQU"     char[30];
"XRAMOF"      uint;
block "CHECKSUM_PARAM" struct
{
ulong;
taggedstruct
{
"CHECKSUM_CALCULATION"
enum
{
"ACTIVE_PAGE",
"WORKING_PAGE"
};
};
};
(block "DEFINED_PAGES" struct
{
uint;
char[101];
taggedunion
{
"RAM" struct
{
enum
{
"RAM_INIT_BY_ECU",
"RAM_INIT_BY_TOOL"
};
taggedstruct
{
"DEFAULT";
};
};
"ROM" taggedstruct
{
"DEFAULT";
};
"FLASH" struct
{
enum
{
"NO_FLASH_BACK",
"AUTO_FLASH_BACK",
"FLASH_BACK"
};
taggedstruct
{
"DEFAULT";
};
};
"EEPROM" struct
{
enum
{
"NO_FLASH_BACK",
"AUTO_FLASH_BACK",
"FLASH_BACK"
};
taggedstruct
{
"DEFAULT";
};
};
};
})*;
"BYTE_ORDER" enum
{
"MSB_FIRST",
"MSB_LAST"
};
"THREE_BYTE_ADDRESSES";
"COPY_FLASH_TO_RAM_BY_COMMAND";
};
};
block "KP_BLOB" struct
{
long;
enum
{
"INTERN",
"EXTERN"
};
uint;
taggedstruct
{
"PSEUDO_ADR" uint;
"VS_DEF"     char[20];
};
};
"DP_BLOB" struct
{
ulong;
ulong;
};
};
};
/end A2ML"""
    res = parser.parseFromString(DATA)


def test_taggedstruct2():
    DATA = """
    /begin A2ML
    taggedstruct {
        ("EXCLUSIVE" uchar; )*;
        "POSSIBLE_SOURCES" ( uint )*;
    };
    /end A2ML
    """
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    res = parser.parseFromString(DATA)


def test_taggedstruct3():
    DATA = """
    /begin A2ML
    taggedstruct {
    (block "RASTER" struct {
    char [101];
    char [9];
    uchar;
    int;
    long;
    taggedstruct {
    ("EXCLUSIVE" uchar; )*;
    };
    }; )*;
    };
    /end A2ML
    """
    parser = ParserWrapper("aml", "amlFile", AMLListener)
    res = parser.parseFromString(DATA)
