import os
import re
import typing
from collections import defaultdict
from pprint import pprint
from time import perf_counter

from rich.progress import BarColumn
from rich.progress import Progress
from rich.progress import SpinnerColumn
from rich.progress import TaskProgressColumn
from rich.progress import TimeElapsedColumn
from rich.progress import TimeRemainingColumn

import pya2l.a2lparser_ext as ext
from pya2l import classes
from pya2l import model

# from  .a2lparser_ext import A2LParser as A2LParser_ext

IFD_HEADER = re.compile(r"/begin\s+IF_DATA\s+(\w+)", re.DOTALL | re.MULTILINE)

KW_MAP = {
    "A2ml": model.A2ml,
    "A2mlVersion": model.A2mlVersion,
    "AddrEpk": model.AddrEpk,
    "AlignmentByte": model.AlignmentByte,
    "AlignmentFloat16Ieee": model.AlignmentFloat16Ieee,
    "AlignmentFloat32Ieee": model.AlignmentFloat32Ieee,
    "AlignmentFloat32Ieee": model.AlignmentFloat32Ieee,
    "AlignmentFloat64Ieee": model.AlignmentFloat64Ieee,
    "AlignmentInt64": model.AlignmentInt64,
    "AlignmentLong": model.AlignmentLong,
    "AlignmentWord": model.AlignmentWord,
    "Annotation": model.Annotation,
    "AnnotationLabel": model.AnnotationLabel,
    "AnnotationOrigin": model.AnnotationOrigin,
    "AnnotationText": model.AnnotationText,
    "ArraySize": model.ArraySize,
    "Asap2Version": model.Asap2Version,
    "AxisDescr": model.AxisDescr,
    "AxisPts": model.AxisPts,
    "AxisPtsRef": model.AxisPtsRef,
    "AxisPtsX": model.AxisPtsX,
    "AxisPtsY": model.AxisPtsY,
    "AxisPtsZ": model.AxisPtsZ,
    "AxisPts4": model.AxisPts4,
    "AxisPts5": model.AxisPts5,
    "AxisRescaleX": model.AxisRescaleX,
    "AxisRescaleY": model.AxisRescaleY,
    "AxisRescaleZ": model.AxisRescaleZ,
    "AxisRescale4": model.AxisRescale4,
    "AxisRescale5": model.AxisRescale5,
    "BitMask": model.BitMask,
    "BitOperation": model.BitOperation,
    "ByteOrder": model.ByteOrder,
    "CalibrationAccess": model.CalibrationAccess,
    "CalibrationHandle": model.CalibrationHandle,
    "CalibrationHandleText": model.CalibrationHandleText,
    "CalibrationMethod": model.CalibrationMethod,
    "Characteristic": model.Characteristic,
    "Coeffs": model.Coeffs,
    "CoeffsLinear": model.CoeffsLinear,
    "ComparisonQuantity": model.ComparisonQuantity,
    "CompuMethod": model.CompuMethod,
    "CompuTab": model.CompuTab,
    "CompuTabRef": model.CompuTabRef,
    "CompuVtab": model.CompuVtab,
    "CompuVtabRange": model.CompuVtabRange,
    "CpuType": model.CpuType,
    "CurveAxisRef": model.CurveAxisRef,
    "Customer": model.Customer,
    "CustomerNo": model.CustomerNo,
    "DataSize": model.DataSize,
    "DefCharacteristic": model.DefCharacteristic,
    "DefaultValue": model.DefaultValue,
    "DefaultValueNumeric": model.DefaultValueNumeric,
    "DependentCharacteristic": model.DependentCharacteristic,
    "Deposit": model.Deposit,
    "Discrete": model.Discrete,
    "DisplayIdentifier": model.DisplayIdentifier,
    "DistOpX": model.DistOpX,
    "DistOpY": model.DistOpY,
    "DistOpZ": model.DistOpZ,
    "DistOp4": model.DistOp4,
    "DistOp5": model.DistOp5,
    "Ecu": model.Ecu,
    "EcuAddress": model.EcuAddress,
    "EcuAddressExtension": model.EcuAddressExtension,
    "EcuCalibrationOffset": model.EcuCalibrationOffset,
    "Epk": model.Epk,
    "ErrorMask": model.ErrorMask,
    "ExtendedLimits": model.ExtendedLimits,
    "FixAxisPar": model.FixAxisPar,
    "FixAxisParDist": model.FixAxisParDist,
    "FixAxisParList": model.FixAxisParList,
    "FixNoAxisPtsX": model.FixNoAxisPtsX,
    "FixNoAxisPtsY": model.FixNoAxisPtsY,
    "FixNoAxisPtsZ": model.FixNoAxisPtsZ,
    "FixNoAxisPts4": model.FixNoAxisPts4,
    "FixNoAxisPts5": model.FixNoAxisPts5,
    "FncValues": model.FncValues,
    "Format": model.Format,
    "Formula": model.Formula,
    "FormulaInv": model.FormulaInv,
    "Frame": model.Frame,
    "FrameMeasurement": model.FrameMeasurement,
    "Function": model.Function,
    "FunctionList": model.FunctionList,
    "FunctionVersion": model.FunctionVersion,
    "Group": model.Group,
    "GuardRails": model.GuardRails,
    "Header": model.Header,
    "Identification": model.Identification,
    "IfData": model.IfData,
    "InMeasurement": model.InMeasurement,
    "Instance": model.Instance,
    "Layout": model.Layout,
    "LeftShift": model.LeftShift,
    "LocMeasurement": model.LocMeasurement,
    "MapList": model.MapList,
    "MatrixDim": model.MatrixDim,
    "MaxGrad": model.MaxGrad,
    "MaxRefresh": model.MaxRefresh,
    "Measurement": model.Measurement,
    "MemoryLayout": model.MemoryLayout,
    "MemorySegment": model.MemorySegment,
    "ModCommon": model.ModCommon,
    "ModPar": model.ModPar,
    "Module": model.Module,
    "Monotony": model.Monotony,
    "NoAxisPtsX": model.NoAxisPtsX,
    "NoAxisPtsY": model.NoAxisPtsY,
    "NoAxisPtsZ": model.NoAxisPtsZ,
    "NoAxisPts4": model.NoAxisPts4,
    "NoAxisPts5": model.NoAxisPts5,
    "NoOfInterfaces": model.NoOfInterfaces,
    "NoRescaleX": model.NoRescaleX,
    "NoRescaleY": model.NoRescaleY,
    "NoRescaleZ": model.NoRescaleZ,
    "NoRescale4": model.NoRescale4,
    "NoRescale5": model.NoRescale5,
    "Number": model.Number,
    "OffsetX": model.OffsetX,
    "OffsetY": model.OffsetY,
    "OffsetZ": model.OffsetZ,
    "Offset4": model.Offset4,
    "Offset5": model.Offset5,
    "OutMeasurement": model.OutMeasurement,
    "PhoneNo": model.PhoneNo,
    "PhysUnit": model.PhysUnit,
    "Project": model.Project,
    "ProjectNo": model.ProjectNo,
    "ReadOnly": model.ReadOnly,
    "ReadWrite": model.ReadWrite,
    "RecordLayout": model.RecordLayout,
    "RefCharacteristic": model.RefCharacteristic,
    "RefGroup": model.RefGroup,
    "RefMeasurement": model.RefMeasurement,
    "RefMemorySegment": model.RefMemorySegment,
    "RefUnit": model.RefUnit,
    "Reserved": model.Reserved,
    "RightShift": model.RightShift,
    "RipAddrW": model.RipAddrW,
    "RipAddrX": model.RipAddrX,
    "RipAddrY": model.RipAddrY,
    "RipAddrZ": model.RipAddrZ,
    "RipAddr4": model.RipAddr4,
    "RipAddr5": model.RipAddr5,
    "Root": model.Root,
    "ShiftOpX": model.ShiftOpX,
    "ShiftOpY": model.ShiftOpY,
    "ShiftOpZ": model.ShiftOpZ,
    "ShiftOp4": model.ShiftOp4,
    "ShiftOp5": model.ShiftOp5,
    "SignExtend": model.SignExtend,
    "SiExponents": model.SiExponents,
    "SrcAddrX": model.SrcAddrX,
    "SrcAddrY": model.SrcAddrY,
    "SrcAddrZ": model.SrcAddrZ,
    "SrcAddr4": model.SrcAddr4,
    "SrcAddr5": model.SrcAddr5,
    "StaticRecordLayout": model.StaticRecordLayout,
    "StatusStringRef": model.StatusStringRef,
    "StepSize": model.StepSize,
    "SubFunction": model.SubFunction,
    "SubGroup": model.SubGroup,
    "Supplier": model.Supplier,
    "StructureComponent": model.StructureComponent,
    "SymbolLink": model.SymbolLink,
    "SystemConstant": model.SystemConstant,
    "SRecLayout": model.SRecLayout,
    "TypedefCharacteristic": model.TypedefCharacteristic,
    "TypedefMeasurement": model.TypedefMeasurement,
    "TypedefStructure": model.TypedefStructure,
    "Unit": model.Unit,
    "UnitConversion": model.UnitConversion,
    "User": model.User,
    "UserRights": model.UserRights,
    "VarAddress": model.VarAddress,
    "VarCharacteristic": model.VarCharacteristic,
    "VarCriterion": model.VarCriterion,
    "VarForbiddenComb": model.VarForbiddenComb,
    "VarMeasurement": model.VarMeasurement,
    "VarNaming": model.VarNaming,
    "VarSelectionCharacteristic": model.VarSelectionCharacteristic,
    "VarSeparator": model.VarSeparator,
    "VariantCoding": model.VariantCoding,
    "Version": model.Version,
    "Virtual": model.Virtual,
    "VirtualCharacteristic": model.VirtualCharacteristic,
}


