
#if !defined(__UNMARSHAL_HPP)
    #define __UNMARSHAL_HPP

    #include <any>
    #include <cassert>
    #include <iostream>
    #include <memory>
    #include <optional>
    #include <sstream>
    #include <vector>

    #include "types.hpp"

class Reader {
   public:

    Reader() = delete;

    explicit Reader(const std::stringstream& inbuf) : m_buf(inbuf.str()) {
    }

    template<typename T>
    inline T from_binary() {
        auto tmp = *reinterpret_cast<const T*>(&m_buf[m_offset]);
        m_offset += sizeof(T);
        return tmp;
    }

    inline std::string from_binary_str() {
        auto        length = from_binary<std::size_t>();
        std::string result;
        auto        start = m_buf.cbegin() + m_offset;

        std::copy(start, start + length, std::back_inserter(result));
        m_offset += length;
        return result;
    }

   private:

    std::string m_buf;
    std::size_t m_offset = 0;
};

struct Node {
    enum class NodeType {
        TYPE,
        BLOCK,
        BLOCK_INTERN,
        MEMBER,
        STRUCT,
        STRUCT_MEMBER,
        TAGGED_STRUCT,
        TAGGED_STRUCT_MEMBER,
        TAGGED_STRUCT_DEFINITION,
        TAGGED_UNION,
        TAGGED_UNION_MEMBER,
        ENUMERATION,
        ENUMERATORS,
        REFERRER,
        PDT,
    };

    Node() = default;

    virtual ~Node() {
    }

    explicit Node(NodeType type) : m_node_type(type) {
    }

    NodeType type() const noexcept {
        return m_node_type;
    }

    NodeType m_node_type;
};

struct Referrer : public Node {
    explicit Referrer(ReferrerType category, const std::string& identifier) :
        Node(Node::NodeType::REFERRER), m_category(category), m_identifier(identifier) {
    }

    ReferrerType m_category;
    std::string  m_identifier;
};

struct PDT : public Node {
    explicit PDT(AMLPredefinedType type) : Node(Node::NodeType::PDT), m_type(type) {
    }

    AMLPredefinedType m_type;
};

struct Enumerators : public Node {
    explicit Enumerators() : Node(Node::NodeType::ENUMERATORS) {
    }
};

using enumerators_t = std::map<std::string, std::uint32_t>;

struct Enumeration : public Node {
    Enumeration(const std::string& name, const enumerators_t& values) :
        Node(Node::NodeType::ENUMERATION), m_name(name), m_values(values) {
    }

    std::string   m_name;
    enumerators_t m_values;
};

struct TaggedStructDefinition : public Node {
    explicit TaggedStructDefinition(bool multiple, std::optional<std::unique_ptr<Node>>&& type) :
        Node(Node::NodeType::TAGGED_STRUCT_DEFINITION), m_multiple(multiple), m_type(std::move(type)) {
    }

    bool                                 m_multiple;
    std::optional<std::unique_ptr<Node>> m_type;
};

struct TaggedStructMember : public Node {
    explicit TaggedStructMember(bool multiple, Node&& definition) :
        Node(Node::NodeType::TAGGED_STRUCT_MEMBER), m_multiple(multiple), m_definition(std::move(definition)) {
    }

    bool m_multiple;
    Node m_definition;
};

struct TaggedStruct : public Node {
    TaggedStruct(const std::string& name, std::vector< std::tuple<std::string, Node>>&& members) :
        Node(Node::NodeType::TAGGED_STRUCT), m_name(name), m_members(std::move(members)) {
    }

    std::string                                m_name;
    std::vector<std::tuple<std::string, Node>> m_members;
};

struct Member : public Node {
    Member() : Node(Node::NodeType::MEMBER), m_array_spec(), m_type(nullptr) {
    }

    Member(Member&& other) {
        m_node_type = other.m_node_type;
        std::swap(m_array_spec, other.m_array_spec);
        std::swap(m_type, other.m_type);
    }

    Member& operator=(Member&& other) {
        m_node_type = other.m_node_type;
        std::swap(m_array_spec, other.m_array_spec);
        std::swap(m_type, other.m_type);

        return *this;
    }

