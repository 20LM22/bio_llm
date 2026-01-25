import sys
import os
import json
import pandas as pd
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

print("Starting annotation of consolidated JSON set")

# -------------------- Command-line arguments --------------------
# Example:
# python annotate_consolidated_json.py 'gpt-5.2-2025-12-11' '../stats/gpt-5.2-2025-12-11/consolidated_set.json' 'config_nx_3_ny_1_nz_18_test_set.json' '2025-12-30_00-35-54'

model_name = sys.argv[1]
consolidated_json = sys.argv[2]  # JSON file, line-delimited
config_file = sys.argv[3]
time = sys.argv[4]

# -------------------- Load consolidated JSON --------------------
res = []  # list of entries

try:
    with open(consolidated_json, 'r', encoding='utf-8') as f:
        for line in f:
            obj = json.loads(line)
            res.append(obj)
    print(f"Loaded {consolidated_json}, {len(res)} sentences")
except Exception as e:
    print("Error loading JSON:", e)
    sys.exit(1)

# -------------------- Load config for naming consistency --------------------
with open(f'../config/{config_file}', 'r', encoding='utf-8') as f:
    params = json.load(f)

shot_count = params['num_shots_per_input_sentence']
syntax_count = params['num_correction_attempts_per_shot']
semantic_count = params['num_semantic_checks']
set_name = params["set_name"]

# -------------------- Manual annotation loop --------------------
translations_total = sum(len(entry["stl"]) for entry in res)
translations_count = 0
correct = 0
incorrect = 0

annotated = []

for entry in res:
    sentence = entry["input_sentence"]
    stl_list = entry["stl"]

    print("="*80)
    print(f"Sentence:\n{sentence}")

    annotated_entry = {"input_sentence": sentence, "stl": []}

    for stl_dict in stl_list:
        formula = stl_dict["formula"]
        absorbed = stl_dict.get("absorbed", None)
        translations_count += 1

        print("-"*80)
        print(f"{translations_count}/{translations_total}")
        print(f"STL: {formula}   (absorbed: {absorbed})")

        choice = input("1 = correct, 0 = incorrect (ENTER = 0): ").strip()
        label = 1 if choice == "1" else 0

        if label:
            correct += 1
        else:
            incorrect += 1

        annotated_entry["stl"].append({"formula": formula, "absorbed": absorbed, "label": label})

    annotated.append(annotated_entry)

# -------------------- Save annotated JSON --------------------
os.makedirs(f'../stats/{model_name}', exist_ok=True)
annotated_json_file = f'../stats/{model_name}/{set_name}_annotated_AFTER_CONSOLIDATED_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.json'

with open(annotated_json_file, 'w', encoding='utf-8') as f:
    for entry in annotated:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"Annotated JSON saved to {annotated_json_file}")

# -------------------- Save summary CSV --------------------
stats_df = pd.DataFrame(
    [[correct, incorrect, translations_total]],
    columns=["correct", "incorrect", "total"]
)

stats_csv_file = f'../stats/{model_name}/{set_name}_semantic_labels_AFTER_CONSOLIDATED_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.csv'
stats_df.to_csv(stats_csv_file, index=False)

print(f"Summary CSV saved to {stats_csv_file}")
print(f"Total translations: {translations_total}, Correct: {correct}, Incorrect: {incorrect}")
