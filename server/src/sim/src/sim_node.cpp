#include <chrono>
#include <memory>
#include <string>

#include "rclcpp/rclcpp.hpp"
#include "sim_interfaces/msg/from_sim.hpp"
#include "sim_interfaces/msg/from_server.hpp"
#include "sim/spot_env.hpp"

using namespace std::chrono_literals;

class SimNode : public rclcpp::Node {
public:
    SimNode()
    : Node("sim_node"),
      spot_env_(RenderMode::HUMAN, 3247, true)
    {
        publisher_ = this->create_publisher<sim_interfaces::msg::FromSim>("from_sim", 1);
        timer_ = this->create_wall_timer(500ms, std::bind(&SimNode::timer_callback, this));
        subscription_ =
        this->create_subscription<sim_interfaces::msg::FromServer>("from_server", 10, std::bind(&SimNode::topic_callback, this, std::placeholders::_1));
    }

private:
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::Publisher<sim_interfaces::msg::FromSim>::SharedPtr publisher_;
    rclcpp::Subscription<sim_interfaces::msg::FromServer>::SharedPtr subscription_;
    SpotEnv spot_env_;

    void timer_callback()
    {
        auto message = sim_interfaces::msg::FromSim();
        message.sim_data = {0.0f, 0.0f, 0.0f};
        publisher_->publish(message);
    }

    void topic_callback(const sim_interfaces::msg::FromServer & msg) const
    {
        std::string array_str = "[";
        for (size_t i = 0; i < msg.server_data.size(); ++i) {
            array_str += std::to_string(msg.server_data[i]);
            if (i < msg.server_data.size() - 1) {
                array_str += ", ";
            }
        }
        array_str += "]";
        RCLCPP_INFO(this->get_logger(), "I heard: '%s'", array_str.c_str());
    }
};

int main(int argc, char * argv[])
{
    rclcpp::init(argc, argv);
    rclcpp::spin(std::make_shared<SimNode>());
    rclcpp::shutdown();
    return 0;
}