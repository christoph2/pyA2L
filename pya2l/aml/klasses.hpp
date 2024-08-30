
#if !defined(__KLASSES_HPP)
    #define __KLASSES_HPP

    #include <bit>
    #include <cstdint>
    #include <map>
    #include <optional>
    #include <sstream>
    #include <variant>

    #include "types.hpp"

template<typename... Ts>
struct Overload : Ts... {
    using Ts::operator()...;
};

template<typename T>
inline std::string to_binary(const T& value) {
    std::string result;

    auto ptr = reinterpret_cast<const std::string::value_type*>(&value);
    for (std::size_t idx = 0; idx < sizeof(T); ++idx) {
        auto ch = ptr[idx];
        result.push_back(ch);
    }
    return result;
}

template<>
inline std::string to_binary<std::string>(const std::string& value) {
    std::string result;

    auto              ptr    = reinterpret_cast<const std::string::value_type*>(value.c_str());
    const std::size_t length = std::size(value);

    // We are using Pascal strings as serialization format.
    auto len_bin = to_binary(length);
    std::copy(len_bin.begin(), len_bin.end(), std::back_inserter(result));
    for (std::size_t idx = 0; idx < length; ++idx) {
        auto ch = ptr[idx];
        result.push_back(ch);
    }
    return result;
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
        return static_cast<long double>(std::get<std::int64_t>(value));
    } else if (std::holds_alternative<long double>(value)) {
        return std::get<long double>(value);
    }
    return {};
}

class Referrer {
   public:

    explicit Referrer(ReferrerType category, const std::string& identifier) : m_category(category), m_identifier(identifier) {
    }

    const ReferrerType& get_category() const noexcept {
        return m_category;
    }

    const std::string& get_identifier() const noexcept {
        return m_identifier;
    }

   private:

    ReferrerType m_category;
    std::string  m_identifier;
};

class Enumerator {
   public:

    explicit Enumerator(const std::string& tag, const std::optional<numeric_t>& value) : m_tag(tag), m_value(value) {
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

    const std::string& get_tag() const noexcept {
        return m_tag;
    }

    const std::optional<numeric_t>& get_value() const noexcept {
        return m_value;
    }

   private:

    std::string              m_tag;
    std::optional<numeric_t> m_value;
};

class Enumeration {
   public:

    explicit Enumeration(const std::string& name, const std::vector<Enumerator>& enumerators) : m_name(name) {
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
                    value = static_cast<std::int64_t>(std::get<long double>(value_cont));
                }
                m_enumerators[tag] = value;
                last_idx           = value + 1ULL;
            } else {
                m_enumerators[tag] = last_idx++;
            }
        }
    }

    const std::string& get_name() const noexcept {
        return m_name;
    }

    const std::map<std::string, std::uint64_t>& get_enumerators() const noexcept {
        return m_enumerators;
    }

   private:

    std::string                          m_name;
    std::map<std::string, std::uint64_t> m_enumerators{};
};

using EnumerationOrReferrer = std::variant<std::monostate, Referrer, Enumeration>;

class Type;

class BlockDefinition {
public:

    BlockDefinition() : m_tag(), m_type(nullptr) {
    }

    explicit BlockDefinition(const std::string& tag, Type* type) :
        m_tag(tag), m_type(type) {
    }

    const std::string& get_tag() const noexcept {
        return m_tag;
    }

    const Type* get_type() const noexcept {
        return m_type;
    }

private:

    std::string m_tag;
    Type* m_type;
};

class Member {
   public:

    Member() : m_block(std::nullopt), m_type(nullptr) {
    }

    explicit Member(std::optional<BlockDefinition> block, Type* type, const std::vector<std::uint64_t>& arr_spec) :
        m_block(block), m_type(type), m_arr_spec(arr_spec) {
    }

    const std::optional<BlockDefinition> get_block() const noexcept {
        return m_block;
    };

    const Type* get_type() const noexcept {
        return m_type;
    }

    const std::vector<std::uint64_t>& get_array_spec() const noexcept {
        return m_arr_spec;
    }

   private:

       std::optional<BlockDefinition> m_block;
    Type*                      m_type;
    std::vector<std::uint64_t> m_arr_spec{};
};

class StructMember {
   public:

    explicit StructMember(const Member& member) : m_member(member) {
    }

    const Member& get_member() const noexcept {
        return m_member;
    }

   private:

    Member m_member;
};

class Struct {
   public:

    explicit Struct(const std::string& name, const std::vector<StructMember>& members) : m_name(name), m_members(members) {
    }

    const std::string& get_name() const noexcept {
        return m_name;
    }

    const std::vector<StructMember>& get_members() const noexcept {
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

    explicit TaggedStructDefinition(const std::string& tag, const Member& member, bool multiple) :
        m_tag(tag), m_member(member), m_multiple(multiple) {
    }

    const std::string& get_tag() const noexcept {
        return m_tag;
    }

    const Member& get_member() const noexcept {
        return m_member;
    }

    bool get_multiple() const noexcept {
        return m_multiple;
    }

   private:

    std::string m_tag;
    Member      m_member;
    bool        m_multiple;
};

class TaggedStructMember {
   public:

