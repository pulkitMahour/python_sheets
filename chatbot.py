import streamlit as st
import time
import os

from langchain_google_genai import GoogleGenerativeAI

def response_generator(query):
    api_key = os.environ['API_KEY']
    model = GoogleGenerativeAI(model="models/gemini-1.5-flash", google_api_key=api_key, temperature=0.7)

    response = model.invoke(query)

    for word in response.split():
        yield word + " "
        time.sleep(0.05)


st.title("Simple chat")

with st.expander("ℹ️ Disclaimer"):
    st.caption('Please note, this demo is designed to process a maximum of 3 interactions and may be unavailable if too many request send concurrently. Thank you for your understanding.')

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=message["avatar"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    st.session_state.messages.append({"role": "user", "content": prompt, "avatar":"🐲"})
    # Display user message in chat message container
    with st.chat_message("user", avatar="🐲"):
        st.markdown(prompt)
    with st.chat_message("ai", avatar="🧠"):
        if len(st.session_state.messages) < 6:
            response = st.write_stream(response_generator(prompt))
        else:
            response = st.write("Your one time quote is exhausted, if you want to start the conversation again just reload the page. Thanks")
    st.session_state.messages.append({"role": "assistant", "content": response, "avatar":"🧠"})
    # st.session_state


