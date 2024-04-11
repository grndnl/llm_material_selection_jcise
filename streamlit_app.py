import streamlit as st
from openai import OpenAI
from langsmith import Client
from streamlit_feedback import streamlit_feedback
import uuid
from langsmith.wrappers import wrap_openai
import random


langsmith_client = Client()

st.set_page_config(
    page_title="LLM Material Selection",
    page_icon="🧊",
    layout="wide"
)

# metal 3d cube emoji

def get_default():
    if st.session_state["chat_disabled"]:
        return ""
    else:
        designs = ["kitchen utensil grip", "spacecraft component", "underwater component", "safety helmet"]
        criteria = ["lightweight", "heat resistant", "corrosion resistant", "high strength"]

        # pick a random  design and criteria
        design = random.choice(designs)
        criterion = random.choice(criteria)

        default = "A {design} that is {criterion}.".format(design=design, criterion=criterion)
        default = str(default)

        return default


def run_model(model, messages):
    materials = ["Steel", "Aluminium", "Titanium", "Glass", "Wood", "Thermoplastic", "Elastomer", "Thermoset", "Composite"]
    full_response = "On a scale of 0-10, where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', here are some material scores:\n\n"
    for material in materials:
        if model == 'zero-shot':
            user_input = messages[-1]["content"]
            message = compile_question('zero-shot', user_input=user_input, material=material)
            message = {"role": "user", "content": message}
            response = client.chat.completions.create(model="gpt-3.5-turbo-0125", messages=[message], langsmith_extra={"run_id": run_id})
            full_response += f"{material}: {response.choices[0].message.content}\n\n"
    return full_response


few_shot = """
        - Example 1
        Design: Bicycle Grip
        Criterion: Impact Resistant
        You are tasked with designing the grip of a bicycle frame which should be impact resistant.
        How well do you think each of the provided materials would perform in this application? (Use a scale of 0-10 where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent')
    
        Steel: 6 
        Aluminium: 5 
        Titanium: 4 
        Glass: 2 
        Wood: 8 
        Thermoplastic: 9 
        Elastomer: 9 
        Thermoset: 6 
        Composite: 7 
    
        - Example 2
        Design: Medical Implant Grip
        Criterion: Durable
        You are tasked with designing the grip of a medical implant which should be durable. How well do you
        think each of the provided materials would perform in this application? (Use a scale of 0-10 where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent')
        
        Steel: 7 
        Aluminium: 2 
        Titanium: 9 
        Glass: 5 
        Wood: 0 
        Thermoplastic: 8 
        Elastomer: 8 
        Thermoset: 7 
        Composite: 7 
        """


def compile_question(question_type, user_input, material, count=0, reasoning=None):
    if question_type == 'zero-shot':
        question = f"You are a material science and design engineer expert.\n" \
                   f"You are tasked with designing a {user_input}.\n" \
                   f"How well do you think {material} would perform in this application? Answer on a scale of 0-10, " \
                   f"where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', with just the number and no other words."

    elif question_type == 'few-shot':
        question = f"You are a material science and design engineer expert.\n" \
                   f"Below are two examples of how materials would perform from 0-10 given a design and a criterion:\n" \
                   f"{few_shot}\n" \
                   f"You are tasked with designing a {user_input}.\n" \
                   f"How well do you think {material} would perform in this application? Answer on a scale of 0-10, " \
                   f"where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', with just the number and no other words.\n"

    elif question_type == 'parallel':
        question = f"You are a material science and design engineer expert.\n" \
                   f"You are tasked with designing a {user_input}.\n" \
                   f"For each of the following materials, how well do you think they would perform in this application? Answer on a scale of 0-10, " \
                   f"where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', just with the integers separated by commas, and no other words or explanation. Be concise and answer for all 9 materials.\n" \
                   f"Materials:\n{material}\nAnswers:\n"

    elif question_type == 'chain-of-thought':
        if count == 0:
            question = f"You are a material science and design engineer expert.\n" \
                   f"You are tasked with designing a {user_input}.\n" \
                       f"How well do you think {material} would perform in this application?"
        else:
            question = f"You are a material science and design engineer expert.\n" \
                   f"You are tasked with designing a {user_input}.\n" \
                       f"How well do you think {material} would perform in this application? Below is some reasoning that you can follow:\n\n" \
                       f"{reasoning}\n\n" \
                       f"Answer on a scale of 0-10, " \
                       f"where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', with just the number and no other words.\n"

    else:
        raise ValueError("Invalid question type")
    return question


