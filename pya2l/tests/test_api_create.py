import pytest
import sqlalchemy
from sqlalchemy.orm import sessionmaker

import pya2l.model as model
from pya2l.api.create import (
    AxisPtsCreator,
    CharacteristicCreator,
    CompuMethodCreator,
    Creator,
    FunctionCreator,
    GroupCreator,
    MeasurementCreator,
    ModuleCreator,
    ProjectCreator,
    RecordLayoutCreator,
)


@pytest.fixture
def session():
    engine = sqlalchemy.create_engine("sqlite:///:memory:")
    model.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def test_module(session):
    module = model.Module(name="TEST_MODULE", longIdentifier="Test Module")
    session.add(module)
    session.commit()
    return module


class TestCreator:
    def test_commit(self, session):
        creator = Creator(session)
        obj = model.Unit(name="TEST_UNIT", longIdentifier="Test Unit")
        session.add(obj)
        creator.commit()

        unit = session.query(model.Unit).filter(model.Unit.name == "TEST_UNIT").first()
        assert unit is not None
        assert unit.longIdentifier == "Test Unit"

    def test_rollback(self, session):
        creator = Creator(session)
        obj = model.Unit(name="TEST_UNIT", longIdentifier="Test Unit")
        session.add(obj)
        creator.rollback()

        unit = session.query(model.Unit).filter(model.Unit.name == "TEST_UNIT").first()
        assert unit is None


class TestProjectCreator:
    def test_create_project(self, session):
        creator = ProjectCreator(session)
        project = creator.create_project("TEST_PROJ", "Test Project")
        creator.commit()
        assert project.name == "TEST_PROJ"
        assert project.longIdentifier == "Test Project"

    def test_add_header_and_project_no(self, session):
        creator = ProjectCreator(session)
        project = creator.create_project("TEST_PROJ", "Test Project")
        header = creator.add_header(project, "Test Comment")
        creator.add_project_no(header, "12345")
        creator.commit()
        assert project.header.comment == "Test Comment"
        assert project.header.project_no.projectNumber == "12345"


