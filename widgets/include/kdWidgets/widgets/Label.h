#pragma once
#include <kdWidgets/widgets/Widget.h>

enum class TextType { H1, H2, H3, H4, H5, H6, P, EM, I, STRONG, B, U, A };
inline std::vector<std::string> TextTypeStrings = {
    "h1", "h2", "h3", "h4", "h5", "h6", "p", "em", "i", "strong", "b", "u", "a"};

/**
 * A widget that displays a text label.
 * The textType controls the HTML tag used to render the text (e.g. h1, p, em, etc).
 */
class Label : public Widget {
  public:
    using Widget::Widget;

    std::string text;
    TextType textType;

    Label(const std::string &text = "", TextType textType = TextType::P)
        : text(text)
        , textType(textType) {}

    std::string getName() override { return "Label"; }

    nlohmann::json getState() const override {
        nlohmann::json j;
        j["text"] = text;
        j["textType"] = textTypeToString(textType);
        return j;
    }

    std::string textTypeToString(TextType type) const {
        return TextTypeStrings[static_cast<int>(type)];
    }

    void setState(const nlohmann::json &state) override {
        if (state.contains("text") && state["text"].is_string()) {
            text = state["text"];
        }
        if (state.contains("textType") && state["textType"].is_string()) {
            std::string typeStr = state["textType"];
            auto it = std::find(TextTypeStrings.begin(), TextTypeStrings.end(), typeStr);
            if (it != TextTypeStrings.end()) {
                textType = static_cast<TextType>(std::distance(TextTypeStrings.begin(), it));
            }
        }
    }

    std::string renderEsm() override {
        return R"(
            function Text({id, el, emitWidgetMessage, initialState, style}) {
                const textType = initialState?.textType || 'p';
                let node = document.createElement(textType);
                node.id = 'text-' + id;
                node.textContent = initialState?.text || '';
                if (style) {
                    Object.assign(node.style, style);
                }
                el.appendChild(node);

                el.addEventListener("server", (e) => {
                    if (e.detail?.type === "state_message") {
                        const newText = e.detail?.payload?.state?.text;
                        if (typeof newText === 'string') {
                            node.textContent = newText;
                        }
                        const newTextType = e.detail?.payload?.state?.textType;
                        if (typeof newTextType === 'string' && newTextType !== textType) {
                            const newNode = document.createElement(newTextType);
                            newNode.id = 'text-' + id;
                            newNode.textContent = node.textContent;
                            node.replaceWith(newNode);
                            node = newNode;
                        }
                    }
                });

                return () => {
                    node.remove();
                };
            }
            export default Text;
        )";
    }
};