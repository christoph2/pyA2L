import re
from dataclasses import dataclass, field
from enum import IntEnum
from pprint import pprint
from typing import Any, List, Optional


class IfDataTokenType(IntEnum):
    NONE = 0
    IDENT = 1
    FLOAT = 2
    INT = 3
    COMMENT = 4
    STRING = 6
    BEGIN = 7
    END = 8
    WS = 9


@dataclass
class IfDataToken:
    type: IfDataTokenType
    value: Any


PAT_WS = re.compile(r"\s+")
PAT_BEGIN = re.compile("/begin")
PAT_END = re.compile("/end")

PAT_COMMENT = re.compile(r"(/\*.*?\*/)|(//.*?)")
PAT_STRING = re.compile(r'"[^"]*"')

PAT_FLOAT = re.compile(r"[+\-]?(\d+([.]\d*)?([eE][+\-]?\d+)?|[.]\d+([eE][+\-]?\d+)?)")

PAT_INT = re.compile(r"(0x[0-9a-fA-F]+)|([+\-]?[0-9]+)")
PAT_IDENT = re.compile(r"([a-zA-Z_][a-zA-Z_0-9.]*)\b")


EXPRESSIONS = [
    (IfDataTokenType.WS, PAT_WS),
    (IfDataTokenType.COMMENT, PAT_COMMENT),
    (IfDataTokenType.STRING, PAT_STRING),
    (IfDataTokenType.INT, PAT_INT),
    (IfDataTokenType.FLOAT, PAT_FLOAT),
    (IfDataTokenType.BEGIN, PAT_BEGIN),
    (IfDataTokenType.END, PAT_END),
    (IfDataTokenType.IDENT, PAT_IDENT),
]


class IfDataLexer:

    def __init__(self, section: str, skip_list: list[IfDataTokenType] = [IfDataTokenType.WS, IfDataTokenType.COMMENT]):
        self.section = section
        self.section_length = len(section)
        self.skip_list = skip_list
        self.pos = 0

    def run(self) -> List[IfDataToken]:
        result = []
        while self.pos < self.section_length:
            token = self.get_token()
            if token is not None:
                result.append(token)
        return result

    def get_token(self) -> Optional[IfDataToken]:
        token = None
        for code, expr in EXPRESSIONS:
            match = expr.match(self.section, self.pos)
            if match:
                self.pos += match.end() - match.start()
                text = match.group()
                if code in self.skip_list:
                    return None
                # print(code.name, text)
                return IfDataToken(code, text)
        print(f"Invalid char {self.section[self.pos]!r}")
        self.pos += 1
        return None


def ifdata_lexer(
    section: str, skip_list: list[IfDataTokenType] = [IfDataTokenType.WS, IfDataTokenType.COMMENT]
) -> List[IfDataToken]:
    length = len(section)
    pos = 0
    result = []

    while pos < length:
        found = False
        for code, expr in EXPRESSIONS:
            match = expr.match(section, pos)
            if match:
                pos += match.end() - match.start()
                if pos > 60:
                    print()
                text = match.group()
                if code in skip_list:
                    continue
                print(code.name, text)
                found = True
                result.append(IfDataToken(code, text))
                continue
        if not found:
            print(f"Invalid char {section[pos]!r}")
            pos += 1
    return result


