#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#pragma warning(disable: 4251)

#include "a2l.h"

namespace py = pybind11;

PYBIND11_MODULE(a2l_parser, m) {
    py::class_<a2l>(m, "a2l").def(py::init<antlr4::TokenStream *>())

        ;
}

// Disable warning C4251
