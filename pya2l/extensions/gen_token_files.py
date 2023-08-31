#!/bin/env python

literalNames = [
    "<INVALID>",
    "'ALIGNMENT_BYTE'",
    "'ALIGNMENT_FLOAT16_IEEE'",
    "'ALIGNMENT_FLOAT32_IEEE'",
    "'ALIGNMENT_FLOAT64_IEEE'",
    "'ALIGNMENT_INT64'",
    "'ALIGNMENT_LONG'",
    "'ALIGNMENT_WORD'",
    "'ANNOTATION'",
    "'ANNOTATION_LABEL'",
    "'ANNOTATION_ORIGIN'",
    "'ANNOTATION_TEXT'",
    "'BIT_MASK'",
    "'BYTE_ORDER'",
    "'CALIBRATION_ACCESS'",
    "'CALIBRATION'",
    "'NO_CALIBRATION'",
    "'NOT_IN_MCD_SYSTEM'",
    "'OFFLINE_CALIBRATION'",
    "'DEFAULT_VALUE'",
    "'DEPOSIT'",
    "'ABSOLUTE'",
    "'DIFFERENCE'",
    "'DISCRETE'",
    "'DISPLAY_IDENTIFIER'",
    "'ECU_ADDRESS_EXTENSION'",
    "'EXTENDED_LIMITS'",
    "'FORMAT'",
    "'FUNCTION_LIST'",
    "'GUARD_RAILS'",
    "'IF_DATA'",
    "'MATRIX_DIM'",
    "'MAX_REFRESH'",
    "'MONOTONY'",
    "'MON_DECREASE'",
    "'MON_INCREASE'",
    "'STRICT_DECREASE'",
    "'STRICT_INCREASE'",
    "'MONOTONOUS'",
    "'STRICT_MON'",
    "'NOT_MON'",
    "'PHYS_UNIT'",
    "'READ_ONLY'",
    "'REF_CHARACTERISTIC'",
    "'REF_MEMORY_SEGMENT'",
    "'REF_UNIT'",
    "'STEP_SIZE'",
    "'SYMBOL_LINK'",
    "'VERSION'",
    "'ASAP2_VERSION'",
    "'A2ML_VERSION'",
    "'PROJECT'",
    "'HEADER'",
    "'PROJECT_NO'",
    "'MODULE'",
    "'A2ML'",
    "'AXIS_PTS'",
    "'CHARACTERISTIC'",
    "'ASCII'",
    "'CURVE'",
    "'MAP'",
    "'CUBOID'",
    "'CUBE_4'",
    "'CUBE_5'",
    "'VAL_BLK'",
    "'VALUE'",
    "'AXIS_DESCR'",
    "'CURVE_AXIS'",
    "'COM_AXIS'",
    "'FIX_AXIS'",
    "'RES_AXIS'",
    "'STD_AXIS'",
    "'AXIS_PTS_REF'",
    "'CURVE_AXIS_REF'",
    "'FIX_AXIS_PAR'",
    "'FIX_AXIS_PAR_DIST'",
    "'FIX_AXIS_PAR_LIST'",
    "'MAX_GRAD'",
    "'COMPARISON_QUANTITY'",
    "'DEPENDENT_CHARACTERISTIC'",
    "'MAP_LIST'",
    "'NUMBER'",
    "'VIRTUAL_CHARACTERISTIC'",
    "'COMPU_METHOD'",
    "'IDENTICAL'",
    "'FORM'",
    "'LINEAR'",
    "'RAT_FUNC'",
    "'TAB_INTP'",
    "'TAB_NOINTP'",
    "'TAB_VERB'",
    "'COEFFS'",
    "'COEFFS_LINEAR'",
    "'COMPU_TAB_REF'",
    "'FORMULA'",
    "'FORMULA_INV'",
    "'STATUS_STRING_REF'",
    "'COMPU_TAB'",
    "'DEFAULT_VALUE_NUMERIC'",
    "'COMPU_VTAB'",
    "'COMPU_VTAB_RANGE'",
    "'FRAME'",
    "'FRAME_MEASUREMENT'",
    "'FUNCTION'",
    "'DEF_CHARACTERISTIC'",
    "'FUNCTION_VERSION'",
    "'IN_MEASUREMENT'",
    "'LOC_MEASUREMENT'",
    "'OUT_MEASUREMENT'",
    "'SUB_FUNCTION'",
    "'GROUP'",
    "'REF_MEASUREMENT'",
    "'ROOT'",
    "'SUB_GROUP'",
    "'INSTANCE'",
    "'MEASUREMENT'",
    "'ARRAY_SIZE'",
    "'BIT_OPERATION'",
    "'LEFT_SHIFT'",
    "'RIGHT_SHIFT'",
    "'SIGN_EXTEND'",
    "'ECU_ADDRESS'",
    "'ERROR_MASK'",
    "'LAYOUT'",
    "'ROW_DIR'",
    "'COLUMN_DIR'",
    "'READ_WRITE'",
    "'VIRTUAL'",
    "'MOD_COMMON'",
    "'DATA_SIZE'",
    "'S_REC_LAYOUT'",
    "'MOD_PAR'",
    "'ADDR_EPK'",
    "'CALIBRATION_METHOD'",
    "'CALIBRATION_HANDLE'",
    "'CALIBRATION_HANDLE_TEXT'",
    "'CPU_TYPE'",
    "'CUSTOMER'",
    "'CUSTOMER_NO'",
    "'ECU'",
    "'ECU_CALIBRATION_OFFSET'",
    "'EPK'",
    "'MEMORY_LAYOUT'",
    "'PRG_CODE'",
    "'PRG_DATA'",
    "'PRG_RESERVED'",
    "'MEMORY_SEGMENT'",
    "'CALIBRATION_VARIABLES'",
    "'CODE'",
    "'DATA'",
    "'EXCLUDE_FROM_FLASH'",
    "'OFFLINE_DATA'",
    "'RESERVED'",
    "'SERAM'",
    "'VARIABLES'",
    "'EEPROM'",
    "'EPROM'",
    "'FLASH'",
    "'RAM'",
    "'ROM'",
    "'REGISTER'",
    "'INTERN'",
    "'EXTERN'",
    "'NO_OF_INTERFACES'",
    "'PHONE_NO'",
    "'SUPPLIER'",
    "'SYSTEM_CONSTANT'",
    "'USER'",
    "'RECORD_LAYOUT'",
    "'AXIS_PTS_X'",
    "'AXIS_PTS_Y'",
    "'AXIS_PTS_Z'",
    "'AXIS_PTS_4'",
    "'AXIS_PTS_5'",
    "'AXIS_RESCALE_X'",
    "'AXIS_RESCALE_Y'",
    "'AXIS_RESCALE_Z'",
    "'AXIS_RESCALE_4'",
    "'AXIS_RESCALE_5'",
    "'DIST_OP_X'",
    "'DIST_OP_Y'",
    "'DIST_OP_Z'",
    "'DIST_OP_4'",
    "'DIST_OP_5'",
    "'FIX_NO_AXIS_PTS_X'",
    "'FIX_NO_AXIS_PTS_Y'",
    "'FIX_NO_AXIS_PTS_Z'",
    "'FIX_NO_AXIS_PTS_4'",
    "'FIX_NO_AXIS_PTS_5'",
    "'FNC_VALUES'",
    "'ALTERNATE_CURVES'",
    "'ALTERNATE_WITH_X'",
    "'ALTERNATE_WITH_Y'",
    "'IDENTIFICATION'",
    "'NO_AXIS_PTS_X'",
    "'NO_AXIS_PTS_Y'",
    "'NO_AXIS_PTS_Z'",
    "'NO_AXIS_PTS_4'",
    "'NO_AXIS_PTS_5'",
    "'STATIC_RECORD_LAYOUT'",
    "'NO_RESCALE_X'",
    "'NO_RESCALE_Y'",
    "'NO_RESCALE_Z'",
    "'NO_RESCALE_4'",
    "'NO_RESCALE_5'",
    "'OFFSET_X'",
    "'OFFSET_Y'",
    "'OFFSET_Z'",
    "'OFFSET_4'",
    "'OFFSET_5'",
    "'RIP_ADDR_W'",
    "'RIP_ADDR_X'",
    "'RIP_ADDR_Y'",
    "'RIP_ADDR_Z'",
    "'RIP_ADDR_4'",
    "'RIP_ADDR_5'",
    "'SHIFT_OP_X'",
    "'SHIFT_OP_Y'",
    "'SHIFT_OP_Z'",
    "'SHIFT_OP_4'",
    "'SHIFT_OP_5'",
    "'SRC_ADDR_X'",
    "'SRC_ADDR_Y'",
    "'SRC_ADDR_Z'",
    "'SRC_ADDR_4'",
    "'SRC_ADDR_5'",
    "'TYPEDEF_CHARACTERISTIC'",
    "'TYPEDEF_MEASUREMENT'",
    "'TYPEDEF_STRUCTURE'",
    "'STRUCTURE_COMPONENT'",
    "'UNIT'",
    "'DERIVED'",
    "'EXTENDED_SI'",
    "'SI_EXPONENTS'",
    "'UNIT_CONVERSION'",
    "'USER_RIGHTS'",
    "'REF_GROUP'",
    "'VARIANT_CODING'",
    "'VAR_CHARACTERISTIC'",
    "'VAR_ADDRESS'",
    "'VAR_CRITERION'",
    "'VAR_MEASUREMENT'",
    "'VAR_SELECTION_CHARACTERISTIC'",
    "'VAR_FORBIDDEN_COMB'",
    "'VAR_NAMING'",
    "'NUMERIC'",
    "'APLHA'",
    "'VAR_SEPARATOR'",
    "'.'",
    "'['",
    "']'",
    "'UBYTE'",
    "'SBYTE'",
    "'UWORD'",
    "'SWORD'",
    "'ULONG'",
    "'SLONG'",
    "'A_UINT64'",
    "'A_INT64'",
    "'FLOAT16_IEEE'",
    "'FLOAT32_IEEE'",
    "'FLOAT64_IEEE'",
    "'BYTE'",
    "'WORD'",
    "'LONG'",
    "'PBYTE'",
    "'PWORD'",
    "'PLONG'",
    "'DIRECT'",
    "'LITTLE_ENDIAN'",
    "'BIG_ENDIAN'",
    "'MSB_LAST'",
    "'MSB_FIRST'",
    "'INDEX_INCR'",
    "'INDEX_DECR'",
    "'SYMBOL_TYPE_LINK'",
    "'/begin'",
    "'/end'",
]


