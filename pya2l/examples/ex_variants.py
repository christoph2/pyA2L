import sys

import pya2l.model as model
from pya2l import DB
from pya2l.api.inspect import Measurement
from pya2l.api.inspect import VariantCoding

db = DB()
session = db.open_create("variants")
vc = VariantCoding(session)

print(end="\n")
for name, combinations in vc.combinations.items():
    print(name)
    for combi in combinations:
        print(
            "{:30s} {:12s} {:}".format(
                str(combi.comb),
                combi.var_name or "N/A",
                "0x{:08x}".format(combi.address) if combi.address else "N/A",
            )
        )
    print(end="\n")
