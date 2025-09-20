// bindings.cc
#include <pybind11/pybind11.h>

namespace py = pybind11;

// forward declaration of the binder in bindwidgets.cc
void bind_widgets(py::module_ &m);

PYBIND11_MODULE(kdwidgets, m) {
    m.doc() = "Python bindings for kdWidgets";
    bind_widgets(m);
}
