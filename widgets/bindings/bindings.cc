// bindings.cc
#include <pybind11/pybind11.h>

namespace py = pybind11;

// forward declaration of the binder in bindwidgets.cc
void bind_widgets(py::module_ &m);
void bind_server(py::module_ &m);
void bind_helpers(py::module_ &m);
void bind_messages(py::module_ &m);

PYBIND11_MODULE(kdwidgets, m) {
    m.doc() = "Python bindings for kdWidgets";
    bind_widgets(m);
    bind_messages(m);
    bind_server(m);
    bind_helpers(m);
}
