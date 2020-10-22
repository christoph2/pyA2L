#
# Just import an .a2l file, nothing more.
#
from pya2l import DB

db = DB()
session = db.import_a2l("ASAP2_Demo_V161.a2l")