class TestModuleCreator:
    def test_create_module(self, session):
        creator = ModuleCreator(session)
        project = model.Project(name="P", longIdentifier="L")
        session.add(project)
        module = creator.create_module("MOD", "Long", project=project)
        creator.commit()
        assert module.name == "MOD"
        assert module in project.module

    def test_add_unit(self, session, test_module):
        creator = ModuleCreator(session)
        unit = creator.add_unit(test_module, "UNIT", "Long", "Display", type_str="DERIVED", ref_unit="REF")
        creator.commit()
        assert unit.name == "UNIT"
        assert unit.display == "Display"
        assert unit.ref_unit.unit == "REF"

    def test_add_compu_tab(self, session, test_module):
        creator = ModuleCreator(session)
        tab = creator.add_compu_tab(test_module, "TAB", "Long", "TAB_INTP", [(0.0, 0.0), (1.0, 10.0)], default_numeric=5.0)
        creator.commit()
        assert tab.name == "TAB"
        assert len(tab.pairs) == 2
        assert tab.default_value_numeric.display_value == 5.0

    def test_add_compu_vtab(self, session, test_module):
        creator = ModuleCreator(session)
        tab = creator.add_compu_vtab(test_module, "VTAB", "Long", "TAB_VERB", [(0.0, "OFF"), (1.0, "ON")], default_value="UNKNOWN")
        creator.commit()
        assert tab.name == "VTAB"
        assert len(tab.pairs) == 2
        assert tab.default_value.display_string == "UNKNOWN"

    def test_add_compu_vtab_range(self, session, test_module):
        creator = ModuleCreator(session)
        tab = creator.add_compu_vtab_range(
            test_module, "VTAB_RANGE", "Long", [(0.0, 10.0, "LOW"), (11.0, 20.0, "HIGH")], default_value="OUT"
        )
        creator.commit()
        assert tab.name == "VTAB_RANGE"
        assert len(tab.triples) == 2
        assert tab.default_value.display_string == "OUT"

    def test_add_group(self, session, test_module):
        creator = ModuleCreator(session)
        group = creator.add_group(test_module, "GROUP", "Long", root=True)
        creator.commit()
        assert group.groupName == "GROUP"
        assert group.module == test_module
        assert group.root is not None

    def test_add_sub_group(self, session, test_module):
        creator = ModuleCreator(session)
        group = creator.add_group(test_module, "PARENT", "Long")
        sub_group = creator.add_sub_group(group, ["CHILD"])
        creator.commit()
        assert sub_group.identifier[0] == "CHILD"
        assert sub_group.group == group

    @pytest.mark.skip
    def test_add_if_data(self, session, test_module):
        creator = ModuleCreator(session)
        ifd = creator.add_if_data(test_module, "TEXT")
        creator.commit()
        assert test_module.if_data[0].ifDataText == "TEXT"

    def test_add_mod_common(self, session, test_module):
        creator = ModuleCreator(session)
        mc = creator.add_mod_common(test_module, comment="Comment", byte_order="MSB_LAST", data_size=16)
        creator.commit()
        assert mc.comment == "Comment"
        assert mc.byte_order.byteOrder == "MSB_LAST"
        assert mc.data_size.size == 16

    def test_add_mod_par(self, session, test_module):
        creator = ModuleCreator(session)
        mp = creator.add_mod_par(test_module, comment="Comment", cpu_type="Pentium", customer="Me")
        creator.commit()
        assert mp.comment == "Comment"
        assert mp.cpu_type.cPU == "Pentium"
        assert mp.customer.customer == "Me"

    def test_add_typedef_structure(self, session, test_module):
        creator = ModuleCreator(session)
        ts = creator.add_typedef_structure(test_module, "STRUCT", "Long", 100)
        creator.commit()
        assert ts.name == "STRUCT"
        assert ts.module == test_module

    def test_add_structure_component(self, session, test_module):
        creator = ModuleCreator(session)
        ts = creator.add_typedef_structure(test_module, "STRUCT", "Long", 100)
        sc = creator.add_structure_component(ts, "COMP", "UINT8", 0)
        creator.commit()
        assert sc.name == "COMP"
        assert ts.structure_component[0] == sc


class TestCompuMethodCreator:
    def test_create_compu_method(self, session, test_module):
        creator = CompuMethodCreator(session)
        cm = creator.create_compu_method("CM", "Long", "IDENTICAL", "%d", "V", module_name="TEST_MODULE")
        creator.commit()
        assert cm.name == "CM"
        assert test_module.compu_method[0] == cm

    def test_add_coeffs_linear(self, session):
        creator = CompuMethodCreator(session)
        cm = model.CompuMethod(name="CM", longIdentifier="L", conversionType="LINEAR", format="%d", unit="V")
        session.add(cm)
        coeffs = creator.add_coeffs_linear(cm, 2.0, 1.0)
        creator.commit()
        assert coeffs.a == 2.0
        assert coeffs.compu_method == cm

    def test_add_coeffs(self, session):
        creator = CompuMethodCreator(session)
        cm = model.CompuMethod(name="CM", longIdentifier="L", conversionType="RAT_FUNC", format="%d", unit="V")
        session.add(cm)
        coeffs = creator.add_coeffs(cm, 1, 2, 3, 4, 5, 6)
        creator.commit()
        assert coeffs.a == 1
        assert coeffs.f == 6

    def test_add_compu_tab_ref(self, session):
        creator = CompuMethodCreator(session)
        cm = model.CompuMethod(name="CM", longIdentifier="L", conversionType="TAB_REF", format="%d", unit="V")
        session.add(cm)
        ctr = creator.add_compu_tab_ref(cm, "TAB")
        creator.commit()
        assert ctr.conversionTable == "TAB"
        assert ctr.compu_method == cm

    def test_add_formula(self, session):
        creator = CompuMethodCreator(session)
        cm = model.CompuMethod(name="CM", longIdentifier="L", conversionType="FORMULA", format="%d", unit="V")
        session.add(cm)
        f = creator.add_formula(cm, "X1", formula_inv="X1")
        creator.commit()
        assert f.f_x == "X1"
        assert f.formula_inv.g_x == "X1"
        assert f.compu_method == cm

    def test_add_ref_unit(self, session):
        creator = CompuMethodCreator(session)
        cm = model.CompuMethod(name="CM", longIdentifier="L", conversionType="IDENTICAL", format="%d", unit="V")
        session.add(cm)
        ru = creator.add_ref_unit(cm, "UNIT")
        creator.commit()
        assert ru.unit == "UNIT"
        assert ru.compu_method == cm

    def test_add_status_string_ref(self, session):
        creator = CompuMethodCreator(session)
        cm = model.CompuMethod(name="CM", longIdentifier="L", conversionType="IDENTICAL", format="%d", unit="V")
        session.add(cm)
        ssr = creator.add_status_string_ref(cm, "TAB")
        creator.commit()
        assert ssr.conversionTable == "TAB"
        assert ssr.compu_method == cm