    TaggedStructMember() = default;

    explicit TaggedStructMember(const TaggedStructDefinition& tsd, const BlockDefinition& block, bool multiple) :
        m_tsd(tsd), m_block(block), m_multiple(multiple) {
    }

    const TaggedStructDefinition& get_tagged_struct_def() const noexcept {
        return m_tsd;
    }

    const BlockDefinition& get_block() const noexcept {
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

    explicit TaggedStruct(const std::string& name, const std::vector<TaggedStructMember>& members) :
        m_name(name), m_members(members) {
        for (const auto& elem : m_members) {
            const auto  block = elem.get_block();
            const auto  tsd   = elem.get_tagged_struct_def();
            std::string tag{};

            if (block.get_type()) {
                tag = block.get_tag();
            } else {
                tag = tsd.get_tag();
            }
            if (tag != "") {
                m_tags[tag] = elem;
            }
        }
    }

    const std::string& get_name() const noexcept {
        return m_name;
    }

    const std::vector<TaggedStructMember>& get_members() const noexcept {
        return m_members;
    }

    const std::map<std::string, TaggedStructMember>& get_tags() const noexcept {
        return m_tags;
    }

   private:

    std::string                               m_name;
    std::vector<TaggedStructMember>           m_members;
    std::map<std::string, TaggedStructMember> m_tags;
};

using TaggedStructOrReferrer = std::variant<std::monostate, TaggedStruct, Referrer>;

class TaggedUnionMember {
   public:

    TaggedUnionMember() = default;

    explicit TaggedUnionMember(const std::string& tag, const Member& member, const BlockDefinition& block) :
        m_tag(tag), m_member(member), m_block(block) {
    }

    const std::string& get_tag() const noexcept {
        return m_tag;
    }

    const Member& get_member() const noexcept {
        return m_member;
    }

    const BlockDefinition& get_block() const noexcept {
        return m_block;
    }

   private:

    std::string     m_tag;
    Member          m_member;
    BlockDefinition m_block;
};

class TaggedUnion {
   public:

    explicit TaggedUnion(const std::string& name, const std::vector<TaggedUnionMember>& members) :
        m_name(name), m_members(members) {
        for (const auto& elem : members) {
            const auto mem   = elem.get_member();
            const auto block = elem.get_block();
            if (block.get_type()) {
                const auto tag = block.get_tag();
                m_tags[tag]    = elem;
            }
            if (mem.get_type()) {
                const auto tag = elem.get_tag();
                m_tags[tag]    = elem;
            }
        }
    }

    const std::string& get_name() const noexcept {
        return m_name;
    }

    const std::vector<TaggedUnionMember>& get_members() const noexcept {
        return m_members;
    }

    const std::map<std::string, TaggedUnionMember>& get_tags() const noexcept {
        return m_tags;
    }

   private:

    std::string                              m_name;
    std::vector<TaggedUnionMember>           m_members;
    std::map<std::string, TaggedUnionMember> m_tags;
};

using TaggedUnionOrReferrer = std::variant<std::monostate, TaggedUnion, Referrer>;

using TypeVariant = std::variant<
    std::monostate, AMLPredefinedType, EnumerationOrReferrer, StructOrReferrer, TaggedStructOrReferrer, TaggedUnionOrReferrer>;

class Type {
   public:

    Type(const AMLPredefinedType& predef_type) :
        m_type(predef_type), m_disc(TypeType::PredefinedType) {
    }

    Type(const EnumerationOrReferrer& en) : m_type(en), m_disc(TypeType::Enumeration) {
    }

    Type(const StructOrReferrer& st) : m_type(st), m_disc(TypeType::StructType) {
    }

    Type(const TaggedStructOrReferrer& st) : m_type(st), m_disc(TypeType::TaggedStructType) {
    }

    Type(const TaggedUnionOrReferrer& tu) : m_type(tu), m_disc(TypeType::TaggedUnionType) {
    }

    const TypeVariant& get_type() const noexcept {
        return m_type;
    }

    TypeType get_discriminator() const noexcept {
        return m_disc;
    }

   private:

    TypeVariant m_type;
    TypeType    m_disc;
};

class TypeDefinition {
   public:

    TypeDefinition() : m_tp(nullptr) {
    }

    explicit TypeDefinition(Type* tp) : m_tp(tp) {
    }

    Type* get_type() const noexcept {
        return m_tp;
    }

   private:

    Type* m_tp;
};

class Declaration {
   public:

    explicit Declaration(TypeDefinition td, const BlockDefinition& block) : m_td(td), m_block(block) {
    }

    const TypeDefinition& get_type() const noexcept {
        return m_td;
    }

    const BlockDefinition& get_block() const noexcept {
        return m_block;
    }

   private:

    TypeDefinition  m_td;
    BlockDefinition m_block;
};

class AmlFile {
   public:

    explicit AmlFile(const std::vector<Declaration>& decls) : m_decls(decls) {
    }

    const std::vector<Declaration>& get_decls() const noexcept {
        return m_decls;
    }

   private:

    std::vector<Declaration> m_decls;
};

#endif  // __KLASSES_HPP
