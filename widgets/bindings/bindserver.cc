// bindserver.cc
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/functional.h>

namespace py = pybind11;

// Server includes
#include <kdWidgets/Server.h>
#include <kdWidgets/messages/Message.h>
#include <kdWidgets/messages/CallbackMessage.h>

void bind_server(py::module_ &m) {
    // Bind PerSocketData struct
    py::class_<PerSocketData>(m, "PerSocketData")
        .def(py::init<>())
        .def_readwrite("id", &PerSocketData::id);

    // Bind WorkerThread struct
    py::class_<WorkerThread>(m, "WorkerThread")
        .def(py::init<>())
        .def("run_worker_thread", &WorkerThread::runWorkerThread,
             "Run the worker thread",
             py::arg("port"), py::arg("title"), py::arg("host"))
        .def_readonly("listening", &WorkerThread::listening_);

    // Bind Server class
    py::class_<Server, std::shared_ptr<Server>>(m, "Server")
        .def(py::init<>())
        .def(py::init<int>(), py::arg("port"))
        .def(py::init<int, std::string>(), py::arg("port"), py::arg("title"))
        .def(py::init<int, std::string, std::string>(),
             py::arg("port"), py::arg("title"), py::arg("host"))
        .def("add_widget", &Server::addWidget,
             "Add a widget to the server",
             py::arg("widget"))
        .def("register_callback", &Server::registerCallback,
             "Register a callback message",
             py::arg("message"))
        .def("to_clients", &Server::toClients,
             "Send a message to all connected clients",
             py::arg("message"));
}