class TestMeasurementCreator:
    def test_create_measurement(self, session, test_module):
        creator = MeasurementCreator(session)
        meas = creator.create_measurement("M", "L", "UBYTE", "CM", 1, 0, 0, 100, module_name="TEST_MODULE")
        creator.commit()
        assert meas.name == "M"
        assert test_module.measurement[0] == meas

    def test_add_bit_operation(self, session):
        creator = MeasurementCreator(session)
        meas = model.Measurement(
            name="M", longIdentifier="L", datatype="UBYTE", conversion="CM", resolution=1, accuracy=0, lowerLimit=0, upperLimit=100
        )
        session.add(meas)
        bit_op = creator.add_bit_operation(meas, left_shift=2, sign_extend=True)
        creator.commit()
        assert bit_op.left_shift.bitcount == 2
        assert bit_op.sign_extend is not None

    def test_add_array_size(self, session):
        creator = MeasurementCreator(session)
        meas = model.Measurement(
            name="M", longIdentifier="L", datatype="UBYTE", conversion="CM", resolution=1, accuracy=0, lowerLimit=0, upperLimit=100
        )
        session.add(meas)
        asize = creator.add_array_size(meas, 10)
        creator.commit()
        assert asize.number == 10
        assert asize.measurement == meas

    def test_add_ecu_address(self, session):
        creator = MeasurementCreator(session)
        meas = model.Measurement(
            name="M", longIdentifier="L", datatype="UBYTE", conversion="CM", resolution=1, accuracy=0, lowerLimit=0, upperLimit=100
        )
        session.add(meas)
        addr = creator.add_ecu_address(meas, 0x1234)
        creator.commit()
        assert addr.address == 0x1234
        assert addr.measurement == meas

    def test_add_matrix_dim(self, session):
        creator = MeasurementCreator(session)
        meas = model.Measurement(
            name="M", longIdentifier="L", datatype="UBYTE", conversion="CM", resolution=1, accuracy=0, lowerLimit=0, upperLimit=100
        )
        session.add(meas)
        md = creator.add_matrix_dim(meas, 2, 3, 4)
        creator.commit()
        assert md.numbers[0] == 2
        assert md.numbers[1] == 3
        assert md.numbers[2] == 4
        assert md.measurement == meas

    def test_add_phys_unit(self, session):
        creator = MeasurementCreator(session)
        meas = model.Measurement(
            name="M", longIdentifier="L", datatype="UBYTE", conversion="CM", resolution=1, accuracy=0, lowerLimit=0, upperLimit=100
        )
        session.add(meas)
        pu = creator.add_phys_unit(meas, "V")
        creator.commit()
        assert pu.unit == "V"
        assert pu.measurement == meas

    def test_add_format(self, session):
        creator = MeasurementCreator(session)
        meas = model.Measurement(
            name="M", longIdentifier="L", datatype="UBYTE", conversion="CM", resolution=1, accuracy=0, lowerLimit=0, upperLimit=100
        )
        session.add(meas)
        fmt = creator.add_format(meas, "%d")
        creator.commit()
        assert fmt.formatString == "%d"
        assert fmt.measurement == meas

    def test_add_symbol_link(self, session):
        creator = MeasurementCreator(session)
        meas = model.Measurement(
            name="M", longIdentifier="L", datatype="UBYTE", conversion="CM", resolution=1, accuracy=0, lowerLimit=0, upperLimit=100
        )
        session.add(meas)
        sl = creator.add_symbol_link(meas, "SYM", 0)
        creator.commit()
        assert sl.symbolName == "SYM"
        assert sl.measurement == meas

    def test_add_virtual(self, session):
        creator = MeasurementCreator(session)
        meas = model.Measurement(
            name="M", longIdentifier="L", datatype="UBYTE", conversion="CM", resolution=1, accuracy=0, lowerLimit=0, upperLimit=100
        )
        session.add(meas)
        v = creator.add_virtual(meas, ["M1"])
        creator.commit()
        assert v.measuringChannel[0] == "M1"
        assert v.measurement == meas


