#include <iostream>

#include "amlLexer.h"
#include "aml_visitor.h"
#include "antlr4-runtime.h"

using namespace antlr4;

void marshal(std::stringstream& ss, const AmlFile& amlf);
void unmarshal(const std::stringstream& inbuf);

int main(int argc, const char* argv[]) {
    std::ifstream stream;

    if (argc == 2) {
        stream.open(argv[1]);
    } else {
        //stream.open("C:/csProjects/pyA2L/examples/xcp100.aml");
        stream.open("C:/csProjects/pyA2L/pya2l/examples/AML.tmp");
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
    auto       res = std::any_cast<AmlFile>(visitor.visitAmlFile(tree));

    std::stringstream ss;
    marshal(ss, res);
    // std::cout << ss.str();

    constexpr auto FNAME{ "aml_dump.bin" };

    std::ofstream outf(FNAME, std::ios::binary);
    outf << ss.str();
    outf.close();

    std::stringstream rbuf;
    std::ifstream     inf(FNAME, std::ios::binary);

    rbuf << inf.rdbuf();

    // std::string ppp = ;
    unmarshal(rbuf);

    inf.close();

    return 0;
}
