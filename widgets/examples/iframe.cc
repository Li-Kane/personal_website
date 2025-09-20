#include <kdWidgets/Server.h>
#include <kdWidgets/messages/StateMessage.h>
#include <kdWidgets/widgets/Iframe.h>
#include <kdWidgets/widgets/LayoutContainer.h>

/**
 * Example that demonstrates using multiple iframe widgets
 * in a layout container. The first iframe can be updated
 * dynamically by sending state messages from the server.
 */
int main() {
    nlohmann::json flex_layout = {
        {"display", "flex"}, {"flexDirection", "row"}, {"height", "100%"}, {"width", "100%"}};
    nlohmann::json iframe_layout = {
        {"flex", "1"},
        {"display", "flex"},
        {"justifyContent", "center"},
        {"alignItems", "center"},
    };
    nlohmann::json iframe_style = {
        {"height", "95%"},
        {"width", "95%"},
    };
    auto layoutContainer = Widget::create<LayoutContainer>();
    auto Iframe1 = Widget::create<Iframe>("https://www.example.com");
    auto Iframe2 = Widget::create<Iframe>("https://www.wikipedia.org/");
    layoutContainer->layout = flex_layout;
    Iframe1->layout = iframe_layout;
    Iframe2->layout = iframe_layout;
    Iframe1->style = iframe_style;
    Iframe2->style = iframe_style;
    layoutContainer->addChildren({Iframe1, Iframe2});
    auto server = Server::create();
    server->addWidget(layoutContainer);
    std::string new_src = "init";
    StateMessage state_message_template;
    while (!new_src.empty()) {
        std::cout << "Type new source you want to send from the server...\n";
        std::getline(std::cin, new_src);
        Iframe1->src = new_src;
        state_message_template.setData(*Iframe1);
        server->toClients(state_message_template);
    }

    std::cout << "Press Enter to exit...\n";
    std::cin.get();
    server.reset();
    return 0;
}