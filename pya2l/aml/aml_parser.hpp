#if !defined(__AML_PARSER_HPP)
    #define __AML_PARSER_HPP

// namespace Aml {
    #include "klasses.hpp"
    #include "utils.hpp"

class AMLParser {
   public:

    explicit AMLParser(const std::vector<AmlToken>& tokens) : m_tokens(tokens), m_pos(0), m_error_count(0) {
    }

    std::size_t get_error_count() const noexcept {
        return m_error_count;
    }

    const AmlToken& current_token() const {
        if (m_pos >= std::size(m_tokens)) {
            throw std::runtime_error(
                "[ERROR (pya2l.AMLParser)] Unexpected end of token stream at position " +
                std::to_string(m_pos) + " (total tokens: " + std::to_string(std::size(m_tokens)) + ")"
            );
        }
        return m_tokens[m_pos];
    }

    const AmlToken& la(std::size_t offs) const {
        if (m_pos + offs >= std::size(m_tokens)) {
            throw std::runtime_error(
                "[ERROR (pya2l.AMLParser)] Look-ahead out of bounds: position " +
                std::to_string(m_pos + offs) + " (total tokens: " + std::to_string(std::size(m_tokens)) + ")"
            );
        }
        return m_tokens[m_pos + offs];
    }

    void consume() {
        if (m_pos >= std::size(m_tokens)) {
            throw std::runtime_error(
                "[ERROR (pya2l.AMLParser)] Cannot consume past end of token stream (position " +
                std::to_string(m_pos) + ", total tokens: " + std::to_string(std::size(m_tokens)) + ")"
            );
        }
        m_pos++;
    }

    static std::string token_type_name(AmlTokenType t) {
        switch (t) {
            case AmlTokenType::NONE:          return "NONE";
            case AmlTokenType::IDENT:         return "IDENT";
            case AmlTokenType::FLOAT:         return "FLOAT";
            case AmlTokenType::INT:           return "INT";
            case AmlTokenType::COMMENT:       return "COMMENT";
            case AmlTokenType::TAG:           return "TAG";
            case AmlTokenType::BEGIN:         return "BEGIN(/begin)";
            case AmlTokenType::END:           return "END(/end)";
            case AmlTokenType::ENUM:          return "ENUM";
            case AmlTokenType::STRUCT:        return "STRUCT";
            case AmlTokenType::TAGGED_STRUCT: return "TAGGED_STRUCT";
            case AmlTokenType::TAGGED_UNION:  return "TAGGED_UNION";
            case AmlTokenType::PDT:           return "PDT";
            case AmlTokenType::LBRACE:        return "{";
            case AmlTokenType::RBRACE:        return "}";
            case AmlTokenType::LPARAN:        return "(";
            case AmlTokenType::RPARAN:        return ")";
            case AmlTokenType::LSQ:           return "[";
            case AmlTokenType::RSQ:           return "]";
            case AmlTokenType::EQU:           return "=";
            case AmlTokenType::SEMI:          return ";";
            case AmlTokenType::COLON:         return ",";
            case AmlTokenType::STAR:          return "*";
            case AmlTokenType::BLOCK:         return "BLOCK";
            case AmlTokenType::INCLUDE:       return "INCLUDE";
            default:                          return "<unknown>";
        }
    }

    std::string token_location(const AmlToken& tok) const {
        return "line " + std::to_string(tok.line) + ", col " + std::to_string(tok.col);
    }

    bool expect(AmlTokenType type, TokenDataType value = std::nullopt) {
        auto token = current_token();
        if (type != token.type) {
            std::cerr << "[ERROR (pya2l.AMLParser)] Expected token type '" << token_type_name(type)
                      << "' but got '" << token_type_name(token.type)
                      << "' at " << token_location(token) << "\n";
            return false;
        }
        if (value && token.value) {
            if (*value != *token.value) {
                std::cerr << "[ERROR (pya2l.AMLParser)] Unexpected token value at " << token_location(token) << "\n";
                return false;
            }
        }
        return true;
    }

    void match(AmlTokenType type, bool consume_token = true) {
        if (!expect(type)) {
            auto& tok = current_token();
            throw std::runtime_error(
                "[ERROR (pya2l.AMLParser)] Expected '" + token_type_name(type) +
                "' but got '" + token_type_name(tok.type) + "' at " + token_location(tok)
            );
        }
        if (consume_token) {
            consume();
        }
    }

