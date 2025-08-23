#if !defined(__AML_PARSER_HPP)
    #define __AML_PARSER_HPP

// namespace Aml {
    #include "klasses.hpp"
    #include "utils.hpp"

class AMLParser {
   public:

    explicit AMLParser(const std::vector<AmlToken>& tokens) : m_tokens(tokens), m_pos(0) {
    }

    const AmlToken& current_token() const noexcept {
        return m_tokens[m_pos];
    }

    const AmlToken& la(std::size_t offs) const noexcept {
        return m_tokens[m_pos + offs];
    }

    void consume() noexcept {
        m_pos++;
    }

    bool expect(AmlTokenType type, TokenDataType value = std::nullopt) {
        auto token = current_token();
        if (type != token.type) {
            std::cerr << "Invalid AmlToken type!!!\n";
            return false;
        }
        if (value && token.value) {
            if (*value != *token.value) {
                std::cerr << "Unexpected AmlToken value!!!\n";
                return false;
            }
        }
        return true;
    }

    void match(AmlTokenType type, bool consume_token = true) {
        if (!expect(type)) {
            throw std::runtime_error("Invalid AmlToken type.");
        }
        if (consume_token) {
            consume();
        }
    }

    auto match_get_value(AmlTokenType type, bool consume_token = true) -> TokenDataType {
        if (!expect(type)) {
            throw std::runtime_error("Invalid AmlToken type.");
        }
        auto value = current_token().value;

        if (consume_token) {
            consume();
        }
        return value;
    }

    auto get_tag() -> std::string {
        return variant_get<std::string>(*match_get_value(AmlTokenType::TAG));
    }

    auto get_ident() -> std::string {
        return variant_get<std::string>(*match_get_value(AmlTokenType::IDENT));
    }

    auto get_int() -> int64_t {
        auto token = current_token();
        auto value = *token.value;
        consume();
        if (std::holds_alternative<int64_t >(value)) {
            return std::get<int64_t>(value);
        } else if (std::holds_alternative<long double>(value)) {
            return static_cast<long double>(std::get<long double>(value));
        } else if (std::holds_alternative<std::string>(value)) {
            return std::strtoll(std::get<std::string>(value).c_str(), nullptr, 10);
        } else {
            throw std::runtime_error("get_int(): Invalid AMLType.");
        }
    }

    auto parse() -> AmlFile {
        if (std::size(m_tokens) == 0) {
            std::cout << "Empty AML section." << std::endl;
            return {};
        }
        return aml_file();
    }

    auto aml_file() -> AmlFile {
        std::string a2ml;

        match(AmlTokenType::BEGIN);
        a2ml       = get_ident();
        auto decls = declaration();
        match(AmlTokenType::END);
        a2ml = get_ident();
        return AmlFile(decls);
    }

    auto declaration() -> std::vector<Declaration> {
        std::vector<Declaration> decls;
        while (true) {
            auto token = current_token();
            if (token.type == AmlTokenType::END) {
                break;
            }
            if (token.type == AmlTokenType::BLOCK) {
                decls.emplace_back(nullptr, std::make_shared<BlockDefinition>(block_definition()));
            } else {
                decls.emplace_back(std::make_shared<TypeDefinition>(type_definition()), nullptr);
            }
            token = current_token();
            if (token.type == AmlTokenType::SEMI) {
                match(AmlTokenType::SEMI);
            }
        }
        return decls;
    }

    auto type_definition() -> TypeDefinition {
        auto tn = type_name();
        return TypeDefinition(std::make_shared<Type>(tn));
    }

    auto type_name() -> Type {
        auto token = current_token();

        if (token.type == AmlTokenType::STRUCT) {
            return struct_type_name();
        } else if (token.type == AmlTokenType::TAGGED_STRUCT) {
            return taggedstruct_type_name();
        } else if (token.type == AmlTokenType::TAGGED_UNION) {
            return taggedunion_type_name();
        } else if (token.type == AmlTokenType::PDT) {
            return predefined_type_name();
        } else if (token.type == AmlTokenType::ENUM) {
            return enum_type_name();
        } else {
            std::cerr << "Unexpected token (not an AML type)\n";
            consume();
        }
    }

