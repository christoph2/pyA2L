
#include "a2llg.h"
#include "antlr4-runtime.h"
#include "ifdata.hpp"
#include "unmarshal.hpp"

using namespace antlr4;

int main() {
    std::ifstream stream;

#if 0
    if (argc == 2) {
        stream.open(argv[1]);
    }
    else {
        // stream.open("C:/csProjects/pyA2L/examples/xcp100.aml");
        stream.open("C:/Users/HP/PycharmProjects/pyA2L/pya2l/examples/AML.tmp");
    }
#endif

    std::ifstream aml_stream;
    aml_stream.open("C:/Users/HP/PycharmProjects/pyA2L/pya2l/examples/aml_dump.bin", std::ios_base::binary);
    std::stringstream aml_buffer;

    aml_buffer << aml_stream.rdbuf();

    auto umm = unmarshal(aml_buffer);

    stream.open("C:/Users/HP/PycharmProjects/pyA2L/pya2l/examples/some_if_data.txt");

    ANTLRInputStream input(stream);

    auto ifd_lexer = a2llg(&input);

    auto tk = ifd_lexer.getAllTokens();
    for (const auto& tok : tk) {
        auto tp = tok->getType();
        std::cout << tok->getText() << " : " << tp << std::endl;
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
