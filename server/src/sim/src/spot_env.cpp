#include "sim/spot_env.hpp"

void SpotEnv::createMbody() {
    mb_ = kd::Multibody::fromUrdf(assets_path_ + "spot_simple.urdf", fc_);
    mb_->ensureCurrent();
    mb_->resetData();

    std::cout << "[SpotEnv] Multibody created" << std::endl;
    assert(kc::allFinalized());
}

void SpotEnv::create_environment(int size) {
    ks::PhysicalMaterialInfo mat_info;
    mat_info.color = ks::Color::fromHex("0d1440");
}

void SpotEnv::setupGraphics() {
    graphics_handles_ = GraphicsHandles();

    // web server
    graphics_handles_.web_server = std::make_shared<Karana::WebUI::Server>(port_);
    std::cout << "[WebUI] Listening at " << graphics_handles_.web_server->guessUrl() << std::endl;
    std::cout << "[WebUI] Waiting for client(s) [timeout=20s]" << std::endl;
    graphics_handles_.web_server->waitForClients(1, 20.0);

    // web scene
    graphics_handles_.web_scene = ks::WebScene::create(mb_->name() + "_web_scene", graphics_handles_.web_server);
    graphics_handles_.web_scene->defaultCamera()->pointCameraAt(
        km::Vec3(0.0, 15.0, 10.0), km::Vec3(0.0, 5.0, 0.0), km::Vec3(0.0, 0.0, 1.0)
    );

    // proxy scene
    kc::ks_ptr<kf::Frame>  root_frame = mb_->getNewtonianFrame()->container().root();
    proxy_scene_ = ks::ProxyScene::create(mb_->name() + "_proxy_scene", root_frame);
    mb_->setScene(proxy_scene_);
    proxy_scene_->registerClientScene(graphics_handles_.web_scene, root_frame);
}

SpotEnv::SpotEnv(RenderMode render_mode, int port, bool sync_real_time) {
    // Constructor implementation (if needed)
    render_mode_ = render_mode;
    port_ = port;
    sync_real_time_ = sync_real_time;

    init_sim();
}

SpotEnv::~SpotEnv() {
    std::cout << "[SpotEnv] Destructor called" << std::endl;
    // Destructor implementation (if needed)
    if (render_mode_ == RenderMode::HUMAN) {
        graphics_handles_.web_server->sync();
        graphics_handles_.web_server->closeLocalClients();
        graphics_handles_.web_server.reset();
        proxy_scene_->unregisterClientScene(*(graphics_handles_.web_scene));
        kc::discard(graphics_handles_.web_scene);
    }
    kc::discard(proxy_scene_);
    kc::discard(mb_);
    kc::discard(fc_);
    assert(kc::allDestroyed());
}

void SpotEnv::init_sim() {
    // Initialization code for the simulation environment
    assets_path_ = ament_index_cpp::get_package_share_directory("sim") + "/assets/";
    fc_ = kf::FrameContainer::create("root");
    createMbody();

    // setup graphics if enabled
    if (render_mode_ == RenderMode::HUMAN) {
        // Initialize rendering (not implemented here)
        setupGraphics();
    } else {
        proxy_scene_ = ks::ProxyScene::create(mb_->name() + "_proxy_scene", fc_->root());
        mb_->setScene(proxy_scene_);
    }
}