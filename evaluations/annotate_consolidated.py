import sys
import os
import json
import pandas as pd
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

model_name = sys.argv[1]
consolidated_json = sys.argv[2]
config_file = sys.argv[3]
time = sys.argv[4]

res = []
try:
    with open(consolidated_json, 'r', encoding='utf-8') as f:        
        content = f.read().strip()

        if content.startswith('['):
            data = json.loads(content)
            if not isinstance(data, list):
                raise ValueError("Top-level JSON is not a list")
            res.extend(data)

    print(f"Loaded {consolidated_json}, {len(res)} sentences")
except Exception as e:
    print("Error loading JSON:", e)
    sys.exit(1)

consolidation_type = sys.argv[5] if len(sys.argv) > 5 else 'general'

with open(f'../config/{config_file}', 'r', encoding='utf-8') as f:
    params = json.load(f)

shot_count = params['num_shots_per_input_sentence']
syntax_count = params['num_correction_attempts_per_shot']
semantic_count = params['num_semantic_checks']
set_name = params["set_name"]

# ------------------------------------------------------------
# Annotate consolidated translations
# ------------------------------------------------------------
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

# ------------------------------------------------------------
# Save annotations
# ------------------------------------------------------------
os.makedirs(f'../stats/{model_name}', exist_ok=True)
annotated_json_file = f'../stats/{model_name}/{set_name}_consolidated_output_annotations_{consolidation_type}_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.json'

with open(annotated_json_file, 'w', encoding='utf-8') as f:
    for entry in annotated:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# ------------------------------------------------------------
# Save stats
# ------------------------------------------------------------
stats_df = pd.DataFrame(
    [[correct, incorrect, translations_total]],
    columns=["correct", "incorrect", "total"]
)

stats_csv_file = f'../stats/{model_name}/{set_name}_consolidated_output_annotations_{consolidation_type}_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.csv'
stats_df.to_csv(stats_csv_file, index=False)
