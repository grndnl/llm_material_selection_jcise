import streamlit as st
from streamlit_feedback import streamlit_feedback


st.title("Get material feedback from GPT-4")

st.header("What would you like to design?")

feedback = streamlit_feedback(
    feedback_type="thumbs",
    # optional_text_label="[Optional] Please provide an explanation",
)
feedback