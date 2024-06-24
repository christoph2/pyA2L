
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
    if (std::holds_alternative<std::int64_t>(value)) {
        return std::bit_cast<long double>(std::get<std::int64_t>(value));
    } else if (std::holds_alternative<long double>(value)) {
        return std::get<long double>(value);
    }
    return {};
}

class Referrer {
   public:

    Referrer(ReferrerType category, const std::string& identifier) : m_category(category), m_identifier(identifier) {
    }

    ReferrerType get_category() const noexcept {
        return m_category;
    }

    std::string get_identifier() const noexcept {
        return m_identifier;
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
        std::int64_t  value    = 0ULL;
        for (const auto& en : enumerators) {
            auto tag       = en.get_tag();
            auto value_opt = en.get_value();
            if (value_opt) {
                auto value_cont = *value_opt;

                if (std::holds_alternative<std::int64_t>(value_cont)) {
                    value = std::get<std::int64_t>(value_cont);
                } else if (std::holds_alternative<long double>(value_cont)) {
                    value = std::bit_cast<std::int64_t>(std::get<long double>(value_cont));
                }
                m_enumerators[tag] = value;
                last_idx           = value + 1ULL;
            } else {
                m_enumerators[tag] = last_idx++;
            }
        }
    }

    std::string get_name() const noexcept {
        return m_name;
    }

    std::map<std::string, std::uint64_t> get_enumerators() const noexcept {
        return m_enumerators;
    }

   private:

    std::string                          m_name;
    std::map<std::string, std::uint64_t> m_enumerators{};
};

using EnumerationOrReferrer = std::variant<std::monostate, Referrer, Enumeration>;

class Type;

class Member {
   public:

    Member() : m_type(nullptr) {
    }

    Member(Type* type, const std::vector<std::uint64_t>& arr_spec) : m_type(type), m_arr_spec(arr_spec) {
    }

    Type* get_type() const noexcept {
        return m_type;
    }

    std::vector<std::uint64_t> get_array_spec() const noexcept {
        return m_arr_spec;
    }

   private:

    Type*                      m_type;
    std::vector<std::uint64_t> m_arr_spec{};
};

class BlockDefinition {
   public:

    BlockDefinition() : m_tag(), m_type(nullptr), m_member(), m_multiple(false) {
    }

    BlockDefinition(const std::string& tag, Type* type, const Member& member, bool multiple) :
        m_tag(tag), m_type(type), m_member(member), m_multiple(multiple) {
    }

    std::string get_tag() const noexcept {
        return m_tag;
    }

    Type* get_type() const noexcept {
        return m_type;
    }

    Member get_member() const noexcept {
        return m_member;
    }

    bool get_multiple() const noexcept {
        return m_multiple;
    }

   private:

    std::string m_tag;
    Type*       m_type;
    Member      m_member;
    bool        m_multiple;
};

class StructMember {
   public:

    StructMember(const Member& member, bool multiple) : m_member(member), m_multiple(multiple) {
    }

    Member get_member() const noexcept {
        return m_member;
    }

    bool get_multiple() const noexcept {
        return m_multiple;
    }

   private:

    Member m_member;
    bool   m_multiple;
};

class Struct {
   public:

    Struct(const std::string& name, const std::vector<StructMember>& members) : m_name(name), m_members(members) {
    }

    std::string get_name() const noexcept {
        return m_name;
    }

    std::vector<StructMember> get_members() const noexcept {
        return m_members;
    }

   private:

    std::string               m_name;
    std::vector<StructMember> m_members;
};

using StructOrReferrer = std::variant<std::monostate, Struct, Referrer>;

class TaggedStructDefinition {
   public:

    TaggedStructDefinition() = default;

    TaggedStructDefinition(const std::string& tag, const Member& member) : m_tag(tag), m_member(member) {
    }

    std::string get_tag() const noexcept {
        return m_tag;
    }

    Member get_member() const noexcept {
        return m_member;
    }

   private:

