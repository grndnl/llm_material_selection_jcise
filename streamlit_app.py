import streamlit as st
from openai import OpenAI
from langsmith import Client
from streamlit_feedback import streamlit_feedback
import uuid
from langsmith.wrappers import wrap_openai
import random
import time
import pandas as pd

langsmith_client = Client()

st.set_page_config(
    page_title="LLM Material Selection",
    page_icon="🧊",
    layout="wide"
)


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


def run_model(model, prior_messages):
    materials = ["Steel", "Aluminium", "Titanium", "Glass", "Wood", "Thermoplastic", "Elastomer", "Thermoset", "Composite"]
    full_response = ""
    if model == 'parallel':
        materials = [", ".join(materials)]

    for material in materials:
        user_input = prior_messages[-2]["content"]

        if model == 'chain-of-thought':
            count = 0
            reasoning_question = compile_question(model, user_input=user_input, material=material, count=count)
            reasoning_question = {"role": "user", "content": reasoning_question}
            reasoning = client.chat.completions.create(model="gpt-4-0125-preview", messages=[reasoning_question])

            count = 1
            run_id = st.session_state["run_id_chain_of_thought"]
            message = compile_question(model, user_input=user_input, material=material, count=count, reasoning=reasoning.choices[0].message.content)
            message = {"role": "user", "content": message}

        else:
            message = compile_question(model, user_input=user_input, material=material)
            message = {"role": "user", "content": message}

            if model == 'few-shot':
                run_id = st.session_state["run_id_few_shot"]
            elif model == 'zero-shot':
                run_id = st.session_state["run_id_zero_shot"]
            elif model == 'parallel':
                run_id = st.session_state["run_id_parallel"]
            else:
                raise ValueError("Invalid model type")

        response = client.chat.completions.create(model="gpt-3.5-turbo-0125", messages=[message], langsmith_extra={"run_id": run_id})
        full_response += f"{material}: {response.choices[0].message.content}\n\n"
    return full_response


