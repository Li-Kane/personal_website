import kdwidgets

# Create a simple label with default text type (P)
label1 = kdwidgets.Label("Hello World!")

# Create a label with specific text type
label2 = kdwidgets.Label("Main Title", kdwidgets.TextType.H1)

# Create an empty label and set properties
label3 = kdwidgets.Label()
label3.text = "Emphasis text"
label3.textType = kdwidgets.TextType.EM

# Print label information
print(f"Label 1 ID: {label1.getId()}")
print(f"Label 1 Name: {label1.getName()}")
print(f"Label 1 Text: {label1.text}")
print(f"Label 1 Text Type: {label1.textTypeToString(label1.textType)}")

print(f"\nLabel 2 Text: {label2.text}")
print(f"Label 2 Text Type: {label2.textTypeToString(label2.textType)}")

# Get and print state
state = label1.getState()
print(f"\nLabel 1 State: {state}")

# Test state management
label1.setState({"text": "Updated text", "textType": "h2"})
print(f"After setState - Text: {label1.text}")
print(f"After setState - Type: {label1.textTypeToString(label1.textType)}")