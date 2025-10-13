"""
1. load in a group of STL sentences --> where do they come from? Format them as an array
2. we want to start by being as restrictive as possible:
    2a. bin the sentences into groups based on whether they have the exact same APs
    2b. what to do with the sentences that don't fall into a bin? that's ok, there can be bins with just 1 element
3. then we try to reduce the number of elements in each bin --> we do this iteratively until convergence
    3a. for each bin do:
        do all pairwise comparisons between elements
            for each pairwise comparison:
                determine if one element represents a superset or subset of the other --> take either the smaller or larger
                I think for now take the more specific element
            continue this until the bin only has 1 element or the size of the bin stops changing between iterations **need the SAT solver thing for this

python consolidate.py 'gpt-4o-2024-08-06' "prelim_set_translations_gpt-4o-2024-08-06_nx_2_ny_2_nz_18_2025-10-05_20-07-09.pkl" "config_nx_2_ny_2_nz_18_prelim_set.json" '2025-10-05_20-07-09'
"""

import numpy as np
import pandas, pickle, json, os, sys
from lark import Lark
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from z3 import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from stl2literal import get_species_list_STL2literal, get_smt

# Step 1: load in the STL statements

with open(f'../config/{sys.argv[3]}') as f:
    params = json.load(f)

model_name = sys.argv[1]
model = SentenceTransformer(params['embedding_model_name'], device='cpu')
shot_count = params['num_shots_per_input_sentence']
syntax_count = params['num_correction_attempts_per_shot']
semantic_count = params['num_semantic_checks']
grammar = params['grammar']
set_name = params["set_name"]
time = sys.argv[4]
parser = Lark(grammar)

res = defaultdict(list)

try:
    with open(f'../pkl/{model_name}/{sys.argv[2]}', 'rb') as f:
        translations = pickle.load(f)
        print(f'Loaded {f}')
except Exception as e:
    print(e)

print("starting step 1")
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
                # need to record stl
                syntactically_valid_translations.append(entry)

    res[row['input statement']] = syntactically_valid_translations

# now res is filled like this: {'input sentence 1': [stl1, stl2, etc.], 'input sentence 2': [stl1, stl2, etc.]}
# 2. we want to start by being as restrictive as possible:
#     2a. bin the sentences into groups based on whether they have the exact same APs
#     2b. what to do with the sentences that don't fall into a bin? that's ok, there can be bins with just 1 element
print("starting step 2")
for input_sentence in res.keys():
    stl_set = res[input_sentence] # stl_set is [stl1, stl2, etc.]
    bin_dict = defaultdict(list)

    for stl in stl_set:
        # for each input sentence, let's create a dictionary
        # then let's parse this stl to get a list of its APs
        parsed_stl = parser.parse(stl)
        species_list = get_species_list_STL2literal(parsed_stl) # the species list is now a string

        # need to make the species list a key and the stl the value
        bin_dict[species_list].append(stl)

    # Step 3: Now all the bins have been filled up
    # iteratively consolidated them
    for key in bin_dict.keys():
        while True:
            prev_len = len(bin_dict[key])
            remove_items = set()

            # pairwise comparisons
            for i in range(0, len(bin_dict[key])-1):
                stl1 = parser.parse(bin_dict[key][i])
                # need to come up with a mapping of this parse tree to an SMT boolean expression

                result_1, signals_1, derivatives_1 = get_smt(stl1)
                for s, t_a, t_b in signals_1:
                    s = [Real(f'{s}_{t}') for t in range(int(t_a), int(t_b))]
                for d, t_a, t_b in derivatives_1:
                    d = [Real(f'{d}_{t}') for t in range(int(t_a), int(t_b))]
                    d_derivative = [d[i+1] - d[i] for i in range(len(d) - 1)]

                for j in range(i+1, len(bin_dict[key])):
                    if j in remove_items:
                        continue
                    # need to compare bin_dict[key][i] and bin_dict[key][j]
                    stl2 = parser.parse(bin_dict[key][j])
                    # get phi and psi from stl1 and stl2
                    result_2, signals_2, derivatives_2 = get_smt(stl2)
                    for s, t_a, t_b in signals_2:
                        s = [Real(f'{s}_{t}') for t in range(int(t_a), int(t_b))]
                    for d, t_a, t_b in derivatives_2:
                        d = [Real(f'{d}_{t}') for t in range(int(t_a), int(t_b))]
                        d_derivative = [d[i + 1] - d[i] for i in range(len(d) - 1)]

                    s = Solver()
                    s.add(Not(result_1 == result_2))
                    if s.check() == unsat:
                        # stl1 == stl2 so stl2 can be removed
                        remove_items.add(j)

            bin_dict[key] = [stl for i, stl in enumerate(bin_dict[key]) if i not in remove_items]

            if len(bin_dict[key]) == prev_len or len(bin_dict[key]) == 1:
                break

    output = []
    for k in bin_dict.keys():
        output.extend(bin_dict[k])
    res[input_sentence] = output

row_arr = [[key] + value for key, value in res.items()]
max_len = max(len(row) for row in row_arr)
for row in row_arr:
    row.extend([''] * (max_len - len(row)))
p = pandas.DataFrame(row_arr)
p.to_csv(f'../stats/{model_name}/AFTER_{set_name}_consolidated_set_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.csv', index=False)
