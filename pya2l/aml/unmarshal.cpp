
#include <cassert>
#include <iostream>
#include <sstream>
#include <vector>

#include "types.hpp"

class Reader {
   public:

    Reader() = delete;

    Reader(const std::stringstream& inbuf) : m_buf(inbuf.str()) {
    }

    template<typename T>
    inline T from_binary() {
        auto tmp = *reinterpret_cast<const T*>(&m_buf[m_offset]);
        m_offset += sizeof(T);
        return tmp;
    }

    inline std::string from_binary_str() {
        auto        length = from_binary<std::uint32_t>();
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

    Unmarshaller(const std::stringstream& inbuf) : m_reader(inbuf) {
    }

    void load_pdt() {
        const auto pdt = AMLPredefinedType(m_reader.from_binary<std::uint8_t>());
    }

    void load_referrrer() {
        const auto  cat        = ReferrerType(m_reader.from_binary<std::uint8_t>());
        const auto& identifier = m_reader.from_binary_str();
    }

    void load_enum() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "E") {
            auto name             = m_reader.from_binary_str();
            auto enumerator_count = m_reader.from_binary<std::uint32_t>();

            for (auto idx = 0; idx < enumerator_count; ++idx) {
                auto tag   = m_reader.from_binary_str();
                auto value = m_reader.from_binary< std::uint32_t>();
            }
        } else if (disc == "R") {
            load_referrrer();
        }
    }

    void load_tagged_struct_definition() {
        const auto multiple  = m_reader.from_binary<bool>();
        auto       available = m_reader.from_binary< bool >();
        if (available) {
            load_type();
        }
        // Else TAG only.
    }

    void load_tagged_struct_member() {
        const auto  multiple = m_reader.from_binary<bool>();
        const auto& dt       = m_reader.from_binary_str();
        if (dt == "T") {
            load_tagged_struct_definition();
        } else if (dt == "B") {
            load_block();
        }
    }

    void load_tagged_struct() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "S") {
            auto name       = m_reader.from_binary_str();
            auto tags_count = m_reader.from_binary<std::uint32_t>();
            for (auto idx = 0; idx < tags_count; ++idx) {
                const auto& tag = m_reader.from_binary_str();
                load_tagged_struct_member();
            }
        } else if (disc == "R") {
            load_referrrer();
        }
    }

    void load_tagged_union() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "U") {
            auto name       = m_reader.from_binary_str();
            auto tags_count = m_reader.from_binary<std::uint32_t>();
            for (auto idx = 0; idx < tags_count; ++idx) {
                auto        tag = m_reader.from_binary_str();
                const auto& dt  = m_reader.from_binary_str();
                if (dt == "M") {
                    load_member();
                } else if (dt == "B") {
                    load_block();
                }
            }
        } else if (disc == "R") {
            load_referrrer();
        }
    }

    void load_type() {
        const auto& tag = m_reader.from_binary_str();
        // "PD" - AMLPredefinedType
        // "TS" - TaggedStruct
        // "TU" - TaggedUnion
        // "ST" - Struct
        // "EN" - Enumeration
        const auto& disc = m_reader.from_binary_str();

        if (disc == "PD") {
            load_pdt();
        } else if (disc == "TS") {
            load_tagged_struct();
        } else if (disc == "TU") {
            load_tagged_union();
        } else if (disc == "ST") {
            load_struct();
        } else if (disc == "EN") {
            load_enum();
        } else {
            assert(true == false);
        }
    }

    void load_member() {
        auto                       arr_count = m_reader.from_binary<std::uint32_t>();
        std::vector<std::uint32_t> array_spec;
        for (auto idx = 0; idx < arr_count; ++idx) {
            array_spec.push_back(m_reader.from_binary<std::uint32_t>());
        }
        load_type();
    }

    void load_struct() {
        const auto& disc = m_reader.from_binary_str();
        if (disc == "S") {
            auto name         = m_reader.from_binary_str();
            auto member_count = m_reader.from_binary<std::uint32_t>();
            for (auto idx = 0; idx < member_count; ++idx) {
                load_member();
                auto mult = m_reader.from_binary<bool>();
            }
        } else if (disc == "R") {
            load_referrrer();
        }
    }

    void load_block() {
        const auto& tag  = m_reader.from_binary_str();
        const auto& disc = m_reader.from_binary_str();
        if (disc == "T") {
            load_type();
        } else if (disc == "M") {
            load_member();
        }
        auto multiple = m_reader.from_binary<bool>();
    }

    void run() {
        auto decl_count = m_reader.from_binary<std::uint32_t>();
        for (auto idx = 0; idx < decl_count; ++idx) {
            const auto& disc1 = m_reader.from_binary_str();

            if (disc1 == "TY") {
                load_type();
            } else if (disc1 == "BL") {
                load_block();
            }
        }
    }

   private:

    Reader m_reader;
};

void unmarshal(const std::stringstream& inbuf) {
    auto unm = Unmarshaller(inbuf);
    unm.run();
}
