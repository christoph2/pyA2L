
#if !defined(__SYSCONSTS_HPP)
#define __SYSCONSTS_HPP

#include <cstdint>
#include <string>
#include <variant>
#include <vector>

#include "ctre.hpp"


using sys_const_variant_t = std::variant<std::monostate, std::int64_t, long double, std::string>;
using sys_const_t = std::tuple<std::string, sys_const_variant_t>;


static constexpr auto PAT_FLOAT = ctll::fixed_string{ "^[+\\-]?(\\d+([.]\\d*)?([eE][+\\-]?\\d+)?|[.]\\d+([eE][+\\-]?\\d+)?)" };
static constexpr auto PAT_INT = ctll::fixed_string{ "^(?:[+\\-])?[0-9]+$" };
static constexpr auto PAT_HEX = ctll::fixed_string{ "^0x[0-9a-fA-F]+$" };


std::vector<sys_const_t> process_sys_consts(const std::vector<std::tuple<std::string, std::string>>& constants) {
    std::vector<sys_const_t> result{};

    for (const auto& [name, value]: constants) {

        if (ctre::match<PAT_INT>(value)) {
            result.emplace_back(name, std::strtoll(value.c_str(), nullptr, 10));
        } else if (ctre::match<PAT_HEX>(value)) {
            result.emplace_back(name, std::strtoll(value.c_str(), nullptr, 16));
        } else if (ctre::match<PAT_FLOAT>(value)) {
            result.emplace_back(name, std::strtold(value.c_str(), nullptr));
        } else {
            result.emplace_back(name, value);
        }
    }
    return result;
}

#endif
