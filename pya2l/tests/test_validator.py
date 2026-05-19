"""Tests for pya2l.api.validate.Validator."""

import hashlib

import pytest

from pya2l.a2lparser import A2LParser
from pya2l.api.validate import Category, Diagnostics, Level, Message, Validator


def _parse(tmp_path, a2l_content: str):
    h = hashlib.md5(a2l_content.encode("latin-1"), usedforsecurity=False).hexdigest()[:8]
    a2l_file = tmp_path / f"tv_{h}.a2l"
    a2l_file.write_text(a2l_content, encoding="latin-1")
    return A2LParser().parse(str(a2l_file), in_memory=True)


def _diag_codes(messages):
    return [m.diag_code for m in messages]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

PREAMBLE = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
  /begin MODULE TestModule ""
"""
POSTAMBLE = """
  /end MODULE
/end PROJECT
"""


def _a2l(*body_lines):
    return PREAMBLE + "\n".join(body_lines) + POSTAMBLE


# ---------------------------------------------------------------------------
# MOD_COMMON checks
# ---------------------------------------------------------------------------


def test_missing_byte_order(tmp_path):
    a2l = _a2l(
        '/begin MOD_COMMON ""',
        "/end MOD_COMMON",
    )
    db = _parse(tmp_path, a2l)
    msgs = Validator(db.session)()
    codes = _diag_codes(msgs)
    assert Diagnostics.MISSING_BYTE_ORDER in codes


def test_missing_alignment(tmp_path):
    a2l = _a2l(
        '/begin MOD_COMMON ""',
        "  BYTE_ORDER MSB_LAST",
        "/end MOD_COMMON",
    )
    db = _parse(tmp_path, a2l)
    msgs = Validator(db.session)()
    codes = _diag_codes(msgs)
    assert Diagnostics.MISSING_ALIGNMENT in codes


def test_no_module(tmp_path):
    a2l = """
ASAP2_VERSION 1 71
/begin PROJECT TestProject ""
/end PROJECT
"""
    db = _parse(tmp_path, a2l)
    msgs = Validator(db.session)()
    assert Diagnostics.MISSING_MODULE in _diag_codes(msgs)


# ---------------------------------------------------------------------------
# Cross-reference checks — COMPU_METHOD
# ---------------------------------------------------------------------------

RECORD_LAYOUT_SNIPPET = """
/begin RECORD_LAYOUT RL_UBYTE
  FNC_VALUES 1 UBYTE ROW_DIR DIRECT
/end RECORD_LAYOUT
"""

COMPU_METHOD_SNIPPET = """
/begin COMPU_METHOD CM_LINEAR ""
  TAB_NOINTP "%6.3" ""
  COEFFS_LINEAR 1.0 0.0
/end COMPU_METHOD
"""

MEASUREMENT_SNIPPET = """
/begin MEASUREMENT MEAS_1 ""
  FLOAT32_IEEE CM_LINEAR 0 0 0 100
/end MEASUREMENT
"""

MEASUREMENT_BAD_CM_SNIPPET = """
/begin MEASUREMENT MEAS_BAD ""
  FLOAT32_IEEE NONEXISTENT_CM 0 0 0 100
/end MEASUREMENT
"""

CHARACTERISTIC_SNIPPET = """
/begin CHARACTERISTIC CHAR_1 "" VALUE 0x0 RL_UBYTE 0 CM_LINEAR 0 100
/end CHARACTERISTIC
"""

CHARACTERISTIC_BAD_CM_SNIPPET = """
/begin CHARACTERISTIC CHAR_BAD "" VALUE 0x0 RL_UBYTE 0 NONEXISTENT_CM 0 100
/end CHARACTERISTIC
"""

CHARACTERISTIC_BAD_RL_SNIPPET = """
/begin CHARACTERISTIC CHAR_BAD_RL "" VALUE 0x0 NONEXISTENT_RL 0 CM_LINEAR 0 100
/end CHARACTERISTIC
"""


def _full_a2l(*snippets):
    return PREAMBLE + "\n".join(snippets) + POSTAMBLE


def test_valid_compu_method_ref(tmp_path):
    a2l = _full_a2l(COMPU_METHOD_SNIPPET, MEASUREMENT_SNIPPET, RECORD_LAYOUT_SNIPPET, CHARACTERISTIC_SNIPPET)
    db = _parse(tmp_path, a2l)
    msgs = Validator(db.session)()
    codes = _diag_codes(msgs)
    assert Diagnostics.MISSING_COMPU_METHOD not in codes
    assert Diagnostics.MISSING_RECORD_LAYOUT not in codes


def test_missing_compu_method_measurement(tmp_path):
    a2l = _full_a2l(MEASUREMENT_BAD_CM_SNIPPET)
    db = _parse(tmp_path, a2l)
    msgs = Validator(db.session)()
    codes = _diag_codes(msgs)
    assert Diagnostics.MISSING_COMPU_METHOD in codes
    bad = [m for m in msgs if m.diag_code == Diagnostics.MISSING_COMPU_METHOD]
    assert any("MEAS_BAD" in m.text for m in bad)


def test_missing_compu_method_characteristic(tmp_path):
    a2l = _full_a2l(RECORD_LAYOUT_SNIPPET, CHARACTERISTIC_BAD_CM_SNIPPET)
    db = _parse(tmp_path, a2l)
    msgs = Validator(db.session)()
    codes = _diag_codes(msgs)
    assert Diagnostics.MISSING_COMPU_METHOD in codes


def test_no_compu_method_sentinel_is_valid(tmp_path):
    a2l = _full_a2l(
        RECORD_LAYOUT_SNIPPET,
        """
