#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

//#include <iostream>
#include <sstream>

#include "a2lparser.hpp"

namespace py = pybind11;

std::string ValueContainer::s_encoding{ "ascii" };

template<typename... Ts>
struct Overload : Ts... {
    using Ts::operator()...;
};

#if 0
auto ItemGetter = Overload {
	[](const std::string& elem) {
		auto raw_value = std::get<std::string>(elem);

		py::handle py_s = PyUnicode_Decode(raw_value.data(), raw_value.length(), ValueContainer::get_encoding().c_str(), "strict");
		if (!py_s) {
			throw py::error_already_set();
		}
		return py::reinterpret_steal<py::str>(py_s);
	},
	[](const unsigned long long& elem) { return elem; },
	[](const signed long long& elem) { return elem; },
	[](const long double& elem) { return elem; },
	[](auto elem) {
		return elem;
	},
};
#endif

PYBIND11_MODULE(a2lparser_ext, m) {
    py::class_<ValueContainer>(m, "ValueContainer")
        .def(py::init<std::string_view>(), py::arg("name"))
        .def("get_name", &ValueContainer::get_name)
        .def("get_keywords", &ValueContainer::get_keywords)
        .def("get_parameters", &ValueContainer::get_parameters)
        .def_property_readonly("parameters", [](const ValueContainer& self) {
            py::list result;

            auto encoding = ValueContainer::get_encoding().c_str();

            auto ItemGetter = Overload{

                [&result, encoding](std::string value) {
                    py::handle py_s = PyUnicode_Decode(value.data(), value.length(), encoding, "strict");
                    if (!py_s) {
                        throw py::error_already_set();
                    }
                    result.append(py::reinterpret_steal<py::str>(py_s));
                },
                [&result](auto value) { result.append(value); },

            };

            for (const auto& elem : self.get_parameters()) {
#if 0
					if (std::holds_alternative<std::string>(elem)) {
						auto raw_value = std::get<std::string>(elem);

						py::handle py_s = PyUnicode_Decode(raw_value.data(), raw_value.length(), ValueContainer::get_encoding().c_str(), "strict");
						if (!py_s) {
							throw py::error_already_set();
						}
						result.append(py::reinterpret_steal<py::str>(py_s));
					} else if (std::holds_alternative<unsigned long long>(elem)) {
						result.append(std::get<unsigned long long>(elem));
					} else if (std::holds_alternative<signed long long>(elem)) {
						result.append(std::get<signed long long>(elem));
					} else if (std::holds_alternative<long double>(elem)) {
						result.append(std::get<long double>(elem));
					}
#endif
                std::visit(ItemGetter, elem);
            }
            return result;
        });

    py::class_<A2LParser>(m, "A2LParser")
        .def(py::init<>())
        .def("parse", &A2LParser::parse)
        .def("get_values", &A2LParser::get_values, py::return_value_policy::move)
        .def("get_tables", &A2LParser::get_tables, py::return_value_policy::move)
        .def_property_readonly("keyword_counter", &A2LParser::get_keyword_counter);
}

#if 0
m.def("return_bytes",
    []() {
        std::string s("\xba\xd0\xba\xd0");  // Not valid UTF-8
        return py::bytes(s);  // Return the data without transcoding
    }
);
#endif
