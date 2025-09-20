#pragma once
#include <kdWidgets/messages/Message.h>
#include <kdWidgets/widgets/Widget.h>
#include <nlohmann/json.hpp>
#include <string>

/**
 * Default message sent from server to client
 * when a new widget is added. This message contains
 * all the necessary information to load the widget.
 */
class WidgetMessage : public Message {
  public:
    std::string type() const override { return "widget_message"; }

    std::string callback_name() const override { return "add_widget"; }

    void setData(Widget &widget) {
        widget_id = widget.getId();
        esm = widget.renderEsm();
        state = widget.getState();
        style = widget.style;
        parent_id = widget.parent_id;
        widget_name = widget.getName();
        layout = widget.layout;
    }

    std::string serialize() const override {
        nlohmann::json data;
        data["type"] = type();
        data["callback_name"] = callback_name();
        data["widget_name"] = widget_name;
        data["widget_id"] = widget_id;
        data["esm"] = esm;
        data["state"] = state;
        data["style"] = style;
        data["parent_id"] = parent_id;
        data["layout"] = layout;
        return data.dump();
    }

    nlohmann::json state;
    nlohmann::json layout;
    nlohmann::json style;
    std::string widget_id;
    std::string esm;
    std::string parent_id;
    std::string widget_name;
};
