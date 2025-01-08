
#include "a2lparser.hpp"

#include <limits.h>

std::string ValueContainer::s_encoding{ "ascii" };

int main() {
    // const std::string FN{ "C:\\Users\\Chris\\PycharmProjects\\asamint\\asamint\\examples\\A2L.TMP" };
    const std::string FN{ "C:\\csProjects\\pyA2L\\pya2l\\examples\\A2L.TMP" };

    const std::string ENC{ "latin1" };
    auto parser = A2LParser(std::nullopt, FN, ENC);
    // parser.parse("C:\\csProjects\\pyA2L\\pya2l\\examples\\A2L.TMP", "latin1");

    const auto& tree = parser.get_values();
    const auto& tables = parser.get_tables();

    return 0;
}
