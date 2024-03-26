import pandas as pd


def calculate_mean_distance(row, survey_df):
    # Filter the survey responses for matching design, criteria, and material
    matching_responses = survey_df[(survey_df['design'] == row['design']) &
                                   (survey_df['criteria'] == row['criteria']) &
                                   (survey_df['material'] == row['material'])]['response']

    # Calculate the absolute distance between the generated value and each survey response
    distances = abs(matching_responses - row['response'])

    # Calculate and return the mean of these distances
    return distances.mean()


if __name__ == '__main__':
    results = []

    # Load the survey responses CSV
    survey_responses_path = '../data/survey_responses_mapped.csv'
    survey_responses_df = pd.read_csv(survey_responses_path)

    # drop the rows with nan values
    survey_responses_df = survey_responses_df.dropna()

    # Group the survey responses by 'design', 'criteria', 'material' and calculate mean and std
    grouped_survey_stats = survey_responses_df.groupby(['design', 'criteria', 'material'])['response'].agg(
        ['mean', 'std']).reset_index()

    for model in ['gpt-4-0125-preview', 'mixtral', 'melm']:
        for experiment in ['zero-shot', 'few-shot', 'parallel', 'chain-of-thought',
                              'temperature-0', 'temperature-0.2', 'temperature-0.4', 'temperature-0.6',
                              'temperature-0.8', 'temperature-1']:
            if model == 'melm' and experiment == 'temperature-0':
                experiment = 'temperature-0.1'

            # load model data
            model_data_path = f'../generation/answers/{experiment}_{model}.csv'
            model_data_df = pd.read_csv(model_data_path)


            # clean the response column by only taking the first digits in the string
            try:
                model_data_df['response'] = model_data_df['response'].str.extract(r'(\d+)').astype(int)
            except:
                pass

            # floor all values above 10 to 10, and all values below 0 to 0
            model_data_df['response'] = model_data_df['response'].apply(lambda x: min(10, max(0, x)))

            model_data_df['mean_distance'] = model_data_df.apply(
                lambda row: calculate_mean_distance(row, survey_responses_df), axis=1)

            # Save the mean z-scored in the results array
            mean_distances = model_data_df['mean_distance'].mean()
            results.append({'model': model, 'experiment': experiment, 'mean_distances': mean_distances})

    # Save the results to a CSV file
    results_df = pd.DataFrame(results)
    results_df.to_csv('mean_distances.csv', index=False)



