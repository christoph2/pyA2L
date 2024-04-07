from pya2l import DB
from pya2l import model

db = DB()
session = db.open_create("ASAP2_Demo_V161")
measurements = session.query(model.Measurement).order_by(model.Measurement.name).all()
for m in measurements:
    print("{:48} {:12} 0x{:08x}".format(m.name, m.datatype, m.ecu_address.address))
# print(dir(m))
ifd = model.IfData()
print(ifd)
print(dir(ifd))
