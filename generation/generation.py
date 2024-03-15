from llama_index.llms.replicate import Replicate
from llama_index.llms.openai import OpenAI
import os
import pandas as pd
from tqdm import tqdm
from prompt_templates import few_shot


def run_thread(model, question, max_new_tokens=2):
    if model == 'mixtral':
        # API token of the model/pipeline that we will be using
        os.environ["REPLICATE_API_TOKEN"] = ""
        llm = Replicate(model="mistralai/mixtral-8x7b-instruct-v0.1", max_new_tokens=2)
    elif model == 'gpt-4-0125-preview':
        # OpenAI model
        llm = OpenAI(model="gpt-4-0125-preview", max_new_tokens=max_new_tokens)
    else:
        raise ValueError("Invalid model")

    response = llm.complete(question)
    return response.text


def compile_question(design, criterion, material, question_type, reasoning=None):
    if question_type == 'zero_shot':
        question = f"You are a material science and design engineer expert.\n" \
                   f"You are tasked with designing a {design}. The design should be {criterion}.\n" \
                   f"How well do you think {material} would perform in this application? Answer on a scale of 1-10, " \
                   f"where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', with just the number and no other words."
    elif question_type == 'few-shot':
        question = f"You are a material science and design engineer expert.\n" \
                   f"Below are two examples of how materials would perform from 1-10 given a design and a criterion:\n" \
                   f"{few_shot}\n" \
                   f"You are tasked with designing a {design}. The design should be {criterion}.\n" \
                   f"How well do you think {material} would perform in this application? Answer on a scale of 1-10, " \
                   f"where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', with just the number and no other words.\n"
    elif question_type == 'parallel':
        question = f"You are a material science and design engineer expert.\n" \
                   f"You are tasked with designing a {design}. The design should be {criterion}.\n" \
                   f"For each of the following materials, how well do you think they would perform in this application? Answer on a scale of 1-10, " \
                   f"where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', with just the number and no other words.\n" \
                   f"Materials:\n{material}\nAnswers:\n"
    elif question_type == 'chain-of-thought':
        if count == 0:
            question = f"You are a material science and design engineer expert.\n" \
                       f"You are tasked with designing a {design}. The design should be {criterion}.\n" \
                       f"How well do you think {material} would perform in this application?"
        else:
            question = f"You are a material science and design engineer expert.\n" \
                       f"You are tasked with designing a {design}. The design should be {criterion}.\n" \
                       f"How well do you think {material} would perform in this application? Below is some reasoning that you can follow:\n\n" \
                       f"{reasoning}\n\n" \
                       f"Answer on a scale of 1-10, " \
                       f"where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', with just the number and no other words.\n"
    else:
        raise ValueError("Invalid question type")
    return question


def append_results(results, design, criterion, material, response, question_type):
    if question_type == 'parallel':
        response = response.replace(" ", "")
        responses = {x.split(":")[0]: x.split(":")[1] for x in response.split("\n")}
        for i, mat in enumerate(material.split(", ")):
            try:
                results = results._append({
                    'design': design,
                    'criteria': criterion,
                    'material': mat,
                    'response': responses[mat]
                }, ignore_index=True)
            except ValueError:
                raise ValueError(f"Response is not a single integer: {response}")

    else:
        # validate response is only a single integer
        try:
            response = int(response)
        except ValueError:
            try:
                response = int(response.split()[0])
                response = int(response)
            except ValueError:
                raise ValueError(f"Response is not a single integer: {response}")
        results = results._append({
            'design': design,
            'criteria': criterion,
            'material': material,
            'response': response
        }, ignore_index=True)

    return results


if __name__ == '__main__':
    overwrite_results = False

    materials = [
        "steel",
        "aluminium",
        # "titanium",
        # "glass",
        # "wood",
        # "thermoplastic",
        # "elastomer",
        # "thermoset",
        # "composite"
    ]
    designs = [
        "kitchen utensil grip",
        # "spacecraft component",
        # "underwater component",
        # "safety helmet"
    ]
    criteria = [
        "lightweight",
        # "heat resistant",
        # "corrosion resistant",
        # "high strength"
    ]

    for question_type in ['zero_shot', 'few-shot', 'parallel', 'chain-of-thought']:  # , 'temperature']:
        for model in ['gpt-4-0125-preview', 'mixtral']:  # , 'melm']:
            # if results exist and we don't want to overwrite, skip
            if os.path.exists(f"answers/{question_type}_{model}.csv") and not overwrite_results:
                print(f"Skipping {question_type} questions for {model}")
                continue

            # initialize results dataframe
            results = pd.DataFrame(columns=['design', 'criteria', 'material', 'response'])

            if question_type == 'parallel':
                materials = [", ".join(materials)]

            for design in tqdm(designs, desc=f"Running {question_type} questions for {model}"):
                for criterion in criteria:
                    for material in materials:
                        if question_type != 'chain-of-thought':
                            question = compile_question(design, criterion, material, question_type)
                            response = run_thread(model, question)
                        elif question_type == 'chain-of-thought':
                            count = 0
                            question = compile_question(design, criterion, material, question_type)
                            reasoning = run_thread(model, question, max_new_tokens=300)

                            count = 1
                            question = compile_question(design, criterion, material, question_type, reasoning=reasoning)
                            response = run_thread(model, question)
                        else:
                            raise ValueError("Invalid question type")

                        results = append_results(results, design, criterion, material, response, question_type)

            if not os.path.exists("answers"):
                os.makedirs("answers")
            results.to_csv(f"answers/{question_type}_{model}.csv", index=False)
