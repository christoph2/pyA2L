
#include "aml_visitor.h"

void dumps(std::stringstream& ss, const Type* tp_);

// AMLPredefinedType.
void dumps(std::stringstream& ss, const AMLPredefinedType& pdt) {
    ss << to_binary<std::string>("PD");
    auto value = static_cast<std::uint8_t>(pdt);
    ss << to_binary(value);
}

// Referrer.
void dumps(std::stringstream& ss, const Referrer& ref) {
    ss << to_binary<std::string>("R");
    auto cat = static_cast<std::uint8_t>(ref.get_category());
    auto idf = ref.get_identifier();
    ss << to_binary(cat);
    ss << to_binary(idf);
}


// BlockDefinition.
void dumps(std::stringstream& ss, const BlockDefinition& block) {
    ss << to_binary<std::string>("B");
    const auto& tag = block.get_tag();
    const auto  type = block.get_type();
    ss << to_binary(tag);
    if (type) {
        ss << to_binary<std::string>("T");
        dumps(ss, type);

    }
}

// Member.
void dumps(std::stringstream& ss, const Member& mem) {
    const auto& tp = mem.get_type();
    if (tp != nullptr) {
        ss << to_binary<std::string>("T");

        const auto& arr_spec = mem.get_array_spec();
        const std::size_t array_size = std::size(arr_spec);
        ss << to_binary(array_size);
        for (std::uint32_t arr : arr_spec) {
            ss << to_binary<std::uint32_t>(arr);
        }

        dumps(ss, tp);
    }
    else {
        const auto& blk = *mem.get_block();
        dumps(ss, blk);
    }
}

// TaggedStructDefinition.
void dumps(std::stringstream& ss, const TaggedStructDefinition& tsd) {
    const auto  multiple = tsd.get_multiple();
    const auto& member   = tsd.get_member();
    const auto  tp       = member.get_type();
    ss << to_binary<bool>(multiple);
    if (tp) {
        ss << to_binary<bool>(true);  // available.
        dumps(ss, member);
    } else {
        // Tag-only.
        ss << to_binary<bool>(false);  // NOT available.
    }
}

// TaggedStructMember.
void dumps(std::stringstream& ss, const TaggedStructMember& tsm) {
    const auto multiple = tsm.get_multiple();
    ss << to_binary<bool>(multiple);
    if (tsm.get_block().get_type()) {
        const auto& block = tsm.get_block();
        dumps(ss, block);
    } else {
        ss << to_binary<std::string>("T");
        const auto& tsd = tsm.get_tagged_struct_def();
        dumps(ss, tsd);
    }
}

// TaggedStruct.
void dumps(std::stringstream& ss, const TaggedStructOrReferrer& sr) {
    ss << to_binary<std::string>("TS");
    if (std::holds_alternative<TaggedStruct>(sr)) {
        ss << to_binary<std::string>("S");
        const auto&       ts         = std::get<TaggedStruct>(sr);
        const auto&       members    = ts.get_members();
        const auto&       name       = ts.get_name();
        const auto&       tags       = ts.get_tags();
        const std::size_t tags_count = std::size(tags);
        ss << to_binary(name);
        ss << to_binary(tags_count);
        for (const auto& [tag, value] : tags) {
            ss << to_binary(tag);
            dumps(ss, value);
        }
    } else if (std::holds_alternative<Referrer>(sr)) {
        auto ref = std::get<Referrer>(sr);
        dumps(ss, ref);
    }
}

// TaggedUnionMember.
void dumps(std::stringstream& ss, const TaggedUnionMember& tum) {
    // const auto& tag    = tum.get_tag();
    const auto& block  = tum.get_block();
    const auto& member = tum.get_member();
    if (block.get_type()) {
        dumps(ss, block);
    } else {
        ss << to_binary<std::string>("M");
        dumps(ss, member);
    }
}

