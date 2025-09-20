#include <Karana/CoalScene/CoalScene.h>
#include <Karana/Collision/FrameCollider.h>
#include <Karana/Collision/PenaltyContact.h>
#include <Karana/Frame/FrameContainer.h>
#include <Karana/GeneralKModels/SyncRealTime.h>
#include <Karana/GeneralKModels/UniformGravity.h>
#include <Karana/GeneralKModels/UpdateProxyScene.h>
#include <Karana/KCore/Base.h>
#include <Karana/Math/HomTran.h>
#include <Karana/Math/SpatialInertia.h>
#include <Karana/ProxyScene/ProxyScene.h>
#include <Karana/ProxyScene/ProxySceneNode.h>
#include <Karana/SOADyn/BodyBase.h>
#include <Karana/SOADyn/Multibody.h>
#include <Karana/SOADyn/PhysicalBody.h>
#include <Karana/SOADyn/PhysicalHinge.h>
#include <Karana/SOADyn/PinSubhinge.h>
#include <Karana/SOADyn/StatePropagator.h>
#include <Karana/SOADyn/SubTree.h>
#include <Karana/Scene/Scene.h>
#include <Karana/Scene/ScenePartSpec.h>
#include <Karana/WebScene/WebScene.h>
#include <Karana/WebUI/Server.h>
#include <cstdlib>
#include <iostream>
#include <kdWidgets/Helpers.h>
#include <kdWidgets/Server.h>
#include <kdWidgets/messages/StateMessage.h>
#include <kdWidgets/widgets/Button.h>
#include <kdWidgets/widgets/Iframe.h>
#include <kdWidgets/widgets/IntSlider.h>
#include <kdWidgets/widgets/Label.h>
#include <kdWidgets/widgets/LayoutContainer.h>
#include <kdWidgets/widgets/TextInput.h>
#include <string>
#include <unordered_map>

/**
 * Example that shows interacting with a kdFlex simulation
 * using kdWidgets. The simulation is run with n links depending
 * on user input from a text input widget. The simulation
 * is displayed in an iframe widget that connects to a
 * Karana WebSocket server running a Karana WebGL scene.
 */

namespace kc = Karana::Core;
namespace kf = Karana::Frame;
namespace kd = Karana::Dynamics;
namespace km = Karana::Math;
namespace ks = Karana::Scene;

struct GraphicsHandles {
    kc::ks_ptr<ks::ProxySceneNode> axes_node;
    kc::ks_ptr<ks::WebScene> graphics_scene;
};

// procedurally generate a n-link pendulum multibody
kc::ks_ptr<kd::Multibody> createMbody(int n_links, kc::ks_ptr<kf::FrameContainer> fc) {
    kc::ks_ptr<kd::Multibody> mb = kd::Multibody::create("mb", fc);

    // inertia used for both bodies
    km::SpatialInertia spI(2.0, km::Vec3::Zero(), Eigen::DiagonalMatrix<double, 3>(3, 2, 1));

    // inboard to joint transform used for both bodies
    km::HomTran ib2j;

    // body to joint transform used for both bodies
    km::HomTran b2j(km::Vec3(0, 0, 1.0));

    // adding colored material)
    ks::PhysicalMaterialInfo mat_info;
    mat_info.color = ks::Color::BLUE;
    kc::ks_ptr<ks::PhysicalMaterial> blue = std::make_shared<ks::PhysicalMaterial>(mat_info);
    mat_info.color = ks::Color::LIGHTBLUE;
    kc::ks_ptr<ks::PhysicalMaterial> light_blue = std::make_shared<ks::PhysicalMaterial>(mat_info);

    // our geometries
    kc::ks_ptr<ks::SphereGeometry> sphere_geometry = std::make_shared<ks::SphereGeometry>(0.3);
    kc::ks_ptr<ks::CylinderGeometry> cylinder_geometry =
        std::make_shared<ks::CylinderGeometry>(0.025, 1.0);

    // our transforms
    km::HomTran collisions_transform = km::HomTran(km::Vec3(0.0, 0.0, 0.0));
    km::HomTran vis_transform =
        km::HomTran(km::UnitQuaternion(Eigen::AngleAxis(M_PI / 2, Eigen::Vector3d(1.0, 0.0, 0.0))),
                    km::Vec3(0.0, 0.0, 0.5));

    // Add a scene part that is for collisions and
    ks::ScenePartSpec sp_col;
    sp_col.name = "sp_collision";
    sp_col.geometry = sphere_geometry;
    sp_col.material = blue;
    sp_col.transform = collisions_transform;
    sp_col.scale = km::Vec3(1, 1, 1);

    // Add a scene part that is purely visual
    ks::ScenePartSpec sp_vis;
    sp_vis.name = "sp_graphics";
    sp_vis.geometry = cylinder_geometry;
    sp_vis.material = light_blue;
    sp_vis.transform = vis_transform;
    sp_vis.scale = km::Vec3(1, 1, 1);
    sp_vis.layers = ks::LAYER_GRAPHICS;

    // params for each body in pendulum
    kd::PhysicalBodyParams params;
    params.spI = spI;
    params.axes = {km::Vec3(0.0, 1.0, 0.0)};
    params.body2joint_T = b2j;
    params.inb2joint_T = ib2j;
    params.scene_part_specs = {sp_col, sp_vis};

    auto vroot = std::static_pointer_cast<kd::PhysicalBody>(mb->virtualRoot());
    kd::PhysicalBody::addSerialChain(
        "body", n_links, *vroot, kd::HingeBase::HINGE_TYPE::BALL, &params);

    // checks and set initial state
    mb->ensureCurrent();
    mb->resetData();
    assert(kc::allFinalized());

    mb->dumpTree("mb");
    return mb;
}