    auto match_get_value(AmlTokenType type, bool consume_token = true) -> TokenDataType {
        if (!expect(type)) {
            auto& tok = current_token();
            throw std::runtime_error(
                "[ERROR (pya2l.AMLParser)] Expected '" + token_type_name(type) +
                "' but got '" + token_type_name(tok.type) + "' at " + token_location(tok)
            );
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
            return static_cast<int64_t>(std::get<long double>(value));
        } else if (std::holds_alternative<std::string>(value)) {
            return std::strtoll(std::get<std::string>(value).c_str(), nullptr, 10);
        } else {
            throw std::runtime_error("[ERROR (pya2l.AMLParser)] get_int(): Token at " + token_location(token) + " has no numeric value.");
        }
    }

    auto parse() -> AmlFile {
        if (std::size(m_tokens) == 0) {
            std::cerr << "[WARNING (pya2l.AMLParser)] Empty AML section - no tokens to parse." << std::endl;
            return {};
        }
        auto result = aml_file();
        if (m_error_count > 0) {
            std::cerr << "[WARNING (pya2l.AMLParser)] AML parsing completed with " << m_error_count << " error(s) - some definitions were skipped." << std::endl;
        }
        return result;
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
            try {
                if (token.type == AmlTokenType::BLOCK) {
                    decls.emplace_back(nullptr, std::make_shared<BlockDefinition>(block_definition()));
                } else {
                    decls.emplace_back(std::make_shared<TypeDefinition>(type_definition()), nullptr);
                }
            } catch (const std::runtime_error& e) {
                m_error_count++;
                std::cerr << "[WARNING (pya2l.AMLParser)] Skipping declaration: " << e.what() << std::endl;
                skip_to_next_member();
                continue;
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

        if (token.type == AmlTokenType::TAG) {
            std::string tag_value{};
            if (token.value && std::holds_alternative<std::string>(*token.value)) {
                tag_value = std::get<std::string>(*token.value);
            }
            throw std::runtime_error(
                "[ERROR (pya2l.AMLParser)] Unexpected TAG '" + tag_value +
                "' where a type name was expected at " + token_location(token)
            );
        }

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
            throw std::runtime_error(
                "[ERROR (pya2l.AMLParser)] Unexpected token '" + token_type_name(token.type) +
                "' - expected an AML type (struct/taggedstruct/taggedunion/enum/PDT) at " + token_location(token)
            );
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
                try {
                    members.emplace_back(struct_member());
                } catch (const std::runtime_error& e) {
                    m_error_count++;
                    std::cerr << "[WARNING (pya2l.AMLParser)] Skipping struct member: " << e.what() << std::endl;
                    skip_to_next_member();
                }
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
                try {
                    members.emplace_back(tagged_struct_member());
                } catch (const std::runtime_error& e) {
                    m_error_count++;
                    std::cerr << "[WARNING (pya2l.AMLParser)] Skipping tagged struct member: " << e.what() << std::endl;
                    skip_to_next_member();
                }
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
            throw std::runtime_error(
                "[ERROR (pya2l.AMLParser)] Missing required TAG in taggedstruct_definition - got '" +
                token_type_name(token.type) + "' at " + token_location(token)
            );
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
                try {
                    members.emplace_back(tagged_union_member());
                } catch (const std::runtime_error& e) {
                    m_error_count++;
                    std::cerr << "[WARNING (pya2l.AMLParser)] Skipping tagged union member: " << e.what() << std::endl;
                    skip_to_next_member();
                }
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
        } else {
            throw std::runtime_error(
                "[ERROR (pya2l.AMLParser)] Unexpected token '" + token_type_name(token.type) +
                "' in tagged_union_member - expected TAG or BLOCK at " + token_location(token)
            );
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
        auto                  token = current_token();
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

    void skip_to_next_member() {
        int brace_depth = 0;
        int paren_depth = 0;
        while (m_pos < std::size(m_tokens)) {
            auto& token = m_tokens[m_pos];
            if (token.type == AmlTokenType::LBRACE) {
                brace_depth++;
            } else if (token.type == AmlTokenType::RBRACE) {
                if (brace_depth == 0) {
                    return;  // End of containing block — don't consume
                }
                brace_depth--;
            } else if (token.type == AmlTokenType::LPARAN) {
                paren_depth++;
            } else if (token.type == AmlTokenType::RPARAN) {
                if (paren_depth > 0) {
                    paren_depth--;
                }
            } else if (token.type == AmlTokenType::SEMI && brace_depth == 0 && paren_depth == 0) {
                m_pos++;  // Consume the semicolon
                return;   // Ready for next member
            } else if (token.type == AmlTokenType::END && brace_depth == 0) {
                return;   // End of AML block
            }
            m_pos++;
        }
    }

    std::vector<AmlToken> m_tokens;
    std::size_t           m_pos;
    std::size_t           m_error_count;
};

// };   // namespace Aml

#endif  // __AML_PARSER_HPP
