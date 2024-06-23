#include <iostream>

#include "amlLexer.h"
#include "aml_visitor.h"
#include "antlr4-runtime.h"

using namespace antlr4;

int main(int argc, const char* argv[]) {
    std::ifstream stream;

    if (argc == 2) {
        stream.open(argv[1]);
    } else {
        stream.open("C:/csProjects/pyA2L/examples/xcp100.aml");
    }

    ANTLRInputStream input(stream);

    amlLexer          lexer(&input);
    CommonTokenStream tokens(&lexer);
#if 0
    while (tokens.LA(1) != Token::EOF) {
        auto tk = tokens.LT(1);
        std::cout << tk->toString() << std::endl;
        tokens.consume();
    }
#endif

    amlParser                  parser(&tokens);
    amlParser::AmlFileContext* tree = parser.amlFile();

    AmlVisitor visitor;
    auto       res = visitor.visitAmlFile(tree);

    return 0;
}
