import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt
import pickle, sys, os, pandas
from thefuzz import fuzz
from sentence_transformers import SentenceTransformer
import json
from stl2literal import STL2literal

model_name = sys.argv[1].split('/')[1]

try:
    with open(f'../pkl/{sys.argv[2]}', 'rb') as f:
        translations = pickle.load(f)
        print(f'Loaded {f}')
except Exception as e:
    print("there was an exception")
    print(e)

# Output the translation table as a csv file
os.makedirs(f'../stats/{model_name}', exist_ok=True)
translations.to_csv(f'../stats/{model_name}/translations.csv')

# load in the config specified by the script
with open(f'../config/{sys.argv[3]}') as f:
    params = json.load(f)

embedding_model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(params['embedding_model_name'], device='cpu')

grammar = params['grammar']

#######################################################################################################################
# Table for extraction, parsing success rate
#######################################################################################################################

# translations can be missing because the model didn't need to use all of its syntax feedback correction attempts
success_rate = pandas.DataFrame(columns=['Input Sentence', 'STL Extraction Success Rate', 'STL Parsing Success Rate', 'Number of Translations'])
success_rate['Input Sentence'] = translations['input statement']
success_rate['STL Extraction Success Rate'] = 0
success_rate['STL Parsing Success Rate'] = 0
success_rate['Number of Translations'] = 0

total_success_rate = pandas.DataFrame(index=[0])
total_success_rate['Input Sentence'] = 'Overall'

for col in translations.columns:
    if 'STL-shot' in col:
        success_rate['STL Extraction Success Rate'] += np.where(translations[col] == 'STL could not be extracted', 1, 0)
        success_rate['STL Parsing Success Rate'] += np.where(translations[col] == 'STL could not be parsed', 1, 0)
        success_rate['Number of Translations'] += np.where(translations[col].isnull(), 0, 1)

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

total_success_rate['STL Extraction Success Rate'] = np.where(num_total_translations==0, 0, 1-(total_success_rate['STL Extraction Success Rate'] / num_total_translations))
total_success_rate['STL Parsing Success Rate'] = np.where(num_total_passed_extraction==0, 0, 1-(total_success_rate['STL Parsing Success Rate'] / num_total_passed_extraction))

stats = pandas.concat([success_rate, total_success_rate], ignore_index=True)
stats.to_csv(f'../stats/{model_name}/stats.csv', index=False)

#######################################################################################################################
# TODO: Table where rows are shots and each table belongs to one sentence: report cosine sim. and stl of ALL attempts
#######################################################################################################################

#######################################################################################################################
# Table where rows are shots and each table belongs to one sentence: report best cosine sim. and stl of each semantic attempt
#######################################################################################################################

shot_count = params['num_shots_per_input_sentence']
semantic_count = params['num_semantic_checks']+1
syntax_count = params['num_correction_attempts_per_shot']+1

# construct outer table
# table_arr = []

# print(f"col names: translations.columns")

# print(translations)
translations.to_csv(f'../stats/{model_name}/translations.csv', index=False)

# for each row - sentence in the df
for (index, row) in translations.iterrows():
    # first construct shot x semantic attempt table
    col_names = []
    for i in range(semantic_count):
        col_names.append(f'Semantic attempt {i}')
        col_names.append(f'Semantic attempt {i} sim')

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
        
        # now we need to loop through the semantic attempts and separate them
        # shot0-s1-f2, shot0-s1-f3
        count_semantic_attempts = 0
        count_inside_semantic_attempt = 0
        best_stl = None
        best_sim = None
        done_with_semantic_attempt = False
        first_time = True
        
        # print(f'row subset is: {row_subset}')
        
        for _id, entry in enumerate(row_subset):
            # print(f'entry is: {entry}')
            # print(f'count inside semantic attempt: {count_inside_semantic_attempt}')
            # print(f'semantic attempts: {count_semantic_attempts}')
            # just keep counting by multiples of semantic attempts
            if count_inside_semantic_attempt < semantic_count:
                # print(f'should be inside this 4 times')
                # get the embedding of each entry
                if entry is None or entry == 'STL could not be parsed' or entry == 'STL could not be extracted':
                    # handle this problem
                    count_inside_semantic_attempt += 1

                else:
                    literal = STL2literal(entry, grammar)
                    literal_embedding = ( np.array(model.encode(literal, normalize_embeddings=True)) )
                    sim = cosine_similarity(np.array(literal_embedding).reshape(1,-1), np.array(nl_embedding).reshape(1,-1))[0][0]
                    
                    if first_time or sim > best_sim:
                        # print(f'REAPLCES BEST SIMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM')
                        first_time = False
                        best_sim = sim
                        best_stl = entry

                    count_inside_semantic_attempt += 1

            if count_inside_semantic_attempt == semantic_count:
                # print(f'then should be here once')
                count_inside_semantic_attempt = 0
                r_stl = 'N/A' if first_time else best_stl
                r_sim = 'N/A' if first_time else best_sim
                # done with semantic attempt, need to process this as an entry for this new row
                # print(f'trying to assign stl: {r_stl}')

                new_row.loc[i, f'Semantic attempt {count_semantic_attempts}'] = r_stl
                new_row.loc[i, f'Semantic attempt {count_semantic_attempts} sim'] = r_sim
                # print(f'at the end of semantic attempt, new row is: {new_row}')
                count_semantic_attempts += 1

        # print(f'at the end new row is: {new_row}')
        sentence_table = pandas.concat([sentence_table, new_row], ignore_index=False)
        # print(f'sentence_table is: {sentence_table}')
    
    short_sentence_name = row['input statement'][:10]
    sentence_table.to_csv(f'../stats/{model_name}/{short_sentence_name}_{index}_best_sim_shot_semantic.csv', index=False)
    
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