def assoc_name(param) -> str:
    return param.keyword_name.lower()


def lower_first(text: str) -> str:
    return f"{text[0].lower()}{text[1:]}"


def make_zipper(kw) -> typing.Callable[[typing.Container[typing.Any]], typing.Dict[str, typing.Any]]:
    if hasattr(kw, "__required_parameters__"):
        table_name = kw.__tablename__.upper()
        if table_name == "IFDATA":
            table_name = "IF_DATA"  # Needs to be fixed elsewhere.
        klass = classes.KEYWORD_MAP.get(table_name)
        has_multiple = [a for a in klass.attrs if len(a) > 2 and a[2] is classes.MULTIPLE]
        if has_multiple:
            if len(klass.attrs) == 1:

                def zipper(values, mult_values: list[typing.Any]):
                    # There's a single parameter of list type.
                    result = {}
                    result[lower_first(klass.attrs[0][1])] = mult_values
                    return result

            else:
                MULT_COLUMN = {
                    "VAR_CHARACTERISTIC": "criterionName",
                    "DEPENDENT_CHARACTERISTIC": "characteristic_id",
                    "VIRTUAL_CHARACTERISTIC": "characteristic_id",
                    "VAR_CRITERION": "value",
                }

                def zipper(values, mult_values: list[typing.Any]):
                    # Scalars, the final value is a list.
                    result = dict(zip([p.name for p in kw.__required_parameters__[:-1]], values))
                    result[MULT_COLUMN[table_name]] = mult_values
                    return result

        else:

            def zipper(values, mult_values: list[typing.Any]):
                # Standard case -- all scalar values.
                return dict(zip([p.name for p in kw.__required_parameters__], values))

    else:

        def zipper(values, mult_values: list[typing.Any]):
            # No values at all (Currently DISCRETE, GUARD_RAILS, and READ_ONLY).
            return {}

    return zipper


