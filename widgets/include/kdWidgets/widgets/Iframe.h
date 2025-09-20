#pragma once
#include <kdWidgets/widgets/Widget.h>

/**
 * An iframe widget to embed external web pages.
 * The src property controls the URL loaded in the iframe.
 */
class Iframe : public Widget {
  public:
    using Widget::Widget;
    std::string src;

    Iframe(std::string src = "about:blank")
        : src(std::move(src)) {}

    std::string getName() override { return "Iframe"; }

    nlohmann::json getState() const override {
        nlohmann::json j;
        j["src"] = src;
        return j;
    }

    void setState(const nlohmann::json &state) override {
        if (state.contains("src") && state["src"].is_string()) {
            src = state["src"];
        }
    }

    std::string renderEsm() override {
        return R"(
            function Iframe({id, el, emitWidgetMessage, initialState, style}) {
                const iframe = document.createElement('iframe');
                iframe.id = 'iframe-' + id;
                iframe.src = initialState?.src || 'about:blank';
                el.appendChild(iframe);

                // apply styles
                if (style) {
                    Object.assign(iframe.style, style);
                }

                // listen for state messages from server to update src
                el.addEventListener("server", (e) => {
                    if (e.detail?.type === "state_message") {
                        const newSrc = e.detail?.payload?.state?.src;
                        if (typeof newSrc === 'string' && newSrc !== iframe.src) {
                            iframe.src = newSrc;
                        }
                    }
                });

                return () => {
                    el.innerHTML = '';
                };
            }
            export default Iframe;
        )";
    }
};