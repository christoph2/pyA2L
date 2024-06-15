#include <iostream>

#include "antlr4-runtime.h"
#include "amlLexer.h"
#include "amlParser.h"

#include "aml_visitor.h"

using namespace std;
using namespace antlr4;

int main(int argc, const char* argv[]) {
	std::ifstream stream;
    stream.open("C:/Users/HP/PycharmProjects/pyA2L/examples/ASAP2_Demo_V161.aml");


    ANTLRInputStream input(stream);

    pya2l::amlLexer lexer(&input);
    CommonTokenStream tokens(&lexer);
#if 0
    while (tokens.LA(1) != Token::EOF) {
        auto tk = tokens.LT(1);
        std::cout << tk->toString() << std::endl;
        tokens.consume();
    }
#endif

    pya2l::amlParser parser(&tokens);
    pya2l::amlParser::AmlFileContext * tree = parser.amlFile();

    AmlVisitor visitor;
    auto res = visitor.visitAmlFile(tree);

	return 0;
}
