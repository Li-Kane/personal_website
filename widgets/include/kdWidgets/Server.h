#pragma once
#include <atomic>
#include <filesystem>
#include <fstream>
#include <future>
#include <kdWidgets/Helpers.h>
#include <kdWidgets/messages/CallbackMessage.h>
#include <kdWidgets/messages/Message.h>
#include <kdWidgets/messages/StateMessage.h>
#include <kdWidgets/messages/WidgetMessage.h>
#include <mutex>
#include <nlohmann/json.hpp>
#include <string>
#include <thread>
#include <unordered_map>
#include <unordered_set>
#include <uwebsockets/App.h>

struct PerSocketData {
    int id;
};

/**
 * This struct tracks the state of a worker thread.
 */
struct WorkerThread {
    void runWorkerThread(int port, std::string title, std::string host);
    std::atomic<bool> listening_ = false;

    /* uWebSocket worker listens on separate port, or share the same port (works on Linux). */
    struct us_listen_socket_t *listen_;

    /* Every thread has its own Loop, and uWS::Loop::get() returns the Loop for current thread.*/
    struct uWS::Loop *loop_;

    /* Need to capture the uWS::App object (instance). */
    std::shared_ptr<uWS::App> app_;

    /* Thread object for uWebSocket worker */
    std::shared_ptr<std::thread> thread_;

    /* All connected WebSocket clients */
    std::unordered_set<uWS::WebSocket<false, true, PerSocketData> *> connections_;

    /* A map of all widgets */
    std::unordered_map<std::string, std::shared_ptr<Widget>> widgets_;
    /* A vector tracking widget insertion order */
    std::vector<std::string> widget_insertion_order_;
    /* All registered frontend Callbacks */
    std::unordered_map<std::string, CallbackMessage> callbacks_;
};

/**
 * Server class to manage widgets and client connections.
 * This class will start up a uWebSocket server in a separate thread
 * and defer methods to that thread's event loop. It is assumed
 * there will only be one worker thread.
 */
class Server {
  public:
    Server(int port = 9001, std::string title = "kdWidgets", std::string host = "0.0.0.0");
    template <typename... Args> static std::shared_ptr<Server> create(Args &&...args) {
        return std::make_shared<Server>(std::forward<Args>(args)...);
    }
    ~Server();

    void addWidget(std::shared_ptr<Widget> widget);
    void registerCallback(const CallbackMessage msg);
    void toClients(const Message &msg);

  private:
    WorkerThread worker_;
};