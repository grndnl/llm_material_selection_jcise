import pandas as pd


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

            # Merge the experimen_model results with the grouped survey stats to match each generated response with its group stats
            merged_df = pd.merge(model_data_df, grouped_survey_stats, on=['design', 'criteria', 'material'], how='left')

            # Calculate the z-score for each generated response
            merged_df['z_score'] = (merged_df['response'] - merged_df['mean']) / merged_df['std']

            # Save the mean z-scored in the results array
            mean_z_score = merged_df['z_score'].mean()
            results.append({'model': model, 'experiment': experiment, 'mean_z_score': mean_z_score})

    # Save the results to a CSV file
    results_df = pd.DataFrame(results)
    results_df.to_csv('z_scores.csv', index=False)