########################################################################################################################
with st.sidebar:
    "[View the repository for this project](https://github.com/grndnl/llm_material_selection_jcise)"
    "[Link to paper](to be added)"


st.title("Get material feedback from GPT-4")


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "What do you want to design? I can help evaluate some materials for you."}
    ]

if "messages_zero_shot" not in st.session_state:
    st.session_state.messages_zero_shot = []

# if "response_zero_shot" not in st.session_state:
#     st.session_state["response_zero_shot"] = None

if "run_id" not in st.session_state:
    st.session_state["run_id"] = None

if "run_id_zero_shot" not in st.session_state:
    st.session_state["run_id_zero_shot"] = None

if "chat_disabled" not in st.session_state:
    st.session_state["chat_disabled"] = False

if "default" not in st.session_state:
    st.session_state["default"] = get_default()

if "score_zero_shot" not in st.session_state:
    st.session_state["score_zero_shot"] = None

messages = st.session_state.messages
display_messages = st.container()
for msg in messages:
    display_messages.chat_message(msg["role"]).write(msg["content"])
default = st.session_state["default"]
disabled = st.session_state["chat_disabled"]

messages_zero_shot = st.session_state.messages_zero_shot


with st.container():
    prompt = st.chat_input(placeholder=default, disabled=disabled)
    if prompt:
        display_messages.chat_message("user").write(prompt)
        messages.append({"role": "user", "content": prompt})

    # disable chat
    st.session_state["chat_disabled"] = True

col1, col2, col3, col4 = st.columns(4)

if prompt or st.session_state["messages_zero_shot"]:
    with col1:
        st.write("### Zero-shot")

        display_messages_zero_shot = st.container()
        for msg in messages_zero_shot:
            display_messages_zero_shot.chat_message(msg["role"]).write(msg["content"])

        if not st.session_state["messages_zero_shot"]:
            run_id = uuid.uuid4()
            st.session_state["run_id_zero_shot"] = run_id
            client = wrap_openai(OpenAI(api_key=st.secrets["OPENAI_API_KEY"]))

            response = run_model('zero-shot', messages)

            st.session_state["messages_zero_shot"].append({"role": "assistant", "content": response})
            display_messages_zero_shot.chat_message("assistant").write(response)

        if st.session_state["messages_zero_shot"]:
            feedback_zero_shot = streamlit_feedback(
                feedback_type='thumbs',
                # optional_text_label="[Optional] Please provide an explanation",
                key=f"feedback_{st.session_state['run_id_zero_shot']}") #, disable_with_score=st.session_state.score_zero_shot) #, on_submit=submit_feedback)

            # Get the score mapping based on the selected feedback option
            scores = {"👍": 1, "👎": 0}
            # st.write("here, reloaded score or not")
            # st.write(feedback_zero_shot)

            # if f"feedback_{st.session_state['run_id_zero_shot']}":
            #     st.write("here, clicked on feedback1")

        if feedback_zero_shot:
            # Get the score from the selected feedback option's score mapping
            score = scores[feedback_zero_shot["score"]]
            st.toast(f"Thanks for submitting feedback!", icon="👍")
            st.session_state.score_zero_shot = score

            # st.write("here, clicked on feedback2")

            if score is not None:
                # Record the feedback with the formulated feedback type string
                # and optional comment
                # st.write("Recording feedback...")
                feedback_record = langsmith_client.create_feedback(
                    run_id=st.session_state["run_id_zero_shot"],
                    score=score,
                    key='feedback',
                    # project_id='c716f4c2-3719-413c-8b63-43637cb7a1a1'
                )
                st.session_state.feedback = {
                    "feedback_id": str(feedback_record.id),
                    "score": score,
                }
                # st.write("Feedback recorded!")
                # st.write(st.session_state.feedback)
            else:
                st.warning("Invalid feedback score.")

    with col2:
        st.write("### Few-shot")

    with col3:
        st.write("### Parallel")

    with col4:
        st.write("### Chain-of-thought")


st.write("# Session state:")
st.write(st.session_state)