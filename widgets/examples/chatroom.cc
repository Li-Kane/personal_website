#include <kdWidgets/Server.h>
#include <kdWidgets/messages/AddMessage.h>
#include <kdWidgets/widgets/Chat.h>
#include <kdWidgets/widgets/TextInput.h>

/**
 * This example demonstrates using a custom AddMessage message
 * to update a chat widget using only one message at a time instead of
 * sending a full state to fully rerender the widget. Messages can be
 * sent both from the server (terminal) and clients (text input)
 */
int main() {
    auto textInput = Widget::create<TextInput>();
    auto chat = Widget::create<Chat>(std::initializer_list<std::string>{"Welcome to the chat!"});
    auto server = Server::create();
    AddMessage add_message_template;
    textInput->registerCallback("text_input", [chat, server](const nlohmann::json &msg) {
        if (msg.contains("value") && msg["value"].is_string()) {
            chat->addMessage(msg["value"]);
            AddMessage add_message_template;
            add_message_template.setData(msg["value"], *chat);
            server->toClients(add_message_template);
        }
    });
    server->addWidget(textInput);
    server->addWidget(chat);
    std::string new_text = "init";
    while (!new_text.empty()) {
        std::cout << "Type what message you want to send from the server...\n";
        std::getline(std::cin, new_text);
        chat->addMessage(new_text);
        add_message_template.setData(new_text, *chat);
        server->toClients(add_message_template);
    }
    std::cout << "Press Enter to exit...\n";
    std::cin.get();
    server.reset();
    return 0;
}