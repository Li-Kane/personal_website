// bindmessages.cc
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// Message includes
#include <kdWidgets/messages/Message.h>
#include <kdWidgets/messages/CallbackMessage.h>
#include <kdWidgets/messages/StateMessage.h>
#include <kdWidgets/messages/WidgetMessage.h>
#include <kdWidgets/messages/AddMessage.h>

void bind_messages(py::module_ &m) {
    // Create a submodule for messages
    py::module_ messages = m.def_submodule("messages", "Message classes for client-server communication");

    // Bind base Message class
    py::class_<Message>(messages, "Message")
        .def("type", &Message::type)
        .def("callback_name", &Message::callback_name)
        .def("serialize", &Message::serialize);

    // Bind CallbackMessage
    py::class_<CallbackMessage, Message>(messages, "CallbackMessage")
        .def(py::init<>())
        .def_readwrite("new_callback_name", &CallbackMessage::new_callback_name)
        .def_readwrite("callback", &CallbackMessage::callback)
        .def("set_data", &CallbackMessage::setData,
             "Set the callback data",
             py::arg("new_callback_name"), py::arg("callback"));

    // Bind StateMessage
    py::class_<StateMessage, Message>(messages, "StateMessage")
        .def(py::init<>())
        .def_readwrite("state", &StateMessage::state)
        .def_readwrite("widget_id", &StateMessage::widget_id)
        .def("set_data", &StateMessage::setData,
             "Set the state data from a widget",
             py::arg("widget"));

    // Bind WidgetMessage
    py::class_<WidgetMessage, Message>(messages, "WidgetMessage")
        .def(py::init<>())
        .def_readwrite("state", &WidgetMessage::state)
        .def_readwrite("layout", &WidgetMessage::layout)
        .def_readwrite("style", &WidgetMessage::style)
        .def_readwrite("widget_id", &WidgetMessage::widget_id)
        .def_readwrite("esm", &WidgetMessage::esm)
        .def_readwrite("parent_id", &WidgetMessage::parent_id)
        .def_readwrite("widget_name", &WidgetMessage::widget_name)
        .def("set_data", &WidgetMessage::setData,
             "Set the widget data from a widget",
             py::arg("widget"));

    // Bind AddMessage
    py::class_<AddMessage, Message>(messages, "AddMessage")
        .def(py::init<>())
        .def_readwrite("widget_id", &AddMessage::widget_id)
        .def_readwrite("new_message", &AddMessage::new_message)
        .def("set_data", &AddMessage::setData,
             "Set the message data",
             py::arg("message"), py::arg("widget"));
}