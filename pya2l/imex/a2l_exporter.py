#!/usr/bin/env python

"""
A2L exporter: standalone implementation.

Reads a pyA2L a2ldb (A2LDatabase) and emits A2L-like text.
Robust against missing/empty IF_DATA sections.
"""

from __future__ import annotations

import argparse
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, List, Optional, TextIO, Tuple, Union

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import selectinload

import pya2l.model as model
from pya2l.model import A2LDatabase


logger = logging.getLogger(__name__)


@dataclass
class ExporterConfig:
    db_path: Path
    out_path: Path
    module_name: str | None
    loglevel: str = "INFO"


def setup_logging(level: str) -> None:
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(level=numeric, format="%(levelname)s: %(message)s")


def open_database(db_path: Path, loglevel: str = "INFO") -> A2LDatabase:
    db = A2LDatabase(str(db_path), debug=False, logLevel=loglevel)
    try:
        db.session.setup_ifdata_parser(loglevel)
    except Exception:
        logging.getLogger(__name__).debug("Initializing IfData parser failed.", exc_info=True)
    return db


def safe_get(obj: Any, attr: str) -> Any:
    """Safe getattr that returns None on errors."""
    try:
        return getattr(obj, attr)
    except Exception:
        return None


def write_lines(out, lines: Iterable[str]) -> None:
    for ln in lines:
        out.write(f"{ln}\n")


def write_raw_ifdata(out, ifdata_list: list[Any] | None) -> None:
    """Append existing IF_DATA raw blocks unchanged."""
    if not ifdata_list:
        return
    for ifd in ifdata_list:
        raw = safe_get(ifd, "raw") or ""
        if raw.strip():
            out.write("\n")
            out.write(raw.strip())
            out.write("\n")


def write_symbol_link(out, symbol_link_obj: Any | None, logger: logging.Logger) -> None:
    if not symbol_link_obj:
        return
    name = safe_get(symbol_link_obj, "symbolName")
    offset = safe_get(symbol_link_obj, "offset")
    if name is None and offset is None:
        return
    if offset is None:
        logger.warning("SymbolLink %r missing offset; using 0 as fallback.", name)
        offset = 0
    out.write("      SYMBOL_LINK\n")
    out.write(f'        "{name or ""}"  /* symbolName */\n')
    out.write(f"        {offset}  /* offset */\n")


def write_annotation(out, annotation_assoc: list[Any] | None) -> None:
    if not annotation_assoc:
        return
    for a in annotation_assoc:
        out.write("    /begin ANNOTATION\n")
        lbl = safe_get(a, "annotation_label")
        if lbl and safe_get(lbl, "label"):
            out.write(f'      ANNOTATION_LABEL\n        "{lbl.label}"  /* label */\n')
        ori = safe_get(a, "annotation_origin")
        if ori and safe_get(ori, "origin"):
            out.write(f'      ANNOTATION_ORIGIN\n        "{ori.origin}"  /* origin */\n')
        txt = safe_get(a, "annotation_text")
        if txt and getattr(txt, "_text", None):
            out.write("      /begin ANNOTATION_TEXT\n")
            for line in txt._text:
                # line.text expected
                out.write(f'        "{line.text}"\n')
            out.write("      /end ANNOTATION_TEXT\n")
        out.write("    /end ANNOTATION\n")


def write_function_list(out, function_list_obj: Any | None) -> None:
    if not function_list_obj:
        return
    names = getattr(function_list_obj, "name", None)
    if not names:
        return
    out.write("    /begin FUNCTION_LIST\n")
    out.write("      " + " ".join(str(x) for x in names) + "\n")
    out.write("    /end FUNCTION_LIST\n")


def write_matrix_dim(out, matrix_dim_obj: Any | None) -> None:
    if not matrix_dim_obj:
        return
    nums = getattr(matrix_dim_obj, "numbers", None)
    if not nums:
        return
    out.write("    MATRIX_DIM\n")
    out.write("      " + " ".join(str(x) for x in nums) + "\n")


# Block writer: AxisPts
def write_axis_pts(out, axis_pts_list: list[Any] | None) -> None:
    if not axis_pts_list:
        return
    for ap in axis_pts_list:
        out.write("    /begin AXIS_PTS\n")
        out.write(f"      {ap.name}  /* name */\n")
        out.write(f'      "{safe_get(ap, "longIdentifier") or ""}"  /* longIdentifier */\n')
        out.write(f"      {safe_get(ap, 'address') or 0}  /* address */\n")
        out.write(f"      {safe_get(ap, 'inputQuantity') or '-'}  /* inputQuantity */\n")
        out.write(f"      {safe_get(ap, 'depositAttr') or '-'}  /* depositAttr */\n")
        out.write(f"      {safe_get(ap, 'maxDiff') or 0}  /* maxDiff */\n")
        out.write(f"      {safe_get(ap, 'conversion') or '-'}  /* conversion */\n")
        out.write(f"      {safe_get(ap, 'maxAxisPoints') or 0}  /* maxAxisPoints */\n")
        out.write(f"      {safe_get(ap, 'lowerLimit') or 0}  /* lowerLimit */\n")
        out.write(f"      {safe_get(ap, 'upperLimit') or 0}  /* upperLimit */\n")
        write_annotation(out, safe_get(ap, "annotation"))
        bo = safe_get(ap, "byte_order")
        if bo and safe_get(bo, "byteOrder"):
            out.write("      BYTE_ORDER\n")
            out.write(f"        {bo.byteOrder}  /* byteOrder */\n")
        ca = safe_get(ap, "calibration_access")
        if ca and safe_get(ca, "type"):
            out.write("      CALIBRATION_ACCESS\n")
            out.write(f"        {ca.type}  /* type */\n")
        dep = safe_get(ap, "deposit")
        if dep and safe_get(dep, "mode"):
            out.write("      DEPOSIT\n")
            out.write(f"        {dep.mode}  /* mode */\n")
        di = safe_get(ap, "display_identifier")
        if di and safe_get(di, "display_name"):
            out.write("      DISPLAY_IDENTIFIER\n")
            out.write(f"        {di.display_name}  /* display_name */\n")
        ecu_ext = safe_get(ap, "ecu_address_extension")
        if ecu_ext and safe_get(ecu_ext, "extension") is not None:
            out.write("      ECU_ADDRESS_EXTENSION\n")
            out.write(f"        {ecu_ext.extension}  /* extension */\n")
        ext_limits = safe_get(ap, "extended_limits")
        if ext_limits and safe_get(ext_limits, "lowerLimit") is not None and safe_get(ext_limits, "upperLimit") is not None:
            out.write("      EXTENDED_LIMITS\n")
            out.write(f"        {ext_limits.lowerLimit}  /* lowerLimit */\n")
            out.write(f"        {ext_limits.upperLimit}  /* upperLimit */\n")
        fmt = safe_get(ap, "format")
        if fmt and safe_get(fmt, "formatString"):
            out.write("      FORMAT\n")
            out.write(f'        "{fmt.formatString}"  /* formatString */\n')
        write_function_list(out, safe_get(ap, "function_list"))
        if safe_get(ap, "guard_rails"):
            out.write("      GUARD_RAILS\n")
        write_raw_ifdata(out, safe_get(ap, "if_data"))
        mr = safe_get(ap, "max_refresh")
        if mr and safe_get(mr, "scalingUnit") is not None and safe_get(mr, "rate") is not None:
            out.write("      MAX_REFRESH\n")
            out.write(f"        {mr.scalingUnit}  /* scalingUnit */\n")
            out.write(f"        {mr.rate}  /* rate */\n")
        ml = safe_get(ap, "model_link")
        if ml and safe_get(ml, "modelLink"):
            out.write("      MODEL_LINK\n")
            out.write(f'        "{ml.modelLink}"  /* modelLink */\n')
        if safe_get(ap, "monotony"):
            out.write("      MONOTONY\n")
            out.write(f"        {ap.monotony.monotony}  /* monotony */\n")
        if safe_get(ap, "phys_unit") and safe_get(ap.phys_unit, "unit"):
            out.write("      PHYS_UNIT\n")
            out.write(f'        "{ap.phys_unit.unit}"  /* unit */\n')
        if safe_get(ap, "read_only"):
            out.write("      READ_ONLY\n")
        if safe_get(ap, "ref_memory_segment") and safe_get(ap.ref_memory_segment, "name"):
            out.write("      REF_MEMORY_SEGMENT\n")
            out.write(f"        {ap.ref_memory_segment.name}  /* name */\n")
        if safe_get(ap, "step_size"):
            out.write("      STEP_SIZE\n")
            out.write(f"        {ap.step_size.stepSize}  /* stepSize */\n")
        write_symbol_link(out, safe_get(ap, "symbol_link"), logger)
        out.write("    /end AXIS_PTS\n\n")


