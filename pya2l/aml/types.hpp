
#if !defined(__TYPES_HPP)
    #define __TYPES_HPP

    #include <map>
    #include <optional>
    #include <variant>

using string_opt_t = std::optional<std::string>;
using numeric_t    = std::variant<std::monostate, std::int64_t, long double>;

enum class AMLPredefinedType : std::uint8_t {
    CHAR   = 0,
    INT    = 1,
    LONG   = 2,
    UCHAR  = 3,
    UINT   = 4,
    ULONG  = 5,
    DOUBLE = 6,
    FLOAT  = 7,
};

enum class ReferrerType : std::uint8_t {
    Enumeration      = 0,
    StructType       = 1,
    TaggedStructType = 2,
    TaggedUnionType  = 3,
};

enum class TypeType : std::uint8_t {
    PredefinedType   = 0,
    Enumeration      = 1,
    StructType       = 2,
    TaggedStructType = 3,
    TaggedUnionType  = 4,
};

const std::map<std::string, AMLPredefinedType> PredefinedTypesMap{
    { "char",   AMLPredefinedType::CHAR   },
    { "int",    AMLPredefinedType::INT    },
    { "long",   AMLPredefinedType::LONG   },
    { "uchar",  AMLPredefinedType::UCHAR  },
    { "uint",   AMLPredefinedType::UINT   },
    { "ulong",  AMLPredefinedType::ULONG  },
    { "double", AMLPredefinedType::DOUBLE },
    { "float",  AMLPredefinedType::FLOAT  },
};

inline AMLPredefinedType createPredefinedType(const std::string& name) {
    return PredefinedTypesMap.at(name);
}

#endif  // __TYPES_HPP
