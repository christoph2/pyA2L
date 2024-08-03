
#include <stack>

#include "a2llg.h"
#include "antlr4-runtime.h"
#include "ifdata.hpp"
#include "unmarshal.hpp"

using namespace antlr4;

Node load_grammar(const std::string& file_name) {
    std::ifstream aml_stream;
    aml_stream.open(file_name, std::ios_base::binary);
    std::stringstream aml_buffer;
    aml_buffer << aml_stream.rdbuf();
    return unmarshal(aml_buffer);
}

class IfDataParser {
   public:

    using token_t = std::optional<std::tuple<int, std::string>>;

    IfDataParser() = delete;

    explicit IfDataParser(const Node& root, const std::string& ifdata_section) : m_ifdata_section(ifdata_section), m_root(root) {
        m_grammar.push(&m_root);
        m_input = ANTLRInputStream(m_ifdata_section);
        m_lexer = std::make_unique<a2llg>(&m_input);
        consume();
    }

    void parse() {
        auto token = current_token();
        if (token) {
            auto [type, text] = *token;
            switch (type) {
                case a2llg::BEGIN:
                    consume();
                    block_type();
                    break;
                default:
                    std::cerr << "Unknown token type: " << type << std::endl;
            }
            parse();
        }
    }

    token_t next_token() {
        auto tok        = m_lexer->nextToken();
        auto token_type = tok->getType();
        if (token_type == antlr4::Lexer::EOF) {
            return std::nullopt;
        }
        return std::make_tuple<int, std::string>(token_type, tok->getText());
    }

    token_t current_token() {
        return m_current_token;
    }

    void consume() {
        m_current_token = next_token();
    }

    const Node* top() const noexcept {
        if (m_grammar.empty()) {
            std::cerr << "Stack is empty" << std::endl;
        }
        return m_grammar.top();
    }

    void block_type() {
        auto token = current_token();
        if (token) {
            auto [type, text] = *token;
            if (type == a2llg::IDENT) {
                const Node* blk = top()->find_block(text);
                if (blk) {
                    m_grammar.push(blk);
                }
                consume();
                const auto& [multiple, member, type] = blk->member_or_type();
                const auto& map                      = top()->map();
                auto        tk                       = current_token();
                if (type) {
                    m_grammar.push(*type);
                    switch ((*type)->aml_type()) {
                        case Node::AmlType::STRUCT:
                            struct_type();
                            break;
                        case Node::AmlType::TAGGED_STRUCT:
                            tagged_struct_type();
                            break;
                        case Node::AmlType::TAGGED_UNION:
                            tagged_union_type();
                            break;
                        case Node::AmlType::ENUMERATION:
                            enumeration_type();
                            break;
                        case Node::AmlType::PDT:
                            pdt_type();
                            break;
                        default:
                            std::cerr << "Unknown type: " << std::endl;
                            break;
                    }
                } else if (member) {
                    m_grammar.push(*member);
                }
                m_grammar.pop();
            }
        }
    }

    bool match(int token_type, const std::optional<std::string>& value = std::nullopt) {
#if 0
        def match(self, token_type, value = None) :
            ok = self.current_token.type == token_type
            token_value = self.value(self.current_token)
            self.consume()
            if value is None :
        return ok
            else:
        if not ok :
            return False
            return token_value == value
#endif
    }

    void struct_type() {
    }

    void tagged_struct_type() {
        auto token = current_token();
        if (token) {
            auto [tp, text] = *token;
            const auto tos = top();
            const auto& ts_members = tos->get_tagged_struct_members();
            const auto& [type, b0, b1] = ts_members.at(text);
        }
    }

    void tagged_union_type() {
        auto token = current_token();
        if (token) {
            auto [tp, text]   = *token;
            const auto member = top()->find_tag(text);
            const auto& [arr_spec, type] = member->get_type();
            m_grammar.push(type);
            consume();
            do_type();
            m_grammar.pop();
        }
    }

    void do_type() {
        const auto tos = top();
        switch (tos->aml_type()) {
            case Node::AmlType::STRUCT:
                struct_type();
                break;
            case Node::AmlType::TAGGED_STRUCT:
                tagged_struct_type();
                break;
            case Node::AmlType::TAGGED_UNION:
                tagged_union_type();
                break;
            case Node::AmlType::ENUMERATION:
                enumeration_type();
                break;
            case Node::AmlType::PDT:
                pdt_type();
                break;
            default:
                std::cerr << "Unknown type: " << std::endl;
                break;
            }
    }

    void enumeration_type() {
    }

    void pdt_type() {
    }

   private:

    const std::string       m_ifdata_section;
    ANTLRInputStream        m_input;
    const Node&             m_root;
    std::stack<const Node*> m_grammar{};
    std::unique_ptr<a2llg>  m_lexer;
    token_t                 m_current_token;
};

const std::string BASE{ "C:/csProjects/" };
//const std::string BASE{ ""C:/Users/HP/PycharmProjects/" };

int main() {
    std::ifstream stream;

    stream.open(BASE + "pyA2L/pya2l/examples/some_if_data.txt");

    ANTLRInputStream input(stream);

    auto ifd_lexer = a2llg(&input);

    auto root = load_grammar(BASE + "pyA2L/pya2l/examples/aml_dump.bin");

    std::string TEXT("/begin IF_DATA ETK\n"
                     "ADDRESS_MAPPING\n"
                     "0x10000\n"
                     "0x10000\n"
                     "0x1E8\n"
                     "/end IF_DATA");
    auto        lex = IfDataParser(root, TEXT);
    lex.parse();

    return 0;
}

#if 0
a2llg::IDENT
a2llg::FLOAT
a2llg::INT
a2llg::COMMENT
a2llg::WS
a2llg::STRING
a2llg::BEGIN
a2llg::END
#endif
