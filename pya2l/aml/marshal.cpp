
#include "klasses.hpp"

inline std::string null_pointer() {
    return to_binary<nullptr_t>(nullptr);
}

inline std::string false_value() {
    return to_binary<bool>(false);
}

inline std::string true_value() {
    return to_binary<bool>(true);
}

void dumps(std::stringstream& ss, std::shared_ptr<Type> tp_);

// AMLPredefinedType
inline void dumps(std::stringstream& ss, const AMLPredefinedType& pdt) {
    ss << to_binary<std::string>("PD");
    auto value = static_cast<uint8_t>(pdt.get_pdt());
    ss << to_binary(value);
    const auto&       arr_spec   = pdt.get_array_spec();
    const std::size_t array_size = std::size(arr_spec);
    ss << to_binary(array_size);
    for (uint32_t arr : arr_spec) {
        ss << to_binary<uint32_t>(arr);
    }
}

// Referrer.
inline void dumps(std::stringstream& ss, const Referrer& ref) {
    ss << to_binary<std::string>("R");
    auto cat = static_cast<uint8_t>(ref.get_category());
    auto idf = ref.get_identifier();
    ss << to_binary(cat);
    ss << to_binary(idf);
}

// BlockDefinition.
inline void dumps(std::stringstream& ss, std::shared_ptr<BlockDefinition> block) {
    ss << to_binary<std::string>("B");
    const auto& tag      = block->get_tag();
    auto        multiple = block->get_multiple();
    auto        type     = block->get_type();
    ss << to_binary(tag);
    ss << to_binary(multiple);
    if (type) {
        ss << to_binary<std::string>("T");
        dumps(ss, type);
    }
}

// Member.
inline void dumps(std::stringstream& ss, const Member& mem) {
    auto tp = mem.get_type();
    if (mem.is_empty()) {
        ss << false_value();
        return;
    }
    ss << true_value();
    if (tp != nullptr) {
        ss << to_binary<std::string>("T");
        if (tp->get_type().valueless_by_exception() == true) {
        } else {
            dumps(ss, tp);
        }
    } else {
        const auto blk = mem.get_block();
        if (blk) {
            dumps(ss, blk);
        } else {
            // FIX-ME!
        }
    }
}

// TaggedStructDefinition.
inline void dumps(std::stringstream& ss, const TaggedStructDefinition& tsd) {
    const auto  multiple = tsd.get_multiple();
    const auto& member   = tsd.get_member();
    const auto  tp       = member.get_type();
    ss << to_binary<bool>(multiple);
    if (tp) {
        ss << true_value();  // available.
        dumps(ss, member);
    } else {
        // Tag-only.
        ss << false_value();  // NOT available.
    }
}

// TaggedStructMember.
inline void dumps(std::stringstream& ss, const TaggedStructMember& tsm) {
    const auto multiple = tsm.get_multiple();
    ss << to_binary<bool>(multiple);
    if (tsm.get_block()->get_type()) {
        const auto& block = tsm.get_block();
        dumps(ss, block);
    } else {
        ss << to_binary<std::string>("T");
        const auto& tsd = tsm.get_tagged_struct_def();
        dumps(ss, tsd);
    }
}

// TaggedStruct.
inline void dumps(std::stringstream& ss, const TaggedStructOrReferrer& sr) {
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
inline void dumps(std::stringstream& ss, const TaggedUnionMember& tum) {
    // const auto& tag    = tum.get_tag();
    const auto& block  = tum.get_block();
    const auto& member = tum.get_member();
    if (block->get_type()) {
        dumps(ss, block);
    } else {
        ss << to_binary<std::string>("M");
        dumps(ss, member);
    }
}

// TaggedUnion.
inline void dumps(std::stringstream& ss, const TaggedUnionOrReferrer& tr) {
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
inline void dumps(std::stringstream& ss, const StructOrReferrer& sr) {
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
            const auto mem = sm.get_member();
            if (mem) {
                if (mem->is_empty()) {
                    ss << false_value();
                } else {
                    ss << true_value();
                    dumps(ss, *mem);
                }
            } else {
                ss << null_pointer();
            }
        }
    } else if (std::holds_alternative<Referrer>(sr)) {
        auto ref = std::get<Referrer>(sr);
        dumps(ss, ref);
    }
}

// Enumeration.
inline void dumps(std::stringstream& ss, const EnumerationOrReferrer& er) {
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
            ss << to_binary<uint32_t>(static_cast<uint32_t>(value));
        }
    } else if (std::holds_alternative<Referrer>(er)) {
        auto ref = std::get<Referrer>(er);
        dumps(ss, ref);
    }
}

// Type.
inline void dumps(std::stringstream& ss, std::shared_ptr<Type> tp_) {
    auto tp = tp_->get_type();
    // auto tag = tp_->get_tag();
    // ss << to_binary(tag);
    if (tp.valueless_by_exception() == true) {
        return;
    }
    std::visit(
        [&ss, &tp](auto&& arg) {
            using T = std::decay_t<decltype(arg)>;
            if constexpr (std::is_same_v<T, std::monostate>) {
                // std::cout << "std::monostate!? " << '\n';
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

// Typedefinition
inline void dumps(std::stringstream& ss, std::shared_ptr<TypeDefinition> type_def) {
    auto tp = type_def->get_type();
    dumps(ss, tp);
}

// Declaration.
inline void dumps(std::stringstream& ss, const Declaration& decl) {
    auto td    = decl.get_type();
    auto block = decl.get_block();
    if (block) {
        ss << to_binary<std::string>("BL");
        dumps(ss, block);
    } else if (td) {
        ss << to_binary<std::string>("TY");
        dumps(ss, td);
    }
}

// AMLFile.
inline void dumps(std::stringstream& ss, const AmlFile& amlf) {
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
