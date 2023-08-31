/*const*/ inline Keyword PARSER_TABLE = Keyword(
    A2LTokenType::PROJECT, "ROOT", false, false,
    {
},
    {
        Keyword(
            A2LTokenType::ASAP2_VERSION, "ASAP2_VERSION", false, false,
            {
                Parameter(PredefinedType::Uint, "VersionNo"),
                Parameter(PredefinedType::Uint, "UpgradeNo"),
            },
            {}
        ),
        Keyword(
            A2LTokenType::A2ML_VERSION, "A2ML_VERSION", false, false,
            {
                Parameter(PredefinedType::Uint, "VersionNo"),
                Parameter(PredefinedType::Uint, "UpgradeNo"),
            },
            {}
        ),
        Keyword(
            A2LTokenType::PROJECT, "PROJECT", true, false,
            {
                Parameter(PredefinedType::Ident, "Name"),
                Parameter(PredefinedType::String, "LongIdentifier"),
            },
            {
                Keyword(
                    A2LTokenType::HEADER, "HEADER", true, false,
                    {
                        Parameter(PredefinedType::String, "Comment"),
                    },
                    {
                        Keyword(
                            A2LTokenType::PROJECT_NO, "PROJECT_NO", false, false,
                            {
                                Parameter(PredefinedType::Ident, "ProjectNumber"),
                            },
                            {}
                        ),
                        Keyword(
                            A2LTokenType::VERSION, "VERSION", false, false,
                            {
                                Parameter(PredefinedType::String, "VersionIdentifier"),
                            },
                            {}
                        ),
                    }
                ),
                Keyword(
                    A2LTokenType::MODULE, "MODULE", true, true,
                    {
                        Parameter(PredefinedType::Ident, "Name"),
                        Parameter(PredefinedType::String, "LongIdentifier"),
                    },
                    {
                        Keyword(A2LTokenType::A2ML, "A2ML", true, false, {}, {}),
                        Keyword(
                            A2LTokenType::AXIS_PTS, "AXIS_PTS", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(PredefinedType::Ulong, "Address"),
                                Parameter(PredefinedType::Ident, "InputQuantity"),
                                Parameter(PredefinedType::Ident, "DepositAttr"),
                                Parameter(PredefinedType::Float, "MaxDiff"),
                                Parameter(PredefinedType::Ident, "Conversion"),
                                Parameter(PredefinedType::Uint, "MaxAxisPoints"),
                                Parameter(PredefinedType::Float, "LowerLimit"),
                                Parameter(PredefinedType::Float, "UpperLimit"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ANNOTATION, "ANNOTATION", true, true, {},
                                    {
                                        Keyword(
                                            A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Label"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Origin"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", true, false,
                                            {
                                                Parameter(PredefinedType::String, "Text", true),  // MULT
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::BYTE_ORDER, "BYTE_ORDER", false, false,
                                    {
                                        Parameter(PredefinedType::Byteorder, "ByteOrder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::CALIBRATION_ACCESS, "CALIBRATION_ACCESS", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Type",
                                            { "CALIBRATION", "NO_CALIBRATION", "NOT_IN_MCD_SYSTEM", "OFFLINE_CALIBRATION" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DEPOSIT, "DEPOSIT", false, false,
                                    {
                                        Parameter(PredefinedType::Enum, "Mode", { "ABSOLUTE", "DIFFERENCE" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DISPLAY_IDENTIFIER, "DISPLAY_IDENTIFIER", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "display_name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU_ADDRESS_EXTENSION, "ECU_ADDRESS_EXTENSION", false, false,
                                    {
                                        Parameter(PredefinedType::Int, "Extension"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::EXTENDED_LIMITS, "EXTENDED_LIMITS", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "LowerLimit"),
                                        Parameter(PredefinedType::Float, "UpperLimit"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FORMAT, "FORMAT", false, false,
                                    {
                                        Parameter(PredefinedType::String, "FormatString"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FUNCTION_LIST, "FUNCTION_LIST", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::GUARD_RAILS, "GUARD_RAILS", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MONOTONY, "MONOTONY", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Monotony",
                                            { "MON_DECREASE", "MON_INCREASE", "STRICT_DECREASE", "STRICT_INCREASE", "MONOTONOUS",
                                              "STRICT_MON", "NOT_MON" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::PHYS_UNIT, "PHYS_UNIT", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Unit"),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::READ_ONLY, "READ_ONLY", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::REF_MEMORY_SEGMENT, "REF_MEMORY_SEGMENT", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::STEP_SIZE, "STEP_SIZE", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "StepSize"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SYMBOL_LINK, "SYMBOL_LINK", false, false,
                                    {
                                        Parameter(PredefinedType::String, "SymbolName"),
                                        Parameter(PredefinedType::Long, "Offset"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::CHARACTERISTIC, "CHARACTERISTIC", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(
                                    PredefinedType::Enum, "Type",
                                    { "ASCII", "CURVE", "MAP", "CUBOID", "CUBE_4", "CUBE_5", "VAL_BLK", "VALUE" }
                                ),
                                Parameter(PredefinedType::Ulong, "Address"),
                                Parameter(PredefinedType::Ident, "Deposit"),
                                Parameter(PredefinedType::Float, "MaxDiff"),
                                Parameter(PredefinedType::Ident, "Conversion"),
                                Parameter(PredefinedType::Float, "LowerLimit"),
                                Parameter(PredefinedType::Float, "UpperLimit"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ANNOTATION, "ANNOTATION", true, true, {},
                                    {
                                        Keyword(
                                            A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Label"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Origin"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", true, false,
                                            {
                                                Parameter(PredefinedType::String, "Text", true),  // MULT
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_DESCR, "AXIS_DESCR", true, true,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Attribute",
                                            { "CURVE_AXIS", "COM_AXIS", "FIX_AXIS", "RES_AXIS", "STD_AXIS" }
                                        ),
                                        Parameter(PredefinedType::Ident, "InputQuantity"),
                                        Parameter(PredefinedType::Ident, "Conversion"),
                                        Parameter(PredefinedType::Uint, "MaxAxisPoints"),
                                        Parameter(PredefinedType::Float, "LowerLimit"),
                                        Parameter(PredefinedType::Float, "UpperLimit"),
                                    },
                                    {
                                        Keyword(
                                            A2LTokenType::ANNOTATION, "ANNOTATION", true, true, {},
                                            {
                                                Keyword(
                                                    A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", false, false,
                                                    {
                                                        Parameter(PredefinedType::String, "Label"),
                                                    },
                                                    {}
                                                ),
                                                Keyword(
                                                    A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", false, false,
                                                    {
                                                        Parameter(PredefinedType::String, "Origin"),
                                                    },
                                                    {}
                                                ),
                                                Keyword(
                                                    A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", true, false,
                                                    {
                                                        Parameter(PredefinedType::String, "Text", true),  // MULT
                                                    },
                                                    {}
                                                ),
                                            }
                                        ),
                                        Keyword(
                                            A2LTokenType::AXIS_PTS_REF, "AXIS_PTS_REF", false, false,
                                            {
                                                Parameter(PredefinedType::Ident, "AxisPoints"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::BYTE_ORDER, "BYTE_ORDER", false, false,
                                            {
                                                Parameter(PredefinedType::Byteorder, "ByteOrder"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::CURVE_AXIS_REF, "CURVE_AXIS_REF", false, false,
                                            {
                                                Parameter(PredefinedType::Ident, "CurveAxis"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::DEPOSIT, "DEPOSIT", false, false,
                                            {
                                                Parameter(PredefinedType::Enum, "Mode", { "ABSOLUTE", "DIFFERENCE" }),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::EXTENDED_LIMITS, "EXTENDED_LIMITS", false, false,
                                            {
                                                Parameter(PredefinedType::Float, "LowerLimit"),
                                                Parameter(PredefinedType::Float, "UpperLimit"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::FIX_AXIS_PAR, "FIX_AXIS_PAR", false, false,
                                            {
                                                Parameter(PredefinedType::Int, "Offset"),
                                                Parameter(PredefinedType::Int, "Shift"),
                                                Parameter(PredefinedType::Uint, "Numberapo"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::FIX_AXIS_PAR_DIST, "FIX_AXIS_PAR_DIST", false, false,
                                            {
                                                Parameter(PredefinedType::Int, "Offset"),
                                                Parameter(PredefinedType::Int, "Distance"),
                                                Parameter(PredefinedType::Uint, "Numberapo"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::FIX_AXIS_PAR_LIST, "FIX_AXIS_PAR_LIST", true, false,
                                            {
                                                Parameter(PredefinedType::Float, "AxisPts_Value", true),  // MULT
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::FORMAT, "FORMAT", false, false,
                                            {
                                                Parameter(PredefinedType::String, "FormatString"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::MAX_GRAD, "MAX_GRAD", false, false,
                                            {
                                                Parameter(PredefinedType::Float, "MaxGradient"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::MONOTONY, "MONOTONY", false, false,
                                            {
                                                Parameter(
                                                    PredefinedType::Enum, "Monotony",
                                                    { "MON_DECREASE", "MON_INCREASE", "STRICT_DECREASE", "STRICT_INCREASE",
                                                      "MONOTONOUS", "STRICT_MON", "NOT_MON" }
                                                ),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::PHYS_UNIT, "PHYS_UNIT", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Unit"),
                                            },
                                            {}
                                        ),
                                        Keyword(A2LTokenType::READ_ONLY, "READ_ONLY", false, false, {}, {}),
                                        Keyword(
                                            A2LTokenType::STEP_SIZE, "STEP_SIZE", false, false,
                                            {
                                                Parameter(PredefinedType::Float, "StepSize"),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::BIT_MASK, "BIT_MASK", false, false,
                                    {
                                        Parameter(PredefinedType::Ulong, "Mask"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::BYTE_ORDER, "BYTE_ORDER", false, false,
                                    {
                                        Parameter(PredefinedType::Byteorder, "ByteOrder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::CALIBRATION_ACCESS, "CALIBRATION_ACCESS", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Type",
                                            { "CALIBRATION", "NO_CALIBRATION", "NOT_IN_MCD_SYSTEM", "OFFLINE_CALIBRATION" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::COMPARISON_QUANTITY, "COMPARISON_QUANTITY", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DEPENDENT_CHARACTERISTIC, "DEPENDENT_CHARACTERISTIC", true, false,
                                    {
                                        Parameter(PredefinedType::String, "Formula"),
                                        Parameter(PredefinedType::Ident, "Characteristic", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::DISCRETE, "DISCRETE", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::DISPLAY_IDENTIFIER, "DISPLAY_IDENTIFIER", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "display_name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU_ADDRESS_EXTENSION, "ECU_ADDRESS_EXTENSION", false, false,
                                    {
                                        Parameter(PredefinedType::Int, "Extension"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::EXTENDED_LIMITS, "EXTENDED_LIMITS", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "LowerLimit"),
                                        Parameter(PredefinedType::Float, "UpperLimit"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FORMAT, "FORMAT", false, false,
                                    {
                                        Parameter(PredefinedType::String, "FormatString"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FUNCTION_LIST, "FUNCTION_LIST", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::GUARD_RAILS, "GUARD_RAILS", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MAP_LIST, "MAP_LIST", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MATRIX_DIM, "MATRIX_DIM", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "xDim"),
                                        Parameter(PredefinedType::Uint, "yDim"),
                                        Parameter(PredefinedType::Uint, "zDim"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MAX_REFRESH, "MAX_REFRESH", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "ScalingUnit"),
                                        Parameter(PredefinedType::Ulong, "Rate"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NUMBER, "NUMBER", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Number"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::PHYS_UNIT, "PHYS_UNIT", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Unit"),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::READ_ONLY, "READ_ONLY", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::REF_MEMORY_SEGMENT, "REF_MEMORY_SEGMENT", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::STEP_SIZE, "STEP_SIZE", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "StepSize"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SYMBOL_LINK, "SYMBOL_LINK", false, false,
                                    {
                                        Parameter(PredefinedType::String, "SymbolName"),
                                        Parameter(PredefinedType::Long, "Offset"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::VIRTUAL_CHARACTERISTIC, "VIRTUAL_CHARACTERISTIC", true, false,
                                    {
                                        Parameter(PredefinedType::String, "Formula"),
                                        Parameter(PredefinedType::Ident, "Characteristic", true),  // MULT
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::COMPU_METHOD, "COMPU_METHOD", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(
                                    PredefinedType::Enum, "ConversionType",
                                    { "IDENTICAL", "FORM", "LINEAR", "RAT_FUNC", "TAB_INTP", "TAB_NOINTP", "TAB_VERB" }
                                ),
                                Parameter(PredefinedType::String, "Format"),
                                Parameter(PredefinedType::String, "Unit"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::COEFFS, "COEFFS", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "a"),
                                        Parameter(PredefinedType::Float, "b"),
                                        Parameter(PredefinedType::Float, "c"),
                                        Parameter(PredefinedType::Float, "d"),
                                        Parameter(PredefinedType::Float, "e"),
                                        Parameter(PredefinedType::Float, "f"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::COEFFS_LINEAR, "COEFFS_LINEAR", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "a"),
                                        Parameter(PredefinedType::Float, "b"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::COMPU_TAB_REF, "COMPU_TAB_REF", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "ConversionTable"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FORMULA, "FORMULA", true, false,
                                    {
                                        Parameter(PredefinedType::String, "F_x"),
                                    },
                                    {
                                        Keyword(
                                            A2LTokenType::FORMULA_INV, "FORMULA_INV", false, false,
                                            {
                                                Parameter(PredefinedType::String, "G_x"),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::REF_UNIT, "REF_UNIT", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Unit"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::STATUS_STRING_REF, "STATUS_STRING_REF", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "ConversionTable"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::COMPU_TAB, "COMPU_TAB", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(PredefinedType::Enum, "ConversionType", { "TAB_INTP", "TAB_NOINTP" }),
                                Parameter(
                                    { PredefinedType::Uint, "NumberValuePairs" },
                                    { { PredefinedType::Float, "InVal" }, { PredefinedType::Float, "OutVal" } }
                                ),
                            },
                            {
                                Keyword(
                                    A2LTokenType::DEFAULT_VALUE, "DEFAULT_VALUE", false, false,
                                    {
                                        Parameter(PredefinedType::String, "display_string"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DEFAULT_VALUE_NUMERIC, "DEFAULT_VALUE_NUMERIC", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "display_value"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::COMPU_VTAB, "COMPU_VTAB", true, true,
                            { Parameter(PredefinedType::Ident, "Name"), Parameter(PredefinedType::String, "LongIdentifier"),
                              Parameter(PredefinedType::Enum, "ConversionType", { "TAB_VERB", "" }),
                              Parameter(
                                  { PredefinedType::Uint, "NumberValuePairs" },
                                  { { PredefinedType::Float, "InVal" }, { PredefinedType::Float, "OutVal" } }
                              ) },
                            {
                                Keyword(
                                    A2LTokenType::DEFAULT_VALUE, "DEFAULT_VALUE", false, false,
                                    {
                                        Parameter(PredefinedType::String, "display_string"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::COMPU_VTAB_RANGE, "COMPU_VTAB_RANGE", true, true,
                            { Parameter(PredefinedType::Ident, "Name"), Parameter(PredefinedType::String, "LongIdentifier"),
                              Parameter(
                                  { PredefinedType::Uint, "NumberValueTriples" }, { { PredefinedType::Float, "InValMin" },
                                                                                    { PredefinedType::Float, "InValMax" },
                                                                                    { PredefinedType::String, "OutVal" } }
                              )

                            },
                            {
                                Keyword(
                                    A2LTokenType::DEFAULT_VALUE, "DEFAULT_VALUE", false, false,
                                    {
                                        Parameter(PredefinedType::String, "display_string"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::FRAME, "FRAME", true, false,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(PredefinedType::Uint, "ScalingUnit"),
                                Parameter(PredefinedType::Ulong, "Rate"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::FRAME_MEASUREMENT, "FRAME_MEASUREMENT", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::FUNCTION, "FUNCTION", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ANNOTATION, "ANNOTATION", true, true, {},
                                    {
                                        Keyword(
                                            A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Label"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Origin"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", true, false,
                                            {
                                                Parameter(PredefinedType::String, "Text", true),  // MULT
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::DEF_CHARACTERISTIC, "DEF_CHARACTERISTIC", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FUNCTION_VERSION, "FUNCTION_VERSION", false, false,
                                    {
                                        Parameter(PredefinedType::String, "VersionIdentifier"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::IN_MEASUREMENT, "IN_MEASUREMENT", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::LOC_MEASUREMENT, "LOC_MEASUREMENT", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::OUT_MEASUREMENT, "OUT_MEASUREMENT", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::REF_CHARACTERISTIC, "REF_CHARACTERISTIC", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SUB_FUNCTION, "SUB_FUNCTION", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),  // MULT
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::GROUP, "GROUP", true, true,
                            {
                                Parameter(PredefinedType::Ident, "GroupName"),
                                Parameter(PredefinedType::String, "GroupLongIdentifier"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ANNOTATION, "ANNOTATION", true, true, {},
                                    {
                                        Keyword(
                                            A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Label"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Origin"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", true, false,
                                            {
                                                Parameter(PredefinedType::String, "Text", true),  // MULT
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::FUNCTION_LIST, "FUNCTION_LIST", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::REF_CHARACTERISTIC, "REF_CHARACTERISTIC", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::REF_MEASUREMENT, "REF_MEASUREMENT", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::ROOT, "ROOT", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::SUB_GROUP, "SUB_GROUP", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),  // MULT
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::IF_DATA, "IF_DATA", true, true,
                            {
                                Parameter(PredefinedType::Ident, "name"),
                            },
                            {}
                        ),
                        Keyword(
                            A2LTokenType::INSTANCE, "INSTANCE", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(PredefinedType::Ident, "TypeName"),
                                Parameter(PredefinedType::Ulong, "Address"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU_ADDRESS_EXTENSION, "ECU_ADDRESS_EXTENSION", false, false,
                                    {
                                        Parameter(PredefinedType::Int, "Extension"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::MEASUREMENT, "MEASUREMENT", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(PredefinedType::Datatype, "Datatype"),
                                Parameter(PredefinedType::Ident, "Conversion"),
                                Parameter(PredefinedType::Uint, "Resolution"),
                                Parameter(PredefinedType::Float, "Accuracy"),
                                Parameter(PredefinedType::Float, "LowerLimit"),
                                Parameter(PredefinedType::Float, "UpperLimit"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ANNOTATION, "ANNOTATION", true, true, {},
                                    {
                                        Keyword(
                                            A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Label"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Origin"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", true, false,
                                            {
                                                Parameter(PredefinedType::String, "Text", true),  // MULT
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::ARRAY_SIZE, "ARRAY_SIZE", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Number"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::BIT_MASK, "BIT_MASK", false, false,
                                    {
                                        Parameter(PredefinedType::Ulong, "Mask"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::BIT_OPERATION, "BIT_OPERATION", true, false, {},
                                    {
                                        Keyword(
                                            A2LTokenType::LEFT_SHIFT, "LEFT_SHIFT", false, false,
                                            {
                                                Parameter(PredefinedType::Ulong, "Bitcount"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::RIGHT_SHIFT, "RIGHT_SHIFT", false, false,
                                            {
                                                Parameter(PredefinedType::Ulong, "Bitcount"),
                                            },
                                            {}
                                        ),
                                        Keyword(A2LTokenType::SIGN_EXTEND, "SIGN_EXTEND", false, false, {}, {}),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::BYTE_ORDER, "BYTE_ORDER", false, false,
                                    {
                                        Parameter(PredefinedType::Byteorder, "ByteOrder"),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::DISCRETE, "DISCRETE", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::DISPLAY_IDENTIFIER, "DISPLAY_IDENTIFIER", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "display_name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU_ADDRESS, "ECU_ADDRESS", false, false,
                                    {
                                        Parameter(PredefinedType::Ulong, "Address"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU_ADDRESS_EXTENSION, "ECU_ADDRESS_EXTENSION", false, false,
                                    {
                                        Parameter(PredefinedType::Int, "Extension"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ERROR_MASK, "ERROR_MASK", false, false,
                                    {
                                        Parameter(PredefinedType::Ulong, "Mask"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FORMAT, "FORMAT", false, false,
                                    {
                                        Parameter(PredefinedType::String, "FormatString"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FUNCTION_LIST, "FUNCTION_LIST", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name", true),  // MULT
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::LAYOUT, "LAYOUT", false, false,
                                    {
                                        Parameter(PredefinedType::Enum, "IndexMode", { "ROW_DIR", "COLUMN_DIR" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MATRIX_DIM, "MATRIX_DIM", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "xDim"),
                                        Parameter(PredefinedType::Uint, "yDim"),
                                        Parameter(PredefinedType::Uint, "zDim"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MAX_REFRESH, "MAX_REFRESH", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "ScalingUnit"),
                                        Parameter(PredefinedType::Ulong, "Rate"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::PHYS_UNIT, "PHYS_UNIT", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Unit"),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::READ_WRITE, "READ_WRITE", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::REF_MEMORY_SEGMENT, "REF_MEMORY_SEGMENT", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SYMBOL_LINK, "SYMBOL_LINK", false, false,
                                    {
                                        Parameter(PredefinedType::String, "SymbolName"),
                                        Parameter(PredefinedType::Long, "Offset"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::VIRTUAL, "VIRTUAL", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "MeasuringChannel", true),  // MULT
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::MOD_COMMON, "MOD_COMMON", true, false,
                            {
                                Parameter(PredefinedType::String, "Comment"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ALIGNMENT_BYTE, "ALIGNMENT_BYTE", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_FLOAT16_IEEE, "ALIGNMENT_FLOAT16_IEEE", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_FLOAT32_IEEE, "ALIGNMENT_FLOAT32_IEEE", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_FLOAT64_IEEE, "ALIGNMENT_FLOAT64_IEEE", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_INT64, "ALIGNMENT_INT64", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_LONG, "ALIGNMENT_LONG", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_WORD, "ALIGNMENT_WORD", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::BYTE_ORDER, "BYTE_ORDER", false, false,
                                    {
                                        Parameter(PredefinedType::Byteorder, "ByteOrder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DATA_SIZE, "DATA_SIZE", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Size"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DEPOSIT, "DEPOSIT", false, false,
                                    {
                                        Parameter(PredefinedType::Enum, "Mode", { "ABSOLUTE", "DIFFERENCE" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::S_REC_LAYOUT, "S_REC_LAYOUT", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::MOD_PAR, "MOD_PAR", true, false,
                            {
                                Parameter(PredefinedType::String, "Comment"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ADDR_EPK, "ADDR_EPK", false, true,
                                    {
                                        Parameter(PredefinedType::Ulong, "Address"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::CALIBRATION_METHOD, "CALIBRATION_METHOD", true, true,
                                    {
                                        Parameter(PredefinedType::String, "Method"),
                                        Parameter(PredefinedType::Ulong, "Version"),
                                    },
                                    {
                                        Keyword(
                                            A2LTokenType::CALIBRATION_HANDLE, "CALIBRATION_HANDLE", true, true,
                                            {
                                                Parameter(PredefinedType::Long, "Handle", true),  // MULT
                                            },
                                            {
                                                Keyword(
                                                    A2LTokenType::CALIBRATION_HANDLE_TEXT, "CALIBRATION_HANDLE_TEXT", false, false,
                                                    {
                                                        Parameter(PredefinedType::String, "Text"),
                                                    },
                                                    {}
                                                ),
                                            }
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::CPU_TYPE, "CPU_TYPE", false, false,
                                    {
                                        Parameter(PredefinedType::String, "CPU"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::CUSTOMER, "CUSTOMER", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Customer"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::CUSTOMER_NO, "CUSTOMER_NO", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Number"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU, "ECU", false, false,
                                    {
                                        Parameter(PredefinedType::String, "ControlUnit"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU_CALIBRATION_OFFSET, "ECU_CALIBRATION_OFFSET", false, false,
                                    {
                                        Parameter(PredefinedType::Long, "Offset"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::EPK, "EPK", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Identifier"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MEMORY_LAYOUT, "MEMORY_LAYOUT", true, true,
                                    {
                                        Parameter(PredefinedType::Enum, "PrgType", { "PRG_CODE", "PRG_DATA", "PRG_RESERVED" }),
                                        Parameter(PredefinedType::Ulong, "Address"),
                                        Parameter(PredefinedType::Ulong, "Size"),
                                        Parameter(PredefinedType::Long, "Offset_0"),
                                        Parameter(PredefinedType::Long, "Offset_1"),
                                        Parameter(PredefinedType::Long, "Offset_2"),
                                        Parameter(PredefinedType::Long, "Offset_3"),
                                        Parameter(PredefinedType::Long, "Offset_4"),
                                    },
                                    {
                                        Keyword(
                                            A2LTokenType::IF_DATA, "IF_DATA", true, true,
                                            {
                                                Parameter(PredefinedType::Ident, "name"),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::MEMORY_SEGMENT, "MEMORY_SEGMENT", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                        Parameter(PredefinedType::String, "LongIdentifier"),
                                        Parameter(
                                            PredefinedType::Enum, "PrgType",
                                            { "CALIBRATION_VARIABLES", "CODE", "DATA", "EXCLUDE_FROM_FLASH", "OFFLINE_DATA",
                                              "RESERVED", "SERAM", "VARIABLES" }
                                        ),
                                        Parameter(
                                            PredefinedType::Enum, "MemoryType",
                                            { "EEPROM", "EPROM", "FLASH", "RAM", "ROM", "REGISTER" }
                                        ),
                                        Parameter(PredefinedType::Enum, "Attribute", { "INTERN", "EXTERN" }),
                                        Parameter(PredefinedType::Ulong, "Address"),
                                        Parameter(PredefinedType::Ulong, "Size"),
                                        Parameter(PredefinedType::Long, "Offset_0"),
                                        Parameter(PredefinedType::Long, "Offset_1"),
                                        Parameter(PredefinedType::Long, "Offset_2"),
                                        Parameter(PredefinedType::Long, "Offset_3"),
                                        Parameter(PredefinedType::Long, "Offset_4"),
                                    },
                                    {
                                        Keyword(
                                            A2LTokenType::IF_DATA, "IF_DATA", true, true,
                                            {
                                                Parameter(PredefinedType::Ident, "name"),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::NO_OF_INTERFACES, "NO_OF_INTERFACES", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Num"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::PHONE_NO, "PHONE_NO", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Telnum"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SUPPLIER, "SUPPLIER", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Manufacturer"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SYSTEM_CONSTANT, "SYSTEM_CONSTANT", false, true,
                                    {
                                        Parameter(PredefinedType::String, "Name"),
                                        Parameter(PredefinedType::String, "Value"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::USER, "USER", false, false,
                                    {
                                        Parameter(PredefinedType::String, "UserName"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::VERSION, "VERSION", false, false,
                                    {
                                        Parameter(PredefinedType::String, "VersionIdentifier"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::RECORD_LAYOUT, "RECORD_LAYOUT", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ALIGNMENT_BYTE, "ALIGNMENT_BYTE", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_FLOAT16_IEEE, "ALIGNMENT_FLOAT16_IEEE", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_FLOAT32_IEEE, "ALIGNMENT_FLOAT32_IEEE", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_FLOAT64_IEEE, "ALIGNMENT_FLOAT64_IEEE", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_INT64, "ALIGNMENT_INT64", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_LONG, "ALIGNMENT_LONG", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_WORD, "ALIGNMENT_WORD", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_PTS_X, "AXIS_PTS_X", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                        Parameter(PredefinedType::Indexorder, "IndexIncr"),
                                        Parameter(PredefinedType::Addrtype, "Addressing"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_PTS_Y, "AXIS_PTS_Y", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                        Parameter(PredefinedType::Indexorder, "IndexIncr"),
                                        Parameter(PredefinedType::Addrtype, "Addressing"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_PTS_Z, "AXIS_PTS_Z", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                        Parameter(PredefinedType::Indexorder, "IndexIncr"),
                                        Parameter(PredefinedType::Addrtype, "Addressing"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_PTS_4, "AXIS_PTS_4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                        Parameter(PredefinedType::Indexorder, "IndexIncr"),
                                        Parameter(PredefinedType::Addrtype, "Addressing"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_PTS_5, "AXIS_PTS_5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                        Parameter(PredefinedType::Indexorder, "IndexIncr"),
                                        Parameter(PredefinedType::Addrtype, "Addressing"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_RESCALE_X, "AXIS_RESCALE_X", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                        Parameter(PredefinedType::Uint, "MaxNumberOfRescalePairs"),
                                        Parameter(PredefinedType::Indexorder, "IndexIncr"),
                                        Parameter(PredefinedType::Addrtype, "Addressing"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_RESCALE_Y, "AXIS_RESCALE_Y", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                        Parameter(PredefinedType::Uint, "MaxNumberOfRescalePairs"),
                                        Parameter(PredefinedType::Indexorder, "IndexIncr"),
                                        Parameter(PredefinedType::Addrtype, "Addressing"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_RESCALE_Z, "AXIS_RESCALE_Z", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                        Parameter(PredefinedType::Uint, "MaxNumberOfRescalePairs"),
                                        Parameter(PredefinedType::Indexorder, "IndexIncr"),
                                        Parameter(PredefinedType::Addrtype, "Addressing"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_RESCALE_4, "AXIS_RESCALE_4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                        Parameter(PredefinedType::Uint, "MaxNumberOfRescalePairs"),
                                        Parameter(PredefinedType::Indexorder, "IndexIncr"),
                                        Parameter(PredefinedType::Addrtype, "Addressing"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_RESCALE_5, "AXIS_RESCALE_5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                        Parameter(PredefinedType::Uint, "MaxNumberOfRescalePairs"),
                                        Parameter(PredefinedType::Indexorder, "IndexIncr"),
                                        Parameter(PredefinedType::Addrtype, "Addressing"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DIST_OP_X, "DIST_OP_X", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DIST_OP_Y, "DIST_OP_Y", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DIST_OP_Z, "DIST_OP_Z", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DIST_OP_4, "DIST_OP_4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DIST_OP_5, "DIST_OP_5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FIX_NO_AXIS_PTS_X, "FIX_NO_AXIS_PTS_X", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "NumberOfAxisPoints"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FIX_NO_AXIS_PTS_Y, "FIX_NO_AXIS_PTS_Y", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "NumberOfAxisPoints"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FIX_NO_AXIS_PTS_Z, "FIX_NO_AXIS_PTS_Z", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "NumberOfAxisPoints"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FIX_NO_AXIS_PTS_4, "FIX_NO_AXIS_PTS_4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "NumberOfAxisPoints"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FIX_NO_AXIS_PTS_5, "FIX_NO_AXIS_PTS_5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "NumberOfAxisPoints"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FNC_VALUES, "FNC_VALUES", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                        Parameter(
                                            PredefinedType::Enum, "IndexMode",
                                            { "ALTERNATE_CURVES", "ALTERNATE_WITH_X", "ALTERNATE_WITH_Y", "COLUMN_DIR", "ROW_DIR" }
                                        ),
                                        Parameter(PredefinedType::Addrtype, "Addresstype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::IDENTIFICATION, "IDENTIFICATION", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_AXIS_PTS_X, "NO_AXIS_PTS_X", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_AXIS_PTS_Y, "NO_AXIS_PTS_Y", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_AXIS_PTS_Z, "NO_AXIS_PTS_Z", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_AXIS_PTS_4, "NO_AXIS_PTS_4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_AXIS_PTS_5, "NO_AXIS_PTS_5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::STATIC_RECORD_LAYOUT, "STATIC_RECORD_LAYOUT", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::NO_RESCALE_X, "NO_RESCALE_X", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_RESCALE_Y, "NO_RESCALE_Y", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_RESCALE_Z, "NO_RESCALE_Z", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_RESCALE_4, "NO_RESCALE_4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_RESCALE_5, "NO_RESCALE_5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::OFFSET_X, "OFFSET_X", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::OFFSET_Y, "OFFSET_Y", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::OFFSET_Z, "OFFSET_Z", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::OFFSET_4, "OFFSET_4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::OFFSET_5, "OFFSET_5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RESERVED, "RESERVED", false, true,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datasize, "DataSize"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RIP_ADDR_W, "RIP_ADDR_W", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RIP_ADDR_X, "RIP_ADDR_X", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RIP_ADDR_Y, "RIP_ADDR_Y", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RIP_ADDR_Z, "RIP_ADDR_Z", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RIP_ADDR_4, "RIP_ADDR_4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RIP_ADDR_5, "RIP_ADDR_5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SHIFT_OP_X, "SHIFT_OP_X", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SHIFT_OP_Y, "SHIFT_OP_Y", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SHIFT_OP_Z, "SHIFT_OP_Z", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SHIFT_OP_4, "SHIFT_OP_4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SHIFT_OP_5, "SHIFT_OP_5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SRC_ADDR_X, "SRC_ADDR_X", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SRC_ADDR_Y, "SRC_ADDR_Y", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SRC_ADDR_Z, "SRC_ADDR_Z", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SRC_ADDR_4, "SRC_ADDR_4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SRC_ADDR_5, "SRC_ADDR_5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Datatype, "Datatype"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::TYPEDEF_CHARACTERISTIC, "TYPEDEF_CHARACTERISTIC", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(
                                    PredefinedType::Enum, "Type",
                                    { "ASCII", "CURVE", "MAP", "CUBOID", "CUBE_4", "CUBE_5", "VAL_BLK", "VALUE" }
                                ),
                                Parameter(PredefinedType::Ident, "Deposit"),
                                Parameter(PredefinedType::Float, "MaxDiff"),
                                Parameter(PredefinedType::Ident, "Conversion"),
                                Parameter(PredefinedType::Float, "LowerLimit"),
                                Parameter(PredefinedType::Float, "UpperLimit"),
                            },
                            {}
                        ),
                        Keyword(
                            A2LTokenType::TYPEDEF_MEASUREMENT, "TYPEDEF_MEASUREMENT", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(PredefinedType::Datatype, "Datatype"),
                                Parameter(PredefinedType::Ident, "Conversion"),
                                Parameter(PredefinedType::Uint, "Resolution"),
                                Parameter(PredefinedType::Float, "Accuracy"),
                                Parameter(PredefinedType::Float, "LowerLimit"),
                                Parameter(PredefinedType::Float, "UpperLimit"),
                            },
                            {}
                        ),
                        Keyword(
                            A2LTokenType::TYPEDEF_STRUCTURE, "TYPEDEF_STRUCTURE", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(PredefinedType::Ulong, "Size"),
                                Parameter(PredefinedType::Linktype, "Link"),
                                Parameter(PredefinedType::String, "Symbol"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::STRUCTURE_COMPONENT, "STRUCTURE_COMPONENT", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                        Parameter(PredefinedType::Ident, "Deposit"),
                                        Parameter(PredefinedType::Ulong, "Offset"),
                                        Parameter(PredefinedType::Linktype, "Link"),
                                        Parameter(PredefinedType::String, "Symbol"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::UNIT, "UNIT", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(PredefinedType::String, "Display"),
                                Parameter(PredefinedType::Enum, "Type", { "DERIVED", "EXTENDED_SI" }),
                            },
                            {
                                Keyword(
                                    A2LTokenType::SI_EXPONENTS, "SI_EXPONENTS", false, false,
                                    {
                                        Parameter(PredefinedType::Int, "Length"),
                                        Parameter(PredefinedType::Int, "Mass"),
                                        Parameter(PredefinedType::Int, "Time"),
                                        Parameter(PredefinedType::Int, "ElectricCurrent"),
                                        Parameter(PredefinedType::Int, "Temperature"),
                                        Parameter(PredefinedType::Int, "AmountOfSubstance"),
                                        Parameter(PredefinedType::Int, "LuminousIntensity"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::REF_UNIT, "REF_UNIT", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Unit"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::UNIT_CONVERSION, "UNIT_CONVERSION", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "Gradient"),
                                        Parameter(PredefinedType::Float, "Offset"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::USER_RIGHTS, "USER_RIGHTS", true, true,
                            {
                                Parameter(PredefinedType::Ident, "UserLevelId"),
                            },
                            {
                                Keyword(A2LTokenType::READ_ONLY, "READ_ONLY", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::REF_GROUP, "REF_GROUP", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),  // MULT
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::VARIANT_CODING, "VARIANT_CODING", true, false, {},
                            {
                                Keyword(
                                    A2LTokenType::VAR_CHARACTERISTIC, "VAR_CHARACTERISTIC", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                        Parameter(PredefinedType::Ident, "CriterionName", true),  // MULT
                                    },
                                    {
                                        Keyword(
                                            A2LTokenType::VAR_ADDRESS, "VAR_ADDRESS", true, false,
                                            {
                                                Parameter(PredefinedType::Ulong, "Address", true),  // MULT
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::VAR_CRITERION, "VAR_CRITERION", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                        Parameter(PredefinedType::String, "LongIdentifier"),
                                        Parameter(PredefinedType::Ident, "Value", true),  // MULT
                                    },
                                    {
                                        Keyword(
                                            A2LTokenType::VAR_MEASUREMENT, "VAR_MEASUREMENT", false, false,
                                            {
                                                Parameter(PredefinedType::Ident, "Name"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::VAR_SELECTION_CHARACTERISTIC, "VAR_SELECTION_CHARACTERISTIC", false,
                                            false,
                                            {
                                                Parameter(PredefinedType::Ident, "Name"),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(A2LTokenType::VAR_FORBIDDEN_COMB, "VAR_FORBIDDEN_COMB", true, true, {}, {}),
                                Keyword(
                                    A2LTokenType::VAR_NAMING, "VAR_NAMING", false, false,
                                    {
                                        Parameter(PredefinedType::Enum, "Tag", { "NUMERIC", "APLHA" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::VAR_SEPARATOR, "VAR_SEPARATOR", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Separator"),
                                    },
                                    {}
                                ),
                            }
                        ),
                    }
                ),
            }
        ),
    }
);
