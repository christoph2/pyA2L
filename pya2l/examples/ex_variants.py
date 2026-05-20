import sys
from pprint import pprint

from pya2l import DB
from pya2l.api.inspect import Project


db = DB()
session = db.open_create(sys.argv[1], loglevel="DEBUG")
prj = Project(session)

mod = prj.module[0]
pprint(mod.variant_coding)