ZIPPER_MAP = {}
ASSOC_MAP = defaultdict(dict)

for k, v in KW_MAP.items():
    ZIPPER_MAP[k] = make_zipper(v)
    if hasattr(v, "__optional_elements__") and v.__optional_elements__:
        for p in v.__optional_elements__:
            ASSOC_MAP[k][p.name] = (assoc_name(p), p.multiple)
ASSOC_MAP["root"]["Asap2Version"] = ("asap2version", False)
ASSOC_MAP["root"]["Project"] = ("project", False)


class FakeRoot:
    asap2version = None
    project = None

    def __getattribute__(self, name):
        return True


def update_tables(session, parser):
    MAP = {
        "CompuTab": (model.CompuTab, model.CompuTabPair, "pairs", "numberValuePairs", ("inVal", "outVal")),
        "CompuVtab": (model.CompuVtab, model.CompuVtabPair, "pairs", "numberValuePairs", ("inVal", "outVal")),
        "CompuVtabRange": (
            model.CompuVtabRange,
            model.CompuVtabRangeTriple,
            "triples",
            "numberValueTriples",
            ("inValMin", "inValMax", "outVal"),
        ),
    }

    for table_type, name, values in p.get_tables():
        print("TBL", table_type, name)
        t0, t1, assoc, counter, columns = MAP[table_type]
        result = []
        for row in values:
            result.append(t1(**dict(zip(columns, row))))
        session.add_all(result)
        inst = session.query(t0).filter(t0.name == name).first()
        setattr(inst, counter, len(values))
        getattr(inst, assoc).extend(result)
        session.add(inst)


