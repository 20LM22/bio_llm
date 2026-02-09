# import pickle
# import json
# import sys
# import csv
# import pandas as pd
# import numpy as np
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# from sentence_groups import sentence_to_group

# sys.stdout.reconfigure(encoding='utf-8')

# from sklearn.metrics.pairwise import cosine_similarity
# from sentence_transformers import SentenceTransformer

# sys.path.insert(1, '..')
# from stl2literal import STL2literal

# translations_pkl = sys.argv[1]
# filtered_pkl = sys.argv[2]
# consolidated_json = sys.argv[3]
# output_csv = sys.argv[4] if len(sys.argv) > 4 else "stl_step_by_step_with_groups.csv"

# with open(f"../config/config_nx_3_ny_1_nz_18_final_test_set.json") as f:
#     params = json.load(f)

# set_name = params["set_name"]
# grammar = params["grammar"]

# # ------------------------------------------------------------
# # Load raw translations DataFrame
# # ------------------------------------------------------------
# with open(translations_pkl, "rb") as f:
#     translations = pickle.load(f)

# # ------------------------------------------------------------
# # Load filtered pickle
# # ------------------------------------------------------------
# with open(filtered_pkl, "rb") as f:
#     filtered = pickle.load(f)

# # ------------------------------------------------------------
# # Load consolidated JSON
# # ------------------------------------------------------------
# consolidated = []
# with open(consolidated_json, "r", encoding="utf-8") as f:
#     for line in f:
#         line = line.strip()
#         if line:
#             consolidated.append(json.loads(line))

# # ------------------------------------------------------------
# # Extract raw STL candidates per sentence
# # ------------------------------------------------------------
# raw_stl = {}

# for _, row in translations.iterrows():
#     sentence = row["input statement"]
#     stls = []

#     for col in translations.columns:
#         if "shot" not in col:
#             continue

#         entry = row[col]
#         if entry in (
#             None,
#             "STL could not be extracted",
#             "STL could not be parsed"
#         ):
#             continue

#         entry = entry.replace("∞", "inf")
#         stls.append(entry)

#     raw_stl[sentence] = stls

# # ------------------------------------------------------------
# # Load embedding model
# # ------------------------------------------------------------
# model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")  # or use your param
# print("Loaded embedding model")

# # ------------------------------------------------------------
# # Write CSV with cosine similarity
# # ------------------------------------------------------------
# with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
#     writer = csv.DictWriter(
#         csvfile,
#         fieldnames=["sentence", "group", "step", "stl_formula", "label", "cosine_sim"]
#     )
#     writer.writeheader()

#     for entry in consolidated:
#         sentence = entry["input_sentence"]
#         group = sentence_to_group.get(sentence, "UNKNOWN")

#         # Compute sentence embedding once
#         nl_embedding = model.encode(sentence, normalize_embeddings=True)

#         # ---------- RAW ----------
#         for stl in raw_stl.get(sentence, []):
#             literal = STL2literal(stl, grammar)  # pass grammar if you have it
#             literal_embedding = model.encode(literal, normalize_embeddings=True)
#             sim = float(cosine_similarity(
#                 literal_embedding.reshape(1, -1),
#                 nl_embedding.reshape(1, -1)
#             )[0][0])

#             writer.writerow({
#                 "sentence": sentence,
#                 "group": group,
#                 "step": "raw",
#                 "stl_formula": stl,
#                 "label": "",
#                 "cosine_sim": f"{sim:.6f}"
#             })

#         # ---------- FILTERED ----------
#         for stl_formula, *_, label in filtered.get(sentence, []):
#             literal = STL2literal(stl_formula, grammar)
#             literal_embedding = model.encode(literal, normalize_embeddings=True)
#             sim = float(cosine_similarity(
#                 literal_embedding.reshape(1, -1),
#                 nl_embedding.reshape(1, -1)
#             )[0][0])

#             writer.writerow({
#                 "sentence": sentence,
#                 "group": group,
#                 "step": "filtered",
#                 "stl_formula": stl_formula,
#                 "label": label,
#                 "cosine_sim": f"{sim:.6f}"
#             })

#         # ---------- CONSOLIDATED ----------
#         for stl in entry.get("stl", []):
#             literal = STL2literal(stl["formula"], grammar)
#             literal_embedding = model.encode(literal, normalize_embeddings=True)
#             sim = float(cosine_similarity(
#                 literal_embedding.reshape(1, -1),
#                 nl_embedding.reshape(1, -1)
#             )[0][0])

#             writer.writerow({
#                 "sentence": sentence,
#                 "group": group,
#                 "step": "consolidated",
#                 "stl_formula": stl["formula"],
#                 "label": stl["label"],
#                 "cosine_sim": f"{sim:.6f}"
#             })

# print(f"CSV written to {output_csv}")





# ###########################################

# import json
# import sys
# from collections import defaultdict
# from sentence_groups import sentence_to_group

# sys.stdout.reconfigure(encoding='utf-8')

# # --------------------------------------------------
# # Load annotated JSON lines
# # --------------------------------------------------
# annotated = []
# with open(sys.argv[1], "r", encoding="utf-8") as f:
#     for line in f:
#         line = line.strip()
#         if not line:
#             continue
#         annotated.append(json.loads(line))

# # --------------------------------------------------
# # Accumulators
# # --------------------------------------------------
# sentence_counts = defaultdict(int)
# group_sentences_with_correct = defaultdict(int)
# total_sentences_with_correct = 0

# # --------------------------------------------------
# # Count sentences and check for at least one correct STL
# # --------------------------------------------------
# for entry in annotated:
#     sentence = entry["input_sentence"]
#     if sentence not in sentence_to_group:
#         continue

#     group = sentence_to_group[sentence]
#     sentence_counts[group] += 1

#     # Check if sentence has at least one semantically correct STL
#     stls = entry.get("stl", [])
#     sentence_has_correct = any(stl_entry.get("label", 0) == 1 for stl_entry in stls)

#     if sentence_has_correct:
#         group_sentences_with_correct[group] += 1
#         total_sentences_with_correct += 1

# # --------------------------------------------------
# # Print counts per group
# # --------------------------------------------------
# print("\n=== Sentence counts per group ===\n")
# for group in sorted(sentence_counts):
#     print(f"Group {group}: {sentence_counts[group]} sentences")

# # --------------------------------------------------
# # Print sentences with ≥1 correct STL
# # --------------------------------------------------
# print("\n=== Sentences with ≥1 semantically correct STL ===\n")
# print(f"Overall: {total_sentences_with_correct} sentences")

# for group in sorted(group_sentences_with_correct):
#     count = group_sentences_with_correct[group]
#     print(f"Group {group}: {count} sentences")


















# import json
# from collections import defaultdict
# from sentence_groups import sentence_to_group
# import sys

# sys.stdout.reconfigure(encoding='utf-8')

# annotated = []

# with open(sys.argv[1], "r", encoding="utf-8") as f:
#     for line in f:
#         line = line.strip()
#         if not line:
#             continue
#         annotated.append(json.loads(line))

# # --- Compute stats ---
# stats = defaultdict(lambda: defaultdict(int))

# for entry in annotated:
#     sentence = entry["input_sentence"]
#     if sentence not in sentence_to_group:
#         continue  # or raise an error
#     group = sentence_to_group[sentence]
#     for stl_entry in entry["stl"]:
#         label = stl_entry["label"]
#         stats[group][label] += 1

# # --- Print results ---
# for group in sorted(stats):
#     print(f"Group {group}:")
#     print(f"  label = 0 -> {stats[group].get(0,0)}")
#     print(f"  label = 1 -> {stats[group].get(1,0)}")