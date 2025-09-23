#include "json_caster.h"
#include <pybind11/stl.h>

py::object json_to_python(const nlohmann::json& j) {
    if (j.is_null()) {
        return py::none();
    } else if (j.is_boolean()) {
        return py::bool_(j.get<bool>());
    } else if (j.is_number_integer()) {
        return py::int_(j.get<int>());
    } else if (j.is_number_float()) {
        return py::float_(j.get<double>());
    } else if (j.is_string()) {
        return py::str(j.get<std::string>());
    } else if (j.is_array()) {
        py::list result;
        for (const auto& element : j) {
            result.append(json_to_python(element));
        }
        return result;
    } else if (j.is_object()) {
        py::dict result;
        for (const auto& [key, value] : j.items()) {
            result[py::str(key)] = json_to_python(value);
        }
        return result;
    }
    return py::none();
}

nlohmann::json python_to_json(py::handle obj) {
    if (obj.is_none()) {
        return nlohmann::json();
    } else if (py::isinstance<py::bool_>(obj)) {
        return obj.cast<bool>();
    } else if (py::isinstance<py::int_>(obj)) {
        return obj.cast<int>();
    } else if (py::isinstance<py::float_>(obj)) {
        return obj.cast<double>();
    } else if (py::isinstance<py::str>(obj)) {
        return obj.cast<std::string>();
    } else if (py::isinstance<py::list>(obj) || py::isinstance<py::tuple>(obj)) {
        nlohmann::json result = nlohmann::json::array();
        for (auto item : obj) {
            result.push_back(python_to_json(item));
        }
        return result;
    } else if (py::isinstance<py::dict>(obj)) {
        nlohmann::json result = nlohmann::json::object();
        for (auto item : obj.cast<py::dict>()) {
            std::string key = item.first.cast<std::string>();
            result[key] = python_to_json(item.second);
        }
        return result;
    }
    throw std::runtime_error("Cannot convert Python object to JSON");
}