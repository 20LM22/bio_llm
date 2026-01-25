import sys
sys.stdout.reconfigure(encoding='utf-8')

import pickle, os, pandas
from collections import defaultdict
import json

print("starting annotation")

model_name = sys.argv[1]
filtered_pkl = sys.argv[2]
config_file = sys.argv[3]
time = sys.argv[4]

# ------------------------------------------------------------
# Load filtered candidates
# ------------------------------------------------------------
try:
    with open(filtered_pkl, 'rb') as f:
        res = pickle.load(f)
        print(f"Loaded {filtered_pkl}")
except Exception as e:
    print(e)
    sys.exit(1)

# ------------------------------------------------------------
# Load config (for naming consistency)
# ------------------------------------------------------------
with open(f'../config/{config_file}') as f:
    params = json.load(f)

shot_count = params['num_shots_per_input_sentence']
syntax_count = params['num_correction_attempts_per_shot']
semantic_count = params['num_semantic_checks']
set_name = params["set_name"]

# ------------------------------------------------------------
# Manual annotation loop
# ------------------------------------------------------------
translations_total = sum(len(v) for v in res.values())
translations_count = 0

correct = 0
incorrect = 0

annotated = defaultdict(list)

for sentence, stl_sims in res.items():
    print("=" * 80)
    print(f"Sentence:\n{sentence}")

    for stl, sim in stl_sims:
        translations_count += 1
        print("-" * 80)
        print(f"{translations_count}/{translations_total}")
        print(f"Cosine similarity: {sim:.4f}")
        print("STL:")
        print(stl)

        choice = input("1 = correct, 0 = incorrect (ENTER = 0): ").strip()

        if choice == "1":
            label = 1
            correct += 1
        else:
            label = 0
            incorrect += 1

        annotated[sentence].append((stl, sim, label))

# ------------------------------------------------------------
# Save annotation stats
# ------------------------------------------------------------
os.makedirs(f'../stats/{model_name}', exist_ok=True)

stats_df = pandas.DataFrame(
    [[correct, incorrect, translations_total]],
    columns=["correct", "incorrect", "total"]
)

stats_df.to_csv(
    f'../stats/{model_name}/{set_name}_semantic_labels_AFTER_COSINE_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.csv',
    index=False
)