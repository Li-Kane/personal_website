// bindwidgets.cc
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>
#include <pybind11/operators.h>

// Widget includes
#include <kdWidgets/widgets/Widget.h>
#include <kdWidgets/widgets/Label.h>
#include <kdWidgets/widgets/Button.h>
#include <kdWidgets/widgets/Chat.h>
#include <kdWidgets/widgets/Checkbox.h>
#include <kdWidgets/widgets/Dropdown.h>
#include <kdWidgets/widgets/FloatSlider.h>
#include <kdWidgets/widgets/IntSlider.h>
#include <kdWidgets/widgets/Iframe.h>
#include <kdWidgets/widgets/LayoutContainer.h>
#include <kdWidgets/widgets/RadioButtons.h>
#include <kdWidgets/widgets/TextInput.h>

// For JSON support
#include "json_caster.h"

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
        .def("render_esm", &Widget::renderEsm)
        .def("get_name", &Widget::getName)
        .def("get_id", &Widget::getId)
        .def("get_state", &Widget::getState)
        .def("set_state", &Widget::setState)
        .def("get_children", &Widget::getChildren)
        .def("register_callback", &Widget::registerCallback)
        .def("unregister_callback", &Widget::unregisterCallback)
        .def("get_callback", &Widget::getCallback)
        .def_readwrite("layout", &Widget::layout)
        .def_readwrite("style", &Widget::style)
        .def_readwrite("parent_id", &Widget::parent_id);

    // Bind Label class
    py::class_<Label, Widget, std::shared_ptr<Label>>(m, "Label")
        .def(py::init<>())
        .def(py::init<const std::string&>())
        .def(py::init<const std::string&, TextType>())
        .def_readwrite("text", &Label::text)
        .def_readwrite("text_type", &Label::textType)
        .def("text_type_to_string", &Label::textTypeToString);

    // Bind Button class
    py::class_<Button, Widget, std::shared_ptr<Button>>(m, "Button")
        .def(py::init<>())
        .def(py::init<std::string>())
        .def(py::init<std::string, bool>())
        .def(py::init<std::string, bool, std::string>())
        .def_readwrite("description", &Button::description)
        .def_readwrite("disabled", &Button::disabled)
        .def_readwrite("tooltip", &Button::tooltip);

    // Bind Checkbox class
    py::class_<Checkbox, Widget, std::shared_ptr<Checkbox>>(m, "Checkbox")
        .def(py::init<>())
        .def(py::init<bool>())
        .def(py::init<bool, std::string>())
        .def(py::init<bool, std::string, bool>())
        .def(py::init<bool, std::string, bool, bool>())
        .def_readwrite("value", &Checkbox::value)
        .def_readwrite("description", &Checkbox::description)
        .def_readwrite("disabled", &Checkbox::disabled)
        .def_readwrite("indent", &Checkbox::indent);

    // Bind TextInput class
    py::class_<TextInput, Widget, std::shared_ptr<TextInput>>(m, "TextInput")
        .def(py::init<>())
        .def(py::init<std::string>())
        .def_readwrite("placeholder", &TextInput::placeholder);

    // Bind FloatSlider class
    py::class_<FloatSlider, Widget, std::shared_ptr<FloatSlider>>(m, "FloatSlider")
        .def(py::init<>())
        .def(py::init<double>())
        .def(py::init<double, double>())
        .def(py::init<double, double, double>())
        .def(py::init<double, double, double, double>())
        .def(py::init<double, double, double, double, std::string>())
        .def(py::init<double, double, double, double, std::string, bool>())
        .def(py::init<double, double, double, double, std::string, bool, std::string>())
        .def(py::init<double, double, double, double, std::string, bool, std::string, bool>())
        .def(py::init<double, double, double, double, std::string, bool, std::string, bool, bool>())
        .def(py::init<double, double, double, double, std::string, bool, std::string, bool, bool, std::string>())
        .def_readwrite("value", &FloatSlider::value)
        .def_readwrite("min", &FloatSlider::min)
        .def_readwrite("max", &FloatSlider::max)
        .def_readwrite("step", &FloatSlider::step)
        .def_readwrite("description", &FloatSlider::description)
        .def_readwrite("disabled", &FloatSlider::disabled)
        .def_readwrite("readout", &FloatSlider::readout)
        .def_readwrite("readout_format", &FloatSlider::readout_format)
        .def_readwrite("orientation", &FloatSlider::orientation)
        .def_readwrite("continuous_update", &FloatSlider::continuous_update);

    // Bind IntSlider class
    py::class_<IntSlider, Widget, std::shared_ptr<IntSlider>>(m, "IntSlider")
        .def(py::init<>())
        .def(py::init<int>())
        .def(py::init<int, int>())
        .def(py::init<int, int, int>())
        .def(py::init<int, int, int, int>())
        .def(py::init<int, int, int, int, std::string>())
        .def(py::init<int, int, int, int, std::string, bool>())
        .def(py::init<int, int, int, int, std::string, bool, bool>())
        .def(py::init<int, int, int, int, std::string, bool, bool, bool>())
        .def(py::init<int, int, int, int, std::string, bool, bool, bool, std::string>())
        .def_readwrite("value", &IntSlider::value)
        .def_readwrite("min", &IntSlider::min)
        .def_readwrite("max", &IntSlider::max)
        .def_readwrite("step", &IntSlider::step)
        .def_readwrite("description", &IntSlider::description)
        .def_readwrite("disabled", &IntSlider::disabled)
        .def_readwrite("readout", &IntSlider::readout)
        .def_readwrite("orientation", &IntSlider::orientation)
        .def_readwrite("continuous_update", &IntSlider::continuous_update);

    // Bind Dropdown class
    py::class_<Dropdown, Widget, std::shared_ptr<Dropdown>>(m, "Dropdown")
        .def(py::init<>())
        .def(py::init<std::vector<std::string>>())
        .def(py::init<std::vector<std::string>, std::string>())
        .def(py::init<std::vector<std::string>, std::string, std::string>())
        .def(py::init<std::vector<std::string>, std::string, std::string, bool>())
        .def_readwrite("options", &Dropdown::options)
        .def_readwrite("value", &Dropdown::value)
        .def_readwrite("description", &Dropdown::description)
        .def_readwrite("disabled", &Dropdown::disabled);

    // Bind RadioButtons class
    py::class_<RadioButtons, Widget, std::shared_ptr<RadioButtons>>(m, "RadioButtons")
        .def(py::init<>())
        .def(py::init<std::vector<std::string>>())
        .def(py::init<std::vector<std::string>, std::string>())
        .def(py::init<std::vector<std::string>, std::string, std::string>())
        .def(py::init<std::vector<std::string>, std::string, std::string, bool>())
        .def_readwrite("options", &RadioButtons::options)
        .def_readwrite("value", &RadioButtons::value)
        .def_readwrite("description", &RadioButtons::description)
        .def_readwrite("disabled", &RadioButtons::disabled);

    // Bind Chat class
    py::class_<Chat, Widget, std::shared_ptr<Chat>>(m, "Chat")
        .def(py::init<>())
        .def(py::init<const std::vector<std::string>&>())
        .def_readwrite("messages", &Chat::messages)
        .def("add_message", &Chat::addMessage);

    // Bind Iframe class
    py::class_<Iframe, Widget, std::shared_ptr<Iframe>>(m, "Iframe")
        .def(py::init<>())
        .def(py::init<std::string>())
        .def(py::init<std::string, bool>())
        .def_readwrite("src", &Iframe::src)
        .def_readwrite("is_static", &Iframe::is_static);

    // Bind LayoutContainer class
    py::class_<LayoutContainer, Widget, std::shared_ptr<LayoutContainer>>(m, "LayoutContainer")
        .def(py::init<>())
        .def("add_child", &LayoutContainer::addChild)
        .def("add_children", &LayoutContainer::addChildren);
}