import re
import sys
import traceback
import typing
from collections import defaultdict
from os import unlink
from pathlib import Path
from time import perf_counter

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

import pya2l.a2lparser_ext as ext
from pya2l import classes, model
from pya2l.logger import Logger
from pya2l.utils import detect_encoding


IFD_HEADER = re.compile(r"/begin\s+IF_DATA\s+(\w+)", re.DOTALL | re.MULTILINE)

KW_MAP = {
    "A2ml": model.A2ml,
    "A2mlVersion": model.A2mlVersion,
    "AddrEpk": model.AddrEpk,
    "AddressType": model.AddressType,
    "AlignmentByte": model.AlignmentByte,
    "AlignmentFloat16Ieee": model.AlignmentFloat16Ieee,
    "AlignmentFloat32Ieee": model.AlignmentFloat32Ieee,
    "AlignmentFloat64Ieee": model.AlignmentFloat64Ieee,
    "AlignmentInt64": model.AlignmentInt64,
    "AlignmentLong": model.AlignmentLong,
    "AlignmentWord": model.AlignmentWord,
    "Annotation": model.Annotation,
    "AnnotationLabel": model.AnnotationLabel,
    "AnnotationOrigin": model.AnnotationOrigin,
    "AnnotationText": model.AnnotationText,
    "ArComponent": model.ArComponent,
    "ArPrototypeOf": model.ArPrototypeOf,
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
    "Blob": model.Blob,
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
    "ConsistentExchange": model.ConsistentExchange,
    "Conversion": model.Conversion,
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
    "Encoding": model.Encoding,
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
    "InputQuantity": model.InputQuantity,
    "Instance": model.Instance,
    "Layout": model.Layout,
    "LeftShift": model.LeftShift,
    "Limits": model.Limits,
    "LocMeasurement": model.LocMeasurement,
    "MapList": model.MapList,
    "MatrixDim": model.MatrixDim,
    "MaxGrad": model.MaxGrad,
    "MaxRefresh": model.MaxRefresh,
    "Measurement": model.Measurement,
    "MemoryLayout": model.MemoryLayout,
    "MemorySegment": model.MemorySegment,
    "ModCommon": model.ModCommon,
    "ModelLink": model.ModelLink,
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
    "Overwrite": model.Overwrite,
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
    "StaticAddressOffsets": model.StaticAddressOffsets,
    "StatusStringRef": model.StatusStringRef,
    "StepSize": model.StepSize,
    "SubFunction": model.SubFunction,
    "SubGroup": model.SubGroup,
    "Supplier": model.Supplier,
    "StructureComponent": model.StructureComponent,
    "SymbolTypeLink": model.SymbolTypeLink,
    "SymbolLink": model.SymbolLink,
    "SystemConstant": model.SystemConstant,
    "SRecLayout": model.SRecLayout,
    "TransformerInObjects": model.TransformerInObjects,
    "TransformerOutObjects": model.TransformerOutObjects,
    "Transformer": model.Transformer,
    "TypedefAxis": model.TypedefAxis,
    "TypedefBlob": model.TypedefBlob,
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


def make_zipper(kw) -> typing.Callable[[typing.Container[typing.Any]], dict[str, typing.Any]]:  # noqa: UP006
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
                    result = dict(zip([p.name for p in kw.__required_parameters__[:-1]], values))  # noqa: B905
                    result[MULT_COLUMN[table_name]] = mult_values
                    return result

        else:

            def zipper(values, mult_values: list[typing.Any]):
                # Standard case -- all scalar values.
                return dict(zip([p.name for p in kw.__required_parameters__], values))  # noqa: B905

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


def update_tuple_table(tuple_table, rows: list, columns: list) -> list:
    result = []
    for row in rows:
        result.append(tuple_table(**dict(zip(columns, row))))  # noqa: B905
    return result


def update_tables(session, tables):
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
        "VarForbiddenComb": (
            model.VarForbiddenComb,
            model.VarForbiddedCombPair,
            "pairs",
            "numberValuePairs",
            ("criterionName", "criterionValue"),
        ),
    }
    combinations = session.query(model.VarForbiddenComb).all()
    for table_type, name, values in tables:
        master_table, tuple_table, assoc, counter, columns = MAP[table_type]
        if table_type == "VarForbiddenComb":
            combi = combinations.pop(0)
            result = update_tuple_table(tuple_table, values, columns)
            session.add_all(result)
            setattr(master_table, counter, len(values))
            combi.pairs.extend(result)
            continue
        result = update_tuple_table(tuple_table, values, columns)
        session.add_all(result)
        inst = session.query(master_table).filter(master_table.name == name).first()
        if inst is not None:
            setattr(inst, counter, len(values))
            getattr(inst, assoc).extend(result)
            session.add(inst)


