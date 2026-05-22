import numpy as np
import pandas, pickle, json, os, sys
from lark import Lark
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from z3 import *
from pathlib import Path

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
            return

        # Case 3: atomic omega
        if isinstance(node, Tree) and node.data == "omega" and node.children[0].data != "omega_and_omega" and node.children[0].data != "u_and_u":
            start = node.meta.start_pos
            end = node.meta.end_pos
            pieces.append(stl_str[start:end])
            return

        # Otherwise: recurse (do NOT collect here)
        if isinstance(node, Tree):
            for child in node.children:
                collect(child, node)

    collect(tree)
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

with open(f'../config/{sys.argv[3]}') as f:
    params = json.load(f)

model_name = sys.argv[1]
input_path = sys.argv[2]
model = SentenceTransformer(params['embedding_model_name'], device='cpu')
shot_count = params['num_shots_per_input_sentence']
syntax_count = params['num_correction_attempts_per_shot']
semantic_count = params['num_semantic_checks']
grammar = params['grammar']
set_name = params["set_name"]
time = sys.argv[4]
consolidation_type = sys.argv[5]
output_json_path = sys.argv[6] if len(sys.argv) > 6 else None
parser = Lark(grammar, propagate_positions=True)
general = consolidation_type == "general"


def load_input(path):
    if path.lower().endswith('.json'):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    with open(path, 'rb') as f:
        return pickle.load(f)


def normalize_entry(entry):
    if isinstance(entry, dict):
        return entry.get('formula') or entry.get('stl')
    if isinstance(entry, (tuple, list)):
        return entry[0] if len(entry) > 0 else None
    return entry


def collect_stl_candidates(raw_input):
    res = defaultdict(list)

    if isinstance(raw_input, pandas.DataFrame):
        relevant_cols = [col for col in raw_input.columns if col.startswith('shot')]
        for _, row in raw_input.iterrows():
            sentence = row['input statement']
            for entry in row[relevant_cols]:
                if (
                    entry is None or
                    entry == 'STL could not be extracted' or
                    entry == 'STL could not be parsed' or
                    pandas.isna(entry)
                ):
                    continue
                stl = str(entry).replace('∞', 'inf')
                res[sentence].append(stl)
        return res

    if isinstance(raw_input, dict):
        for sentence, entries in raw_input.items():
            if isinstance(entries, dict):
                entries = [entries]
            for entry in entries:
                stl = normalize_entry(entry)
                if stl is None:
                    continue
                res[sentence].append(str(stl).replace('∞', 'inf'))
        return res

    if isinstance(raw_input, list):
        for record in raw_input:
            sentence = record.get('input_sentence')
            if sentence is None:
                continue
            stl_entries = record.get('stl', [])
            for entry in stl_entries:
                stl = normalize_entry(entry)
                if stl is None:
                    continue
                res[sentence].append(str(stl).replace('∞', 'inf'))
        return res

    raise ValueError('Unsupported input format for consolidation')


raw_input = load_input(input_path)
print(f"Loaded consolidation input from {input_path}")
stl_statements = collect_stl_candidates(raw_input)

if output_json_path is None:
    output_json_path = (
        f'../stats/{model_name}/{set_name}_consolidated_output_{consolidation_type}_'
        f'{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.json'
    )

res = defaultdict(list)

for sentence, stl_sims in stl_statements.items():
    for stl in stl_sims:
        res[sentence].append(stl)

global_stats = {}
per_bin_stats = defaultdict(dict)

for index, input_sentence in enumerate(res.keys()):
   
    stl_set = res[input_sentence] # stl_set is [stl1, stl2, etc.]
    bin_dict = defaultdict(list)
            
    # ------------------------------------------------------------
    # Split statements on outer conjunctions
    # ------------------------------------------------------------   
    for stl in stl_set: 
        try:
            stl_pieces = split_outermost(stl, parser)
        except Exception as e:
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

    # ------------------------------------------------------------
    # Iteratively consolidate statements within each bin
    # ------------------------------------------------------------  
    for key in bin_dict.keys():
        
        # Remove duplicates first (exact string matches)
        bin_dict[key] = remove_duplicates(bin_dict[key])
        
        while True:
            prev_len = len(bin_dict[key])
            remove_items = set()

            # Pairwise comparisons
            for i in range(0, len(bin_dict[key])-1):
                if i in remove_items:
                    continue

                stl1 = parser.parse(bin_dict[key][i]["stl"])
                result_1 = get_smt(stl1)

                for j in range(i+1, len(bin_dict[key])):
                    if j in remove_items:
                        continue
                    stl2 = parser.parse(bin_dict[key][j]["stl"])
                    result_2 = get_smt(stl2)

                    s = Solver()
                    
                    if (general): # General consolidation
                        # Check if stl1 => stl2 (stl2 redundant and remove)
                        s.push()
                        s.add(Not(Implies(result_1, result_2)))
                        if s.check() == z3.unsat:
                            # stl1 absorbs stl2
                            bin_dict[key][i]["absorbed"] += bin_dict[key][j]["absorbed"] + 1
                            remove_items.add(j)
                            s.pop()
                            continue
                        s.pop()
                        # Check if stl2 => stl1 (stl1 redundant and remove)
                        s.push()
                        s.add(Not(Implies(result_2, result_1)))
                        if s.check() == z3.unsat:
                            # stl2 absorbs stl1
                            bin_dict[key][j]["absorbed"] += bin_dict[key][i]["absorbed"] + 1
                            remove_items.add(i)
                            s.pop()
                            break
                        s.pop()
                    else: # Specific consolidation                        
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

# ------------------------------------------------------------
# Save results
# ------------------------------------------------------------  

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
    
# Save consolidated results to JSON
output_path = Path(output_json_path)
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(records, f, ensure_ascii=False, indent=2)
