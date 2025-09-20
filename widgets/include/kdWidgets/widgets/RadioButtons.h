#pragma once
#include <algorithm>
#include <kdWidgets/widgets/Widget.h>
#include <string>
#include <vector>

/**
 * A set of radio buttons allowing a single selection
 * from a list of options. Emits 'radio_change' event
 * with payload { value: "the selected option" }.
 */
class RadioButtons : public Widget {
  public:
    using Widget::Widget;

    // Public state
    std::vector<std::string> options;
    std::string value;
    std::string description;
    bool disabled = false;

    RadioButtons(std::vector<std::string> options = {},
                 std::string value = "",
                 std::string description = "",
                 bool disabled = false)
        : options(std::move(options))
        , value(std::move(value))
        , description(std::move(description))
        , disabled(disabled) {
        normalize_();
    }

    std::string getName() override { return "RadioButtons"; }

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
        // Emits 'radio_change' with { value }
        return R"(
            function RadioButtons({ id, el, emitWidgetMessage, initialState, style }) {
                const state = Object.assign({
                    options: [],
                    value: "",
                    description: "",
                    disabled: false
                }, initialState || {});

                // Ensure value is valid or set to first option
                if (state.options.length > 0 && !state.options.includes(state.value)) {
                    state.value = state.options[0];
                }

                const container = document.createElement('div');
                container.style.display = 'flex';
                container.style.flexDirection = 'column';
                container.style.gap = '0.5rem';

                const label = document.createElement('div');
                label.textContent = state.description;
                label.style.fontWeight = '500';
                label.style.marginBottom = '0.25rem';

                const radioContainer = document.createElement('div');
                radioContainer.style.display = 'flex';
                radioContainer.style.flexDirection = 'column';
                radioContainer.style.gap = '0.25rem';

                // Create radio buttons
                const updateRadios = () => {
                    radioContainer.innerHTML = '';
                    
                    state.options.forEach((opt, index) => {
                        const radioWrapper = document.createElement('div');
                        radioWrapper.style.display = 'flex';
                        radioWrapper.style.alignItems = 'center';
                        radioWrapper.style.gap = '0.5rem';
                        
                        const radio = document.createElement('input');
                        radio.type = 'radio';
                        radio.id = `radio-${id}-${index}`;
                        radio.name = `radiogroup-${id}`;
                        radio.value = opt;
                        radio.checked = (opt === state.value);
                        radio.disabled = state.disabled;
                        
                        const radioLabel = document.createElement('label');
                        radioLabel.htmlFor = `radio-${id}-${index}`;
                        radioLabel.textContent = opt;
                        radioLabel.style.cursor = state.disabled ? 'default' : 'pointer';
                        radioLabel.style.userSelect = 'none';
                        
                        // Event handler
                        radio.addEventListener('change', (e) => {
                            if (e.target.checked) {
                                state.value = e.target.value;
                                emitWidgetMessage({
                                    el,
                                    type: 'radio_change',
                                    payload: { value: state.value }
                                });
                            }
                        });
                        
                        radioWrapper.appendChild(radio);
                        radioWrapper.appendChild(radioLabel);
                        radioContainer.appendChild(radioWrapper);
                    });
                };

                updateRadios();

                // Assemble
                if (state.description) {
                    container.appendChild(label);
                }
                container.appendChild(radioContainer);
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
                            updateRadios();
                        }
                        if (typeof p.description === 'string') {
                            state.description = p.description;
                            label.textContent = p.description;
                            if (p.description && !label.isConnected) {
                                container.insertBefore(label, radioContainer);
                            }
                        }
                        if (typeof p.disabled === 'boolean') {
                            state.disabled = p.disabled;
                            const radios = radioContainer.querySelectorAll('input[type="radio"]');
                            radios.forEach(r => r.disabled = p.disabled);
                            const labels = radioContainer.querySelectorAll('label');
                            labels.forEach(l => l.style.cursor = p.disabled ? 'default' : 'pointer');
                        }
                    }
                });

                return () => {
                    el.innerHTML = '';
                };
            }
            export default RadioButtons;
        )";
    }

  private:
    void normalize_() {
        // If no value set or value not in options, default to first option
        if (!options.empty()) {
            if (value.empty() ||
                std::find(options.begin(), options.end(), value) == options.end()) {
                value = options[0];
            }
        } else {
            value = "";
        }
    }
};