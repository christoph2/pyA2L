
import sys

from pya2l import DB
import pya2l.model as model

db = DB()
session = db.open_create("ASAP2_Demo_V161")
db.export_a2l(sys.stdout)
