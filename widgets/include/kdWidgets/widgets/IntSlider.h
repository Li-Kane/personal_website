#pragma once
#include <algorithm>
#include <kdWidgets/widgets/Widget.h>
#include <nlohmann/json.hpp>

/**
 * A slider widget for selecting integer values.
 * Emits 'int_slider_change' event with payload { value: int }.
 */
class IntSlider : public Widget {
  public:
    using Widget::Widget;

    // Public state
    int value;
    int min;
    int max;
    int step;
    std::string description;
    bool disabled;
    bool readout;
    std::string orientation;
    bool continuous_update;

    IntSlider(int value = 0,
              int min = 0,
              int max = 100,
              int step = 1,
              std::string description = "",
              bool readout = true,
              bool continuous_update = true,
              bool disabled = false,
              std::string orientation = "horizontal")
        : value(value)
        , min(min)
        , max(max)
        , step(step)
        , description(std::move(description))
        , disabled(disabled)
        , readout(readout)
        , orientation(std::move(orientation))
        , continuous_update(continuous_update) {
        normalize_();
    }

    std::string getName() override { return "IntSlider"; }

    nlohmann::json getState() const override {
        return {{"value", value},
                {"min", min},
                {"max", max},
                {"step", step},
                {"description", description},
                {"disabled", disabled},
                {"readout", readout},
                {"orientation", orientation},
                {"continuous_update", continuous_update}};
    }

    void setState(const nlohmann::json &s) override {
        if (s.contains("min") && s["min"].is_number_integer())
            min = s["min"].get<int>();
        if (s.contains("max") && s["max"].is_number_integer())
            max = s["max"].get<int>();
        if (s.contains("step") && s["step"].is_number_integer())
            step = std::max(1, s["step"].get<int>());
        if (s.contains("value") && s["value"].is_number_integer())
            value = s["value"].get<int>();
        if (s.contains("description") && s["description"].is_string())
            description = s["description"].get<std::string>();
        if (s.contains("disabled") && s["disabled"].is_boolean())
            disabled = s["disabled"].get<bool>();
        if (s.contains("readout") && s["readout"].is_boolean())
            readout = s["readout"].get<bool>();
        if (s.contains("orientation") && s["orientation"].is_string())
            orientation = s["orientation"].get<std::string>();
        if (s.contains("continuous_update") && s["continuous_update"].is_boolean())
            continuous_update = s["continuous_update"].get<bool>();
        normalize_();
    }

    std::string renderEsm() override {
        return R"(
            function IntSlider({ id, el, emitWidgetMessage, initialState, style }) {
                const state = Object.assign({
                    value: 0, min: 0, max: 100, step: 1,
                    description: "", disabled: false, readout: true,
                    orientation: "horizontal", continuous_update: true
                }, initialState || {});

                const root = document.createElement('div');
                root.id = 'intslider-' + id;
                root.style.display = 'flex';
                root.style.alignItems = 'center';
                root.style.gap = '0.5rem';
                root.style.flexDirection = (state.orientation === 'vertical') ? 'column' : 'row';

                const label = document.createElement('label');
                label.htmlFor = 'range-' + id;
                label.textContent = state.description || '';
                label.style.minWidth = 'auto';

                const range = document.createElement('input');
                range.type = 'range';
                range.id = 'range-' + id;
                range.min = state.min;
                range.max = state.max;
                range.step = state.step;
                range.value = state.value;
                range.disabled = !!state.disabled;
                if (state.orientation === 'vertical') {
                    range.style.writingMode = 'bt-lr';
                    range.style.direction = 'rtl';
                    range.style.webkitAppearance = 'slider-vertical';
                    root.style.width = 'fit-content';
                } 

                const readout = document.createElement('input');
                readout.type = 'number';
                readout.id = 'readout-' + id;
                readout.value = state.value;
                readout.min = state.min;
                readout.max = state.max;
                readout.step = state.step;
                readout.style.width = '6rem';
                if (!state.readout) readout.style.display = 'none';
                readout.disabled = !!state.disabled;

                const updateBoth = (newValue) => {
                    const n = Number(newValue);
                    range.value = String(newValue);
                    readout.value = String(newValue);
                };

                const sendChange = (newValue) => {
                    emitWidgetMessage({
                        el,
                        type: 'int_slider_change',
                        payload: { value: Number(newValue)}
                    });
                };

                // interactions
                if (state.continuous_update) {
                    range.addEventListener('input', (e) => {
                        updateBoth(e.target.value);
                        sendChange(e.target.value);
                    });
                    readout.addEventListener('input', (e) => {
                        updateBoth(e.target.value);
                        sendChange(e.target.value);
                    });
                } else {
                    range.addEventListener('change', (e) => {
                        updateBoth(e.target.value);
                        sendChange(e.target.value);
                    });
                    readout.addEventListener('change', (e) => {
                        updateBoth(e.target.value);
                        sendChange(e.target.value);
                    });
                }

                // Assemble
                if (state.description) root.appendChild(label);
                root.appendChild(range);
                root.appendChild(readout);
                el.appendChild(root);

                // Server -> client updates
                el.addEventListener('server', (e) => {
                    const msg = e.detail;
                    if (!msg) return;
                    if (msg.type === 'state_message') {
                        const p = msg.payload?.state || {};
                        if (typeof p.min === 'number')  { state.min = p.min; range.min = p.min; readout.min = p.min; }
                        if (typeof p.max === 'number')  { state.max = p.max; range.max = p.max; readout.max = p.max; }
                        if (typeof p.step === 'number') { state.step = Math.max(1, p.step); range.step = state.step; readout.step = state.step; }
                        if (typeof p.value === 'number') { state.value = p.value; updateBoth(p.value); }
                        if (typeof p.description === 'string') { state.description = p.description; label.textContent = p.description; if (p.description && !label.isConnected) root.insertBefore(label, range); }
                        if (typeof p.disabled === 'boolean') { state.disabled = p.disabled; range.disabled = p.disabled; readout.disabled = p.disabled; }
                        if (typeof p.readout === 'boolean') { state.readout = p.readout; readout.style.display = p.readout ? '' : 'none'; }
                        if (typeof p.orientation === 'string') { state.orientation = p.orientation; root.style.flexDirection = (p.orientation === 'vertical') ? 'column' : 'row'; }
                        if (typeof p.continuous_update === 'boolean') { state.continuous_update = p.continuous_update; }
                    }
                });

                return () => { el.innerHTML = ''; };
            }
            export default IntSlider;
        )";
    }

  private:
    void normalize_() {
        if (min > max)
            std::swap(min, max);
        if (step <= 0)
            step = 1;
        value = std::clamp(value, min, max);
    }
};
