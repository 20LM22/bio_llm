"""
1. load in a group of STL sentences --> format them as an array
2. then:
    2a. break up all the sentences by splitting on outer conjunctions (ands)
    2b. bin the resulting sentence pieces into groups based on whether they have the exact same APs
    2c. what to do with the sentences that don't fall into a bin? that's ok, there can be bins with just 1 element
3. then we try to reduce the number of elements in each bin --> we do this iteratively until convergence
    3a. for each bin do:
        do all pairwise comparisons between elements
            for each pairwise comparison:
                determine if one element represents a superset or subset of the other --> take either the smaller or larger
                I think for now take the more specific element
            continue this until the bin only has 1 element or the size of the bin stops changing between iterations **need the SAT solver thing for this

Run with:
python consolidate.py 'gpt-4o-2024-08-06' "prelim_set_translations_gpt-4o-2024-08-06_nx_2_ny_2_nz_18_2025-10-05_20-07-09.pkl" "config_nx_2_ny_2_nz_18_prelim_set.json" '2025-10-05_20-07-09'
python consolidate.py 'gpt-5.2-2025-12-11' "test_set_translations_gpt-5.2-2025-12-11_nx_3_ny_1_nz_18_2025-12-30_00-35-54.pkl" "config_nx_3_ny_1_nz_18_test_set.json" '2025-12-30_00-35-54'

"""

import numpy as np
import pandas, pickle, json, os, sys
from lark import Lark
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from z3 import *

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from stl2literal import get_species_list_STL2literal, get_smt

from lark import Tree

def tree_to_text(tree):
    """Flatten a Lark tree to its original string (concatenate all leaves)."""
    if isinstance(tree, str):
        return tree
    elif isinstance(tree, Tree):
        return " ".join(tree_to_text(child) for child in tree.children)
    else:
        return str(tree)

def split_outermost(stl_str, parser):
    tree = parser.parse(stl_str)
    pieces = []

    def collect(node, parent=None):
        # Case 1: always split omega_and_omega
        if isinstance(node, Tree) and node.data == "omega_and_omega":
            for child in node.children:
                collect(child, node)
            return

        # Case 2: split u_and_u iff parent is omega
        if (
            isinstance(node, Tree)
            and node.data == "u_and_u"
            and isinstance(parent, Tree)
            and parent.data == "omega"
        ):
            # print("we found a u_and_u that needs to be split")
            for child in node.children:
                start = child.meta.start_pos
                end = child.meta.end_pos
                pieces.append(stl_str[start:end])
                # collect(child, node)
            return

        # Case 3: atomic omega
        if isinstance(node, Tree) and node.data == "omega" and node.children[0].data != "omega_and_omega" and node.children[0].data != "u_and_u":
            # print("i am inside omega")
            start = node.meta.start_pos
            end = node.meta.end_pos
            pieces.append(stl_str[start:end])
            return

        # Otherwise: recurse (do NOT collect here)
        if isinstance(node, Tree):
            # print("i am recursing")
            for child in node.children:
                collect(child, node)

    collect(tree)
    # print(f"number of elements in pieces: {len(pieces)}")
    # print(f"pieces: {pieces}")
    return [p.strip() for p in pieces]

def remove_duplicates(entries):
    merged = {}
    for entry in entries:
        key = " ".join(entry["stl"].split())
        if key not in merged:
            merged[key] = {
                "stl": entry["stl"],
                "absorbed": entry["absorbed"]
            }
        else:
            merged[key]["absorbed"] += entry["absorbed"] + 1
    return list(merged.values())

# Step 1: load in the STL statements

with open(f'../config/{sys.argv[3]}') as f:
    params = json.load(f)
# print("done with that")

model_name = sys.argv[1]
model = SentenceTransformer(params['embedding_model_name'], device='cpu')
shot_count = params['num_shots_per_input_sentence']
syntax_count = params['num_correction_attempts_per_shot']
semantic_count = params['num_semantic_checks']
grammar = params['grammar']
set_name = params["set_name"]
time = sys.argv[4]
parser = Lark(grammar, propagate_positions=True)

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
# print(res)

