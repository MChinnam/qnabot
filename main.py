import streamlit as st

# Title for the app
st.title("Input and Display App")

# Text input field
user_input = st.text_input("Enter something:")

# Button to submit the input
submit_button = st.button("Submit")

# Display the input when the button is clicked
if submit_button:
    st.write("You entered:", user_input)
