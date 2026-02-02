import pickle
import sys
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

sys.stdout.reconfigure(encoding="utf-8")

# --------------------------------------------------
# Load annotated pickle
# --------------------------------------------------
with open(sys.argv[1], "rb") as f:
    annotated = pickle.load(f)

# --------------------------------------------------
# sentence_to_group (ORDER MATTERS — dict preserves order)
# --------------------------------------------------
from sentence_groups import sentence_to_group

# --------------------------------------------------
# Load embedding model
# --------------------------------------------------
model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

# --------------------------------------------------
# Iterate sentences IN GIVEN ORDER
# --------------------------------------------------
# print("\n=== Sentences and their STL translations (in fixed order) ===\n")
print("\n=== Sentences with NO STL translations ===\n")

for sentence in sentence_to_group:
    if sentence not in annotated or not annotated[sentence]:
        print(f"[NO STL] Group {sentence_to_group[sentence]}")
        print(sentence)
        print()

# for sentence, group in sentence_to_group.items():

#     print("=" * 100)
#     print(f"SENTENCE (Group {group}):")
#     print(sentence)
#     print("-" * 100)

#     # If sentence has no annotations, print blank section
#     if sentence not in annotated or not annotated[sentence]:
#         print("(no STL translations)\n")
#         continue

#     # Embed sentence once
#     sent_emb = np.array(model.encode(sentence, normalize_embeddings=True))

#     # Print all STL translations
#     for idx, entry in enumerate(annotated[sentence], 1):
#         # assuming structure: (stl, ..., label)
#         stl = entry[0]
#         label = entry[-1]

#         stl_emb = np.array(model.encode(stl, normalize_embeddings=True))

#         sim = cosine_similarity(
#             stl_emb.reshape(1, -1),
#             sent_emb.reshape(1, -1)
#         )[0][0]

#         print(f"[STL {idx}]")
#         print(f"Label: {label}")
#         print(f"Cosine similarity: {sim:.4f}")
#         print(stl)
#         print()

#     print()  # extra spacing between sentences


# import pickle
# import sys
# import numpy as np
# from collections import defaultdict
# from sentence_groups import sentence_to_group
# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity

# sys.stdout.reconfigure(encoding="utf-8")

# # --------------------------------------------------
# # Load annotated pickle
# # --------------------------------------------------
# with open(sys.argv[1], "rb") as f:
#     annotated = pickle.load(f)

# # --------------------------------------------------
# # Load embedding model
# # --------------------------------------------------
# model = SentenceTransformer("all-MiniLM-L6-v2", device="cpu")

# # --------------------------------------------------
# # Accumulators
# # --------------------------------------------------
# group_sims = defaultdict(list)
# all_sims = []

# # Track sentences with at least one correct STL (label == 1)
# group_sentences_with_correct = defaultdict(int)
# total_sentences_with_correct = 0

# # --------------------------------------------------
# # Compute similarities and collect semantic pass info
# # --------------------------------------------------
# for sentence, entries in annotated.items():
#     if sentence not in sentence_to_group:
#         continue

#     group = sentence_to_group[sentence]

#     # Embed parent sentence once
#     sent_emb = np.array(model.encode(sentence, normalize_embeddings=True))

#     sentence_has_correct = False

#     for stl, *_ , label in entries:  # assuming last element is label
#         # Embed STL
#         stl_emb = np.array(model.encode(stl, normalize_embeddings=True))

#         # Cosine similarity
#         sim = cosine_similarity(
#             stl_emb.reshape(1, -1),
#             sent_emb.reshape(1, -1)
#         )[0][0]

#         group_sims[group].append(sim)
#         all_sims.append(sim)

#         # Check label
#         if label == 1:
#             sentence_has_correct = True

#     if sentence_has_correct:
#         group_sentences_with_correct[group] += 1
#         total_sentences_with_correct += 1

# # --------------------------------------------------
# # Print cosine similarity averages
# # --------------------------------------------------
# print("\n=== Group averages ===\n")
# for group in sorted(group_sims):
#     sims = group_sims[group]
#     avg_sim = float(np.mean(sims)) if sims else 0.0
#     print(
#         f"Group {group}: "
#         f"avg cosine similarity = {avg_sim:.4f} "
#         f"(n_stl={len(sims)})"
#     )

# print("\n=== Overall average ===\n")
# overall_avg = float(np.mean(all_sims)) if all_sims else 0.0
# print(
#     f"Overall avg cosine similarity = {overall_avg:.4f} "
#     f"(n_stl={len(all_sims)})"
# )

# # --------------------------------------------------
# # Print sentences with ≥1 correct STL
# # --------------------------------------------------
# print("\n=== Sentences with ≥1 semantically correct STL ===\n")
# print(f"Overall: {total_sentences_with_correct} sentences")

# for group in sorted(group_sentences_with_correct):
#     count = group_sentences_with_correct[group]
#     print(f"Group {group}: {count} sentences")


# import pickle
# from collections import defaultdict
# import sys
# from sentence_groups import sentence_to_group

# sys.stdout.reconfigure(encoding="utf-8")

# # --- Open pickle in binary mode ---
# with open(sys.argv[1], "rb") as f:
#     annotated = pickle.load(f)

# sentence_counts = defaultdict(int)

# for sentence in annotated:
#     if sentence not in sentence_to_group:
#         continue
#     group = sentence_to_group[sentence]
#     sentence_counts[group] += 1

# for group in sorted(sentence_counts):
#     print(f"Group {group}: {sentence_counts[group]} sentences")

# # import pickle
# # from collections import defaultdict
# # import sys
# # from sentence_groups import sentence_to_group

# # sys.stdout.reconfigure(encoding="utf-8")

# # # --- Open pickle in binary mode ---
# # with open(sys.argv[1], "rb") as f:
# #     annotated = pickle.load(f)

# # --- Compute statistics ---
# stats = defaultdict(lambda: defaultdict(int))

# for sentence, entries in annotated.items():
#     if sentence not in sentence_to_group:
#         continue

#     group = sentence_to_group[sentence]
#     print(f"{group}")

#     for _, _, label in entries:
#         stats[group][label] += 1

# # --- Print results ---
# for group in sorted(stats):
#     print(f"Group {group}:")
#     print(f"  label = 0 -> {stats[group].get(0, 0)}")
#     print(f"  label = 1 -> {stats[group].get(1, 0)}")
