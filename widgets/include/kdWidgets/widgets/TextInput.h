#pragma once
#include <kdWidgets/widgets/Widget.h>

/**
 * A simple text input widget that emits an event
 * when the user presses Enter. The event is 'text_input'
 * and the payload is { value: "the input text" }.
 */
class TextInput : public Widget {
  public:
    using Widget::Widget;

    // Public state
    std::string placeholder;

    TextInput(std::string placeholder = "")
        : placeholder(std::move(placeholder)) {}

    std::string getName() override { return "TextInput"; }

    nlohmann::json getState() const override {
        nlohmann::json j;
        j["placeholder"] = placeholder;
        return j;
    }

    std::string renderEsm() override {
        // emits 'text_input' with { value }
        return R"(
            function TextInput({id, el, emitWidgetMessage, initialState, style}) {
                const input = document.createElement('input');
                input.type = 'text';
                input.id = 'textinput-' + id;
                input.placeholder = initialState?.placeholder || '';
                if (style) {
                    Object.assign(input.style, style);
                }
                el.appendChild(input);
                
                // handle enter key press
                input.addEventListener('keydown', (event) => {
                    // listen to enter key press
                    if (event.key === 'Enter') {
                        const newValue = event.target.value;
                        emitWidgetMessage({el, type: 'text_input', payload: {value: newValue}});
                        event.target.value = '';
                    }
                });

                // server -> client updates
                el.addEventListener("server", (e) => {
                    if (e.detail?.type === "state_message") {
                        const newPlaceholder = e.detail?.payload?.state?.placeholder;
                        if (typeof newPlaceholder === 'string' && newPlaceholder !== input.placeholder) {
                            input.placeholder = newPlaceholder;
                        }
                    }
                });

                return () => {
                    input.remove();
                };
            }
            export default TextInput;
        )";
    }
};
