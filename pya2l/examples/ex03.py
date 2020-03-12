
from pya2l import DB
import pya2l.model as model

db = DB()
session = db.open_existing("ASAP2_Demo_V161")
measurements = session.query(model.Measurement).order_by(model.Measurement.name).all()
for m in measurements:
    print("{:48} {:12} 0x{:08x}".format(m.name, m.datatype, m.ecu_address.address))
