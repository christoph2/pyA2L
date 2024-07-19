
#include "a2llg.h"
#include "antlr4-runtime.h"
#include "ifdata.hpp"

using namespace antlr4;

int main() {
    std::ifstream stream;

#if 0
    if (argc == 2) {
        stream.open(argv[1]);
    }
    else {
        // stream.open("C:/csProjects/pyA2L/examples/xcp100.aml");
        stream.open("C:/csProjects/pyA2L/pya2l/examples/AML.tmp");
    }
#endif

    stream.open("C:\\csProjects\\pyA2L\\pya2l\\examples\\some_if_data.txt");

    ANTLRInputStream input(stream);

    auto ifd_lexer = a2llg(&input);

    auto tk = ifd_lexer.getAllTokens();
    for (const auto& tok : tk) {
        auto tp = tok->getType();
        std::cout << tok->getText() << " : " << tp << std::endl;
    }

    return 0;
}
