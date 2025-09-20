#pragma once
#include <kdWidgets/widgets/Widget.h>

/**
 * A container widget that can hold other widgets.
 * This widget does not render anything itself, it is
 * just a logical container for layout purposes. You can
 * organize children using layout_ styles
 */
class LayoutContainer : public Widget {
  public:
    using Widget::Widget;

    std::string getName() override { return "LayoutContainer"; }

    std::string renderEsm() override {
        return R"(
            function LayoutContainer({id, el, emitWidgetMessage, initialState, style}) {

                return () => {
                    el.innerHTML = '';
                };
            }
            export default LayoutContainer;
        )";
    }

    void addChild(std::shared_ptr<Widget> child) {
        children_.push_back(child);
        child->parent_id = this->getId();
    }

    void addChildren(const std::vector<std::shared_ptr<Widget>> &children) {
        children_.insert(children_.end(), children.begin(), children.end());
        for (const auto &child : children) {
            child->parent_id = this->getId();
        }
    }
};