#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <sstream>

#include "unmarshal.hpp"

namespace py = pybind11;

std::string parse(const std::string& aml_stuff);

auto unmarshal(const std::stringstream& inbuf) -> Node {
    auto unm    = Unmarshaller(inbuf);
    return unm.run();
}

PYBIND11_MODULE(amlparser_ext, m) {
    m.def("parse_aml", [](const std::string& aml_text) { return py::bytes(parse(aml_text)); }, py::return_value_policy::move);
	m.def("unmarshal", &unmarshal, py::return_value_policy::move);

	py::class_<Node>(m, "Node")
		.def(py::init<std::string_view>())
	;

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
