
#include <stack>

#include "a2llg.h"
#include "antlr4-runtime.h"
#include "ifdata.hpp"
#include "unmarshal.hpp"

using namespace antlr4;

Root load_grammar(const std::string& file_name) {
    std::ifstream aml_stream;
    aml_stream.open(file_name, std::ios_base::binary);
    std::stringstream aml_buffer;
    aml_buffer << aml_stream.rdbuf();
    return unmarshal(aml_buffer);
}

class IfDataParser {
   public:

    explicit IfDataParser(Root& root) : m_root(root) {
        // m_grammar.push(&m_root);
    }

    void parse(const std::string& section) {
        std::cout << "Parsing section: " << section << std::endl;
    }

    // find_node -- type
    const Node* find_block(const std::string& tag) {
        // auto mr = m_grammar.top();
        //  auto root  = dynamic_cast<Root*>(mr);
        auto root  = &m_root;
        auto nodes = root->nodes();

        for (auto& node : nodes) {
            auto idx = node.index();
            if (std::holds_alternative<Block>(node)) {
                auto block = std::get<Block>(node);
            }
#if 0
            if ((node.type() == Node::NodeType::BLOCK)) {
                auto res = node.find(tag);
                if (res != nullptr) {
                    return res;
                }
                Block* block = (Block*)&node;
                auto   res2  = block->find(tag);
            }
#endif
        }
        return nullptr;
    }

   private:

    Root&                    m_root;
    std::stack<NodeVariant*> m_grammar{};
};

int main() {
    std::ifstream stream;

    stream.open("C:/Users/HP/PycharmProjects/pyA2L/pya2l/examples/some_if_data.txt");

    ANTLRInputStream input(stream);

    auto ifd_lexer = a2llg(&input);

    // std::stack<Node*> gram;
    // gram.push(&root);

    auto root   = load_grammar("C:/Users/HP/PycharmProjects/pyA2L/pya2l/examples/aml_dump.bin");
    auto parser = IfDataParser(root);
    parser.parse("/begin IF_DATA ETK\n"
                 "ADDRESS_MAPPING\n"
                 "0x10000\n"
                 "0x10000\n"
                 "0x1E8\n"
                 "/end IF_DATA");
    parser.find_block("IF_DATA");
    while (true) {
        auto tok = ifd_lexer.nextToken();
        auto tp  = tok->getType();
        std::cout << tok->getText() << " : " << tp << std::endl;
        if (tok->getType() == antlr4::Lexer::EOF) {
            break;
        }
        if (tok->getType() == a2llg::BEGIN) {
            auto name = ifd_lexer.nextToken();
            std::cout << name->getText() << " : " << name->getType() << std::endl;
            if (name->getType() == a2llg::IDENT) {
                // auto top = gram.top();
                //  top->
            }
        }
    }

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
