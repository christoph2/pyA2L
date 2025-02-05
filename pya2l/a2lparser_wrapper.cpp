#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <sstream>

#include "a2lparser.hpp"
#include "parser.hpp"
#include "preprocessor.hpp"
#include "sysconsts.hpp"

namespace py = pybind11;

std::string ValueContainer::s_encoding{ "ascii" };


auto convert_loglevel(const std::string& level) -> spdlog::level::level_enum {
    spdlog::level::level_enum result = spdlog::level::level_enum::warn;

	if (level == "CRITICAL") {
		result = spdlog::level::critical;
	} else if (level == "FATAL") {
		result = spdlog::level::critical;
	} else if (level == "ERROR") {
		result = spdlog::level::err;
	} else if (level == "WARN") {
		result = spdlog::level::warn;
	} else if (level == "WARNING") {
		result = spdlog::level::warn;
	} else if (level == "INFO") {
		result = spdlog::level::info;
	} else if (level == "DEBUG") {
		result = spdlog::level::debug;
	}
	return result;
}


inline auto unicode_decode(std::string_view value, const char * encoding) -> py::str {
	py::handle py_s = PyUnicode_Decode(value.data(), value.length(), encoding, "strict");
    if (!py_s) {
		throw py::error_already_set();
    }
    return py::reinterpret_steal<py::str>(py_s);
}

auto parse(const std::string& file_name, const std::string& encoding, const std::string& log_level) -> std::tuple<std::size_t, const ValueContainer, const std::vector<A2LParser::value_table_t>, AmlData> {
	auto logger = create_logger("a2l", convert_loglevel(log_level));
	Preprocessor p{ convert_loglevel(log_level) };
	std::vector<A2LParser::value_table_t> converted_tables{};

    std::chrono::steady_clock::time_point start1 = std::chrono::steady_clock::now();
    const auto res                   = p.process(file_name, encoding);
    const auto [fns, linemap, ifdr] = res;
    p.finalize();
    std::chrono::steady_clock::time_point stop1 = std::chrono::steady_clock::now();
    logger->info("Elapsed Time: {}[s]", (std::chrono::duration_cast<std::chrono::milliseconds>(stop1 - start1).count()) / 1000.0);

    std::chrono::steady_clock::time_point start2 = std::chrono::steady_clock::now();
	logger->info("Start parsing...");
    const auto&        parser = A2LParser(res, fns.a2l, encoding, convert_loglevel(log_level));
    auto counter = parser.get_keyword_counter();
    const auto& values = parser.get_values();
    std::chrono::steady_clock::time_point stop2 = std::chrono::steady_clock::now();
    logger->info("Elapsed Time: {}[s]", (std::chrono::duration_cast<std::chrono::milliseconds>(stop2 - start2).count()) / 1000.0);
    logger->info("Number of keywords: {}", counter);
	const auto& tables = parser.get_tables();
	for (const auto&[tp, name, rows]: tables) {
		const auto& tpt = unicode_decode(tp, encoding.c_str());
		const auto& namet = unicode_decode(name, encoding.c_str());
		std::vector<std::vector<AsamVariantType>> result;
		for (const auto& row: rows) {
			std::vector<AsamVariantType> fixed_row;
			for (const auto& column: row) {
				if (std::holds_alternative<std::string>(column)) {
					fixed_row.emplace_back(unicode_decode(std::get<std::string>(column), encoding.c_str()));
				} else {
					fixed_row.emplace_back(column);
				}
			}
			result.emplace_back(fixed_row);
		}
		converted_tables.emplace_back(tpt, namet, result);
	}
	auto aml_data = parse_aml(fns.aml);
    return {counter, values, converted_tables, aml_data};
}

template<typename... Ts>
struct Overload : Ts... {
    using Ts::operator()...;
};


PYBIND11_MODULE(a2lparser_ext, m) {
    m.def("parse", &parse, py::return_value_policy::move);
    m.def("process_sys_consts", &process_sys_consts, py::return_value_policy::move);

    py::class_<AmlData>(m, "AmlData")
        .def(py::init<const std::string&, const std::string&>())
        .def_property_readonly("text", &AmlData::get_text)
        .def_property_readonly("parsed", [](const AmlData& self) {
            return py::bytes(self.parsed);
        })
    ;

    py::class_<ValueContainer>(m, "ValueContainer")
        .def(py::init<std::string_view>(), py::arg("name"))
        .def("get_name", &ValueContainer::get_name)
        .def("get_keywords", &ValueContainer::get_keywords)
        .def("get_parameters", &ValueContainer::get_parameters)
        .def("get_multiple_values", &ValueContainer::get_multiple_values)
        .def("get_if_data", &ValueContainer::get_if_data)
        .def_property_readonly(
            "if_data",
            [](const ValueContainer& self) {
                auto        encoding = ValueContainer::get_encoding().c_str();
                std::string value;
                auto        if_data = self.get_if_data();

                if (if_data) {
                    py::handle py_s = PyUnicode_Decode((*if_data).data(), (*if_data).length(), encoding, "strict");

                    if (!py_s) {
                        throw py::error_already_set();
                    }

                    return py::reinterpret_steal<py::str>(py_s);
                } else {
                    return py::str{ "" };
                }
            }
        )
        .def_property_readonly("parameters", [](const ValueContainer& self) {
            py::list result;

            auto encoding = ValueContainer::get_encoding().c_str();
#if !defined(__APPLE__)
            auto ItemGetter = Overload{

                [&result, encoding](const std::string& value) {
                    py::handle py_s = PyUnicode_Decode(value.data(), value.length(), encoding, "strict");
                    if (!py_s) {
                        throw py::error_already_set();
                    }
                    result.append(py::reinterpret_steal<py::str>(py_s));
                },
                [&result](auto value) { result.append(value); },
            };
#endif
            for (const auto& value : self.get_parameters()) {
#if defined(__APPLE__)
                if (std::holds_alternative<std::string>(value)) {
                    auto raw_value = std::get<std::string>(value);

                    py::handle py_s = PyUnicode_Decode(raw_value.data(), raw_value.length(), encoding, "strict");
                    if (!py_s) {
                        throw py::error_already_set();
                    }
                    result.append(py::reinterpret_steal<py::str>(py_s));
                } else if (std::holds_alternative<unsigned long long>(value)) {
                    result.append(std::get<unsigned long long>(value));
                } else if (std::holds_alternative<signed long long>(value)) {
                    result.append(std::get<signed long long>(value));
                } else if (std::holds_alternative<long double>(value)) {
                    result.append(std::get<long double>(value));
                }
#else
                std::visit(ItemGetter, value);
#endif
            }
            return result;
        });
}
