#pragma once
#include <kdWidgets/widgets/Widget.h>

/**
 * A checkbox widget that can be toggled on or off.
 * Emits 'checkbox_change' event with payload { value: bool }.
 */
class Checkbox : public Widget {
  public:
    using Widget::Widget;

    // Public state (similar to ipywidgets)
    bool value;
    std::string description;
    bool disabled;
    bool indent;

    Checkbox(bool value = false,
             std::string description = "",
             bool disabled = false,
             bool indent = false)
        : value(value)
        , description(std::move(description))
        , disabled(disabled)
        , indent(indent) {}

    std::string getName() override { return "Checkbox"; }

    nlohmann::json getState() const override {
        return {{"value", value},
                {"description", description},
                {"disabled", disabled},
                {"indent", indent}};
    }

    void setState(const nlohmann::json &s) override {
        if (s.contains("value") && s["value"].is_boolean())
            value = s["value"].get<bool>();
        if (s.contains("description") && s["description"].is_string())
            description = s["description"].get<std::string>();
        if (s.contains("disabled") && s["disabled"].is_boolean())
            disabled = s["disabled"].get<bool>();
        if (s.contains("indent") && s["indent"].is_boolean())
            indent = s["indent"].get<bool>();
    }

    std::string renderEsm() override {
        // Emits 'checkbox_change' with { value }
        return R"(
            function Checkbox({ id, el, emitWidgetMessage, initialState, style }) {
                const state = Object.assign({
                    value: false,
                    description: "",
                    disabled: false,
                    indent: false
                }, initialState || {});

                const container = document.createElement('div');
                container.style.display = 'flex';
                container.style.alignItems = 'center';
                container.style.gap = '0.5rem';
                if (state.indent) {
                    container.style.marginLeft = '20px';
                }

                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.id = 'checkbox-' + id;
                checkbox.checked = state.value;
                checkbox.disabled = state.disabled;

                const label = document.createElement('label');
                label.htmlFor = 'checkbox-' + id;
                label.textContent = state.description;
                label.style.cursor = state.disabled ? 'default' : 'pointer';
                label.style.userSelect = 'none';

                // Event handler
                checkbox.addEventListener('change', (e) => {
                    state.value = e.target.checked;
                    emitWidgetMessage({
                        el,
                        type: 'checkbox_change',
                        payload: { value: state.value }
                    });
                });

                // Assemble
                container.appendChild(checkbox);
                if (state.description) {
                    container.appendChild(label);
                }
                el.appendChild(container);

                // Server -> client updates
                el.addEventListener('server', (e) => {
                    const msg = e.detail;
                    if (!msg) return;
                    
                    if (msg.type === 'state_message') {
                        const p = msg.payload?.state || {};
                        if (typeof p.value === 'boolean') {
                            state.value = p.value;
                            checkbox.checked = p.value;
                        }
                        if (typeof p.description === 'string') {
                            state.description = p.description;
                            label.textContent = p.description;
                        }
                        if (typeof p.disabled === 'boolean') {
                            state.disabled = p.disabled;
                            checkbox.disabled = p.disabled;
                            label.style.cursor = p.disabled ? 'default' : 'pointer';
                        }
                        if (typeof p.indent === 'boolean') {
                            state.indent = p.indent;
                            container.style.marginLeft = p.indent ? '20px' : '0';
                        }
                    }
                });

                return () => {
                    el.innerHTML = '';
                };
            }
            export default Checkbox;
        )";
    }
};