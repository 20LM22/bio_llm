import sys
sys.stdout.reconfigure(encoding='utf-8')

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle, os, pandas
from sentence_transformers import SentenceTransformer
import json
from collections import defaultdict

sys.path.insert(1, '..')
from stl2literal import STL2literal
print('done importing')

model_name = sys.argv[1]

for i in range(0,4):
    print(f'{i}: {sys.argv[i]}')

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

model = SentenceTransformer(params['embedding_model_name'], device='cpu')
shot_count = params['num_shots_per_input_sentence']
syntax_count = params['num_correction_attempts_per_shot']
semantic_count = params['num_semantic_checks']
time = sys.argv[4]
set_name = params["set_name"]

grammar = params['grammar']

res = defaultdict(list)
print("waiting")

# fill in semantic successes
for index, row in translations.iterrows():
    print("in translations")
    # for the nx=2, ny=2, nz=18, all have to be done

    # for the nx=2, ny=1, nz=18 results, only TNF ("times intervals, then decreased at the")
    # and It is reported ("It is reported that in recovered case") need to be recorded
    #if "It is reported that in recovered case" in row['input statement'] or "times intervals, then decreased at the" in row['input statement']:
    if 1==1:
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

# # print these out to the user and have them mark whether they think they're good or not
translations_total = 0

for key in res.keys():
    translations_total += len(res[key])

translations_count = 0
correct = 0
incorrect = 0

for key in res.keys(): # res_top.keys():
    print(f"key is: {key}")
    print(f"res[key]: {res[key]}")
    new_syn_valid_arr = []
    for stl, sim in res[key]: # res_top[key]:
        print(f"{translations_count}/{translations_total} annotations completed.")
        translations_count += 1
        # need to ask the user to mark the annotation as a 0 or 1
        print(f"Sentence: {key}")
        print(f"STL: {stl}")
        choice = input("1 for yes, 0 for no: ")
        if int(choice) == 1:
            correct += 1
        elif int(choice) == 0:
            incorrect += 1
        # then need to construct a new array that we will replace the current one in the dictionary with
        # but this array will have the user's annotation
        new_syn_valid_arr.append((stl,sim,choice))
    res[key] = new_syn_valid_arr # res_top[key] = new_syn_valid_arr

"""
for key in res_bottom.keys():
    new_syn_valid_arr = []
    for stl, sim in res_bottom[key]:
        print(f"{translations_count}/{translations_total} annotations completed.")
        translations_count += 1
        # need to ask the user to mark the annotation as a 0 or 1
        print(f"Sentence: {key}")
        print(f"STL: {stl}")
        choice = input("1 for yes, 0 for no: ")
        if int(choice) == 1:
            correct += 1
        elif int(choice) == 0:
            incorrect += 1
        # then need to construct a new array that we will replace the current one in the dictionary with
        # but this array will have the user's annotation
        new_syn_valid_arr.append((stl,sim,choice))
    res_bottom[key] = new_syn_valid_arr
"""

p = pandas.DataFrame(data=[[correct, incorrect, translations_total]], columns=["correct", "incorrect", "total"]) # deepseek has 17/347 correct
p.to_csv(f'../stats/{model_name}/{set_name}_semantically_correct_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.csv', index=False)

try:
    with open(f'../pkl/{set_name}_semantic_labels_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl', 'wb') as r:
        pickle.dump(res, r)
    """
    with open(f'../pkl/{set_name}_top_3_histogram_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl', 'wb') as r:
        pickle.dump(res_top, r)
    with open(f'../pkl/{set_name}_bottom_3_histogram_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl', 'wb') as r:
        pickle.dump(res_bottom, r)
    """
except Exception as e:
    print("there was a pickle problem")
    print(e)