// Create a graphics scene and setup the WebUI server
GraphicsHandles setupGraphics(const kc::ks_ptr<Karana::WebUI::Server> &web_server,
                              kd::Multibody &mb,
                              int num_links) {
    GraphicsHandles out;
    out.graphics_scene = ks::WebScene::create(mb.name() + "_webscene", web_server);
    out.graphics_scene->defaultCamera()->pointCameraAt(
        km::Vec3(-4, 8, -num_links / 2 + 2), km::Vec3(0, 0, -num_links / 2), km::Vec3(0, 0, 1));
    out.graphics_scene->_setShadows(km::Vec3(0, 0, -1));

    kc::ks_ptr<kf::Frame> root_frame = mb.getNewtonianFrame()->container().root();
    kc::ks_ptr<ks::ProxyScene> proxy_scene =
        ks::ProxyScene::create(mb.name() + "_proxy_scene", root_frame);
    mb.setScene(proxy_scene);
    proxy_scene->registerClientScene(out.graphics_scene, root_frame);

    out.axes_node = ks::ProxySceneNode::create("root_axes", proxy_scene);
    out.axes_node->graphics(*(out.graphics_scene))->showAxes(0.5);
    return out;
}

// add wall, ground, and top connection objects
void addObjects(kd::Multibody &mb, int num_links) {
    kc::ks_ptr<ks::ProxyScene> proxy_scene = mb.getScene();
    // alternate geometries
    kc::ks_ptr<ks::BoxGeometry> box_geom = std::make_shared<ks::BoxGeometry>(0.1, 0.1, 0.1);
    kc::ks_ptr<ks::CapsuleGeometry> capsule_geom = std::make_shared<ks::CapsuleGeometry>(0.1, 0.15);

    // create an obstacle wall  to be placed in the path of the pendulum
    kc::ks_ptr<ks::BoxGeometry> obstacle_geom =
        std::make_shared<ks::BoxGeometry>(0.5, 1.8, 0.1 + num_links);

    // create a ground for the pendulum to collide with
    kc::ks_ptr<ks::BoxGeometry> ground_geom = std::make_shared<ks::BoxGeometry>(7.5, 7.5, 0.5);

    // create a connection part for the top of the pendulum
    kc::ks_ptr<ks::BoxGeometry> connection_geom =
        std::make_shared<ks::BoxGeometry>(0.25, 0.25, 0.1);

    // create various visual materials to color the bodies
    ks::PhysicalMaterialInfo mat_info;
    mat_info.color = ks::Color::DARKSEAGREEN;
    kc::ks_ptr<ks::PhysicalMaterial> seagreen = std::make_shared<ks::PhysicalMaterial>(mat_info);
    mat_info.color = ks::Color::BEIGE;
    kc::ks_ptr<ks::PhysicalMaterial> beige = std::make_shared<ks::PhysicalMaterial>(mat_info);
    mat_info.color = ks::Color::BLACK;
    kc::ks_ptr<ks::PhysicalMaterial> black = std::make_shared<ks::PhysicalMaterial>(mat_info);

    // add the wall
    kc::ks_ptr<ks::ProxyScenePart> obstacle_part =
        ks::ProxyScenePart::create("obstacle_part", obstacle_geom, proxy_scene, seagreen);
    obstacle_part->setTranslation(km::Vec3(2.75, 0, -num_links / 2 - 0.1));

    // add the ground
    kc::ks_ptr<ks::ProxyScenePart> ground =
        ks::ProxyScenePart::create("ground", ground_geom, proxy_scene, beige, ks::LAYER_ALL);
    ground->setTranslation(km::Vec3(0, 0, -num_links));

    // add an upper connection point for the pendulum that is purely visual
    kc::ks_ptr<ks::ProxyScenePart> connection = ks::ProxyScenePart::create(
        "connection", connection_geom, proxy_scene, black, ks::LAYER_GRAPHICS);
}