def write_characteristics(out, char_list: list[Any] | None) -> None:
    if not char_list:
        return
    for ch in char_list:
        out.write("    /begin CHARACTERISTIC\n")
        out.write(f"      {ch.name}  /* name */\n")
        out.write(f'      "{safe_get(ch, "longIdentifier") or ""}"  /* longIdentifier */\n')
        out.write(f"      {safe_get(ch, 'type') or '-'}  /* type */\n")
        out.write(f"      {safe_get(ch, 'address') or 0}  /* address */\n")
        out.write(f"      {safe_get(ch, 'deposit') or '-'}  /* deposit */\n")
        out.write(f"      {safe_get(ch, 'maxDiff') or 0}  /* maxDiff */\n")
        out.write(f"      {safe_get(ch, 'conversion') or '-'}  /* conversion */\n")
        out.write(f"      {safe_get(ch, 'lowerLimit') or 0}  /* lowerLimit */\n")
        out.write(f"      {safe_get(ch, 'upperLimit') or 0}  /* upperLimit */\n")
        write_annotation(out, safe_get(ch, "annotation"))
        # axis_descr (condensed)
        for ad in safe_get(ch, "axis_descr") or []:
            out.write("      /begin AXIS_DESCR\n")
            out.write(f"        {ad.attribute}  /* attribute */\n")
            out.write(f"        {ad.inputQuantity}  /* inputQuantity */\n")
            out.write(f"        {ad.conversion}  /* conversion */\n")
            out.write(f"        {ad.maxAxisPoints}  /* maxAxisPoints */\n")
            out.write(f"        {ad.lowerLimit}  /* lowerLimit */\n")
            out.write(f"        {ad.upperLimit}  /* upperLimit */\n")
            write_annotation(out, safe_get(ad, "annotation"))
            apr = safe_get(ad, "axis_pts_ref")
            if apr and safe_get(apr, "axisPoints"):
                out.write("        AXIS_PTS_REF\n")
                out.write(f"          {apr.axisPoints}  /* axisPoints */\n")
            write_raw_ifdata(out, safe_get(ad, "if_data"))
            out.write("      /end AXIS_DESCR\n")
        # simple optional blocks
        if safe_get(ch, "bit_mask"):
            out.write("      BIT_MASK\n")
            out.write(f"        {ch.bit_mask.mask}  /* mask */\n")
        if safe_get(ch, "byte_order"):
            bo = ch.byte_order
            out.write("      BYTE_ORDER\n")
            out.write(f"        {bo.byteOrder}  /* byteOrder */\n")
        ca = safe_get(ch, "calibration_access")
        if ca and safe_get(ca, "type"):
            out.write("      CALIBRATION_ACCESS\n")
            out.write(f"        {ca.type}  /* type */\n")
        cq = safe_get(ch, "comparison_quantity")
        if cq and safe_get(cq, "name"):
            out.write("      COMPARISON_QUANTITY\n")
            out.write(f"        {cq.name}  /* name */\n")
        dc = safe_get(ch, "dependent_characteristic")
        if dc and safe_get(dc, "characteristicList"):
            out.write("      /begin DEPENDENT_CHARACTERISTIC\n")
            out.write(f'        "{dc.formula}"  /* formula */\n')
            for dep_ch in dc.characteristicList:
                out.write(f"        {dep_ch}\n")
            out.write("      /end DEPENDENT_CHARACTERISTIC\n")
        if safe_get(ch, "discrete"):
            out.write("      DISCRETE\n")
        di = safe_get(ch, "display_identifier")
        if di and safe_get(di, "display_name"):
            out.write("      DISPLAY_IDENTIFIER\n")
            out.write(f"        {di.display_name}  /* display_name */\n")
        ecu_ext = safe_get(ch, "ecu_address_extension")
        if ecu_ext and safe_get(ecu_ext, "extension") is not None:
            out.write("      ECU_ADDRESS_EXTENSION\n")
            out.write(f"        {ecu_ext.extension}  /* extension */\n")
        enc = safe_get(ch, "encoding")
        if enc and safe_get(enc, "encodingName"):
            out.write("      ENCODING\n")
            out.write(f'        "{enc.encodingName}"  /* encodingName */\n')
        ext_limits = safe_get(ch, "extended_limits")
        if ext_limits and safe_get(ext_limits, "lowerLimit") is not None and safe_get(ext_limits, "upperLimit") is not None:
            out.write("      EXTENDED_LIMITS\n")
            out.write(f"        {ext_limits.lowerLimit}  /* lowerLimit */\n")
            out.write(f"        {ext_limits.upperLimit}  /* upperLimit */\n")
        fmt = safe_get(ch, "format")
        if fmt and safe_get(fmt, "formatString"):
            out.write("      FORMAT\n")
            out.write(f'        "{fmt.formatString}"  /* formatString */\n')
        write_function_list(out, safe_get(ch, "function_list"))
        if safe_get(ch, "guard_rails"):
            out.write("      GUARD_RAILS\n")
        write_raw_ifdata(out, safe_get(ch, "if_data"))
        write_matrix_dim(out, safe_get(ch, "matrix_dim"))
        if safe_get(ch, "max_refresh"):
            mr = ch.max_refresh
            out.write("      MAX_REFRESH\n")
            out.write(f"        {mr.scalingUnit}  /* scalingUnit */\n")
            out.write(f"        {mr.rate}  /* rate */\n")
        ml = safe_get(ch, "model_link")
        if ml and safe_get(ml, "modelLink"):
            out.write("      MODEL_LINK\n")
            out.write(f'        "{ml.modelLink}"  /* modelLink */\n')
        num = safe_get(ch, "number")
        if num and safe_get(num, "number") is not None:
            out.write("      NUMBER\n")
            out.write(f"        {num.number}  /* number */\n")
        if safe_get(ch, "phys_unit") and safe_get(ch.phys_unit, "unit"):
            out.write("      PHYS_UNIT\n")
            out.write(f'        "{ch.phys_unit.unit}"  /* unit */\n')
        if safe_get(ch, "read_only"):
            out.write("      READ_ONLY\n")
        if safe_get(ch, "ref_memory_segment") and safe_get(ch.ref_memory_segment, "name"):
            out.write("      REF_MEMORY_SEGMENT\n")
            out.write(f"        {ch.ref_memory_segment.name}  /* name */\n")
        if safe_get(ch, "step_size"):
            out.write("      STEP_SIZE\n")
            out.write(f"        {ch.step_size.stepSize}  /* stepSize */\n")
        write_symbol_link(out, safe_get(ch, "symbol_link"), logger)
        vc = safe_get(ch, "virtual_characteristic")
        if vc and safe_get(vc, "formula"):
            out.write("      /begin VIRTUAL_CHARACTERISTIC\n")
            out.write(f'        "{vc.formula}"  /* formula */\n')
            if safe_get(vc, "characteristicList"):
                for virt_ch in vc.characteristicList:
                    out.write(f"        {virt_ch}\n")
            out.write("      /end VIRTUAL_CHARACTERISTIC\n")
        out.write("    /end CHARACTERISTIC\n\n")


def write_compu_methods(out, compu_list: list[Any] | None) -> None:
    if not compu_list:
        return
    for cm in compu_list:
        out.write("    /begin COMPU_METHOD\n")
        out.write(f"      {cm.name}  /* name */\n")
        out.write(f'      "{safe_get(cm, "longIdentifier") or ""}"  /* longIdentifier */\n')
        out.write(f"      {safe_get(cm, 'conversionType') or '-'}  /* conversionType */\n")
        out.write(f'      "{safe_get(cm, "format") or ""}"  /* format */\n')
        out.write(f'      "{safe_get(cm, "unit") or ""}"  /* unit */\n')
        if safe_get(cm, "coeffs"):
            c = cm.coeffs
            out.write("      COEFFS\n")
            out.write(f"        {c.a}  /* a */\n")
            out.write(f"        {c.b}  /* b */\n")
            out.write(f"        {c.c}  /* c */\n")
            out.write(f"        {c.d}  /* d */\n")
            out.write(f"        {c.e}  /* e */\n")
            out.write(f"        {c.f}  /* f */\n")
        if safe_get(cm, "coeffs_linear"):
            cl = cm.coeffs_linear
            out.write("      COEFFS_LINEAR\n")
            out.write(f"        {cl.a}  /* a */\n")
            out.write(f"        {cl.b}  /* b */\n")
        if safe_get(cm, "compu_tab_ref"):
            ctr = cm.compu_tab_ref
            out.write("      COMPU_TAB_REF\n")
            out.write(f"        {ctr.conversionTable}  /* conversionTable */\n")
        if safe_get(cm, "formula"):
            f = cm.formula
            out.write("      /begin FORMULA\n")
            out.write(f'        "{f.f_x}"  /* f_x */\n')
            if safe_get(f, "formula_inv") and safe_get(f.formula_inv, "g_x"):
                out.write("        FORMULA_INV\n")
                out.write(f'          "{f.formula_inv.g_x}"  /* g_x */\n')
            out.write("      /end FORMULA\n")
        if safe_get(cm, "ref_unit"):
            ru = cm.ref_unit
            out.write("      REF_UNIT\n")
            out.write(f"        {ru.unit}  /* unit */\n")
        if safe_get(cm, "status_string_ref"):
            ssr = cm.status_string_ref
            out.write("      STATUS_STRING_REF\n")
            out.write(f"        {ssr.conversionTable}  /* conversionTable */\n")
        out.write("    /end COMPU_METHOD\n\n")


