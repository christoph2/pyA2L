
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "token_stream.hpp"

namespace py = pybind11;

PYBIND11_MODULE(tokenstream, m) {
  py::class_<TokenReader>(m, "TokenReader")
      .def(py::init<const std::string &>())
      .def("LA", &TokenReader::LA, py::arg("k"))
      .def("LT", &TokenReader::LT, py::arg("i"))
      .def("seek", &TokenReader::seek, py::arg("index"))
      .def_property_readonly("index", &TokenReader::getIndex)
      .def("consume", &TokenReader::consume)
      .def("mark", &TokenReader::mark)
      .def("release", &TokenReader::release, py::arg("marker"))
      //		.def_readwrite("tokens", &TokenReader::_tokens)
      .def_property_readonly("tokenSource", &TokenReader::getTokenSource);

  py::class_<TokenSource>(m, "A2LTokenSource")
      .def(py::init<>())
      .def_property_readonly("_factory", &TokenSource::getFactory);

  py::class_<ANTLRToken>(m, "ANTLRToken")
      .def(py::init<std::size_t, ANTLRToken::token_t, std::size_t, std::size_t,
                    std::size_t, std::size_t, std::string_view>())
      .def_property_readonly("tokenIndex", &ANTLRToken::tokenIndex)
      .def_property_readonly("type", &ANTLRToken::type)
      .def_property_readonly("line", &ANTLRToken::line)
      .def_property_readonly("column", &ANTLRToken::column)
      .def_property_readonly("start", &ANTLRToken::start)
      .def_property_readonly("stop", &ANTLRToken::stop)
      .def_property_readonly("source", &ANTLRToken::getSource)
      .def_property("text", &ANTLRToken::getText, &ANTLRToken::setText)
      .def_property_readonly("getText", &ANTLRToken::getText)
      .def("__repr__", &ANTLRToken::to_string);

  py::class_<TokenFactory>(m, "TokenFactory")
      .def("create", &TokenFactory::create);
}
