#pragma once
#include <kdWidgets/widgets/Widget.h>
#include <string>

/**
 * A button widget that can be clicked.
 * Emits 'button_click' event with no payload when clicked.
 */
class Button : public Widget {
  public:
    using Widget::Widget;

    // Public state (similar to ipywidgets, but without button_style and icon)
    std::string description;
    bool disabled;
    std::string tooltip;

    Button(std::string description = "Button", bool disabled = false, std::string tooltip = "")
        : description(std::move(description))
        , disabled(disabled)
        , tooltip(std::move(tooltip)) {}

    std::string getName() override { return "Button"; }

    nlohmann::json getState() const override {
        return {{"description", description}, {"disabled", disabled}, {"tooltip", tooltip}};
    }

    void setState(const nlohmann::json &s) override {
        if (s.contains("description") && s["description"].is_string())
            description = s["description"].get<std::string>();
        if (s.contains("disabled") && s["disabled"].is_boolean())
            disabled = s["disabled"].get<bool>();
        if (s.contains("tooltip") && s["tooltip"].is_string())
            tooltip = s["tooltip"].get<std::string>();
    }

    std::string renderEsm() override {
        return R"(
            function Button({ id, el, emitWidgetMessage, initialState, style }) {
                const state = Object.assign({
                    description: "Button",
                    disabled: false,
                    tooltip: ""
                }, initialState || {});

                const button = document.createElement('button');
                button.id = 'button-' + id;
                button.textContent = state.description;
                button.disabled = state.disabled;
                if (state.tooltip) {
                    button.title = state.tooltip;
                }
                
                // Basic styling
                button.style.padding = '0.375rem 0.75rem';
                button.style.fontSize = '14px';
                button.style.borderRadius = '4px';
                button.style.border = '1px solid #ccc';
                button.style.backgroundColor = '#f8f9fa';
                button.style.color = '#333';
                button.style.cursor = state.disabled ? 'default' : 'pointer';
                button.style.transition = 'background-color 0.15s ease-in-out';

                // custom styles
                if (style) {
                    Object.assign(button.style, style);
                }
                
                // Hover effect (when not disabled)
                if (!state.disabled) {
                    button.addEventListener('mouseenter', () => {
                        button.style.backgroundColor = '#e2e6ea';
                    });
                    button.addEventListener('mouseleave', () => {
                        button.style.backgroundColor = '#f8f9fa';
                    });
                }

                // Click handler
                button.addEventListener('click', () => {
                    if (!state.disabled) {
                        emitWidgetMessage({
                            el,
                            type: 'button_click',
                            payload: {}
                        });
                    }
                });

                el.appendChild(button);

                // Server -> client updates
                el.addEventListener('server', (e) => {
                    const msg = e.detail;
                    if (!msg) return;
                    
                    if (msg.type === 'state_message') {
                        const p = msg.payload?.state || {};
                        if (typeof p.description === 'string') {
                            state.description = p.description;
                            button.textContent = p.description;
                        }
                        if (typeof p.disabled === 'boolean') {
                            state.disabled = p.disabled;
                            button.disabled = p.disabled;
                            button.style.cursor = p.disabled ? 'default' : 'pointer';
                        }
                        if (typeof p.tooltip === 'string') {
                            state.tooltip = p.tooltip;
                            button.title = p.tooltip;
                        }
                    }
                });

                return () => {
                    el.innerHTML = '';
                };
            }
            export default Button;
        )";
    }
};