/begin CHARACTERISTIC CHAR_NO_CM "" VALUE 0x0 RL_UBYTE 0 NO_COMPU_METHOD 0 100
/end CHARACTERISTIC
""",
    )
    db = _parse(tmp_path, a2l)
    msgs = Validator(db.session)()
    assert Diagnostics.MISSING_COMPU_METHOD not in _diag_codes(msgs)


# ---------------------------------------------------------------------------
# Cross-reference checks — RECORD_LAYOUT
# ---------------------------------------------------------------------------


def test_missing_record_layout_characteristic(tmp_path):
    a2l = _full_a2l(COMPU_METHOD_SNIPPET, CHARACTERISTIC_BAD_RL_SNIPPET)
    db = _parse(tmp_path, a2l)
    msgs = Validator(db.session)()
    codes = _diag_codes(msgs)
    assert Diagnostics.MISSING_RECORD_LAYOUT in codes
    bad = [m for m in msgs if m.diag_code == Diagnostics.MISSING_RECORD_LAYOUT]
    assert any("CHAR_BAD_RL" in m.text for m in bad)


# ---------------------------------------------------------------------------
# Namespace uniqueness checks
# ---------------------------------------------------------------------------


def test_duplicate_within_namespace(tmp_path):
    a2l = _full_a2l(
        COMPU_METHOD_SNIPPET,
        MEASUREMENT_SNIPPET,
        # Second measurement with the same name → duplicate in namespace 1
        MEASUREMENT_SNIPPET,
    )
    db = _parse(tmp_path, a2l)
    msgs = Validator(db.session)()
    codes = _diag_codes(msgs)
    assert Diagnostics.MULTIPLE_DEFINITIONS_IN_NAMESPACE in codes


def test_identifier_in_multiple_namespaces(tmp_path):
    # Same name "MEAS_1" used in both measurement namespace and compu_tab namespace.
    a2l = _full_a2l(
        COMPU_METHOD_SNIPPET,
        MEASUREMENT_SNIPPET,
        """
/begin COMPU_TAB MEAS_1 "" TAB_NOINTP 1
  0 0
/end COMPU_TAB
""",
    )
    db = _parse(tmp_path, a2l)
    msgs = Validator(db.session)()
    codes = _diag_codes(msgs)
    assert Diagnostics.DEFINITION_IN_MULTIPLE_NAMESPACES in codes


# ---------------------------------------------------------------------------
# C identifier length check
# ---------------------------------------------------------------------------


def test_c_identifier_too_long(tmp_path):
    long_name = "A" * 33  # one over the 32-char ISO C90 limit
    a2l = _full_a2l(
        COMPU_METHOD_SNIPPET,
        f"""
/begin MEASUREMENT {long_name} ""
  FLOAT32_IEEE CM_LINEAR 0 0 0 100
/end MEASUREMENT
""",
    )
    db = _parse(tmp_path, a2l)
    msgs = Validator(db.session)()
    codes = _diag_codes(msgs)
    assert Diagnostics.INVALID_C_IDENTIFIER in codes
    bad = [m for m in msgs if m.diag_code == Diagnostics.INVALID_C_IDENTIFIER]
    assert any(long_name in m.text for m in bad)


def test_c_identifier_exactly_32_chars_is_valid(tmp_path):
    name_32 = "B" * 32
    a2l = _full_a2l(
        COMPU_METHOD_SNIPPET,
        f"""
/begin MEASUREMENT {name_32} ""
  FLOAT32_IEEE CM_LINEAR 0 0 0 100
/end MEASUREMENT
""",
    )
    db = _parse(tmp_path, a2l)
    msgs = Validator(db.session)()
    codes = _diag_codes(msgs)
    assert Diagnostics.INVALID_C_IDENTIFIER not in codes


# ---------------------------------------------------------------------------
# Message structure
# ---------------------------------------------------------------------------


def test_message_fields(tmp_path):
    """Every emitted Message must have all namedtuple fields populated."""
    a2l = _a2l(
        '/begin MOD_COMMON "msg-fields-unique"',
        "/end MOD_COMMON",
    )
    db = _parse(tmp_path, a2l)
    msgs = Validator(db.session)()
    assert len(msgs) > 0
    for msg in msgs:
        assert isinstance(msg, Message)
        assert isinstance(msg.type, Level)
        assert isinstance(msg.category, Category)
        assert isinstance(msg.diag_code, Diagnostics)
        assert isinstance(msg.text, str)
