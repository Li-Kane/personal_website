#pragma once
#include <kdWidgets/messages/Message.h>
#include <nlohmann/json.hpp>
#include <string>

/**
 * Message to add a new message to a Chat widget.
 * The payload contains the widget_id and the new message string.
 * The client-side callback will append the message to the chat log.
 */
class AddMessage : public Message {
  public:
    std::string widget_id;
    std::string new_message;

    std::string type() const override { return "add_message"; }

    std::string callback_name() const override { return "default"; }

    std::string serialize() const override {
        nlohmann::json data;
        data["type"] = type();
        data["callback_name"] = callback_name();
        data["widget_id"] = widget_id;
        data["new_message"] = new_message;
        return data.dump();
    }

    void setData(std::string message, const Widget &widget) {
        widget_id = widget.getId();
        new_message = message;
    }
};
