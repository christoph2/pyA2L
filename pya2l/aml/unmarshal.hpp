
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

class Node {
public:

    enum class NodeType : std::uint8_t {
        TERMINAL,
        MAP,
        AGGR,
        NONE,
    };

    enum class AmlType : std::uint8_t {
        NONE,
        TYPE,
        TERMINAL,
        BLOCK,
        BLOCK_INTERN,
        ENUMERATION,
        ENUMERATOR,
        ENUMERATORS,
        MEMBER,
        MEMBERS,
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

    using terminal_t = std::variant<std::monostate, long long, float, std::string>;
    using list_t = std::vector<Node>;
    using map_t = std::map<std::string, Node>;

    explicit Node() : m_aml_type(AmlType::NONE), m_node_type(NodeType::NONE) {}

    explicit Node(AmlType aml_type, const terminal_t value) : m_aml_type(aml_type), m_node_type(NodeType::TERMINAL),
        m_value(value) {

    }

    explicit Node(AmlType aml_type, const list_t& list) : m_aml_type(aml_type), m_node_type(NodeType::AGGR), m_list(list) {}
    explicit Node(AmlType aml_type, const map_t& map) : m_aml_type(aml_type), m_node_type(NodeType::MAP), m_map(map) {}

private:
    AmlType m_aml_type;
    NodeType m_node_type;
    terminal_t m_value{};
    list_t m_list{};
    map_t m_map{};
};

inline Node make_pdt(AMLPredefinedType type)  {
    auto res = Node(Node::AmlType::PDT, static_cast<int>(type));
    return res;
}

inline Node make_referrer(ReferrerType category, const std::string& identifier) {
    Node::map_t map = {
        {"CATEGORY", Node(Node::AmlType::TERMINAL, static_cast<int>(category))},
        {"IDENTIFIER", Node(Node::AmlType::TERMINAL, identifier)}
    };
    auto res = Node(Node::AmlType::REFERRER, map);
    return res;
}

using enumerators_t = std::map<std::string, std::uint32_t>;

inline Node make_enumerator(const std::string& name, std::uint32_t value) {
    Node::map_t map = {
        {"NAME", Node(Node::AmlType::TERMINAL, name)},
        {"VALUE", Node(Node::AmlType::TERMINAL, value)}
    };
    auto res = Node(Node::AmlType::ENUMERATOR, map);
    return res;
}

inline Node make_enumeration(const std::string& name, const enumerators_t& values) {
    Node::list_t lst{};

    for (const auto& [name, value] : values) {
        lst.emplace_back(make_enumerator(name, value));
    }
    Node::map_t map = {
        {"NAME", Node(Node::AmlType::TERMINAL, name)},
        {"VALUES", Node(Node::AmlType::ENUMERATORS, lst)},
    };

    auto res = Node(Node::AmlType::ENUMERATION, map);
    return res;
};

inline Node make_tagged_struct_definition(bool multiple, std::optional<Node> type) {
    Node type_node;

    auto tn = *type;

    if (type) {
        type_node = *type;
    }
    else {
        type_node = Node();
    }

    Node::map_t map = {
        {"MULTIPLE", Node(Node::AmlType::TERMINAL, multiple)},
        {"TYPE", type_node},
    };
    auto res = Node(Node::AmlType::TAGGED_STRUCT_DEFINITION, map);
    return res;
}


inline Node make_tagged_struct_member(bool multiple, const Node& definition) {
    Node::map_t map = {
        {"MULTIPLE", Node(Node::AmlType::TERMINAL, multiple)},
        {"DEFINITION", definition},
    };
    auto res = Node(Node::AmlType::TAGGED_STRUCT_MEMBER, map);
    return res;
}

inline Node make_tagged_struct(const std::string& name, std::vector<std::tuple<std::string, Node>> members) {
    Node::list_t lst{};

    for (const auto& [tag, member] : members) {
        Node::map_t mem_map = {
            {"TAG", Node(Node::AmlType::TERMINAL, tag)},
            {"MEMBER", member},
        };
        lst.emplace_back(Node(Node::AmlType::MEMBER, mem_map));
    }

    Node::map_t map = {
        {"NAME", Node(Node::AmlType::TERMINAL, name)},
        {"MEMBERS", Node(Node::AmlType::MEMBERS, lst)},
    };
    auto res = Node(Node::AmlType::TAGGED_STRUCT, map);
    return res;
}

inline Node make_member(const std::vector<std::uint32_t>& array_spec, const Node& type) {
    Node::list_t lst{};

    for (const auto& arrs : array_spec) {
        lst.emplace_back(Node(Node::AmlType::TERMINAL, arrs));
    }

    Node::map_t map = {
        {"TYPE", type},
        {"ARR_SPEC", Node(Node::AmlType::MEMBERS, lst)},
    };

    auto res = Node(Node::AmlType::MEMBER, map);
    return res;
}

inline Node make_block(const std::string& tag, bool multiple, const Node& type, const Node& member) {
    Node::map_t map = {
        {"TAG", Node(Node::AmlType::TERMINAL, tag)},
        {"MULTIPLE", Node(Node::AmlType::TERMINAL, multiple)},
        {"TYPE", type},
        {"MEMBER", member},
    };
    auto res = Node(Node::AmlType::BLOCK, map);
    return res;
}

inline Node make_struct_member(bool multiple, const Node& member) {
    Node::map_t map = {
        {"MULTIPLE", Node(Node::AmlType::TERMINAL, multiple)},
        {"MEMBER", member},
    };
    auto res = Node(Node::AmlType::STRUCT_MEMBER, map);
    return res;
}

inline Node make_struct(const std::string& name, std::vector<Node>& members) {
    Node::map_t map = {
        {"NAME", Node(Node::AmlType::TERMINAL, name)},
        {"MEMBERS", Node(Node::AmlType::MEMBERS, members)},
    };
    auto res = Node(Node::AmlType::STRUCT, map);
    return res;
}

inline Node make_tagged_uinion_member(const std::string& tag, const Node& member) {
    Node::map_t map = {
        {"TAG", Node(Node::AmlType::TERMINAL, tag)},
        {"MEMBER", member},
    };
    auto res = Node(Node::AmlType::TAGGED_UNION_MEMBER, map);
    return res;
}

inline Node make_tagged_uniom(const std::string& name, std::vector<Node>& members) {
    Node::map_t map = {
        {"NAME", Node(Node::AmlType::TERMINAL, name)},
        {"MEMBERS", Node(Node::AmlType::MEMBERS, members)},
    };
    auto res = Node(Node::AmlType::TAGGED_UNION, map);
    return res;
}

inline Node make_root(std::vector<Node>& members) {
    Node::map_t map = {
        {"MEMBERS", Node(Node::AmlType::MEMBERS, members)},
    };
    auto res = Node(Node::AmlType::ROOT, map);
    return res;
}

class Unmarshaller {
   public:

    Unmarshaller(const std::stringstream& inbuf) : m_reader(inbuf) {
    }

    Node load_pdt() {
        return make_pdt(static_cast<AMLPredefinedType>(m_reader.from_binary<std::uint8_t>()));
    }

    Node load_referrrer() {
        const auto  cat        = ReferrerType(m_reader.from_binary<std::uint8_t>());
        const auto& identifier = m_reader.from_binary_str();
        return make_referrer(cat, identifier);
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
            return make_enumeration( name, enumerators );
        } else if (disc == "R") {
            return load_referrrer();
        }
    }

    Node load_tagged_struct_definition() {
        const auto multiple  = m_reader.from_binary<bool>();
        auto       available = m_reader.from_binary< bool >();

        if (available) {
            return make_tagged_struct_definition(multiple, load_type());
        }
        // else TAG only.
        return make_tagged_struct_definition(multiple, std::nullopt);
    }

    Node load_tagged_struct_member() {
        const auto  multiple = m_reader.from_binary<bool>();
        const auto& dt       = m_reader.from_binary_str();

        if (dt == "T") {
            return make_tagged_struct_member(multiple, load_tagged_struct_definition());
        } else if (dt == "B") {
            return make_tagged_struct_member(multiple, load_block());
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
            return make_tagged_struct( name, members );
        } else if (disc == "R") {
            return load_referrrer();
        }
    }

    Node load_tagged_union() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "U") {
            auto                           name       = m_reader.from_binary_str();
            auto                           tags_count = m_reader.from_binary<std::size_t>();
            std::vector<Node> members;

            // make_tagged_uinion_member

            for (auto idx = 0UL; idx < tags_count; ++idx) {
                auto        tag = m_reader.from_binary_str();
                const auto& dt  = m_reader.from_binary_str();

                if (dt == "M") {
                    members.emplace_back(make_tagged_uinion_member(tag, load_member()));
                    //members.emplace_back(tag, std::move(load_member()));
                } else if (dt == "B") {
                    members.emplace_back(make_tagged_uinion_member(tag, load_block()));
                    //members.emplace_back(tag, std::move(load_block()));
                }
            }
            return make_tagged_uniom(name, members);

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

    Node load_member() {
        auto                       arr_count = m_reader.from_binary<std::size_t>();
        std::vector<std::uint32_t> array_spec;
        for (auto idx = 0UL; idx < arr_count; ++idx) {
            array_spec.push_back(m_reader.from_binary<std::uint32_t>());
        }
        return make_member(array_spec, load_type());
    }

    Node load_struct() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "S") {
            auto                      name         = m_reader.from_binary_str();
            auto                      member_count = m_reader.from_binary<std::size_t>();
            std::vector<Node> members;

            for (auto idx = 0UL; idx < member_count; ++idx) {
                auto member = load_member();
                auto mult   = m_reader.from_binary<bool>();
                members.emplace_back(make_struct_member(mult, member));
            }
            return make_struct(name, members);
        } else if (disc == "R") {
            return load_referrrer();
        }
    }

    Node load_block() {
        const auto& tag  = m_reader.from_binary_str();
        const auto& disc = m_reader.from_binary_str();

        Node tp{};
        Node member{};
        if (disc == "T") {
            tp = load_type();
        } else if (disc == "M") {
            member = load_member();
        }
        auto multiple = m_reader.from_binary<bool>();
        return make_block(tag, multiple, tp, member);
    }

    Node run() {
        auto                     decl_count = m_reader.from_binary<std::size_t>();
        std::vector<Node> result;
        for (auto idx = 0UL; idx < decl_count; ++idx) {
            const auto& disc1 = m_reader.from_binary_str();

            if (disc1 == "TY") {
                result.emplace_back(load_type());
            } else if (disc1 == "BL") {
                auto bt = m_reader.from_binary_str();
                result.emplace_back(load_block());
            }
        }
        return make_root(result);
    }

   private:

    Reader m_reader;
};

Node unmarshal(const std::stringstream& inbuf);

#endif  // __UNMARSHAL_HPP