// setup collision detection
kc::ks_ptr<ks::CoalScene> setupCollisionScene(kd::Multibody &mb) {
    // Register a CoalScene instance to perform collision and distance queries
    kc::ks_ptr<ks::CoalScene> col_scene = ks::CoalScene::create("collision_scene");
    kc::ks_ptr<kd::PhysicalBody> vroot =
        std::static_pointer_cast<kd::PhysicalBody>(mb.virtualRoot());
    mb.getScene()->registerClientScene(col_scene, vroot, ks::LAYER_COLLISION);
    return col_scene;
}

// Setup state propagator and integrator
// then register models and callbacks to the state propagator
std::shared_ptr<kd::StatePropagator> setupPropagator(kc::ks_ptr<kd::Multibody> &mb,
                                                     kc::ks_ptr<ks::CoalScene> &col_scene,
                                                     int num_links) {
    kc::ks_ptr<ks::ProxyScene> proxy_scene = mb->getScene();
    kc::ks_ptr<ks::ProxySceneNode> root_scene_node =
        ks::ProxySceneNode::create("root_scene_node", proxy_scene);
    root_scene_node->graphics()->showAxes(0.5);

    // Set propagtor, integrator and integrator options
    std::shared_ptr<kd::StatePropagator> sp =
        kd::StatePropagator::create(mb, km::IntegratorType::CVODE);
    const kc::ks_ptr<km::Integrator> &integrator = sp->getIntegrator();
    kd::StatePropagator::spOptions &sp_options = sp->getOptions();

    // add uniform gravity model
    kc::ks_ptr<Karana::Models::UniformGravity> ug =
        Karana::Models::UniformGravity::create("gravity", mb);
    ug->params->g = km::Vec3{0, 0, -9.81};
    sp->registerModel(ug);
    ug.reset();

    // Make sure the visualization scene is updated after each state change.
    kc::ks_ptr<Karana::Models::UpdateProxyScene> ups =
        Karana::Models::UpdateProxyScene::create("update_proxy_scene", mb->getScene());
    sp->registerModel(ups);
    ups.reset();

    // sync the simulation time with real-time.
    kc::ks_ptr<Karana::Models::SyncRealTime> sync_rt =
        Karana::Models::SyncRealTime::create("sync_real_time", 1.0);
    sp->registerModel(sync_rt);
    sync_rt.reset();

    // add penalty contact model
    Karana::Collision::FrameCollider kf_collider(proxy_scene, col_scene);
    kc::ks_ptr<Karana::Models::PenaltyContact> mdl =
        Karana::Models::PenaltyContact::create("penalty_contact", kf_collider);

    // register penalty contact model on each body
    for (int link = 0; link < num_links; link++) {
        std::string body_string = "body_" + std::to_string(link);
        auto phys_body = kc::static_pointer_cast<kd::PhysicalBody>(mb->getBody(body_string));
        mdl->registerBody(phys_body);
    }

    // set model parameters
    mdl->params->kp = 100000;
    mdl->params->kc = 20000;
    mdl->params->mu = 0.3;
    mdl->params->n = 1.5;
    mdl->params->linear_region_tol = 1e-3;
    sp->registerModel(mdl);
    mdl.reset();

    return sp;
}

