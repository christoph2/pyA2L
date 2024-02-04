
#include "a2lparser.hpp"

#include <limits.h>

std::string ValueContainer::s_encoding{ "ascii" };

int main() {
    std::cout << asam_int.valid_range() << std::endl;
    std::cout << asam_uint.valid_range() << std::endl;

    std::tuple<int, std::string, float> t1(10, "Test", 3.14);
    int                                 n  = 7;
    const auto                          t2 = std::tuple_cat(t1, std::make_tuple("Foo", "bar"), t1, std::tie(n));
    n                                      = 42;
    print(t2);

    auto parser = A2LParser();
    parser.parse("C:\\csProjects\\pyA2L\\pya2l\\examples\\A2L.TMP", "latin1");

    const auto& tree = parser.get_values();

    // std::cout << tree.to_string();

    const auto& tables = parser.get_tables();

    return 0;
}