class A2LParser:
    def __init__(self) -> None:
        self.debug: bool = False
        self.logger: Logger = Logger("A2LDB", "INFO")

    def __del__(self) -> None:
        pass

    def close(self) -> None:
        pass

    def parse(
        self,
        file_name: str,
        encoding: str = "latin-1",
        in_memory: bool = False,
        local: bool = False,
        remove_existing: bool = False,
        loglevel: str = "INFO",
        progress_bar: bool = True,
    ) -> model.A2LDatabase:
        loglevel = loglevel.upper()
        effective_progress = progress_bar and sys.stderr.isatty() and loglevel not in ("ERROR", "CRITICAL")
        self.silent: bool = not effective_progress
        a2l_fn, db_fn = path_components(in_memory, file_name, local)
        if not in_memory:
            if remove_existing:
                try:
                    unlink(str(db_fn))
                except Exception:
                    pass  # nosec
            elif db_fn.exists():
                raise OSError(f"file {db_fn!r} already exists.")
        if not encoding:
            self.logger.info("Detecting encoding...")
            encoding = detect_encoding(file_name=a2l_fn)
        self.encoding = encoding
        start_time = perf_counter()
        self.db: model.A2LDatabase = model.A2LDatabase(str(db_fn), debug=self.debug)
        # self.db.session.commit()
        self.logger.info(f"Importing {a2l_fn!r} [{encoding}] ==> DB {db_fn!r}.")
        try:
            keyword_counter, values, tables, aml_data = ext.parse(str(a2l_fn), encoding, loglevel)
        except Exception as e:
            self.logger.error(f"Failed to parse {a2l_fn!r}: {e}")
            self.logger.error(traceback.format_exc())
            try:
                unlink(str(db_fn))
            except Exception:
                pass  # nosec
            raise
        aml_section = model.AMLSection()
        if aml_data:
            aml_section.text = aml_data.text
            aml_section.parsed = aml_data.parsed
        self.db.session.add(aml_section)
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
        self.progress_bar = Progress(*progress_columns, console=Console(stderr=True), disable=self.silent)
        if not self.silent:
            self.task = self.progress_bar.add_task("[blue]writing to DB...", total=keyword_counter)
        # Adaptive flush strategy: balance memory usage and performance across file sizes
        if keyword_counter < 10000:
            self.advance = 100  # Small files: flush often to limit session overhead
        elif keyword_counter < 100000:
            # Medium files: scale from 200 to 500 based on size
            self.advance = min(500, 200 + (keyword_counter - 10000) // 300)
        else:
            # Large files: use max of 1000 or 1% to avoid over-flushing
            self.advance = max(1000, keyword_counter // 100)
        fr = FakeRoot()
        with self.progress_bar:
            self.traverse(values, fr, None, False)
        self.db.session.commit()
        update_tables(self.db.session, tables)
        self.db.session.commit()
        self.logger.info(f"Done. Elapsed time [{perf_counter() - start_time:.2f}s].")
        return self.db

    def traverse(self, tree: typing.Any, parent: typing.Any, attr: str | None, multiple: bool, level: int = 0) -> None:
        self.counter += 1
        inst = None
        mult: list = []
        name = tree.get_name()

        if not self.silent and self.counter % self.advance == 0:
            self.db.session.flush()
            self.progress_bar.update(self.task, advance=self.advance)
            # db.session.commit()
        if name != "root":
            table = KW_MAP[name]
            zipper = ZIPPER_MAP[name]
            try:
                params = tree.parameters
            except UnicodeDecodeError as e:
                self.logger.error(f"UnicodeDecodeError reading parameters of {name!r}: {e}")
                params = {}
            mult = tree.multiple_values
            try:
                raw_if_data = tree.if_data
            except UnicodeDecodeError as exc:
                self.logger.warning(f"Failed to decode IF_DATA in {name!r} using encoding {self.encoding!r}: {exc}")
                raw_if_data = []
            if_data = self._decode_if_data_sections(raw_if_data)

            values = zipper(params, mult)
            if name not in {
                "ReadOnly",
                "GuardRails",
                "Discrete",
                "ReadWrite",
                "ConsistentExchange",
                "StaticRecordLayout",
                "StaticAddressOffsets",
            }:
                inst = table(**values)
                if if_data:
                    # print(parent, table, params, if_data)
                    if parent.if_data is None:
                        parent.if_data = []
                    for section in if_data:
                        ifd_section = model.IfData(raw=section)
                        parent.if_data.append(ifd_section)
                # db.session.add(inst)
            else:
                inst = True
            if multiple:
                if getattr(parent, attr) is None:
                    setattr(parent, attr, [inst])
                elif attr != "if_data":
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
            self.traverse(kw, inst, attr, mult, level + 1)
        if name not in ("root", "IfData") and not isinstance(inst, bool):
            self.db.session.add(inst)

    def _decode_if_data_sections(self, sections: typing.Any) -> list[str]:
        if not sections:
            return []
        encoding = getattr(self, "encoding", "latin-1")
        decoded = []
        for section in sections:
            if section is None:
                continue
            if isinstance(section, bytes):
                try:
                    decoded.append(section.decode(encoding))
                except UnicodeDecodeError:
                    decoded.append(section.decode(encoding, errors="replace"))
            else:
                decoded.append(section)
        return decoded


def enforce_suffix(pth: Path, suffix: str):
    """Path.with_suffix() works not as expected, if filename contains dots."""
    if not str(pth).endswith(suffix):
        return Path(str(pth) + suffix)
    return pth


def path_components(in_memory: bool, file_name: str, local=False):
    """
    Parameters
    ----------
    in_memory: bool

    file_name: str

    local: bool
    """

    db_fn = ""
    a2l_fn = ""

    file_path = Path(file_name)
    if in_memory:
        db_fn = ":memory:"
    else:
        if local:
            db_fn = enforce_suffix(Path(file_path.stem), ".a2ldb")
        else:
            db_fn = enforce_suffix((file_path.parent / file_path.stem), ".a2ldb")
    if not file_path.suffix:
        a2l_fn = enforce_suffix((file_path.parent / file_path.stem), ".a2l")
    else:
        a2l_fn = enforce_suffix((file_path.parent / file_path.stem), file_path.suffix)
    return (a2l_fn, db_fn)
