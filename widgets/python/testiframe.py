import kdwidgets

def main():
    """
    Example that demonstrates using multiple iframe widgets
    in a layout container. The first iframe can be updated
    dynamically by sending state messages from the server.
    """

    # Layout configurations
    flex_layout = {
        "display": "flex",
        "flexDirection": "row",
        "height": "100%",
        "width": "100%"
    }

    iframe_layout = {
        "flex": "1",
        "display": "flex",
        "justifyContent": "center",
        "alignItems": "center"
    }

    iframe_style = {
        "height": "95%",
        "width": "95%"
    }

    # Create widgets
    layout_container = kdwidgets.LayoutContainer()
    iframe1 = kdwidgets.Iframe("https://www.example.com")
    iframe2 = kdwidgets.Iframe("https://www.wikipedia.org/")

    # Apply layouts and styles
    layout_container.layout = flex_layout
    iframe1.layout = iframe_layout
    iframe2.layout = iframe_layout
    iframe1.style = iframe_style
    iframe2.style = iframe_style

    # Add iframes to container
    layout_container.add_children([iframe1, iframe2])

    # Create server
    server = kdwidgets.Server()
    server.add_widget(layout_container)

    print("Iframe server started!")
    print("The page shows two iframes side by side:")
    print("- Left: example.com (can be changed)")
    print("- Right: wikipedia.org (static)")
    print("\nType new URLs to change the left iframe (empty line to quit):")

    # Server URL update loop
    new_src = "init"
    while new_src != "":
        new_src = input("Enter new URL for left iframe: ")

        # Update iframe source
        iframe1.src = new_src

        # Send state message to clients
        state_message = kdwidgets.messages.StateMessage()
        state_message.set_data(iframe1)
        server.to_clients(state_message)

        print(f"Updated left iframe to: {new_src}")

    print("Iframe server stopped.")

if __name__ == "__main__":
    main()