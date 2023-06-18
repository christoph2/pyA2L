#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "preprocessor.hpp"

namespace py = pybind11;

PYBIND11_MODULE(preprocessor, m) {
    m.def("escape_string", &escape_string);
    m.def("test_escape_string", &test_escape_string);
    py::class_<Preprocessor>(m, "Preprocessor")
        .def(py::init<const std::string &>(), py::arg("loglevel"))
        .def("process", &Preprocessor::process, py::arg("filename"), py::arg("encoding"))
        .def("finalize", &Preprocessor::finalize);
    py::class_<Filenames>(m, "Filenames")
        .def(py::init<const std::string &, const std::string &, const std::string &>())
        .def_readonly("a2l", &Filenames::a2l)
        .def_readonly("aml", &Filenames::aml)
        .def_readonly("ifdata", &Filenames::ifdata);
    py::class_<IfDataReader>(m, "IfDataReader")
        .def(py::init<const std::string &, IfDataBuilder &>())
        .def("get", &IfDataReader::get)
        .def("open", &IfDataReader::open)
        .def("close", &IfDataReader::close);
    py::class_<LineMap>(m, "LineMap").def(py::init<>()).def("lookup", &LineMap::lookup);
}
