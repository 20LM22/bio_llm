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
# Table for each shot: analyze the diff. in cosine sim. between each semantic attempt
#######################################################################################################################

shot_count = params['num_shots_per_input_sentence']
semantic_count = params['num_semantic_checks']
syntax_count = params['num_correction_attempts_per_shot']

# construct outer table
table_arr = []

# print(f"col names: translations.columns")

# for each row in the df
for (index, row) in translations.iterrows():
    # first construct shot x semantic attempt table
    col_names = []
    for i in range(semantic_count):
        col_names.append(f'S{i}')
    row_names = []
    for i in range(shot_count):
        row_names.append(f'shot{i}')
    shot_x_semantic = pandas.DataFrame(index=row_names, columns=col_names)

    print(f"row names: {row}")

    nl_embedding = np.array(model.encode(row['input statement'], normalize_embeddings=True))

    # go the shot x semantic table and fill it in by searching this row of the translations table for columns with the same name
    for sub_index, sub_row in shot_x_semantic.iterrows():
        for col in shot_x_semantic.columns:
            # sub_index = 'shot1'
            # col = 'S1'
            # get all columns with both shot1 and S1 in the column name
            relevant_translations_cols = []
            for sub_col in translations.columns:
                if sub_index in sub_col and col in sub_col:
                    relevant_translations_cols.append(sub_col)
            row_subset = row[relevant_translations_cols] # row_subset = ['shot1-S1-F{all}']
            # need to reduce this row_subset to the entry that has the highest cosine similarity
            row_subset_filtered = [x for x in row_subset if x != 'STL could not be parsed' and x != 'STL could not be extracted' and x is not None]
            literal_embeddings = []
            for stl in row_subset_filtered:
                # get the literal translation, then the embedding that goes with the literal
                literal = STL2literal(stl, grammar)
                literal_embeddings.append( np.array(model.encode(literal, normalize_embeddings=True)) )

            if len(literal_embeddings) == 0:
                sub_row[col] = -1 # TODO: maybe handle this case differently?
            elif len(literal_embeddings) == 1:
                sim = cosine_similarity(np.array(literal_embeddings).reshape(1,-1), np.array(nl_embedding).reshape(1,-1))
                sub_row[col] = max(sim)
            else:
                sim = cosine_similarity(np.array(literal_embeddings), np.array(nl_embedding).reshape(1,-1))
                sub_row[col] = max(sim)
    
    # now construct the comparison table
    col_names = ['Input Sentence']
    for i in range(semantic_count-1):
        col_names.append(f'S{i}/{i+1}')
    row_names = []
    for i in range(shot_count):
        row_names.append(f'shot{i}')
    shot_x_semantic_comparisons = pandas.DataFrame(index=row_names, columns=col_names)
    
    # fill in the table
    for _id, col in enumerate(shot_x_semantic_comparisons.columns):
        if _id == 0:
            continue
        split = col.split('/')
        print(f'split: {split}')
        col1 = split[0]
        col2 = 'S' + split[1]
        shot_x_semantic_comparisons[col] = shot_x_semantic[col2] - shot_x_semantic[col1] 

    # add total column
    shot_x_semantic_comparisons['Total'] = shot_x_semantic_comparisons.sum(axis=1)

    # append this table (for this sentence) to the overall table
    table_arr.append(shot_x_semantic_comparisons)

res = pandas.concat(table_arr, ignore_index=False)
res.to_csv(f'../stats/{model_name}/sim_diff_across_attempts.csv', index=False)

#######################################################################################################################
# Table for each shot: report the best cosine sim.
#######################################################################################################################

## Not done

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

        print(f'the row subset filtered is: {row_subset_filtered}')
        literal_embeddings = []
        for stl in row_subset_filtered:
            # get the literal translation, then the embedding that goes with the literal
            literal = STL2literal(stl, grammar)
            literal_embeddings.append( np.array(model.encode(literal, normalize_embeddings=True)) )

        if len(literal_embeddings) == 0:
            row[f'shot{i}'] = None
            row[f'shot{i} sim'] = None
        elif len(literal_embeddings) == 1:
            sim = cosine_similarity(np.array(literal_embeddings).reshape(1,-1), np.array(nl_embedding).reshape(1,-1))
            row[f'shot{i}'] = row_subset_filtered[0]
            row[f'shot{i} sim'] = max(sim)
        else:
            sim = cosine_similarity(np.array(literal_embeddings), np.array(nl_embedding).reshape(1,-1))
            row[f'shot{i} sim'] = max(sim)
            row[f'shot{i}'] = row_subset_filtered[np.argmax(sim)]

best_resp.to_csv(f'../stats/{model_name}/sim_diff_across_attempts.csv', index=False)

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
