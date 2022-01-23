import sys

import pya2l.model as model
from pya2l import DB

db = DB()
session = db.open_create("ASAP2_Demo_V161")
db.export_a2l(sys.stdout)
