
#if !defined(__TYPES_HPP)
    #define __TYPES_HPP

    #include <map>
    #include <optional>
    #include <set>
    #include <variant>


using string_opt_t = std::optional<std::string>;
using numeric_t    = std::variant<std::monostate, int64_t, long double>;

enum class AMLPredefinedTypeEnum : uint8_t {
    CHAR   = 0,
    INT    = 1,
    LONG   = 2,
    UCHAR  = 3,
    UINT   = 4,
    ULONG  = 5,
    INT64   = 6,
    UINT64 = 7,
    DOUBLE = 8,
    FLOAT  = 9,
    FLOAT16 = 10,
};

enum class ReferrerType : uint8_t {
    Enumeration      = 0,
    StructType       = 1,
    TaggedStructType = 2,
    TaggedUnionType  = 3,
};

enum class TypeType : uint8_t {
    PredefinedType   = 0,
    Enumeration      = 1,
    StructType       = 2,
    TaggedStructType = 3,
    TaggedUnionType  = 4,
    NullType         = 6,
};

const std::map<std::string, AMLPredefinedTypeEnum> PredefinedTypesMap {
    { "char",    AMLPredefinedTypeEnum::CHAR    },
    { "int",     AMLPredefinedTypeEnum::INT     },
    { "long",    AMLPredefinedTypeEnum::LONG    },
    { "uchar",   AMLPredefinedTypeEnum::UCHAR   },
    { "uint",    AMLPredefinedTypeEnum::UINT    },
    { "ulong",   AMLPredefinedTypeEnum::ULONG   },
	{ "int64",   AMLPredefinedTypeEnum::INT64   },
	{ "uint64",  AMLPredefinedTypeEnum::UINT64  },
    { "double",  AMLPredefinedTypeEnum::DOUBLE  },
    { "float",   AMLPredefinedTypeEnum::FLOAT   },
	{ "float16", AMLPredefinedTypeEnum::FLOAT16 },
};

const std::set<std::string> PredefinedTypesSet {
    "char", "int", "long", "uchar", "uint", "ulong", "int64", "uint64",  "double", "float",  "float16"
};

inline AMLPredefinedTypeEnum createPredefinedType(const std::string& name) {
    return PredefinedTypesMap.at(name);
}

#endif  // __TYPES_HPP