class A2LParser:
    def __init__(self, prepro_result):
        self.parser = ext.A2LParser(prepro_result)

    def parse(self, filename: str, encoding: str = "latin-1", dbname: str = ":memory:"):
        self.debug = False
        start = perf_counter()
        self.db = model.A2LDatabase(dbname, debug=self.debug)
        print(f"Parsing: '{filename}' [{encoding}] ==> DB '{dbname}'.")
        self.parser.parse(filename, encoding)
        values = self.parser.get_values()
        print(f"Keyword counter: {self.parser.keyword_counter} -- Elapsed Time: {perf_counter() - start:.2f}s.", end="\n\n")
        self.counter = 0

        progress_columns = (
            SpinnerColumn(style="white"),
            "[progress.description]{task.description}",
            BarColumn(),
            TaskProgressColumn(),
            "Elapsed:",
            TimeElapsedColumn(),
            "Remaining:",
            TimeRemainingColumn(),
        )
        self.progress_bar = Progress(*progress_columns)
        self.task = self.progress_bar.add_task("[blue]writing to DB...", total=self.parser.keyword_counter)
        self.advance = self.parser.keyword_counter // 100 if self.parser.keyword_counter >= 100 else 1
        fr = FakeRoot()
        with self.progress_bar:
            self.traverse(values, fr, None, False)
        self.db.session.commit()
        self.db.close()
        print()
        return (self.db, ())

    def traverse(self, tree, parent, attr, multiple, level=0):
        self.counter += 1
        inst = None
        mult: list = []
        space = "    " * level
        name = tree.get_name()

        # print("TABLE ==> ", name, parent, multiple)
        if self.counter % self.advance == 0:
            self.db.session.flush()
            self.progress_bar.update(self.task, advance=self.advance)
            # db.session.commit()
        if name != "root":
            table = KW_MAP[name]
            zipper = ZIPPER_MAP[name]
            try:
                params = tree.parameters

            except UnicodeDecodeError as e:
                print(e, "***", tree, name, table)
                params = {}
                # if_data = []
            mult = tree.get_multiple_values()
            if_data = tree.if_data

            values = zipper(params, mult)
            if name not in ("ReadOnly", "GuardRails", "Discrete"):
                inst = table(**values)

                if if_data:
                    #    print(parent, table, params, if_data)
                    if parent.if_data is None:
                        parent.if_data = []

                    ma = IFD_HEADER.search(if_data)
                    if ma:
                        ifd_name = ma.group(1)

                    ifd = model.IfData(raw=if_data)
                    parent.if_data.append(ifd)
                # db.session.add(inst)
            else:
                inst = True
            # if name == "DependentCharacteristic":
            #     print(values, inst)
            if multiple:
                if getattr(parent, attr) is None:
                    setattr(parent, attr, [inst])
                else:
                    getattr(parent, attr).append(inst)
            else:
                setattr(parent, attr, inst)
        for kw in tree.get_keywords():
            if name != "root":
                elem = ASSOC_MAP[name][kw.get_name()]
                attr, mult = elem
            else:
                inst = FakeRoot()
                attr = "fake"
                mult = False
                an = "root"
            self.traverse(kw, inst, attr, mult, level + 1)
        if name != "root" and not isinstance(inst, bool):
            self.db.session.add(inst)
