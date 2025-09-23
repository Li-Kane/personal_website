#pragma once

#include <pybind11/pybind11.h>
#include <nlohmann/json.hpp>

namespace py = pybind11;

py::object json_to_python(const nlohmann::json& j);
nlohmann::json python_to_json(py::handle obj);