# import sys
# sys.stdout.reconfigure(encoding='utf-8')

# import numpy as np
# from sklearn.metrics.pairwise import cosine_similarity
# import pickle, os, pandas
# from sentence_transformers import SentenceTransformer
# import json
# from collections import defaultdict

# sys.path.insert(1, '..')
# from stl2literal import STL2literal

# print('done importing')

# model_name = sys.argv[1]

# try:
#     with open(sys.argv[2], 'rb') as f:
#         translations = pickle.load(f)
#         print(f'Loaded {f}')
# except Exception as e:
#     print(e)
#     sys.exit(1)

# # Make sure model folder is available
# os.makedirs(f'../stats/{model_name}', exist_ok=True)

# # Load config
# with open(f'../config/{sys.argv[3]}') as f:
#     params = json.load(f)

# model = SentenceTransformer(params['embedding_model_name'], device='cpu')
# shot_count = params['num_shots_per_input_sentence']
# syntax_count = params['num_correction_attempts_per_shot']
# semantic_count = params['num_semantic_checks']
# time = sys.argv[4]
# set_name = params["set_name"]
# grammar = params['grammar']

# res_all = defaultdict(list)
# res_top = defaultdict(list)

# print("computing similarities")

# # ------------------------------------------------------------
# # Step 1: compute cosine similarities (unchanged logic)
# # ------------------------------------------------------------
# for sentence, stls in translations.items():
#     nl_embedding = np.array(
#         model.encode(sentence, normalize_embeddings=True)
#     )

#     syntactically_valid_translations = []

#     for entry in stls:
#         entry = entry.replace("∞", "inf")
#         literal = STL2literal(entry, grammar)
#         literal_embedding = np.array(
#             model.encode(literal, normalize_embeddings=True)
#         )

#         sim = cosine_similarity(
#             literal_embedding.reshape(1, -1),
#             nl_embedding.reshape(1, -1)
#         )[0][0]

#         syntactically_valid_translations.append((entry, sim))

#     res_all[sentence] = syntactically_valid_translations

# # ------------------------------------------------------------
# # Step 2: percentile-based filtering
# # ------------------------------------------------------------
# total_before = 0
# total_after = 0
# per_sentence_stats = []

# for sentence, stl_sims in res_all.items():
#     if len(stl_sims) == 0:
#         continue

#     sims = np.array([sim for _, sim in stl_sims])
#     mean_sim = float(np.mean(sims))

#     # Dynamic percentile rule
#     x = max(0.0, mean_sim - 0.5) * 20.0
#     percentile = max(0.0, 90.0 - x)

#     threshold = np.percentile(sims, percentile)

#     kept = [(stl, sim) for stl, sim in stl_sims if sim >= threshold]

#     res_top[sentence] = kept

#     total_before += len(stl_sims)
#     total_after += len(kept)

#     per_sentence_stats.append({
#         "input_sentence": sentence,
#         "mean_sim": mean_sim,
#         "percentile_used": percentile,
#         "threshold": threshold,
#         "before": len(stl_sims),
#         "after": len(kept)
#     })

# # ------------------------------------------------------------
# # Step 3: save stats + filtered results
# # ------------------------------------------------------------
# print(f"Total before filtering: {total_before}")
# print(f"Total after filtering:  {total_after}")
# print(f"Retention ratio:        {total_after / max(1, total_before):.3f}")

# stats_df = pandas.DataFrame(per_sentence_stats)
# stats_df.to_csv(
#     f'../stats/{model_name}/{set_name}_cosine_filter_stats_general_{time}.csv',
#     index=False
# )

# with open(
#     f'../pkl/{set_name}_cosine_filtered_general_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl',
#     'wb'
# ) as f:
#     pickle.dump(res_top, f)

# print("done")


# ---------------------------------------------
# Below supports filtering -> consolidation

import sys
sys.stdout.reconfigure(encoding='utf-8')

import os
import json
import pickle
import numpy as np
import pandas as pd
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

sys.path.insert(1, '..')
from stl2literal import STL2literal

print("done importing")

