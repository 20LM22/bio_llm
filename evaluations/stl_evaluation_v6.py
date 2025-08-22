import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle, sys, os, pandas
from sentence_transformers import SentenceTransformer
import json

sys.path.insert(1, '..')
from stl2literal import STL2literal

model_name = sys.argv[1]
print(f'model name: {model_name}')

try:
    with open(f'../pkl/{model_name}/{sys.argv[2]}', 'rb') as f:
        translations = pickle.load(f)
        print(f'Loaded {f}')
except Exception as e:
    print("there was an exception")
    print(e)

# load in the config specified by the script
with open(f'../config/{sys.argv[3]}') as f:
    params = json.load(f)

shots = params['num_shots_per_input_sentence']
semantics = params['num_semantic_checks']
syntaxs = params['num_correction_attempts_per_shot']

# Output the translation table as a csv file
os.makedirs(f'../stats/{model_name}', exist_ok=True)
translations.to_csv(f'../stats/{model_name}/translations_shots_{shots}_syntax_{syntaxs}_semantic_{semantics}.csv')

embedding_model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(params['embedding_model_name'], device='cpu')

grammar = params['grammar']
sim_threshold = 0.7

#######################################################################################################################
# Table for extraction, parsing success rate
#######################################################################################################################

# translations can be missing because the model didn't need to use all of its syntax feedback correction attempts
success_rate = pandas.DataFrame(columns=['Input Sentence', 'STL Extraction Success Rate', 'STL Parsing Success Rate', 'Number of Translations'])
success_rate['Input Sentence'] = translations['input statement']
success_rate['STL Extraction Success Rate'] = 0
success_rate['STL Parsing Success Rate'] = 0
success_rate['Number of Translations'] = 0
success_rate['Number of Syntactically Correct Translations'] = 0
success_rate['Semantic Passes'] = 0
success_rate['Semantic Success Rate'] = 0

total_success_rate = pandas.DataFrame(index=[0])
total_success_rate['Input Sentence'] = 'Overall'

# success_rate['All valid STL'] = []
shot_count = params['num_shots_per_input_sentence']

for col in translations.columns:
    if 'STL-shot' in col:
        success_rate['STL Extraction Success Rate'] += np.where(translations[col] == 'STL could not be extracted', 1, 0)
        success_rate['STL Parsing Success Rate'] += np.where(translations[col] == 'STL could not be parsed', 1, 0)
        success_rate['Number of Translations'] += np.where(translations[col].isnull(), 0, 1)

# fill in semantic successes
for index, row in translations.iterrows():
    
    nl_embedding = np.array(model.encode(row['input statement'], normalize_embeddings=True))
    row_subset = pandas.DataFrame()
    row_counter = 0

    for i in range(shot_count):
        relevant_translations_cols = []
        for col in translations.columns:
            if f'shot{i}-' in col:
                relevant_translations_cols.append(col)
        row_subset = row[relevant_translations_cols] # row subset has everything with shot-i in the column name
    
        for entry in row_subset:
            if entry != 'STL could not be extracted' and entry != 'STL could not be parsed' and entry is not None:
                # add this entry
                entry = entry.replace("∞", "inf")
                literal = STL2literal(entry, grammar)
                literal_embedding = ( np.array(model.encode(literal, normalize_embeddings=True)) )
                sim = cosine_similarity(np.array(literal_embedding).reshape(1,-1), np.array(nl_embedding).reshape(1,-1))[0][0]
                if sim > sim_threshold:
                    row_counter += 1

    success_rate.loc[index, 'Semantic Passes'] = row_counter

total_success_rate['STL Extraction Success Rate'] = success_rate['STL Extraction Success Rate'].sum()
total_success_rate['STL Parsing Success Rate'] = success_rate['STL Parsing Success Rate'].sum()

num_passed_extraction = np.zeros(translations.shape[0])
num_passed_extraction = success_rate['Number of Translations'] - success_rate['STL Extraction Success Rate']
num_passed_parsing = np.zeros(translations.shape[0])
num_passed_parsing = num_passed_extraction - success_rate['STL Parsing Success Rate']

num_total_translations = success_rate['Number of Translations'].sum()
num_total_passed_extraction = num_total_translations - success_rate['STL Extraction Success Rate'].sum()
num_total_passed_parsing = num_total_passed_extraction - success_rate['STL Parsing Success Rate'].sum()

success_rate['STL Extraction Success Rate'] = np.where(success_rate['Number of Translations']==0, 0, 1-(success_rate['STL Extraction Success Rate'] / success_rate['Number of Translations']))
success_rate['STL Parsing Success Rate'] = np.where(num_passed_extraction==0, 0, 1-(success_rate['STL Parsing Success Rate'] / num_passed_extraction))
success_rate['Number of Syntactically Correct Translations'] = success_rate['STL Extraction Success Rate'] * success_rate['STL Parsing Success Rate'] * success_rate['Number of Translations']
success_rate['Semantic Success Rate'] = success_rate['Semantic Passes'] / success_rate['Number of Syntactically Correct Translations']