def write_compu_tabs(out, tabs: list[Any] | None) -> None:
    if not tabs:
        return
    for t in tabs:
        # detect type by attributes
        if hasattr(t, "numberValuePairs"):
            out.write("    /begin COMPU_TAB\n")
            out.write(f"      {t.name}  /* name */\n")
            out.write(f'      "{safe_get(t, "longIdentifier") or ""}"  /* longIdentifier */\n')
            out.write(f"      {t.conversionType}  /* conversionType */\n")
            out.write(f"      {t.numberValuePairs}  /* numberValuePairs */\n")
            dv = safe_get(t, "default_value")
            if dv and safe_get(dv, "display_string"):
                out.write("      DEFAULT_VALUE\n")
                out.write(f'        "{dv.display_string}"  /* display_string */\n')
            dvn = safe_get(t, "default_value_numeric")
            if dvn and safe_get(dvn, "display_value") is not None:
                out.write("      DEFAULT_VALUE_NUMERIC\n")
                out.write(f"        {dvn.display_value}  /* display_value */\n")
            out.write("    /end COMPU_TAB\n\n")
        elif hasattr(t, "numberValueTriples"):
            out.write("    /begin COMPU_VTAB_RANGE\n")
            out.write(f"      {t.name}  /* name */\n")
            out.write(f'      "{safe_get(t, "longIdentifier") or ""}"  /* longIdentifier */\n')
            out.write(f"      {t.numberValueTriples}  /* numberValueTriples */\n")
            dv = safe_get(t, "default_value")
            if dv and safe_get(dv, "display_string"):
                out.write("      DEFAULT_VALUE\n")
                out.write(f'        "{dv.display_string}"  /* display_string */\n')
            out.write("    /end COMPU_VTAB_RANGE\n\n")
        else:
            out.write("    /begin COMPU_VTAB\n")
            out.write(f"      {t.name}  /* name */\n")
            out.write(f"      {safe_get(t, 'longIdentifier') or ''}   /* longIdentifier */\n")
            out.write(f"      {t.conversionType}  /* conversionType */\n")
            out.write(f"      {t.numberValuePairs}  /* numberValuePairs */\n")
            dv = safe_get(t, "default_value")
            if dv and safe_get(dv, "display_string"):
                out.write("      DEFAULT_VALUE\n")
                out.write(f'        "{dv.display_string}"  /* display_string */\n')
            out.write("    /end COMPU_VTAB\n\n")


def write_frames(out, frame_list: list[Any] | None) -> None:
    if not frame_list:
        return
    for f in frame_list:
        out.write("    /begin FRAME\n")
        out.write(f"      {f.name}  /* name */\n")
        out.write(f'      "{safe_get(f, "longIdentifier") or ""}"  /* longIdentifier */\n')
        out.write(f"      {safe_get(f, 'scalingUnit') or 0}  /* scalingUnit */\n")
        out.write(f"      {safe_get(f, 'rate') or 0}  /* rate */\n")
        fm = safe_get(f, "frame_measurement")
        if fm and safe_get(fm, "identifier"):
            out.write("      FRAME_MEASUREMENT\n")
            out.write("        " + " ".join(str(x) for x in fm.identifier) + "\n")
        write_raw_ifdata(out, safe_get(f, "if_data"))
        out.write("    /end FRAME\n\n")


def write_functions(out, func_list: list[Any] | None) -> None:
    if not func_list:
        return
    for fn in func_list:
        out.write("    /begin FUNCTION\n")
        out.write(f"      {fn.name}  /* name */\n")
        out.write(f'      "{safe_get(fn, "longIdentifier") or ""}"  /* longIdentifier */\n')
        write_annotation(out, safe_get(fn, "annotation"))
        ar_comp = safe_get(fn, "ar_component")
        if ar_comp and safe_get(ar_comp, "componentType"):
            out.write("      AR_COMPONENT\n")
            out.write(f"        {ar_comp.componentType}  /* componentType */\n")
        def_char = safe_get(fn, "def_characteristic")
        if def_char and safe_get(def_char, "identifier"):
            out.write("      /begin DEF_CHARACTERISTIC\n")
            out.write("        " + " ".join(str(x) for x in def_char.identifier) + "\n")
            out.write("      /end DEF_CHARACTERISTIC\n")
        fv = safe_get(fn, "function_version")
        if fv and safe_get(fv, "versionIdentifier"):
            out.write("      FUNCTION_VERSION\n")
            out.write(f'        "{fv.versionIdentifier}"  /* versionIdentifier */\n')
        write_raw_ifdata(out, safe_get(fn, "if_data"))
        for tag, attr in (
            ("IN_MEASUREMENT", "in_measurement"),
            ("LOC_MEASUREMENT", "loc_measurement"),
            ("OUT_MEASUREMENT", "out_measurement"),
        ):
            ent = safe_get(fn, attr)
            if ent and safe_get(ent, "identifier"):
                out.write(f"      /begin {tag}\n")
                out.write("        " + " ".join(str(x) for x in ent.identifier) + "\n")
                out.write(f"      /end {tag}\n")
        rc = safe_get(fn, "ref_characteristic")
        if rc and safe_get(rc, "identifier"):
            out.write("      /begin REF_CHARACTERISTIC\n")
            out.write("        " + " ".join(str(x) for x in rc.identifier) + "\n")
            out.write("      /end REF_CHARACTERISTIC\n")
        sf = safe_get(fn, "sub_function")
        if sf and safe_get(sf, "identifier"):
            out.write("      /begin SUB_FUNCTION\n")
            out.write("        " + " ".join(str(x) for x in sf.identifier) + "\n")
            out.write("      /end SUB_FUNCTION\n")
        out.write("    /end FUNCTION\n\n")


def write_groups(out, group_list: list[Any] | None) -> None:
    if not group_list:
        return
    for g in group_list:
        out.write("    /begin GROUP\n")
        out.write(f"      {g.groupName}  /* groupName */\n")
        out.write(f'      "{safe_get(g, "groupLongIdentifier") or ""}"  /* groupLongIdentifier */\n')
        write_annotation(out, safe_get(g, "annotation"))
        write_function_list(out, safe_get(g, "function_list"))
        write_raw_ifdata(out, safe_get(g, "if_data"))
        rc = safe_get(g, "ref_characteristic")
        if rc and safe_get(rc, "identifier"):
            out.write("      /begin REF_CHARACTERISTIC\n")
            out.write("        " + " ".join(str(x) for x in rc.identifier) + "\n")
            out.write("      /end REF_CHARACTERISTIC\n")
        rm = safe_get(g, "ref_measurement")
        if rm and safe_get(rm, "identifier"):
            out.write("      /begin REF_MEASUREMENT\n")
            out.write("        " + " ".join(str(x) for x in rm.identifier) + "\n")
            out.write("      /end REF_MEASUREMENT\n")
        if safe_get(g, "root"):
            out.write("      ROOT\n")
        sub = safe_get(g, "sub_group")
        if sub and safe_get(sub, "identifier"):
            out.write("      /begin SUB_GROUP\n")
            out.write("        " + " ".join(str(x) for x in sub.identifier) + "\n")
            out.write("      /end SUB_GROUP\n")
        out.write("    /end GROUP\n\n")


def write_instances(out, instance_list: list[Any] | None) -> None:
    if not instance_list:
        return
    for inst in instance_list:
        out.write("    /begin INSTANCE\n")
        out.write(f"      {inst.name}  /* name */\n")
        out.write(f'      "{safe_get(inst, "longIdentifier") or ""}"  /* longIdentifier */\n')
        out.write(f"      {safe_get(inst, 'typeName') or '-'}  /* typeName */\n")
        out.write(f"      {safe_get(inst, 'address') or 0}  /* address */\n")
        addr_type = safe_get(inst, "address_type")
        if addr_type and safe_get(addr_type, "addrType"):
            out.write("      ADDRESS_TYPE\n")
            out.write(f"        {addr_type.addrType}  /* addrType */\n")
        write_annotation(out, safe_get(inst, "annotation"))
        ca = safe_get(inst, "calibration_access")
        if ca and safe_get(ca, "type"):
            out.write("      CALIBRATION_ACCESS\n")
            out.write(f"        {ca.type}  /* type */\n")
        di = safe_get(inst, "display_identifier")
        if di and safe_get(di, "display_name"):
            out.write("      DISPLAY_IDENTIFIER\n")
            out.write(f"        {di.display_name}  /* display_name */\n")
        ecu_ext = safe_get(inst, "ecu_address_extension")
        if ecu_ext and safe_get(ecu_ext, "extension") is not None:
            out.write("      ECU_ADDRESS_EXTENSION\n")
            out.write(f"        {ecu_ext.extension}  /* extension */\n")
        write_raw_ifdata(out, safe_get(inst, "if_data"))
        write_matrix_dim(out, safe_get(inst, "matrix_dim"))
        mr = safe_get(inst, "max_refresh")
        if mr and safe_get(mr, "scalingUnit") is not None and safe_get(mr, "rate") is not None:
            out.write("      MAX_REFRESH\n")
            out.write(f"        {mr.scalingUnit}  /* scalingUnit */\n")
            out.write(f"        {mr.rate}  /* rate */\n")
        ml = safe_get(inst, "model_link")
        if ml and safe_get(ml, "modelLink"):
            out.write("      MODEL_LINK\n")
            out.write(f'        "{ml.modelLink}"  /* modelLink */\n')
        num = safe_get(inst, "number")
        if num and safe_get(num, "number") is not None:
            out.write("      NUMBER\n")
            out.write(f"        {num.number}  /* number */\n")
        if safe_get(inst, "read_only"):
            out.write("      READ_ONLY\n")
        write_symbol_link(out, safe_get(inst, "symbol_link"), logger)
        out.write("    /end INSTANCE\n\n")


