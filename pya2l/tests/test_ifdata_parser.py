#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pkgutil
import contextlib
from pprint import pprint
import pytest

from pya2l.if_data_parser import IfDataParser

from pya2l.aml.listener import AMLListener
from pya2l.parserlib import ParserWrapper

ETAS1 = """
    /begin IF_DATA ASAP1B_Bypass
                /begin KP_BLOB
                    BUFFER_OFFSET    "VSwVlv_r_Bypass.Vector"
                    SOURCE_ID        "VSwVlv_r_Bypass.Channel"
                    /* no BIT_OFFSET       */
                    /* no POSSIBLE_SOURCES */
                /end KP_BLOB
    /end IF_DATA
"""

ETAS2 = "/begin IF_DATA ASAP1B_CCP KP_BLOB 0x00 0xD0001240 0x2 RASTER 1 /end IF_DATA"
ETAS3 = "/begin IF_DATA ETK KP_BLOB 0xD0001240 INTERN 0x2 RASTER 2 /end IF_DATA"

SEGMENT = """
/begin IF_DATA XCP
  /begin SEGMENT
    0x0
    0x2
    0x0
    0x0
    0x0
    /begin CHECKSUM
      XCP_ADD_12
      MAX_BLOCK_SIZE 0x0
      EXTERNAL_FUNCTION ""
    /end CHECKSUM
    /begin PAGE
      0x1
      ECU_ACCESS_DONT_CARE
      XCP_READ_ACCESS_DONT_CARE
      XCP_WRITE_ACCESS_DONT_CARE
      INIT_SEGMENT 0x0
    /end PAGE
    /begin PAGE
      0x0
      ECU_ACCESS_DONT_CARE
      XCP_READ_ACCESS_DONT_CARE
      XCP_WRITE_ACCESS_DONT_CARE
      INIT_SEGMENT 0x0
    /end PAGE
    /begin ADDRESS_MAPPING
      0xE1058 0xE1058 0xE9D
    /end ADDRESS_MAPPING
  /end SEGMENT
/end IF_DATA
"""

