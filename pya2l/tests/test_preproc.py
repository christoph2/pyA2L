#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib
import sys

BASE_DIR = pathlib.Path(__file__).absolute().parent

import pytest

from pya2l.preprocessor import Preprocessor


#@pytest.mark.skip
def test_singleline_ifdata():
    pre = Preprocessor()
    res = pre.process(BASE_DIR / "singleline_ifdata.a2l")
    assert len(res.if_data_sections) == 1
    sec = res.if_data_sections[0]
    assert sec.data == r"/begin IF_DATA XCP /begin DAQ_EVENT FIXED_EVENT_LIST EVENT 0x0 /end DAQ_EVENT /end IF_DATA"
    assert sec.start_line == (1, 173)
    assert sec.end_line == (1, 263)
    assert res.a2l_data == '/begin MEASUREMENT ecuCounter "16 bit counter incrementing exactly every 100us in XCP slave time" UWORD ecuCounter_COMPU_METHOD 0 0 0 65535 ECU_ADDRESS 0x2E348 PHYS_UNIT "" /begin IF_DATA XCP                                                            /end IF_DATA /end MEASUREMENT'

#@pytest.mark.skip
def test_multiple_ifdatas_per_line():
    pre = Preprocessor()
    res = pre.process(BASE_DIR / "multiple_ifdatas_per_line.a2l")
    '''
    assert res.a2l_data == '/begin MEASUREMENT BitSlice "Testsignal: 4 Bit on a byte boundary" UWORD BitSlice.CONVERSION 0 0 0 15 BIT_MASK 0x3C0    BYTE_ORDER MSB_LAST ECU_ADDRESS 0x125438 ECU_ADDRESS_EXTENSION 0x0 FORMAT "%.3" /begin IF_DATA CANAPE_EXT                                                                         /end IF_DATA SYMBOL_LINK "wordCounter" 0 /end MEASUREMENT /begin MEASUREMENT BitSlice0 "Testsignal: 5 Bit" UWORD BitSlice.CONVERSION 0 0 0 31 BIT_MASK 0x1F BYTE_ORDER MSB_LAST ECU_ADDRESS 0x125438 ECU_ADDRESS_EXTENSION 0x0 FORMAT "%.3" /begin IF_DATA CANAPE_EXT                                                                          /end IF_DATA SYMBOL_LINK "wordCounter" 0 /end MEASUREMENT /begin MEASUREMENT BitSlice1 "Testsignal: 5 Bit " UWORD BitSlice.CONVERSION 0 0 0 31 BIT_MASK 0x3E0 BYTE_ORDER MSB_LAST ECU_ADDRESS 0x125438 ECU_ADDRESS_EXTENSION 0x0 FORMAT "%.3" /begin IF_DATA CANAPE_EXT                                                                          /end IF_DATA SYMBOL_LINK "wordCounter" 0 /end MEASUREMENT'
    '''
    sections = res.if_data_sections
    assert len(sections) == 3

    sec = sections[0]
    assert sec.start_line == (1, 200)
    assert sec.end_line == (1, 310)
    assert sec.data == '/begin IF_DATA CANAPE_EXT 100 LINK_MAP "wordCounter" 0x125438 0x0 0 0x0 1 0x8F 0x0 DISPLAY 0 0 15 /end IF_DATA'

    sec = sections[1]
    assert sec.start_line == (1, 534)
    assert sec.end_line == (1, 645)
    assert sec.data == '/begin IF_DATA CANAPE_EXT 100 LINK_MAP "wordCounter1" 0x12543a 0x0 0 0x0 1 0x8F 0x0 DISPLAY 0 0 31 /end IF_DATA'

    sec = sections[2]
    assert sec.start_line == (1, 871)
    assert sec.end_line == (1, 982)
    assert sec.data == '/begin IF_DATA CANAPE_EXT 100 LINK_MAP "wordCounter2" 0x12543c 0x0 0 0x0 1 0x8F 0x0 DISPLAY 0 0 31 /end IF_DATA'

#@pytest.mark.skip
def test_clean_ifdata():
    pre = Preprocessor()
    res = pre.process(BASE_DIR / "clean_ifdata.a2l")
    sections = res.if_data_sections
    assert len(sections) == 1
    sec = sections[0]
    assert sec.start_line == (12, 4)
    assert sec.end_line == (16, 16)
    assert sec.data == '/begin IF_DATA XCP\n/begin DAQ_EVENT\nFIXED_EVENT_LIST EVENT 0x0\n/end DAQ_EVENT\n    /end IF_DATA'
    assert res.a2l_data == """/begin MEASUREMENT
    ecuCounter
    "16 bit counter incrementing exactly every 100us in XCP slave time"
    UWORD ecuCounter_
    COMPU_METHOD
    0
    0
    0
    65535
    ECU_ADDRESS 0x2E348
    PHYS_UNIT ""
    /begin IF_DATA XCP



    /end IF_DATA
/end MEASUREMENT"""

#@pytest.mark.skip
def test_notso_clean_ifdata1():
    pre = Preprocessor()
    res = pre.process(BASE_DIR / "notso_clean_ifdata.a2l")
    sections = res.if_data_sections
    assert len(sections) == 1
    sec = sections[0]
    #print(res)
    assert sec.start_line == (13, 4)
    assert sec.end_line == (16, 36)
    assert sec.data == '/begin IF_DATA XCP \n/begin DAQ_EVENT\nFIXED_EVENT_LIST EVENT 0x0\n        /end DAQ_EVENT  /end IF_DATA'
    assert res.a2l_data == '\n/begin MEASUREMENT \n    ecuCounter \n    "16 bit counter incrementing exactly every 100us in XCP slave time" \n    UWORD ecuCounter_\n    COMPU_METHOD \n    0 \n    0 \n    0 \n    65535 \n    ECU_ADDRESS 0x2E348 \n    PHYS_UNIT "" \n    /begin IF_DATA XCP \n\n\n                        /end IF_DATA'

#@pytest.mark.skip
def test_notso_clean_ifdata2():
    pre = Preprocessor()
    res = pre.process(BASE_DIR / "notso_clean_ifdata2.a2l")
    sections = res.if_data_sections
    assert len(sections) == 1
    sec = sections[0]
    #print(res)
    assert sec.start_line == (13, 4)
    assert sec.end_line == (16, 36)
    assert sec.data == '/begin IF_DATA XCP \n/begin DAQ_EVENT\nFIXED_EVENT_LIST EVENT 0x0\n        /end DAQ_EVENT  /end IF_DATA'
    assert res.a2l_data == '\n/begin MEASUREMENT \n    ecuCounter \n    "16 bit counter incrementing exactly every 100us in XCP slave time" \n    UWORD ecuCounter_\n    COMPU_METHOD \n    0 \n    0 \n    0 \n    65535 \n    ECU_ADDRESS 0x2E348 \n    PHYS_UNIT "" \n    /begin IF_DATA XCP \n\n\n                        /end IF_DATA'