total_success_rate['STL Extraction Success Rate'] = np.where(num_total_translations==0, 0, 1-(total_success_rate['STL Extraction Success Rate'] / num_total_translations))
total_success_rate['STL Parsing Success Rate'] = np.where(num_total_passed_extraction==0, 0, 1-(total_success_rate['STL Parsing Success Rate'] / num_total_passed_extraction))
total_success_rate['Number of Translations'] = success_rate['Number of Translations'].sum()
total_success_rate['Semantic Passes'] = success_rate['Semantic Passes'].sum()
total_success_rate['Number of Syntactically Correct Translations'] = total_success_rate['STL Extraction Success Rate'] * total_success_rate['STL Parsing Success Rate'] * total_success_rate['Number of Translations']
total_success_rate['Semantic Success Rate'] = total_success_rate['Semantic Passes'] / total_success_rate['Number of Syntactically Correct Translations']

stats = pandas.concat([success_rate, total_success_rate], ignore_index=True)
stats.to_csv(f'../stats/{model_name}/stats_shots_{shots}_syntax_{syntaxs}_semantic_{semantics}.csv', index=False)

#######################################################################################################################
# TODO: Table where rows are shots and each table belongs to one sentence: report cosine sim. and stl of ALL attempts
#######################################################################################################################

shot_count = params['num_shots_per_input_sentence']
semantic_count = params['num_semantic_checks']+1
syntax_count = params['num_correction_attempts_per_shot']+1

# for each row - sentence in the df
for (index, row) in translations.iterrows():
    # first construct shot x semantic attempt table
    col_names = []
    for i in range(semantic_count):
        for j in range(syntax_count):
            col_names.append(f'S{i}-F{j}')
            col_names.append(f'S{i}-F{j} sim')

    nl_embedding = np.array(model.encode(row['input statement'], normalize_embeddings=True))
    # make the df that will hold all info for this sentence
    sentence_table = pandas.DataFrame(columns=col_names)

    for i in range(shot_count):
        new_row = pandas.DataFrame(columns=col_names)
        # fill in new row

        relevant_translations_cols = []
        for col in translations.columns:
            if f'shot{i}' in col:
                relevant_translations_cols.append(col)
        row_subset = row[relevant_translations_cols] # row subset has everything with shot-i in the column name
        
        best_stl = None
        best_sim = None
        m = 0
        k = 0
               
        for _id, entry in enumerate(row_subset):
            if entry == 'STL could not be parsed' or entry == 'STL could not be extracted':
                new_row.loc[i, f'S{k}-F{m}'] = 'N/A' 
                new_row.loc[i, f'S{k}-F{m} sim'] = 'N/A'
            elif entry is not None:
                entry = entry.replace("∞", "inf")
                literal = STL2literal(entry, grammar)
                literal_embedding = ( np.array(model.encode(literal, normalize_embeddings=True)) )
                sim = cosine_similarity(np.array(literal_embedding).reshape(1,-1), np.array(nl_embedding).reshape(1,-1))[0][0]
                new_row.loc[i, f'S{k}-F{m}'] = sim 
                new_row.loc[i, f'S{k}-F{m} sim'] = entry
            
            if m == syntax_count-1:
                k += 1
            m = (m+1) % syntax_count
            
        sentence_table = pandas.concat([sentence_table, new_row], ignore_index=False)
    
    short_sentence_name = row['input statement'][:15]
    sentence_table.to_csv(f'../stats/{model_name}/{short_sentence_name}_all_feedback_shots_{shots}_syntax_{syntaxs}_semantic_{semantics}.csv', index=False)

#######################################################################################################################
# Table where rows are shots and each table belongs to one sentence: report best cosine sim. and stl of each semantic attempt
#######################################################################################################################

shot_count = params['num_shots_per_input_sentence']
semantic_count = params['num_semantic_checks']+1
syntax_count = params['num_correction_attempts_per_shot']+1

improvements_all_sentences = pandas.DataFrame(columns=['Sentence'])