// TaggedUnion.
void dumps(std::stringstream& ss, const TaggedUnionOrReferrer& tr) {
    ss << to_binary<std::string>("TU");
    if (std::holds_alternative<TaggedUnion>(tr)) {
        ss << to_binary<std::string>("U");
        const auto&       tu         = std::get<TaggedUnion>(tr);
        const auto&       members    = tu.get_members();
        const auto&       name       = tu.get_name();
        const auto&       tags       = tu.get_tags();
        const std::size_t tags_count = std::size(tags);
        ss << to_binary(name);
        ss << to_binary(tags_count);
        for (const auto& [tag, value] : tags) {
            ss << to_binary(tag);
            dumps(ss, value);
        }
    } else if (std::holds_alternative<Referrer>(tr)) {
        auto ref = std::get<Referrer>(tr);
        dumps(ss, ref);
    }
}

// Struct.
void dumps(std::stringstream& ss, const StructOrReferrer& sr) {
    ss << to_binary<std::string>("ST");
    if (std::holds_alternative<Struct>(sr)) {
        ss << to_binary<std::string>("S");
        const auto&       st           = std::get<Struct>(sr);
        const auto&       name         = st.get_name();
        const auto&       members      = st.get_members();
        const std::size_t member_count = std::size(members);
        ss << to_binary(name);
        ss << to_binary(member_count);
        for (const auto& sm : members) {
            //auto        mult = sm.get_multiple();
            const auto& mem  = sm.get_member();
            dumps(ss, mem);
            //ss << to_binary(mult);
        }
    } else if (std::holds_alternative<Referrer>(sr)) {
        auto ref = std::get<Referrer>(sr);
        dumps(ss, ref);
    }
}

// Enumeration.
void dumps(std::stringstream& ss, const EnumerationOrReferrer& er) {
    ss << to_binary<std::string>("EN");
    if (std::holds_alternative<Enumeration>(er)) {
        ss << to_binary<std::string>("E");
        const auto&       enumeration      = std::get<Enumeration>(er);
        const auto&       name             = enumeration.get_name();
        const auto&       enumerators      = enumeration.get_enumerators();
        const std::size_t enumerator_count = std::size(enumerators);
        ss << to_binary(name);
        ss << to_binary(enumerator_count);
        for (const auto& [tag, value] : enumerators) {
            ss << to_binary(tag);
            ss << to_binary<std::uint32_t>(value);
        }
    } else if (std::holds_alternative<Referrer>(er)) {
        auto ref = std::get<Referrer>(er);
        dumps(ss, ref);
    }
}

// Type.
void dumps(std::stringstream& ss, const Type* tp_) {
    auto tp  = tp_->get_type();
    //auto tag = tp_->get_tag();
    //ss << to_binary(tag);
    std::visit(
        [&ss, &tp](auto&& arg) {
            using T = std::decay_t<decltype(arg)>;
            if constexpr (std::is_same_v<T, std::monostate>) {
                std::cout << "std::monostate!? " << '\n';
            } else if constexpr (std::is_same_v<T, AMLPredefinedType>) {
                dumps(ss, arg);
            } else if constexpr (std::is_same_v<T, EnumerationOrReferrer>) {
                dumps(ss, arg);
            } else if constexpr (std::is_same_v<T, StructOrReferrer>) {
                dumps(ss, arg);
            } else if constexpr (std::is_same_v<T, TaggedStructOrReferrer>) {
                dumps(ss, arg);
            } else if constexpr (std::is_same_v<T, TaggedUnionOrReferrer>) {
                dumps(ss, arg);
            }
        },
        tp
    );
}

// Declaration.
void dumps(std::stringstream& ss, const Declaration& decl) {
    const auto  tp    = decl.get_type();
    const auto& block = decl.get_block();
    if (block.get_type() != nullptr) {
        ss << to_binary<std::string>("BL");
        dumps(ss, block);
    } else if (tp.get_type() != nullptr) {
        ss << to_binary<std::string>("TY");
        dumps(ss, tp.get_type());
    }
}

// AMLFile.
void dumps(std::stringstream& ss, const AmlFile& amlf) {
    const auto&       decls      = amlf.get_decls();
    const std::size_t decl_count = std::size(decls);
    ss << to_binary<std::size_t>(decl_count);
    for (const auto& decl : decls) {
        dumps(ss, decl);
    }
}

void marshal(std::stringstream& ss, const AmlFile& amlf) {
    dumps(ss, amlf);
}
