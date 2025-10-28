#pragma once

#include <pybind11/pybind11.h>
#include <nlohmann/json.hpp>

namespace py = pybind11;

py::object json_to_python(const nlohmann::json& j);
nlohmann::json python_to_json(py::handle obj);

// Type caster for automatic conversion between Python and nlohmann::json
namespace pybind11 { namespace detail {
    template <> struct type_caster<nlohmann::json> {
    public:
        PYBIND11_TYPE_CASTER(nlohmann::json, _("json"));

        // Python -> C++
        bool load(handle src, bool) {
            try {
                value = python_to_json(src);
                return true;
            } catch (...) {
                return false;
            }
        }

        // C++ -> Python
        static handle cast(const nlohmann::json& src, return_value_policy, handle) {
            return json_to_python(src).release();
        }
    };
}} // namespace pybind11::detail