def _min_passthrough_lookup(module: Any) -> dict[str, float]:
    """Build lookup of conversion name -> min passthrough (from table inVals)."""
    tables: dict[str, Any] = {}
    for collection_name in ("compu_tab", "compu_vtab", "compu_vtab_range"):
        for tbl in safe_get(module, collection_name) or []:
            name = safe_get(tbl, "name")
            if name:
                tables[name] = tbl

    def _min_from_table(tbl: Any | None) -> float | None:
        if tbl is None:
            return None
        values: list[float] = []
        entries = safe_get(tbl, "pairs") or safe_get(tbl, "triples") or []
        for entry in entries:
            candidate = safe_get(entry, "inValMin")
            if candidate is None:
                candidate = safe_get(entry, "inVal")
            if candidate is not None:
                try:
                    values.append(float(candidate))
                except Exception:
                    continue
        return min(values) if values else None

    lookup: dict[str, float] = {}
    for cm in safe_get(module, "compu_method") or []:
        ref = safe_get(cm, "compu_tab_ref")
        tab_name = safe_get(ref, "conversionTable") if ref else None
        if not tab_name:
            continue
        min_val = _min_from_table(tables.get(tab_name))
        if min_val is not None and safe_get(cm, "name"):
            lookup[cm.name] = min_val
    return lookup


def write_measurements(out, measurement_list: list[Any] | None, min_passthrough: dict[str, float] | None = None) -> None:
    if not measurement_list:
        return
    min_passthrough = min_passthrough or {}
    for m in measurement_list:
        out.write("    /begin MEASUREMENT\n")
        out.write(f"      {m.name}  /* name */\n")
        out.write(f'      "{safe_get(m, "longIdentifier") or ""}"  /* longIdentifier */\n')
        out.write(f"      {safe_get(m, 'datatype') or '-'}  /* datatype */\n")
        out.write(f"      {safe_get(m, 'conversion') or '-'}  /* conversion */\n")
        out.write(f"      {safe_get(m, 'resolution') or 0}  /* resolution */\n")
        out.write(f"      {safe_get(m, 'accuracy') or 0}  /* accuracy */\n")
        out.write(f"      {safe_get(m, 'lowerLimit') or 0}  /* lowerLimit */\n")
        out.write(f"      {safe_get(m, 'upperLimit') or 0}  /* upperLimit */\n")
        addr_type = safe_get(m, "address_type")
        if addr_type and safe_get(addr_type, "addrType"):
            out.write("      ADDRESS_TYPE\n")
            out.write(f"        {addr_type.addrType}  /* addrType */\n")
        write_annotation(out, safe_get(m, "annotation"))
        arr = safe_get(m, "array_size")
        if arr and safe_get(arr, "number"):
            out.write("      ARRAY_SIZE\n")
            out.write(f"        {arr.number}  /* number */\n")
        bm = safe_get(m, "bit_mask")
        if bm and safe_get(bm, "mask") is not None:
            out.write("      BIT_MASK\n")
            out.write(f"        {bm.mask}  /* mask */\n")
        bo_obj = safe_get(m, "bit_operation")
        if bo_obj:
            out.write("      /begin BIT_OPERATION\n")
            if safe_get(bo_obj, "left_shift"):
                ls = bo_obj.left_shift
                out.write("        LEFT_SHIFT\n")
                out.write(f"          {ls.bitcount}  /* bitcount */\n")
            if safe_get(bo_obj, "right_shift"):
                rs = bo_obj.right_shift
                out.write("        RIGHT_SHIFT\n")
                out.write(f"          {rs.bitcount}  /* bitcount */\n")
            if safe_get(bo_obj, "sign_extend"):
                out.write("        SIGN_EXTEND\n")
            out.write("      /end BIT_OPERATION\n")
        byte_order = safe_get(m, "byte_order")
        if byte_order and safe_get(byte_order, "byteOrder"):
            out.write("      BYTE_ORDER\n")
            out.write(f"        {byte_order.byteOrder}  /* byteOrder */\n")
        if safe_get(m, "discrete"):
            out.write("      DISCRETE\n")
        di = safe_get(m, "display_identifier")
        if di and safe_get(di, "display_name"):
            out.write("      DISPLAY_IDENTIFIER\n")
            out.write(f"        {di.display_name}  /* display_name */\n")
        ecu_addr = safe_get(m, "ecu_address")
        if ecu_addr and safe_get(ecu_addr, "address") is not None:
            out.write("      ECU_ADDRESS\n")
            out.write(f"        {ecu_addr.address}  /* address */\n")
        ecu_ext = safe_get(m, "ecu_address_extension")
        if ecu_ext and safe_get(ecu_ext, "extension") is not None:
            out.write("      ECU_ADDRESS_EXTENSION\n")
            out.write(f"        {ecu_ext.extension}  /* extension */\n")
        em = safe_get(m, "error_mask")
        if em and safe_get(em, "mask") is not None:
            out.write("      ERROR_MASK\n")
            out.write(f"        {em.mask}  /* mask */\n")
        fmt = safe_get(m, "format")
        if fmt and safe_get(fmt, "formatString"):
            out.write("      FORMAT\n")
            out.write(f'        "{fmt.formatString}"  /* formatString */\n')
        write_function_list(out, safe_get(m, "function_list"))
        write_raw_ifdata(out, safe_get(m, "if_data"))
        layout = safe_get(m, "layout")
        if layout and safe_get(layout, "indexMode"):
            out.write("      LAYOUT\n")
            out.write(f"        {layout.indexMode}  /* indexMode */\n")
        write_matrix_dim(out, safe_get(m, "matrix_dim"))
        mr = safe_get(m, "max_refresh")
        if mr and safe_get(mr, "scalingUnit") is not None and safe_get(mr, "rate") is not None:
            out.write("      MAX_REFRESH\n")
            out.write(f"        {mr.scalingUnit}  /* scalingUnit */\n")
            out.write(f"        {mr.rate}  /* rate */\n")
        min_pass = min_passthrough.get(safe_get(m, "conversion"))
        if min_pass is not None:
            out.write("      MIN_PASSTHROUGH\n")
            out.write(f"        {min_pass}  /* minPassThrough */\n")
        ml = safe_get(m, "model_link")
        if ml and safe_get(ml, "modelLink"):
            out.write("      MODEL_LINK\n")
            out.write(f'        "{ml.modelLink}"  /* modelLink */\n')
        if safe_get(m, "phys_unit") and safe_get(m.phys_unit, "unit"):
            out.write("      PHYS_UNIT\n")
            out.write(f'        "{m.phys_unit.unit}"  /* unit */\n')
        if safe_get(m, "read_write"):
            out.write("      READ_WRITE\n")
        if safe_get(m, "ref_memory_segment") and safe_get(m.ref_memory_segment, "name"):
            out.write("      REF_MEMORY_SEGMENT\n")
            out.write(f"        {m.ref_memory_segment.name}  /* name */\n")
        write_symbol_link(out, safe_get(m, "symbol_link"), logger)
        if safe_get(m, "virtual") and safe_get(m.virtual, "measuringChannel"):
            out.write("      /begin VIRTUAL\n")
            out.write("        " + " ".join(str(x) for x in m.virtual.measuringChannel) + "\n")
            out.write("      /end VIRTUAL\n")
        out.write("    /end MEASUREMENT\n\n")


