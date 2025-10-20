from pya2l import DB, model


db = DB()
session = db.open_create("ASAP2_Demo_V161")
measurements = session.query(model.Measurement).order_by(model.Measurement.name).all()
for m in measurements:
    print(f"{m.name:48} {m.datatype:12} 0x{m.ecu_address.address:08x}")
# print(dir(m))
ifd = model.IfData()
print(ifd)
print(dir(ifd))