// Initialize the state of the multibody and integrator
void initializeState(kd::Multibody &mb, kd::StatePropagator &sp) {
    // modify the initial multibody state
    kc::ks_ptr<kd::BodyBase> bd1 = mb.getBody("body_0");
    bd1->parentHinge()->subhinge(0)->setQ(km::Vec3(0.0, M_PI / 3, 0.0)); // set initial angle
    bd1->parentHinge()->subhinge(0)->setU(km::Vec3(0.0, -0.5, 0.0));     // set initial velocity

    // set integrator state
    sp.setState(km::Ktime(0), mb.dynamicsToState());
}

// Run the simulation for a specified duration
void runSimulation(kd::StatePropagator &sp) {
    // Register timed event for periodic updates
    km::Ktime h(10000000);
    auto t = kd::TimedEvent::create("hop_size", h, [](const km::Ktime &) {}, false);
    t->period = h;
    sp.registerTimedEvent(t);
    t.reset();

    // run the simulation
    sp.advanceTo(km::secondsToKtime(5));
}

int main() {
    nlohmann::json col_layout = {
        {"display", "flex"}, {"flexDirection", "column"}, {"height", "100%"}, {"width", "100%"}};
    nlohmann::json tabbar_layout = {
        {"display", "flex"},
        {"flexDirection", "row"},
        {"flex", "1"},
        {"alignItems", "center"},
        {"gap", "2rem"},
        {"padding", "0 2rem"},
    };
    nlohmann::json iframe_layout = {
        {"flex", "12"},
        {"display", "flex"},
        {"justifyContent", "center"},
        {"alignItems", "center"},
    };
    nlohmann::json iframe_style = {
        {"height", "95%"},
        {"width", "95%"},
    };
    auto colContainer = Widget::create<LayoutContainer>();
    auto tabbarContainer = Widget::create<LayoutContainer>();
    auto label = Widget::create<Label>("Enter Num Links: ", TextType::H1);
    auto textInput = Widget::create<TextInput>();
    auto Iframe1 = Widget::create<Iframe>("http://localhost:2555");
    colContainer->layout = col_layout;
    tabbarContainer->layout = tabbar_layout;
    tabbarContainer->addChildren({label, textInput});
    Iframe1->layout = iframe_layout;
    Iframe1->style = iframe_style;
    colContainer->addChildren({tabbarContainer, Iframe1});
    auto server = Server::create();
    server->addWidget(colContainer);

    int port = 2555;
    kc::ks_ptr<Karana::WebUI::Server> web_server = std::make_shared<Karana::WebUI::Server>(port);
    web_server->waitForClients(1);

    textInput->registerCallback("text_input", [&](const nlohmann::json &msg) {
        if (msg.contains("value") && msg["value"].is_string()) {
            std::string num_links_str = msg["value"];
            int num_links = std::stoi(num_links_str);
            if (num_links < 1) {
                std::cout << "Number of links must be at least 1" << std::endl;
                return;
            }
            std::cout << "Creating simulation with " << num_links << " links" << std::endl;
            kc::ks_ptr<kf::FrameContainer> fc = kf::FrameContainer::create("root");
            kc::ks_ptr<kd::Multibody> mb = createMbody(num_links, fc);

            // setup graphics server
            GraphicsHandles handles = setupGraphics(web_server, *mb, num_links);
            // setup collision detection
            kc::ks_ptr<ks::CoalScene> col_scene = setupCollisionScene(*mb);

            // add the ground, wall, and top connection
            addObjects(*mb, num_links);

            // set up state propagator
            std::shared_ptr<kd::StatePropagator> sp = setupPropagator(mb, col_scene, num_links);

            // initialize the state
            initializeState(*mb, *sp);

            runSimulation(*sp);

            kc::discard(sp);
            auto &scene = mb->getScene();
            kc::discard(handles.axes_node);
            handles.axes_node.reset();
            scene->unregisterClientScene(*(handles.graphics_scene));
            kc::discard(handles.graphics_scene);
            kc::discard(scene);
            kc::discard(mb);
            kc::discard(fc);
        }
    });

    std::cout << "Press Enter to exit...\n";
    std::cin.get();
    web_server->sync();
    web_server->closeLocalClients();
    web_server.reset();
    server.reset();
    return 0;
}