def write_blobs(out, blobs: list[Any] | None) -> None:
    if not blobs:
        return
    for b in blobs:
        out.write("    /begin BLOB\n")
        out.write(f"      {b.name}  /* name */\n")
        out.write(f'      "{safe_get(b, "longIdentifier") or ""}"  /* longIdentifier */\n')
        out.write(f"      {safe_get(b, 'address') or 0}  /* address */\n")
        out.write(f"      {safe_get(b, 'length') or 0}  /* length */\n")
        addr_type = safe_get(b, "address_type")
        if addr_type and safe_get(addr_type, "addrType"):
            out.write("      ADDRESS_TYPE\n")
            out.write(f"        {addr_type.addrType}  /* addrType */\n")
        write_annotation(out, safe_get(b, "annotation"))
        ca = safe_get(b, "calibration_access")
        if ca and safe_get(ca, "type"):
            out.write("      CALIBRATION_ACCESS\n")
            out.write(f"        {ca.type}  /* type */\n")
        di = safe_get(b, "display_identifier")
        if di and safe_get(di, "display_name"):
            out.write("      DISPLAY_IDENTIFIER\n")
            out.write(f"        {di.display_name}  /* display_name */\n")
        ecu_ext = safe_get(b, "ecu_address_extension")
        if ecu_ext and safe_get(ecu_ext, "extension") is not None:
            out.write("      ECU_ADDRESS_EXTENSION\n")
            out.write(f"        {ecu_ext.extension}  /* extension */\n")
        write_raw_ifdata(out, safe_get(b, "if_data"))
        mr = safe_get(b, "max_refresh")
        if mr and safe_get(mr, "scalingUnit") is not None and safe_get(mr, "rate") is not None:
            out.write("      MAX_REFRESH\n")
            out.write(f"        {mr.scalingUnit}  /* scalingUnit */\n")
            out.write(f"        {mr.rate}  /* rate */\n")
        ml = safe_get(b, "model_link")
        if ml and safe_get(ml, "modelLink"):
            out.write("      MODEL_LINK\n")
            out.write(f'        "{ml.modelLink}"  /* modelLink */\n')
        write_symbol_link(out, safe_get(b, "symbol_link"), logger)
        out.write("    /end BLOB\n\n")


def write_mod_common(out, mod_common_obj: Any | None) -> None:
    if not mod_common_obj:
        return
    # NoModCommon may be used; try attribute access safe
    comment = safe_get(mod_common_obj, "comment")
    out.write("    /begin MOD_COMMON\n")
    out.write(f'      "{comment or ""}"  /* comment */\n')
    for attr_name in (
        "alignment_byte",
        "alignment_float16_ieee",
        "alignment_float32_ieee",
        "alignment_float64_ieee",
        "alignment_int64",
        "alignment_long",
        "alignment_word",
    ):
        attr = safe_get(mod_common_obj, attr_name)
        if attr and safe_get(attr, "alignmentBorder") is not None:
            tag = attr_name.upper()
            out.write(f"      {tag}\n")
            out.write(f"        {attr.alignmentBorder}  /* alignmentBorder */\n")
    bo = safe_get(mod_common_obj, "byte_order")
    if bo and safe_get(bo, "byteOrder"):
        out.write("      BYTE_ORDER\n")
        out.write(f"        {bo.byteOrder}  /* byteOrder */\n")
    ds = safe_get(mod_common_obj, "data_size")
    if ds and safe_get(ds, "size") is not None:
        out.write("      DATA_SIZE\n")
        out.write(f"        {ds.size}  /* size */\n")
    out.write("    /end MOD_COMMON\n\n")


def write_memory_layouts(out, mem_layouts: list[Any] | None) -> None:
    if not mem_layouts:
        return
    for ml in mem_layouts:
        out.write("      /begin MEMORY_LAYOUT\n")
        out.write(f"        {ml.prgType}  /* prgType */\n")
        out.write(f"        {ml.address}  /* address */\n")
        out.write(f"        {ml.size}  /* size */\n")
        out.write(f"        {ml.offset_0}  /* offset_0 */\n")
        out.write(f"        {ml.offset_1}  /* offset_1 */\n")
        out.write(f"        {ml.offset_2}  /* offset_2 */\n")
        out.write(f"        {ml.offset_3}  /* offset_3 */\n")
        out.write(f"        {ml.offset_4}  /* offset_4 */\n")
        write_raw_ifdata(out, safe_get(ml, "if_data"))
        out.write("      /end MEMORY_LAYOUT\n\n")


def write_memory_segments(out, mem_segments: list[Any] | None) -> None:
    if not mem_segments:
        return
    for ms in mem_segments:
        out.write("      /begin MEMORY_SEGMENT\n")
        out.write(f"        {ms.name}  /* name */\n")
        out.write(f'        "{safe_get(ms, "longIdentifier") or ""}"  /* longIdentifier */\n')
        out.write(f"        {ms.prgType}  /* prgType */\n")
        out.write(f"        {ms.memoryType}  /* memoryType */\n")
        out.write(f"        {ms.attribute}  /* attribute */\n")
        out.write(f"        {ms.address}  /* address */\n")
        out.write(f"        {ms.size}  /* size */\n")
        out.write(f"        {ms.offset_0}  /* offset_0 */\n")
        out.write(f"        {ms.offset_1}  /* offset_1 */\n")
        out.write(f"        {ms.offset_2}  /* offset_2 */\n")
        out.write(f"        {ms.offset_3}  /* offset_3 */\n")
        out.write(f"        {ms.offset_4}  /* offset_4 */\n")
        write_raw_ifdata(out, safe_get(ms, "if_data"))
        out.write("      /end MEMORY_SEGMENT\n\n")


def write_typedefs(out, typedef_chars: list[Any] | None, typedef_meas: list[Any] | None, typedef_structs: list[Any] | None) -> None:
    if typedef_chars:
        for tc in typedef_chars:
            out.write("    /begin TYPEDEF_CHARACTERISTIC\n")
            out.write(f"      {tc.name}  /* name */\n")
            out.write(f'      "{safe_get(tc, "longIdentifier") or ""}"  /* longIdentifier */\n')
            out.write(f"      {tc.type}  /* type */\n")
            out.write(f"      {tc.deposit}  /* deposit */\n")
            out.write(f"      {tc.maxDiff}  /* maxDiff */\n")
            out.write(f"      {tc.conversion}  /* conversion */\n")
            out.write(f"      {tc.lowerLimit}  /* lowerLimit */\n")
            out.write(f"      {tc.upperLimit}  /* upperLimit */\n")
            write_annotation(out, safe_get(tc, "annotation"))
            write_matrix_dim(out, safe_get(tc, "matrix_dim"))
            out.write("    /end TYPEDEF_CHARACTERISTIC\n\n")
    if typedef_meas:
        for tm in typedef_meas:
            out.write("    /begin TYPEDEF_MEASUREMENT\n")
            out.write(f"      {tm.name}  /* name */\n")
            out.write(f'      "{safe_get(tm, "longIdentifier") or ""}"  /* longIdentifier */\n')
            out.write(f"      {tm.datatype}  /* datatype */\n")
            out.write(f"      {tm.conversion}  /* conversion */\n")
            out.write(f"      {tm.resolution}  /* resolution */\n")
            out.write(f"      {tm.accuracy}  /* accuracy */\n")
            out.write(f"      {tm.lowerLimit}  /* lowerLimit */\n")
            out.write(f"      {tm.upperLimit}  /* upperLimit */\n")
            write_annotation(out, safe_get(tm, "annotation"))
            bm = safe_get(tm, "bit_mask")
            if bm and safe_get(bm, "mask") is not None:
                out.write("      BIT_MASK\n")
                out.write(f"        {bm.mask}  /* mask */\n")
            byte_order = safe_get(tm, "byte_order")
            if byte_order and safe_get(byte_order, "byteOrder"):
                out.write("      BYTE_ORDER\n")
                out.write(f"        {byte_order.byteOrder}  /* byteOrder */\n")
            if safe_get(tm, "discrete"):
                out.write("      DISCRETE\n")
            di = safe_get(tm, "display_identifier")
            if di and safe_get(di, "display_name"):
                out.write("      DISPLAY_IDENTIFIER\n")
                out.write(f"        {di.display_name}  /* display_name */\n")
            ecu_ext = safe_get(tm, "ecu_address_extension")
            if ecu_ext and safe_get(ecu_ext, "extension") is not None:
                out.write("      ECU_ADDRESS_EXTENSION\n")
                out.write(f"        {ecu_ext.extension}  /* extension */\n")
            em = safe_get(tm, "error_mask")
            if em and safe_get(em, "mask") is not None:
                out.write("      ERROR_MASK\n")
                out.write(f"        {em.mask}  /* mask */\n")
            fmt = safe_get(tm, "format")
            if fmt and safe_get(fmt, "formatString"):
                out.write("      FORMAT\n")
                out.write(f'        "{fmt.formatString}"  /* formatString */\n')
            write_function_list(out, safe_get(tm, "function_list"))
            layout = safe_get(tm, "layout")
            if layout and safe_get(layout, "indexMode"):
                out.write("      LAYOUT\n")
                out.write(f"        {layout.indexMode}  /* indexMode */\n")
            write_matrix_dim(out, safe_get(tm, "matrix_dim"))
            mr = safe_get(tm, "max_refresh")
            if mr and safe_get(mr, "scalingUnit") is not None and safe_get(mr, "rate") is not None:
                out.write("      MAX_REFRESH\n")
                out.write(f"        {mr.scalingUnit}  /* scalingUnit */\n")
                out.write(f"        {mr.rate}  /* rate */\n")
            if safe_get(tm, "phys_unit") and safe_get(tm.phys_unit, "unit"):
                out.write("      PHYS_UNIT\n")
                out.write(f'        "{tm.phys_unit.unit}"  /* unit */\n')
            if safe_get(tm, "read_write"):
                out.write("      READ_WRITE\n")
            if safe_get(tm, "ref_memory_segment") and safe_get(tm.ref_memory_segment, "name"):
                out.write("      REF_MEMORY_SEGMENT\n")
                out.write(f"        {tm.ref_memory_segment.name}  /* name */\n")
            out.write("    /end TYPEDEF_MEASUREMENT\n\n")
    if typedef_structs:
        for ts in typedef_structs:
            out.write("    /begin TYPEDEF_STRUCTURE\n")
            out.write(f"      {ts.name}  /* name */\n")
            out.write(f'      "{safe_get(ts, "longIdentifier") or ""}"  /* longIdentifier */\n')
            out.write(f"      {ts.size}  /* size */\n")
            write_annotation(out, safe_get(ts, "annotation"))
            if safe_get(ts, "structure_component"):
                for sc in ts.structure_component:
                    out.write("      /begin STRUCTURE_COMPONENT\n")
                    out.write(f"        {sc.name}  /* name */\n")
                    out.write(f"        {sc.type_ref}  /* type_Ref */\n")
                    out.write(f"        {sc.offset}  /* offset */\n")
                    al = safe_get(sc, "address_offset")
                    if al and safe_get(al, "offset") is not None:
                        out.write("        ADDRESS_OFFSET\n")
                        out.write(f"          {al.offset}  /* offset */\n")
                    layout = safe_get(sc, "layout")
                    if layout and safe_get(layout, "indexMode"):
                        out.write("        LAYOUT\n")
                        out.write(f"          {layout.indexMode}  /* indexMode */\n")
                    write_matrix_dim(out, safe_get(sc, "matrix_dim"))
                    num = safe_get(sc, "number")
                    if num and safe_get(num, "number") is not None:
                        out.write("        NUMBER\n")
                        out.write(f"          {num.number}  /* number */\n")
                    stl = safe_get(sc, "symbol_type_link")
                    if stl and safe_get(stl, "link"):
                        out.write("        SYMBOL_TYPE_LINK\n")
                        out.write(f'          "{stl.link}"  /* link */\n')
                    out.write("      /end STRUCTURE_COMPONENT\n")
            stl = safe_get(ts, "symbol_type_link")
            if stl and safe_get(stl, "link"):
                out.write("      SYMBOL_TYPE_LINK\n")
                out.write(f'        "{stl.link}"  /* link */\n')
            out.write("    /end TYPEDEF_STRUCTURE\n\n")


