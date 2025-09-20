// bindwidgets.cc
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/operators.h>

// Widget includes
#include <kdWidgets/widgets/Widget.h>
#include <kdWidgets/widgets/Label.h>

// For JSON support
#include <nlohmann/json.hpp>

namespace py = pybind11;

// JSON conversion helpers
namespace pybind11 { namespace detail {
    template <> struct type_caster<nlohmann::json> {
    public:
        PYBIND11_TYPE_CASTER(nlohmann::json, _("dict"));

        bool load(handle src, bool) {
            if (src.is_none()) {
                value = nlohmann::json();
                return true;
            }

            try {
                if (isinstance<dict>(src)) {
                    value = nlohmann::json::object();
                    for (auto item : src.cast<dict>()) {
                        std::string key = item.first.cast<std::string>();
                        auto val = item.second;

                        if (isinstance<str>(val)) {
                            value[key] = val.cast<std::string>();
                        } else if (isinstance<bool_>(val)) {
                            value[key] = val.cast<bool>();
                        } else if (isinstance<py::int_>(val)) {
                            value[key] = val.cast<int>();
                        } else if (isinstance<py::float_>(val)) {
                            value[key] = val.cast<double>();
                        }
                    }
                    return true;
                }
            } catch (...) {
                return false;
            }
            return false;
        }

        static handle cast(nlohmann::json src, return_value_policy, handle) {
            if (src.is_null()) {
                return none().inc_ref();
            } else if (src.is_boolean()) {
                return bool_(src.get<bool>()).inc_ref();
            } else if (src.is_number_integer()) {
                return py::int_(src.get<int>()).inc_ref();
            } else if (src.is_number_float()) {
                return py::float_(src.get<double>()).inc_ref();
            } else if (src.is_string()) {
                return str(src.get<std::string>()).inc_ref();
            } else if (src.is_object()) {
                dict d;
                for (auto& [key, val] : src.items()) {
                    d[str(key)] = cast(val, return_value_policy::copy, handle());
                }
                return d.inc_ref();
            }
            return none().inc_ref();
        }
    };
}}

namespace py = pybind11;

void bind_widgets(py::module_ &m) {
    // Bind TextType enum
    py::enum_<TextType>(m, "TextType")
        .value("H1", TextType::H1)
        .value("H2", TextType::H2)
        .value("H3", TextType::H3)
        .value("H4", TextType::H4)
        .value("H5", TextType::H5)
        .value("H6", TextType::H6)
        .value("P", TextType::P)
        .value("EM", TextType::EM)
        .value("I", TextType::I)
        .value("STRONG", TextType::STRONG)
        .value("B", TextType::B)
        .value("U", TextType::U)
        .value("A", TextType::A)
        .export_values();

    // Bind Widget base class
    py::class_<Widget, std::shared_ptr<Widget>>(m, "Widget")
        .def("renderEsm", &Widget::renderEsm)
        .def("getName", &Widget::getName)
        .def("getId", &Widget::getId)
        .def("getState", &Widget::getState)
        .def("setState", &Widget::setState)
        .def("getChildren", &Widget::getChildren)
        .def("registerCallback", &Widget::registerCallback)
        .def("unregisterCallback", &Widget::unregisterCallback)
        .def("getCallback", &Widget::getCallback)
        .def_readwrite("layout", &Widget::layout)
        .def_readwrite("style", &Widget::style)
        .def_readwrite("parent_id", &Widget::parent_id);

    // Bind Label class
    py::class_<Label, Widget, std::shared_ptr<Label>>(m, "Label")
        .def(py::init<>())
        .def(py::init<const std::string&>())
        .def(py::init<const std::string&, TextType>())
        .def_readwrite("text", &Label::text)
        .def_readwrite("textType", &Label::textType)
        .def("textTypeToString", &Label::textTypeToString);
}