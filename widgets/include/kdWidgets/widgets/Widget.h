// Widget.h
#pragma once
#include <memory>
#include <nlohmann/json.hpp>
#include <string>

/**
 * Base class for all widgets.
 * Widgets must implement renderEsm() to provide
 * the client-side rendering code, and getName()
 * to provide the widget type name.
 * Implementations should also implement getState()
 * and setState() to manage the widget's state.
 */
class Widget {
  public:
    Widget()
        : id_(widgetIdCounter_++) {}

    // factory method to create widgets
    template <class T, class... Args> static std::shared_ptr<T> create(Args &&...args) {
        static_assert(std::is_base_of_v<Widget, T>, "T must inherit from Widget");
        return std::make_shared<T>(std::forward<Args>(args)...);
    }
    virtual ~Widget() = default;

    // must be implemented
    virtual std::string renderEsm() = 0;
    virtual std::string getName() = 0;

    // Accessors
    std::string getId() const { return "widget-" + std::to_string(id_); }
    std::function<void(const nlohmann::json &)> getCallback(const std::string &event) {
        if (callbacks_.find(event) != callbacks_.end()) {
            return callbacks_[event];
        }
        return nullptr;
    }
    std::vector<std::shared_ptr<Widget>> getChildren() const { return children_; }
    virtual nlohmann::json getState() const { return nlohmann::json(); } // default empty state;
    virtual void setState(const nlohmann::json &state) {}                // default no-op

    // Register a callback to be invoked on certain events
    void registerCallback(const std::string &event,
                          std::function<void(const nlohmann::json &)> callback) {
        callbacks_[event] = callback;
    }

    // remove a registered callback
    void unregisterCallback(const std::string &event) { callbacks_.erase(event); }

    // optional attributes
    nlohmann::json layout; // styles applied to the widget's container
    nlohmann::json
        style; // styles applied to the widget itself (specific meaning depends on widget type)
    std::string parent_id; // id of parent widget, if any

  protected:
    std::unordered_map<std::string, std::function<void(const nlohmann::json &)>> callbacks_;
    std::vector<std::shared_ptr<Widget>> children_;

  private:
    int id_;
    inline static int widgetIdCounter_ = 0;
};