best_resp.to_csv(f'../stats/{model_name}/best_sim_shot.csv', index=False)

#######################################################################################################################
# Produce similarity heatmaps
#######################################################################################################################
"""
# remove all columns from the table that don't correspond to actual translations
nl_sentence_embeddings = embedding_model.encode(translations['input statement'], normalize_embeddings=True)
literal_sentence_embeddings = embedding_model.encode(translations.filter(regex='Literal-').copy().to_numpy().flatten(), normalize_embeddings=True)

nl_sentences = np.array(translations['input statement'].str[:10])

literal_sentences = translations.filter(regex='Literal-').copy()
for col in literal_sentences.columns:
    literal_sentences[col] = np.where((pandas.isna(literal_sentences[col])) | (literal_sentences[col]=='Literal could not be generated') | (literal_sentences[col]=='STL to literal failed'), literal_sentences[col], "S-" + translations['input statement'].str[:10] + "-A-" + str(col.split('-')[1]))
literal_sentences = literal_sentences.to_numpy().flatten()

indices_to_remove = []
for _id,l in enumerate(literal_sentences):
    if l=='Literal could not be generated' or l=='STL to literal failed' or l==None:
        indices_to_remove.append(_id)
literal_sentences_clean = [x for x in literal_sentences if x != "Literal could not be generated" and x != 'STL to literal failed' and x != None ]
literal_sentence_embeddings_clean = [x for _id, x in enumerate(literal_sentence_embeddings) if _id not in indices_to_remove ]

# compute similarity matrix
# print("NL embeddings:", len(nl_sentence_embeddings))
# print("Literal embeddings:", len(literal_sentence_embeddings_clean))
if len(literal_sentence_embeddings_clean) > 0:
    sim_matrix = cosine_similarity(np.array(nl_sentence_embeddings), np.array(literal_sentence_embeddings_clean))

    # export heatmap
    plt.figure(figsize=(30,10))
    ax = sns.heatmap(sim_matrix, annot=True, vmin=0, vmax=1)

    # NEW BORDER AROUND HEATMAP
    # ax.add_patch(Rectangle((3,4), 1,1,fill=False, edgecolor='blue', lw=3))

    plt.title(f'Produced Literal STL vs. Original NL Cosine Similarity\nModel:{model_name}')
    ax.set_xticks(range(len(literal_sentences_clean)))
    ax.set_yticklabels(nl_sentences, rotation=0)
    ax.set_xticklabels(literal_sentences_clean, rotation=45)
    plt.tight_layout()
    os.makedirs(f'../images/{model_name}', exist_ok=True)
    plt.savefig(f'../images/{model_name}/produced_literal_vs_original_nl.png')
else:
    print("literal sentence embeddings clean was empty")

# compute similarity for the stl against the reference stl using fuzzy matching
stl_ref_statements = np.array(translations['reference STL']) # need to fix these names
stl_produced_statements = translations.filter(regex='STL-').copy()
for col in stl_produced_statements.columns:
    stl_produced_statements[col] = np.where((stl_produced_statements[col]=='STL could not be extracted') | (stl_produced_statements[col]=='STL could not be parsed'), stl_produced_statements[col], "STL-'" + translations['reference STL'].str[:10] + "'-A-" + str(col.split('-')[1]))
stl_produced_statements = stl_produced_statements.to_numpy().flatten()
stl_produced_clean_labels = [x for x in stl_produced_statements if x != "STL could not be extracted" and x != 'STL could not be parsed' ]

if len(stl_produced_clean_labels) > 0:
    reference_stl = translations['reference STL']
    produced_stl_subset = [x for x in translations.filter(regex='STL-').copy().to_numpy().flatten() if x != 'STL could not be extracted' and x != 'STL could not be parsed']
    fuzz_matrix = np.zeros((reference_stl.shape[0], len(produced_stl_subset)))

    for i in range(fuzz_matrix.shape[0]):
        for j in range(fuzz_matrix.shape[1]):
            fuzz_matrix[i][j] = fuzz.ratio(produced_stl_subset[j], reference_stl[i])

    fuzz_matrix = fuzz_matrix/100

    # heatmap
    plt.figure(figsize=(30,10))
    ax = sns.heatmap(fuzz_matrix, annot=True, vmin=0, vmax=1)
    plt.title(f'Produced STL vs. Reference STL Similarity\nModel:Test')
    ax.set_xticks(range(len(stl_produced_clean_labels)))
    ax.set_yticklabels(stl_ref_statements, rotation=0)
    ax.set_xticklabels(stl_produced_clean_labels, rotation=45)
    plt.tight_layout()
    plt.savefig(f'../images/{model_name}/produced_vs_ref_stl.png')
else:
    print("stl produced clean labels was empty")
"""
#######################################################################################################################
# STL heatmaps on a per-sentence basis 
#######################################################################################################################
"""
# Get number of sentences
sentences = translations['input statement'].unique()
num_sentences = len(sentences)

# These aggregate the data and labels for all the plots
stl_matrix_arr = []
stl_produced_labels_arr = []
stl_ref_labels_arr = []

# Generate a small heatmap and labels for each sentence
for _id, sentence in enumerate(sentences):
    # First, need to take a subset of translations that corresponds only to the rows with this sentence
    subset = translations[translations['input statement']==sentence]

    # Labels for the reference STL 
    stl_ref_labels = []
    for index, val in enumerate(subset['reference STL']):
        stl_ref_labels.append(f'{index} - {val}')
    
    # Labels for produced STL - also needs to be cleaned
    stl_produced_labels = []
    stl_produced_cols = subset.filter(regex='STL-').copy()
    for index, row in stl_produced_cols.iterrows():
        # for this row, need to get the STL number
        for j, element in enumerate(row):
            if element=='STL could not be extracted' or element=='STL could not be parsed':
                stl_produced_labels.append(element)
            else:
                stl_produced_labels.append(str(index) + '-A' + str(stl_produced_cols.columns[j].split('-')[1]))
    stl_produced_clean_labels = [x for x in stl_produced_labels if x != 'STL could not be extracted' and x != 'STL could not be parsed']

    if len(stl_produced_clean_labels) <= 0:
        continue

    # Produce the fuzz data matrix
    
    # First set up the matrix inputs
    reference_stl = subset['reference STL'].reset_index(drop=True)
    produced_stl_subset = [x for x in subset.filter(regex='STL-').copy().to_numpy().flatten() if x != 'STL could not be extracted' and x != 'STL could not be parsed']
    fuzz_matrix = np.zeros((reference_stl.shape[0], len(produced_stl_subset)))

    for i in range(fuzz_matrix.shape[0]):
        for j in range(fuzz_matrix.shape[1]):
            fuzz_matrix[i][j] = fuzz.ratio(produced_stl_subset[j], reference_stl[i])
    fuzz_matrix = fuzz_matrix/100

    # Add labels and matrix to overall arrays
    stl_matrix_arr.append(fuzz_matrix)
    stl_produced_labels_arr.append(stl_produced_clean_labels)
    stl_ref_labels_arr.append(stl_ref_labels)


if len(stl_matrix_arr) > 0:
    # Export {stl_matrix_arr}-many plots
    fig, axs = plt.subplots(len(stl_matrix_arr), 1, figsize=(20,60))
    axs = np.atleast_1d(axs)

    # Print all the heatmaps
    for _id, ax in enumerate(axs):
        sns.heatmap(stl_matrix_arr[_id], ax=ax, annot=True, vmin=0, vmax=1)
        ax.set_title(f'Produced STL vs. Reference STL Similarity\nNL Sentence:\n{sentences[_id]}\nModel:{model_name}')
        ax.set_xticks(range(len(stl_produced_labels_arr[_id])))
        ax.set_yticklabels(stl_ref_labels_arr[_id], rotation=0)
        ax.set_xticklabels(stl_produced_labels_arr[_id], rotation=45)
    fig.tight_layout()
    plt.savefig(f'../images/{model_name}/per_sentence_translation_heatmaps.png')
else:
    print("there were no per-sentence matrices")
"""
