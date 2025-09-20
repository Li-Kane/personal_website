// bindhelpers.cc
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// Helpers includes
#include <kdWidgets/Helpers.h>

void bind_helpers(py::module_ &m) {
    // Create a submodule for Helpers namespace
    py::module_ helpers = m.def_submodule("helpers", "Helper functions for creating HTML and JavaScript");

    // Bind the helper functions
    helpers.def("create_index_html", &Helpers::createIndexHtml,
               "Create a basic index.html page with the given title",
               py::arg("title"));

    helpers.def("create_script", &Helpers::createScript,
               "Create the client-side script to connect to the server",
               py::arg("port"));
}