# now res is filled like this: {'input sentence 1': [stl1, stl2, etc.], 'input sentence 2': [stl1, stl2, etc.]}
# 2. we want to start by being as restrictive as possible:
#     2a. bin the sentences into groups based on whether they have the exact same APs
#     2b. what to do with the sentences that don't fall into a bin? that's ok, there can be bins with just 1 element
print("starting step 2")

global_stats = {}
per_bin_stats = defaultdict(dict)

for index, input_sentence in enumerate(res.keys()):
   
    stl_set = res[input_sentence] # stl_set is [stl1, stl2, etc.]
    # print(f"\nstl set is:\n")
    bin_dict = defaultdict(list)
            
    for stl in stl_set:     # Step 2A: split on outer conjunctions
        # print(f"stl: {stl}")
        try:
            stl_pieces = split_outermost(stl, parser)
            # print("split!")
        except Exception as e:
            # print(f"Failed to split STL: {e}")
            continue

        for piece in stl_pieces:
            parsed_piece = parser.parse(piece)
            species_list = get_species_list_STL2literal(parsed_piece)
            bin_dict[species_list].append({
                "stl": piece,
                "absorbed": 0
            })
                    
    initial_total = sum(len(v) for v in bin_dict.values())
    for key in bin_dict:
        per_bin_stats[input_sentence][key] = {
            "initial": len(bin_dict[key])
    }

    # Step 3: Now all the bins have been filled up
    # iteratively consolidated them
    for key in bin_dict.keys():
        
        # PHASE 1: exact duplicate removal
        bin_dict[key] = remove_duplicates(bin_dict[key])
        
        while True:
            prev_len = len(bin_dict[key])
            remove_items = set()

            # pairwise comparisons
            for i in range(0, len(bin_dict[key])-1):
                if i in remove_items:
                    continue

                stl1 = parser.parse(bin_dict[key][i]["stl"])
                # print(f"statement1: {bin_dict[key][i]["stl"]}")
                # print(f"stl1: {stl1}")
                
                result_1 = get_smt(stl1) # stl1

                for j in range(i+1, len(bin_dict[key])):
                    if j in remove_items:
                        continue
                    # need to compare bin_dict[key][i] and bin_dict[key][j]
                    stl2 = parser.parse(bin_dict[key][j]["stl"])
                    result_2 = get_smt(stl2) # stl2

                    s = Solver()

                    # # # Keep GENERAL:
                    # # Check if stl1 => stl2 (stl2 redundant and remove)
                    # s.push()
                    # s.add(Not(Implies(result_1, result_2)))
                    # if s.check() == z3.unsat:
                    #     # stl1 absorbs stl2
                    #     bin_dict[key][i]["absorbed"] += bin_dict[key][j]["absorbed"] + 1
                    #     remove_items.add(j)
                    #     s.pop()
                    #     continue
                    # s.pop()
                    # # Check if stl2 => stl1 (stl1 redundant and remove)
                    # s.push()
                    # s.add(Not(Implies(result_2, result_1)))
                    # if s.check() == z3.unsat:
                    #     # stl2 absorbs stl1
                    #     bin_dict[key][j]["absorbed"] += bin_dict[key][i]["absorbed"] + 1
                    #     remove_items.add(i)
                    #     s.pop()
                    #     break
                    # s.pop()

                    # Keep SPECIFIC:
                    # Check if stl1 => stl2 (stl1 redundant and remove)
                    s.push()
                    s.add(Not(Implies(result_1, result_2)))
                    if s.check() == z3.unsat:
                        # stl2 absorbs stl1
                        bin_dict[key][j]["absorbed"] += bin_dict[key][i]["absorbed"] + 1
                        remove_items.add(i)
                        s.pop()
                        break
                    s.pop()
                    # Check if stl2 => stl1 (stl2 redundant and remove)
                    s.push()
                    s.add(Not(Implies(result_2, result_1)))
                    if s.check() == z3.unsat:
                        # stl1 absorbs stl2
                        bin_dict[key][i]["absorbed"] += bin_dict[key][j]["absorbed"] + 1
                        remove_items.add(j)
                        s.pop()
                        continue
                    s.pop()

            bin_dict[key] = [stl for i, stl in enumerate(bin_dict[key]) if i not in remove_items]

            if len(bin_dict[key]) == prev_len or len(bin_dict[key]) == 1:
                break

    final_total = sum(len(v) for v in bin_dict.values())

    global_stats[input_sentence] = {
        "initial": initial_total,
        "final": final_total,
        "reduction": initial_total - final_total,
        "reduction_ratio": 1 - (final_total / initial_total if initial_total > 0 else 0.0)
    }

    for key in bin_dict:
        per_bin_stats[input_sentence][key].update({
            "final": len(bin_dict[key]),
            "reduction": per_bin_stats[input_sentence][key]["initial"] - len(bin_dict[key]),
            "reduction_ratio": (1- (
                len(bin_dict[key]) /
                per_bin_stats[input_sentence][key]["initial"]
                if per_bin_stats[input_sentence][key]["initial"] > 0 else 0.0)
            )
    })

    output = []
    for k in bin_dict.keys():
        output.extend(bin_dict[k])
    res[input_sentence] = output