def write_typedef_axes(out, typedef_axes: list[Any] | None) -> None:
    if not typedef_axes:
        return
    for ta in typedef_axes:
        out.write("    /begin TYPEDEF_AXIS\n")
        out.write(f"      {ta.name}  /* name */\n")
        out.write(f'      "{safe_get(ta, "longIdentifier") or ""}"  /* longIdentifier */\n')
        out.write(f"      {safe_get(ta, 'inputQuantity') or '-'}  /* inputQuantity */\n")
        out.write(f"      {safe_get(ta, 'depositAttr') or '-'}  /* depositAttr */\n")
        out.write(f"      {safe_get(ta, 'maxDiff') or 0}  /* maxDiff */\n")
        out.write(f"      {safe_get(ta, 'conversion') or '-'}  /* conversion */\n")
        out.write(f"      {safe_get(ta, 'maxAxisPoints') or 0}  /* maxAxisPoints */\n")
        out.write(f"      {safe_get(ta, 'lowerLimit') or 0}  /* lowerLimit */\n")
        out.write(f"      {safe_get(ta, 'upperLimit') or 0}  /* upperLimit */\n")
        write_annotation(out, safe_get(ta, "annotation"))
        if safe_get(ta, "byte_order"):
            bo = ta.byte_order
            out.write("      BYTE_ORDER\n")
            out.write(f"        {bo.byteOrder}  /* byteOrder */\n")
        ca = safe_get(ta, "calibration_access")
        if ca and safe_get(ca, "type"):
            out.write("      CALIBRATION_ACCESS\n")
            out.write(f"        {ca.type}  /* type */\n")
        dep = safe_get(ta, "deposit")
        if dep and safe_get(dep, "mode"):
            out.write("      DEPOSIT\n")
            out.write(f"        {dep.mode}  /* mode */\n")
        di = safe_get(ta, "display_identifier")
        if di and safe_get(di, "display_name"):
            out.write("      DISPLAY_IDENTIFIER\n")
            out.write(f"        {di.display_name}  /* display_name */\n")
        ecu_ext = safe_get(ta, "ecu_address_extension")
        if ecu_ext and safe_get(ecu_ext, "extension") is not None:
            out.write("      ECU_ADDRESS_EXTENSION\n")
            out.write(f"        {ecu_ext.extension}  /* extension */\n")
        if safe_get(ta, "extended_limits"):
            el = ta.extended_limits
            out.write("      EXTENDED_LIMITS\n")
            out.write(f"        {el.lowerLimit}  /* lowerLimit */\n")
            out.write(f"        {el.upperLimit}  /* upperLimit */\n")
        fmt = safe_get(ta, "format")
        if fmt and safe_get(fmt, "formatString"):
            out.write("      FORMAT\n")
            out.write(f'        "{fmt.formatString}"  /* formatString */\n')
        if safe_get(ta, "guard_rails"):
            out.write("      GUARD_RAILS\n")
        write_raw_ifdata(out, safe_get(ta, "if_data"))
        mr = safe_get(ta, "max_refresh")
        if mr and safe_get(mr, "scalingUnit") is not None and safe_get(mr, "rate") is not None:
            out.write("      MAX_REFRESH\n")
            out.write(f"        {mr.scalingUnit}  /* scalingUnit */\n")
            out.write(f"        {mr.rate}  /* rate */\n")
        ml = safe_get(ta, "model_link")
        if ml and safe_get(ml, "modelLink"):
            out.write("      MODEL_LINK\n")
            out.write(f'        "{ml.modelLink}"  /* modelLink */\n')
        if safe_get(ta, "monotony"):
            out.write("      MONOTONY\n")
            out.write(f"        {ta.monotony.monotony}  /* monotony */\n")
        if safe_get(ta, "phys_unit") and safe_get(ta.phys_unit, "unit"):
            out.write("      PHYS_UNIT\n")
            out.write(f'        "{ta.phys_unit.unit}"  /* unit */\n')
        if safe_get(ta, "read_only"):
            out.write("      READ_ONLY\n")
        if safe_get(ta, "ref_memory_segment") and safe_get(ta.ref_memory_segment, "name"):
            out.write("      REF_MEMORY_SEGMENT\n")
            out.write(f"        {ta.ref_memory_segment.name}  /* name */\n")
        if safe_get(ta, "step_size"):
            out.write("      STEP_SIZE\n")
            out.write(f"        {ta.step_size.stepSize}  /* stepSize */\n")
        write_symbol_link(out, safe_get(ta, "symbol_link"), logger)
        out.write("    /end TYPEDEF_AXIS\n\n")


def write_typedef_blobs(out, typedef_blobs: list[Any] | None) -> None:
    if not typedef_blobs:
        return
    for tb in typedef_blobs:
        out.write("    /begin TYPEDEF_BLOB\n")
        out.write(f"      {tb.name}  /* name */\n")
        out.write(f'      "{safe_get(tb, "longIdentifier") or ""}"  /* longIdentifier */\n')
        out.write(f"      {safe_get(tb, 'length') or 0}  /* length */\n")
        addr_type = safe_get(tb, "address_type")
        if addr_type and safe_get(addr_type, "addrType"):
            out.write("      ADDRESS_TYPE\n")
            out.write(f"        {addr_type.addrType}  /* addrType */\n")
        write_annotation(out, safe_get(tb, "annotation"))
        ca = safe_get(tb, "calibration_access")
        if ca and safe_get(ca, "type"):
            out.write("      CALIBRATION_ACCESS\n")
            out.write(f"        {ca.type}  /* type */\n")
        di = safe_get(tb, "display_identifier")
        if di and safe_get(di, "display_name"):
            out.write("      DISPLAY_IDENTIFIER\n")
            out.write(f"        {di.display_name}  /* display_name */\n")
        ecu_ext = safe_get(tb, "ecu_address_extension")
        if ecu_ext and safe_get(ecu_ext, "extension") is not None:
            out.write("      ECU_ADDRESS_EXTENSION\n")
            out.write(f"        {ecu_ext.extension}  /* extension */\n")
        write_raw_ifdata(out, safe_get(tb, "if_data"))
        mr = safe_get(tb, "max_refresh")
        if mr and safe_get(mr, "scalingUnit") is not None and safe_get(mr, "rate") is not None:
            out.write("      MAX_REFRESH\n")
            out.write(f"        {mr.scalingUnit}  /* scalingUnit */\n")
            out.write(f"        {mr.rate}  /* rate */\n")
        ml = safe_get(tb, "model_link")
        if ml and safe_get(ml, "modelLink"):
            out.write("      MODEL_LINK\n")
            out.write(f'        "{ml.modelLink}"  /* modelLink */\n')
        write_symbol_link(out, safe_get(tb, "symbol_link"), logger)
        out.write("    /end TYPEDEF_BLOB\n\n")


