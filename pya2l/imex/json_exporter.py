#!/usr/bin/env python
"""Exporter: a2ldb -> JSON.

Full JSON exporter matching exporter_new.py coverage.
Robust implementation with dataclasses, type hints, and logging.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import selectinload

import pya2l.model as model
from pya2l.model import A2LDatabase


@dataclass
class ExporterConfig:
    """Configuration for the JSON exporter."""

    db_path: Path
    out_path: Path
    module_name: str | None
    pretty: bool
    loglevel: str = "INFO"


def setup_logging(level: str) -> None:
    """Configure basic logging."""
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(level=numeric, format="%(levelname)s: %(message)s")


def open_database(db_path: Path, loglevel: str = "INFO") -> A2LDatabase:
    """Open A2LDatabase; optionally initialize IF_DATA parser."""
    db = A2LDatabase(str(db_path), debug=False, logLevel=loglevel)
    try:
        db.session.setup_ifdata_parser(loglevel)
    except Exception:
        logging.getLogger(__name__).debug(
            "IF_DATA parser could not be initialized.",
            exc_info=True,
        )
    return db


def safe_get(obj: Any, attr: str) -> Any:
    """Safe getattr with None fallback."""
    try:
        return getattr(obj, attr)
    except Exception:
        return None


def as_list(value: Any) -> list[Any]:
    """Normalize iterable ORM fields to Python lists."""
    if not value:
        return []
    if isinstance(value, list):
        return value
    try:
        return list(value)
    except Exception:
        return [value]


def _bool_flag(obj: Any) -> bool:
    """ORM flag fields are often modeled as dedicated objects."""
    return bool(obj)


def matrix_dim_to_list(matrix_dim_obj: Any) -> list[int] | None:
    """Return MATRIX_DIM as a list of ints."""
    if not matrix_dim_obj:
        return None
    nums = safe_get(matrix_dim_obj, "numbers")
    if not nums:
        return None
    try:
        return [int(x) for x in nums]
    except Exception:
        return [int(x) for x in list(nums)]


def function_list_to_list(function_list_obj: Any) -> list[str]:
    """FUNCTION_LIST as a list of names (strings)."""
    if not function_list_obj:
        return []
    names = safe_get(function_list_obj, "name")
    if not names:
        return []
    return [str(x) for x in names]


def symbol_link_to_dict(symbol_link_obj: Any) -> dict[str, Any] | None:
    """SYMBOL_LINK as dict."""
    if not symbol_link_obj:
        return None
    return {
        "symbolName": safe_get(symbol_link_obj, "symbolName"),
        "offset": safe_get(symbol_link_obj, "offset"),
    }


def max_refresh_to_dict(max_refresh_obj: Any) -> dict[str, Any] | None:
    """MAX_REFRESH as dict."""
    if not max_refresh_obj:
        return None
    return {
        "scalingUnit": safe_get(max_refresh_obj, "scalingUnit"),
        "rate": safe_get(max_refresh_obj, "rate"),
    }


def ifdata_raw_list(sections: Iterable[Any] | None) -> list[str]:
    """Collect raw text of IF_DATA sections if present."""
    raws: list[str] = []
    for s in as_list(sections):
        raw = safe_get(s, "raw")
        if raw and str(raw).strip():
            raws.append(str(raw))
    return raws


def ifdata_parsed_list(session: Any, sections: Sequence[Any] | None) -> list[Any]:
    """Parse IF_DATA (best effort)."""
    if not sections:
        return []
    try:
        parsed = session.parse_ifdata(sections)
        return parsed or []
    except Exception:
        logging.getLogger(__name__).debug("Error parsing IF_DATA.", exc_info=True)
        return []


def extended_limits_to_dict(ext_limits_obj: Any) -> dict[str, Any] | None:
    """EXTENDED_LIMITS as dict."""
    if not ext_limits_obj:
        return None
    lower = safe_get(ext_limits_obj, "lowerLimit")
    upper = safe_get(ext_limits_obj, "upperLimit")
    if lower is None and upper is None:
        return None
    return {
        "lowerLimit": lower,
        "upperLimit": upper,
    }


def annotation_to_list(annos: Iterable[Any] | None) -> list[dict[str, Any]]:
    """Convert annotations to simple dicts."""
    result: list[dict[str, Any]] = []
    for a in as_list(annos):
        label = safe_get(a, "annotation_label")
        origin = safe_get(a, "annotation_origin")
        text = safe_get(a, "annotation_text")

        lines: list[str] = []
        if text and getattr(text, "_text", None):
            for ln in text._text:
                t = safe_get(ln, "text")
                if t is not None:
                    lines.append(str(t))

        result.append(
            {
                "label": safe_get(label, "label") if label else None,
                "origin": safe_get(origin, "origin") if origin else None,
                "text_lines": lines,
            }
        )
    return result


def axis_descr_to_dict(session: Any, ad: Any) -> dict[str, Any]:
    """AXIS_DESCR to dict."""
    out: dict[str, Any] = {
        "attribute": safe_get(ad, "attribute"),
        "inputQuantity": safe_get(ad, "inputQuantity"),
        "conversion": safe_get(ad, "conversion"),
        "maxAxisPoints": safe_get(ad, "maxAxisPoints"),
        "lowerLimit": safe_get(ad, "lowerLimit"),
        "upperLimit": safe_get(ad, "upperLimit"),
        "annotation": annotation_to_list(safe_get(ad, "annotation")),
        "axis_pts_ref": safe_get(safe_get(ad, "axis_pts_ref"), "axisPoints"),
        "if_data_raw": ifdata_raw_list(safe_get(ad, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(ad, "if_data")),
    }
    return out


def axis_pts_to_dict(session: Any, ap: Any) -> dict[str, Any]:
    """AXIS_PTS to dict."""
    out: dict[str, Any] = {
        "name": safe_get(ap, "name"),
        "longIdentifier": safe_get(ap, "longIdentifier"),
        "address": safe_get(ap, "address"),
        "inputQuantity": safe_get(ap, "inputQuantity"),
        "depositAttr": safe_get(ap, "depositAttr"),
        "maxDiff": safe_get(ap, "maxDiff"),
        "conversion": safe_get(ap, "conversion"),
        "maxAxisPoints": safe_get(ap, "maxAxisPoints"),
        "lowerLimit": safe_get(ap, "lowerLimit"),
        "upperLimit": safe_get(ap, "upperLimit"),
        "annotation": annotation_to_list(safe_get(ap, "annotation")),
        "byte_order": safe_get(safe_get(ap, "byte_order"), "byteOrder"),
        "calibration_access": safe_get(safe_get(ap, "calibration_access"), "type"),
        "deposit": safe_get(safe_get(ap, "deposit"), "mode"),
        "display_identifier": safe_get(safe_get(ap, "display_identifier"), "display_name"),
        "ecu_address_extension": safe_get(safe_get(ap, "ecu_address_extension"), "extension"),
        "extended_limits": extended_limits_to_dict(safe_get(ap, "extended_limits")),
        "format": safe_get(safe_get(ap, "format"), "formatString"),
        "function_list": function_list_to_list(safe_get(ap, "function_list")),
        "guard_rails": _bool_flag(safe_get(ap, "guard_rails")),
        "max_refresh": max_refresh_to_dict(safe_get(ap, "max_refresh")),
        "model_link": safe_get(safe_get(ap, "model_link"), "modelLink"),
        "monotony": safe_get(safe_get(ap, "monotony"), "monotony"),
        "phys_unit": safe_get(safe_get(ap, "phys_unit"), "unit"),
        "read_only": _bool_flag(safe_get(ap, "read_only")),
        "ref_memory_segment": safe_get(safe_get(ap, "ref_memory_segment"), "name"),
        "step_size": safe_get(safe_get(ap, "step_size"), "stepSize"),
        "symbol_link": symbol_link_to_dict(safe_get(ap, "symbol_link")),
        "if_data_raw": ifdata_raw_list(safe_get(ap, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(ap, "if_data")),
    }
    return out


def characteristic_to_dict(session: Any, ch: Any) -> dict[str, Any]:
    """CHARACTERISTIC to dict."""
    out: dict[str, Any] = {
        "name": safe_get(ch, "name"),
        "longIdentifier": safe_get(ch, "longIdentifier"),
        "type": safe_get(ch, "type"),
        "address": safe_get(ch, "address"),
        "deposit": safe_get(ch, "deposit"),
        "maxDiff": safe_get(ch, "maxDiff"),
        "conversion": safe_get(ch, "conversion"),
        "lowerLimit": safe_get(ch, "lowerLimit"),
        "upperLimit": safe_get(ch, "upperLimit"),
        "annotation": annotation_to_list(safe_get(ch, "annotation")),
        "axis_descr": [axis_descr_to_dict(session, ad) for ad in as_list(safe_get(ch, "axis_descr"))],
        "bit_mask": safe_get(safe_get(ch, "bit_mask"), "mask"),
        "byte_order": safe_get(safe_get(ch, "byte_order"), "byteOrder"),
        "calibration_access": safe_get(safe_get(ch, "calibration_access"), "type"),
        "comparison_quantity": safe_get(safe_get(ch, "comparison_quantity"), "name"),
        "dependent_characteristic": (
            None
            if not safe_get(ch, "dependent_characteristic")
            else {
                "formula": safe_get(ch.dependent_characteristic, "formula"),
                "characteristic": as_list(safe_get(ch.dependent_characteristic, "characteristic")),
            }
        ),
        "discrete": _bool_flag(safe_get(ch, "discrete")),
        "display_identifier": safe_get(safe_get(ch, "display_identifier"), "display_name"),
        "ecu_address_extension": safe_get(safe_get(ch, "ecu_address_extension"), "extension"),
        "encoding": safe_get(safe_get(ch, "encoding"), "conversionType"),
        "extended_limits": extended_limits_to_dict(safe_get(ch, "extended_limits")),
        "format": safe_get(safe_get(ch, "format"), "formatString"),
        "function_list": function_list_to_list(safe_get(ch, "function_list")),
        "guard_rails": _bool_flag(safe_get(ch, "guard_rails")),
        "map_list": as_list(safe_get(safe_get(ch, "map_list"), "name")) if safe_get(ch, "map_list") else [],
        "matrix_dim": matrix_dim_to_list(safe_get(ch, "matrix_dim")),
        "max_refresh": max_refresh_to_dict(safe_get(ch, "max_refresh")),
        "model_link": safe_get(safe_get(ch, "model_link"), "modelLink"),
        "number": safe_get(safe_get(ch, "number"), "number"),
        "phys_unit": safe_get(safe_get(ch, "phys_unit"), "unit"),
        "read_only": _bool_flag(safe_get(ch, "read_only")),
        "ref_memory_segment": safe_get(safe_get(ch, "ref_memory_segment"), "name"),
        "step_size": safe_get(safe_get(ch, "step_size"), "stepSize"),
        "symbol_link": symbol_link_to_dict(safe_get(ch, "symbol_link")),
        "virtual_characteristic": (
            None
            if not safe_get(ch, "virtual_characteristic")
            else {
                "formula": safe_get(ch.virtual_characteristic, "formula"),
                "characteristic": as_list(safe_get(ch.virtual_characteristic, "characteristic")),
            }
        ),
        "if_data_raw": ifdata_raw_list(safe_get(ch, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(ch, "if_data")),
    }
    return out


def compu_method_to_dict(cm: Any) -> dict[str, Any]:
    """COMPU_METHOD to dict."""
    out: dict[str, Any] = {
        "name": safe_get(cm, "name"),
        "longIdentifier": safe_get(cm, "longIdentifier"),
        "conversionType": safe_get(cm, "conversionType"),
        "format": safe_get(cm, "format"),
        "unit": safe_get(cm, "unit"),
        "coeffs": None,
        "coeffs_linear": None,
        "compu_tab_ref": None,
        "formula": None,
        "ref_unit": None,
        "status_string_ref": None,
    }

    coeffs = safe_get(cm, "coeffs")
    if coeffs:
        out["coeffs"] = {
            "a": safe_get(coeffs, "a"),
            "b": safe_get(coeffs, "b"),
            "c": safe_get(coeffs, "c"),
            "d": safe_get(coeffs, "d"),
            "e": safe_get(coeffs, "e"),
            "f": safe_get(coeffs, "f"),
        }

    coeffs_linear = safe_get(cm, "coeffs_linear")
    if coeffs_linear:
        out["coeffs_linear"] = {"a": safe_get(coeffs_linear, "a"), "b": safe_get(coeffs_linear, "b")}

    ctr = safe_get(cm, "compu_tab_ref")
    if ctr:
        out["compu_tab_ref"] = {"conversionTable": safe_get(ctr, "conversionTable")}

    formula = safe_get(cm, "formula")
    if formula:
        inv = safe_get(formula, "formula_inv")
        out["formula"] = {
            "f_x": safe_get(formula, "f_x"),
            "formula_inv": {"g_x": safe_get(inv, "g_x")} if inv else None,
        }

    ru = safe_get(cm, "ref_unit")
    if ru:
        out["ref_unit"] = {"unit": safe_get(ru, "unit")}

    ssr = safe_get(cm, "status_string_ref")
    if ssr:
        out["status_string_ref"] = {"conversionTable": safe_get(ssr, "conversionTable")}

    return out


def _compu_tab_common(t: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "name": safe_get(t, "name"),
        "longIdentifier": safe_get(t, "longIdentifier"),
        "default_value": None,
        "default_value_numeric": None,
    }
    dv = safe_get(t, "default_value")
    if dv:
        base["default_value"] = {"display_string": safe_get(dv, "display_string")}
    dvn = safe_get(t, "default_value_numeric")
    if dvn:
        base["default_value_numeric"] = {"display_value": safe_get(dvn, "display_value")}
    return base


def compu_tab_to_dict(t: Any) -> dict[str, Any]:
    out = _compu_tab_common(t)
    out.update(
        {
            "kind": "COMPU_TAB",
            "conversionType": safe_get(t, "conversionType"),
            "numberValuePairs": safe_get(t, "numberValuePairs"),
            "pairs": [
                {"inVal": safe_get(p, "inVal"), "outVal": safe_get(p, "outVal")}
                for p in as_list(safe_get(t, "pairs"))
            ],
        }
    )
    return out


def compu_vtab_to_dict(t: Any) -> dict[str, Any]:
    out = _compu_tab_common(t)
    out.update(
        {
            "kind": "COMPU_VTAB",
            "conversionType": safe_get(t, "conversionType"),
            "numberValuePairs": safe_get(t, "numberValuePairs"),
            "pairs": [
                {"inVal": safe_get(p, "inVal"), "outVal": safe_get(p, "outVal")}
                for p in as_list(safe_get(t, "pairs"))
            ],
        }
    )
    return out


def compu_vtab_range_to_dict(t: Any) -> dict[str, Any]:
    out = _compu_tab_common(t)
    out.update(
        {
            "kind": "COMPU_VTAB_RANGE",
            "numberValueTriples": safe_get(t, "numberValueTriples"),
            "triples": [
                {
                    "inValMin": safe_get(p, "inValMin"),
                    "inValMax": safe_get(p, "inValMax"),
                    "outVal": safe_get(p, "outVal"),
                }
                for p in as_list(safe_get(t, "triples"))
            ],
        }
    )
    return out


def frame_to_dict(session: Any, fr: Any) -> dict[str, Any]:
    fm = safe_get(fr, "frame_measurement")
    identifiers: list[str] | None = None
    if fm and safe_get(fm, "identifier"):
        identifiers = [str(x) for x in fm.identifier]

    out: dict[str, Any] = {
        "name": safe_get(fr, "name"),
        "longIdentifier": safe_get(fr, "longIdentifier"),
        "scalingUnit": safe_get(fr, "scalingUnit"),
        "rate": safe_get(fr, "rate"),
        "frame_measurement": identifiers,
        "if_data_raw": ifdata_raw_list(safe_get(fr, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(fr, "if_data")),
    }
    return out


def function_to_dict(session: Any, fn: Any) -> dict[str, Any]:
    out: dict[str, Any] = {
        "name": safe_get(fn, "name"),
        "longIdentifier": safe_get(fn, "longIdentifier"),
        "annotation": annotation_to_list(safe_get(fn, "annotation")),
        "def_characteristic": None,
        "function_version": None,
        "in_measurement": None,
        "loc_measurement": None,
        "out_measurement": None,
        "ref_characteristic": None,
        "sub_function": None,
        "if_data_raw": ifdata_raw_list(safe_get(fn, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(fn, "if_data")),
    }

    def_char = safe_get(fn, "def_characteristic")
    if def_char and safe_get(def_char, "identifier"):
        out["def_characteristic"] = [str(x) for x in def_char.identifier]

    fv = safe_get(fn, "function_version")
    if fv:
        out["function_version"] = {"versionIdentifier": safe_get(fv, "versionIdentifier")}

    for tag, attr in (
        ("in_measurement", "in_measurement"),
        ("loc_measurement", "loc_measurement"),
        ("out_measurement", "out_measurement"),
    ):
        ent = safe_get(fn, attr)
        if ent and safe_get(ent, "identifier"):
            out[tag] = [str(x) for x in ent.identifier]

    rc = safe_get(fn, "ref_characteristic")
    if rc and safe_get(rc, "identifier"):
        out["ref_characteristic"] = [str(x) for x in rc.identifier]

    sf = safe_get(fn, "sub_function")
    if sf and safe_get(sf, "identifier"):
        out["sub_function"] = [str(x) for x in sf.identifier]

    return out


def group_to_dict(session: Any, g: Any) -> dict[str, Any]:
    out: dict[str, Any] = {
        "groupName": safe_get(g, "groupName"),
        "groupLongIdentifier": safe_get(g, "groupLongIdentifier"),
        "annotation": annotation_to_list(safe_get(g, "annotation")),
        "function_list": function_list_to_list(safe_get(g, "function_list")),
        "ref_characteristic": None,
        "ref_measurement": None,
        "root": _bool_flag(safe_get(g, "root")),
        "sub_group": None,
        "if_data_raw": ifdata_raw_list(safe_get(g, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(g, "if_data")),
    }

    rc = safe_get(g, "ref_characteristic")
    if rc and safe_get(rc, "identifier"):
        out["ref_characteristic"] = [str(x) for x in rc.identifier]

    rm = safe_get(g, "ref_measurement")
    if rm and safe_get(rm, "identifier"):
        out["ref_measurement"] = [str(x) for x in rm.identifier]

    sub = safe_get(g, "sub_group")
    if sub and safe_get(sub, "identifier"):
        out["sub_group"] = [str(x) for x in sub.identifier]

    return out


def instance_to_dict(session: Any, inst: Any) -> dict[str, Any]:
    num = safe_get(inst, "number")
    out: dict[str, Any] = {
        "name": safe_get(inst, "name"),
        "longIdentifier": safe_get(inst, "longIdentifier"),
        "typeName": safe_get(inst, "typeName"),
        "address": safe_get(inst, "address"),
        "address_type": safe_get(safe_get(inst, "address_type"), "addrType"),
        "annotation": annotation_to_list(safe_get(inst, "annotation")),
        "calibration_access": safe_get(safe_get(inst, "calibration_access"), "type"),
        "display_identifier": safe_get(safe_get(inst, "display_identifier"), "display_name"),
        "ecu_address_extension": safe_get(safe_get(inst, "ecu_address_extension"), "extension"),
        "matrix_dim": matrix_dim_to_list(safe_get(inst, "matrix_dim")),
        "max_refresh": max_refresh_to_dict(safe_get(inst, "max_refresh")),
        "model_link": safe_get(safe_get(inst, "model_link"), "modelLink"),
        "number": safe_get(num, "number") if num else None,
        "read_only": _bool_flag(safe_get(inst, "read_only")),
        "symbol_link": symbol_link_to_dict(safe_get(inst, "symbol_link")),
        "if_data_raw": ifdata_raw_list(safe_get(inst, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(inst, "if_data")),
    }
    return out


def measurement_to_dict(session: Any, m: Any, min_passthrough: dict[str, float] | None = None) -> dict[str, Any]:
    arr = safe_get(m, "array_size")
    bm = safe_get(m, "bit_mask")
    layout = safe_get(m, "layout")

    virtual = safe_get(m, "virtual")
    virtual_list: list[str] | None = None
    if virtual and safe_get(virtual, "measuringChannel"):
        virtual_list = [str(x) for x in virtual.measuringChannel]

    bit_op = safe_get(m, "bit_operation")
    bit_operation_dict: dict[str, Any] | None = None
    if bit_op:
        bit_operation_dict = {}
        ls = safe_get(bit_op, "left_shift")
        if ls:
            bit_operation_dict["left_shift"] = {"bitcount": safe_get(ls, "bitcount")}
        rs = safe_get(bit_op, "right_shift")
        if rs:
            bit_operation_dict["right_shift"] = {"bitcount": safe_get(rs, "bitcount")}
        if safe_get(bit_op, "sign_extend"):
            bit_operation_dict["sign_extend"] = True

    out: dict[str, Any] = {
        "name": safe_get(m, "name"),
        "longIdentifier": safe_get(m, "longIdentifier"),
        "datatype": safe_get(m, "datatype"),
        "conversion": safe_get(m, "conversion"),
        "resolution": safe_get(m, "resolution"),
        "accuracy": safe_get(m, "accuracy"),
        "lowerLimit": safe_get(m, "lowerLimit"),
        "upperLimit": safe_get(m, "upperLimit"),
        "address_type": safe_get(safe_get(m, "address_type"), "addrType"),
        "annotation": annotation_to_list(safe_get(m, "annotation")),
        "array_size": safe_get(arr, "number") if arr else None,
        "bit_mask": safe_get(bm, "mask") if bm else None,
        "bit_operation": bit_operation_dict,
        "byte_order": safe_get(safe_get(m, "byte_order"), "byteOrder"),
        "discrete": _bool_flag(safe_get(m, "discrete")),
        "display_identifier": safe_get(safe_get(m, "display_identifier"), "display_name"),
        "ecu_address": safe_get(safe_get(m, "ecu_address"), "address"),
        "ecu_address_extension": safe_get(safe_get(m, "ecu_address_extension"), "extension"),
        "error_mask": safe_get(safe_get(m, "error_mask"), "mask"),
        "format": safe_get(safe_get(m, "format"), "formatString"),
        "function_list": function_list_to_list(safe_get(m, "function_list")),
        "layout": safe_get(layout, "indexMode") if layout else None,
        "matrix_dim": matrix_dim_to_list(safe_get(m, "matrix_dim")),
        "max_refresh": max_refresh_to_dict(safe_get(m, "max_refresh")),
        "model_link": safe_get(safe_get(m, "model_link"), "modelLink"),
        "phys_unit": safe_get(safe_get(m, "phys_unit"), "unit"),
        "read_write": _bool_flag(safe_get(m, "read_write")),
        "ref_memory_segment": safe_get(safe_get(m, "ref_memory_segment"), "name"),
        "symbol_link": symbol_link_to_dict(safe_get(m, "symbol_link")),
        "virtual": virtual_list,
        "if_data_raw": ifdata_raw_list(safe_get(m, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(m, "if_data")),
        "min_passthrough": None,
    }
    if min_passthrough:
        out["min_passthrough"] = min_passthrough.get(safe_get(m, "conversion"))
    return out


def _min_passthrough_lookup(module: Any) -> dict[str, float]:
    tables: dict[str, Any] = {}
    for collection_name in ("compu_tab", "compu_vtab", "compu_vtab_range"):
        for tbl in as_list(safe_get(module, collection_name)):
            name = safe_get(tbl, "name")
            if name:
                tables[name] = tbl

    def _min_from_table(tbl: Any | None) -> float | None:
        if tbl is None:
            return None
        values: list[float] = []
        entries = as_list(safe_get(tbl, "pairs")) + as_list(safe_get(tbl, "triples"))
        for entry in entries:
            candidate = safe_get(entry, "inValMin")
            if candidate is None:
                candidate = safe_get(entry, "inVal")
            if candidate is None:
                continue
            try:
                values.append(float(candidate))
            except Exception:
                continue
        return min(values) if values else None

    lookup: dict[str, float] = {}
    for cm in as_list(safe_get(module, "compu_method")):
        ref = safe_get(cm, "compu_tab_ref")
        tab_name = safe_get(ref, "conversionTable") if ref else None
        if not tab_name:
            continue
        min_val = _min_from_table(tables.get(tab_name))
        name = safe_get(cm, "name")
        if min_val is not None and name:
            lookup[name] = min_val
    return lookup


def mod_common_to_dict(mc: Any) -> dict[str, Any] | None:
    if not mc:
        return None

    out: dict[str, Any] = {"comment": safe_get(mc, "comment")}

    for attr_name in (
        "alignment_byte",
        "alignment_float16_ieee",
        "alignment_float32_ieee",
        "alignment_float64_ieee",
        "alignment_int64",
        "alignment_long",
        "alignment_word",
    ):
        attr = safe_get(mc, attr_name)
        if attr and safe_get(attr, "alignmentBorder") is not None:
            out[attr_name] = safe_get(attr, "alignmentBorder")

    out["byte_order"] = safe_get(safe_get(mc, "byte_order"), "byteOrder")
    out["data_size"] = safe_get(safe_get(mc, "data_size"), "size")
    return out


def memory_layout_to_dict(session: Any, ml: Any) -> dict[str, Any]:
    out: dict[str, Any] = {
        "prgType": safe_get(ml, "prgType"),
        "address": safe_get(ml, "address"),
        "size": safe_get(ml, "size"),
        "offset_0": safe_get(ml, "offset_0"),
        "offset_1": safe_get(ml, "offset_1"),
        "offset_2": safe_get(ml, "offset_2"),
        "offset_3": safe_get(ml, "offset_3"),
        "offset_4": safe_get(ml, "offset_4"),
        "if_data_raw": ifdata_raw_list(safe_get(ml, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(ml, "if_data")),
    }
    return out


def memory_segment_to_dict(session: Any, ms: Any) -> dict[str, Any]:
    out: dict[str, Any] = {
        "name": safe_get(ms, "name"),
        "longIdentifier": safe_get(ms, "longIdentifier"),
        "prgType": safe_get(ms, "prgType"),
        "memoryType": safe_get(ms, "memoryType"),
        "attribute": safe_get(ms, "attribute"),
        "address": safe_get(ms, "address"),
        "size": safe_get(ms, "size"),
        "offset_0": safe_get(ms, "offset_0"),
        "offset_1": safe_get(ms, "offset_1"),
        "offset_2": safe_get(ms, "offset_2"),
        "offset_3": safe_get(ms, "offset_3"),
        "offset_4": safe_get(ms, "offset_4"),
        "if_data_raw": ifdata_raw_list(safe_get(ms, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(ms, "if_data")),
    }
    return out


def mod_par_to_dict(session: Any, mp: Any) -> dict[str, Any] | None:
    if not mp:
        return None

    out: dict[str, Any] = {
        "comment": safe_get(mp, "comment"),
        "addr_epk": [safe_get(a, "address") for a in as_list(safe_get(mp, "addr_epk"))],
        "calibration_method": [],
        "cpu_type": safe_get(safe_get(mp, "cpu_type"), "cPU"),
        "customer": safe_get(safe_get(mp, "customer"), "customer"),
        "customer_no": safe_get(safe_get(mp, "customer_no"), "number"),
        "ecu": safe_get(safe_get(mp, "ecu"), "controlUnit"),
        "ecu_calibration_offset": safe_get(safe_get(mp, "ecu_calibration_offset"), "offset"),
        "epk": safe_get(safe_get(mp, "epk"), "identifier"),
        "memory_layout": [memory_layout_to_dict(session, ml) for ml in as_list(safe_get(mp, "memory_layout"))],
        "memory_segment": [memory_segment_to_dict(session, ms) for ms in as_list(safe_get(mp, "memory_segment"))],
        "no_of_interfaces": safe_get(safe_get(mp, "no_of_interfaces"), "num"),
        "phone_no": safe_get(safe_get(mp, "phone_no"), "telnum"),
        "supplier": safe_get(safe_get(mp, "supplier"), "manufacturer"),
        "system_constant": [],
        "user": safe_get(safe_get(mp, "user"), "userName"),
        "version": safe_get(safe_get(mp, "version"), "versionIdentifier"),
    }

    for cm in as_list(safe_get(mp, "calibration_method")):
        cm_entry: dict[str, Any] = {
            "method": safe_get(cm, "method"),
            "version": safe_get(cm, "version"),
            "calibration_handle": [],
        }
        for ch in as_list(safe_get(cm, "calibration_handle")):
            cm_entry["calibration_handle"].append(
                {
                    "handle": list(as_list(safe_get(ch, "handle"))),
                    "calibration_handle_text": safe_get(safe_get(ch, "calibration_handle_text"), "text"),
                }
            )
        out["calibration_method"].append(cm_entry)

    for sc in as_list(safe_get(mp, "system_constant")):
        out["system_constant"].append({"name": safe_get(sc, "name"), "value": safe_get(sc, "value")})

    return out


def structure_component_to_dict(sc: Any) -> dict[str, Any]:
    num = safe_get(sc, "number")
    stl = safe_get(sc, "symbol_type_link")
    return {
        "name": safe_get(sc, "name"),
        "type_ref": safe_get(sc, "type_ref"),
        "offset": safe_get(sc, "offset"),
        "matrix_dim": matrix_dim_to_list(safe_get(sc, "matrix_dim")),
        "number": safe_get(num, "number") if num else None,
        "symbol_type_link": safe_get(stl, "link") if stl else None,
    }


def typedef_characteristic_to_dict(tc: Any) -> dict[str, Any]:
    return {
        "name": safe_get(tc, "name"),
        "longIdentifier": safe_get(tc, "longIdentifier"),
        "type": safe_get(tc, "type"),
        "deposit": safe_get(tc, "deposit"),
        "maxDiff": safe_get(tc, "maxDiff"),
        "conversion": safe_get(tc, "conversion"),
        "lowerLimit": safe_get(tc, "lowerLimit"),
        "upperLimit": safe_get(tc, "upperLimit"),
        "annotation": annotation_to_list(safe_get(tc, "annotation")),
        "matrix_dim": matrix_dim_to_list(safe_get(tc, "matrix_dim")),
    }


def typedef_measurement_to_dict(tm: Any) -> dict[str, Any]:
    return {
        "name": safe_get(tm, "name"),
        "longIdentifier": safe_get(tm, "longIdentifier"),
        "datatype": safe_get(tm, "datatype"),
        "conversion": safe_get(tm, "conversion"),
        "resolution": safe_get(tm, "resolution"),
        "accuracy": safe_get(tm, "accuracy"),
        "lowerLimit": safe_get(tm, "lowerLimit"),
        "upperLimit": safe_get(tm, "upperLimit"),
    }


def blob_to_dict(session: Any, b: Any) -> dict[str, Any]:
    return {
        "name": safe_get(b, "name"),
        "longIdentifier": safe_get(b, "longIdentifier"),
        "address": safe_get(b, "address"),
        "length": safe_get(b, "length"),
        "address_type": safe_get(safe_get(b, "address_type"), "addrType"),
        "annotation": annotation_to_list(safe_get(b, "annotation")),
        "calibration_access": safe_get(safe_get(b, "calibration_access"), "type"),
        "display_identifier": safe_get(safe_get(b, "display_identifier"), "display_name"),
        "ecu_address_extension": safe_get(safe_get(b, "ecu_address_extension"), "extension"),
        "max_refresh": max_refresh_to_dict(safe_get(b, "max_refresh")),
        "symbol_link": symbol_link_to_dict(safe_get(b, "symbol_link")),
    }


def typedef_axis_to_dict(ta: Any) -> dict[str, Any]:
    return {
        "name": safe_get(ta, "name"),
        "longIdentifier": safe_get(ta, "longIdentifier"),
        "inputQuantity": safe_get(ta, "inputQuantity"),
        "depositAttr": safe_get(ta, "depositAttr"),
        "maxDiff": safe_get(ta, "maxDiff"),
        "conversion": safe_get(ta, "conversion"),
        "maxAxisPoints": safe_get(ta, "maxAxisPoints"),
        "lowerLimit": safe_get(ta, "lowerLimit"),
        "upperLimit": safe_get(ta, "upperLimit"),
        "annotation": annotation_to_list(safe_get(ta, "annotation")),
        "byte_order": safe_get(safe_get(ta, "byte_order"), "byteOrder"),
        "calibration_access": safe_get(safe_get(ta, "calibration_access"), "type"),
        "deposit": safe_get(safe_get(ta, "deposit"), "mode"),
        "extended_limits": (
            None
            if not safe_get(ta, "extended_limits")
            else {
                "lowerLimit": safe_get(ta.extended_limits, "lowerLimit"),
                "upperLimit": safe_get(ta.extended_limits, "upperLimit"),
            }
        ),
        "format": safe_get(safe_get(ta, "format"), "format"),
        "guard_rails": _bool_flag(safe_get(ta, "guard_rails")),
        "monotony": safe_get(safe_get(ta, "monotony"), "monotony"),
        "phys_unit": safe_get(safe_get(ta, "phys_unit"), "unit"),
        "read_only": _bool_flag(safe_get(ta, "read_only")),
        "ref_memory_segment": safe_get(safe_get(ta, "ref_memory_segment"), "name"),
        "step_size": safe_get(safe_get(ta, "step_size"), "stepSize"),
    }


def transformer_to_dict(tr: Any) -> dict[str, Any]:
    return {
        "name": safe_get(tr, "name"),
        "version": safe_get(tr, "version"),
        "dllname32": safe_get(tr, "dllname32"),
        "dllname64": safe_get(tr, "dllname64"),
        "timeout": safe_get(tr, "timeout"),
        "trigger": safe_get(tr, "trigger"),
        "reverse": safe_get(tr, "reverse"),
        "transformer_in_objects": list(as_list(safe_get(safe_get(tr, "transformer_in_objects"), "identifier"))),
        "transformer_out_objects": list(as_list(safe_get(safe_get(tr, "transformer_out_objects"), "identifier"))),
    }


def _column_dict(obj: Any) -> dict[str, Any]:
    if obj is None:
        return {}
    cols = [c.name for c in getattr(obj, "__table__").columns if not c.name.endswith("_rid") and c.name not in ("rid",)]
    return {col: safe_get(obj, col) for col in cols}


def record_layout_to_dict(rl: Any) -> dict[str, Any]:
    out: dict[str, Any] = {"name": safe_get(rl, "name"), "entries": []}
    for elem in getattr(rl, "__optional_elements__", ()):
        attr = re.sub(r"(?<!^)(?=[A-Z])", "_", elem.name).lower()
        data = safe_get(rl, attr)
        if data is None:
            continue
        for item in as_list(data):
            out["entries"].append({"keyword": elem.keyword_name, "values": _column_dict(item)})
    return out


def typedef_structure_to_dict(ts: Any) -> dict[str, Any]:
    stl = safe_get(ts, "symbol_type_link")
    return {
        "name": safe_get(ts, "name"),
        "longIdentifier": safe_get(ts, "longIdentifier"),
        "size": safe_get(ts, "size"),
        "structure_component": [structure_component_to_dict(sc) for sc in as_list(safe_get(ts, "structure_component"))],
        "symbol_type_link": safe_get(stl, "link") if stl else None,
    }


def unit_to_dict(u: Any) -> dict[str, Any]:
    si = safe_get(u, "si_exponents")
    uc = safe_get(u, "unit_conversion")
    ru = safe_get(u, "ref_unit")

    out: dict[str, Any] = {
        "name": safe_get(u, "name"),
        "longIdentifier": safe_get(u, "longIdentifier"),
        "display": safe_get(u, "display"),
        "type": safe_get(u, "type"),
        "si_exponents": None,
        "ref_unit": safe_get(ru, "unit") if ru else None,
        "unit_conversion": None,
    }

    if si:
        out["si_exponents"] = {
            "length": safe_get(si, "length"),
            "mass": safe_get(si, "mass"),
            "time": safe_get(si, "time"),
            "electricCurrent": safe_get(si, "electricCurrent"),
            "temperature": safe_get(si, "temperature"),
            "amountOfSubstance": safe_get(si, "amountOfSubstance"),
            "luminousIntensity": safe_get(si, "luminousIntensity"),
        }

    if uc:
        out["unit_conversion"] = {"gradient": safe_get(uc, "gradient"), "offset": safe_get(uc, "offset")}

    return out


def user_rights_to_dict(ur: Any) -> dict[str, Any]:
    ref_groups: list[dict[str, Any]] = []
    for r in as_list(safe_get(ur, "ref_group")):
        ref_groups.append({"identifier": safe_get(r, "identifier")})

    return {
        "userLevelId": safe_get(ur, "userLevelId"),
        "read_only": _bool_flag(safe_get(ur, "read_only")),
        "ref_group": ref_groups,
    }


def variant_coding_to_dict(vc: Any) -> dict[str, Any] | None:
    if not vc:
        return None

    var_characteristic: list[dict[str, Any]] = []
    for v in as_list(safe_get(vc, "var_characteristic")):
        va = safe_get(v, "var_address")
        addr: list[Any] | None = None
        if va and safe_get(va, "address"):
            addr = [x for x in va.address]

        var_characteristic.append(
            {
                "name": safe_get(v, "name"),
                "criterionName": safe_get(v, "criterionName"),
                "var_address": addr,
            }
        )

    var_criterion: list[dict[str, Any]] = []
    for c in as_list(safe_get(vc, "var_criterion")):
        vm = safe_get(c, "var_measurement")
        vsc = safe_get(c, "var_selection_characteristic")
        var_criterion.append(
            {
                "name": safe_get(c, "name"),
                "longIdentifier": safe_get(c, "longIdentifier"),
                "value": safe_get(c, "value"),
                "var_measurement": safe_get(vm, "name") if vm else None,
                "var_selection_characteristic": safe_get(vsc, "name") if vsc else None,
            }
        )

    return {"var_characteristic": var_characteristic, "var_criterion": var_criterion}


def module_to_dict(session: Any, mod: Any) -> dict[str, Any]:
    """MODULE to dict (matching exporter_new.py coverage)."""
    aml_section = session.query(model.AMLSection).first()
    min_passthrough = _min_passthrough_lookup(mod)

    try:
        transformers = [transformer_to_dict(tr) for tr in as_list(safe_get(mod, "transformer"))]
    except OperationalError as exc:
        logging.getLogger(__name__).warning("Skipping TRANSFORMER export due to schema mismatch: %s", exc)
        transformers = []

    try:
        record_layouts = [record_layout_to_dict(rl) for rl in as_list(safe_get(mod, "record_layout"))]
    except OperationalError as exc:
        logging.getLogger(__name__).warning("Skipping RECORD_LAYOUT export due to schema mismatch: %s", exc)
        record_layouts = []

    out: dict[str, Any] = {
        "name": safe_get(mod, "name"),
        "longIdentifier": safe_get(mod, "longIdentifier"),
        "aml_section_text": safe_get(aml_section, "text") if aml_section else None,
        "axis_pts": [axis_pts_to_dict(session, ap) for ap in as_list(safe_get(mod, "axis_pts"))],
        "characteristic": [characteristic_to_dict(session, ch) for ch in as_list(safe_get(mod, "characteristic"))],
        "compu_method": [compu_method_to_dict(cm) for cm in as_list(safe_get(mod, "compu_method"))],
        "compu_tab": [compu_tab_to_dict(t) for t in as_list(safe_get(mod, "compu_tab"))],
        "compu_vtab": [compu_vtab_to_dict(t) for t in as_list(safe_get(mod, "compu_vtab"))],
        "compu_vtab_range": [compu_vtab_range_to_dict(t) for t in as_list(safe_get(mod, "compu_vtab_range"))],
        "frame": [frame_to_dict(session, f) for f in as_list(safe_get(mod, "frame"))],
        "function": [function_to_dict(session, fn) for fn in as_list(safe_get(mod, "function"))],
        "group": [group_to_dict(session, g) for g in as_list(safe_get(mod, "group"))],
        "instance": [instance_to_dict(session, i) for i in as_list(safe_get(mod, "instance"))],
        "measurement": [measurement_to_dict(session, m, min_passthrough) for m in as_list(safe_get(mod, "measurement"))],
        "mod_common": mod_common_to_dict(safe_get(mod, "mod_common")),
        "mod_par": mod_par_to_dict(session, safe_get(mod, "mod_par")),
        "typedef_characteristic": [typedef_characteristic_to_dict(tc) for tc in as_list(safe_get(mod, "typedef_characteristic"))],
        "typedef_measurement": [typedef_measurement_to_dict(tm) for tm in as_list(safe_get(mod, "typedef_measurement"))],
        "typedef_structure": [typedef_structure_to_dict(ts) for ts in as_list(safe_get(mod, "typedef_structure"))],
        "typedef_axis": [typedef_axis_to_dict(ta) for ta in as_list(safe_get(mod, "typedef_axis"))],
        "unit": [unit_to_dict(u) for u in as_list(safe_get(mod, "unit"))],
        "user_rights": [user_rights_to_dict(ur) for ur in as_list(safe_get(mod, "user_rights"))],
        "variant_coding": variant_coding_to_dict(safe_get(mod, "variant_coding")),
        "if_data_raw": ifdata_raw_list(safe_get(mod, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(mod, "if_data")),
        "blob": [blob_to_dict(session, b) for b in as_list(safe_get(mod, "blob"))],
        "record_layout": record_layouts,
        "transformer": transformers,
    }
    return out


def project_to_dict(db: A2LDatabase, module_name: str | None = None) -> dict[str, Any]:
    """Create a serializable dict for the entire project."""
    session = db.session
    proj = session.query(model.Project).first()
    if proj is None:
        raise RuntimeError("No Project row found in the database.")

    header_obj = safe_get(proj, "header")
    header: dict[str, Any] | None = None
    if header_obj:
        header = {
            "comment": safe_get(header_obj, "comment"),
            "project_no": safe_get(safe_get(header_obj, "project_no"), "projectNumber"),
            "version": safe_get(safe_get(header_obj, "version"), "versionIdentifier"),
        }

    record_layout_opt = selectinload(model.Module.record_layout)
    transformer_opt = selectinload(model.Module.transformer)
    module_opts = [
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
    modules_query = session.query(model.Module).options(*module_opts)
    if module_name:
        modules_query = modules_query.filter(model.Module.name == module_name)
    try:
        modules = modules_query.all()
    except OperationalError as exc:
        logging.getLogger(__name__).warning(
            "Module preload failed (schema mismatch?). Retrying without RECORD_LAYOUT/TRANSFORMER: %s", exc
        )
        fallback_opts = [opt for opt in module_opts if opt not in (record_layout_opt, transformer_opt)]
        modules_query = session.query(model.Module).options(*fallback_opts)
        if module_name:
            modules_query = modules_query.filter(model.Module.name == module_name)
        modules = modules_query.all()

    out: dict[str, Any] = {
        "name": safe_get(proj, "name"),
        "longIdentifier": safe_get(proj, "longIdentifier"),
        "header": header,
        "modules": [module_to_dict(session, mod) for mod in modules],
        "if_data_raw": ifdata_raw_list(safe_get(proj, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(proj, "if_data")),
    }
    return out


def parse_args(argv: list[str] | None = None) -> ExporterConfig:
    """Parse CLI arguments and build ExporterConfig."""
    parser = argparse.ArgumentParser(description="Export a2ldb -> JSON (pyA2L).")
    parser.add_argument(
        "database",
        type=Path,
        help="Path to the a2ldb file (or basename without .a2ldb).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output file (.json). Default: <db>.json",
    )
    parser.add_argument(
        "-m",
        "--module",
        type=str,
        help="Optional: export only this module.",
        default=None,
    )
    parser.add_argument("--pretty", action="store_true", help="Write formatted JSON.")
    parser.add_argument(
        "-l",
        "--loglevel",
        type=str,
        help="Log level (DEBUG, INFO, WARNING).",
        default="INFO",
    )
    args = parser.parse_args(argv)

    db_path = args.database
    if not db_path.exists():
        candidate = db_path.with_suffix(".a2ldb")
        if candidate.exists():
            db_path = candidate
        else:
            raise FileNotFoundError(f"DB-Datei nicht gefunden: {args.database}")

    out_path = args.output or db_path.with_suffix(".json")
    return ExporterConfig(
        db_path=db_path,
        out_path=out_path,
        module_name=args.module,
        pretty=args.pretty,
        loglevel=args.loglevel,
    )


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    cfg = parse_args(argv)
    setup_logging(cfg.loglevel)
    logger = logging.getLogger(__name__)
    logger.info("Starting JSON export...")

    db = open_database(cfg.db_path, cfg.loglevel)
    try:
        data = project_to_dict(db, cfg.module_name)
        logger.info("Writing JSON to %s", cfg.out_path)
        with cfg.out_path.open("w", encoding="utf-8") as fh:
            if cfg.pretty:
                json.dump(data, fh, ensure_ascii=False, indent=4)
            else:
                json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
    finally:
        try:
            db.close()
        except Exception:
            logger.debug("Error while closing the database.", exc_info=True)

    logger.info("Export finished. File: %s", cfg.out_path)


if __name__ == "__main__":
    main()
