import kdwidgets

def main():
    """
    This example demonstrates using a custom AddMessage message
    to update a chat widget using only one message at a time instead of
    sending a full state to fully rerender the widget. Messages can be
    sent both from the server (terminal) and clients (text input)
    """

    # Create widgets
    text_input = kdwidgets.TextInput("Type a message and press Enter...")
    chat = kdwidgets.Chat(["Welcome to the chat!"])
    server = kdwidgets.Server()

    # Register callback for text input
    def on_text_input(msg):
        if "value" in msg and isinstance(msg["value"], str):
            message = msg["value"]
            chat.add_message(message)
            # Create and send add message to clients
            add_message = kdwidgets.messages.AddMessage()
            add_message.set_data(message, chat)
            server.to_clients(add_message)
            print(f"User sent: {message}")

    text_input.register_callback("text_input", on_text_input)

    # Add widgets to server
    server.add_widget(text_input)
    server.add_widget(chat)

    print("Chat server started!")
    print("Messages from users will appear here.")
    print("Type messages below to send from server (empty line to quit):")

    # Server message loop
    new_text = "init"
    while new_text.strip() != "":
        new_text = input("\nType message to send from server: ")

        chat.add_message(f"[Server] {new_text}")
        add_message = kdwidgets.messages.AddMessage()
        add_message.set_data(f"[Server] {new_text}", chat)
        server.to_clients(add_message)
        print(f"Server sent: {new_text}")

    print("Chat server stopped.")

if __name__ == "__main__":
    main()