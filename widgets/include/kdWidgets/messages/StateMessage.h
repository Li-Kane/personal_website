#pragma once
#include <kdWidgets/messages/Message.h>
#include <kdWidgets/widgets/Widget.h>
#include <nlohmann/json.hpp>
#include <string>

/**
 * Message sent from server to client to update
 * the state of an existing widget.
 */
class StateMessage : public Message {
  public:
    nlohmann::json state;
    std::string widget_id;

    std::string type() const override { return "state_message"; }

    std::string callback_name() const override { return "default"; }

    void setData(const Widget &widget) {
        widget_id = widget.getId();
        state = widget.getState();
    }

    std::string serialize() const override {
        nlohmann::json data;
        data["type"] = type();
        data["callback_name"] = callback_name();
        data["widget_id"] = widget_id;
        data["state"] = state;
        return data.dump();
    }
};
