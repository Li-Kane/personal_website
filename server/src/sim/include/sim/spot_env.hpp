#pragma once
#include <Karana/Frame/FrameContainer.h>
#include <Karana/SOADyn/Multibody.h>
#include <ament_index_cpp/get_package_share_directory.hpp>
#include <Karana/WebUI/Server.h>
#include <Karana/ProxyScene/ProxySceneNode.h>
#include <Karana/ProxyScene/ProxyScene.h>
#include <Karana/WebScene/WebScene.h>
#include <Karana/Frame/Frame.h>

namespace kf = Karana::Frame;
namespace kd = Karana::Dynamics;
namespace kc = Karana::Core;
namespace ks = Karana::Scene;
namespace km = Karana::Math;

enum class RenderMode {
    NONE,
    HUMAN
};

// keep pointers to our graphics for destruction later
struct GraphicsHandles {
    kc::ks_ptr<Karana::WebUI::Server> web_server;
    kc::ks_ptr<ks::WebScene> web_scene;
};

class SpotEnv {
    public:
        SpotEnv(RenderMode render_mode=RenderMode::NONE, int port=3247, bool sync_real_time = false);
        ~SpotEnv();
        void init_sim();

    private:
        RenderMode render_mode_;
        int port_;
        bool sync_real_time_;
        std::string assets_path_;
        kc::ks_ptr<kf::FrameContainer> fc_;
        kc::ks_ptr<kd::Multibody> mb_;
        GraphicsHandles graphics_handles_;
        kc::ks_ptr<ks::ProxyScene> proxy_scene_;

        void create_environment(int size);
        void createMbody();
        void setupGraphics();
};