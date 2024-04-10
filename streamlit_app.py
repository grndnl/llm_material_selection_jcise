import streamlit as st
from openai import OpenAI
from langsmith import Client
from streamlit_feedback import streamlit_feedback
import uuid
from langsmith.wrappers import wrap_openai


langsmith_client = Client()

st.set_page_config(
    page_title="LLM Material Selection",
    page_icon="🧊",
)

openai_api_key = st.secrets["OPENAI_API_KEY"]


def get_default():
    return "heat resistant spacecraft component"


with st.sidebar:
    "[View the repository for this project](https://github.com/grndnl/llm_material_selection_jcise)"
    "[Link to paper](to be added)"


st.title("Get material feedback from GPT-4")


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "What do you want to design? I can help evaluate some materials for you."}
    ]

if "response" not in st.session_state:
    st.session_state["response"] = None

if "run_id" not in st.session_state:
    st.session_state["run_id"] = None

messages = st.session_state.messages
for msg in messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder=get_default()):
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()
    run_id = uuid.uuid4()
    st.session_state["run_id"] = run_id
    client = wrap_openai(OpenAI(api_key=openai_api_key))
    response = client.chat.completions.create(model="gpt-3.5-turbo-0125", messages=messages, langsmith_extra={"run_id": run_id})
    st.session_state["response"] = response.choices[0].message.content
    with st.chat_message("assistant"):
        messages.append({"role": "assistant", "content": st.session_state["response"]})
        st.write(st.session_state["response"])

if st.session_state["response"]:
    feedback = streamlit_feedback(
        feedback_type='thumbs',
        # optional_text_label="[Optional] Please provide an explanation",
        key=f"feedback_{prompt}",
    )

    # Get the score mapping based on the selected feedback option
    scores = {"👍": 1, "👎": 0}
    st.write(feedback)

    if feedback:
        st.write('here')
        # Get the score from the selected feedback option's score mapping
        score = scores[feedback["score"]]

        if score is not None:
            # Record the feedback with the formulated feedback type string
            # and optional comment
            st.write("Recording feedback...")
            feedback_record = langsmith_client.create_feedback(
                run_id=st.session_state.run_id,
                score=score,
                key='feedback',
                # project_id='c716f4c2-3719-413c-8b63-43637cb7a1a1'
            )
            st.session_state.feedback = {
                "feedback_id": str(feedback_record.id),
                "score": score,
            }
            st.write("Feedback recorded!")
            st.write(st.session_state.feedback)
        else:
            st.warning("Invalid feedback score.")