class TestAxisPtsCreator:
    def test_create_axis_pts(self, session, test_module):
        creator = AxisPtsCreator(session)
        ap = creator.create_axis_pts("AP", "L", 0x1000, "IQ", "RL", 0, "CM", 10, 0, 100, module_name="TEST_MODULE")
        creator.commit()
        assert ap.name == "AP"
        assert test_module.axis_pts[0] == ap

    def test_add_step_size(self, session):
        creator = AxisPtsCreator(session)
        ap = model.AxisPts(
            name="AP",
            longIdentifier="L",
            address=0,
            inputQuantity="IQ",
            depositAttr="RL",
            maxDiff=0,
            conversion="CM",
            maxAxisPoints=10,
            lowerLimit=0,
            upperLimit=100,
        )
        session.add(ap)
        # We need to add record layout and other dependencies if they are validated by SQLAlchemy
        # But here the error seems to be due to how StepSize is added or linked
        ss = creator.add_step_size(ap, 0.5)
        creator.commit()
        assert ss.stepSize == 0.5
        # Use relationship to verify
        assert ap.step_size == ss

    def test_add_byte_order(self, session):
        creator = AxisPtsCreator(session)
        ap = model.AxisPts(
            name="AP",
            longIdentifier="L",
            address=0,
            inputQuantity="IQ",
            depositAttr="RL",
            maxDiff=0,
            conversion="CM",
            maxAxisPoints=10,
            lowerLimit=0,
            upperLimit=100,
        )
        session.add(ap)
        bo = creator.add_byte_order(ap, "MSB_LAST")
        creator.commit()
        assert bo.byteOrder == "MSB_LAST"
        assert ap.byte_order == bo

    def test_add_monotony(self, session):
        creator = AxisPtsCreator(session)
        ap = model.AxisPts(
            name="AP",
            longIdentifier="L",
            address=0,
            inputQuantity="IQ",
            depositAttr="RL",
            maxDiff=0,
            conversion="CM",
            maxAxisPoints=10,
            lowerLimit=0,
            upperLimit=100,
        )
        session.add(ap)
        mon = creator.add_monotony(ap, "MON_INCREASE")
        creator.commit()
        assert mon.monotony == "MON_INCREASE"
        assert ap.monotony == mon


class TestCharacteristicCreator:
    def test_create_characteristic(self, session, test_module):
        creator = CharacteristicCreator(session)
        char = creator.create_characteristic("C", "L", "VALUE", 0x1000, "RL", 0, "CM", 0, 100, module_name="TEST_MODULE")
        creator.commit()
        assert char.name == "C"
        assert test_module.characteristic[0] == char

    def test_add_axis_descr(self, session):
        creator = CharacteristicCreator(session)
        char = model.Characteristic(
            name="C",
            longIdentifier="L",
            type="VALUE",
            address=0,
            deposit="RL",
            maxDiff=0,
            conversion="CM",
            lowerLimit=0,
            upperLimit=100,
        )
        session.add(char)
        axis = creator.add_axis_descr(char, "STD_AXIS", "IQ", "CM", 10, 0, 100)
        creator.commit()
        assert axis.attribute == "STD_AXIS"
        assert char.axis_descr[0] == axis

    def test_add_dependent_characteristic(self, session):
        creator = CharacteristicCreator(session)
        char = model.Characteristic(
            name="C",
            longIdentifier="L",
            type="VALUE",
            address=0,
            deposit="RL",
            maxDiff=0,
            conversion="CM",
            lowerLimit=0,
            upperLimit=100,
        )
        session.add(char)
        dc = creator.add_dependent_characteristic(char, "X1", ["C2"])
        creator.commit()
        assert dc.formula == "X1"
        assert dc.characteristic_id[0] == "C2"

    def test_add_virtual_characteristic(self, session):
        creator = CharacteristicCreator(session)
        char = model.Characteristic(
            name="C",
            longIdentifier="L",
            type="VALUE",
            address=0,
            deposit="RL",
            maxDiff=0,
            conversion="CM",
            lowerLimit=0,
            upperLimit=100,
        )
        session.add(char)
        vc = creator.add_virtual_characteristic(char, "X1", ["C2"])
        creator.commit()
        assert vc.formula == "X1"
        assert vc.characteristic_id[0] == "C2"


