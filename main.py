import streamlit as st

from add_data import addata
from chatbot import chatbot


col1, col2 = st.columns([4,1], vertical_alignment="bottom")

with col1:
    heading1 = st.title("Dragon Bot 🐲")

with col2:
    on = st.toggle("Add Task",  help="You can add the task to the Google Sheets.")


if on:
    addata()
else:
    chatbot()