BASIC = """
    /begin IF_DATA XCP
      /begin PROTOCOL_LAYER
        0x100 0x20 0x20 0x20 0x20 0x20 0x20 0x20 0x8 0x8 BYTE_ORDER_MSB_LAST ADDRESS_GRANULARITY_BYTE
        OPTIONAL_CMD SET_REQUEST
        OPTIONAL_CMD GET_SEED
        OPTIONAL_CMD UNLOCK
        OPTIONAL_CMD SET_MTA
        OPTIONAL_CMD SHORT_DOWNLOAD
        OPTIONAL_CMD PROGRAM_START
        OPTIONAL_CMD PROGRAM_CLEAR
        OPTIONAL_CMD PROGRAM
        OPTIONAL_CMD PROGRAM_RESET
        OPTIONAL_CMD GET_PGM_PROCESSOR_INFO
        OPTIONAL_CMD GET_SECTOR_INFO
        OPTIONAL_CMD PROGRAM_PREPARE
        OPTIONAL_CMD PROGRAM_NEXT
        OPTIONAL_CMD PROGRAM_MAX
        OPTIONAL_CMD PROGRAM_VERIFY
        OPTIONAL_CMD TRANSPORT_LAYER_CMD
        OPTIONAL_CMD GET_ID
        OPTIONAL_CMD UPLOAD
        OPTIONAL_CMD SHORT_UPLOAD
        OPTIONAL_CMD BUILD_CHECKSUM
        OPTIONAL_CMD DOWNLOAD_NEXT
        OPTIONAL_CMD SET_CAL_PAGE
        OPTIONAL_CMD GET_CAL_PAGE
        OPTIONAL_CMD CLEAR_DAQ_LIST
        OPTIONAL_CMD SET_DAQ_PTR
        OPTIONAL_CMD WRITE_DAQ
        OPTIONAL_CMD SET_DAQ_LIST_MODE
        OPTIONAL_CMD GET_DAQ_LIST_MODE
        OPTIONAL_CMD START_STOP_DAQ_LIST
        OPTIONAL_CMD FREE_DAQ
        OPTIONAL_CMD ALLOC_DAQ
        OPTIONAL_CMD ALLOC_ODT
        OPTIONAL_CMD ALLOC_ODT_ENTRY
        OPTIONAL_CMD START_STOP_SYNCH
        OPTIONAL_CMD DOWNLOAD
        OPTIONAL_CMD MODIFY_BITS
        OPTIONAL_CMD GET_PAG_PROCESSOR_INFO
        OPTIONAL_CMD GET_SEGMENT_INFO
        OPTIONAL_CMD GET_PAGE_INFO
        OPTIONAL_CMD SET_SEGMENT_MODE
        OPTIONAL_CMD GET_SEGMENT_MODE
        OPTIONAL_CMD COPY_CAL_PAGE
        OPTIONAL_CMD GET_DAQ_CLOCK
        OPTIONAL_CMD READ_DAQ
        OPTIONAL_CMD GET_DAQ_LIST_MODE
        OPTIONAL_CMD DOWNLOAD_MAX
        COMMUNICATION_MODE_SUPPORTED
          BLOCK
            SLAVE
            MASTER 0x14 0x5
      /end PROTOCOL_LAYER
      /begin DAQ
        STATIC 0x3 0x2 0x0 OPTIMISATION_TYPE_DEFAULT ADDRESS_EXTENSION_DAQ IDENTIFICATION_FIELD_TYPE_ABSOLUTE GRANULARITY_ODT_ENTRY_SIZE_DAQ_BYTE 0x4 OVERLOAD_INDICATION_EVENT
        PRESCALER_SUPPORTED
        /begin TIMESTAMP_SUPPORTED
          0x1 SIZE_DWORD UNIT_1US
        /end TIMESTAMP_SUPPORTED
        /begin DAQ_LIST
          0x0
          DAQ_LIST_TYPE DAQ
          MAX_ODT 0x5
          MAX_ODT_ENTRIES 0x7
        /end DAQ_LIST
        /begin DAQ_LIST
          0x1
          DAQ_LIST_TYPE DAQ
          MAX_ODT 0x4
          MAX_ODT_ENTRIES 0x7
        /end DAQ_LIST
        /begin DAQ_LIST
          0x2
          DAQ_LIST_TYPE DAQ
          MAX_ODT 0x3
          MAX_ODT_ENTRIES 0x7
        /end DAQ_LIST
        /begin EVENT
          "5ms" "5ms" 0x0 DAQ 0xFF 0x5 0x6 0xFF
        /end EVENT
        /begin EVENT
          "extEvent" "extEvent" 0x1 DAQ 0xFF 0x1 0x9 0xFF
        /end EVENT
      /end DAQ
      /begin XCP_ON_CAN
        0x100
        CAN_ID_BROADCAST 0x52
        CAN_ID_MASTER 0x51
        CAN_ID_SLAVE 0x50
        BAUDRATE 0x7A120
      /end XCP_ON_CAN
    /end IF_DATA
"""

def load_file(name):
    parser = ParserWrapper("aml", "amlFile", AMLListener, useDatabase=False)
    data = str(pkgutil.get_data("pya2l", "examples/{}".format(name)), "ascii")
    return parser.parseFromString(data)

@pytest.fixture
def vector_aml():
    return load_file("vector.aml")

@pytest.fixture
def etas_aml():
    return load_file("etas.aml")

def test_if_data_segment(vector_aml):
    ip = IfDataParser(vector_aml)
    res = ip.parse(SEGMENT)
    assert res == [
        {'tag': 'IF_DATA', 'value': [[[[
            {'tag': 'SEGMENT', 'value': [0, 2, 0, 0, 0, [[
            {'tag': 'CHECKSUM', 'value': ['XCP_ADD_12', [
            {'tag': 'MAX_BLOCK_SIZE', 'value': 0},
            {'tag': 'EXTERNAL_FUNCTION', 'value': ''}]]}],
            [{'tag': 'PAGE', 'value': [1, 'ECU_ACCESS_DONT_CARE', 'XCP_READ_ACCESS_DONT_CARE', 'XCP_WRITE_ACCESS_DONT_CARE',
            [{'tag': 'INIT_SEGMENT', 'value': 0}]]}], [
            {'tag': 'PAGE', 'value': [0, 'ECU_ACCESS_DONT_CARE', 'XCP_READ_ACCESS_DONT_CARE', 'XCP_WRITE_ACCESS_DONT_CARE',
            [{'tag': 'INIT_SEGMENT', 'value': 0}]]}],
            [{'tag': 'ADDRESS_MAPPING', 'value': [921688, 921688, 3741]}]]]}]], []]]}
        ]

