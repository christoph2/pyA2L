#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#pragma warning(disable: 4251 4273)

#include "a2l.h"

namespace py = pybind11;

PYBIND11_MODULE(a2lparser, m) {
    py::class_<a2l>(m, "a2l")
        .def(py::init<antlr4::TokenStream *>())
        .def("addErrorListener", &a2l::addErrorListener, py::arg("listener"))
        .def("removeErrorListeners", &a2l::removeErrorListeners);
}