# ------------------------------------------------------------
# CLI args
# ------------------------------------------------------------
model_name = sys.argv[1]
translations_path = sys.argv[2]   # <-- pandas df pkl
config_name = sys.argv[3]
time = sys.argv[4]

# ------------------------------------------------------------
# Load translations (DataFrame)
# ------------------------------------------------------------
try:
    translations = pickle.load(open(translations_path, "rb"))
    print(f"Loaded translations DataFrame from {translations_path}")
except Exception as e:
    print(f"Failed to load translations: {e}")
    sys.exit(1)

# ------------------------------------------------------------
# Load config
# ------------------------------------------------------------
with open(f"../config/{config_name}") as f:
    params = json.load(f)

set_name = params["set_name"]
grammar = params["grammar"]
shot_count = params["num_shots_per_input_sentence"]
syntax_count = params["num_correction_attempts_per_shot"]
semantic_count = params["num_semantic_checks"]

# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
os.makedirs("../pkl", exist_ok=True)
os.makedirs(f"../stats/{model_name}", exist_ok=True)

filtered_pkl_path = (
    f"../pkl/{model_name}/{set_name}_filtered_output_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl"
)

stats_csv_path = (
    f"../stats/{model_name}/{set_name}_cosine_filter_stats_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.csv"
)

# ------------------------------------------------------------
# Load embedding model
# ------------------------------------------------------------
model = SentenceTransformer(
    params["embedding_model_name"],
    device="cpu"
)

res_all = defaultdict(list)
res_top = defaultdict(list)

print("computing similarities")

# ------------------------------------------------------------
# Step 1: compute similarities (DataFrame-aware)
# ------------------------------------------------------------
for _, row in translations.iterrows():
    sentence = row["input statement"]

    nl_embedding = np.array(
        model.encode(sentence, normalize_embeddings=True)
    )

    stl_candidates = []

    for i in range(shot_count):
        relevant_cols = [
            col for col in translations.columns
            if f"shot{i}-" in col
        ]

        for entry in row[relevant_cols]:
            if (
                entry is None or
                entry == "STL could not be extracted" or
                entry == "STL could not be parsed"
            ):
                continue

            entry = entry.replace("∞", "inf")
            stl_candidates.append(entry)

    # compute similarity for each candidate
    for entry in stl_candidates:
        literal = STL2literal(entry, grammar)
        literal_embedding = np.array(
            model.encode(literal, normalize_embeddings=True)
        )

        sim = cosine_similarity(
            literal_embedding.reshape(1, -1),
            nl_embedding.reshape(1, -1)
        )[0][0]

        res_all[sentence].append((entry, sim))

# ------------------------------------------------------------
# Step 2: percentile-based filtering
# ------------------------------------------------------------
total_before = 0
total_after = 0
per_sentence_stats = []

for sentence, stl_sims in res_all.items():
    if not stl_sims:
        continue

    sims = np.array([sim for _, sim in stl_sims])
    mean_sim = float(np.mean(sims))

    # x = max(0.0, mean_sim - 0.5) * 20.0
    percentile = 80.0 # max(0.0, 90.0 - x)

    threshold = np.percentile(sims, percentile)
    kept = [(stl, sim) for stl, sim in stl_sims if sim >= threshold]

    res_top[sentence] = kept

    total_before += len(stl_sims)
    total_after += len(kept)

    per_sentence_stats.append({
        "input_sentence": sentence,
        "mean_sim": mean_sim,
        "percentile_used": percentile,
        "threshold": threshold,
        "before": len(stl_sims),
        "after": len(kept),
    })

# ------------------------------------------------------------
# Step 3: save outputs
# ------------------------------------------------------------
print(f"Total before filtering: {total_before}")
print(f"Total after filtering:  {total_after}")
print(f"Retention ratio:        {total_after / max(1, total_before):.3f}")

pd.DataFrame(per_sentence_stats).to_csv(
    stats_csv_path,
    index=False
)

with open(filtered_pkl_path, "wb") as f:
    pickle.dump(res_top, f)

print(f"Wrote filtered pkl to {filtered_pkl_path}")
