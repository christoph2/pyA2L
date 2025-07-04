inline Keyword PARSER_TABLE = Keyword(
    A2LTokenType::PROJECT, "ROOT", "Root", false, false,
    {
},
    {
        Keyword(
            A2LTokenType::ASAP2_VERSION, "ASAP2_VERSION", "Asap2Version", false, false,
            {
                Parameter(PredefinedType::Uint, "VersionNo"),
                Parameter(PredefinedType::Uint, "UpgradeNo"),
            },
            {}
        ),
        Keyword(
            A2LTokenType::A2ML_VERSION, "A2ML_VERSION", "A2mlVersion", false, false,
            {
                Parameter(PredefinedType::Uint, "VersionNo"),
                Parameter(PredefinedType::Uint, "UpgradeNo"),
            },
            {}
        ),
        Keyword(
            A2LTokenType::PROJECT, "PROJECT", "Project", true, false,
            {
                Parameter(PredefinedType::Ident, "Name"),
                Parameter(PredefinedType::String, "LongIdentifier"),
            },
            {
                Keyword(
                    A2LTokenType::HEADER, "HEADER", "Header", true, false,
                    {
                        Parameter(PredefinedType::String, "Comment"),
                    },
                    {
                        Keyword(
                            A2LTokenType::PROJECT_NO, "PROJECT_NO", "ProjectNo", false, false,
                            {
                                Parameter(PredefinedType::Ident, "ProjectNumber"),
                            },
                            {}
                        ),
                        Keyword(
                            A2LTokenType::VERSION, "VERSION", "Version", false, false,
                            {
                                Parameter(PredefinedType::String, "VersionIdentifier"),
                            },
                            {}
                        ),
                    }
                ),
                Keyword(
                    A2LTokenType::MODULE, "MODULE", "Module", true, true,
                    {
                        Parameter(PredefinedType::Ident, "Name"),
                        Parameter(PredefinedType::String, "LongIdentifier"),
                    },
                    {
                        Keyword(A2LTokenType::A2ML, "A2ML", "A2ml", true, false, {}, {}),
                        Keyword(
                            A2LTokenType::AXIS_PTS, "AXIS_PTS", "AxisPts", true, true,
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
                                    A2LTokenType::ANNOTATION, "ANNOTATION", "Annotation", true, true, {},
                                    {
                                        Keyword(
                                            A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", "AnnotationLabel", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Label"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", "AnnotationOrigin", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Origin"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", "AnnotationText", true, false,
                                            {
                                                Parameter(PredefinedType::String, "Text", true),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::_BYTE_ORDER, "_BYTE_ORDER", "ByteOrder", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Byteorder",
                                            { "_LITTLE_ENDIAN", "_BIG_ENDIAN", "MSB_LAST", "MSB_FIRST" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::CALIBRATION_ACCESS, "CALIBRATION_ACCESS", "CalibrationAccess", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Type",
                                            { "CALIBRATION", "NO_CALIBRATION", "NOT_IN_MCD_SYSTEM", "OFFLINE_CALIBRATION" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DEPOSIT, "DEPOSIT", "Deposit", false, false,
                                    {
                                        Parameter(PredefinedType::Enum, "Mode", { "ABSOLUTE", "DIFFERENCE" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DISPLAY_IDENTIFIER, "DISPLAY_IDENTIFIER", "DisplayIdentifier", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "display_name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU_ADDRESS_EXTENSION, "ECU_ADDRESS_EXTENSION", "EcuAddressExtension", false,
                                    false,
                                    {
                                        Parameter(PredefinedType::Int, "Extension"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::EXTENDED_LIMITS, "EXTENDED_LIMITS", "ExtendedLimits", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "LowerLimit"),
                                        Parameter(PredefinedType::Float, "UpperLimit"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FORMAT, "FORMAT", "Format", false, false,
                                    {
                                        Parameter(PredefinedType::String, "FormatString"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FUNCTION_LIST, "FUNCTION_LIST", "FunctionList", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name", true),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::GUARD_RAILS, "GUARD_RAILS", "GuardRails", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", "IfData", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MONOTONY, "MONOTONY", "Monotony", false, false,
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
                                    A2LTokenType::PHYS_UNIT, "PHYS_UNIT", "PhysUnit", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Unit"),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::READ_ONLY, "READ_ONLY", "ReadOnly", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::REF_MEMORY_SEGMENT, "REF_MEMORY_SEGMENT", "RefMemorySegment", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::STEP_SIZE, "STEP_SIZE", "StepSize", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "StepSize"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SYMBOL_LINK, "SYMBOL_LINK", "SymbolLink", false, false,
                                    {
                                        Parameter(PredefinedType::String, "SymbolName"),
                                        Parameter(PredefinedType::Long, "Offset"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::CHARACTERISTIC, "CHARACTERISTIC", "Characteristic", true, true,
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
                                    A2LTokenType::ANNOTATION, "ANNOTATION", "Annotation", true, true, {},
                                    {
                                        Keyword(
                                            A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", "AnnotationLabel", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Label"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", "AnnotationOrigin", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Origin"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", "AnnotationText", true, false,
                                            {
                                                Parameter(PredefinedType::String, "Text", true),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_DESCR, "AXIS_DESCR", "AxisDescr", true, true,
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
                                            A2LTokenType::ANNOTATION, "ANNOTATION", "Annotation", true, true, {},
                                            {
                                                Keyword(
                                                    A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", "AnnotationLabel", false,
                                                    false,
                                                    {
                                                        Parameter(PredefinedType::String, "Label"),
                                                    },
                                                    {}
                                                ),
                                                Keyword(
                                                    A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", "AnnotationOrigin", false,
                                                    false,
                                                    {
                                                        Parameter(PredefinedType::String, "Origin"),
                                                    },
                                                    {}
                                                ),
                                                Keyword(
                                                    A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", "AnnotationText", true, false,
                                                    {
                                                        Parameter(PredefinedType::String, "Text", true),
                                                    },
                                                    {}
                                                ),
                                            }
                                        ),
                                        Keyword(
                                            A2LTokenType::AXIS_PTS_REF, "AXIS_PTS_REF", "AxisPtsRef", false, false,
                                            {
                                                Parameter(PredefinedType::Ident, "AxisPoints"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::_BYTE_ORDER, "_BYTE_ORDER", "ByteOrder", false, false,
                                            {
                                                Parameter(
                                                    PredefinedType::Enum, "Byteorder",
                                                    { "_LITTLE_ENDIAN", "_BIG_ENDIAN", "MSB_LAST", "MSB_FIRST" }
                                                ),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::CURVE_AXIS_REF, "CURVE_AXIS_REF", "CurveAxisRef", false, false,
                                            {
                                                Parameter(PredefinedType::Ident, "CurveAxis"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::DEPOSIT, "DEPOSIT", "Deposit", false, false,
                                            {
                                                Parameter(PredefinedType::Enum, "Mode", { "ABSOLUTE", "DIFFERENCE" }),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::EXTENDED_LIMITS, "EXTENDED_LIMITS", "ExtendedLimits", false, false,
                                            {
                                                Parameter(PredefinedType::Float, "LowerLimit"),
                                                Parameter(PredefinedType::Float, "UpperLimit"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::FIX_AXIS_PAR, "FIX_AXIS_PAR", "FixAxisPar", false, false,
                                            {
                                                Parameter(PredefinedType::Int, "Offset"),
                                                Parameter(PredefinedType::Int, "Shift"),
                                                Parameter(PredefinedType::Uint, "Numberapo"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::FIX_AXIS_PAR_DIST, "FIX_AXIS_PAR_DIST", "FixAxisParDist", false, false,
                                            {
                                                Parameter(PredefinedType::Int, "Offset"),
                                                Parameter(PredefinedType::Int, "Distance"),
                                                Parameter(PredefinedType::Uint, "Numberapo"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::FIX_AXIS_PAR_LIST, "FIX_AXIS_PAR_LIST", "FixAxisParList", true, false,
                                            {
                                                Parameter(PredefinedType::Float, "AxisPts_Value", true),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::FORMAT, "FORMAT", "Format", false, false,
                                            {
                                                Parameter(PredefinedType::String, "FormatString"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::MAX_GRAD, "MAX_GRAD", "MaxGrad", false, false,
                                            {
                                                Parameter(PredefinedType::Float, "MaxGradient"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::MONOTONY, "MONOTONY", "Monotony", false, false,
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
                                            A2LTokenType::PHYS_UNIT, "PHYS_UNIT", "PhysUnit", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Unit"),
                                            },
                                            {}
                                        ),
                                        Keyword(A2LTokenType::READ_ONLY, "READ_ONLY", "ReadOnly", false, false, {}, {}),
                                        Keyword(
                                            A2LTokenType::STEP_SIZE, "STEP_SIZE", "StepSize", false, false,
                                            {
                                                Parameter(PredefinedType::Float, "StepSize"),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::BIT_MASK, "BIT_MASK", "BitMask", false, false,
                                    {
                                        Parameter(PredefinedType::Ulong, "Mask"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::_BYTE_ORDER, "_BYTE_ORDER", "ByteOrder", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Byteorder",
                                            { "_LITTLE_ENDIAN", "_BIG_ENDIAN", "MSB_LAST", "MSB_FIRST" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::CALIBRATION_ACCESS, "CALIBRATION_ACCESS", "CalibrationAccess", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Type",
                                            { "CALIBRATION", "NO_CALIBRATION", "NOT_IN_MCD_SYSTEM", "OFFLINE_CALIBRATION" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::COMPARISON_QUANTITY, "COMPARISON_QUANTITY", "ComparisonQuantity", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DEPENDENT_CHARACTERISTIC, "DEPENDENT_CHARACTERISTIC", "DependentCharacteristic",
                                    true, false,
                                    {
                                        Parameter(PredefinedType::String, "Formula"),
                                        Parameter(PredefinedType::Ident, "Characteristic", true),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::DISCRETE, "DISCRETE", "Discrete", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::DISPLAY_IDENTIFIER, "DISPLAY_IDENTIFIER", "DisplayIdentifier", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "display_name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU_ADDRESS_EXTENSION, "ECU_ADDRESS_EXTENSION", "EcuAddressExtension", false,
                                    false,
                                    {
                                        Parameter(PredefinedType::Int, "Extension"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::EXTENDED_LIMITS, "EXTENDED_LIMITS", "ExtendedLimits", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "LowerLimit"),
                                        Parameter(PredefinedType::Float, "UpperLimit"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FORMAT, "FORMAT", "Format", false, false,
                                    {
                                        Parameter(PredefinedType::String, "FormatString"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FUNCTION_LIST, "FUNCTION_LIST", "FunctionList", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name", true),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::GUARD_RAILS, "GUARD_RAILS", "GuardRails", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", "IfData", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MAP_LIST, "MAP_LIST", "MapList", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MATRIX_DIM, "MATRIX_DIM", "MatrixDim", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Numbers", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MAX_REFRESH, "MAX_REFRESH", "MaxRefresh", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "ScalingUnit"),
                                        Parameter(PredefinedType::Ulong, "Rate"),
                                    },
                                    {}
                                ),
								Keyword(
									A2LTokenType::MODEL_LINK, "MODEL_LINK", "ModelLink", false, false,
									{
										Parameter(PredefinedType::String, "link"),
									},
									{}
								),
                                Keyword(
                                    A2LTokenType::NUMBER, "NUMBER", "Number", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Number"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::PHYS_UNIT, "PHYS_UNIT", "PhysUnit", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Unit"),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::READ_ONLY, "READ_ONLY", "ReadOnly", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::REF_MEMORY_SEGMENT, "REF_MEMORY_SEGMENT", "RefMemorySegment", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::STEP_SIZE, "STEP_SIZE", "StepSize", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "StepSize"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SYMBOL_LINK, "SYMBOL_LINK", "SymbolLink", false, false,
                                    {
                                        Parameter(PredefinedType::String, "SymbolName"),
                                        Parameter(PredefinedType::Long, "Offset"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::VIRTUAL_CHARACTERISTIC, "VIRTUAL_CHARACTERISTIC", "VirtualCharacteristic", true,
                                    false,
                                    {
                                        Parameter(PredefinedType::String, "Formula"),
                                        Parameter(PredefinedType::Ident, "Characteristic", true),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::COMPU_METHOD, "COMPU_METHOD", "CompuMethod", true, true,
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
                                    A2LTokenType::COEFFS, "COEFFS", "Coeffs", false, false,
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
                                    A2LTokenType::COEFFS_LINEAR, "COEFFS_LINEAR", "CoeffsLinear", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "a"),
                                        Parameter(PredefinedType::Float, "b"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::COMPU_TAB_REF, "COMPU_TAB_REF", "CompuTabRef", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "ConversionTable"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FORMULA, "FORMULA", "Formula", true, false,
                                    {
                                        Parameter(PredefinedType::String, "F_x"),
                                    },
                                    {
                                        Keyword(
                                            A2LTokenType::FORMULA_INV, "FORMULA_INV", "FormulaInv", false, false,
                                            {
                                                Parameter(PredefinedType::String, "G_x"),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::REF_UNIT, "REF_UNIT", "RefUnit", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Unit"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::STATUS_STRING_REF, "STATUS_STRING_REF", "StatusStringRef", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "ConversionTable"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::COMPU_TAB, "COMPU_TAB", "CompuTab", true, true,
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
                                    A2LTokenType::DEFAULT_VALUE, "DEFAULT_VALUE", "DefaultValue", false, false,
                                    {
                                        Parameter(PredefinedType::String, "display_string"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DEFAULT_VALUE_NUMERIC, "DEFAULT_VALUE_NUMERIC", "DefaultValueNumeric", false,
                                    false,
                                    {
                                        Parameter(PredefinedType::Float, "display_value"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::COMPU_VTAB, "COMPU_VTAB", "CompuVtab", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(PredefinedType::Enum, "ConversionType", { "TAB_VERB", "" }),
                                Parameter(
                                    { PredefinedType::Uint, "NumberValuePairs" },
                                    { { PredefinedType::Float, "InVal" }, { PredefinedType::String, "OutVal" } }
                                ),
                            },
                            {
                                Keyword(
                                    A2LTokenType::DEFAULT_VALUE, "DEFAULT_VALUE", "DefaultValue", false, false,
                                    {
                                        Parameter(PredefinedType::String, "display_string"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::COMPU_VTAB_RANGE, "COMPU_VTAB_RANGE", "CompuVtabRange", true, true,
                            { Parameter(PredefinedType::Ident, "Name"), Parameter(PredefinedType::String, "LongIdentifier"),
                              Parameter(
                                  { PredefinedType::Uint, "NumberValueTriples" }, { { PredefinedType::Float, "InValMin" },
                                                                                    { PredefinedType::Float, "InValMax" },
                                                                                    { PredefinedType::String, "OutVal" } }
                              ) },
                            {
                                Keyword(
                                    A2LTokenType::DEFAULT_VALUE, "DEFAULT_VALUE", "DefaultValue", false, false,
                                    {
                                        Parameter(PredefinedType::String, "display_string"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::FRAME, "FRAME", "Frame", true, false,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(PredefinedType::Uint, "ScalingUnit"),
                                Parameter(PredefinedType::Ulong, "Rate"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::FRAME_MEASUREMENT, "FRAME_MEASUREMENT", "FrameMeasurement", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", "IfData", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::FUNCTION, "FUNCTION", "Function", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ANNOTATION, "ANNOTATION", "Annotation", true, true, {},
                                    {
                                        Keyword(
                                            A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", "AnnotationLabel", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Label"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", "AnnotationOrigin", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Origin"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", "AnnotationText", true, false,
                                            {
                                                Parameter(PredefinedType::String, "Text", true),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::DEF_CHARACTERISTIC, "DEF_CHARACTERISTIC", "DefCharacteristic", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FUNCTION_VERSION, "FUNCTION_VERSION", "FunctionVersion", false, false,
                                    {
                                        Parameter(PredefinedType::String, "VersionIdentifier"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", "IfData", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::IN_MEASUREMENT, "IN_MEASUREMENT", "InMeasurement", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::LOC_MEASUREMENT, "LOC_MEASUREMENT", "LocMeasurement", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::OUT_MEASUREMENT, "OUT_MEASUREMENT", "OutMeasurement", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::REF_CHARACTERISTIC, "REF_CHARACTERISTIC", "RefCharacteristic", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SUB_FUNCTION, "SUB_FUNCTION", "SubFunction", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::GROUP, "GROUP", "Group", true, true,
                            {
                                Parameter(PredefinedType::Ident, "GroupName"),
                                Parameter(PredefinedType::String, "GroupLongIdentifier"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ANNOTATION, "ANNOTATION", "Annotation", true, true, {},
                                    {
                                        Keyword(
                                            A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", "AnnotationLabel", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Label"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", "AnnotationOrigin", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Origin"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", "AnnotationText", true, false,
                                            {
                                                Parameter(PredefinedType::String, "Text", true),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::FUNCTION_LIST, "FUNCTION_LIST", "FunctionList", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", "IfData", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::REF_CHARACTERISTIC, "REF_CHARACTERISTIC", "RefCharacteristic", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::REF_MEASUREMENT, "REF_MEASUREMENT", "RefMeasurement", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::ROOT, "ROOT", "Root", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::SUB_GROUP, "SUB_GROUP", "SubGroup", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::IF_DATA, "IF_DATA", "IfData", true, true,
                            {
                                Parameter(PredefinedType::Ident, "name"),
                            },
                            {}
                        ),
                        Keyword(
                            A2LTokenType::INSTANCE, "INSTANCE", "Instance", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(PredefinedType::Ident, "TypeName"),
                                Parameter(PredefinedType::Ulong, "Address"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::COMPARISON_QUANTITY, "COMPARISON_QUANTITY", "ComparisonQuantity", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DEPENDENT_CHARACTERISTIC, "DEPENDENT_CHARACTERISTIC", "DependentCharacteristic",
                                    true, false,
                                    {
                                        Parameter(PredefinedType::String, "Formula"),
                                        Parameter(PredefinedType::Ident, "Characteristic", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DISPLAY_IDENTIFIER, "DISPLAY_IDENTIFIER", "DisplayIdentifier", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "display_name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU_ADDRESS_EXTENSION, "ECU_ADDRESS_EXTENSION", "EcuAddressExtension", false,
                                    false,
                                    {
                                        Parameter(PredefinedType::Int, "Extension"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", "IfData", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MATRIX_DIM, "MATRIX_DIM", "MatrixDim", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Numbers", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NUMBER, "NUMBER", "Number", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Number"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SYMBOL_LINK, "SYMBOL_LINK", "SymbolLink", false, false,
                                    {
                                        Parameter(PredefinedType::String, "SymbolName"),
                                        Parameter(PredefinedType::Long, "Offset"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::MEASUREMENT, "MEASUREMENT", "Measurement", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(
                                    PredefinedType::Enum, "Datatype",
                                    { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64", "FLOAT16_IEEE",
                                      "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                ),
                                Parameter(PredefinedType::Ident, "Conversion"),
                                Parameter(PredefinedType::Uint, "Resolution"),
                                Parameter(PredefinedType::Float, "Accuracy"),
                                Parameter(PredefinedType::Float, "LowerLimit"),
                                Parameter(PredefinedType::Float, "UpperLimit"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ANNOTATION, "ANNOTATION", "Annotation", true, true, {},
                                    {
                                        Keyword(
                                            A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", "AnnotationLabel", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Label"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", "AnnotationOrigin", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Origin"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", "AnnotationText", true, false,
                                            {
                                                Parameter(PredefinedType::String, "Text", true),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::ARRAY_SIZE, "ARRAY_SIZE", "ArraySize", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Number"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::BIT_MASK, "BIT_MASK", "BitMask", false, false,
                                    {
                                        Parameter(PredefinedType::Ulong, "Mask"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::BIT_OPERATION, "BIT_OPERATION", "BitOperation", true, false, {},
                                    {
                                        Keyword(
                                            A2LTokenType::LEFT_SHIFT, "LEFT_SHIFT", "LeftShift", false, false,
                                            {
                                                Parameter(PredefinedType::Ulong, "Bitcount"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::RIGHT_SHIFT, "RIGHT_SHIFT", "RightShift", false, false,
                                            {
                                                Parameter(PredefinedType::Ulong, "Bitcount"),
                                            },
                                            {}
                                        ),
                                        Keyword(A2LTokenType::SIGN_EXTEND, "SIGN_EXTEND", "SignExtend", false, false, {}, {}),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::_BYTE_ORDER, "_BYTE_ORDER", "ByteOrder", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Byteorder",
                                            { "_LITTLE_ENDIAN", "_BIG_ENDIAN", "MSB_LAST", "MSB_FIRST" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::DISCRETE, "DISCRETE", "Discrete", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::DISPLAY_IDENTIFIER, "DISPLAY_IDENTIFIER", "DisplayIdentifier", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "display_name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU_ADDRESS, "ECU_ADDRESS", "EcuAddress", false, false,
                                    {
                                        Parameter(PredefinedType::Ulong, "Address"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU_ADDRESS_EXTENSION, "ECU_ADDRESS_EXTENSION", "EcuAddressExtension", false,
                                    false,
                                    {
                                        Parameter(PredefinedType::Int, "Extension"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ERROR_MASK, "ERROR_MASK", "ErrorMask", false, false,
                                    {
                                        Parameter(PredefinedType::Ulong, "Mask"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FORMAT, "FORMAT", "Format", false, false,
                                    {
                                        Parameter(PredefinedType::String, "FormatString"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FUNCTION_LIST, "FUNCTION_LIST", "FunctionList", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", "IfData", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::LAYOUT, "LAYOUT", "Layout", false, false,
                                    {
                                        Parameter(PredefinedType::Enum, "IndexMode", { "ROW_DIR", "COLUMN_DIR" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MATRIX_DIM, "MATRIX_DIM", "MatrixDim", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Numbers", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MAX_REFRESH, "MAX_REFRESH", "MaxRefresh", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "ScalingUnit"),
                                        Parameter(PredefinedType::Ulong, "Rate"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::PHYS_UNIT, "PHYS_UNIT", "PhysUnit", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Unit"),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::READ_WRITE, "READ_WRITE", "ReadWrite", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::REF_MEMORY_SEGMENT, "REF_MEMORY_SEGMENT", "RefMemorySegment", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SYMBOL_LINK, "SYMBOL_LINK", "SymbolLink", false, false,
                                    {
                                        Parameter(PredefinedType::String, "SymbolName"),
                                        Parameter(PredefinedType::Long, "Offset"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::VIRTUAL, "VIRTUAL", "Virtual", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "MeasuringChannel", true),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::MOD_COMMON, "MOD_COMMON", "ModCommon", true, false,
                            {
                                Parameter(PredefinedType::String, "Comment"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ALIGNMENT_BYTE, "ALIGNMENT_BYTE", "AlignmentByte", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_FLOAT16_IEEE, "ALIGNMENT_FLOAT16_IEEE", "AlignmentFloat16Ieee", false,
                                    false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_FLOAT32_IEEE, "ALIGNMENT_FLOAT32_IEEE", "AlignmentFloat32Ieee", false,
                                    false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_FLOAT64_IEEE, "ALIGNMENT_FLOAT64_IEEE", "AlignmentFloat64Ieee", false,
                                    false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_INT64, "ALIGNMENT_INT64", "AlignmentInt64", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_LONG, "ALIGNMENT_LONG", "AlignmentLong", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_WORD, "ALIGNMENT_WORD", "AlignmentWord", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::_BYTE_ORDER, "_BYTE_ORDER", "ByteOrder", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Byteorder",
                                            { "_LITTLE_ENDIAN", "_BIG_ENDIAN", "MSB_LAST", "MSB_FIRST" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DATA_SIZE, "DATA_SIZE", "DataSize", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Size"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DEPOSIT, "DEPOSIT", "Deposit", false, false,
                                    {
                                        Parameter(PredefinedType::Enum, "Mode", { "ABSOLUTE", "DIFFERENCE" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::S_REC_LAYOUT, "S_REC_LAYOUT", "SRecLayout", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::MOD_PAR, "MOD_PAR", "ModPar", true, false,
                            {
                                Parameter(PredefinedType::String, "Comment"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ADDR_EPK, "ADDR_EPK", "AddrEpk", false, true,
                                    {
                                        Parameter(PredefinedType::Ulong, "Address"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::CALIBRATION_METHOD, "CALIBRATION_METHOD", "CalibrationMethod", true, true,
                                    {
                                        Parameter(PredefinedType::String, "Method"),
                                        Parameter(PredefinedType::Ulong, "Version"),
                                    },
                                    {
                                        Keyword(
                                            A2LTokenType::CALIBRATION_HANDLE, "CALIBRATION_HANDLE", "CalibrationHandle", true, true,
                                            {
                                                Parameter(PredefinedType::Ulong, "Handle", true),
                                            },
                                            {
                                                Keyword(
                                                    A2LTokenType::CALIBRATION_HANDLE_TEXT, "CALIBRATION_HANDLE_TEXT",
                                                    "CalibrationHandleText", false, false,
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
                                    A2LTokenType::CPU_TYPE, "CPU_TYPE", "CpuType", false, false,
                                    {
                                        Parameter(PredefinedType::String, "CPU"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::CUSTOMER, "CUSTOMER", "Customer", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Customer"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::CUSTOMER_NO, "CUSTOMER_NO", "CustomerNo", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Number"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU, "ECU", "Ecu", false, false,
                                    {
                                        Parameter(PredefinedType::String, "ControlUnit"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ECU_CALIBRATION_OFFSET, "ECU_CALIBRATION_OFFSET", "EcuCalibrationOffset", false,
                                    false,
                                    {
                                        Parameter(PredefinedType::Long, "Offset"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::EPK, "EPK", "Epk", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Identifier"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MEMORY_LAYOUT, "MEMORY_LAYOUT", "MemoryLayout", true, true,
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
                                            A2LTokenType::IF_DATA, "IF_DATA", "IfData", true, true,
                                            {
                                                Parameter(PredefinedType::Ident, "name"),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::MEMORY_SEGMENT, "MEMORY_SEGMENT", "MemorySegment", true, true,
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
                                            { "EEPROM", "EPROM", "FLASH", "RAM", "ROM", "REGISTER", "NOT_IN_ECU" }
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
                                            A2LTokenType::IF_DATA, "IF_DATA", "IfData", true, true,
                                            {
                                                Parameter(PredefinedType::Ident, "name"),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::NO_OF_INTERFACES, "NO_OF_INTERFACES", "NoOfInterfaces", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Num"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::PHONE_NO, "PHONE_NO", "PhoneNo", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Telnum"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SUPPLIER, "SUPPLIER", "Supplier", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Manufacturer"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SYSTEM_CONSTANT, "SYSTEM_CONSTANT", "SystemConstant", false, true,
                                    {
                                        Parameter(PredefinedType::String, "Name"),
                                        Parameter(PredefinedType::String, "Value"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::USER, "USER", "User", false, false,
                                    {
                                        Parameter(PredefinedType::String, "UserName"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::VERSION, "VERSION", "Version", false, false,
                                    {
                                        Parameter(PredefinedType::String, "VersionIdentifier"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::RECORD_LAYOUT, "RECORD_LAYOUT", "RecordLayout", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                            },
                            {
                                Keyword(
                                    A2LTokenType::ALIGNMENT_BYTE, "ALIGNMENT_BYTE", "AlignmentByte", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_FLOAT16_IEEE, "ALIGNMENT_FLOAT16_IEEE", "AlignmentFloat16Ieee", false,
                                    false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_FLOAT32_IEEE, "ALIGNMENT_FLOAT32_IEEE", "AlignmentFloat32Ieee", false,
                                    false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_FLOAT64_IEEE, "ALIGNMENT_FLOAT64_IEEE", "AlignmentFloat64Ieee", false,
                                    false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_INT64, "ALIGNMENT_INT64", "AlignmentInt64", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_LONG, "ALIGNMENT_LONG", "AlignmentLong", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::ALIGNMENT_WORD, "ALIGNMENT_WORD", "AlignmentWord", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "AlignmentBorder"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_PTS_X, "AXIS_PTS_X", "AxisPtsX", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                        Parameter(PredefinedType::Enum, "Indexorder", { "INDEX_INCR", "INDEX_DECR" }),
                                        Parameter(PredefinedType::Enum, "Addresstype", { "PBYTE", "PWORD", "PLONG", "DIRECT" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_PTS_Y, "AXIS_PTS_Y", "AxisPtsY", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                        Parameter(PredefinedType::Enum, "Indexorder", { "INDEX_INCR", "INDEX_DECR" }),
                                        Parameter(PredefinedType::Enum, "Addresstype", { "PBYTE", "PWORD", "PLONG", "DIRECT" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_PTS_Z, "AXIS_PTS_Z", "AxisPtsZ", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                        Parameter(PredefinedType::Enum, "Indexorder", { "INDEX_INCR", "INDEX_DECR" }),
                                        Parameter(PredefinedType::Enum, "Addresstype", { "PBYTE", "PWORD", "PLONG", "DIRECT" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_PTS_4, "AXIS_PTS_4", "AxisPts4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                        Parameter(PredefinedType::Enum, "Indexorder", { "INDEX_INCR", "INDEX_DECR" }),
                                        Parameter(PredefinedType::Enum, "Addresstype", { "PBYTE", "PWORD", "PLONG", "DIRECT" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_PTS_5, "AXIS_PTS_5", "AxisPts5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                        Parameter(PredefinedType::Enum, "Indexorder", { "INDEX_INCR", "INDEX_DECR" }),
                                        Parameter(PredefinedType::Enum, "Addresstype", { "PBYTE", "PWORD", "PLONG", "DIRECT" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_RESCALE_X, "AXIS_RESCALE_X", "AxisRescaleX", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                        Parameter(PredefinedType::Uint, "MaxNumberOfRescalePairs"),
                                        Parameter(PredefinedType::Enum, "Indexorder", { "INDEX_INCR", "INDEX_DECR" }),
                                        Parameter(PredefinedType::Enum, "Addresstype", { "PBYTE", "PWORD", "PLONG", "DIRECT" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_RESCALE_Y, "AXIS_RESCALE_Y", "AxisRescaleY", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                        Parameter(PredefinedType::Uint, "MaxNumberOfRescalePairs"),
                                        Parameter(PredefinedType::Enum, "Indexorder", { "INDEX_INCR", "INDEX_DECR" }),
                                        Parameter(PredefinedType::Enum, "Addresstype", { "PBYTE", "PWORD", "PLONG", "DIRECT" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_RESCALE_Z, "AXIS_RESCALE_Z", "AxisRescaleZ", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                        Parameter(PredefinedType::Uint, "MaxNumberOfRescalePairs"),
                                        Parameter(PredefinedType::Enum, "Indexorder", { "INDEX_INCR", "INDEX_DECR" }),
                                        Parameter(PredefinedType::Enum, "Addresstype", { "PBYTE", "PWORD", "PLONG", "DIRECT" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_RESCALE_4, "AXIS_RESCALE_4", "AxisRescale4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                        Parameter(PredefinedType::Uint, "MaxNumberOfRescalePairs"),
                                        Parameter(PredefinedType::Enum, "Indexorder", { "INDEX_INCR", "INDEX_DECR" }),
                                        Parameter(PredefinedType::Enum, "Addresstype", { "PBYTE", "PWORD", "PLONG", "DIRECT" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_RESCALE_5, "AXIS_RESCALE_5", "AxisRescale5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                        Parameter(PredefinedType::Uint, "MaxNumberOfRescalePairs"),
                                        Parameter(PredefinedType::Enum, "Indexorder", { "INDEX_INCR", "INDEX_DECR" }),
                                        Parameter(PredefinedType::Enum, "Addresstype", { "PBYTE", "PWORD", "PLONG", "DIRECT" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DIST_OP_X, "DIST_OP_X", "DistOpX", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DIST_OP_Y, "DIST_OP_Y", "DistOpY", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DIST_OP_Z, "DIST_OP_Z", "DistOpZ", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DIST_OP_4, "DIST_OP_4", "DistOp4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DIST_OP_5, "DIST_OP_5", "DistOp5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FIX_NO_AXIS_PTS_X, "FIX_NO_AXIS_PTS_X", "FixNoAxisPtsX", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "NumberOfAxisPoints"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FIX_NO_AXIS_PTS_Y, "FIX_NO_AXIS_PTS_Y", "FixNoAxisPtsY", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "NumberOfAxisPoints"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FIX_NO_AXIS_PTS_Z, "FIX_NO_AXIS_PTS_Z", "FixNoAxisPtsZ", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "NumberOfAxisPoints"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FIX_NO_AXIS_PTS_4, "FIX_NO_AXIS_PTS_4", "FixNoAxisPts4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "NumberOfAxisPoints"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FIX_NO_AXIS_PTS_5, "FIX_NO_AXIS_PTS_5", "FixNoAxisPts5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "NumberOfAxisPoints"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FNC_VALUES, "FNC_VALUES", "FncValues", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                        Parameter(
                                            PredefinedType::Enum, "IndexMode",
                                            { "ALTERNATE_CURVES", "ALTERNATE_WITH_X", "ALTERNATE_WITH_Y", "COLUMN_DIR", "ROW_DIR" }
                                        ),
                                        Parameter(PredefinedType::Enum, "Addresstype", { "PBYTE", "PWORD", "PLONG", "DIRECT" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::IDENTIFICATION, "IDENTIFICATION", "Identification", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_AXIS_PTS_X, "NO_AXIS_PTS_X", "NoAxisPtsX", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_AXIS_PTS_Y, "NO_AXIS_PTS_Y", "NoAxisPtsY", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_AXIS_PTS_Z, "NO_AXIS_PTS_Z", "NoAxisPtsZ", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_AXIS_PTS_4, "NO_AXIS_PTS_4", "NoAxisPts4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_AXIS_PTS_5, "NO_AXIS_PTS_5", "NoAxisPts5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::STATIC_RECORD_LAYOUT, "STATIC_RECORD_LAYOUT", "StaticRecordLayout", false, false,
                                    {}, {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_RESCALE_X, "NO_RESCALE_X", "NoRescaleX", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_RESCALE_Y, "NO_RESCALE_Y", "NoRescaleY", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_RESCALE_Z, "NO_RESCALE_Z", "NoRescaleZ", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_RESCALE_4, "NO_RESCALE_4", "NoRescale4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NO_RESCALE_5, "NO_RESCALE_5", "NoRescale5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::OFFSET_X, "OFFSET_X", "OffsetX", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::OFFSET_Y, "OFFSET_Y", "OffsetY", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::OFFSET_Z, "OFFSET_Z", "OffsetZ", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::OFFSET_4, "OFFSET_4", "Offset4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::OFFSET_5, "OFFSET_5", "Offset5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RESERVED, "RESERVED", "Reserved", false, true,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(PredefinedType::Enum, "DataSize", { "BYTE", "WORD", "LONG" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RIP_ADDR_W, "RIP_ADDR_W", "RipAddrW", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RIP_ADDR_X, "RIP_ADDR_X", "RipAddrX", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RIP_ADDR_Y, "RIP_ADDR_Y", "RipAddrY", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RIP_ADDR_Z, "RIP_ADDR_Z", "RipAddrZ", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RIP_ADDR_4, "RIP_ADDR_4", "RipAddr4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::RIP_ADDR_5, "RIP_ADDR_5", "RipAddr5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SHIFT_OP_X, "SHIFT_OP_X", "ShiftOpX", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SHIFT_OP_Y, "SHIFT_OP_Y", "ShiftOpY", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SHIFT_OP_Z, "SHIFT_OP_Z", "ShiftOpZ", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SHIFT_OP_4, "SHIFT_OP_4", "ShiftOp4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SHIFT_OP_5, "SHIFT_OP_5", "ShiftOp5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SRC_ADDR_X, "SRC_ADDR_X", "SrcAddrX", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SRC_ADDR_Y, "SRC_ADDR_Y", "SrcAddrY", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SRC_ADDR_Z, "SRC_ADDR_Z", "SrcAddrZ", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SRC_ADDR_4, "SRC_ADDR_4", "SrcAddr4", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::SRC_ADDR_5, "SRC_ADDR_5", "SrcAddr5", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Position"),
                                        Parameter(
                                            PredefinedType::Enum, "Datatype",
                                            { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64",
                                              "FLOAT16_IEEE", "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                        ),
                                    },
                                    {}
                                ),
                            }
                        ),
						Keyword(
                            A2LTokenType::TYPEDEF_AXIS, "TYPEDEF_AXIS", "TypedefAxis", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
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
                                    A2LTokenType::ANNOTATION, "ANNOTATION", "Annotation", true, true, {},
                                    {
                                        Keyword(
                                            A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", "AnnotationLabel", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Label"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", "AnnotationOrigin", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Origin"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", "AnnotationText", true, false,
                                            {
                                                Parameter(PredefinedType::String, "Text", true),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::_BYTE_ORDER, "_BYTE_ORDER", "ByteOrder", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Byteorder",
                                            { "_LITTLE_ENDIAN", "_BIG_ENDIAN", "MSB_LAST", "MSB_FIRST" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::CALIBRATION_ACCESS, "CALIBRATION_ACCESS", "CalibrationAccess", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Type",
                                            { "CALIBRATION", "NO_CALIBRATION", "NOT_IN_MCD_SYSTEM", "OFFLINE_CALIBRATION" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::DEPOSIT, "DEPOSIT", "Deposit", false, false,
                                    {
                                        Parameter(PredefinedType::Enum, "Mode", { "ABSOLUTE", "DIFFERENCE" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::EXTENDED_LIMITS, "EXTENDED_LIMITS", "ExtendedLimits", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "LowerLimit"),
                                        Parameter(PredefinedType::Float, "UpperLimit"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FORMAT, "FORMAT", "Format", false, false,
                                    {
                                        Parameter(PredefinedType::String, "FormatString"),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::GUARD_RAILS, "GUARD_RAILS", "GuardRails", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::MONOTONY, "MONOTONY", "Monotony", false, false,
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
                                    A2LTokenType::PHYS_UNIT, "PHYS_UNIT", "PhysUnit", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Unit"),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::READ_ONLY, "READ_ONLY", "ReadOnly", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::REF_MEMORY_SEGMENT, "REF_MEMORY_SEGMENT", "RefMemorySegment", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::STEP_SIZE, "STEP_SIZE", "StepSize", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "StepSize"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::TYPEDEF_CHARACTERISTIC, "TYPEDEF_CHARACTERISTIC", "TypedefCharacteristic", true, true,
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
                                                        {
                                Keyword(
                                    A2LTokenType::ANNOTATION, "ANNOTATION", "Annotation", true, true, {},
                                    {
                                        Keyword(
                                            A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", "AnnotationLabel", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Label"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", "AnnotationOrigin", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Origin"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", "AnnotationText", true, false,
                                            {
                                                Parameter(PredefinedType::String, "Text", true),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::AXIS_DESCR, "AXIS_DESCR", "AxisDescr", true, true,
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
                                            A2LTokenType::ANNOTATION, "ANNOTATION", "Annotation", true, true, {},
                                            {
                                                Keyword(
                                                    A2LTokenType::ANNOTATION_LABEL, "ANNOTATION_LABEL", "AnnotationLabel", false,
                                                    false,
                                                    {
                                                        Parameter(PredefinedType::String, "Label"),
                                                    },
                                                    {}
                                                ),
                                                Keyword(
                                                    A2LTokenType::ANNOTATION_ORIGIN, "ANNOTATION_ORIGIN", "AnnotationOrigin", false,
                                                    false,
                                                    {
                                                        Parameter(PredefinedType::String, "Origin"),
                                                    },
                                                    {}
                                                ),
                                                Keyword(
                                                    A2LTokenType::ANNOTATION_TEXT, "ANNOTATION_TEXT", "AnnotationText", true, false,
                                                    {
                                                        Parameter(PredefinedType::String, "Text", true),
                                                    },
                                                    {}
                                                ),
                                            }
                                        ),
                                        Keyword(
                                            A2LTokenType::AXIS_PTS_REF, "AXIS_PTS_REF", "AxisPtsRef", false, false,
                                            {
                                                Parameter(PredefinedType::Ident, "AxisPoints"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::_BYTE_ORDER, "_BYTE_ORDER", "ByteOrder", false, false,
                                            {
                                                Parameter(
                                                    PredefinedType::Enum, "Byteorder",
                                                    { "_LITTLE_ENDIAN", "_BIG_ENDIAN", "MSB_LAST", "MSB_FIRST" }
                                                ),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::CURVE_AXIS_REF, "CURVE_AXIS_REF", "CurveAxisRef", false, false,
                                            {
                                                Parameter(PredefinedType::Ident, "CurveAxis"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::DEPOSIT, "DEPOSIT", "Deposit", false, false,
                                            {
                                                Parameter(PredefinedType::Enum, "Mode", { "ABSOLUTE", "DIFFERENCE" }),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::EXTENDED_LIMITS, "EXTENDED_LIMITS", "ExtendedLimits", false, false,
                                            {
                                                Parameter(PredefinedType::Float, "LowerLimit"),
                                                Parameter(PredefinedType::Float, "UpperLimit"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::FIX_AXIS_PAR, "FIX_AXIS_PAR", "FixAxisPar", false, false,
                                            {
                                                Parameter(PredefinedType::Int, "Offset"),
                                                Parameter(PredefinedType::Int, "Shift"),
                                                Parameter(PredefinedType::Uint, "Numberapo"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::FIX_AXIS_PAR_DIST, "FIX_AXIS_PAR_DIST", "FixAxisParDist", false, false,
                                            {
                                                Parameter(PredefinedType::Int, "Offset"),
                                                Parameter(PredefinedType::Int, "Distance"),
                                                Parameter(PredefinedType::Uint, "Numberapo"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::FIX_AXIS_PAR_LIST, "FIX_AXIS_PAR_LIST", "FixAxisParList", true, false,
                                            {
                                                Parameter(PredefinedType::Float, "AxisPts_Value", true),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::FORMAT, "FORMAT", "Format", false, false,
                                            {
                                                Parameter(PredefinedType::String, "FormatString"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::MAX_GRAD, "MAX_GRAD", "MaxGrad", false, false,
                                            {
                                                Parameter(PredefinedType::Float, "MaxGradient"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::MONOTONY, "MONOTONY", "Monotony", false, false,
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
                                            A2LTokenType::PHYS_UNIT, "PHYS_UNIT", "PhysUnit", false, false,
                                            {
                                                Parameter(PredefinedType::String, "Unit"),
                                            },
                                            {}
                                        ),
                                        Keyword(A2LTokenType::READ_ONLY, "READ_ONLY", "ReadOnly", false, false, {}, {}),
                                        Keyword(
                                            A2LTokenType::STEP_SIZE, "STEP_SIZE", "StepSize", false, false,
                                            {
                                                Parameter(PredefinedType::Float, "StepSize"),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::BIT_MASK, "BIT_MASK", "BitMask", false, false,
                                    {
                                        Parameter(PredefinedType::Ulong, "Mask"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::_BYTE_ORDER, "_BYTE_ORDER", "ByteOrder", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Byteorder",
                                            { "_LITTLE_ENDIAN", "_BIG_ENDIAN", "MSB_LAST", "MSB_FIRST" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::CALIBRATION_ACCESS, "CALIBRATION_ACCESS", "CalibrationAccess", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Type",
                                            { "CALIBRATION", "NO_CALIBRATION", "NOT_IN_MCD_SYSTEM", "OFFLINE_CALIBRATION" }
                                        ),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::DISCRETE, "DISCRETE", "Discrete", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::DISPLAY_IDENTIFIER, "DISPLAY_IDENTIFIER", "DisplayIdentifier", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "display_name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::EXTENDED_LIMITS, "EXTENDED_LIMITS", "ExtendedLimits", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "LowerLimit"),
                                        Parameter(PredefinedType::Float, "UpperLimit"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::FORMAT, "FORMAT", "Format", false, false,
                                    {
                                        Parameter(PredefinedType::String, "FormatString"),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::GUARD_RAILS, "GUARD_RAILS", "GuardRails", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::IF_DATA, "IF_DATA", "IfData", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::MAX_REFRESH, "MAX_REFRESH", "MaxRefresh", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "ScalingUnit"),
                                        Parameter(PredefinedType::Ulong, "Rate"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::NUMBER, "NUMBER", "Number", false, false,
                                    {
                                        Parameter(PredefinedType::Uint, "Number"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::PHYS_UNIT, "PHYS_UNIT", "PhysUnit", false, false,
                                    {
                                        Parameter(PredefinedType::String, "Unit"),
                                    },
                                    {}
                                ),
                                Keyword(A2LTokenType::READ_ONLY, "READ_ONLY", "ReadOnly", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::REF_MEMORY_SEGMENT, "REF_MEMORY_SEGMENT", "RefMemorySegment", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::STEP_SIZE, "STEP_SIZE", "StepSize", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "StepSize"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::VIRTUAL_CHARACTERISTIC, "VIRTUAL_CHARACTERISTIC", "VirtualCharacteristic", true,
                                    false,
                                    {
                                        Parameter(PredefinedType::String, "Formula"),
                                        Parameter(PredefinedType::Ident, "Characteristic", true),
                                    },
                                    {}
                                ),
                            }
                        ),
						Keyword(
							A2LTokenType::BLOB, "BLOB", "Blob", true, true,
							{
								Parameter(PredefinedType::Ident, "Name"),
								Parameter(PredefinedType::String, "LongIdentifier"),
								Parameter(PredefinedType::Ulong, "Address"),
                                Parameter(PredefinedType::Ulong, "Length"),
							},
							{
//#if 0
                                Keyword(
                                    A2LTokenType::CALIBRATION_ACCESS, "CALIBRATION_ACCESS", "CalibrationAccess", false, false,
                                    {
                                        Parameter(
                                            PredefinedType::Enum, "Type",
                                            { "CALIBRATION", "NO_CALIBRATION", "NOT_IN_MCD_SYSTEM", "OFFLINE_CALIBRATION" }
                                        ),
                                    },
                                    {}
                                ),
//#endif
							}
                        ),
						Keyword(
							A2LTokenType::TRANSFORMER, "TRANSFORMER", "Transformer", true, true,
							{
								Parameter(PredefinedType::Ident, "Name"),
								Parameter(PredefinedType::String, "Version"),
								Parameter(PredefinedType::String, "Dllname32"),
								Parameter(PredefinedType::String, "Dllname64"),
								Parameter(PredefinedType::Ulong, "Timeout"),
								Parameter(PredefinedType::Ident, "Trigger"),
								Parameter(PredefinedType::Ident, "Reverse"),
							},
							{
                                Keyword(
                                    A2LTokenType::TRANSFORMER_IN_OBJECTS, "TRANSFORMER_IN_OBJECTS", "TransformerInObjects", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::TRANSFORMER_OUT_OBJECTS, "TRANSFORMER_OUT_OBJECTS", "TransformerOutObjects", true, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),
                                    },
                                    {}
                                ),
							}
						),
                        Keyword(
                            A2LTokenType::TYPEDEF_MEASUREMENT, "TYPEDEF_MEASUREMENT", "TypedefMeasurement", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(
                                    PredefinedType::Enum, "Datatype",
                                    { "UBYTE", "SBYTE", "UWORD", "SWORD", "ULONG", "SLONG", "A_UINT64", "A_INT64", "FLOAT16_IEEE",
                                      "FLOAT32_IEEE", "FLOAT64_IEEE" }
                                ),
                                Parameter(PredefinedType::Ident, "Conversion"),
                                Parameter(PredefinedType::Uint, "Resolution"),
                                Parameter(PredefinedType::Float, "Accuracy"),
                                Parameter(PredefinedType::Float, "LowerLimit"),
                                Parameter(PredefinedType::Float, "UpperLimit"),
                            },
                            {}
                        ),
                        Keyword(
                            A2LTokenType::TYPEDEF_STRUCTURE, "TYPEDEF_STRUCTURE", "TypedefStructure", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(PredefinedType::Ulong, "Size"),
                            },
                            {
								Keyword(
									A2LTokenType::STRUCTURE_COMPONENT, "STRUCTURE_COMPONENT", "StructureComponent", true, true,
									{
										Parameter(PredefinedType::Ident, "Name"),
										Parameter(PredefinedType::Ident, "Type_Ref"),
										Parameter(PredefinedType::Ulong, "Offset"),
									},
									{
										Keyword(
											A2LTokenType::MATRIX_DIM, "MATRIX_DIM", "MatrixDim", false, false,
											{
												Parameter(PredefinedType::Uint, "Numbers", true),
											},
											{}
										),
										Keyword(
											A2LTokenType::NUMBER, "NUMBER", "Number", false, false,
											{
												Parameter(PredefinedType::Uint, "Number"),
											},
											{}
										),
										Keyword(
											A2LTokenType::SYMBOL_TYPE_LINK, "SYMBOL_TYPE_LINK", "SymbolTypeLink", false, false,
											{
												Parameter(PredefinedType::String, "Link"),
											},
											{}
										),
									}
								),
								Keyword(
									A2LTokenType::SYMBOL_TYPE_LINK, "SYMBOL_TYPE_LINK", "SymbolTypeLink", false, false,
									{
										Parameter(PredefinedType::String, "Link"),
									},
									{}
								),
                            }
                        ),
                        Keyword(
                            A2LTokenType::UNIT, "UNIT", "Unit", true, true,
                            {
                                Parameter(PredefinedType::Ident, "Name"),
                                Parameter(PredefinedType::String, "LongIdentifier"),
                                Parameter(PredefinedType::String, "Display"),
                                Parameter(PredefinedType::Enum, "Type", { "DERIVED", "EXTENDED_SI" }),
                            },
                            {
                                Keyword(
                                    A2LTokenType::SI_EXPONENTS, "SI_EXPONENTS", "SiExponents", false, false,
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
                                    A2LTokenType::REF_UNIT, "REF_UNIT", "RefUnit", false, false,
                                    {
                                        Parameter(PredefinedType::Ident, "Unit"),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::UNIT_CONVERSION, "UNIT_CONVERSION", "UnitConversion", false, false,
                                    {
                                        Parameter(PredefinedType::Float, "Gradient"),
                                        Parameter(PredefinedType::Float, "Offset"),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::USER_RIGHTS, "USER_RIGHTS", "UserRights", true, true,
                            {
                                Parameter(PredefinedType::Ident, "UserLevelId"),
                            },
                            {
                                Keyword(A2LTokenType::READ_ONLY, "READ_ONLY", "ReadOnly", false, false, {}, {}),
                                Keyword(
                                    A2LTokenType::REF_GROUP, "REF_GROUP", "RefGroup", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "Identifier", true),
                                    },
                                    {}
                                ),
                            }
                        ),
                        Keyword(
                            A2LTokenType::VARIANT_CODING, "VARIANT_CODING", "VariantCoding", true, false, {},
                            {
                                Keyword(
                                    A2LTokenType::VAR_CHARACTERISTIC, "VAR_CHARACTERISTIC", "VarCharacteristic", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                        Parameter(PredefinedType::Ident, "CriterionName", true),
                                    },
                                    {
                                        Keyword(
                                            A2LTokenType::VAR_ADDRESS, "VAR_ADDRESS", "VarAddress", true, false,
                                            {
                                                Parameter(PredefinedType::Ulong, "Address", true),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::VAR_CRITERION, "VAR_CRITERION", "VarCriterion", true, true,
                                    {
                                        Parameter(PredefinedType::Ident, "Name"),
                                        Parameter(PredefinedType::String, "LongIdentifier"),
                                        Parameter(PredefinedType::Ident, "Value", true),
                                    },
                                    {
                                        Keyword(
                                            A2LTokenType::VAR_MEASUREMENT, "VAR_MEASUREMENT", "VarMeasurement", false, false,
                                            {
                                                Parameter(PredefinedType::Ident, "Name"),
                                            },
                                            {}
                                        ),
                                        Keyword(
                                            A2LTokenType::VAR_SELECTION_CHARACTERISTIC, "VAR_SELECTION_CHARACTERISTIC",
                                            "VarSelectionCharacteristic", false, false,
                                            {
                                                Parameter(PredefinedType::Ident, "Name"),
                                            },
                                            {}
                                        ),
                                    }
                                ),
                                Keyword(
                                    A2LTokenType::VAR_FORBIDDEN_COMB, "VAR_FORBIDDEN_COMB", "VarForbiddenComb", true, true, {
									Parameter(
                                           // { PredefinedType::Uint, "NumberValuePairs"},
										{ { PredefinedType::Ident, "CriterionName" }, { PredefinedType::Ident, "CriterionValue" } }
									),

									}, {}
                                ),
                                Keyword(
                                    A2LTokenType::VAR_NAMING, "VAR_NAMING", "VarNaming", false, false,
                                    {
                                        Parameter(PredefinedType::Enum, "Tag", { "NUMERIC", "APLHA" }),
                                    },
                                    {}
                                ),
                                Keyword(
                                    A2LTokenType::VAR_SEPARATOR, "VAR_SEPARATOR", "VarSeparator", false, false,
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
