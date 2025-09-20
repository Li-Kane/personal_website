import kdwidgets
import time
import threading

def main():
    # Create a server instance
    print("Creating server...")
    server = kdwidgets.Server()

    # Create a label widget
    label = kdwidgets.Label("Initial Text", kdwidgets.TextType.H1)
    print(f"Created label with ID: {label.getId()}")

    # Add the label to the server
    print("Adding label to server...")
    server.add_widget(label)

    print("Server is running at http://localhost:9001")
    print("You can open this URL in a browser to see the label")

    input_text = "init"
    while input_text != "":
        input_text = input("Enter new label text (or press Enter to quit): ")
        if input_text != "":
            label.text = input_text
            print(f"Updated label text to: {label.text}")
            state_msg = kdwidgets.messages.StateMessage()
            state_msg.set_data(label)
            server.to_clients(state_msg)

if __name__ == "__main__":
    main()