#pragma once
#include <algorithm>
#include <cmath>
#include <kdWidgets/widgets/Widget.h>

class FloatSlider : public Widget {
  public:
    using Widget::Widget;

    // Public state
    double value = 0.0;
    double min = 0.0;
    double max = 100.0;
    double step = 0.1;
    std::string description;
    bool disabled = false;
    bool readout = true;
    std::string readout_format = ".2f";
    std::string orientation = "horizontal"; // "horizontal" | "vertical"
    bool continuous_update = true;

    FloatSlider(double value = 0.0,
                double min = 0.0,
                double max = 100.0,
                double step = 0.1,
                std::string description = "",
                bool readout = true,
                std::string readout_format = ".2f",
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
        , readout_format(std::move(readout_format))
        , orientation(std::move(orientation))
        , continuous_update(continuous_update) {
        normalize_();
    }

    std::string getName() override { return "FloatSlider"; }

    nlohmann::json getState() const override {
        return {{"value", value},
                {"min", min},
                {"max", max},
                {"step", step},
                {"description", description},
                {"disabled", disabled},
                {"readout", readout},
                {"readout_format", readout_format},
                {"orientation", orientation},
                {"continuous_update", continuous_update}};
    }

    void setState(const nlohmann::json &s) override {
        if (s.contains("min") && s["min"].is_number())
            min = s["min"].get<double>();
        if (s.contains("max") && s["max"].is_number())
            max = s["max"].get<double>();
        if (s.contains("step") && s["step"].is_number())
            step = std::max(1e-16, s["step"].get<double>());
        if (s.contains("value") && s["value"].is_number())
            value = s["value"].get<double>();
        if (s.contains("description") && s["description"].is_string())
            description = s["description"].get<std::string>();
        if (s.contains("disabled") && s["disabled"].is_boolean())
            disabled = s["disabled"].get<bool>();
        if (s.contains("readout") && s["readout"].is_boolean())
            readout = s["readout"].get<bool>();
        if (s.contains("readout_format") && s["readout_format"].is_string())
            readout_format = s["readout_format"].get<std::string>();
        if (s.contains("orientation") && s["orientation"].is_string())
            orientation = s["orientation"].get<std::string>();
        if (s.contains("continuous_update") && s["continuous_update"].is_boolean())
            continuous_update = s["continuous_update"].get<bool>();
        normalize_();
    }

    std::string renderEsm() override {
        // Emits 'float_slider_change' with { value }
        // Listens for 'server' CustomEvent with { type: 'state_message', payload: { ...fields } }
        return R"(
            function FloatSlider({ id, el, emitWidgetMessage, initialState, style }) {
                const state = Object.assign({
                    value: 0.0, min: 0.0, max: 100.0, step: 0.1,
                    description: "", disabled: false, readout: true,
                    readout_format: ".2f",
                    orientation: "horizontal", continuous_update: true
                }, initialState || {});

                const root = document.createElement('div');
                root.id = 'floatslider-' + id;
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
                range.step = state.step; // floats allowed
                range.value = state.value;
                range.disabled = !!state.disabled;
                if (state.orientation === 'vertical') {
                    range.style.writingMode = 'bt-lr';
                    range.style.direction = 'rtl';
                    range.style.webkitAppearance = 'slider-vertical';
                    root.style.width = 'fit-content';
                } 

                // ipywidgets FloatSlider readout is formatted text (not editable)
                const readout = document.createElement('input');
                readout.type = 'number';
                readout.id = 'readout-' + id;
                readout.style.minWidth = '5rem';
                readout.style.textAlign = 'right';
                if (!state.readout) readout.style.display = 'none';

                const fmt = (v, fmtstr) => {
                    // Support like ".2f" => fixed 2 decimals
                    if (typeof v !== 'number' || !isFinite(v)) return String(v);
                    const m = /^\.([0-9]+)f$/.exec(fmtstr || "");
                    if (m) { return v.toFixed(parseInt(m[1], 10)); }
                    return String(v);
                };

                const updateBoth = (v) => {
                    const n = Number(v);
                    range.value = String(n);
                    readout.value = fmt(n, state.readout_format);
                };

                const sendChange = (v, phase) => {
                    emitWidgetMessage({
                        el,
                        type: 'float_slider_change',
                        payload: { value: Number(v), phase }
                    });
                };

                // interactions
                if (state.continuous_update) {
                    range.addEventListener('input', (e) => {
                        updateBoth(e.target.value);
                        sendChange(e.target.value, 'changing');
                    });
                    readout.addEventListener('input', (e) => {
                        updateBoth(e.target.value);
                        sendChange(e.target.value, 'changing');
                    });
                } else {
                    range.addEventListener('change', (e) => {
                        updateBoth(e.target.value);
                        sendChange(e.target.value, 'commit');
                    });
                    readout.addEventListener('change', (e) => {
                        updateBoth(e.target.value);
                        sendChange(e.target.value, 'commit');
                    });
                }

                // Assemble
                if (state.description) root.appendChild(label);
                root.appendChild(range);
                root.appendChild(readout);
                updateBoth(state.value);
                el.appendChild(root);

                // Server -> client updates
                el.addEventListener('server', (e) => {
                    const msg = e.detail;
                    if (!msg) return;
                    if (msg.type === 'state_message') {
                        const p = msg.payload?.state || {};
                        if (typeof p.min === 'number')  { state.min = p.min; range.min = p.min; }
                        if (typeof p.max === 'number')  { state.max = p.max; range.max = p.max; }
                        if (typeof p.step === 'number') { state.step = Math.max(1e-16, p.step); range.step = state.step; }
                        if (typeof p.value === 'number') { state.value = p.value; updateBoth(p.value); }
                        if (typeof p.description === 'string') { state.description = p.description; label.textContent = p.description; if (p.description && !label.isConnected) root.insertBefore(label, range); }
                        if (typeof p.disabled === 'boolean') { state.disabled = p.disabled; range.disabled = p.disabled; }
                        if (typeof p.readout === 'boolean') { state.readout = p.readout; readout.style.display = p.readout ? '' : 'none'; }
                        if (typeof p.readout_format === 'string') { state.readout_format = p.readout_format; updateBoth(range.value); }
                        if (typeof p.orientation === 'string') { state.orientation = p.orientation; root.style.flexDirection = (p.orientation === 'vertical') ? 'column' : 'row'; }
                        if (typeof p.continuous_update === 'boolean') { state.continuous_update = p.continuous_update; }
                    }
                });

                return () => { el.innerHTML = ''; };
            }
            export default FloatSlider;
        )";
    }

  private:
    static double snap_(double v, double min, double step) {
        // Snap value to nearest step from min (similar to HTML range behavior)
        double t = (v - min) / step;
        double r = std::round(t);
        return min + r * step;
    }

    void normalize_() {
        if (min > max)
            std::swap(min, max);
        if (step <= 0.0)
            step = 1e-16;
        // clamp then snap to step grid
        value = std::clamp(value, min, max);
        value = std::clamp(snap_(value, min, step), min, max);
    }
};
