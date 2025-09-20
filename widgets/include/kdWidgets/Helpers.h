#pragma once
#include <cstdlib>
#include <functional>
#include <kdWidgets/Server.h>
#include <nlohmann/json.hpp>
#include <string>

namespace Helpers {

    /**
     * Create a basic index.html page with the given title
     */
    inline std::string createIndexHtml(std::string title) {
        return R"(
    <!doctype html>
    <html>
    <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>)" + title +
               R"(</title>
    </head>
    <body style="margin:0">
        <main style="width: 100vw; height: 100vh; overflow: scroll;">
        </main>
        <script type="module" src="./script.js"></script>
    </body>
    </html>
    )";
    }

    /**
     * Create the client-side script to connect to the server
     * and handle messages and callbacks.
     */
    inline std::string createScript(int port) {
        std::string host = "127.0.0.1";
        char *env_host = std::getenv("KARANA_WEBUI_ADDRESS");
        if (env_host) {
            host = std::string(env_host);
        }

        return R"(
    // setup a global root element for widgets to attach to
    let root = document.querySelector("main");
    const websocket = new WebSocket("ws://)" +
               host + R"(:)" + std::to_string(port) + R"(/ws");
    // pend an invoke if the callback is still loading
    const pendingInvokes = new Map();
    // map of name -> Function or null if loading
    const callbacks = new Map();
    callbacks.set("register_callback", registerCallback);
    callbacks.set("add_widget", addWidget);
    callbacks.set("default", defaultMessageHandler);
    // registry of widget_id -> element
    const widgets = new Map();

    // handle incoming messages
    websocket.addEventListener("message", async (ev) => {
        let msg;
        try { msg = JSON.parse(ev.data); } catch (e) { console.error("Bad JSON", e); return; }

        const callback = callbacks.get(msg.callback_name);
        if (callback) {
            callback(msg);
        } else if (callback === null) {
            // still loading callback, enqueue
            enqueueInvoke(msg.callback_name, msg);
        } else {
            // not found, use default handler
            defaultMessageHandler(msg);
        }
        });

        // forward all "widget" events to the server
        root.addEventListener("widget", (e) => {
        const element = e.target;
        const widgetId = e.detail?.widgetId ?? element.id ?? null;
        const msg = {
            type: e.detail?.type ?? "unknown",
            widget_id: widgetId,
            payload: e.detail?.payload ?? null,
        }
        websocket.send(JSON.stringify(msg));
        });

        // helper for widgets to send messages
        function emitWidgetMessage({el, type, payload}) {
        el.dispatchEvent(new CustomEvent("widget", {
            detail: { type, widgetId: el.id, payload },
            bubbles: true,
            composed: true,
        }));
        }

        // emit message from server to the widget by its id
        function emitServerMessage({widgetId, type, payload}) {
        const el = document.getElementById(widgetId);
        if (el) {
            el.dispatchEvent(new CustomEvent("server", {
            detail: { type, payload },
            bubbles: true,
            composed: true,
            }));
        }
    }

    // Enqueue an invoke to be called once the callback is loaded
    function enqueueInvoke(name, msg) {
        if (!pendingInvokes.has(name)) {
            pendingInvokes.set(name, []);
        }
        pendingInvokes.get(name).push(msg);
        }

        // Flush all pending invokes for a callback name
        function flushPendingInvokes(name, callback) {
        const invokes = pendingInvokes.get(name) || [];
        for (const msg of invokes) {
            if (callback) {
            callback({ msg });
            }
        }
        pendingInvokes.delete(name);
    }

    /** Load ESM from source text. */
    async function importEsmFromString(src, name) {
        if (!src || !name) {
            console.error("importEsmFromString requires src and name");
            return;
        }
        const url = URL.createObjectURL(new Blob(
            [src + `\n//# sourceURL=${name}.js`],
            { type: "text/javascript" }
        ));
        try {
            return await import(url);
        } finally {
            queueMicrotask(() => URL.revokeObjectURL(url));
        }
        }

        // special handler to register a new callback
        async function registerCallback() {
        // set up a promise to load the callback
        const callbackPromise = (async () => {
        const mod = await importEsmFromString(msg.callback, msg.new_callback_name);
            if (!mod || !mod.default || typeof mod.default !== 'function') {
            throw new Error("Failed to load callback ESM or setup function missing");
            }
            const setup = mod.default;
            const callback = setup({root, emitWidgetMessage, emitServerMessage, importEsmFromString});
            if (typeof callback !== 'function') throw new Error("Callback setup did not return a function");
            return callback;
        })();

        // mark as loading
        callbacks.set(msg.new_callback_name, null);

        // when loaded, set and flush any pending invokes
        callbackPromise.then((callback) => {
            callbacks.set(msg.new_callback_name, callback);
            flushPendingInvokes(msg.new_callback_name, callback);
        }).catch((err) => {
            console.error("Failed to load callback", err);
            callbacks.delete(msg.new_callback_name);
        });
    }

    // special handler to add a new widget
    async function addWidget(msg) {
        const { widget_id, widget_name, esm, state, layout, style, parent_id } = msg;

        const parent = parent_id ? document.getElementById(parent_id) : root;

        // element: ensure container
        let el = document.getElementById(widget_id);
        if (!el) {
            el = document.createElement('div');
            el.id = widget_id;
            parent.appendChild(el);
        }

        // apply layout styles to container
        if (layout && typeof layout === 'object') {
            Object.assign(el.style, layout);
        }

        // load the widget's view ESM (per-widget ESM)
        let mod;
        if (widgets.has(widget_name)) {
            mod = widgets.get(widget_name);
        } else {
            mod = await importEsmFromString(esm, widget_name);
            widgets.set(widget_name, mod);
        }
        if (!mod || !mod.default || typeof mod.default !== 'function') {
            console.error('Failed to load widget ESM for widget_name', widget_name);
            return;
        }
        mod.default({
            id: widget_id,
            el,
            emitWidgetMessage,
            style,
            initialState: state,
        });
    };

    // default handler if no specific callback is found
    function defaultMessageHandler(msg) {
        emitServerMessage({widgetId: msg.widget_id, type: msg.type, payload: msg});
    }
    )";
    }

} // namespace Helpers