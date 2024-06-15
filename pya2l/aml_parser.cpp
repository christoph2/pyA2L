#include <iostream>

#include "antlr4-runtime.h"
#include "aml_visitor.h"
#include "amlLexer.h"


using namespace antlr4;

int main(int argc, const char* argv[]) {
	std::ifstream stream;

    if (argc == 2) {
        stream.open(argv[1]);
    } else {
        stream.open("C:/csProjects/pyA2L/examples/ASAP2_Demo_V161.aml");
    }

    ANTLRInputStream input(stream);

    amlLexer lexer(&input);
    CommonTokenStream tokens(&lexer);
#if 0
    while (tokens.LA(1) != Token::EOF) {
        auto tk = tokens.LT(1);
        std::cout << tk->toString() << std::endl;
        tokens.consume();
    }
#endif

    amlParser parser(&tokens);
    amlParser::AmlFileContext * tree = parser.amlFile();

    AmlVisitor visitor;
    auto res = visitor.visitAmlFile(tree);

	return 0;
}
