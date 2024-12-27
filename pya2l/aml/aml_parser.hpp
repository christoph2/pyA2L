

#if !defined(__AML_PARSER_HPP)
#define __AML_PARSER_HPP

#include "klasses.hpp"

class AMLParser {
public:

    explicit AMLParser(const std::vector<Token>& tokens) : m_tokens(tokens), m_pos(0) {        

    }

    const Token& current_token() const noexcept {
        return m_tokens[m_pos];
    }

    const Token& la(std::size_t offs) const noexcept {
        return m_tokens[m_pos + offs];
    }


    void consume() noexcept {
        m_pos++;
    }

    bool expect(TokenType type, TokenDataType value = std::nullopt) {
        auto token = current_token();
        if (type != token.type) {
            std::cerr << "Invalid token type!!!\n";
            return false;
        }
        if (value && token.value) {
            if (*value != *token.value) {
                std::cerr << "Unexpected token value!!!\n";
                return false;
            }
        }
        return true;
    }

    void match(TokenType type, bool consume_token=true) {
        if (!expect(type)) {
            throw std::runtime_error("Invalid token type.");
        }
        if (consume_token) {
            consume();
        }
    }

    auto match_get_value(TokenType type, bool consume_token = true) -> TokenDataType {
        if (!expect(type)) {
            throw std::runtime_error("Invalid token type.");
        }
        auto value = current_token().value;

        if (consume_token) {
            consume();
        }
        return value;
    }



    void parse() {
        aml_file();
    }

    void aml_file() {
        auto r1 = expect(TokenType::BEGIN);
        consume();
        auto t1 = current_token();
        auto r2 = expect(TokenType::IDENT, "A2ML");
        consume();        
        declaration();
        match(TokenType::END);
        auto value = match_get_value(TokenType::IDENT);

    }

    void declaration() {
        while (true) {
            auto token = current_token();
            if (token.type == TokenType::END) {
                break;
            }
            if (token.type == TokenType::BLOCK) {
                block_definition();
            }
            else {
                type_definition();
            }
            token = current_token(); 
            if (token.type == TokenType::SEMI) {
                match(TokenType::SEMI);
            }
        }        
    }

    void type_definition() {
        type_name();
    }

    void type_name() {

        auto token = current_token();

        if (token.type == TokenType::STRUCT) {
            struct_type_name();
        } else if(token.type == TokenType::TAGGED_STRUCT) {
            taggedstruct_type_name();
        } else if (token.type == TokenType::TAGGED_UNION) {
            taggedunion_type_name();
        } else if (token.type == TokenType::PDT) {
            predefined_type_name();
        } else if (token.type == TokenType::ENUM) {
            enum_type_name();
        }
        else {
            throw std::runtime_error("NO type...\n");
        }
    }

    void predefined_type_name() {
        auto value = match_get_value(TokenType::PDT);
       // match(TokenType::SEMI);
    }

    void block_definition() {
        bool multiple{ false };
        match(TokenType::BLOCK);
        auto tag = match_get_value(TokenType::TAG);

        auto token = current_token();
        if (token.type == TokenType::LPARAN) {
            match(TokenType::LPARAN);
            multiple = true;
            token = current_token();
        }

        type_name();
        token = current_token();
        if (token.type == TokenType::LSQ) {
            while (true) {
                array_specifier();
                token = current_token();
                if (token.type != TokenType::LSQ) {
                    break;
                }
            }
        }

        if (multiple) {
            match(TokenType::RPARAN);
            match(TokenType::STAR);
        }
    }

    void struct_type_name() {
        match(TokenType::STRUCT);
        auto token = current_token();
        if (token.type == TokenType::IDENT) {
            auto value = match_get_value(TokenType::IDENT);
            token = current_token();
        }
        if (token.type == TokenType::LBRACE) {
            match(TokenType::LBRACE);
            while (true) {                
                struct_member();    // rep!!!
                token = current_token();
                if (token.type == TokenType::RBRACE) {
                    break;
                }
            }
            match(TokenType::RBRACE);
        }
    }

    void struct_member() {
        auto token = current_token();
        if (token.type == TokenType::RBRACE) {
            return; // Empty.
        }
        member();
        token = current_token();
        if (token.type == TokenType::SEMI) {
            consume();  // Optional ';'
        }
    }

    void taggedstruct_type_name() {
        match(TokenType::TAGGED_STRUCT);
        auto token = current_token();
        if (token.type == TokenType::IDENT) {
            auto value = match_get_value(TokenType::IDENT);
            token = current_token();
        }
        if (token.type == TokenType::LBRACE) {
            match(TokenType::LBRACE);                        
            while (true) {
                tagged_struct_member();
                token = current_token();
                if (token.type == TokenType::RBRACE) {
                    break;
                }
            }
            match(TokenType::RBRACE);
        }
        token = current_token();
        if (token.type == TokenType::SEMI) {
            consume();  // Optional ';'
        }
    }