def write_units(out, unit_list: list[Any] | None) -> None:
    if not unit_list:
        return
    for u in unit_list:
        out.write("    /begin UNIT\n")
        out.write(f"      {u.name}  /* name */\n")
        out.write(f'      "{safe_get(u, "longIdentifier") or ""}"  /* longIdentifier */\n')
        out.write(f'      "{safe_get(u, "display") or ""}"  /* display */\n')
        out.write(f"      {safe_get(u, 'type') or '-'}  /* type */\n")
        si = safe_get(u, "si_exponents")
        if si:
            out.write("      SI_EXPONENTS\n")
            out.write(f"        {si.length}  /* length */\n")
            out.write(f"        {si.mass}  /* mass */\n")
            out.write(f"        {si.time}  /* time */\n")
            out.write(f"        {si.electricCurrent}  /* electricCurrent */\n")
            out.write(f"        {si.temperature}  /* temperature */\n")
            out.write(f"        {si.amountOfSubstance}  /* amountOfSubstance */\n")
            out.write(f"        {si.luminousIntensity}  /* luminousIntensity */\n")
        if safe_get(u, "ref_unit") and safe_get(u.ref_unit, "unit"):
            out.write("      REF_UNIT\n")
            out.write(f"        {u.ref_unit.unit}  /* unit */\n")
        uc = safe_get(u, "unit_conversion")
        if uc:
            out.write("      UNIT_CONVERSION\n")
            out.write(f"        {uc.gradient}  /* gradient */\n")
            out.write(f"        {uc.offset}  /* offset */\n")
        out.write("    /end UNIT\n\n")


def write_user_rights(out, ur_list: list[Any] | None) -> None:
    if not ur_list:
        return
    for ur in ur_list:
        out.write("    /begin USER_RIGHTS\n")
        out.write(f"      {ur.userLevelId}  /* userLevelId */\n")
        if safe_get(ur, "read_only"):
            out.write("      READ_ONLY\n")
        rg = safe_get(ur, "ref_group")
        if rg:
            for r in rg:
                out.write("      /begin REF_GROUP\n")
                out.write("        MULTIPLE\n")
                out.write(f"        {r.identifier}  /* identifier */\n")
                out.write("      /end REF_GROUP\n")
        out.write("    /end USER_RIGHTS\n\n")


def write_variant_coding(out, vc: Any | None) -> None:
    if not vc:
        return
    out.write("    /begin VARIANT_CODING\n")
    for v in safe_get(vc, "var_characteristic") or []:
        out.write("      /begin VAR_CHARACTERISTIC\n")
        out.write(f"        {v.name}  /* name */\n")
        out.write("      MULTIPLE\n")
        out.write(f"        {v.criterionName}  /* criterionName */\n")
        va = safe_get(v, "var_address")
        if va and safe_get(va, "address"):
            out.write("        /begin VAR_ADDRESS\n")
            out.write("          " + " ".join(str(x) for x in va.address) + "\n")
            out.write("        /end VAR_ADDRESS\n")
        out.write("      /end VAR_CHARACTERISTIC\n")
    for vc_entry in safe_get(vc, "var_criterion") or []:
        out.write("      /begin VAR_CRITERION\n")
        out.write(f"        {vc_entry.name}  /* name */\n")
        out.write(f'        "{safe_get(vc_entry, "longIdentifier") or ""}"  /* longIdentifier */\n')
        out.write("      MULTIPLE\n")
        out.write(f"        {vc_entry.value}  /* value */\n")
        vm = safe_get(vc_entry, "var_measurement")
        if vm and safe_get(vm, "name"):
            out.write("        VAR_MEASUREMENT\n")
            out.write(f"          {vm.name}  /* name */\n")
        vsc = safe_get(vc_entry, "var_selection_characteristic")
        if vsc and safe_get(vsc, "name"):
            out.write("        VAR_SELECTION_CHARACTERISTIC\n")
            out.write(f"          {vsc.name}  /* name */\n")
        out.write("      /end VAR_CRITERION\n")
    out.write("    /end VARIANT_CODING\n\n")


def _camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def _iter_columns(obj: Any) -> list[str]:
    return [c.name for c in getattr(obj, "__table__").columns if not c.name.endswith("_rid") and c.name != "rid"]


def write_record_layout_entries(out, keyword: str, entries: Any | list[Any]) -> None:
    if entries is None:
        return
    if not isinstance(entries, list):
        entries = [entries]
    for entry in entries:
        cols = _iter_columns(entry)
        values = [safe_get(entry, col) for col in cols]
        out.write(f"      {keyword}\n")
        out.write("        " + " ".join("" if v is None else str(v) for v in values) + "\n")


def write_record_layouts(out, layouts: list[Any] | None) -> None:
    if not layouts:
        return
    for rl in layouts:
        out.write("    /begin RECORD_LAYOUT\n")
        out.write(f"      {rl.name}  /* name */\n")
        for elem in getattr(rl, "__optional_elements__", ()):
            attr = _camel_to_snake(elem.name)
            data = safe_get(rl, attr)
            if data is None:
                continue
            write_record_layout_entries(out, elem.keyword_name, data)
        out.write("    /end RECORD_LAYOUT\n\n")


def write_transformers(out, transformers: list[Any] | None) -> None:
    if not transformers:
        return
    for tr in transformers:
        out.write("    /begin TRANSFORMER\n")
        out.write(f"      {tr.name}  /* name */\n")
        out.write(f'      "{safe_get(tr, "version") or ""}"  /* version */\n')
        out.write(f'      "{safe_get(tr, "dllname32") or ""}"  /* dllname32 */\n')
        out.write(f'      "{safe_get(tr, "dllname64") or ""}"  /* dllname64 */\n')
        out.write(f"      {safe_get(tr, 'timeout') or 0}  /* timeout */\n")
        out.write(f"      {safe_get(tr, 'trigger') or '-'}  /* trigger */\n")
        out.write(f"      {safe_get(tr, 'reverse') or '-'}  /* reverse */\n")
        tio = safe_get(tr, "transformer_in_objects")
        if tio and safe_get(tio, "identifier"):
            out.write("      /begin TRANSFORMER_IN_OBJECTS\n")
            out.write("        " + " ".join(str(x) for x in tio.identifier) + "\n")
            out.write("      /end TRANSFORMER_IN_OBJECTS\n")
        too = safe_get(tr, "transformer_out_objects")
        if too and safe_get(too, "identifier"):
            out.write("      /begin TRANSFORMER_OUT_OBJECTS\n")
            out.write("        " + " ".join(str(x) for x in too.identifier) + "\n")
            out.write("      /end TRANSFORMER_OUT_OBJECTS\n")
        out.write("    /end TRANSFORMER\n\n")


def _prepare_output(out_target: Path | TextIO) -> tuple[TextIO, bool]:
    if hasattr(out_target, "write"):
        return out_target, False
    out_path = Path(out_target)
    return out_path.open("w", encoding="utf-8"), True