    Member(const std::vector<std::uint32_t>& array_spec, std::unique_ptr<Node> type) :
        Node(Node::NodeType::MEMBER), m_array_spec(array_spec), m_type(std::move(type)) {
    }

    std::vector<std::uint32_t> m_array_spec;
    std::unique_ptr<Node>      m_type;
};

struct BlockIntern : public Node {
    BlockIntern() : Node(Node::NodeType::BLOCK_INTERN), m_type(nullptr) {
    }

    BlockIntern(Member&& member, std::unique_ptr<Node> type) :
        Node(Node::NodeType::BLOCK_INTERN), m_member(std::move(member)), m_type(std::move(type)) {
    }

    void set_type(std::unique_ptr<Node> type) noexcept {
        m_type = std::move(type);
    }

    void set_member(Member&& member) noexcept {
        m_member = std::move(member);
    }

    Member                m_member;
    std::unique_ptr<Node> m_type;
};

struct Block : public Node {
    Block(const std::string& tag, bool multiple, BlockIntern&& member) :
        Node(Node::NodeType::BLOCK), m_tag(tag), m_multiple(multiple), m_member(std::move(member)) {
    }

    std::string m_tag;
    bool        m_multiple;
    BlockIntern m_member;
};

struct StructMember : public Node {
    StructMember(bool multiple, Member&& member) :
        Node(Node::NodeType::STRUCT_MEMBER), m_multiple(multiple), m_member(std::move(member)) {
    }

    bool   m_multiple;
    Member m_member;
};

struct Struct : public Node {
    Struct(const std::string& name, std::vector<StructMember>&& members) :
        Node(Node::NodeType::STRUCT), m_name(name), m_members(std::move(members)) {
    }

    std::string               m_name;
    std::vector<StructMember> m_members;
};

struct TaggedUnionMember : public Node {
    TaggedUnionMember(const std::string& tag, Node&& member) :
        Node(Node::NodeType::TAGGED_UNION_MEMBER), m_tag(tag), m_member(std::move(member)) {
    }

    std::string m_tag;
    Node        m_member;
};

struct TaggedUnion : public Node {
    TaggedUnion(const std::string& name, std::vector<TaggedUnionMember>&& members) :
        Node(Node::NodeType::TAGGED_UNION), m_name(name), m_members(std::move(members)) {
    }

    std::string                    m_name;
    std::vector<TaggedUnionMember> m_members;
};

class Unmarshaller {
   public:

    Unmarshaller(const std::stringstream& inbuf) : m_reader(inbuf) {
    }

    PDT load_pdt() {
        return PDT{ static_cast<AMLPredefinedType>(m_reader.from_binary<std::uint8_t>()) };
    }

    Referrer load_referrrer() {
        const auto  cat        = ReferrerType(m_reader.from_binary<std::uint8_t>());
        const auto& identifier = m_reader.from_binary_str();
        return Referrer{ cat, identifier };
    }