    std::string m_tag;
    Member      m_member;
};

class TaggedStructMember {
   public:

    // taggedstruct_definition, block_definition, multiple
    TaggedStructMember(const TaggedStructDefinition& tsd, const BlockDefinition& block, bool multiple) :
        m_tsd(tsd), m_block(block), m_multiple(multiple) {
    }

    TaggedStructDefinition get_tagged_struct_def() const noexcept {
        return m_tsd;
    }

    BlockDefinition get_block() const noexcept {
        return m_block;
    }

    bool get_multiple() const noexcept {
        return m_multiple;
    }

   private:

    TaggedStructDefinition m_tsd;
    BlockDefinition        m_block;
    bool                   m_multiple;
};

class TaggedStruct {
   public:

    TaggedStruct(const std::string& name, const std::vector<TaggedStructMember>& members) : m_name(name), m_members(members) {
    }

    std::string get_name() const noexcept {
        return m_name;
    }

    std::vector<TaggedStructMember> get_members() const noexcept {
        return m_members;
    }

   private:

    std::string                     m_name;
    std::vector<TaggedStructMember> m_members;
};

using TaggedStructOrReferrer = std::variant<std::monostate, TaggedStruct, Referrer>;

class TaggedUnionMember {
   public:

    TaggedUnionMember(const std::string& tag, const Member& member, const BlockDefinition& block) :
        m_tag(tag), m_member(member), m_block(block) {
    }

    std::string get_tag() const noexcept {
        return m_tag;
    }

    Member get_member() const noexcept {
        return m_member;
    }

    BlockDefinition get_block() const noexcept {
        return m_block;
    }

   private:

    std::string     m_tag;
    Member          m_member;
    BlockDefinition m_block;
};

class TaggedUnion {
   public:

    TaggedUnion(const std::string& name, const std::vector<TaggedUnionMember>& members) : m_name(name), m_members(members) {
        for (const auto& mem : members) {
            auto tag   = mem.get_tag();
            auto elem  = mem.get_member();
            auto block = mem.get_block();
            auto mtype = elem.get_type();
            auto btype = block.get_type();
            if (btype == nullptr) {
                auto bb = 0;
            }
        }
    }

    std::string get_name() const noexcept {
        return m_name;
    }

    std::vector<TaggedUnionMember> get_members() const noexcept {
        return m_members;
    }

   private:

    std::string                    m_name;
    std::vector<TaggedUnionMember> m_members;
};

using TaggedUnionOrReferrer = std::variant<std::monostate, TaggedUnion, Referrer>;

using TypeVariant = std::variant<
    std::monostate, std::string, EnumerationOrReferrer, StructOrReferrer, TaggedStructOrReferrer, TaggedUnionOrReferrer>;

class Type {
   public:

    Type(const std::string& predef_type_name) : m_type(predef_type_name), m_disc(TypeType::PredefinedType) {
    }

    Type(const EnumerationOrReferrer& en) : m_type(en), m_disc(TypeType::Enumeration) {
    }

    Type(const StructOrReferrer& st) : m_type(st), m_disc(TypeType::StructType) {
    }

    Type(const TaggedStructOrReferrer& st) : m_type(st), m_disc(TypeType::TaggedStructType) {
    }

    Type(const TaggedUnionOrReferrer& tu) : m_type(tu), m_disc(TypeType::TaggedUnionType) {
    }

    TypeVariant get_type() const noexcept {
        return m_type;
    }

    TypeType get_discriminator() const noexcept {
        return m_disc;
    }

   private:

    TypeVariant m_type;
    TypeType    m_disc;
};

class Declaration {
   public:

    Declaration(Type* tp, const BlockDefinition& block) : m_tp(tp), m_block(block) {
    }

    Type* get_type() const noexcept {
        return m_tp;
    }

    BlockDefinition get_block() const noexcept {
        return m_block;
    }

   private:

    Type*           m_tp;
    BlockDefinition m_block;
};

#endif  // __KLASSES_HPP
