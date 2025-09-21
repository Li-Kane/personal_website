#pragma once

#include <pybind11/pybind11.h>
#include <nlohmann/json.hpp>

namespace py = pybind11;

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