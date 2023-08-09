import streamlit as st
import random
import time
from QnA_Maker_code import QuestionAnswering

# Please install all the required libraries
# run the following command in terminal to start streamlit UI: streamlit run streamlit_cleaned_code.py

qa_client = QuestionAnswering()


st.title("Fission Q&A bot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


default_message = "Hello, I am FissionLabs bot. Let me know how can I help you?"
# st.markdown(default_message)
st.session_state.messages.append({"role": "assistant", "content": default_message})
# Accept user input
if prompt := st.chat_input("What is up?"):
    # print(prompt)
    user_input = prompt
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    # st.button("service")

    with st.chat_message("user"):
        # print(prompt)
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        # print(message_placeholder.chat_message)
        full_response = ""

        assistant_response = qa_client.get_output(user_input)
        full_response = assistant_response
        message_placeholder.markdown(assistant_response)
    st.session_state.messages.append({"role": "assistant", "content": full_response})
