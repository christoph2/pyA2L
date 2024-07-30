
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
        // TYPE,
        BLOCK,
        BLOCK_INTERN,
        ENUMERATION,
        ENUMERATOR,
        MEMBER,
        PDT,
        REFERRER,
        ROOT,
        STRUCT,
        STRUCT_MEMBER,
        TAGGED_STRUCT,
        TAGGED_STRUCT_DEFINITION,
        TAGGED_STRUCT_MEMBER,
        TAGGED_UNION,
        TAGGED_UNION_MEMBER,
    };

    Node() = default;

    Node(const Node& other) = default;

    virtual ~Node() {
    }

    explicit Node(NodeType type) : m_node_type(type) {
    }

    NodeType type() const noexcept {
        return m_node_type;
    }

    virtual const Node* find(const std::string& value) const noexcept {
        return nullptr;
    }

    NodeType m_node_type;
};

struct Referrer : public Node {
    explicit Referrer(ReferrerType category, const std::string& identifier) :
        Node(Node::NodeType::REFERRER), m_category(category), m_identifier(identifier) {
    }

    Referrer(const Referrer& other) = default;

    ReferrerType m_category;
    std::string  m_identifier;
};

struct PDT : public Node {
    explicit PDT(AMLPredefinedType type) : Node(Node::NodeType::PDT), m_type(type) {
    }

    PDT(const PDT& other) = default;

    AMLPredefinedType m_type;
};

    #if 0
struct Enumerators : public Node {
    explicit Enumerators() : Node(Node::NodeType::ENUMERATORS) {
    }
};
    #endif

using enumerators_t = std::map<std::string, std::uint32_t>;

struct Enumerator : public Node {
    explicit Enumerator(const std::string& name, std::uint32_t value) :
        Node(Node::NodeType::ENUMERATOR), m_name(name), m_value(value) {
    }

    Enumerator() = default;

    std::string   m_name;
    std::uint32_t m_value;
};

struct Enumeration : public Node {
    Enumeration(const std::string& name, const enumerators_t& values) :
        Node(Node::NodeType::ENUMERATION), m_name(name), m_values(values) {
        for (const auto& [name, value] : values) {
            m_enumerators[name] = Enumerator(name, value);
        }
    }

    Enumeration(const Enumeration& other) {
        m_node_type = other.m_node_type;
        m_name      = other.m_name;
        m_values    = other.m_values;
    }

    const Node* find(const std::string& value) const noexcept override {
        auto res = m_enumerators.find(value);

        if (res != m_enumerators.end()) {
            // const auto& [key, value] = res;
            // return &value;
            return nullptr;
        } else {
            return nullptr;
        }
    }

    std::string                       m_name;
    enumerators_t                     m_values;
    std::map<std::string, Enumerator> m_enumerators;
};

struct TaggedStructDefinition : public Node {
    explicit TaggedStructDefinition(bool multiple, std::optional<std::shared_ptr<Node>> type) :
        Node(Node::NodeType::TAGGED_STRUCT_DEFINITION), m_multiple(multiple), m_type(type) {
    }

    TaggedStructDefinition(const TaggedStructDefinition& other) {
        m_node_type = other.m_node_type;
        m_multiple  = other.m_multiple;
        m_type      = other.m_type;
    }

    bool                                 m_multiple;
    std::optional<std::shared_ptr<Node>> m_type;
};

struct TaggedStructMember : public Node {
    explicit TaggedStructMember(bool multiple, const Node& definition) :
        Node(Node::NodeType::TAGGED_STRUCT_MEMBER), m_multiple(multiple), m_definition(definition) {
    }

    TaggedStructMember(const TaggedStructMember& other) {
        m_node_type  = other.m_node_type;
        m_multiple   = other.m_multiple;
        m_definition = other.m_definition;
    }

    bool m_multiple;
    Node m_definition;
};

struct TaggedStruct : public Node {
    TaggedStruct(const std::string& name, const std::vector< std::tuple<std::string, Node>> members) :
        Node(Node::NodeType::TAGGED_STRUCT), m_name(name), m_members(members) {
    }

