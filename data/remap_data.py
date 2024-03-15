import pandas as pd

# Load the CSV file into a pandas DataFrame
file_path = 'survey_responses.csv'
df = pd.read_csv(file_path)

# Mapping questions to 'design' and 'criteria'
design_map = {
    range(1, 5): "kitchen",
    range(5, 9): "spacecraft",
    range(9, 13): "underwater",
    range(13, 17): "helmet",
}
criteria_map = {
    1: "lightweight",
    2: "resistant to heat",
    3: "corrosion resistant",
    4: "high strength",
}

# Expand these mappings to cover all questions
design_dict = {}
criteria_dict = {}
for k, v in design_map.items():
    for i in k:
        design_dict[i] = v

for i in range(1, 17):
    criteria_dict[i] = criteria_map[(i - 1) % 4 + 1]

# Materials list for columns
materials = ["Steel", "Aluminium", "Titanium", "Glass", "Wood", "Thermoplastic", "Elastomer", "Thermoset", "Composite"]





# # Calculate the threshold for dropping respondents based on more than 51% zero responses
# # Calculate the number of times each respondent answered zero across all material-related questions
# zero_counts = df.filter(regex='^Q[0-9]+_').apply(lambda x: (x == 0).sum(), axis=1)
#
# # First, find the total number of material-related questions each respondent answered
# total_questions = df.filter(regex='^Q[0-9]+_').shape[1]
#
# # Find the threshold for 50% of total questions
# threshold = total_questions * 0.5
#
# # Identify respondents who answered zero more than 51% of the time
# respondents_to_drop = zero_counts[zero_counts > threshold].index
#
# # Drop these respondents from the original DataFrame
# df_filtered = df.drop(index=respondents_to_drop)





# Create a new DataFrame to hold the mapped data
mapped_data = []

# Extract and map the data from the original DataFrame
for q_num in range(1, 17):
    q_cols = [f"Q{q_num}_{material}" for material in materials]
    for material in materials:
        for index, row in df.iterrows():
            mapped_data.append({
                "design": design_dict[q_num],
                "criteria": criteria_dict[q_num],
                "material": material.lower(),
                "response": row[f"Q{q_num}_{material}"]
            })

# Convert the mapped data to a DataFrame
mapped_df = pd.DataFrame(mapped_data)

# Show a sample of the new DataFrame to verify the transformation
print(mapped_df.head())

mapped_df.to_csv('survey_responses_mapped.csv', index=False)
