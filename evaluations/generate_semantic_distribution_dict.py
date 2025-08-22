import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle, sys, os, pandas
from sentence_transformers import SentenceTransformer
import json
from collections import defaultdict

sys.path.insert(1, '..')
from stl2literal import STL2literal

model_name = sys.argv[1]

try:
    with open(f'../pkl/{model_name}/{sys.argv[2]}', 'rb') as f:
        translations = pickle.load(f)
        print(f'Loaded {f}')
except Exception as e:
    print(e)

# Make sure model folder is available
os.makedirs(f'../stats/{model_name}', exist_ok=True)

# Load config specified by the script
with open(f'../config/{sys.argv[3]}') as f:
    params = json.load(f)

embedding_model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(params['embedding_model_name'], device='cpu')
shot_count = params['num_shots_per_input_sentence']
syntax_count = params['num_correction_attempts_per_shot']
semantic_count = params['num_semantic_checks']

grammar = params['grammar']

#######################################################################################################################
# Table for extraction, parsing success rate
#######################################################################################################################

res = defaultdict(list)

# fill in semantic successes
for index, row in translations.iterrows():

    nl_embedding = np.array(model.encode(row['input statement'], normalize_embeddings=True))
    row_subset = pandas.DataFrame()
    row_counter = 0

    syntactically_valid_translations = []

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
                # need to record stl and its similarity
                syntactically_valid_translations.append((entry, sim))

    res[row['input statement']] = syntactically_valid_translations

# print these out to the user and have them mark whether they think they're good or not
translations_total = 0
for key in res.keys():
    translations_total += len(res[key])

translations_count = 0

for key in res.keys():
    new_syn_valid_arr = []
    for stl, sim in res[key]:
        print(f"{translations_count}/{translations_total} annotations completed.")
        translations_count += 1
        # need to ask the user to mark the annotation as a 0 or 1
        print(f"Sentence: {key}")
        print(f"STL: {stl}")
        choice = input("1 for yes, 0 for no: ")
        # then need to construct a new array that we will replace the current one in the dictionary with
        # but this array will have the user's annotation
        new_syn_valid_arr.append((stl,sim,choice))
    res[key] = new_syn_valid_arr

try:
    with open(f'../pkl/high_low_histogram_distribution_comparison_{model_name}_shots_{shot_count}_syntax_{syntax_count}_semantic_{semantic_count}.pkl', 'wb') as r:
        pickle.dump(res, r)
except Exception as e:
    print("there was a pickle problem")
    print(e)