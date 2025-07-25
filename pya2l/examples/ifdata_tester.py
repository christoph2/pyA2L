import atexit
import json
import os
import sys
from pprint import pprint

import pya2l.a2lparser_ext as ext
from pya2l import DB
from pya2l.aml.ifdata_parser import IfDataParser


os.chdir(r"C:\csprojects\pyA2L\pya2l\examples")

db = DB()
# session = db.open_create("XCPsim2")
session = db.open_create("ASAP2_Demo_V161")

ifdp = IfDataParser(session)
# pprint(ifdp.root)

IFD0 = """/begin IF_DATA XCP
/begin SEGMENT 0x01 0x02 0x00 0x00 0x00
/begin CHECKSUM XCP_ADD_44 MAX_BLOCK_SIZE 0xFFFF EXTERNAL_FUNCTION "" /end CHECKSUM
/begin PAGE 0x01 ECU_ACCESS_WITH_XCP_ONLY XCP_READ_ACCESS_WITH_ECU_ONLY XCP_WRITE_ACCESS_NOT_ALLOWED /end PAGE
/begin PAGE 0x00 ECU_ACCESS_WITH_XCP_ONLY XCP_READ_ACCESS_WITH_ECU_ONLY XCP_WRITE_ACCESS_WITH_ECU_ONLY /end PAGE
/end SEGMENT
/end IF_DATA"""

pprint(ifdp.parse(IFD0))

IFD1 = """/begin IF_DATA XCP
      /begin PROTOCOL_LAYER
        0x0100
        0x07D0
        0x2710
        0x00
        0x00
        0x00
        0x00
        0x00
        0xA6
        0x28
        BYTE_ORDER_MSB_LAST
        ADDRESS_GRANULARITY_BYTE
        OPTIONAL_CMD GET_COMM_MODE_INFO
        OPTIONAL_CMD GET_ID
        OPTIONAL_CMD SET_MTA
        OPTIONAL_CMD UPLOAD
        OPTIONAL_CMD SHORT_UPLOAD
        OPTIONAL_CMD BUILD_CHECKSUM
        OPTIONAL_CMD TRANSPORT_LAYER_CMD
        OPTIONAL_CMD USER_CMD
        OPTIONAL_CMD DOWNLOAD
        OPTIONAL_CMD DOWNLOAD_NEXT
        OPTIONAL_CMD SHORT_DOWNLOAD
        OPTIONAL_CMD MODIFY_BITS
        OPTIONAL_CMD SET_CAL_PAGE
        OPTIONAL_CMD GET_CAL_PAGE
        OPTIONAL_CMD GET_PAG_PROCESSOR_INFO
        OPTIONAL_CMD GET_PAGE_INFO
        OPTIONAL_CMD SET_DAQ_PTR
        OPTIONAL_CMD WRITE_DAQ
        OPTIONAL_CMD SET_DAQ_LIST_MODE
        OPTIONAL_CMD GET_DAQ_LIST_MODE
        OPTIONAL_CMD START_STOP_DAQ_LIST
        OPTIONAL_CMD START_STOP_SYNCH
        OPTIONAL_CMD GET_DAQ_CLOCK
        OPTIONAL_CMD GET_DAQ_PROCESSOR_INFO
        OPTIONAL_CMD GET_DAQ_RESOLUTION_INFO
        OPTIONAL_CMD GET_DAQ_EVENT_INFO
        OPTIONAL_CMD FREE_DAQ
        OPTIONAL_CMD ALLOC_DAQ
        OPTIONAL_CMD ALLOC_ODT
        OPTIONAL_CMD ALLOC_ODT_ENTRY
        OPTIONAL_CMD PROGRAM_START
        OPTIONAL_CMD PROGRAM_CLEAR
        OPTIONAL_CMD PROGRAM
        OPTIONAL_CMD PROGRAM_RESET
        OPTIONAL_CMD PROGRAM_PREPARE
        COMMUNICATION_MODE_SUPPORTED BLOCK
          SLAVE
          MASTER
            0x2B
            0x00
      /end PROTOCOL_LAYER
      /begin PAG
        0x01
      /end PAG
      /begin PGM
        PGM_MODE_ABSOLUTE
        0x01
        0x08
      /end PGM
      /begin DAQ
        DYNAMIC
        0x00
        0x05
        0x00
        OPTIMISATION_TYPE_DEFAULT
        ADDRESS_EXTENSION_FREE
        IDENTIFICATION_FIELD_TYPE_ABSOLUTE
        GRANULARITY_ODT_ENTRY_SIZE_DAQ_BYTE
        0x07
        OVERLOAD_INDICATION_PID
        PRESCALER_SUPPORTED
        /begin TIMESTAMP_SUPPORTED
          0x03
          SIZE_WORD
          UNIT_1MS
        /end TIMESTAMP_SUPPORTED
        /begin EVENT
          "5ms_Task"
          "5ms_Task"
          0x00
          DAQ
          0x01
          0x05
          0x06
          0x00
        /end EVENT
        /begin EVENT
          "10ms_Task"
          "10ms_Tas"
          0x01
          DAQ
          0x01
          0x0A
          0x06
          0x00
        /end EVENT
        /begin EVENT
          "20ms_Task"
          "20ms_Tas"
          0x02
          DAQ
          0x01
          0x14
          0x06
          0x00
        /end EVENT
        /begin EVENT
          "40ms_Task"
          "40ms_Tas"
          0x03
          DAQ
          0x01
          0x28
          0x06
          0x00
        /end EVENT
        /begin EVENT
          "80ms_Task"
          "80ms_Tas"
          0x04
          DAQ
          0x01
          0x50
          0x06
          0x00
        /end EVENT
      /end DAQ
      /begin XCP_ON_CAN
        0x0100
        CAN_ID_MASTER 0x01E2
        CAN_ID_SLAVE 0x9BFC1010
        BAUDRATE 0x07A120
        SAMPLE_POINT 0x4B
        SAMPLE_RATE SINGLE
        BTL_CYCLES 0x08
        SJW 0x02
        SYNC_EDGE SINGLE
        MAX_DLC_REQUIRED
      /end XCP_ON_CAN
    /end IF_DATA
    /begin IF_DATA CANAPE_MODULE
    /end IF_DATA"""

pprint(ifdp.parse(IFD1))
