#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/complex.h>

#include <pybind11/attr.h>
#include <pybind11/iostream.h>
#include <pybind11/numpy.h>

#include <sstream>

#include "unmarshal.hpp"
//#include "ifdata_lexer.hpp"

namespace py = pybind11;

std::string parse(const std::string& aml_stuff);


Node unmarshal(const py::bytes& data) {
	std::stringstream inbuf{data};
    auto unm    = Unmarshaller(inbuf);
    return unm.run();
}

inline auto unicode_decode(std::string_view value, const char * encoding) -> py::str {
	py::handle py_s = PyUnicode_Decode(value.data(), value.length(), encoding, "strict");
    if (!py_s) {
		throw py::error_already_set();
    }
    return py::reinterpret_steal<py::str>(py_s);
}

PYBIND11_MODULE(amlparser_ext, m) {
    // m.def("parse_aml", [](const std::string& aml_text) {
	// 	return py::bytes(parse(aml_text));
	// }, py::return_value_policy::move);

	m.def("unmarshal", &unmarshal, py::return_value_policy::move);
	//m.def("ifdata_lexer", &ifdata_lexer, py::return_value_policy::move);

	py::class_<Node>(m, "Node")
		.def(py::init<>())
		.def_property_readonly("value", &Node::value)
		.def_property_readonly("list", &Node::list)
		.def_property_readonly("map", &Node::map)
		.def_property_readonly("aml_type", &Node::aml_type)
		.def_property_readonly("node_type", &Node::node_type)
		.def_property_readonly("content", &Node::get_content)
		.def("find_block", &Node::find_block)
		.def("member_or_type", &Node::member_or_type)
		.def("find_tag", &Node::find_tag)
		.def_property_readonly("tag", &Node::get_tag)
		.def_property_readonly("multiple", &Node::is_multiple)
		.def_property_readonly("type", &Node::get_type)
		.def_property_readonly("members", &Node::get_members)
		.def_property_readonly("tagged_struct_members", &Node::get_tagged_struct_members)
	;

	py::enum_<Node::NodeType>(m, "NodeType")
		.value("TERMINAL", Node::NodeType::TERMINAL)
		.value("MAP", Node::NodeType::MAP)
		.value("AGGR", Node::NodeType::AGGR)
		.value("NONE", Node::NodeType::NONE)
	;

	py::enum_<Node::AmlType>(m, "AmlType")
		.value("NONE", Node::AmlType::NONE)
		.value("TYPE", Node::AmlType::TYPE)
		.value("TERMINAL", Node::AmlType::TERMINAL)
		.value("BLOCK", Node::AmlType::BLOCK)
		.value("BLOCK_INTERN", Node::AmlType::BLOCK_INTERN)
		.value("ENUMERATION", Node::AmlType::ENUMERATION)
		.value("ENUMERATOR", Node::AmlType::ENUMERATOR)
		.value("ENUMERATORS", Node::AmlType::ENUMERATORS)
		.value("MEMBER", Node::AmlType::MEMBER)
		.value("MEMBERS", Node::AmlType::MEMBERS)
		.value("PDT", Node::AmlType::PDT)
		.value("REFERRER", Node::AmlType::REFERRER)
		.value("ROOT", Node::AmlType::ROOT)
		.value("STRUCT", Node::AmlType::STRUCT)
		.value("STRUCT_MEMBER", Node::AmlType::STRUCT_MEMBER)
		.value("TAGGED_STRUCT", Node::AmlType::TAGGED_STRUCT)
		.value("TAGGED_STRUCT_DEFINITION", Node::AmlType::TAGGED_STRUCT_DEFINITION)
		.value("TAGGED_STRUCT_MEMBER", Node::AmlType::TAGGED_STRUCT_MEMBER)
		.value("TAGGED_UNION", Node::AmlType::TAGGED_UNION)
		.value("TAGGED_UNION_MEMBER", Node::AmlType::TAGGED_UNION_MEMBER)
	;
}
