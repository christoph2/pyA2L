import atexit
import json
import os
import sys
from pprint import pprint

import pya2l.a2lparser_ext as ext
from pya2l import DB
from pya2l.aml.ifdata_parser import IfDataParser


os.chdir(r"C:\Users\HP\PycharmProjects\pyA2L\pya2l\examples")

db = DB()
# session = db.open_create("XCPsim2")
session = db.open_create("ASAP2_Demo_V161")

ifdp = IfDataParser(session)
# pprint(ifdp.root)

IFD = """/begin IF_DATA XCP
/begin SEGMENT 0x01 0x02 0x00 0x00 0x00
/begin CHECKSUM XCP_ADD_44 MAX_BLOCK_SIZE 0xFFFF EXTERNAL_FUNCTION "" /end CHECKSUM
/begin PAGE 0x01 ECU_ACCESS_WITH_XCP_ONLY XCP_READ_ACCESS_WITH_ECU_ONLY XCP_WRITE_ACCESS_NOT_ALLOWED /end PAGE
/begin PAGE 0x00 ECU_ACCESS_WITH_XCP_ONLY XCP_READ_ACCESS_WITH_ECU_ONLY XCP_WRITE_ACCESS_WITH_ECU_ONLY /end PAGE
/end SEGMENT
/end IF_DATA"""

print(ifdp.parse(IFD))
