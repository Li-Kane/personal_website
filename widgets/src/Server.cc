#include <kdWidgets/Server.h>

/**
 * Server constructor, starts up a worker thread and waits
 * for it to be listening before returning.
 */
Server::Server(int port, std::string title, std::string host) {
    std::cout << "Starting kdWidgets worker on port " << port << "...\n";
    worker_.thread_ =
        std::make_shared<std::thread>(&WorkerThread::runWorkerThread, &worker_, port, title, host);

    std::cout << "Waiting for kdWidgets worker to start...\n";
    // dont return from server constructor until it is up and listening
    while (!worker_.listening_.load()) {
        std::this_thread::sleep_for(std::chrono::milliseconds(1));
    }
}

/**
 * This method runs in the worker thread, it sets up the uWebSocket
 * app and starts listening on the specified port.
 */
void WorkerThread::runWorkerThread(int port, std::string title, std::string host) {
    loop_ = uWS::Loop::get();

    app_ = std::make_unique<uWS::App>();

    app_->ws<PerSocketData>(
            "/ws",
            {/* Settings */
             .compression = uWS::SHARED_COMPRESSOR,
             .maxPayloadLength = 16 * 1024,
             .idleTimeout = 10,
             /* Handlers */
             .open =
                 [this](auto *ws) {
                     connections_.insert(ws);
                     std::cout << "Client connected, total=" << connections_.size() << "\n";

                     // send all registered callbacks
                     for (const auto &[cb_name, cb_msg] : callbacks_) {
                         ws->send(cb_msg.serialize(), uWS::OpCode::TEXT);
                     }
                     // send all existing widgets in insertion order
                     WidgetMessage widget_msg;
                     for (const auto &widget_id : widget_insertion_order_) {
                         auto it = widgets_.find(widget_id);
                         if (it != widgets_.end()) {
                             widget_msg.setData(*it->second);
                             ws->send(widget_msg.serialize(), uWS::OpCode::TEXT);
                         }
                     }
                 },
             .message =
                 [this](auto *ws, std::string_view message, uWS::OpCode opCode) {
                     try {
                         // parse message
                         nlohmann::json j;
                         j = nlohmann::json::parse(message);

                         // route message to the widget's callback
                         std::shared_ptr<Widget> widget = widgets_[j["widget_id"]];
                         if (widget) {
                             std::function<void(const nlohmann::json &)> callback =
                                 widget->getCallback(j["type"]);
                             if (callback) {
                                 callback(j["payload"]);
                             }
                         }
                     } catch (const std::exception &e) {
                         std::cerr << "Error with message: " << e.what() << "\n";
                     }
                 },
             .close =
                 [this](auto *ws, int code, std::string_view message) {
                     connections_.erase(ws);
                     std::cout << "Client disconnected, total=" << connections_.size() << "\n";
                 }})
        /* base index.html and script.js for clients */
        .get("/",
             [title](auto *res, auto *req) {
                 res->writeHeader("Content-Type", "text/html; charset=utf-8")
                     ->writeHeader("Cache-Control", "public, max-age=3600")
                     ->end(Helpers::createIndexHtml(title));
             })
        .get("/script.js",
             [port](auto *res, auto *req) {
                 res->writeHeader("Content-Type", "application/javascript; charset=utf-8")
                     ->writeHeader("Cache-Control", "public, max-age=3600")
                     ->end(Helpers::createScript(port));
             })
        .listen(host,
                port,
                [this, host, port](auto *token) {
                    if (token) {
                        std::cout << "Listening on port " << port << std::endl;
                        listen_ = token;
                        listening_.store(true);
                    }
                })
        .run();
}

/**
 * Add a widget to be managed by this server instance.
 * This will send the widget and all its children to
 * any connected clients
 */
void Server::addWidget(std::shared_ptr<Widget> widget) {
    if (!worker_.listening_.load() || !worker_.loop_ || !widget)
        return;

    worker_.loop_->defer([this, widget] {
        // avoid duplicates
        if (worker_.widgets_.find(widget->getId()) != worker_.widgets_.end()) {
            std::cerr << "Widget with id " << widget->getId()
                      << " already exists, skipping addWidget.\n";
            return;
        }

        // track which widgets we have added
        worker_.widgets_[widget->getId()] = widget;
        worker_.widget_insertion_order_.push_back(widget->getId());

        // send widget message to all connected clients
        WidgetMessage widget_msg;
        widget_msg.setData(*widget);
        toClients(widget_msg);

        // also register any children widgets
        for (const auto &child : widget->getChildren()) {
            addWidget(child);
        }
    });
}

/**
 * Register a callback to be sent to clients. This
 * callback will be loaded in the client to handle
 * specific messages.
 */
void Server::registerCallback(const CallbackMessage msg) {
    if (!worker_.listening_.load() || !worker_.loop_)
        return;

    worker_.loop_->defer([this, msg = std::move(msg)] {
        worker_.callbacks_[msg.new_callback_name] = msg;
        toClients(msg);
    });
}

/**
 * Send a message to all connected clients.
 */
void Server::toClients(const Message &msg) {
    if (!worker_.listening_.load() || !worker_.loop_)
        return;

    std::string m = msg.serialize();
    worker_.loop_->defer([this, m = std::move(m)] {
        for (auto *client : worker_.connections_) {
            client->send(m, uWS::OpCode::TEXT);
        }
    });
}

/**
 * Server destructor, stops the worker thread and
 * cleans up resources.
 */
Server::~Server() {
    if (worker_.loop_ != nullptr) {
        worker_.loop_->defer([this]() {
            worker_.app_->close();
            worker_.app_.reset();
        });
    }

    if (worker_.thread_->joinable()) {
        worker_.thread_->join();
    }
}