############################
############################
############################
MAY_KEYWORDS = {
    "ABSOLUTE": [("DEPOSIT", 1)],
    "ALTERNATE_CURVES": [("FNC_VALUES", 3)],
    "ALTERNATE_WITH_X": [("FNC_VALUES", 3)],
    "ALTERNATE_WITH_Y": [("FNC_VALUES", 3)],
    "APLHA": [("VAR_NAMING", 1)],
    "ASCII": [("CHARACTERISTIC", 3), ("TYPEDEF_CHARACTERISTIC", 3)],
    "CALIBRATION": [("CALIBRATION_ACCESS", 1)],
    "CALIBRATION_VARIABLES": [("MEMORY_SEGMENT", 3)],
    "CODE": [("MEMORY_SEGMENT", 3)],
    "COLUMN_DIR": [("FNC_VALUES", 3), ("LAYOUT", 1)],
    "COM_AXIS": [("AXIS_DESCR", 1)],
    "CUBE_4": [("CHARACTERISTIC", 3), ("TYPEDEF_CHARACTERISTIC", 3)],
    "CUBE_5": [("CHARACTERISTIC", 3), ("TYPEDEF_CHARACTERISTIC", 3)],
    "CUBOID": [("CHARACTERISTIC", 3), ("TYPEDEF_CHARACTERISTIC", 3)],
    "CURVE": [("CHARACTERISTIC", 3), ("TYPEDEF_CHARACTERISTIC", 3)],
    "CURVE_AXIS": [("AXIS_DESCR", 1)],
    "DATA": [("MEMORY_SEGMENT", 3)],
    "DERIVED": [("UNIT", 4)],
    "DIFFERENCE": [("DEPOSIT", 1)],
    "EEPROM": [("MEMORY_SEGMENT", 4)],
    "EPROM": [("MEMORY_SEGMENT", 4)],
    "EXCLUDE_FROM_FLASH": [("MEMORY_SEGMENT", 3)],
    "EXTENDED_SI": [("UNIT", 4)],
    "EXTERN": [("MEMORY_SEGMENT", 5)],
    "FIX_AXIS": [("AXIS_DESCR", 1)],
    "FLASH": [("MEMORY_SEGMENT", 4)],
    "FORM": [("COMPU_METHOD", 3)],
    "IDENTICAL": [("COMPU_METHOD", 3)],
    "INTERN": [("MEMORY_SEGMENT", 5)],
    "LINEAR": [("COMPU_METHOD", 3)],
    "MAP": [("CHARACTERISTIC", 3), ("TYPEDEF_CHARACTERISTIC", 3)],
    "MONOTONOUS": [("MONOTONY", 1)],
    "MON_DECREASE": [("MONOTONY", 1)],
    "MON_INCREASE": [("MONOTONY", 1)],
    "NOT_IN_MCD_SYSTEM": [("CALIBRATION_ACCESS", 1)],
    "NOT_MON": [("MONOTONY", 1)],
    "NO_CALIBRATION": [("CALIBRATION_ACCESS", 1)],
    "NUMERIC": [("VAR_NAMING", 1)],
    "OFFLINE_CALIBRATION": [("CALIBRATION_ACCESS", 1)],
    "OFFLINE_DATA": [("MEMORY_SEGMENT", 3)],
    "PRG_CODE": [("MEMORY_LAYOUT", 1)],
    "PRG_DATA": [("MEMORY_LAYOUT", 1)],
    "PRG_RESERVED": [("MEMORY_LAYOUT", 1)],
    "RAM": [("MEMORY_SEGMENT", 4)],
    "RAT_FUNC": [("COMPU_METHOD", 3)],
    "REGISTER": [("MEMORY_SEGMENT", 4)],
    "RESERVED": [("MEMORY_SEGMENT", 3)],
    "RES_AXIS": [("AXIS_DESCR", 1)],
    "ROM": [("MEMORY_SEGMENT", 4)],
    "ROW_DIR": [("FNC_VALUES", 3), ("LAYOUT", 1)],
    "SERAM": [("MEMORY_SEGMENT", 3)],
    "STD_AXIS": [("AXIS_DESCR", 1)],
    "STRICT_DECREASE": [("MONOTONY", 1)],
    "STRICT_INCREASE": [("MONOTONY", 1)],
    "STRICT_MON": [("MONOTONY", 1)],
    "TAB_INTP": [("COMPU_METHOD", 3), ("COMPU_TAB", 3)],
    "TAB_NOINTP": [("COMPU_METHOD", 3), ("COMPU_TAB", 3)],
    "TAB_VERB": [("COMPU_METHOD", 3), ("COMPU_VTAB", 3)],
    "VALUE": [("CHARACTERISTIC", 3), ("TYPEDEF_CHARACTERISTIC", 3)],
    "VAL_BLK": [("CHARACTERISTIC", 3), ("TYPEDEF_CHARACTERISTIC", 3)],
    "VARIABLES": [("MEMORY_SEGMENT", 3)],
}
############################
############################
############################