    auto predefined_type_name() -> AMLPredefinedType {
        auto pdt        = variant_get<AMLPredefinedTypeEnum>(*match_get_value(AmlTokenType::PDT));
        auto array_spec = array_specifier();
        return AMLPredefinedType(pdt, array_spec);
    }

    auto block_definition() -> BlockDefinition {
        bool multiple{ false };
        match(AmlTokenType::BLOCK);
        auto tag = get_tag();

        auto token = current_token();
        if (token.type == AmlTokenType::LPARAN) {
            match(AmlTokenType::LPARAN);
            multiple = true;
            token    = current_token();
        }
        auto tp = type_name();
        token   = current_token();
        if (multiple) {
            match(AmlTokenType::RPARAN);
            match(AmlTokenType::STAR);
        }
        return BlockDefinition(tag, std::make_shared<Type>(tp), multiple);
    }

    auto struct_type_name() -> StructOrReferrer {
        std::string               name;
        std::vector<StructMember> members;

        match(AmlTokenType::STRUCT);
        auto token = current_token();
        if (token.type == AmlTokenType::IDENT) {
            name  = get_ident();
            token = current_token();
        }
        if (token.type == AmlTokenType::LBRACE) {
            match(AmlTokenType::LBRACE);
            while (true) {
                token = current_token();
                if (token.type == AmlTokenType::RBRACE) {
                    break;
                }
                members.emplace_back(struct_member());
            }
            match(AmlTokenType::RBRACE);
            return Struct(name, members);
        } else {
            return Referrer(ReferrerType::StructType, name);
        }
    }

    auto struct_member() -> StructMember {
        auto token = current_token();
        if (token.type == AmlTokenType::RBRACE) {
            return StructMember(std::nullopt);
        }
        auto mem = member();
        token    = current_token();
        if (token.type == AmlTokenType::SEMI) {
            consume();  // Optional ';'
        }
        return StructMember(std::move(mem));
    }

    auto taggedstruct_type_name() -> TaggedStructOrReferrer {
        std::string                      name;
        std::vector< TaggedStructMember> members;

        match(AmlTokenType::TAGGED_STRUCT);
        auto token = current_token();
        if (token.type == AmlTokenType::IDENT) {
            name  = get_ident();
            token = current_token();
        }
        if (token.type == AmlTokenType::LBRACE) {
            match(AmlTokenType::LBRACE);
            while (true) {
                token = current_token();
                if (token.type == AmlTokenType::RBRACE) {
                    break;
                }
                members.emplace_back(tagged_struct_member());
            }
            match(AmlTokenType::RBRACE);
        } else {
            return Referrer(ReferrerType::TaggedStructType, name);
        }
        token = current_token();
        if (token.type == AmlTokenType::SEMI) {
            consume();  // Optional ';'
        }
        return TaggedStruct(name, std::move(members));
    }

    auto tagged_struct_member() -> TaggedStructMember {
        bool                   multiple{ false };
        TaggedStructDefinition tsd;
        BlockDefinition        block;

        auto token = current_token();

        if (token.type == AmlTokenType::LPARAN) {
            match(AmlTokenType::LPARAN);
            multiple = true;
            token    = current_token();
        }
        if (token.type == AmlTokenType::BLOCK) {
            block = block_definition();
        } else {
            tsd = taggedstruct_definition();
        }
        if (multiple) {
            token = current_token();
            if (token.type == AmlTokenType::SEMI) {
                match(AmlTokenType::SEMI);
            }
            match(AmlTokenType::RPARAN);
            match(AmlTokenType::STAR);
        }
        token = current_token();
        if (token.type == AmlTokenType::SEMI) {
            match(AmlTokenType::SEMI);
        }
        return TaggedStructMember(std::move(tsd), std::make_shared<BlockDefinition>(block), multiple);
    }

    auto taggedstruct_definition() -> TaggedStructDefinition {
        std::string tag;
        Member      mem;
        bool        multiple{ false };
        auto        token = current_token();
        if (token.type != AmlTokenType::TAG) {
            std::cerr << "Missing required TAG\n";
        } else {
            tag = get_tag();
        }

        token = current_token();
        if (token.type == AmlTokenType::LPARAN) {
            match(AmlTokenType::LPARAN);
            multiple = true;
        }
        // TODO: check empty, i.e SEMI!!!
        if (token.type == AmlTokenType::SEMI) {
            if (multiple) {
                throw std::runtime_error("Did not expect empty taggedstruct_definition with multiple");
            }
        } else {
            mem   = member();
            token = current_token();
            if (token.type == AmlTokenType::SEMI) {
                match(AmlTokenType::SEMI);
            }
            if (multiple) {
                match(AmlTokenType::RPARAN);
                match(AmlTokenType::STAR);
            }
        }
        return TaggedStructDefinition(tag, std::move(mem), multiple);
    }

