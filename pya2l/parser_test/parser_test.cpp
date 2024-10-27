

#include <filesystem>
#include <fstream>

#include "a2lparser.hpp"
#include "preprocessor.hpp"

std::string ValueContainer::s_encoding{ "latin1" };

void process(const std::string& file_name, const std::string& encoding) {
    Preprocessor p{ "INFO" };

    auto res                   = p.process(file_name, encoding);
    auto& [fns, linemap, ifdr] = res;
    p.finalize();
    auto        parser = A2LParser(res, fns.a2l, encoding);
    const auto& values = parser.get_values();
}

int main(int argc, char** argv) {
    for (auto const & dir_entry : std::filesystem::directory_iterator{ "..\\..\\examples" }) {
        auto pth = dir_entry.path();
        auto ext = pth.extension();
        if (ext != ".a2l") {
            continue;
        }
        std::cout << pth << '\n';
        process(pth.string(), "latin1");
    }
    return 0;
}
