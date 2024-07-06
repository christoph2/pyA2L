#include <iostream>

#include "amlLexer.h"
#include "aml_visitor.h"
#include "antlr4-runtime.h"

using namespace antlr4;

void marshal(std::stringstream& ss, const AmlFile& amlf);

std::string parse(const std::string& aml_stuff) {
    ANTLRInputStream input(aml_stuff);

    amlLexer          lexer(&input);
    CommonTokenStream tokens(&lexer);

    amlParser                  parser(&tokens);
    amlParser::AmlFileContext* tree = parser.amlFile();

    AmlVisitor visitor;
    auto       res = std::any_cast<AmlFile>(visitor.visitAmlFile(tree));

    std::stringstream ss;
    marshal(ss, res);

    return ss.str();
}
