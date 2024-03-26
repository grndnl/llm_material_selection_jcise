from llama_index.llms.replicate import Replicate
from llama_index.llms.openai import OpenAI
import os
import pandas as pd
from tqdm import tqdm
from prompt_templates import few_shot
import re
from peft import PeftModel
from transformers import BitsAndBytesConfig
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def run_thread(model, question, llm=None, max_new_tokens=2, temperature=None):
    if model == 'mixtral':
        if temperature is None:
            temperature = 0.75  # default temperature
        # API token of the model/pipeline that we will be using
        os.environ["REPLICATE_API_TOKEN"] = ""
        llm = Replicate(model="mistralai/mixtral-8x7b-instruct-v0.1", max_new_tokens=max_new_tokens,
                        temperature=temperature)
        response = llm.complete(question).text

    elif model == 'gpt-4-0125-preview':
        if temperature is None:
            temperature = 0.1  # default temperature
        # OpenAI model
        llm = OpenAI(model="gpt-4-0125-preview", max_new_tokens=max_new_tokens, temperature=temperature)
        response = llm.complete(question).text

    elif model == 'melm':
        if temperature is None:
            temperature = 0.4  # default temperature

        question += 'answer: '
        inputs = tokenizer.encode(question, add_special_tokens=False, return_tensors='pt')
        response = llm.generate(input_ids=inputs.to(device),
                                max_new_tokens=max_new_tokens,
                                temperature=temperature,
                                num_beams=1,
                                # top_k=50,
                                top_p=0.9,
                                num_return_sequences=1, eos_token_id=[2, 32000],
                                do_sample=True,
                                repetition_penalty=1,
                                )
        response = tokenizer.batch_decode(response[:, inputs.shape[1]:].detach().cpu().numpy(),
                                          skip_special_tokens=True)[0]

    else:
        raise ValueError("Invalid model")

    return response


def compile_question(design, criterion, material, question_type, reasoning=None):
    if question_type == 'zero-shot' or 'temperature' in question_type:
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
                   f"where 0 is 'unsatisfactory', 5 is 'acceptable', and 10 is 'excellent', just with the integers separated by commas, and no other words or explanation. Be concise and answer for all 9 materials.\n" \
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
        materials = material.split(", ")
        response = response.replace(" ", "")
        try:
            responses = {x.split(":")[0].lower(): x.split(":")[1] for x in response.split("\n")}
        except IndexError:
            try:
                responses = response.split("\n")[0]
                responses = responses.replace(".", "").split(",")
                responses = {materials[i].lower(): responses[i] for i in range(len(materials))}
                responses = {re.sub("[^a-zA-Z]", "", k): v for k, v in responses.items()}
            except Exception as e:
                try:
                    responses = response.split("\n")
                    # drop empty strings
                    responses = [x for x in responses if x]
                    responses = {x.split(":")[0].lower(): x.split(":")[1] for x in responses}
                    # responses = {materials[i].lower(): responses[i] for i in range(len(materials))}
                    responses = {re.sub("[^a-zA-Z]", "", k): v for k, v in responses.items()}
                # except Exception as e:
                #     try:
                #         responses = response.split("\n")[0]
                #         responses = responses.split(",")
                #         responses = {materials[i].lower(): responses[i] for i in range(len(materials.split))}

                except Exception as e:
                    print("Unknown error: ", e)
                    print(response)

        try:
            responses = {re.sub("[^a-zA-Z]", "", k): v for k, v in responses.items()}
        except Exception as e:
            print("Unknown error: ", e)


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
            except TypeError:
                results = results._append({
                    'design': design,
                    'criteria': criterion,
                    'material': mat,
                    'response': None
                }, ignore_index=True)
            except KeyError as e:
                print(e)
                print(responses)
                # raise ValueError(f"Response does not contain all materials: {response}")
                # add null results
                results = results._append({
                    'design': design,
                    'criteria': criterion,
                    'material': mat,
                    'response': response
                }, ignore_index=True)

    else:
        # validate response is only a single integer
        try:
            response = int(response)
        except ValueError:
            try:
                response = response.split()[0]
                response = int(re.sub("[^0-9]", "", response))
            except Exception as e:
                # raise ValueError(f"Response is not a single integer: {response}")
                response = response
        results = results._append({
            'design': design,
            'criteria': criterion,
            'material': material,
            'response': response
        }, ignore_index=True)

    return results


