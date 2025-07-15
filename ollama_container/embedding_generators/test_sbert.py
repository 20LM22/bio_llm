import time
import numpy as np
import os
import pandas
from collections import defaultdict
import pickle
from sentence_transformers import SentenceTransformer

# Generates pkl files from <csv> for all models (<model>) included in 'models_pkl_names'
# Saves pkl files as 'ambiguous_mod_<pkl_name>' in ../pkl/<pkl_name>.pkl

csv = '../csv_inputs/text_input_ambiguous_mod.csv' # specify csv input
models_pkl_names = [['all-MiniLM-L6-v2', 'st_mini_lm_v2'], ['Qwen/Qwen3-Embedding-0.6B', 'st_qwen_p6_v2']] # specify models, pkl names

csv_file = pandas.read_csv(csv, header=None)

for entry in models_pkl_names:
    model_name = entry[0]
    pkl_name = entry[1]

    embedding_dict = defaultdict(dict)
    model = SentenceTransformer(model_name)

    # loop over all of the rows of the file
    # for unique NL statements: first get their embedding, then get embedding of stl and literal, package into dict
    # for already-seen NL statements: get embedding of stl and literal, package into dict

    start = time.time()

    for _id, row in csv_file.iterrows():
        # obtain the nl statement
        nl = row[1]
        embedding_nl = np.array(model.encode(nl, normalize_embeddings=True)) if nl not in embedding_dict else embedding_dict[nl]['embedding']

        # attach embedding of stl and literal stl
        embedding_stl = np.array(model.encode(row[2], normalize_embeddings=True))
        embedding_literal = np.array(model.encode(row[3], normalize_embeddings=True))

        embedding_dict[nl]['embedding'] = embedding_nl
        if 'stl' in embedding_dict[nl]:
            embedding_dict[nl]['stl'].append((row[2], embedding_stl))
            embedding_dict[nl]['literal'].append((row[3], embedding_literal))
        else:
            embedding_dict[nl]['stl'] = [(row[2], embedding_stl)]
            embedding_dict[nl]['literal'] = [(row[3], embedding_literal)]

    print("*************************************************")
    print(f'Completeed in {time.time()-start} seconds')
    print("*************************************************")

    # write dictionary to pkl
    try:
        with open(f'../pkl/ambiguous_mod_{pkl_name}.pkl', 'wb') as results:
            pickle.dump(embedding_dict, results)
    except Exception as e:
        print(e)