    TaggedStruct(const TaggedStruct& other) {
        m_node_type = other.m_node_type;
        m_name      = other.m_name;
        std::copy(other.m_members.begin(), other.m_members.end(), std::back_inserter(m_members));
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

    Member& operator=(const Member& other) {
        m_node_type  = other.m_node_type;
        m_array_spec = other.m_array_spec;
        m_type       = other.m_type;

        return *this;
    }

    Member(const Member& other) {
        m_node_type  = other.m_node_type;
        m_array_spec = other.m_array_spec;
        m_type       = other.m_type;
    }

    Member(const std::vector<std::uint32_t>& array_spec, std::shared_ptr<Node> type) :
        Node(Node::NodeType::MEMBER), m_array_spec(array_spec), m_type(type) {
    }

    std::vector<std::uint32_t> m_array_spec;
    std::shared_ptr<Node>      m_type;
};

struct BlockIntern : public Node {
    BlockIntern() : Node(Node::NodeType::BLOCK_INTERN), m_type(nullptr) {
    }

    BlockIntern(const Member& member, std::shared_ptr<Node> type) :
        Node(Node::NodeType::BLOCK_INTERN), m_member(member), m_type(type) {
    }

    BlockIntern(const BlockIntern& other) {
        m_node_type = other.m_node_type;
        m_member    = other.m_member;
        m_type      = other.m_type;
    }

    void set_type(std::shared_ptr<Node> type) noexcept {
        m_type = std::move(type);
    }

    void set_member(Member&& member) noexcept {
        m_member = std::move(member);
    }

    Member                m_member;
    std::shared_ptr<Node> m_type;
};

struct Block : public Node {
    Block(const std::string& tag, bool multiple, BlockIntern&& member) :
        Node(Node::NodeType::BLOCK), m_tag(tag), m_multiple(multiple), m_member(std::move(member)) {
    }

    bool operator==(const std::string& tag) const noexcept {
        return m_tag == tag;  // && m_multiple == other.m_multiple && m_member == other.m_member;
    }

    std::string get_tag() const noexcept {
        return m_tag;
    }

    const Node* find(const std::string& tag) const noexcept override {
        if (m_tag == tag) {
            return this;
        } else {
            return nullptr;
        }
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

struct Root;

using NodeVariant = std::variant<
    Enumeration, Enumerator, Member, Struct, StructMember, TaggedUnion, TaggedUnionMember, TaggedStructDefinition,
    TaggedStructMember, TaggedStruct, Referrer, Block, BlockIntern, PDT, Root /*, Node*/>;

struct Root : public Node {
    Root(const std::vector<NodeVariant>& nodes) : Node(Node::NodeType::ROOT) {
        std::copy(nodes.begin(), nodes.end(), std::back_inserter(m_nodes));
    }

    Root(const Root& other) {
        m_node_type = other.m_node_type;
        std::copy(other.m_nodes.begin(), other.m_nodes.end(), std::back_inserter(m_nodes));
    }

    std::vector<NodeVariant>& nodes() noexcept {
        return m_nodes;
    }

    #if 0
    // find_node -- type
    const Node* find_block(const std::string& tag) {
        for (auto& node : m_nodes) {
            if ((node.type() == Node::NodeType::BLOCK)) {
                Block* block = dynamic_cast<Block*>(&node);
                if (block->get_tag() == tag) {
                    return block;
                }
            }
            //}
        }
        return nullptr;
    }
    #endif
    std::vector<NodeVariant> m_nodes;
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
            return TaggedStructDefinition(multiple, std::make_shared<Node>(load_type()));
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

    NodeVariant load_type() {
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
        return Member(array_spec, std::make_shared<NodeVariant>(load_type()));
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
            result.set_type(std::make_shared<Node>(load_type()));
        } else if (disc == "M") {
            result.set_member(load_member());
        }
        auto multiple = m_reader.from_binary<bool>();
        return Block(tag, multiple, std::move(result));
    }

    std::vector<NodeVariant> run() {
        auto                     decl_count = m_reader.from_binary<std::size_t>();
        std::vector<NodeVariant> result;
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

auto unmarshal(const std::stringstream& inbuf) -> Root;

#endif  // __UNMARSHAL_HPP
