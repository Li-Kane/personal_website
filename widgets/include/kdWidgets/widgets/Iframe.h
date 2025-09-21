#pragma once
#include <kdWidgets/widgets/Widget.h>

/**
 * An iframe widget to embed external web pages.
 * The src property controls the URL loaded in the iframe.
 * If is_static is false, mouse move events over the iframe
 * will be captured and sent to the server as 'mouse_move' events.
 */
class Iframe : public Widget {
  public:
    using Widget::Widget;
    std::string src;
    bool is_static;

    Iframe(std::string src = "about:blank", bool is_static = true)
        : src(std::move(src)), is_static(is_static) {}

    std::string getName() override { return "Iframe"; }

    nlohmann::json getState() const override {
        nlohmann::json j;
        j["src"] = src;
        j["is_static"] = is_static;
        return j;
    }

    void setState(const nlohmann::json &state) override {
        if (state.contains("src") && state["src"].is_string()) {
            src = state["src"];
        }
        if (state.contains("is_static") && state["is_static"].is_boolean()) {
            is_static = state["is_static"];
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

                // listen to mouse move events
                if (!initialState?.is_static) {
                    el.addEventListener('mousemove', (event) => {
                        const rect = el.getBoundingClientRect();
                        const x = ((event.clientX - rect.left) - (rect.width / 2)) / rect.height;
                        const y = ((event.clientY - rect.top) - (rect.height / 2)) / rect.height;
                        emitWidgetMessage({el, type: 'mouse_move', payload: {x: x, y: y}});
                    });
                }

                return () => {
                    el.innerHTML = '';
                };
            }
            export default Iframe;
        )";
    }
};