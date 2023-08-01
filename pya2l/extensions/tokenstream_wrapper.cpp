
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "token_stream.hpp"

namespace py = pybind11;

#if 0
m.def("return_bytes",
    []() {
        std::string s("\xba\xd0\xba\xd0");  // Not valid UTF-8
        return py::bytes(s);  // Return the data without transcoding
    }
);
#endif

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

    py::class_<TokenSource>(m, "A2LTokenSource").def(py::init<>()).def_property_readonly("_factory", &TokenSource::getFactory);

    py::class_<ANTLRToken>(m, "ANTLRToken")
        .def(py::init<std::size_t, ANTLRToken::token_t, std::size_t, std::size_t, std::size_t, std::size_t, std::string_view>())
        .def_property_readonly("tokenIndex", &ANTLRToken::tokenIndex)
        .def_property_readonly("type", &ANTLRToken::getType)
        .def_property_readonly("line", &ANTLRToken::line)
        .def_property_readonly("column", &ANTLRToken::column)
        .def_property_readonly("start", &ANTLRToken::getStartIndex)
        .def_property_readonly("stop", &ANTLRToken::getStopIndex)
        .def_property_readonly("source", &ANTLRToken::getSource)
        //.def_property("text", &ANTLRToken::getText, &ANTLRToken::setText)
        .def_property_readonly(
            "text",  //&ANTLRToken::getText
            [](const ANTLRToken &self) {
                std::string s = self.getText();
                // py::handle py_s =
                // PyUnicode_DecodeLatin1(s.data(), s.length(),
                // nullptr);
                py::handle py_s = PyUnicode_Decode(s.data(), s.length(), ANTLRToken::encoding.data(), "strict");

                if (!py_s) {
                    throw py::error_already_set();
                }
                return py::reinterpret_steal<py::str>(py_s);
            }
        )
        .def("__repr__", &ANTLRToken::toString);

    // py::class_<TokenFactory>(m, "TokenFactory")
    //     .def("create", &TokenFactory::create);
}

#if 0
PyObject *PyUnicode_FromEncodedObject(PyObject *obj, const char *encoding, const char *errors);

// This uses the Python C API to convert Latin-1 to Unicode
m.def("str_output",
[]() {
std::string s = "Send your r\xe9sum\xe9 to Alice in HR"; // Latin-1
py::handle py_s = PyUnicode_DecodeLatin1(s.data(), s.length(), nullptr);
if (!py_s) {
throw py::error_already_set();
}
return py::reinterpret_steal<py::str>(py_s);
}
);

#endif
