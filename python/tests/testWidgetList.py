import kdwidgets

def main():
    """
    Example showing a list of various widgets and their usage.
    Each widget has a callback registered to print changes
    to the terminal when interacted with. Then, the change is
    loaded into a state message to be synced across all clients.
    """

    # Create server and state message template
    server = kdwidgets.Server()
    state_message_template = kdwidgets.messages.StateMessage()

    # Helper function to automatically update server widget state and send to clients
    def update_state(widget, msg):
        widget.set_state(msg)
        state_message_template.set_data(widget)
        server.to_clients(state_message_template)

    # Main page layout
    page_layout = {
        "display": "flex",
        "flexDirection": "column",
        "padding": "2rem"
    }
    page_layout_container = kdwidgets.LayoutContainer()
    page_layout_container.layout = page_layout

    # INT SLIDER
    int_label = kdwidgets.Label("IntSlider", kdwidgets.TextType.H1)
    int_slider = kdwidgets.IntSlider(50, 0, 100, 1, "test", True, False, False, "vertical")

    def on_int_slider_change(msg):
        if "value" in msg and isinstance(msg["value"], int):
            value = msg["value"]
            print(f"Slider changed to: {value}")
            update_state(int_slider, msg)

    int_slider.register_callback("int_slider_change", on_int_slider_change)
    page_layout_container.add_children([int_label, int_slider])

    # FLOAT SLIDER
    float_label = kdwidgets.Label("FloatSlider", kdwidgets.TextType.H1)
    float_slider = kdwidgets.FloatSlider()

    def on_float_slider_change(msg):
        if "value" in msg and isinstance(msg["value"], (int, float)):
            value = float(msg["value"])
            print(f"Float Slider changed to: {value}")
            update_state(float_slider, msg)

    float_slider.register_callback("float_slider_change", on_float_slider_change)
    page_layout_container.add_children([float_label, float_slider])

    # CHECKBOX
    checkbox_label = kdwidgets.Label("Checkbox", kdwidgets.TextType.H1)
    checkbox = kdwidgets.Checkbox(False, "Check Me!")

    def on_checkbox_change(msg):
        if "value" in msg and isinstance(msg["value"], bool):
            checked = msg["value"]
            print(f"Checkbox changed to: {'checked' if checked else 'unchecked'}")
            update_state(checkbox, msg)

    checkbox.register_callback("checkbox_change", on_checkbox_change)
    page_layout_container.add_children([checkbox_label, checkbox])

    # DROPDOWN
    dropdown_label = kdwidgets.Label("Dropdown", kdwidgets.TextType.H1)
    options = ["Option 1", "Option 2", "Option 3"]
    dropdown = kdwidgets.Dropdown(options, "Option 1", "Choose an option")

    def on_dropdown_change(msg):
        if "value" in msg and isinstance(msg["value"], str):
            value = msg["value"]
            print(f"Dropdown changed to: {value}")
            update_state(dropdown, msg)

    dropdown.register_callback("dropdown_change", on_dropdown_change)
    page_layout_container.add_children([dropdown_label, dropdown])

    # RADIO BUTTONS
    radio_label = kdwidgets.Label("RadioButtons", kdwidgets.TextType.H1)
    radio_options = ["Choice A", "Choice B", "Choice C"]
    radio_buttons = kdwidgets.RadioButtons(radio_options, "Choice A", "Pick one")

    def on_radio_change(msg):
        if "value" in msg and isinstance(msg["value"], str):
            value = msg["value"]
            print(f"RadioButtons changed to: {value}")
            update_state(radio_buttons, msg)

    radio_buttons.register_callback("radio_change", on_radio_change)
    page_layout_container.add_children([radio_label, radio_buttons])

    # TEXT INPUT
    text_label = kdwidgets.Label("TextInput", kdwidgets.TextType.H1)
    text_input = kdwidgets.TextInput("Type something and press Enter")

    def on_text_input(msg):
        if "value" in msg and isinstance(msg["value"], str):
            value = msg["value"]
            print(f"TextInput received: {value}")

    text_input.register_callback("text_input", on_text_input)
    page_layout_container.add_children([text_label, text_input])

    # BUTTON
    button_label = kdwidgets.Label("Button", kdwidgets.TextType.H1)
    button = kdwidgets.Button("Click Me")

    def on_button_click(_msg):
        print("Button was clicked!")

    button.register_callback("button_click", on_button_click)
    page_layout_container.add_children([button_label, button])

    # Add main layout to server
    server.add_widget(page_layout_container)

    print("Widget List server started!")
    print("Open the web interface to interact with all the different widgets.")
    print("Widget interactions will be logged here in the terminal.")
    print("\nPress Enter to exit...")

    try:
        input()
    except KeyboardInterrupt:
        print("\nShutting down server...")

    print("Widget List server stopped.")

if __name__ == "__main__":
    main()