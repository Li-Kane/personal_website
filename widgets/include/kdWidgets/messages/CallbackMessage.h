#pragma once
#include <kdWidgets/messages/Message.h>
#include <nlohmann/json.hpp>
#include <string>

/**
 * Message to register a new client-side callback function.
 * The callback function will be stored in the global 'callbacks' map
 * and can be invoked by sending messages with the corresponding
 * callback_name.
 */
class CallbackMessage : public Message {
  public:
    std::string new_callback_name;
    std::string callback;

    // constructor
    CallbackMessage() = default;

    std::string type() const override { return "register_callback"; }

    std::string callback_name() const override { return "register_callback"; }

    void setData(std::string new_callback_name_arg, const std::string &callback_arg) {
        new_callback_name = new_callback_name_arg;
        callback = callback_arg;
    }

    std::string serialize() const override {
        nlohmann::json data;
        data["type"] = type();
        data["callback_name"] = callback_name();
        data["new_callback_name"] = new_callback_name;
        data["callback"] = callback;
        return data.dump();
    }
};