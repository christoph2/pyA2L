#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Exporter: a2ldb -> JSON.

Vollständiger JSON-Exporter im gleichen Umfang wie exporter_new.py.
Robust, PEP8, Dataclasses, Typannotationen und Logging.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence
import argparse
import json
import logging

from pya2l.model import A2LDatabase
import pya2l.model as model


@dataclass
class ExporterConfig:
    """Konfiguration für den JSON-Exporter."""
    db_path: Path
    out_path: Path
    module_name: Optional[str]
    pretty: bool
    loglevel: str = "INFO"


def setup_logging(level: str) -> None:
    """Basis-Logging konfigurieren."""
    numeric = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(level=numeric, format="%(levelname)s: %(message)s")


def open_database(db_path: Path, loglevel: str = "INFO") -> A2LDatabase:
    """A2LDatabase öffnen; IfData-Parser optional initialisieren."""
    db = A2LDatabase(str(db_path), debug=False, logLevel=loglevel)
    try:
        db.session.setup_ifdata_parser(loglevel)
    except Exception:
        logging.getLogger(__name__).debug(
            "IfData parser nicht initialisierbar.",
            exc_info=True,
        )
    return db


def safe_get(obj: Any, attr: str) -> Any:
    """Sicheres getattr mit None-Rückfall."""
    try:
        return getattr(obj, attr)
    except Exception:
        return None


def as_list(value: Any) -> List[Any]:
    """Normalisiert iterierbare ORM-Felder zu Python-Listen."""
    if not value:
        return []
    if isinstance(value, list):
        return value
    try:
        return list(value)
    except Exception:
        return [value]


def _bool_flag(obj: Any) -> bool:
    """ORM-Flagfelder sind oft als eigenes Objekt modelliert."""
    return bool(obj)


def matrix_dim_to_list(matrix_dim_obj: Any) -> Optional[List[int]]:
    """MATRIX_DIM als Liste von ints."""
    if not matrix_dim_obj:
        return None
    nums = safe_get(matrix_dim_obj, "numbers")
    if not nums:
        return None
    try:
        return [int(x) for x in nums]
    except Exception:
        return [int(x) for x in list(nums)]


def function_list_to_list(function_list_obj: Any) -> List[str]:
    """FUNCTION_LIST als Liste von Namen (Strings)."""
    if not function_list_obj:
        return []
    names = safe_get(function_list_obj, "name")
    if not names:
        return []
    return [str(x) for x in names]


def symbol_link_to_dict(symbol_link_obj: Any) -> Optional[Dict[str, Any]]:
    """SYMBOL_LINK als Dict."""
    if not symbol_link_obj:
        return None
    return {
        "symbolName": safe_get(symbol_link_obj, "symbolName"),
        "offset": safe_get(symbol_link_obj, "offset"),
    }


def max_refresh_to_dict(max_refresh_obj: Any) -> Optional[Dict[str, Any]]:
    """MAX_REFRESH als Dict."""
    if not max_refresh_obj:
        return None
    return {
        "scalingUnit": safe_get(max_refresh_obj, "scalingUnit"),
        "rate": safe_get(max_refresh_obj, "rate"),
    }


def ifdata_raw_list(sections: Optional[Iterable[Any]]) -> List[str]:
    """Rohtexte der IF_DATA-Sektionen sammeln (falls vorhanden)."""
    raws: List[str] = []
    for s in as_list(sections):
        raw = safe_get(s, "raw")
        if raw and str(raw).strip():
            raws.append(str(raw))
    return raws


def ifdata_parsed_list(session: Any, sections: Optional[Sequence[Any]]) -> List[Any]:
    """IF_DATA parsen (best effort)."""
    if not sections:
        return []
    try:
        parsed = session.parse_ifdata(sections)
        return parsed or []
    except Exception:
        logging.getLogger(__name__).debug("Fehler beim Parsen von IF_DATA.", exc_info=True)
        return []


def annotation_to_list(annos: Optional[Iterable[Any]]) -> List[Dict[str, Any]]:
    """Annotationen in einfache Dicts umwandeln."""
    result: List[Dict[str, Any]] = []
    for a in as_list(annos):
        label = safe_get(a, "annotation_label")
        origin = safe_get(a, "annotation_origin")
        text = safe_get(a, "annotation_text")

        lines: List[str] = []
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