SE = """/begin IF_DATA XCP
    /begin PAG
      /* MAX_SEGMENTS       */ 8
    /end PAG

    /begin XCP_ON_USB
      /* XCP on USB version */ 0x100
      /* Vendor ID          */ 0x58B
      /* Product ID         */ 0x7
      /* No of interface    */ 2
      HEADER_LEN_FILL_WORD

      /* OUT-EP for CMD and                                                 */
      /* STIM (additional USB Endpoints may also be specified)              */
      /begin OUT_EP_CMD_STIM
        /* Endpoint number */ 5
        /* transfer type   */ BULK_TRANSFER
        /* packet size     */ 64
        /* Polling interval*/ 0
        /* Message packing */ MESSAGE_PACKING_SINGLE
        /* Message alignm. */ ALIGNMENT_32_BIT
      /end OUT_EP_CMD_STIM

      /* IN-EP for RES/ERR,                                                 */
      /* DAQ (additional USB Endpoints may also be specified)               */
      /* and EV/SERV (if not specified otherwise)                           */
      /begin IN_EP_RESERR_DAQ_EVSERV
        /* Endpoint number */ 7
        /* transfer type   */ BULK_TRANSFER
        /* packet size     */ 64
        /* Polling interval*/ 0
        /* Message packing */ MESSAGE_PACKING_SINGLE
        /* Message alignm. */ ALIGNMENT_32_BIT
        RECOMMENDED_HOST_BUFSIZE 1
      /end IN_EP_RESERR_DAQ_EVSERV

      ALTERNATE_SETTING_NO 1
      INTERFACE_STRING_DESCRIPTOR "XCP Slave 0001"

      /begin IN_EP_ONLY_DAQ
        /* Endpoint number */ 8
        /* transfer type   */ BULK_TRANSFER
        /* packet size     */ 64
        /* Polling interval*/ 0
        /* Message packing */ MESSAGE_PACKING_SINGLE
        /* Message alignm. */ ALIGNMENT_32_BIT
        RECOMMENDED_HOST_BUFSIZE 16
      /end IN_EP_ONLY_DAQ

      /begin DAQ_LIST_USB_ENDPOINT
        /* DAQ-list        */ 0
        /* assigned EP     */ FIXED_IN 8
      /end DAQ_LIST_USB_ENDPOINT

      /begin DAQ_LIST_USB_ENDPOINT
        /* DAQ-list        */ 1
        /* assigned EP     */ FIXED_IN 8
      /end DAQ_LIST_USB_ENDPOINT

      /begin DAQ_LIST_USB_ENDPOINT
        /* DAQ-list        */ 2
        /* assigned EP     */ FIXED_IN 8
      /end DAQ_LIST_USB_ENDPOINT

      /*********** OVERRULE begins ***********/

      /begin PROTOCOL_LAYER
        /* XCP Version */ 0x100
        /* T1          */ 1000
        /* T2          */ 1000
        /* T3          */ 0
        /* T4          */ 0
        /* T5          */ 0
        /* T6          */ 0
        /* T7          */ 0
        /* MAX_CTO     */ 60
        /* MAX_DTO     */ 60
        BYTE_ORDER_MSB_LAST
        ADDRESS_GRANULARITY_BYTE

        OPTIONAL_CMD GET_ID
        OPTIONAL_CMD SET_MTA
        OPTIONAL_CMD UPLOAD
        OPTIONAL_CMD SHORT_UPLOAD
        OPTIONAL_CMD BUILD_CHECKSUM
        OPTIONAL_CMD DOWNLOAD_NEXT
        OPTIONAL_CMD COPY_CAL_PAGE
        OPTIONAL_CMD GET_DAQ_CLOCK

        COMMUNICATION_MODE_SUPPORTED    /* optional modes supported */
          BLOCK
            /* Block Mode for SLAVE  */ SLAVE
            /* Block Mode for MASTER */ MASTER
            /* MAX_BS                */   4
            /* MIN_ST unit is 100 us */   0
          /end PROTOCOL_LAYER

          /begin DAQ
        /* DAQ_CONFIG_TYPE        */ STATIC
        /* MAX_DAQ                */ 3
        /* MAX_EVENT_CHANNEL      */ 3
        /* MIN_DAQ                */ 0
        OPTIMISATION_TYPE_DEFAULT
        ADDRESS_EXTENSION_FREE
        IDENTIFICATION_FIELD_TYPE_ABSOLUTE
        GRANULARITY_ODT_ENTRY_SIZE_DAQ_BYTE
        /* MAX_ODT_ENTRY_SIZE_DAQ */ 4
        NO_OVERLOAD_INDICATION

        /begin TIMESTAMP_SUPPORTED
          /* TIMESTAMP_TICKS  */ 5120
          /* TIMESTAMP_SIZE   */ SIZE_DWORD
          /* RESOLUTION       */ UNIT_10NS
          /* TIMESTAMP_TYPE   */ TIMESTAMP_FIXED
        /end TIMESTAMP_SUPPORTED
        /begin DAQ_LIST
          /* DAQ_LIST_NUMBER */ 0
          DAQ_LIST_TYPE         DAQ
          MAX_ODT               4
          MAX_ODT_ENTRIES       30
          FIRST_PID  0
          EVENT_FIXED           0
        /end DAQ_LIST
        /begin DAQ_LIST
          /* DAQ_LIST_NUMBER */ 1
          DAQ_LIST_TYPE         DAQ
          MAX_ODT               4
          MAX_ODT_ENTRIES       30
          FIRST_PID  4
          EVENT_FIXED           1
        /end DAQ_LIST
        /begin DAQ_LIST
          /* DAQ_LIST_NUMBER */ 2
          DAQ_LIST_TYPE         DAQ
          MAX_ODT               4
          MAX_ODT_ENTRIES       30
          FIRST_PID  8
          EVENT_FIXED           2
        /end DAQ_LIST
        /begin EVENT
          /* name                 */ "segment synchronous"
          /* short name           */ "seg-sync"
          /* EVENT_CHANNEL_NUMBER */ 0
          /* Event type           */ DAQ
          /* MAX_DAQ_LIST         */ 1
          /* TIME_CYCLE           */ 0
          /* TIME_UNIT            */ 0
          /* PRIORITY             */ 7
        /end EVENT
        /begin EVENT
          /* name                 */ "10ms time synchronous"
          /* short name           */ "10ms"
          /* EVENT_CHANNEL_NUMBER */ 1
          /* Event type           */ DAQ
          /* MAX_DAQ_LIST         */ 1
          /* TIME_CYCLE           */ 10
          /* TIME_UNIT            */ 6
          /* PRIORITY             */ 6
        /end EVENT
        /begin EVENT
          /* name                 */ "100ms time synchronous"
          /* short name           */ "100ms"
          /* EVENT_CHANNEL_NUMBER */ 2
          /* Event type           */ DAQ
          /* MAX_DAQ_LIST         */ 1
          /* TIME_CYCLE           */ 100
          /* TIME_UNIT            */ 6
          /* PRIORITY             */ 5
        /end EVENT
      /end DAQ
      /*********** OVERRULE ends ***********/

    /end XCP_ON_USB
  /end IF_DATA
"""

idl = IfDataLexer(SE)
res = idl.run()
pprint(res)
