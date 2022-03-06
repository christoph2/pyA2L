#!/usr/bin/env python
# -*- coding: utf-8 -*-
import contextlib
import pkgutil
from pprint import pprint

import pytest

from pya2l import parsers

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
        STATIC 0x3 0x2 0x0 OPTIMISATION_TYPE_DEFAULT ADDRESS_EXTENSION_DAQ IDENTIFICATION_FIELD_TYPE_ABSOLUTE
        GRANULARITY_ODT_ENTRY_SIZE_DAQ_BYTE 0x4 OVERLOAD_INDICATION_EVENT
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
    parser = parsers.aml()
    data = str(pkgutil.get_data("pya2l", "examples/{}".format(name)), "ascii")
    result = parser.parseFromString(data)
    return result.listener_result


@pytest.fixture
def vector_aml():
    return load_file("vector.aml")


@pytest.fixture
def etas_aml():
    return load_file("etas.aml")


def test_if_data_segment(vector_aml):
    ip = parsers.if_data(vector_aml)
    res = ip.parse(SEGMENT)
    assert res == {
        "tag": "IF_DATA",
        "value": [
            {
                "SEGMENT": [
                    0,
                    2,
                    0,
                    0,
                    0,
                    {
                        "CHECKSUM": ["XCP_ADD_12", {"MAX_BLOCK_SIZE": 0, "EXTERNAL_FUNCTION": ""}],
                        "PAGE": [
                            [
                                1,
                                "ECU_ACCESS_DONT_CARE",
                                "XCP_READ_ACCESS_DONT_CARE",
                                "XCP_WRITE_ACCESS_DONT_CARE",
                                {"INIT_SEGMENT": 0},
                            ],
                            [
                                0,
                                "ECU_ACCESS_DONT_CARE",
                                "XCP_READ_ACCESS_DONT_CARE",
                                "XCP_WRITE_ACCESS_DONT_CARE",
                                {"INIT_SEGMENT": 0},
                            ],
                        ],
                        "ADDRESS_MAPPING": [[921688, 921688, 3741]],
                    },
                ]
            },
            {},
        ],
    }


def test_basic(vector_aml):
    ip = parsers.if_data(vector_aml)
    res = ip.parse(BASIC)
    assert res == {
        "tag": "IF_DATA",
        "value": [
            {
                "PROTOCOL_LAYER": [
                    256,
                    32,
                    32,
                    32,
                    32,
                    32,
                    32,
                    32,
                    8,
                    8,
                    "BYTE_ORDER_MSB_LAST",
                    "ADDRESS_GRANULARITY_BYTE",
                    {
                        "OPTIONAL_CMD": [
                            "SET_REQUEST",
                            "GET_SEED",
                            "UNLOCK",
                            "SET_MTA",
                            "SHORT_DOWNLOAD",
                            "PROGRAM_START",
                            "PROGRAM_CLEAR",
                            "PROGRAM",
                            "PROGRAM_RESET",
                            "GET_PGM_PROCESSOR_INFO",
                            "GET_SECTOR_INFO",
                            "PROGRAM_PREPARE",
                            "PROGRAM_NEXT",
                            "PROGRAM_MAX",
                            "PROGRAM_VERIFY",
                            "TRANSPORT_LAYER_CMD",
                            "GET_ID",
                            "UPLOAD",
                            "SHORT_UPLOAD",
                            "BUILD_CHECKSUM",
                            "DOWNLOAD_NEXT",
                            "SET_CAL_PAGE",
                            "GET_CAL_PAGE",
                            "CLEAR_DAQ_LIST",
                            "SET_DAQ_PTR",
                            "WRITE_DAQ",
                            "SET_DAQ_LIST_MODE",
                            "GET_DAQ_LIST_MODE",
                            "START_STOP_DAQ_LIST",
                            "FREE_DAQ",
                            "ALLOC_DAQ",
                            "ALLOC_ODT",
                            "ALLOC_ODT_ENTRY",
                            "START_STOP_SYNCH",
                            "DOWNLOAD",
                            "MODIFY_BITS",
                            "GET_PAG_PROCESSOR_INFO",
                            "GET_SEGMENT_INFO",
                            "GET_PAGE_INFO",
                            "SET_SEGMENT_MODE",
                            "GET_SEGMENT_MODE",
                            "COPY_CAL_PAGE",
                            "GET_DAQ_CLOCK",
                            "READ_DAQ",
                            "GET_DAQ_LIST_MODE",
                            "DOWNLOAD_MAX",
                        ],
                        "COMMUNICATION_MODE_SUPPORTED": {"SLAVE": None, "MASTER": [20, 5]},
                    },
                ],
                "DAQ": [
                    "STATIC",
                    3,
                    2,
                    0,
                    "OPTIMISATION_TYPE_DEFAULT",
                    "ADDRESS_EXTENSION_DAQ",
                    "IDENTIFICATION_FIELD_TYPE_ABSOLUTE",
                    "GRANULARITY_ODT_ENTRY_SIZE_DAQ_BYTE",
                    4,
                    "OVERLOAD_INDICATION_EVENT",
                    {
                        "PRESCALER_SUPPORTED": None,
                        "TIMESTAMP_SUPPORTED": [1, "SIZE_DWORD", "UNIT_1US", {}],
                        "DAQ_LIST": [
                            [0, {"DAQ_LIST_TYPE": "DAQ", "MAX_ODT": 5, "MAX_ODT_ENTRIES": 7}],
                            [1, {"DAQ_LIST_TYPE": "DAQ", "MAX_ODT": 4, "MAX_ODT_ENTRIES": 7}],
                            [2, {"DAQ_LIST_TYPE": "DAQ", "MAX_ODT": 3, "MAX_ODT_ENTRIES": 7}],
                        ],
                        "EVENT": [["5ms", "5ms", 0, "DAQ", 255, 5, 6, 255], ["extEvent", "extEvent", 1, "DAQ", 255, 1, 9, 255]],
                    },
                ],
            },
            {"XCP_ON_CAN": [[256, {"CAN_ID_BROADCAST": 82, "CAN_ID_MASTER": 81, "CAN_ID_SLAVE": 80, "BAUDRATE": 500000}], {}]},
        ],
    }


def test_etas1(etas_aml):
    ip = parsers.if_data(etas_aml)
    res = ip.parse(ETAS1)
    assert res == {
        "tag": "IF_DATA",
        "value": {"KP_BLOB": [{"BUFFER_OFFSET": "VSwVlv_r_Bypass.Vector", "SOURCE_ID": "VSwVlv_r_Bypass.Channel"}]},
    }


def test_etas2(etas_aml):
    ip = parsers.if_data(etas_aml)
    res = ip.parse(ETAS2)
    assert res == {"tag": "IF_DATA", "value": {"KP_BLOB": [0, 3489665600, 2, {"RASTER": [1]}]}}


def test_etas3(etas_aml):
    ip = parsers.if_data(etas_aml)
    res = ip.parse(ETAS3)
    assert res == {"tag": "IF_DATA", "value": {"KP_BLOB": [3489665600, "INTERN", 2, {"RASTER": [2]}]}}