    auto taggedunion_type_name() -> TaggedUnionOrReferrer {
        std::string                     name;
        std::vector< TaggedUnionMember> members;

        match(AmlTokenType::TAGGED_UNION);
        auto token = current_token();
        if (token.type == AmlTokenType::IDENT) {
            name  = get_ident();
            token = current_token();
        }
        if (token.type == AmlTokenType::LBRACE) {
            match(AmlTokenType::LBRACE);
            while (true) {
                token = current_token();
                if (token.type == AmlTokenType::RBRACE) {
                    break;
                }
                members.emplace_back(tagged_union_member());
            }
            match(AmlTokenType::RBRACE);
            return TaggedUnion(name, std::move(members));
        } else {
            return Referrer(ReferrerType::TaggedUnionType, name);
        }
    }

    auto tagged_union_member() -> TaggedUnionMember {
        std::string     tag;
        Member          mem;
        BlockDefinition block;

        auto token = current_token();
        if (token.type == AmlTokenType::TAG) {
            tag = get_tag();
            mem = member();
        } else if (token.type == AmlTokenType::BLOCK) {
            block = block_definition();
        }
        token = current_token();
        if (token.type == AmlTokenType::SEMI) {
            match(AmlTokenType::SEMI);
            token = current_token();
        }
        return TaggedUnionMember(tag, std::move(mem), std::make_shared<BlockDefinition>(block));
    }

    auto enum_type_name() -> EnumerationOrReferrer {
        std::string             name;
        std::vector<Enumerator> enumerators;

        match(AmlTokenType::ENUM);
        auto token = current_token();
        if (token.type == AmlTokenType::IDENT) {
            name  = get_ident();
            token = current_token();
        }
        if (token.type == AmlTokenType::LBRACE) {
            match(AmlTokenType::LBRACE);
            enumerators = enumerator_list();
            match(AmlTokenType::RBRACE);
        } else {
            return Referrer(ReferrerType::Enumeration, name);
        }
        return Enumeration(name, enumerators);
    }

    auto enumerator_list() -> std::vector<Enumerator> {
        std::vector<Enumerator> result;
        while (true) {
            result.emplace_back(enumerator());
            auto token = current_token();
            if (token.type != AmlTokenType::COLON) {
                break;
            }
            match(AmlTokenType::COLON);
        }
        return result;
    }

    auto enumerator() -> Enumerator {
        std::optional<numeric_t> value;
        auto                     tag   = get_tag();
        auto                     token = current_token();

        if (token.type == AmlTokenType::EQU) {
            match(AmlTokenType::EQU);
            value = get_int();
        }
        return Enumerator(tag, value);
    }

    auto member() -> Member {
        auto token = current_token();

        if (token.type == AmlTokenType::BLOCK) {
            return Member(std::make_shared<BlockDefinition>(block_definition()), nullptr);
        } else {
            if (token.type == AmlTokenType::SEMI) {
                return Member();  // Empty.
            }
            auto tp = type_name();
            return Member(nullptr, tp.get_type().valueless_by_exception() == false ? std::make_shared<Type>(tp) : nullptr);
        }
    }

    auto array_specifier() -> std::vector<uint32_t> {
        std::vector<uint32_t> result;
        uint32_t              value;
        auto                 token = current_token();
        if (token.type == AmlTokenType::LSQ) {
            while (true) {
                token = current_token();
                if (token.type != AmlTokenType::LSQ) {
                    break;
                }
                match(AmlTokenType::LSQ);
                value = static_cast<uint32_t>(get_int());
                result.push_back(value);
                match(AmlTokenType::RSQ);
            }
        }
        return result;
    }

   private:

    std::vector<AmlToken> m_tokens;
    std::size_t           m_pos;
};

// };   // namespace Aml

#endif  // __AML_PARSER_HPP