def load_melm():
    print("Loading MeLM model")
    model_name = 'Open-Orca/OpenOrca-Platypus2-13B'
    FT_model_name = 'MechGPT-13b_v106C'
    peft_model_id = f'{FT_model_name}'
    bnb_config4bit = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16,
    )
    model_base = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        quantization_config=bnb_config4bit,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )

    llm = PeftModel.from_pretrained(model_base, peft_model_id)
    tokenizer = AutoTokenizer.from_pretrained(model_name)

    tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "right"

    print("MeLM model loaded")
    return llm, tokenizer


if __name__ == '__main__':
    overwrite_results = False

    materials = [
        "steel",
        "aluminium",
        "titanium",
        "glass",
        "wood",
        "thermoplastic",
        "elastomer",
        "thermoset",
        "composite"
    ]
    designs = [
        "kitchen utensil grip",
        "spacecraft component",
        "underwater component",
        "safety helmet"
    ]
    criteria = [
        "lightweight",
        "heat resistant",
        "corrosion resistant",
        "high strength"
    ]

    for model_name in ['gpt-4-0125-preview', 'mixtral', 'melm']:
        if model_name == 'melm':
            llm, tokenizer = load_melm()
            device = 'cuda'
        else:
            llm = None

        for question_type in ['zero-shot', 'few-shot', 'parallel', 'chain-of-thought',
                              'temperature-0', 'temperature-0.2', 'temperature-0.4', 'temperature-0.6',
                              'temperature-0.8', 'temperature-1']:
            # if results exist and we don't want to overwrite, skip
            if os.path.exists(f"answers/{question_type}_{model_name}.csv") and not overwrite_results:
                print(f"Skipping {question_type} questions for {model_name}")
                continue

            # initialize results dataframe
            results = pd.DataFrame(columns=['design', 'criteria', 'material', 'response'])

            for design in tqdm(designs, desc=f"Running {question_type} questions for {model_name}"):
                for criterion in criteria:
                    if question_type == 'parallel':
                        material = ", ".join(materials)
                        question = compile_question(design, criterion,  material, question_type)
                        response = run_thread(model_name, question, llm=llm, max_new_tokens=30)
                        results = append_results(results, design, criterion, material, response, question_type)
                    else:
                        for material in materials:
                            if question_type in ['zero-shot', 'few-shot']:
                                question = compile_question(design, criterion, material, question_type)
                                response = run_thread(model_name, question, llm=llm)

                            elif question_type == 'parallel':
                                question = compile_question(design, criterion, [", ".join(materials)], question_type)
                                response = run_thread(model_name, question, llm=llm, max_new_tokens=20)

                            elif question_type == 'chain-of-thought':
                                count = 0
                                question = compile_question(design, criterion, material, question_type)
                                reasoning = run_thread(model_name, question, llm=llm, max_new_tokens=300)

                                count = 1
                                question = compile_question(design, criterion, material, question_type, reasoning=reasoning)
                                response = run_thread(model_name, question, llm=llm)

                            elif 'temperature' in question_type:
                                temp = float(question_type.split("-")[-1])
                                question = compile_question(design, criterion, material, question_type)
                                response = run_thread(model_name, question, llm=llm, temperature=temp)
                            else:
                                raise ValueError(f"Invalid question type: {question_type}")

                            results = append_results(results, design, criterion, material, response, question_type)

            if not os.path.exists("answers"):
                os.makedirs("answers")
            results.to_csv(f"answers/{question_type}_{model_name}.csv", index=False)
