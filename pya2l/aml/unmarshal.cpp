
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

class Unmarshaller {
   public:

    struct type_t;

    using referrer_t                = std::tuple<ReferrerType, std::string>;
    using enumerators_t             = std::map<std::string, std::uint32_t>;
    using enumeration_t             = std::tuple<std::string, enumerators_t>;
    using enumeration_or_referrer_t = std::variant<std::monostate, enumeration_t, referrer_t>;

    using member_t = std::tuple<std::vector<std::uint32_t>, std::unique_ptr<type_t>>;

    using block_intern_t = std::variant<std::monostate, member_t, std::unique_ptr<type_t>>;
    using block_t        = std::tuple<std::string, bool, block_intern_t>;

    using tagged_struct_definition_t  = std::tuple<bool, std::optional<std::unique_ptr<type_t>>>;
    using tagged_struct_member_t      = std::tuple<bool, std::variant<std::monostate, block_t, tagged_struct_definition_t>>;
    using tagged_struct_t             = std::tuple<std::string, std::vector<std::tuple<std::string, tagged_struct_member_t>>>;
    using tagged_struct_or_referrer_t = std::variant<std::monostate, tagged_struct_t, referrer_t>;

    using tagged_union_member_t      = std::tuple< std::string, std::variant<std::monostate, block_t, member_t>>;
    using tagged_union_t             = std::tuple<std::string, std::vector<tagged_union_member_t>>;
    using tagged_union_or_referrer_t = std::variant<std::monostate, tagged_union_t, referrer_t>;

    using struct_member_t      = std::tuple<bool, member_t>;
    using struct_t             = std::tuple<std::string, std::vector<struct_member_t>>;
    using struct_or_referrer_t = std::variant<std::monostate, struct_t, referrer_t>;

    struct type_t {
        type_t()              = default;
        type_t(const type_t&) = delete;
        type_t(type_t&&)      = default;

        type_t(auto&& value) : m_value(std::move(value)) {
        }

        virtual ~type_t() = default;

        std::variant<
            std::monostate, AMLPredefinedType, enumeration_or_referrer_t, tagged_struct_or_referrer_t, tagged_union_or_referrer_t,
            struct_or_referrer_t>
            m_value;
    };

    Unmarshaller(const std::stringstream& inbuf) : m_reader(inbuf) {
    }

    AMLPredefinedType load_pdt() {
        return AMLPredefinedType(m_reader.from_binary<std::uint8_t>());
    }

    referrer_t load_referrrer() {
        const auto  cat        = ReferrerType(m_reader.from_binary<std::uint8_t>());
        const auto& identifier = m_reader.from_binary_str();
        return referrer_t{ cat, identifier };
    }

    enumeration_or_referrer_t load_enum() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "E") {
            auto name             = m_reader.from_binary_str();
            auto enumerator_count = m_reader.from_binary<std::size_t>();

            enumerators_t enumerators;

            for (auto idx = 0UL; idx < enumerator_count; ++idx) {
                auto tag   = m_reader.from_binary_str();
                auto value = m_reader.from_binary< std::uint32_t>();

                enumerators.try_emplace(tag, value);
            }
            return enumeration_t{ name, enumerators };
        } else if (disc == "R") {
            return load_referrrer();
        }
    }

    tagged_struct_definition_t load_tagged_struct_definition() {
        const auto multiple  = m_reader.from_binary<bool>();
        auto       available = m_reader.from_binary< bool >();

        if (available) {
            return tagged_struct_definition_t{ multiple, std::make_unique<type_t>(load_type()) };
        }
        // else TAG only.
        return tagged_struct_definition_t{ multiple, std::nullopt };
    }

    tagged_struct_member_t load_tagged_struct_member() {
        const auto  multiple = m_reader.from_binary<bool>();
        const auto& dt       = m_reader.from_binary_str();

        if (dt == "T") {
            return tagged_struct_member_t{ multiple, load_tagged_struct_definition() };
        } else if (dt == "B") {
            return tagged_struct_member_t{ multiple, load_block() };
        }
    }

    tagged_struct_or_referrer_t load_tagged_struct() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "S") {
            auto                                                         name       = m_reader.from_binary_str();
            auto                                                         tags_count = m_reader.from_binary<std::size_t>();
            std::vector<std::tuple<std::string, tagged_struct_member_t>> members;
            for (auto idx = 0UL; idx < tags_count; ++idx) {
                const auto& tag = m_reader.from_binary_str();
                members.emplace_back(tag, load_tagged_struct_member());
            }
            return tagged_struct_t{ name, std::move(members) };
        } else if (disc == "R") {
            return load_referrrer();
        }
    }

    tagged_union_or_referrer_t load_tagged_union() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "U") {
            auto                               name       = m_reader.from_binary_str();
            auto                               tags_count = m_reader.from_binary<std::size_t>();
            std::vector<tagged_union_member_t> members;

            for (auto idx = 0UL; idx < tags_count; ++idx) {
                auto        tag = m_reader.from_binary_str();
                const auto& dt  = m_reader.from_binary_str();

                if (dt == "M") {
                    members.emplace_back(tag, load_member());
                } else if (dt == "B") {
                    members.emplace_back(tag, load_block());
                }
            }
            return tagged_union_t{ name, std::move(members) };

        } else if (disc == "R") {
            return load_referrrer();
        }
    }

    type_t load_type() {
        const auto& tag = m_reader.from_binary_str();
        // "PD" - AMLPredefinedType
        // "TS" - TaggedStruct
        // "TU" - TaggedUnion
        // "ST" - Struct
        // "EN" - Enumeration
        const auto& disc = m_reader.from_binary_str();
        type_t      result;

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

    member_t load_member() {
        auto                       arr_count = m_reader.from_binary<std::size_t>();
        std::vector<std::uint32_t> array_spec;
        for (auto idx = 0UL; idx < arr_count; ++idx) {
            array_spec.push_back(m_reader.from_binary<std::uint32_t>());
        }
        return member_t{ array_spec, std::make_unique<type_t>(load_type()) };
    }

    struct_or_referrer_t load_struct() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "S") {
            auto                         name         = m_reader.from_binary_str();
            auto                         member_count = m_reader.from_binary<std::size_t>();
            std::vector<struct_member_t> members;

            for (auto idx = 0UL; idx < member_count; ++idx) {
                auto member = load_member();
                auto mult   = m_reader.from_binary<bool>();
                members.emplace_back(mult, std::move(member));
            }
            return struct_t{ name, std::move(members) };
        } else if (disc == "R") {
            return load_referrrer();
        }
    }

    block_t load_block() {
        const auto& tag  = m_reader.from_binary_str();
        const auto& disc = m_reader.from_binary_str();

        block_intern_t result{};
        if (disc == "T") {
            result = std::make_unique<type_t>(load_type());
        } else if (disc == "M") {
            result = load_member();
        }
        auto multiple = m_reader.from_binary<bool>();

        return block_t{ tag, multiple, std::move(result) };
    }

    std::vector<std::variant<type_t, block_t>> run() {
        auto                                       decl_count = m_reader.from_binary<std::size_t>();
        std::vector<std::variant<type_t, block_t>> result;
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

void unmarshal(const std::stringstream& inbuf) {
    auto unm    = Unmarshaller(inbuf);
    auto result = unm.run();
    // return result;
}