class TestFunctionCreator:
    def test_create_function(self, session, test_module):
        creator = FunctionCreator(session)
        fnc = creator.create_function("F", "L", module_name="TEST_MODULE")
        creator.commit()
        assert fnc.name == "F"
        assert fnc.module == test_module

    def test_add_def_characteristic(self, session):
        creator = FunctionCreator(session)
        fnc = model.Function(name="F", longIdentifier="L")
        session.add(fnc)
        dc = creator.add_def_characteristic(fnc, ["C1", "C2"])
        creator.commit()
        assert dc.identifier[0] == "C1"
        assert fnc.def_characteristic.identifier[0] == "C1"


class TestGroupCreator:
    def test_create_group(self, session, test_module):
        creator = GroupCreator(session)
        grp = creator.create_group("G", "L", module_name="TEST_MODULE")
        creator.commit()
        assert grp.groupName == "G"
        assert grp.module == test_module

    def test_add_ref_measurement(self, session):
        creator = GroupCreator(session)
        grp = model.Group(groupName="G", groupLongIdentifier="L")
        session.add(grp)
        rm = creator.add_ref_measurement(grp, ["M1"])
        creator.commit()
        assert rm.identifier[0] == "M1"
        assert grp.ref_measurement.identifier[0] == "M1"


class TestRecordLayoutCreator:
    def test_create_record_layout(self, session, test_module):
        creator = RecordLayoutCreator(session)
        rl = creator.create_record_layout("RL", module_name="TEST_MODULE")
        creator.commit()
        assert rl.name == "RL"
        assert rl.module == test_module

    def test_add_fnc_values(self, session):
        creator = RecordLayoutCreator(session)
        rl = model.RecordLayout(name="RL")
        session.add(rl)
        fv = creator.add_fnc_values(rl, 1, "UBYTE", index_mode="COLUMN_DIR", address_type="DIRECT")
        creator.commit()
        assert fv.position == 1
        assert fv.datatype == "UBYTE"
        assert fv.indexMode == "COLUMN_DIR"
        assert fv.addresstype == "DIRECT"
        assert fv.record_layout == rl

    def test_add_axis_pts_x(self, session):
        creator = RecordLayoutCreator(session)
        rl = model.RecordLayout(name="RL")
        session.add(rl)
        apx = creator.add_axis_pts_x(rl, 1, "UBYTE", index_incr="INDEX_INCR", addressing="DIRECT")
        creator.commit()
        assert apx.position == 1
        assert apx.indexIncr == "INDEX_INCR"
        assert apx.addressing == "DIRECT"

    def test_add_no_axis_pts_x(self, session):
        creator = RecordLayoutCreator(session)
        rl = model.RecordLayout(name="RL")
        session.add(rl)
        napx = creator.add_no_axis_pts_x(rl, 1, "UBYTE")
        creator.commit()
        assert napx.position == 1
        assert napx.datatype == "UBYTE"

    def test_add_fix_no_axis_pts_x(self, session):
        creator = RecordLayoutCreator(session)
        rl = model.RecordLayout(name="RL")
        session.add(rl)
        fnapx = creator.add_fix_no_axis_pts_x(rl, 5)
        creator.commit()
        assert fnapx.numberOfAxisPoints == 5