HEADER = """/*
**
**  !!! AUTOMATICALLY GENERATED FILE -- DO NOT EDIT !!!
**
*/
#if !defined(__TOKEN_TYPE_HPP)
#define __TOKEN_TYPE_HPP

#include <map>
#include <string>
#include <cstdint>

"""

FOOTER = """
#endif  // __TOKEN_TYPE_HPP
"""

HEADER2 = """/*
**
**  !!! AUTOMATICALLY GENERATED FILE -- DO NOT EDIT !!!
**
*/
#if !defined(__A2LTOKEN_HPP)
#define __A2LTOKEN_HPP

#include <map>
#include <string>
#include <cstdint>

"""

FOOTER2 = """
#endif  // __A2LTOKEN_HPP
"""

TPs = (
    ("INVALID", 0),
    ("BEGIN", 276),
    ("END", 277),
    ("IDENT", 278),
    ("FLOAT", 279),
    ("INT", 280),
    ("HEX", 281),
    ("COMMENT", 282),
    ("WS", 283),
    ("STRING", 284),
)

with open("token_type.hpp", "wt") as of:
    of.write(HEADER)
    of.write("const std::map<std::string, int> A2L_KEYWORDS {\n")
    for idx, item in enumerate(literalNames):
        item = item.replace("'", '"')
        if not item.startswith('"'):
            item = f'"{item}"'
        of.write(f"""    {{{item}, {idx}}},\n""")
    of.write("};\n\n")
    of.write("enum class TokenType: std::uint16_t {\n")
    for idx in range(275):
        of.write(f"\tT__{idx}={idx + 1},\n")
    for n, v in TPs:
        of.write(f"\t{n}={v},\n")
    of.write("};\n")
    of.write(FOOTER)

with open("a2ltoken.hpp", "wt") as of:
    of.write(HEADER2)
    of.write("enum class A2LTokenType: std::uint16_t {\n")

    li = [(idx, item) for idx, item in enumerate(literalNames)]
    li.extend([(v, k) for k, v in TPs])
    for idx, item in sorted(li):
        item = item.replace("'", "")
        if item in ("/begin", "/end", "<INVALID>"):
            continue
        if item == ".":
            item = "DOT"
        elif item == "[":
            item = "BRO"
        elif item == "]":  #
            item = "BRC"

        # if not item.startswith('"'):
        #    item = f'"{item}"'
        of.write(f"""    {item} = {idx},\n""")
    of.write("};\n\n")
    of.write(FOOTER2)


with open("a2l.tokens", "wt") as of:
    for idx in range(275):
        of.write(f"T__{idx}={idx + 1}\n")
    for n, v in TPs:
        if v == 0:
            continue
        of.write(f"{n}={v}\n")
    for idx, item in enumerate(literalNames):
        of.write(f"""{item}={idx}\n""")
