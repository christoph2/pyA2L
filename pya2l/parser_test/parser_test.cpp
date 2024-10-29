

#include <filesystem>
#include <fstream>
#include <chrono>

#include "a2lparser.hpp"
#include "preprocessor.hpp"

std::string ValueContainer::s_encoding{ "latin1" };

auto process(const std::string& file_name, const std::string& encoding) -> std::tuple<std::size_t, const ValueContainer> {
    Preprocessor p{ "INFO" };

    std::chrono::steady_clock::time_point start1 = std::chrono::steady_clock::now();
    auto res                   = p.process(file_name, encoding);
    auto& [fns, linemap, ifdr] = res;
    p.finalize();
    std::chrono::steady_clock::time_point stop1 = std::chrono::steady_clock::now();
    std::cout << "[Info (pya2l.Preprocessor)]  Elapsed Time: " << (std::chrono::duration_cast<std::chrono::milliseconds>(stop1 - start1).count()) / 1000.0 << "[s]"  << std::endl;

    std::cout << "[Info (pya2l.A2LParser)]     Parsing intermediate file: " << fns.a2l << std::endl;
    std::chrono::steady_clock::time_point start2 = std::chrono::steady_clock::now();
    auto        parser = A2LParser(res, fns.a2l, encoding);
    auto counter = parser.get_keyword_counter();
    const auto& values = parser.get_values();
    std::chrono::steady_clock::time_point stop2 = std::chrono::steady_clock::now();
    std::cout << "[Info (pya2l.A2LParser)]     Elapsed Time: " << (std::chrono::duration_cast<std::chrono::milliseconds>(stop2 - start2).count()) / 1000.0 << "[s]"  << std::endl;
    std::cout << "[Info (pya2l.A2LParser)]     Number of keywords: " << counter << std::endl;

    return {counter, values};
}

int main(int argc, char** argv) {
    for (auto const & dir_entry : std::filesystem::directory_iterator{ "..\\..\\examples" }) {
        auto pth = dir_entry.path();
        auto ext = pth.extension();
        if (ext != ".a2l") {
            continue;
        }
        auto [counter, values] = process(pth.string(), "latin1");
        std::cout << std::endl;
    }
    return 0;
}
