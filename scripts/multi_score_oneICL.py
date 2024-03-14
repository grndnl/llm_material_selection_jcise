from openai import OpenAI
import os
import json

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def get_completion(prompt, model="gpt-4"):
    messages = [{"role": "user", "content": prompt}
                ,{"role": "system", "content": "You are a Materials Science and Design Engineering expert."}]
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message.content

material_families = f'''
1. Steel
2. Aluminium
3. Titanium
4. Glass
5. Wood
6. Thermoplastic
7. Elastomer
8. Thermoset
9. Composite
'''

design_choice = [
    "Kitchen Utensil Grip",
    "Spacecraft Component",
    "Underwater Component",
    "Safety Helmet"
]

criterion = [
    "Lightweight",
    "Resistant to Heat",
    "Corrosion Resistant",
    "High Strength"
]

def prompt_response(design_choice: str, criterion: str):
    prompt = f"""
    You are given a problem statement to assist a designer as below:
    The information below is provided to you delimited by triple backticks

    Design: '''{design_choice}'''
    Criterion: '''{criterion}'''

    You are tasked with designing the grip of {design_choice} which should be {criterion}.
    
    How well do you think each of the provided materials would perform in this application?

    As a materials science and design engineer with experience in this field, 
    you are supposed to give a score between 0-10 for each of the options provided below. 
    This score should be how applicable each material family would be for this design case. 
    0 would be unacceptable and 10 would be excellent for this use case as mentioned in the question.

    Here are the material families to score on:
    '''{material_families}'''

    The score is intended on a viability perspective, so the focus should be on how well the material satisfies the design and criterion pair.

    An example of how to go ahead with the scoring is as follows:
    Design: Bicycle Frame
    Criterion: Lightweight
    You are tasked with designing the frame of a bicycle which should be lightweight. How well do you
    think each of the provided materials would perform in this application? (Use a scale of 0-10 and the 
    materials are: 

    Steel (4) : Steel has the highest density of all options available so not immediately suitable for light 
    weighting. Despite its high tensile strength, the specific strength of steel is lower than that of other 
    material options and thus not a suitable option.
    Aluminium (9) : Aluminium has the lowest density of metals/alloys in this selection making it an 
    ideal candidate for light-weighting a structural frame. It has a lower specific strength compared to 
    titanium alloys suggesting more material would be required to achieve an equivalent strength. 
    Titanium (8) : titanium as a stand-alone material is not a suitable for this application. Its alloys 
    however can enhance its mechanical strength significantly making it an ideal candidate for this 
    application, second only to thermoset composites.
    Glass (3) : Glass, specifically silicates, have a lower density than most metals/alloys and also have 
    higher mechanical strength however they are typically very brittle, making them less suitable for a 
    lightweight bicycle frame.
    Wood (6) : Wood materials such as bamboo can be relatively light and can be used for bicycle 
    frames. Denser woods such as pine or oak can be quite heavy compared to other alternatives as their
    shape is generally limited to solid volumes. Woods have anisotropic mechanical properties which 
    limits how they can be used.
    Thermoplastic (7) : thermoplastics cover a broad range of polymeric materials. Some examples 
    such as nylon and PET have a low density and sufficiently high stiffness to be a viable option. A 
    low glass transition temperature might affect the materials rigidity and thus suitability for this 
    application.
    Elastomer (1) : Elastomers are characterised by their high ductility in the elastic deformation. 
    While some rigid elastomers such as some polyurethanes exist, these materials are generally 
    unsuitable for the application.
    Thermoset Composite (10) : These materials, specifically carbon fibre epoxy, combine low density 
    with the stiffest materials available to create a composite structure which combines the best 
    properties of two or more materials. As a result, the specific strength for this class of materials is the
    highest meaning it is the most suitable for this application.

    Output should be of a JSON format, use the following format:

    Output JSON:
    (
    'design' : design evaluated from above,
    'criterion' : criterion evaluated from above,
    material name (material family scored - if it is steel then use steel as the key) : score which is an integer ranging from 0-10,
    )
    Only output the JSON for the materials you have scored. No need of an explanation.
    Make sure the response is in a JSON format.
    """


    response = get_completion(prompt)

    # print(f"\n Response Score: \n")
    # print(response)
    return response

# score_json = prompt_response(design_choice[0], criterion[0])

# for i in range(len(materials)):
for j in range(len(design_choice)):
    for k in range(len(criterion)):
        score_json = prompt_response(design_choice[j], criterion[k])

        print(f"Output {j}",score_json)

        path = f"/Users/yashpatawari/LLM-for-Material-Selection/ICL_GPT4_OneShot/{design_choice[j]}_{criterion[k]}.json"

        with open(path, "w") as json_file:
            json.dump(score_json, json_file)
            print(f"Data Saved to {path}")
