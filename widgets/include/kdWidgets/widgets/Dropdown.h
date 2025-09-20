#pragma once
#include <algorithm>
#include <kdWidgets/widgets/Widget.h>
#include <string>
#include <vector>

/**
 * A dropdown widget allowing a single selection
 * from a list of options. Emits 'dropdown_change' event
 * with payload { value: "the selected option" }.
 */
class Dropdown : public Widget {
  public:
    using Widget::Widget;

    // Public state
    std::vector<std::string> options;
    std::string value;
    std::string description;
    bool disabled = false;

    Dropdown(std::vector<std::string> options = {},
             std::string value = "",
             std::string description = "",
             bool disabled = false)
        : options(std::move(options))
        , value(std::move(value))
        , description(std::move(description))
        , disabled(disabled) {
        normalize_();
    }

    std::string getName() override { return "Dropdown"; }

    nlohmann::json getState() const override {
        return {{"options", options},
                {"value", value},
                {"description", description},
                {"disabled", disabled}};
    }

    void setState(const nlohmann::json &s) override {
        if (s.contains("options") && s["options"].is_array()) {
            options.clear();
            for (const auto &opt : s["options"]) {
                if (opt.is_string()) {
                    options.push_back(opt.get<std::string>());
                }
            }
        }
        if (s.contains("value") && s["value"].is_string())
            value = s["value"].get<std::string>();
        if (s.contains("description") && s["description"].is_string())
            description = s["description"].get<std::string>();
        if (s.contains("disabled") && s["disabled"].is_boolean())
            disabled = s["disabled"].get<bool>();

        normalize_();
    }

    std::string renderEsm() override {
        // Emits 'dropdown_change' with { value }
        return R"(
            function Dropdown({ id, el, emitWidgetMessage, initialState, style }) {
                const state = Object.assign({
                    options: [],
                    value: "",
                    description: "",
                    disabled: false
                }, initialState || {});

                // Ensure value is valid
                if (state.options.length > 0 && !state.options.includes(state.value)) {
                    state.value = state.options[0];
                }

                const container = document.createElement('div');
                container.style.display = 'flex';
                container.style.alignItems = 'center';
                container.style.gap = '0.5rem';

                const label = document.createElement('label');
                label.htmlFor = 'dropdown-' + id;
                label.textContent = state.description;
                label.style.minWidth = 'auto';

                const select = document.createElement('select');
                select.id = 'dropdown-' + id;
                select.disabled = state.disabled;
                select.style.minWidth = '100px';

                // Populate options
                const updateOptions = () => {
                    select.innerHTML = '';
                    state.options.forEach(opt => {
                        const option = document.createElement('option');
                        option.value = opt;
                        option.textContent = opt;
                        option.selected = (opt === state.value);
                        select.appendChild(option);
                    });
                };

                updateOptions();

                // Event handler
                select.addEventListener('change', (e) => {
                    state.value = e.target.value;
                    emitWidgetMessage({
                        el,
                        type: 'dropdown_change',
                        payload: { value: state.value }
                    });
                });

                // Assemble
                if (state.description) {
                    container.appendChild(label);
                }
                container.appendChild(select);
                el.appendChild(container);

                // Server -> client updates
                el.addEventListener('server', (e) => {
                    const msg = e.detail;
                    if (!msg) return;
                    
                    if (msg.type === 'state_message') {
                        const p = msg.payload?.state || {};
                        let needsUpdate = false;
                        
                        if (Array.isArray(p.options)) {
                            state.options = p.options.filter(opt => typeof opt === 'string');
                            needsUpdate = true;
                        }
                        if (typeof p.value === 'string') {
                            state.value = p.value;
                            needsUpdate = true;
                        }
                        if (needsUpdate) {
                            // Ensure value is still valid
                            if (state.options.length > 0 && !state.options.includes(state.value)) {
                                state.value = state.options[0];
                            }
                            updateOptions();
                        }
                        if (typeof p.description === 'string') {
                            state.description = p.description;
                            label.textContent = p.description;
                            if (p.description && !label.isConnected) {
                                container.insertBefore(label, select);
                            }
                        }
                        if (typeof p.disabled === 'boolean') {
                            state.disabled = p.disabled;
                            select.disabled = p.disabled;
                        }
                    }
                });

                return () => {
                    el.innerHTML = '';
                };
            }
            export default Dropdown;
        )";
    }

  private:
    void normalize_() {
        // Ensure value is in options, or set to first option if available
        if (!options.empty()) {
            auto it = std::find(options.begin(), options.end(), value);
            if (it == options.end()) {
                value = options[0];
            }
        } else if (value.empty() == false) {
            // If no options but value is set, clear the value
            value = "";
        }
    }
};