def export_db(db: A2LDatabase, out_path: Path | TextIO, module_name: str | None = None) -> None:
    session = db.session
    logger = logging.getLogger(__name__)
    try:
        session.execute("PRAGMA query_only=ON")
    except Exception:
        logger.debug("Unable to switch SQLite connection to query_only mode.", exc_info=True)
    project = session.query(model.Project).first()
    if project is None:
        logger.error("No Project row found in the database.")
        return

    out, close_out = _prepare_output(out_path)
    try:
        out.write("/begin PROJECT\n")
        out.write(f"  {project.name}  /* name */\n")
        out.write(f'  "{project.longIdentifier}"  /* longIdentifier */\n')
        header = safe_get(project, "header")
        if header:
            out.write("  /begin HEADER\n")
            comment = safe_get(header, "comment")
            if comment:
                out.write(f'    "{comment}"  /* comment */\n')
            proj_no = safe_get(header, "project_no")
            if proj_no and safe_get(proj_no, "projectNumber"):
                out.write("    PROJECT_NO\n")
                out.write(f"      {proj_no.projectNumber}  /* projectNumber */\n")
            version = safe_get(header, "version")
            if version and safe_get(version, "versionIdentifier"):
                out.write("    VERSION\n")
                out.write(f'      "{version.versionIdentifier}"  /* versionIdentifier */\n')
            out.write("  /end HEADER\n")
        record_layout_opt = selectinload(model.Module.record_layout)
        transformer_opt = selectinload(model.Module.transformer)
        base_options = [
            selectinload(model.Module.mod_par).selectinload(model.ModPar.addr_epk),
            selectinload(model.Module.mod_par)
            .selectinload(model.ModPar.calibration_method)
            .selectinload(model.CalibrationMethod.calibration_handle),
            selectinload(model.Module.mod_par).selectinload(model.ModPar.memory_segment),
            selectinload(model.Module.compu_method).selectinload(model.CompuMethod.compu_tab_ref),
            selectinload(model.Module.compu_tab).selectinload(model.CompuTab.pairs),
            selectinload(model.Module.compu_vtab).selectinload(model.CompuVtab.pairs),
            selectinload(model.Module.compu_vtab_range).selectinload(model.CompuVtabRange.triples),
            selectinload(model.Module.mod_common),
            record_layout_opt,
            transformer_opt,
        ]
        modules_query = session.query(model.Module).options(*base_options)
        if module_name:
            modules_query = modules_query.filter(model.Module.name == module_name)
        try:
            modules = modules_query.all()
        except OperationalError as exc:
            logger.warning("Module preload failed (schema mismatch?). Retrying without RECORD_LAYOUT/TRANSFORMER: %s", exc)
            fallback_opts = [opt for opt in base_options if opt not in (record_layout_opt, transformer_opt)]
            modules_query = session.query(model.Module).options(*fallback_opts)
            if module_name:
                modules_query = modules_query.filter(model.Module.name == module_name)
            modules = modules_query.all()
        if not modules:
            logger.warning("No modules found (or incorrect module name).")
        for mod in modules:
            out.write("  /begin MODULE\n")
            out.write(f"    {mod.name}  /* name */\n")
            out.write(f'    "{safe_get(mod, "longIdentifier") or ""}"  /* longIdentifier */\n')
            # AML raw text if present
            aml_section = session.query(model.AMLSection).first()
            if aml_section and safe_get(aml_section, "text"):
                out.write("\n")
                out.write(aml_section.text.strip())
                out.write("\n")
            write_axis_pts(out, safe_get(mod, "axis_pts"))
            write_blobs(out, safe_get(mod, "blob"))
            write_characteristics(out, safe_get(mod, "characteristic"))
            write_compu_methods(out, safe_get(mod, "compu_method"))
            write_compu_tabs(out, safe_get(mod, "compu_tab"))
            write_compu_tabs(out, safe_get(mod, "compu_vtab"))
            write_compu_tabs(out, safe_get(mod, "compu_vtab_range"))
            write_frames(out, safe_get(mod, "frame"))
            write_functions(out, safe_get(mod, "function"))
            write_groups(out, safe_get(mod, "group"))
            write_raw_ifdata(out, safe_get(mod, "if_data"))
            write_instances(out, safe_get(mod, "instance"))
            write_measurements(out, safe_get(mod, "measurement"), _min_passthrough_lookup(mod))
            write_mod_common(out, safe_get(mod, "mod_common"))
            mp = safe_get(mod, "mod_par")
            if mp:
                out.write("    /begin MOD_PAR\n")
                out.write(f'      "{safe_get(mp, "comment") or ""}"  /* comment */\n')
                for addr in safe_get(mp, "addr_epk") or []:
                    out.write("      ADDR_EPK\n")
                    out.write(f"        {safe_get(addr, 'address') or 0}  /* address */\n")
                for cm in safe_get(mp, "calibration_method") or []:
                    out.write("      /begin CALIBRATION_METHOD\n")
                    out.write(f'        "{safe_get(cm, "method") or ""}"  /* method */\n')
                    out.write(f"        {safe_get(cm, 'version') or 0}  /* version */\n")
                    for ch in safe_get(cm, "calibration_handle") or []:
                        out.write("        /begin CALIBRATION_HANDLE\n")
                        handles = safe_get(ch, "handle") or []
                        if handles:
                            out.write("          " + " ".join(str(x) for x in handles) + "\n")
                        cht = safe_get(ch, "calibration_handle_text")
                        if cht and safe_get(cht, "text"):
                            out.write("          CALIBRATION_HANDLE_TEXT\n")
                            out.write(f'            "{cht.text}"\n')
                        out.write("        /end CALIBRATION_HANDLE\n")
                    out.write("      /end CALIBRATION_METHOD\n")
                if safe_get(mp, "cpu_type") and safe_get(mp.cpu_type, "cPU"):
                    out.write("      CPU_TYPE\n")
                    out.write(f'        "{mp.cpu_type.cPU}"\n')
                if safe_get(mp, "customer") and safe_get(mp.customer, "customer"):
                    out.write("      CUSTOMER\n")
                    out.write(f'        "{mp.customer.customer}"\n')
                if safe_get(mp, "customer_no") and safe_get(mp.customer_no, "number"):
                    out.write("      CUSTOMER_NO\n")
                    out.write(f'        "{mp.customer_no.number}"\n')
                if safe_get(mp, "ecu") and safe_get(mp.ecu, "controlUnit"):
                    out.write("      ECU\n")
                    out.write(f'        "{mp.ecu.controlUnit}"\n')
                if safe_get(mp, "ecu_calibration_offset") and safe_get(mp.ecu_calibration_offset, "offset") is not None:
                    out.write("      ECU_CALIBRATION_OFFSET\n")
                    out.write(f"        {mp.ecu_calibration_offset.offset}\n")
                if safe_get(mp, "epk") and safe_get(mp.epk, "identifier"):
                    out.write("      EPK\n")
                    out.write(f'        "{mp.epk.identifier}"\n')
                write_memory_layouts(out, safe_get(mp, "memory_layout"))
                write_memory_segments(out, safe_get(mp, "memory_segment"))
                if safe_get(mp, "no_of_interfaces"):
                    out.write("      NO_OF_INTERFACES\n")
                    out.write(f"        {mp.no_of_interfaces.num}  /* num */\n")
                if safe_get(mp, "phone_no") and safe_get(mp.phone_no, "telnum"):
                    out.write("      PHONE_NO\n")
                    out.write(f'        "{mp.phone_no.telnum}"  /* telnum */\n')
                if safe_get(mp, "supplier") and safe_get(mp.supplier, "manufacturer"):
                    out.write("      SUPPLIER\n")
                    out.write(f'        "{mp.supplier.manufacturer}"  /* manufacturer */\n')
                if safe_get(mp, "system_constant"):
                    for sc in mp.system_constant:
                        out.write("      SYSTEM_CONSTANT\n")
                        out.write(f'        "{sc.name}"  /* name */\n')
                        out.write(f'        "{sc.value}"  /* value */\n')
                if safe_get(mp, "user") and safe_get(mp.user, "userName"):
                    out.write("      USER\n")
                    out.write(f'        "{mp.user.userName}"\n')
                if safe_get(mp, "version") and safe_get(mp.version, "versionIdentifier"):
                    out.write("      VERSION\n")
                    out.write(f'        "{mp.version.versionIdentifier}"\n')
                out.write("    /end MOD_PAR\n\n")
            write_typedefs(
                out,
                safe_get(mod, "typedef_characteristic"),
                safe_get(mod, "typedef_measurement"),
                safe_get(mod, "typedef_structure"),
            )
            write_typedef_axes(out, safe_get(mod, "typedef_axis"))
            write_typedef_blobs(out, safe_get(mod, "typedef_blob"))
            write_units(out, safe_get(mod, "unit"))
            write_user_rights(out, safe_get(mod, "user_rights"))
            write_variant_coding(out, safe_get(mod, "variant_coding"))
            try:
                write_record_layouts(out, safe_get(mod, "record_layout"))
            except OperationalError as exc:
                logger.warning("Skipping RECORD_LAYOUT export due to schema mismatch: %s", exc)
            try:
                write_transformers(out, safe_get(mod, "transformer"))
            except OperationalError as exc:
                logger.warning("Skipping TRANSFORMER export due to schema mismatch: %s", exc)
            out.write("  /end MODULE\n\n")
        write_raw_ifdata(out, safe_get(project, "if_data"))
        out.write("/end PROJECT\n")
    finally:
        if close_out:
            out.close()


def parse_args(argv: list[str] | None = None) -> ExporterConfig:
    parser = argparse.ArgumentParser(description="A2L exporter from pyA2L a2ldb.")
    parser.add_argument("database", type=Path, help="Path to the a2ldb file (or basename without .a2ldb).")
    parser.add_argument("-o", "--output", type=Path, help="Output file (.a2l). Default: <db>.a2l")
    parser.add_argument("-m", "--module", type=str, help="Optional: export only this module.", default=None)
    parser.add_argument("-l", "--loglevel", type=str, help="Log level (DEBUG, INFO, WARNING).", default="INFO")
    args = parser.parse_args(argv)
    db_path = args.database
    if not db_path.exists():
        candidate = db_path.with_suffix(".a2ldb")
        if candidate.exists():
            db_path = candidate
        else:
            raise FileNotFoundError(f"Database file not found: {args.database}")
    out_path = args.output or db_path.with_suffix(".a2l")
    return ExporterConfig(db_path=db_path, out_path=out_path, module_name=args.module, loglevel=args.loglevel)


def main(argv: list[str] | None = None) -> None:
    cfg = parse_args(argv)
    setup_logging(cfg.loglevel)
    logger = logging.getLogger(__name__)
    logger.info("Starting export...")
    db = open_database(cfg.db_path, cfg.loglevel)
    try:
        export_db(db, cfg.out_path, cfg.module_name)
    finally:
        try:
            db.close()
        except Exception:
            logger.debug("Error while closing the database.", exc_info=True)

    logger.info("Export finished. File: %s", cfg.out_path)


if __name__ == "__main__":
    main()
