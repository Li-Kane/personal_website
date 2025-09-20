#include <pybind11/pybind11.h>
namespace py = pybind11;

// forward declarations of your binders
// void bind_server(py::module_& m);
void bind_widgets(py::module_ &m);

// The name here ("kdwidgets") must match the target name in pybind11_add_module.
PYBIND11_MODULE(kdwidgets, m) {
    m.doc() = "Python bindings for kdWidgets";
    bind_widgets(m);
}
