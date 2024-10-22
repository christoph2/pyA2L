#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <sstream>

#include "a2lparser.hpp"
#include "preprocessor.hpp"

namespace py = pybind11;

std::string ValueContainer::s_encoding{ "ascii" };

template<typename... Ts>
struct Overload : Ts... {
    using Ts::operator()...;
};

PYBIND11_MODULE(a2lparser_ext, m) {
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

    py::class_<A2LParser>(m, "A2LParser")
        .def(py::init<std::optional<preprocessor_result_t>, const std::string&, const std::string&>())
        .def("close", &A2LParser::close)
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
