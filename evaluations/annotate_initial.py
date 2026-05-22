import sys
sys.stdout.reconfigure(encoding='utf-8')

import os, json, pickle
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from stl2literal import STL2literal

model_name = sys.argv[1]
translations_pkl = sys.argv[2]
config_file = sys.argv[3]
time = sys.argv[4]

try:
    with open(f'../pkl/{model_name}/{translations_pkl}', 'rb') as f:
        translations = pickle.load(f)
        print(f'Loaded {f}')
except Exception as e:
    print(e)

with open(f'../config/{config_file}') as f:
    params = json.load(f)

shot_count = params['num_shots_per_input_sentence']
syntax_count = params['num_correction_attempts_per_shot']
semantic_count = params['num_semantic_checks']
set_name = params["set_name"]
grammar = params["grammar"]

model = SentenceTransformer(
    params['embedding_model_name'],
    device='cpu'
)

# ------------------------------------------------------------
# Prepare translations for annotation (sentence → [(stl, similarity)])
# ------------------------------------------------------------
res = defaultdict(list)

for _, row in translations.iterrows():
    sentence = row['input statement']
    nl_emb = np.array(
        model.encode(sentence, normalize_embeddings=True)
    )

    syntactically_valid = []

    for i in range(shot_count):
        shot_cols = [c for c in translations.columns if f'shot{i}-' in c]

        for col in shot_cols:
            entry = row[col]

            if entry in (
                None,
                'STL could not be extracted',
                'STL could not be parsed'
            ):
                continue

            try:
                entry = entry.replace("∞", "inf")
                literal = STL2literal(entry, grammar)

                lit_emb = np.array(
                    model.encode(literal, normalize_embeddings=True)
                )

                sim = cosine_similarity(
                    lit_emb.reshape(1, -1),
                    nl_emb.reshape(1, -1)
                )[0][0]

                syntactically_valid.append((entry, sim))

            except Exception:
                continue

    res[sentence] = syntactically_valid

# ------------------------------------------------------------
# Annotate initial translations
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
# Save stats
# ------------------------------------------------------------
os.makedirs(f'../stats/{model_name}', exist_ok=True)

stats_df = pd.DataFrame(
    [[correct, incorrect, translations_total]],
    columns=["correct", "incorrect", "total"]
)

stats_df.to_csv(
    f'../stats/{model_name}/{set_name}_initial_output_annotations_'
    f'nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.csv',
    index=False
)

# ------------------------------------------------------------
# Save annotations
# ------------------------------------------------------------
with open(
    f'../pkl/{model_name}/{set_name}_initial_output_annotations_'
    f'nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl',
    'wb'
) as f:
    pickle.dump(annotated, f)