# for each row - sentence in the df
for (index, row) in translations.iterrows():
    nl_embedding = np.array(model.encode(row['input statement'], normalize_embeddings=True))
    col_names = []
    for i in range(semantic_count):
        col_names.append(f'Semantic attempt {i}')
        col_names.append(f'Semantic attempt {i} sim')
    sentence_table = pandas.DataFrame(columns=col_names)

    for i in range(shot_count):
        new_row = pandas.DataFrame(columns=col_names)
        # fill in new row
        relevant_translations_cols = []
        for col in translations.columns:
            if f'shot{i}-' in col:
                relevant_translations_cols.append(col)
        row_subset = row[relevant_translations_cols] # row subset has everything with shot-i in the column name

        # now we need to loop through the semantic attempts and separate them
        # shot0-s1-f2, shot0-s1-f3
        count_semantic_attempts = 0
        count_inside_semantic_attempt = 0
        best_stl = None
        best_sim = None
        done_with_semantic_attempt = False
        first_time = True

        for _id, entry in enumerate(row_subset):
            # just keep counting by multiples of semantic attempts
            if count_inside_semantic_attempt < syntax_count:
                # get the embedding of each entry
                if entry is None or entry == 'STL could not be parsed' or entry == 'STL could not be extracted':
                    # handle this problem
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
                # print('inside equals')
                count_inside_semantic_attempt = 0
                r_stl = 'N/A' if first_time else best_stl
                r_sim = 'N/A' if first_time else best_sim
                # done with semantic attempt, need to process this as an entry for this new row
                new_row.loc[i, f'Semantic attempt {count_semantic_attempts}'] = r_stl
                new_row.loc[i, f'Semantic attempt {count_semantic_attempts} sim'] = r_sim
                count_semantic_attempts += 1
                first_time = True

        sentence_table = pandas.concat([sentence_table, new_row], ignore_index=False)

    # back at the sentence level
    number_of_times_semantic_feedback_portion_reached = 0
    for shot in range(shots):
        if translations.loc[index, f'STL-shot{shot}-S1-F0'] is not None:
            number_of_times_semantic_feedback_portion_reached += 1

    sentence_table['Number of improving translations (relative to initial result)'] = 0
    sentence_table['Number of worsening translations (relative to initial result)'] = 0
    sentence_table['Number of consistent translations (relative to initial result)'] = 0

    for d, r in sentence_table.iterrows():
        for i in range(params['num_semantic_checks']): # TODO: need to get the number of semantic attempts from params
            pos_condition = False
            neg_condition = False
            eq_condition = False

            if sentence_table.loc[d, f'Semantic attempt 0'] is not None and sentence_table.loc[d, f'Semantic attempt 0'] != 'N/A':
                # print(f'sentence_table.loc[d, Semantic attempt {i+1}]: {sentence_table.loc[d, f'Semantic attempt {i+1}']}')
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

    # print(f'sentence table: {sentence_table}')
    short_sentence_name = row['input statement'][:15]
    sentence_table.to_csv(f'../stats/{model_name}/{short_sentence_name}_best_sim_shots_{shots}_syntax_{syntaxs}_semantic_{semantics}.csv', index=False)

    # added bit for times we don't even get a chance at a semantic attempt
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

improvements_all_sentences = pandas.concat([improvements_all_sentences, overall], ignore_index=False)
improvements_all_sentences.to_csv(f'../stats/{model_name}/improvements_all_sentences_shots_{shots}_syntax_{syntaxs}_semantic_{semantics}.csv', index=False)
# print(f'../stats/{model_name}/improvements_all_sentences_shots_{shots}_syntax_{syntaxs}_semantic_{semantics}.csv')

## need to check that these columns add up to number of syntactically correct translations

#######################################################################################################################
# Table where sentences are rows: report the best cosine sim. for each shot and the corresponding STL
#######################################################################################################################

shot_count = params['num_shots_per_input_sentence']
semantic_count = params['num_semantic_checks']
syntax_count = params['num_correction_attempts_per_shot']

col_names = []
for i in range(shot_count):
    col_names.append(f'shot{i}')
    col_names.append(f'shot{i} sim')
best_resp = pandas.DataFrame(columns=col_names)

# for each row in the df
for index, row in translations.iterrows():
    nl_embedding = np.array(model.encode(row['input statement'], normalize_embeddings=True))

    for i in range(shot_count):
        shot_name = f'shot{i}'
        # from translation, grab the columns that have 'shot{i}' in the name
        relevant_translations_cols = []
        for col in translations.columns:
            if f'shot{i}' in col:
                relevant_translations_cols.append(col)
        row_subset = row[relevant_translations_cols]
        # need to reduce this row_subset to the entry that has the highest cosine similarity
        row_subset_filtered = [x for x in row_subset if x != 'STL could not be parsed' and x != 'STL could not be extracted' and x is not None]

        # print(f'the row subset filtered is: {row_subset_filtered}')
        literal_embeddings = []
        for stl in row_subset_filtered:
            # get the literal translation, then the embedding that goes with the literal
            stl = stl.replace("∞", "inf")
            literal = STL2literal(stl, grammar)
            literal_embeddings.append( np.array(model.encode(literal, normalize_embeddings=True)) )

        if len(literal_embeddings) == 0:
            best_resp.at[index, f'shot{i}'] = None
            best_resp.at[index, f'shot{i} sim'] = None
        elif len(literal_embeddings) == 1:
            sim = cosine_similarity(np.array(literal_embeddings).reshape(1,-1), np.array(nl_embedding).reshape(1,-1))
            best_resp.at[index, f'shot{i}'] = row_subset_filtered[0]
            best_resp.at[index, f'shot{i} sim'] = max(sim)
        else:
            sim = cosine_similarity(np.array(literal_embeddings), np.array(nl_embedding).reshape(1,-1))
            best_resp.at[index, f'shot{i} sim'] = max(sim)
            best_resp.at[index, f'shot{i}'] = row_subset_filtered[np.argmax(sim)]

best_resp.to_csv(f'../stats/{model_name}/test_set_best_sim_shot_shots_{shots}_syntax_{syntaxs}_semantic_{semantics}.csv', index=False)