def test_basic(vector_aml):
    ip = IfDataParser(vector_aml)
    res = ip.parse(BASIC)
    assert res == [{'tag': 'IF_DATA', 'value': [[[[{'tag': 'PROTOCOL_LAYER', 'value':
        [256, 32, 32, 32, 32, 32, 32, 32, 8, 8, 'BYTE_ORDER_MSB_LAST', 'ADDRESS_GRANULARITY_BYTE',
        [{'tag': 'OPTIONAL_CMD', 'value': 'SET_REQUEST'},
        {'tag': 'OPTIONAL_CMD', 'value': 'GET_SEED'},
        {'tag': 'OPTIONAL_CMD', 'value': 'UNLOCK'},
        {'tag': 'OPTIONAL_CMD', 'value': 'SET_MTA'},
        {'tag': 'OPTIONAL_CMD', 'value': 'SHORT_DOWNLOAD'},
        {'tag': 'OPTIONAL_CMD', 'value': 'PROGRAM_START'},
        {'tag': 'OPTIONAL_CMD', 'value': 'PROGRAM_CLEAR'},
        {'tag': 'OPTIONAL_CMD', 'value': 'PROGRAM'},
        {'tag': 'OPTIONAL_CMD', 'value': 'PROGRAM_RESET'},
        {'tag': 'OPTIONAL_CMD', 'value': 'GET_PGM_PROCESSOR_INFO'},
        {'tag': 'OPTIONAL_CMD', 'value': 'GET_SECTOR_INFO'},
        {'tag': 'OPTIONAL_CMD', 'value': 'PROGRAM_PREPARE'},
        {'tag': 'OPTIONAL_CMD', 'value': 'PROGRAM_NEXT'},
        {'tag': 'OPTIONAL_CMD', 'value': 'PROGRAM_MAX'},
        {'tag': 'OPTIONAL_CMD', 'value': 'PROGRAM_VERIFY'},
        {'tag': 'OPTIONAL_CMD', 'value': 'TRANSPORT_LAYER_CMD'},
        {'tag': 'OPTIONAL_CMD', 'value': 'GET_ID'},
        {'tag': 'OPTIONAL_CMD', 'value': 'UPLOAD'},
        {'tag': 'OPTIONAL_CMD', 'value': 'SHORT_UPLOAD'},
        {'tag': 'OPTIONAL_CMD', 'value': 'BUILD_CHECKSUM'},
        {'tag': 'OPTIONAL_CMD', 'value': 'DOWNLOAD_NEXT'},
        {'tag': 'OPTIONAL_CMD', 'value': 'SET_CAL_PAGE'},
        {'tag': 'OPTIONAL_CMD', 'value': 'GET_CAL_PAGE'},
        {'tag': 'OPTIONAL_CMD', 'value': 'CLEAR_DAQ_LIST'},
        {'tag': 'OPTIONAL_CMD', 'value': 'SET_DAQ_PTR'},
        {'tag': 'OPTIONAL_CMD', 'value': 'WRITE_DAQ'},
        {'tag': 'OPTIONAL_CMD', 'value': 'SET_DAQ_LIST_MODE'},
        {'tag': 'OPTIONAL_CMD', 'value': 'GET_DAQ_LIST_MODE'},
        {'tag': 'OPTIONAL_CMD', 'value': 'START_STOP_DAQ_LIST'},
        {'tag': 'OPTIONAL_CMD', 'value': 'FREE_DAQ'},
        {'tag': 'OPTIONAL_CMD', 'value': 'ALLOC_DAQ'},
        {'tag': 'OPTIONAL_CMD', 'value': 'ALLOC_ODT'},
        {'tag': 'OPTIONAL_CMD', 'value': 'ALLOC_ODT_ENTRY'},
        {'tag': 'OPTIONAL_CMD', 'value': 'START_STOP_SYNCH'},
        {'tag': 'OPTIONAL_CMD', 'value': 'DOWNLOAD'},
        {'tag': 'OPTIONAL_CMD', 'value': 'MODIFY_BITS'},
        {'tag': 'OPTIONAL_CMD', 'value': 'GET_PAG_PROCESSOR_INFO'},
        {'tag': 'OPTIONAL_CMD', 'value': 'GET_SEGMENT_INFO'},
        {'tag': 'OPTIONAL_CMD', 'value': 'GET_PAGE_INFO'},
        {'tag': 'OPTIONAL_CMD', 'value': 'SET_SEGMENT_MODE'},
        {'tag': 'OPTIONAL_CMD', 'value': 'GET_SEGMENT_MODE'},
        {'tag': 'OPTIONAL_CMD', 'value': 'COPY_CAL_PAGE'},
        {'tag': 'OPTIONAL_CMD', 'value': 'GET_DAQ_CLOCK'},
        {'tag': 'OPTIONAL_CMD', 'value': 'READ_DAQ'},
        {'tag': 'OPTIONAL_CMD', 'value': 'GET_DAQ_LIST_MODE'},
        {'tag': 'OPTIONAL_CMD', 'value': 'DOWNLOAD_MAX'},
        {'type': 'tagged_union', 'tag': 'COMMUNICATION_MODE_SUPPORTED', 'value': [[{'tag': 'SLAVE', 'value': None},
            {'type': 'struct', 'tag': 'MASTER', 'value': [20, 5]}]]}]]}],
            [{'tag': 'DAQ', 'value':
                ['STATIC', 3, 2, 0, 'OPTIMISATION_TYPE_DEFAULT', 'ADDRESS_EXTENSION_DAQ', 'IDENTIFICATION_FIELD_TYPE_ABSOLUTE',
                 'GRANULARITY_ODT_ENTRY_SIZE_DAQ_BYTE', 4, 'OVERLOAD_INDICATION_EVENT',
            [{'tag': 'PRESCALER_SUPPORTED', 'value': None}, [
            {'tag': 'TIMESTAMP_SUPPORTED', 'value': [1, 'SIZE_DWORD', 'UNIT_1US', []]}],
            [{'tag': 'DAQ_LIST', 'value': [0, [
                {'tag': 'DAQ_LIST_TYPE', 'value': 'DAQ'},
                {'tag': 'MAX_ODT', 'value': 5},
                {'tag': 'MAX_ODT_ENTRIES', 'value': 7}]]}],
            [{'tag': 'DAQ_LIST', 'value': [1, [
                {'tag': 'DAQ_LIST_TYPE', 'value': 'DAQ'},
                {'tag': 'MAX_ODT', 'value': 4},
                {'tag': 'MAX_ODT_ENTRIES', 'value': 7}]]}],
            [{'tag': 'DAQ_LIST', 'value': [2, [{
                'tag': 'DAQ_LIST_TYPE', 'value': 'DAQ'},
                {'tag': 'MAX_ODT', 'value': 3},
                {'tag': 'MAX_ODT_ENTRIES', 'value': 7}]]}],
            [{'tag': 'EVENT', 'value': ['5ms', '5ms', 0, 'DAQ', 255, 5, 6, 255]}],
            [{'tag': 'EVENT', 'value': ['extEvent', 'extEvent', 1, 'DAQ', 255, 1, 9, 255]}]]]}]],
        [[{'tag': 'XCP_ON_CAN', 'value': [[256, [{
            'tag': 'CAN_ID_BROADCAST', 'value': 82},
            {'tag': 'CAN_ID_MASTER','value': 81},
            {'tag': 'CAN_ID_SLAVE', 'value': 80},
            {'tag': 'BAUDRATE', 'value': 500000}]], []]}]]]]}
    ]

def test_etas1(etas_aml):
    ip = IfDataParser(etas_aml)
    res = ip.parse(ETAS1)
    assert res == [
        {'tag': 'IF_DATA', 'value': [[[
            {'tag':'KP_BLOB', 'value': [[
                {'tag': 'BUFFER_OFFSET', 'value': 'VSwVlv_r_Bypass.Vector'},
                {'tag': 'SOURCE_ID', 'value': 'VSwVlv_r_Bypass.Channel'}
            ]]}]]]}
    ]

def test_etas2(etas_aml):
    ip = IfDataParser(etas_aml)
    res = ip.parse(ETAS2)
    assert res == [{'value': [[
        {'value': [0, 3489665600, 2, [{'value': 1, 'tag': 'RASTER'}]],
            'type': 'struct', 'tag': 'KP_BLOB'}]], 'tag': 'IF_DATA'}
    ]

def test_etas3(etas_aml):
    ip = IfDataParser(etas_aml)
    res = ip.parse(ETAS3)
    assert res == [{'tag': 'IF_DATA', 'value': [[
        {'type': 'struct', 'tag': 'KP_BLOB', 'value': [3489665600, 'INTERN', 2, [{'tag': 'RASTER', 'value': 2}]]}]]}
    ]