from pathlib import Path

records = []

for input_sentence, entries in res.items():
    record = {
        "input_sentence": input_sentence,
        "stl": [],
        "global": {},
        "per_bin_stats": per_bin_stats[input_sentence],
    }

    # STL entries
    for entry in entries:
        record["stl"].append({
            "formula": entry["stl"],
            "absorbed": entry["absorbed"],
        })

    # Global reduction stats
    gs = global_stats[input_sentence]
    record["global"] = {
        "initial": gs["initial"],
        "final": gs["final"],
        "reduction": gs["reduction"],
        "reduction_ratio": 1-gs["reduction_ratio"],
    }

    records.append(record)
    
out_path = Path(
    f'../stats/{model_name}/AFTER_{set_name}_consolidated_set_'
    f'nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.json'
)

out_path.parent.mkdir(parents=True, exist_ok=True)

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)

####
consolidated_for_cosine = {}

for input_sentence, entries in res.items():
    consolidated_for_cosine[input_sentence] = [
        entry["stl"] for entry in entries
    ]

cosine_out_path = Path(
    f'../pkl/{set_name}_consolidated_{model_name}_'
    f'nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl'
)

with open(cosine_out_path, "wb") as f:
    pickle.dump(consolidated_for_cosine, f)

print(f"Saved consolidated STL pickle to {cosine_out_path}")


""" 
test set should be bigger: 70 total
more models and more sentences
when you have consolidated results then what?
future work, user study
annotate the cosine filtered version
if we run a user study --> conslidating with correctness
bring it back to human level with backtranslation: human in the loop
frequency doens't correlate with the final correctness
need to annotate results
do the resuting sentences capture the full breadht of the sentence
make contributions clear
start getting th eresults
narrow the next steps
share a draft again
first run the 90th percentile heuristic, then run consolidation

todo:
run on the test set without any semantic feedback, llm of the power, best run on the hardest ones --> does it hurt them??
    step 1: find the three hardest sentences from the test set
        (1) This is the reason that seroconversion (undetectable stage to production of IgM followed by
        IgG) in 100% of infected people (with positive virus-specific IgG) is achieved 17–19 days
        after commencement of indications [7].
        
        (2) In parallel, stimulation with CpG 2216 also resulted in lower, but clearly detectable, amounts
        of IFNs.
        
        (3) Monocyte chemotactic factor chemokine(C-C motif) ligand 2 (CCL2) was increased in the
        blood of infected patients as well as the transcripts of its receptor CCR2; this was associated
        with low counts of circulating inflammatory monocytes (Fig. 4I), suggesting a rolefor the
        CCL2/CCR2 axis in the monocyte chemo-attraction into the inflamed lungs.
    step 2: we need to make a config file with just these three options. let's run gpt.
        the configs are:
            config_nx_3_ny_{0,1,2}_nz_18_hard_set.json
    step 3: we need to run each of these.
        i'd like to close my laptop, so that means running each of these in tmux i think

"""