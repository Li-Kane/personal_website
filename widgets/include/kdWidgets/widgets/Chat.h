#pragma once
#include <kdWidgets/widgets/Widget.h>

/**
 * A simple chat widget that displays a list of messages.
 * New messages can be added using the addMessage method.
 * The widget listens for "add_message" events from the server
 * to append new messages without needing a full state update.
 */
class Chat : public Widget {
  public:
    using Widget::Widget;
    std::vector<std::string> messages;

    Chat(const std::vector<std::string> &messages = {})
        : messages(messages) {}

    std::string getName() override { return "Chat"; }

    nlohmann::json getState() const override {
        nlohmann::json j;
        j["messages"] = messages;
        return j;
    }

    void setState(const nlohmann::json &state) override {
        if (state.contains("messages") && state["messages"].is_array()) {
            messages.clear();
            for (const auto &msg : state["messages"]) {
                if (msg.is_string()) {
                    messages.push_back(msg.get<std::string>());
                }
            }
        }
    }

    void addMessage(const std::string &message) { messages.push_back(message); }

    std::string renderEsm() override {
        return R"(
            function Chat({id, el, emitWidgetMessage, initialState, style}) {
                const messages = initialState?.messages || [];
                messages.forEach(msg => {
                    const messageNode = document.createElement('p');
                    messageNode.textContent = msg;
                    el.appendChild(messageNode);
                });

                el.addEventListener("server", (e) => {
                    if (e.detail?.type === "add_message") {
                        const newText = e.detail?.payload?.new_message;
                        const messageNode = document.createElement('p');
                        messageNode.textContent = newText;
                        el.appendChild(messageNode);
                    }
                });

                return () => {
                    el.innerHTML = '';
                };
            }
            export default Chat;
        )";
    }
};