    void tagged_struct_member() {
        bool multiple{ false };
        auto token = current_token();

        if (token.type == TokenType::LPARAN) {
            match(TokenType::LPARAN);
            multiple = true;            
            token = current_token();
        }
        if (token.type == TokenType::BLOCK) {
            block_definition();
        }
        else {
            taggedstruct_definition();
        }
        if (multiple) {
            std::cout << "multiple\n";
            match(TokenType::RPARAN);
            match(TokenType::STAR);
        }
        token = current_token();
        if (token.type == TokenType::SEMI) {
            match(TokenType::SEMI);
        }
    }

    void taggedstruct_definition() {
        bool multiple{ false };
        auto tag = match_get_value(TokenType::TAG);

        auto token = current_token();
        if (token.type == TokenType::LPARAN) {
            match(TokenType::LPARAN);
            multiple = true;
        }
        // TODO: check empty, i.e SEMI!!!
        if (token.type == TokenType::SEMI) {
            if (multiple) {
                throw std::runtime_error("Did not expect empty taggedstruct_definition with multiple");
            }
        }
        else {
            member();
            token = current_token();
            if (token.type == TokenType::SEMI) {
                match(TokenType::SEMI);
            }
            if (multiple) {
                match(TokenType::RPARAN);
                match(TokenType::STAR);

            }
        }
    }

    void taggedunion_type_name() {
        match(TokenType::TAGGED_UNION);
        auto token = current_token();
        if (token.type == TokenType::IDENT) {
            auto value = match_get_value(TokenType::IDENT);
            token = current_token();
        }
        if (token.type == TokenType::LBRACE) {
            match(TokenType::LBRACE);
            while (true) {
                tagged_union_member();
                token = current_token();
                if (token.type == TokenType::RBRACE) {
                    break;
                }
            }
            match(TokenType::RBRACE);
        }
        else {
            // Referrer
        }
    }

    void tagged_union_member() {
        auto token = current_token();
        if (token.type == TokenType::TAG) {
            auto tag = match_get_value(TokenType::TAG);
            member();
        }
        else if (token.type == TokenType::BLOCK) {
            block_definition();
        } else if (token.type == TokenType::SEMI) {
            match(TokenType::SEMI);
            token = current_token();
            std::cout << "TAG only.\n";
        }
        else {
            std::cerr << "Error!!!\n";
        }
    }

    void enum_type_name() {
        match(TokenType::ENUM);
        auto token = current_token();
        if (token.type == TokenType::IDENT) {
            auto value = match_get_value(TokenType::IDENT);
            token = current_token();
        }
        if (token.type == TokenType::LBRACE) {
            match(TokenType::LBRACE);
            while (true) {
                enumerator_list();
                token = current_token();
                if (token.type == TokenType::RBRACE) {
                    break;
                }
            }
            match(TokenType::RBRACE);
        }
    }

    auto enumerator_list() -> std::vector<Enumerator> {
        std::vector<Enumerator> result;
        while (true) {
            result.emplace_back(enumerator());
            auto token = current_token();
            if (token.type != TokenType::COLON) {
                break;
            }
            match(TokenType::COLON);
        }
        return result;
    }

    auto enumerator() -> Enumerator {
        std::optional<numeric_t> value;
        auto tag_r = match_get_value(TokenType::TAG);
        auto tag = std::get<std::string>(*tag_r);
        auto token = current_token();

        if (token.type == TokenType::EQU) {
            match(TokenType::EQU);
            token = current_token();
            value = std::get<long long int>(*token.value);
            consume();
        }
        return Enumerator(tag, value);
    }


    void member() {
        auto token = current_token();

        if (token.type == TokenType::BLOCK) {
            block_definition();
        }
        else {
            type_name();
            token = current_token();
            if (token.type == TokenType::LSQ) {
                while (true) {
                    array_specifier();
                    token = current_token();
                    if (token.type == TokenType::SEMI) {
                        break;
                    }
                }
                match(TokenType::SEMI);
            }
        }
    }

    void array_specifier() {
        match(TokenType::LSQ);
        auto token = current_token();
        auto value = token.value;   // numeric
        consume();
        match(TokenType::RSQ);
    }

#if 0
    amlFile:
    '/begin' 'A2ML'
        (d += declaration) *
        '/end' 'A2ML'
        ;

declaration:
    (t = type_definition ';')
        | (b = block_definition ';')
        ;

type_definition:
    type_name
        ;

type_name:
    pr = predefined_type_name
        | st = struct_type_name
        | ts = taggedstruct_type_name
        | tu = taggedunion_type_name
        | en = enum_type_name
        ;

predefined_type_name:
    (
      name = 'char'
    | name = 'int'
    | name = 'long'
    | name = 'uchar'
    | name = 'uint'
    | name = 'ulong'
    | name = 'int64'
    | name = 'uint64'
    | name = 'double'
    | name = 'float'
    )
        ;
#endif

private:
    std::vector<Token> m_tokens;
    std::size_t m_pos;
};


#endif // __AML_PARSER_HPP
