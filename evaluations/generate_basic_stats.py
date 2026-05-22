import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle, sys, os, pandas
from sentence_transformers import SentenceTransformer
import json

sys.path.insert(1, '..')
from stl2literal import STL2literal

model_name = sys.argv[1]

with open(f'../config/{sys.argv[3]}') as f:
    params = json.load(f)

shot_count = params['num_shots_per_input_sentence']
semantics = params['num_semantic_checks']
syntaxs = params['num_correction_attempts_per_shot']
time = sys.argv[4]
set_name = params["set_name"]
grammar = params['grammar']

#######################################################################################################################
# Write the raw results from the pkl file to a csv
#######################################################################################################################

try:
    with open(f'{sys.argv[2]}', 'rb') as f:
        translations = pickle.load(f)
        print(f'Loaded {f}')
except Exception as e:
    print(e)

os.makedirs(f'../stats/{model_name}', exist_ok=True)
translations.to_csv(f'../stats/{model_name}/{set_name}_raw_results_nx_{syntaxs}_ny_{semantics}_nz_{shot_count}_{time}.csv', index=False)

#######################################################################################################################
# Write table for per-sentence STL extraction, parsing success rate
#######################################################################################################################

success_rate = pandas.DataFrame(columns=['Input Sentence', 'STL Extraction Success Rate', 'STL Parsing Success Rate', 'Number of Translations'])
success_rate['Input Sentence'] = translations['input statement']
success_rate['STL Extraction Success Rate'] = 0
success_rate['STL Parsing Success Rate'] = 0
success_rate['Number of Translations'] = 0
success_rate['Number of Syntactically Correct Translations'] = 0

total_success_rate = pandas.DataFrame(index=[0])
total_success_rate['Input Sentence'] = 'Overall'

for col in translations.columns:
    if 'STL-shot' in col:
        success_rate['STL Extraction Success Rate'] += np.where(translations[col] == 'STL could not be extracted', 1, 0)
        success_rate['STL Parsing Success Rate'] += np.where(translations[col] == 'STL could not be parsed', 1, 0)
        success_rate['Number of Translations'] += np.where(translations[col].isnull(), 0, 1)

total_success_rate['STL Extraction Success Rate'] = success_rate['STL Extraction Success Rate'].sum()
total_success_rate['STL Parsing Success Rate'] = success_rate['STL Parsing Success Rate'].sum()

num_passed_extraction = success_rate['Number of Translations'] - success_rate['STL Extraction Success Rate']
num_passed_parsing = num_passed_extraction - success_rate['STL Parsing Success Rate']

num_total_translations = success_rate['Number of Translations'].sum()
num_total_passed_extraction = num_total_translations - success_rate['STL Extraction Success Rate'].sum()
num_total_passed_parsing = num_total_passed_extraction - success_rate['STL Parsing Success Rate'].sum()

success_rate['STL Extraction Success Rate'] = np.where(success_rate['Number of Translations']==0, 0, 1-(success_rate['STL Extraction Success Rate'] / success_rate['Number of Translations']))
success_rate['STL Parsing Success Rate'] = np.where(num_passed_extraction==0, 0, 1-(success_rate['STL Parsing Success Rate'] / num_passed_extraction))
success_rate['Number of Syntactically Correct Translations'] = success_rate['STL Extraction Success Rate'] * success_rate['STL Parsing Success Rate'] * success_rate['Number of Translations']

total_success_rate['STL Extraction Success Rate'] = np.where(num_total_translations==0, 0, 1-(total_success_rate['STL Extraction Success Rate'] / num_total_translations))
total_success_rate['STL Parsing Success Rate'] = np.where(num_total_passed_extraction==0, 0, 1-(total_success_rate['STL Parsing Success Rate'] / num_total_passed_extraction))
total_success_rate['Number of Translations'] = success_rate['Number of Translations'].sum()
total_success_rate['Number of Syntactically Correct Translations'] = total_success_rate['STL Extraction Success Rate'] * total_success_rate['STL Parsing Success Rate'] * total_success_rate['Number of Translations']

stats = pandas.concat([success_rate, total_success_rate], ignore_index=True)
stats.to_csv(f'../stats/{model_name}/{set_name}_extraction_parsing_stats_nx_{syntaxs}_ny_{semantics}_nz_{shot_count}_{time}.csv', index=False)

#######################################################################################################################
# Write table for per-sentence semantic attempt improvements/degradations
#######################################################################################################################

model = SentenceTransformer(params['embedding_model_name'], device='cpu')
semantic_count = params['num_semantic_checks']+1
syntax_count = params['num_correction_attempts_per_shot']+1

improvements_all_sentences = pandas.DataFrame(columns=['Sentence'])

