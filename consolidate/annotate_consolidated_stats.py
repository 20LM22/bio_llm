import pickle
import json
import sys
import csv
from sentence_groups import sentence_to_group  # make sure this is available

filtered_pkl = sys.argv[1]
consolidated_json = sys.argv[2]
output_csv = sys.argv[3] if len(sys.argv) > 3 else "stl_step_by_step_with_groups.csv"

# --- Load filtered pickle ---
with open(filtered_pkl, "rb") as f:
    filtered = pickle.load(f)

# --- Load consolidated JSON ---
consolidated = []
with open(consolidated_json, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            consolidated.append(json.loads(line))

# --- Write CSV ---
with open(output_csv, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(
        csvfile,
        fieldnames=["sentence", "group", "step", "stl_formula", "label"]
    )
    writer.writeheader()

    for entry in consolidated:
        sentence = entry["input_sentence"]
        group = sentence_to_group.get(sentence, "UNKNOWN")  # annotate group, default if missing

        # --- Filtered STLs ---
        filtered_entries = filtered.get(sentence, [])
        for stl_formula, *_ , label in filtered_entries:
            writer.writerow({
                "sentence": sentence,
                "group": group,
                "step": "filtered",
                "stl_formula": stl_formula,
                "label": label
            })

        # --- Consolidated STLs ---
        for stl in entry.get("stl", []):
            writer.writerow({
                "sentence": sentence,
                "group": group,
                "step": "consolidated",
                "stl_formula": stl["formula"],
                "label": stl["label"]
            })

print(f"CSV written to {output_csv}")



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