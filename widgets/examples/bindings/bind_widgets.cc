// bind_widgets.cc
#include <kdWidgets/widgets/Label.h>
#include <kdWidgets/widgets/Widget.h>
#include <memory>
#include <nlohmann/json.hpp>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

namespace py = pybind11;

// Helper function to convert Python dict to nlohmann::json
nlohmann::json py_dict_to_json(const py::dict &d) {
    nlohmann::json j;
    for (auto item : d) {
        std::string key = py::str(item.first);
        py::object value = py::reinterpret_borrow<py::object>(item.second);

        if (py::isinstance<py::dict>(value)) {
            j[key] = py_dict_to_json(value.cast<py::dict>());
        } else if (py::isinstance<py::list>(value)) {
            nlohmann::json arr = nlohmann::json::array();
            for (auto elem : value) {
                if (py::isinstance<py::dict>(elem)) {
                    arr.push_back(py_dict_to_json(elem.cast<py::dict>()));
                } else if (py::isinstance<py::str>(elem)) {
                    arr.push_back(elem.cast<std::string>());
                } else if (py::isinstance<py::int_>(elem)) {
                    arr.push_back(elem.cast<int>());
                } else if (py::isinstance<py::float_>(elem)) {
                    arr.push_back(elem.cast<double>());
                } else if (py::isinstance<py::bool_>(elem)) {
                    arr.push_back(elem.cast<bool>());
                } else if (elem.is_none()) {
                    arr.push_back(nullptr);
                }
            }
            j[key] = arr;
        } else if (py::isinstance<py::str>(value)) {
            j[key] = value.cast<std::string>();
        } else if (py::isinstance<py::int_>(value)) {
            j[key] = value.cast<int>();
        } else if (py::isinstance<py::float_>(value)) {
            j[key] = value.cast<double>();
        } else if (py::isinstance<py::bool_>(value)) {
            j[key] = value.cast<bool>();
        } else if (value.is_none()) {
            j[key] = nullptr;
        }
    }
    return j;
}

// Helper function to convert nlohmann::json to Python dict
py::dict json_to_py_dict(const nlohmann::json &j) {
    py::dict d;
    for (auto &[key, value] : j.items()) {
        if (value.is_object()) {
            d[key.c_str()] = json_to_py_dict(value);
        } else if (value.is_array()) {
            py::list l;
            for (auto &elem : value) {
                if (elem.is_object()) {
                    l.append(json_to_py_dict(elem));
                } else if (elem.is_string()) {
                    l.append(elem.get<std::string>());
                } else if (elem.is_number_integer()) {
                    l.append(elem.get<int>());
                } else if (elem.is_number_float()) {
                    l.append(elem.get<double>());
                } else if (elem.is_boolean()) {
                    l.append(elem.get<bool>());
                } else if (elem.is_null()) {
                    l.append(py::none());
                }
            }
            d[key.c_str()] = l;
        } else if (value.is_string()) {
            d[key.c_str()] = value.get<std::string>();
        } else if (value.is_number_integer()) {
            d[key.c_str()] = value.get<int>();
        } else if (value.is_number_float()) {
            d[key.c_str()] = value.get<double>();
        } else if (value.is_boolean()) {
            d[key.c_str()] = value.get<bool>();
        } else if (value.is_null()) {
            d[key.c_str()] = py::none();
        }
    }
    return d;
}

void bind_widgets(py::module_ &m) {
    // Bind the base Widget class
    py::class_<Widget, std::shared_ptr<Widget>>(m, "Widget")
        .def("render_esm", &Widget::renderEsm, "Render the widget as ESM JavaScript")
        .def("get_name", &Widget::getName, "Get the widget name")
        .def("get_id", &Widget::getId, "Get the widget ID")
        .def("get_children", &Widget::getChildren, "Get child widgets")
        .def(
            "get_state",
            [](const Widget &w) { return json_to_py_dict(w.getState()); },
            "Get widget state as dictionary")
        .def(
            "set_state",
            [](Widget &w, const py::dict &state) { w.setState(py_dict_to_json(state)); },
            "Set widget state from dictionary",
            py::arg("state"))
        .def(
            "register_callback",
            [](Widget &w, const std::string &event, py::function callback) {
                w.registerCallback(event, [callback](const nlohmann::json &j) {
                    // Convert nlohmann::json to Python dict before calling the callback
                    py::gil_scoped_acquire acquire;
                    callback(json_to_py_dict(j));
                });
            },
            "Register a callback for an event",
            py::arg("event"),
            py::arg("callback"))
        .def("unregister_callback",
             &Widget::unregisterCallback,
             "Remove a callback",
             py::arg("event"))
        .def(
            "get_callback",
            [](Widget &w, const std::string &event) -> py::object {
                auto callback = w.getCallback(event);
                if (callback) {
                    return py::cast(callback);
                }
                return py::none();
            },
            "Get a callback for an event",
            py::arg("event"))
        .def_property(
            "style",
            [](const Widget &w) { return json_to_py_dict(w.style_); },
            [](Widget &w, const py::dict &style) { w.style_ = py_dict_to_json(style); },
            "Widget style attributes")
        .def_readwrite("parent_id", &Widget::parent_id_, "Parent widget ID");

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

    // Bind Label class
    py::class_<Label, Widget, std::shared_ptr<Label>>(m, "Label")
        .def(py::init<>(), "Create an empty Label widget")
        .def(py::init<const std::string &>(), "Create a Label widget with text", py::arg("text"))
        .def(py::init<const std::string &, TextType>(),
             "Create a Label widget with text and type",
             py::arg("text"),
             py::arg("text_type"))
        .def_readwrite("text", &Label::text_, "Label text content")
        .def_readwrite("text_type", &Label::textType_, "Label text type")
        .def("text_type_to_string",
             &Label::textTypeToString,
             "Convert TextType to string",
             py::arg("type"))
        .def_static(
            "create",
            []() { return Widget::create<Label>(); },
            "Factory method to create a Label widget")
        .def_static(
            "create",
            [](const std::string &text) { return Widget::create<Label>(text); },
            "Factory method to create a Label widget with text",
            py::arg("text"))
        .def_static(
            "create",
            [](const std::string &text, TextType type) {
                return Widget::create<Label>(text, type);
            },
            "Factory method to create a Label widget with text and type",
            py::arg("text"),
            py::arg("text_type"));

    // Add a module-level create function for convenience
    m.def(
        "create_label",
        [](const std::string &text = "", TextType type = TextType::P) {
            return Widget::create<Label>(text, type);
        },
        "Create a Label widget",
        py::arg("text") = "",
        py::arg("text_type") = TextType::P);
}