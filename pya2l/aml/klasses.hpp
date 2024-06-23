
#if !defined(__KLASSES_HPP)
    #define __KLASSES_HPP

    #include <bit>
    #include <cstdint>
    #include <map>
    #include <optional>
    #include <sstream>
    #include <variant>

template<typename... Ts>
struct Overload : Ts... {
    using Ts::operator()...;
};

using string_opt_t = std::optional<std::string>;
using numeric_t    = std::variant<std::monostate, std::uint64_t, long double>;

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
    TaggedUnion      = 3,
};

enum class TypeType : std::uint8_t {
    PredefinedType = 0,
    Enumeration = 1,
    StructType = 2,
    TaggedStructType = 3,
    TaggedUnion = 4,
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


inline std::string get_string(auto var) {
	std::string result{};

    if (var) {
       auto opt_str = std::any_cast<string_opt_t>(visit(var));
       if (opt_str) {
          result = *opt_str;
       }

    }

	return result;
}

inline long double as_double(const numeric_t& value) {
    if (std::holds_alternative<std::uint64_t>(value)) {
        return std::bit_cast<long double>(std::get<std::uint64_t>(value));
    } else if (std::holds_alternative<long double>(value)) {
        return std::get<long double>(value);
    }
    return {};
}

class Referrer {
   public:

    Referrer(ReferrerType category, const std::string& identifier) : m_category(category), m_identifier(identifier) {
    }

   private:

    ReferrerType m_category;
    std::string  m_identifier;
};

class Enumerator {
   public:

    Enumerator(const std::string& tag, const std::optional<numeric_t>& value) : m_tag(tag), m_value(value) {
    }

    Enumerator()                  = delete;
    Enumerator(const Enumerator&) = default;
    Enumerator(Enumerator&&)      = default;

    std::string to_string() const noexcept {
        std::stringstream ss;

        ss << "Enumerator(";
        ss << "tag=\"" << m_tag << "\" value=";
        if (m_value) {
            // ss << as_double(*m_value);
        } else {
            ss << "(null)";
        }
        ss << ")";

        return ss.str();
    }

    std::string get_tag() const noexcept {
        return m_tag;
    }

    std::optional<numeric_t> get_value() const noexcept {
        return m_value;
    }

   private:

    std::string              m_tag;
    std::optional<numeric_t> m_value;
};

class Enumeration {
   public:

    Enumeration(const std::string& name, const std::vector<Enumerator>& enumerators) : m_name(name) {
        std::uint64_t last_idx = 0ULL;
        std::uint64_t value    = 0ULL;
        for (const auto& en : enumerators) {
            auto tag       = en.get_tag();
            auto value_opt = en.get_value();
            if (value_opt) {
                auto value_cont = *value_opt;

                if (std::holds_alternative<std::uint64_t>(value_cont)) {
                    value = std::get<std::uint64_t>(value_cont);
                } else if (std::holds_alternative<long double>(value_cont)) {
                    value = std::bit_cast<std::uint64_t>(std::get<long double>(value_cont));
                }
                m_enumerators[tag] = value;
                last_idx           = value + 1ULL;
            } else {
                m_enumerators[tag] = last_idx++;
            }
        }
    }

   private:

    std::string                          m_name;
    std::map<std::string, std::uint64_t> m_enumerators{};
};

using EnumerationOrReferrer = std::variant<std::monostate, Referrer, Enumeration>;

class Type;

class Member {
public:
    Member() : m_type(nullptr) {}
    Member(Type * type, const std::vector<std::uint64_t>& arr_spec) : m_type(type), m_arr_spec(arr_spec) {}
private:
    Type* m_type;
    std::vector<std::uint64_t> m_arr_spec{};
};


class StructMember {
public:
    StructMember() {}
private:
};

class Struct {
public:
    Struct(const std::string& name, const std::vector<StructMember>& members) : m_name(name), m_members(members) {}
private:
    std::string                          m_name;
    std::vector<StructMember> m_members;
};

using StructOrReferrer = std::variant<std::monostate, Struct, Referrer>;

class TaggedStructMember {
public:
    TaggedStructMember() {}
private:
};

class TaggedStruct {
public:
    TaggedStruct() {}
private:
};

using TaggedStructOrReferrer = std::variant<std::monostate, TaggedStruct, Referrer>;


class BlockDefinition {
public:
    BlockDefinition() {}
private:
};

class TaggedUnionMember {
   public:

    TaggedUnionMember(const std::string& tag, const Member& member, const BlockDefinition& block) :
        m_tag(tag), m_member(member), m_block(block) {
    }

   private:

    std::string     m_tag;
    Member          m_member;
    BlockDefinition m_block;
};

class TaggedUnion {
public:
    TaggedUnion() {}
private:
};

using TaggedUnionOrReferrer = std::variant<std::monostate, TaggedUnion, Referrer>;


using TypeVariant = std::variant<std::monostate, std::string, Enumeration, Struct, TaggedStruct, TaggedUnion>;

class Type {
   public:

	Type(const std::string& predef_type_name) : m_type(predef_type_name), m_disc(TypeType::PredefinedType) {
    }

	Type(const Enumeration& en) : m_type(en), m_disc(TypeType::Enumeration) {
    }

	Type(const Struct& st) : m_type(st), m_disc(TypeType::StructType) {
    }

	Type(const TaggedStruct& st) : m_type(st), m_disc(TypeType::TaggedStructType) {
    }

	Type(const TaggedUnion& tu) : m_type(tu), m_disc(TypeType::TaggedUnion) {
    }

   private:
	TypeVariant m_type;
    TypeType m_disc;
};

#endif  // __KLASSES_HPP