def axis_descr_to_dict(session: Any, ad: Any) -> Dict[str, Any]:
    """AXIS_DESCR -> Dict."""
    out: Dict[str, Any] = {
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


def axis_pts_to_dict(session: Any, ap: Any) -> Dict[str, Any]:
    """AXIS_PTS -> Dict."""
    out: Dict[str, Any] = {
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
        "function_list": function_list_to_list(safe_get(ap, "function_list")),
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


def characteristic_to_dict(session: Any, ch: Any) -> Dict[str, Any]:
    """CHARACTERISTIC -> Dict."""
    out: Dict[str, Any] = {
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
        "function_list": function_list_to_list(safe_get(ch, "function_list")),
        "matrix_dim": matrix_dim_to_list(safe_get(ch, "matrix_dim")),
        "max_refresh": max_refresh_to_dict(safe_get(ch, "max_refresh")),
        "phys_unit": safe_get(safe_get(ch, "phys_unit"), "unit"),
        "read_only": _bool_flag(safe_get(ch, "read_only")),
        "ref_memory_segment": safe_get(safe_get(ch, "ref_memory_segment"), "name"),
        "step_size": safe_get(safe_get(ch, "step_size"), "stepSize"),
        "if_data_raw": ifdata_raw_list(safe_get(ch, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(ch, "if_data")),
    }
    return out


def compu_method_to_dict(cm: Any) -> Dict[str, Any]:
    """COMPU_METHOD -> Dict."""
    out: Dict[str, Any] = {
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


def _compu_tab_common(t: Any) -> Dict[str, Any]:
    base: Dict[str, Any] = {
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


def compu_tab_to_dict(t: Any) -> Dict[str, Any]:
    out = _compu_tab_common(t)
    out.update(
        {
            "kind": "COMPU_TAB",
            "conversionType": safe_get(t, "conversionType"),
            "numberValuePairs": safe_get(t, "numberValuePairs"),
        }
    )
    return out


def compu_vtab_to_dict(t: Any) -> Dict[str, Any]:
    out = _compu_tab_common(t)
    out.update(
        {
            "kind": "COMPU_VTAB",
            "conversionType": safe_get(t, "conversionType"),
            "numberValuePairs": safe_get(t, "numberValuePairs"),
        }
    )
    return out


def compu_vtab_range_to_dict(t: Any) -> Dict[str, Any]:
    out = _compu_tab_common(t)
    out.update(
        {
            "kind": "COMPU_VTAB_RANGE",
            "numberValueTriples": safe_get(t, "numberValueTriples"),
        }
    )
    return out


def frame_to_dict(session: Any, fr: Any) -> Dict[str, Any]:
    fm = safe_get(fr, "frame_measurement")
    identifiers: Optional[List[str]] = None
    if fm and safe_get(fm, "identifier"):
        identifiers = [str(x) for x in fm.identifier]

    out: Dict[str, Any] = {
        "name": safe_get(fr, "name"),
        "longIdentifier": safe_get(fr, "longIdentifier"),
        "scalingUnit": safe_get(fr, "scalingUnit"),
        "rate": safe_get(fr, "rate"),
        "frame_measurement": identifiers,
        "if_data_raw": ifdata_raw_list(safe_get(fr, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(fr, "if_data")),
    }
    return out


def function_to_dict(session: Any, fn: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {
        "name": safe_get(fn, "name"),
        "longIdentifier": safe_get(fn, "longIdentifier"),
        "annotation": annotation_to_list(safe_get(fn, "annotation")),
        "def_characteristic": None,
        "function_version": None,
        "in_measurement": None,
        "loc_measurement": None,
        "out_measurement": None,
        "ref_characteristic": None,
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

    return out


def group_to_dict(session: Any, g: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {
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


def instance_to_dict(session: Any, inst: Any) -> Dict[str, Any]:
    num = safe_get(inst, "number")
    out: Dict[str, Any] = {
        "name": safe_get(inst, "name"),
        "longIdentifier": safe_get(inst, "longIdentifier"),
        "typeName": safe_get(inst, "typeName"),
        "address": safe_get(inst, "address"),
        "number": safe_get(num, "number") if num else None,
        "matrix_dim": matrix_dim_to_list(safe_get(inst, "matrix_dim")),
        "symbol_link": symbol_link_to_dict(safe_get(inst, "symbol_link")),
        "if_data_raw": ifdata_raw_list(safe_get(inst, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(inst, "if_data")),
    }
    return out


def measurement_to_dict(session: Any, m: Any) -> Dict[str, Any]:
    arr = safe_get(m, "array_size")
    bm = safe_get(m, "bit_mask")
    layout = safe_get(m, "layout")

    virtual = safe_get(m, "virtual")
    virtual_list: Optional[List[str]] = None
    if virtual and safe_get(virtual, "measuringChannel"):
        virtual_list = [str(x) for x in virtual.measuringChannel]

    out: Dict[str, Any] = {
        "name": safe_get(m, "name"),
        "longIdentifier": safe_get(m, "longIdentifier"),
        "datatype": safe_get(m, "datatype"),
        "conversion": safe_get(m, "conversion"),
        "resolution": safe_get(m, "resolution"),
        "accuracy": safe_get(m, "accuracy"),
        "lowerLimit": safe_get(m, "lowerLimit"),
        "upperLimit": safe_get(m, "upperLimit"),
        "annotation": annotation_to_list(safe_get(m, "annotation")),
        "array_size": safe_get(arr, "number") if arr else None,
        "bit_mask": safe_get(bm, "mask") if bm else None,
        "layout": safe_get(layout, "indexMode") if layout else None,
        "matrix_dim": matrix_dim_to_list(safe_get(m, "matrix_dim")),
        "max_refresh": max_refresh_to_dict(safe_get(m, "max_refresh")),
        "phys_unit": safe_get(safe_get(m, "phys_unit"), "unit"),
        "read_write": _bool_flag(safe_get(m, "read_write")),
        "ref_memory_segment": safe_get(safe_get(m, "ref_memory_segment"), "name"),
        "symbol_link": symbol_link_to_dict(safe_get(m, "symbol_link")),
        "virtual": virtual_list,
        "if_data_raw": ifdata_raw_list(safe_get(m, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(m, "if_data")),
    }
    return out


def mod_common_to_dict(mc: Any) -> Optional[Dict[str, Any]]:
    if not mc:
        return None

    out: Dict[str, Any] = {"comment": safe_get(mc, "comment")}

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


def memory_layout_to_dict(session: Any, ml: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {
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


def memory_segment_to_dict(session: Any, ms: Any) -> Dict[str, Any]:
    out: Dict[str, Any] = {
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


def mod_par_to_dict(session: Any, mp: Any) -> Optional[Dict[str, Any]]:
    if not mp:
        return None

    out: Dict[str, Any] = {
        "comment": safe_get(mp, "comment"),
        "memory_layout": [memory_layout_to_dict(session, ml) for ml in as_list(safe_get(mp, "memory_layout"))],
        "memory_segment": [memory_segment_to_dict(session, ms) for ms in as_list(safe_get(mp, "memory_segment"))],
        "no_of_interfaces": safe_get(safe_get(mp, "no_of_interfaces"), "num"),
        "phone_no": safe_get(safe_get(mp, "phone_no"), "telnum"),
        "supplier": safe_get(safe_get(mp, "supplier"), "manufacturer"),
        "system_constant": [],
    }

    for sc in as_list(safe_get(mp, "system_constant")):
        out["system_constant"].append({"name": safe_get(sc, "name"), "value": safe_get(sc, "value")})

    return out


def structure_component_to_dict(sc: Any) -> Dict[str, Any]:
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


def typedef_characteristic_to_dict(tc: Any) -> Dict[str, Any]:
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


def typedef_measurement_to_dict(tm: Any) -> Dict[str, Any]:
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


def typedef_structure_to_dict(ts: Any) -> Dict[str, Any]:
    stl = safe_get(ts, "symbol_type_link")
    return {
        "name": safe_get(ts, "name"),
        "longIdentifier": safe_get(ts, "longIdentifier"),
        "size": safe_get(ts, "size"),
        "structure_component": [
            structure_component_to_dict(sc) for sc in as_list(safe_get(ts, "structure_component"))
        ],
        "symbol_type_link": safe_get(stl, "link") if stl else None,
    }


def unit_to_dict(u: Any) -> Dict[str, Any]:
    si = safe_get(u, "si_exponents")
    uc = safe_get(u, "unit_conversion")
    ru = safe_get(u, "ref_unit")

    out: Dict[str, Any] = {
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


def user_rights_to_dict(ur: Any) -> Dict[str, Any]:
    ref_groups: List[Dict[str, Any]] = []
    for r in as_list(safe_get(ur, "ref_group")):
        ref_groups.append({"identifier": safe_get(r, "identifier")})

    return {
        "userLevelId": safe_get(ur, "userLevelId"),
        "read_only": _bool_flag(safe_get(ur, "read_only")),
        "ref_group": ref_groups,
    }


def variant_coding_to_dict(vc: Any) -> Optional[Dict[str, Any]]:
    if not vc:
        return None

    var_characteristic: List[Dict[str, Any]] = []
    for v in as_list(safe_get(vc, "var_characteristic")):
        va = safe_get(v, "var_address")
        addr: Optional[List[Any]] = None
        if va and safe_get(va, "address"):
            addr = [x for x in va.address]

        var_characteristic.append(
            {
                "name": safe_get(v, "name"),
                "criterionName": safe_get(v, "criterionName"),
                "var_address": addr,
            }
        )

    var_criterion: List[Dict[str, Any]] = []
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


def module_to_dict(session: Any, mod: Any) -> Dict[str, Any]:
    """MODULE -> Dict (Umfang wie exporter_new.py)."""
    aml_section = session.query(model.AMLSection).first()

    out: Dict[str, Any] = {
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
        "measurement": [measurement_to_dict(session, m) for m in as_list(safe_get(mod, "measurement"))],
        "mod_common": mod_common_to_dict(safe_get(mod, "mod_common")),
        "mod_par": mod_par_to_dict(session, safe_get(mod, "mod_par")),
        "typedef_characteristic": [
            typedef_characteristic_to_dict(tc) for tc in as_list(safe_get(mod, "typedef_characteristic"))
        ],
        "typedef_measurement": [
            typedef_measurement_to_dict(tm) for tm in as_list(safe_get(mod, "typedef_measurement"))
        ],
        "typedef_structure": [
            typedef_structure_to_dict(ts) for ts in as_list(safe_get(mod, "typedef_structure"))
        ],
        "unit": [unit_to_dict(u) for u in as_list(safe_get(mod, "unit"))],
        "user_rights": [user_rights_to_dict(ur) for ur in as_list(safe_get(mod, "user_rights"))],
        "variant_coding": variant_coding_to_dict(safe_get(mod, "variant_coding")),
        "if_data_raw": ifdata_raw_list(safe_get(mod, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(mod, "if_data")),
    }
    return out


def project_to_dict(db: A2LDatabase, module_name: Optional[str] = None) -> Dict[str, Any]:
    """Erzeuge ein serialisierbares Dict für das komplette Projekt."""
    session = db.session
    proj = session.query(model.Project).first()
    if proj is None:
        raise RuntimeError("Keine Project-Zeile in der Datenbank gefunden.")

    header_obj = safe_get(proj, "header")
    header: Optional[Dict[str, Any]] = None
    if header_obj:
        header = {
            "comment": safe_get(header_obj, "comment"),
            "project_no": safe_get(safe_get(header_obj, "project_no"), "projectNumber"),
            "version": safe_get(safe_get(header_obj, "version"), "versionIdentifier"),
        }

    modules_query = session.query(model.Module)
    if module_name:
        modules_query = modules_query.filter(model.Module.name == module_name)
    modules = modules_query.all()

    out: Dict[str, Any] = {
        "name": safe_get(proj, "name"),
        "longIdentifier": safe_get(proj, "longIdentifier"),
        "header": header,
        "modules": [module_to_dict(session, mod) for mod in modules],
        "if_data_raw": ifdata_raw_list(safe_get(proj, "if_data")),
        "if_data_parsed": ifdata_parsed_list(session, safe_get(proj, "if_data")),
    }
    return out


def parse_args(argv: Optional[List[str]] = None) -> ExporterConfig:
    """Argumente parsen und ExporterConfig erzeugen."""
    parser = argparse.ArgumentParser(description="Export a2ldb -> JSON (pyA2L).")
    parser.add_argument(
        "database",
        type=Path,
        help="Pfad zur a2ldb-Datei (oder basename ohne .a2ldb).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Ausgabedatei (.json). Standard: <db>.json",
    )
    parser.add_argument(
        "-m",
        "--module",
        type=str,
        help="Optional: nur dieses Modul exportieren.",
        default=None,
    )
    parser.add_argument("--pretty", action="store_true", help="Schreibe formatiertes JSON.")
    parser.add_argument(
        "-l",
        "--loglevel",
        type=str,
        help="Log-Level (DEBUG, INFO, WARNING).",
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


def main(argv: Optional[List[str]] = None) -> None:
    """CLI entry point."""
    cfg = parse_args(argv)
    setup_logging(cfg.loglevel)
    logger = logging.getLogger(__name__)
    logger.info("Starte JSON-Export...")

    db = open_database(cfg.db_path, cfg.loglevel)
    try:
        data = project_to_dict(db, cfg.module_name)
        logger.info("Schreibe JSON nach %s", cfg.out_path)
        with cfg.out_path.open("w", encoding="utf-8") as fh:
            if cfg.pretty:
                json.dump(data, fh, ensure_ascii=False, indent=4)
            else:
                json.dump(data, fh, ensure_ascii=False, separators=(",", ":"))
    finally:
        try:
            db.close()
        except Exception:
            logger.debug("Fehler beim Schließen der Datenbank.", exc_info=True)

    logger.info("Export beendet. Datei: %s", cfg.out_path)


if __name__ == "__main__":
    main()
