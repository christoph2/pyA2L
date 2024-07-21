#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <sstream>

namespace py = pybind11;

std::string parse(const std::string& aml_stuff);

PYBIND11_MODULE(amlparser_ext, m) {
    m.def("parse_aml", [](const std::string& aml_text) { return py::bytes(parse(aml_text)); });

#if 0
    py::class_<ValueContainer>(m, "ValueContainer")
        .def(py::init<std::string_view>(), py::arg("name"))
        .def("get_name", &ValueContainer::get_name)
        .def("get_keywords", &ValueContainer::get_keywords)
        .def("get_parameters", &ValueContainer::get_parameters)
        .def("get_multiple_values", &ValueContainer::get_multiple_values)
        .def("get_if_data", &ValueContainer::get_if_data)
#endif
};
