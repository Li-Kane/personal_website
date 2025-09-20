#pragma once
#include <nlohmann/json.hpp>
#include <string>

/**
 * Base class for all messages sent between server and client.
 * Messages must implement type(), callback_name(), and serialize().
 *
 * type() refers to the message name, as well as the default event name from server -> widgets if
 * there is no callback implemented callback_name() refers to the name of the client-side callback
 * function to invoke when this message is received serialize() should return the JSON string
 * representation of the message
 */
class Message {
  public:
    Message() = default;
    virtual ~Message() = default;

    virtual std::string type() const = 0;
    virtual std::string callback_name() const = 0;
    virtual std::string serialize() const = 0;
};