for (index, row) in translations.iterrows():
    nl_embedding = np.array(model.encode(row['input statement'], normalize_embeddings=True))
    col_names = []
    for i in range(semantic_count):
        col_names.append(f'Semantic attempt {i}')
        col_names.append(f'Semantic attempt {i} sim')
    sentence_table = pandas.DataFrame(columns=col_names)

    for i in range(shot_count):
        new_row = pandas.DataFrame(columns=col_names)
        relevant_translations_cols = []
        for col in translations.columns:
            if f'shot{i}-' in col:
                relevant_translations_cols.append(col)
        row_subset = row[relevant_translations_cols] 

        count_semantic_attempts = 0
        count_inside_semantic_attempt = 0
        best_stl = None
        best_sim = None
        done_with_semantic_attempt = False
        first_time = True

        for _id, entry in enumerate(row_subset):
            # Keep counting by multiples of semantic attempts
            if count_inside_semantic_attempt < syntax_count:
                # Obtain embedding of each entry
                if entry is None or entry == 'STL could not be parsed' or entry == 'STL could not be extracted':
                    count_inside_semantic_attempt += 1
                else:
                    entry = entry.replace("∞", "inf")
                    literal = STL2literal(entry, grammar)
                    literal_embedding = ( np.array(model.encode(literal, normalize_embeddings=True)) )
                    sim = cosine_similarity(np.array(literal_embedding).reshape(1,-1), np.array(nl_embedding).reshape(1,-1))[0][0]
                    
                    if first_time or sim > best_sim:
                        first_time = False
                        best_sim = sim
                        best_stl = entry

                    count_inside_semantic_attempt += 1

            if count_inside_semantic_attempt == syntax_count:
                count_inside_semantic_attempt = 0
                r_stl = 'N/A' if first_time else best_stl
                r_sim = 'N/A' if first_time else best_sim
                new_row.loc[i, f'Semantic attempt {count_semantic_attempts}'] = r_stl
                new_row.loc[i, f'Semantic attempt {count_semantic_attempts} sim'] = r_sim
                count_semantic_attempts += 1
                first_time = True

        sentence_table = pandas.concat([sentence_table, new_row], ignore_index=False)

    number_of_times_semantic_feedback_portion_reached = 0
    for shot in range(shot_count):
        try:
            if translations.loc[index, f'STL-shot{shot}-S1-F0'] is not None:
                number_of_times_semantic_feedback_portion_reached += 1
        except Exception as e:
            print("No semantic feedback attempts")

    sentence_table['Number of improving translations (relative to initial result)'] = 0
    sentence_table['Number of worsening translations (relative to initial result)'] = 0
    sentence_table['Number of consistent translations (relative to initial result)'] = 0

    for d, r in sentence_table.iterrows():
        for i in range(params['num_semantic_checks']):
            pos_condition = False
            neg_condition = False
            eq_condition = False

            if sentence_table.loc[d, f'Semantic attempt 0'] is not None and sentence_table.loc[d, f'Semantic attempt 0'] != 'N/A':
                if sentence_table.loc[d, f'Semantic attempt {i+1}'] == 'N/A' or sentence_table.loc[d, f'Semantic attempt {i+1}'] is None:
                    pos_condition = False
                    neg_condition = True
                    eq_condition = False
                elif sentence_table.loc[d, f'Semantic attempt {i+1} sim'] > sentence_table.loc[d, f'Semantic attempt 0 sim']:
                    pos_condition = True
                    neg_condition = False
                    eq_condition = False
                elif sentence_table.loc[d, f'Semantic attempt {i+1} sim'] < sentence_table.loc[d, f'Semantic attempt 0 sim']:
                    pos_condition = False
                    neg_condition = True
                    eq_condition = False
                elif sentence_table.loc[d, f'Semantic attempt {i+1} sim'] == sentence_table.loc[d, f'Semantic attempt 0 sim']:
                    pos_condition = False
                    neg_condition = False
                    eq_condition = True

                sentence_table.loc[d, 'Number of improving translations (relative to initial result)'] += 1 if pos_condition else 0
                sentence_table.loc[d, 'Number of worsening translations (relative to initial result)'] += 1 if neg_condition else 0
                sentence_table.loc[d, 'Number of consistent translations (relative to initial result)'] += 1 if eq_condition else 0

    improvements_all_sentences.loc[index, 'Number of Times Semantic Feedback Portion Reached'] = number_of_times_semantic_feedback_portion_reached
    improvements_all_sentences.loc[index, 'Sentence'] = row['input statement']
    improvements_all_sentences.loc[index, 'Number of improving translations (relative to initial result) across all attempts'] = sentence_table['Number of improving translations (relative to initial result)'].sum()
    improvements_all_sentences.loc[index, 'Number of worsening translations (relative to initial result) across all attempts'] = sentence_table['Number of worsening translations (relative to initial result)'].sum()
    improvements_all_sentences.loc[index, 'Number of consistent translations (relative to initial result) across all attempts'] = sentence_table['Number of consistent translations (relative to initial result)'].sum()

overall = pandas.DataFrame(columns=['Sentence', 'Number of improving translations (relative to initial result) across all attempts', 'Number of worsening translations (relative to initial result) across all attempts', 'Number of consistent translations (relative to initial result) across all attempts'])
overall.loc[0, 'Sentence'] = 'Overall'
overall.loc[0, 'Number of improving translations (relative to initial result) across all attempts'] = improvements_all_sentences['Number of improving translations (relative to initial result) across all attempts'].sum()
overall.loc[0, 'Number of worsening translations (relative to initial result) across all attempts'] = improvements_all_sentences['Number of worsening translations (relative to initial result) across all attempts'].sum()
overall.loc[0, 'Number of consistent translations (relative to initial result) across all attempts'] = improvements_all_sentences['Number of consistent translations (relative to initial result) across all attempts'].sum()
overall.loc[0, 'Number of Times Semantic Feedback Portion Reached'] = improvements_all_sentences['Number of Times Semantic Feedback Portion Reached'].sum()

improvements_all_sentences = pandas.concat([improvements_all_sentences, overall], ignore_index=False)
improvements_all_sentences.to_csv(f'../stats/{model_name}/{set_name}_semantic_improvements_nx_{syntaxs}_ny_{semantics}_nz_{shot_count}_{time}.csv', index=False)
