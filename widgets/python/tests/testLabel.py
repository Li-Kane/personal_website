import kdwidgets

# Create a simple label with default text type (P)
label1 = kdwidgets.Label("Hello World!")

# Create a label with specific text type
label2 = kdwidgets.Label("Main Title", kdwidgets.TextType.H1)

# Create an empty label and set properties
label3 = kdwidgets.Label()
label3.text = "Emphasis text"
label3.text_type = kdwidgets.TextType.EM

# Print label information
print(f"Label 1 ID: {label1.get_id()}")
print(f"Label 1 Name: {label1.get_name()}")
print(f"Label 1 Text: {label1.text}")
print(f"Label 1 Text Type: {label1.text_type_to_string(label1.text_type)}")

print(f"\nLabel 2 Text: {label2.text}")
print(f"Label 2 Text Type: {label2.text_type_to_string(label2.text_type)}")

# Get and print state
state = label1.get_state()
print(f"\nLabel 1 State: {state}")

# Test state management
label1.set_state({"text": "Updated text", "text_type": "h2"})
print(f"After set_state - Text: {label1.text}")
print(f"After set_state - Type: {label1.text_type_to_string(label1.text_type)}")