few_shot = """
        - Example 1
        Design: Bicycle Grip
        Criterion: Impact Resistant
        You are tasked with designing the grip of a bicycle frame which should be impact resistant.
        How well do you think each of the provided materials would perform in this application? (Use a scale of 0-10 where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent.')
    
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
                   f"You are tasked with designing a `{user_input}`.\n" \
                   f"How well do you think {material} would perform in this application? Answer on a scale of 0-10, " \
                   f"where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', with just the number and no other words."

    elif question_type == 'few-shot':
        question = f"You are a material science and design engineer expert.\n" \
                   f"Below are two examples of how materials would perform from 0-10 given a design and a criterion:\n" \
                   f"{few_shot}\n" \
                   f"You are tasked with designing a `{user_input}`.\n" \
                   f"How well do you think {material} would perform in this application? Answer on a scale of 0-10, " \
                   f"where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', with just the number and no other words.\n"

    elif question_type == 'parallel':
        question = f"You are a material science and design engineer expert.\n" \
                   f"You are tasked with designing a `{user_input}`.\n" \
                   f"For each of the following materials, how well do you think they would perform in this application? Answer on a scale of 0-10, " \
                   f"where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', just with the integers separated by commas, and no other words or explanation. Be concise and answer for all 9 materials.\n" \
                   f"Materials:\n{material}\nAnswers:\n"

    elif question_type == 'chain-of-thought':
        if count == 0:
            question = f"You are a material science and design engineer expert.\n" \
                   f"You are tasked with designing a `{user_input}`.\n" \
                       f"How well do you think {material} would perform in this application?"
        else:
            question = f"You are a material science and design engineer expert.\n" \
                   f"You are tasked with designing a `{user_input}`.\n" \
                       f"How well do you think {material} would perform in this application? Below is some reasoning that you can follow:\n\n" \
                       f"{reasoning}\n\n" \
                       f"Answer on a scale of 0-10, " \
                       f"where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', with just the number and no other words.\n"

    else:
        raise ValueError("Invalid question type")
    return question


# Get the score mapping based on the selected feedback option
scores = {"👍": 1, "👎": 0}


########################################################################################################################
with st.sidebar:
    st.info("[View the repository for this project](https://github.com/grndnl/llm_material_selection_jcise)\n"
            "[View the paper](to be added)")
    st.info("**Data collection notice:**\n"
            "We collect and store the textual user input and any feedback selected by the user. ")


st.title("Get material feedback from GPT-4")


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "What do you want to design? I can help evaluate some materials for you."}
    ]

if "messages_zero_shot" not in st.session_state:
    st.session_state.messages_zero_shot = []

if "messages_few_shot" not in st.session_state:
    st.session_state.messages_few_shot = []

if "messages_parallel" not in st.session_state:
    st.session_state.messages_parallel = []

if "messages_chain_of_thought" not in st.session_state:
    st.session_state.messages_chain_of_thought = []

if "run_id" not in st.session_state:
    st.session_state["run_id"] = None

if "run_id_zero_shot" not in st.session_state:
    st.session_state["run_id_zero_shot"] = None

if "run_id_few_shot" not in st.session_state:
    st.session_state["run_id_few_shot"] = None

if "run_id_parallel" not in st.session_state:
    st.session_state["run_id_parallel"] = None

if "run_id_chain_of_thought" not in st.session_state:
    st.session_state["run_id_chain_of_thought"] = None

if "chat_disabled" not in st.session_state:
    st.session_state["chat_disabled"] = False

if "default" not in st.session_state:
    st.session_state["default"] = get_default()

if "score_zero_shot" not in st.session_state:
    st.session_state["score_zero_shot"] = None

if "score_few_shot" not in st.session_state:
    st.session_state["score_few_shot"] = None

if "score_parallel" not in st.session_state:
    st.session_state["score_parallel"] = None

if "score_chain_of_thought" not in st.session_state:
    st.session_state["score_chain_of_thought"] = None


tab1, tab2, tab3 = st.tabs(["Demo", "Research Overview", "Survey Responses"])

with tab1:
    messages = st.session_state.messages
    display_messages = st.container()
    for msg in messages:
        display_messages.chat_message(msg["role"]).write(msg["content"])
    default = st.session_state["default"]
    disabled = st.session_state["chat_disabled"]

    messages_zero_shot = st.session_state.messages_zero_shot
    messages_few_shot = st.session_state.messages_few_shot
    messages_parallel = st.session_state.messages_parallel
    messages_chain_of_thought = st.session_state.messages_chain_of_thought


    with st.container():
        prompt = st.chat_input(placeholder=default, disabled=disabled)
        if prompt:
            display_messages.chat_message("user").write(prompt)
            messages.append({"role": "user", "content": prompt})

            time.sleep(0.5)
            bot_message = "I will evaluate a set of materials on a scale of 0 to 10, where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent'.\n\n" \
                          "Four different generation methods will be used, as described in the paper."
            display_messages.chat_message("assistant").write(bot_message)
            messages.append({"role": "assistant", "content": bot_message})

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

                with st.spinner("Generating..."):
                    response = run_model('zero-shot', messages)
                st.session_state["messages_zero_shot"].append({"role": "assistant", "content": response})

                display_messages_zero_shot.chat_message("assistant").write(st.session_state["messages_zero_shot"][-1]["content"])

            if st.session_state["messages_zero_shot"]:
                feedback_zero_shot = streamlit_feedback(
                    feedback_type='thumbs',
                    # optional_text_label="[Optional] Please provide an explanation",
                    key=f"feedback_{st.session_state['run_id_zero_shot']}") #, disable_with_score=st.session_state.score_zero_shot) #, on_submit=submit_feedback)

            if feedback_zero_shot:
                # Get the score from the selected feedback option's score mapping
                score = scores[feedback_zero_shot["score"]]
                st.session_state.score_zero_shot = score

                if score is not None:
                    # Record the feedback with the formulated feedback type string
                    feedback_record = langsmith_client.create_feedback(
                        run_id=st.session_state["run_id_zero_shot"],
                        score=score,
                        key='feedback',
                    )
                    st.session_state.feedback = {
                        "feedback_id": str(feedback_record.id),
                        "score": score,
                    }
                    st.toast(f"Thanks for submitting feedback!", icon="👍")
                else:
                    st.warning("Invalid feedback score.")

        with col2:
            st.write("### Few-shot")

            display_messages_few_shot = st.container()
            for msg in messages_few_shot:
                display_messages_few_shot.chat_message(msg["role"]).write(msg["content"])

            if not st.session_state["messages_few_shot"]:
                run_id_few_shot = uuid.uuid4()
                st.session_state["run_id_few_shot"] = run_id_few_shot
                client = wrap_openai(OpenAI(api_key=st.secrets["OPENAI_API_KEY"]))

                with st.spinner("Generating..."):
                    response = run_model('few-shot', messages)

                st.session_state["messages_few_shot"].append({"role": "assistant", "content": response})
                display_messages_few_shot.chat_message("assistant").write(st.session_state["messages_few_shot"][-1]["content"])

            if st.session_state["messages_few_shot"]:
                feedback_few_shot = streamlit_feedback(
                    feedback_type='thumbs',
                    # optional_text_label="[Optional] Please provide an explanation",
                    key=f"feedback_{st.session_state['run_id_few_shot']}")  # , disable_with_score=st.session_state.score_zero_shot) #, on_submit=submit_feedback)

            if feedback_few_shot:
                # Get the score from the selected feedback option's score mapping
                score = scores[feedback_few_shot["score"]]
                st.session_state.score_few_shot = score

                if score is not None:
                    # Record the feedback with the formulated feedback type string
                    feedback_record = langsmith_client.create_feedback(
                        run_id=st.session_state["run_id_few_shot"],
                        score=score,
                        key='feedback',
                    )
                    st.session_state.feedback = {
                        "feedback_id": str(feedback_record.id),
                        "score": score,
                    }
                    st.toast(f"Thanks for submitting feedback!", icon="👍", )
                else:
                    st.warning("Invalid feedback score.")

        with col3:
            st.write("### Parallel")

            display_messages_parallel = st.container()
            for msg in messages_parallel:
                display_messages_parallel.chat_message(msg["role"]).write(msg["content"])

            if not st.session_state["messages_parallel"]:
                run_id_parallel = uuid.uuid4()
                st.session_state["run_id_parallel"] = run_id_parallel
                client = wrap_openai(OpenAI(api_key=st.secrets["OPENAI_API_KEY"]))

                with st.spinner("Generating..."):
                    response = run_model('parallel', messages)

                    # remove extra text from response
                    response = response.split("Steel, Aluminium, Titanium, Glass, Wood, Thermoplastic, Elastomer, Thermoset, Composite:")[1]

                st.session_state["messages_parallel"].append({"role": "assistant", "content": response})
                display_messages_parallel.chat_message("assistant").write(
                    st.session_state["messages_parallel"][-1]["content"])

            if st.session_state["messages_parallel"]:
                feedback_parallel = streamlit_feedback(
                    feedback_type='thumbs',
                    # optional_text_label="[Optional] Please provide an explanation",
                    key=f"feedback_{st.session_state['run_id_parallel']}")  # , disable_with_score=st.session_state.score_zero_shot) #, on_submit=submit_feedback)

            if feedback_parallel:
                # Get the score from the selected feedback option's score mapping
                score = scores[feedback_parallel["score"]]
                st.session_state.score_parallel = score

                if score is not None:
                    # Record the feedback with the formulated feedback type string
                    feedback_record = langsmith_client.create_feedback(
                        run_id=st.session_state["run_id_parallel"],
                        score=score,
                        key='feedback',
                    )
                    st.session_state.feedback = {
                        "feedback_id": str(feedback_record.id),
                        "score": score,
                    }
                    st.toast(f"Thanks for submitting feedback!", icon="👍", )
                else:
                    st.warning("Invalid feedback score.")

        with col4:
            st.write("### Chain-of-thought")

            display_messages_chain_of_thought = st.container()
            for msg in messages_chain_of_thought:
                display_messages_chain_of_thought.chat_message(msg["role"]).write(msg["content"])

            if not st.session_state["messages_chain_of_thought"]:
                run_id_chain_of_thought = uuid.uuid4()
                st.session_state["run_id_chain_of_thought"] = run_id_chain_of_thought
                client = wrap_openai(OpenAI(api_key=st.secrets["OPENAI_API_KEY"]))

                with st.spinner("Generating..."):
                    response = run_model('chain-of-thought', messages)

                st.session_state["messages_chain_of_thought"].append({"role": "assistant", "content": response})
                display_messages_chain_of_thought.chat_message("assistant").write(
                    st.session_state["messages_chain_of_thought"][-1]["content"])

            if st.session_state["messages_chain_of_thought"]:
                feedback_chain_of_thought = streamlit_feedback(
                    feedback_type='thumbs',
                    # optional_text_label="[Optional] Please provide an explanation",
                    key=f"feedback_{st.session_state['run_id_chain_of_thought']}")  # , disable_with_score=st.session_state.score_zero_shot) #, on_submit=submit_feedback)

            if feedback_chain_of_thought:
                # Get the score from the selected feedback option's score mapping
                score = scores[feedback_chain_of_thought["score"]]
                st.session_state.score_chain_of_thought = score

                if score is not None:
                    # Record the feedback with the formulated feedback type string
                    feedback_record = langsmith_client.create_feedback(
                        run_id=st.session_state["run_id_chain_of_thought"],
                        score=score,
                        key='feedback',
                    )
                    st.session_state.feedback = {
                        "feedback_id": str(feedback_record.id),
                        "score": score,
                    }
                    st.toast(f"Thanks for submitting feedback!", icon="👍", )
                else:
                    st.warning("Invalid feedback score.")

    if st.session_state["messages_chain_of_thought"]:
        time.sleep(1)
        bot_message = "Please submit feedback using the thumbs up or thumbs down buttons, and refresh the page to evaluate a new design!"
        display_messages.chat_message("assistant").write(bot_message)
        messages.append({"role": "assistant", "content": bot_message})

with tab2:
    st.write("# Research Overview")
    # show the image with a good size
    st.image("img.png", width=900)

    st.write("## Contributors")
    author1, author2, author3, author4, author5 = st.columns(5)
    with author1:
        st.write("**Daniele Grandi**")
        "Autodesk Research"
    with author2:
        st.write("**Yash Patawari Jain**")
        "Carnegie Mellon University"
    with author3:
        st.write("**Allin Groom**")
        "Autodesk Research"
    with author4:
        st.write("**Brandon Cramer**")
        "Autodesk Research"
    with author5:
        st.write("**Christopher McComb**")
        "Carnegie Mellon University"


    st.write("## Abstract")
    st.write("""Material selection is a crucial step in conceptual design due to its significant impact on the functionality, aesthetics, manufacturability, and sustainability impact of the final product. This study investigates the use of Large Language Models (LLMs) for material selection in the product design process and compares the performance of LLMs against expert choices for various design scenarios. By collecting a dataset of expert material preferences, the study provides a basis for evaluating how well LLMs can align with expert recommendations through prompt engineering and hyperparameter tuning.

The divergence between LLM and expert recommendations is measured across different model configurations, prompt strategies, and temperature settings. This approach allows for a detailed analysis of factors influencing the LLMs' effectiveness in recommending materials. The results from this study highlight two failure modes, and identify parallel prompting as a useful prompt-engineering method when using LLMs for material selection. The findings further suggest that, while LLMs can provide valuable assistance, their recommendations often vary significantly from those of human experts. This discrepancy underscores the need for further research into how LLMs can be better tailored to replicate expert decision-making in material selection.

This work contributes to the growing body of knowledge on how LLMs can be integrated into the design process, offering insights into their current limitations and potential for future improvements.
""")

with tab3:
    st.write("# Survey Responses")
    st.write("The dataset collected from the expert survey responses used in this study is available for download [here](https://github.com/grndnl/llm_material_selection_jcise/tree/main/data).")

    # load dataset
    df = pd.read_csv("data/survey_responses_mapped.csv").dropna().reset_index(drop=True)
    st.dataframe(df)