    Node load_enum() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "E") {
            auto          name             = m_reader.from_binary_str();
            auto          enumerator_count = m_reader.from_binary<std::size_t>();
            enumerators_t enumerators;

            for (auto idx = 0UL; idx < enumerator_count; ++idx) {
                auto tag   = m_reader.from_binary_str();
                auto value = m_reader.from_binary< std::uint32_t>();
                enumerators.emplace(tag, value);
            }
            return Enumeration{ name, enumerators };
        } else if (disc == "R") {
            return load_referrrer();
        }
    }

    TaggedStructDefinition load_tagged_struct_definition() {
        const auto multiple  = m_reader.from_binary<bool>();
        auto       available = m_reader.from_binary< bool >();

        if (available) {
            return TaggedStructDefinition(multiple, std::make_unique<Node>(load_type()));
        }
        // else TAG only.
        return TaggedStructDefinition(multiple, std::nullopt);
    }

    Node load_tagged_struct_member() {
        const auto  multiple = m_reader.from_binary<bool>();
        const auto& dt       = m_reader.from_binary_str();

        if (dt == "T") {
            return TaggedStructMember(multiple, std::move(load_tagged_struct_definition()));
        } else if (dt == "B") {
            return TaggedStructMember(multiple, std::move(load_block()));
        }
    }

    Node load_tagged_struct() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "S") {
            auto                                       name       = m_reader.from_binary_str();
            auto                                       tags_count = m_reader.from_binary<std::size_t>();
            std::vector<std::tuple<std::string, Node>> members;
            for (auto idx = 0UL; idx < tags_count; ++idx) {
                const auto& tag = m_reader.from_binary_str();
                members.emplace_back(tag, std::move(load_tagged_struct_member()));
            }
            return TaggedStruct{ name, std::move(members) };
        } else if (disc == "R") {
            return load_referrrer();
        }
    }

    Node load_tagged_union() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "U") {
            auto                           name       = m_reader.from_binary_str();
            auto                           tags_count = m_reader.from_binary<std::size_t>();
            std::vector<TaggedUnionMember> members;

            for (auto idx = 0UL; idx < tags_count; ++idx) {
                auto        tag = m_reader.from_binary_str();
                const auto& dt  = m_reader.from_binary_str();

                if (dt == "M") {
                    members.emplace_back(tag, std::move(load_member()));
                } else if (dt == "B") {
                    members.emplace_back(tag, std::move(load_block()));
                }
            }
            return TaggedUnion(name, std::move(members));

        } else if (disc == "R") {
            return load_referrrer();
        }
    }

    Node load_type() {
        const auto& tag = m_reader.from_binary_str();
        // "PD" - AMLPredefinedType
        // "TS" - TaggedStruct
        // "TU" - TaggedUnion
        // "ST" - Struct
        // "EN" - Enumeration
        const auto& disc = m_reader.from_binary_str();
        Node        result;

        if (disc == "PD") {
            return load_pdt();
        } else if (disc == "TS") {
            return load_tagged_struct();
        } else if (disc == "TU") {
            return load_tagged_union();
        } else if (disc == "ST") {
            return load_struct();
        } else if (disc == "EN") {
            return load_enum();
        } else {
            assert(true == false);
        }
        return result;
    }

    Member load_member() {
        auto                       arr_count = m_reader.from_binary<std::size_t>();
        std::vector<std::uint32_t> array_spec;
        for (auto idx = 0UL; idx < arr_count; ++idx) {
            array_spec.push_back(m_reader.from_binary<std::uint32_t>());
        }
        return Member(array_spec, std::make_unique<Node>(load_type()));
    }

    Node load_struct() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "S") {
            auto                      name         = m_reader.from_binary_str();
            auto                      member_count = m_reader.from_binary<std::size_t>();
            std::vector<StructMember> members;

            for (auto idx = 0UL; idx < member_count; ++idx) {
                auto member = load_member();
                auto mult   = m_reader.from_binary<bool>();
                members.emplace_back(mult, std::move(member));
            }
            return Struct(name, std::move(members));
        } else if (disc == "R") {
            return load_referrrer();
        }
    }

    Node load_block() {
        const auto& tag  = m_reader.from_binary_str();
        const auto& disc = m_reader.from_binary_str();

        BlockIntern result{};
        if (disc == "T") {
            result.set_type(std::make_unique<Node>(load_type()));
        } else if (disc == "M") {
            result.set_member(load_member());
        }
        auto multiple = m_reader.from_binary<bool>();
        return Block(tag, multiple, std::move(result));
    }

    std::vector<Node> run() {
        auto              decl_count = m_reader.from_binary<std::size_t>();
        std::vector<Node> result;
        std::vector<Node> nodes;
        for (auto idx = 0UL; idx < decl_count; ++idx) {
            const auto& disc1 = m_reader.from_binary_str();

            if (disc1 == "TY") {
                result.emplace_back(load_type());
            } else if (disc1 == "BL") {
                auto bt = m_reader.from_binary_str();
                result.emplace_back(load_block());
            }
        }
        return result;
    }

   private:

    Reader m_reader;
};

auto unmarshal(const std::stringstream& inbuf) -> std::vector<Node>;

#endif  // __UNMARSHAL_HPP
