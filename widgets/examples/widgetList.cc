#include <kdWidgets/Server.h>
#include <kdWidgets/messages/StateMessage.h>
#include <kdWidgets/widgets/Button.h>
#include <kdWidgets/widgets/Checkbox.h>
#include <kdWidgets/widgets/Dropdown.h>
#include <kdWidgets/widgets/FloatSlider.h>
#include <kdWidgets/widgets/Iframe.h>
#include <kdWidgets/widgets/IntSlider.h>
#include <kdWidgets/widgets/Label.h>
#include <kdWidgets/widgets/LayoutContainer.h>
#include <kdWidgets/widgets/RadioButtons.h>
#include <kdWidgets/widgets/TextInput.h>

/**
 * Example showing a list of various widgets and their usage.
 * Each widget has a callback registered to print changes
 * to the terminal when interacted with. Then, the change is
 * loaded into a state message to be synced across all clients.
 */
int main() {
    /* sync state */
    StateMessage state_message_template;
    // helper to automatically update server widget state and send to clients
    auto update_state =
        [&state_message_template](Widget &widget, Server &server, const nlohmann::json &msg) {
            widget.setState(msg);
            state_message_template.setData(widget);
            server.toClients(state_message_template);
        };

    /* main page */
    auto server = Server::create();
    nlohmann::json page_layout = {
        {"display", "flex"},
        {"flexDirection", "column"},
        {"padding", "2rem"},
    };
    auto pageLayout = Widget::create<LayoutContainer>();
    pageLayout->layout = page_layout;

    /* INT SLIDER */
    auto intLabel = Widget::create<Label>("IntSlider", TextType::H1);
    auto intSlider =
        Widget::create<IntSlider>(50, 0, 100, 1, "test", true, false, false, "vertical");
    intSlider->registerCallback("int_slider_change",
                                [update_state, intSlider, server](const nlohmann::json &msg) {
                                    if (msg.contains("value") && msg["value"].is_number_integer()) {
                                        int value = msg["value"];
                                        std::cout << "Slider changed to: " << value << std::endl;
                                        update_state(*intSlider, *server, msg);
                                    }
                                });
    pageLayout->addChildren({intLabel, intSlider});

    /* FLOAT SLIDER */
    auto floatLabel = Widget::create<Label>("FloatSlider", TextType::H1);
    auto floatSlider = Widget::create<FloatSlider>();
    floatSlider->registerCallback(
        "float_slider_change", [update_state, floatSlider, server](const nlohmann::json &msg) {
            if (msg.contains("value") && msg["value"].is_number()) {
                double value = msg["value"];
                std::cout << "Float Slider changed to: " << value << std::endl;
                update_state(*floatSlider, *server, msg);
            }
        });
    pageLayout->addChildren({floatLabel, floatSlider});

    /* CHECKBOX */
    auto checkboxLabel = Widget::create<Label>("Checkbox", TextType::H1);
    auto checkbox = Widget::create<Checkbox>(false, "Check Me!");
    checkbox->registerCallback(
        "checkbox_change", [update_state, checkbox, server](const nlohmann::json &msg) {
            if (msg.contains("value") && msg["value"].is_boolean()) {
                bool checked = msg["value"];
                std::cout << "Checkbox changed to: " << (checked ? "checked" : "unchecked")
                          << std::endl;
                update_state(*checkbox, *server, msg);
            }
        });
    pageLayout->addChildren({checkboxLabel, checkbox});

    /* DROPDOWN */
    auto dropdownLabel = Widget::create<Label>("Dropdown", TextType::H1);
    std::vector<std::string> options = {"Option 1", "Option 2", "Option 3"};
    auto dropdown = Widget::create<Dropdown>(options, "Option 1", "Choose an option");
    dropdown->registerCallback("dropdown_change",
                               [update_state, dropdown, server](const nlohmann::json &msg) {
                                   if (msg.contains("value") && msg["value"].is_string()) {
                                       std::string value = msg["value"];
                                       std::cout << "Dropdown changed to: " << value << std::endl;
                                       update_state(*dropdown, *server, msg);
                                   }
                               });
    pageLayout->addChildren({dropdownLabel, dropdown});

    /* RADIO BUTTONS */
    auto radioLabel = Widget::create<Label>("RadioButtons", TextType::H1);
    std::vector<std::string> radioOptions = {"Choice A", "Choice B", "Choice C"};
    auto radioButtons = Widget::create<RadioButtons>(radioOptions, "Choice A", "Pick one");
    radioButtons->registerCallback(
        "radio_change", [update_state, radioButtons, server](const nlohmann::json &msg) {
            if (msg.contains("value") && msg["value"].is_string()) {
                std::string value = msg["value"];
                std::cout << "RadioButtons changed to: " << value << std::endl;
                update_state(*radioButtons, *server, msg);
            }
        });
    pageLayout->addChildren({radioLabel, radioButtons});

    /* TEXT INPUT */
    auto textLabel = Widget::create<Label>("TextInput", TextType::H1);
    auto textInput = Widget::create<TextInput>("Type something and press Enter");
    textInput->registerCallback("text_input", [](const nlohmann::json &msg) {
        if (msg.contains("value") && msg["value"].is_string()) {
            std::string value = msg["value"];
            std::cout << "TextInput received: " << value << std::endl;
        }
    });
    pageLayout->addChildren({textLabel, textInput});

    /* BUTTON */
    auto buttonLabel = Widget::create<Label>("Button", TextType::H1);
    auto button = Widget::create<Button>("Click Me");
    button->registerCallback("button_click", [](const nlohmann::json &msg) {
        std::cout << "Button was clicked!" << std::endl;
    });
    pageLayout->addChildren({buttonLabel, button});

    /* leave server open */
    server->addWidget(pageLayout);
    std::cout << "Press Enter to exit...\n";
    std::cin.get();
    server.reset();
    return 0;
}
