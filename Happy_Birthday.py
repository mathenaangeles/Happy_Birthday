import streamlit as st
from message import *
import json

st.set_page_config(
    page_title="Happy Birthday",
    page_icon=":birthday:",
)

st.write("# :birthday: Happy Birthday")

st.markdown(message)

