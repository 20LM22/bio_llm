import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle, sys, os, pandas
from sentence_transformers import SentenceTransformer
import json
from collections import defaultdict

sys.path.insert(1, '..')
from stl2literal import STL2literal

model_name = sys.argv[1]

try:
    with open(f'../pkl/{model_name}/{sys.argv[2]}', 'rb') as f:
        translations = pickle.load(f)
        print(f'Loaded {f}')
except Exception as e:
    print(e)

# Make sure model folder is available
os.makedirs(f'../stats/{model_name}', exist_ok=True)

# Load config specified by the script
with open(f'../config/{sys.argv[3]}') as f:
    params = json.load(f)

embedding_model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(params['embedding_model_name'], device='cpu')
shot_count = params['num_shots_per_input_sentence']
syntax_count = params['num_correction_attempts_per_shot']
semantic_count = params['num_semantic_checks']

grammar = params['grammar']

#######################################################################################################################
# Table for extraction, parsing success rate
#######################################################################################################################

res = defaultdict(list)

# fill in semantic successes
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
                literal = STL2literal(entry, grammar)
                literal_embedding = ( np.array(model.encode(literal, normalize_embeddings=True)) )
                sim = cosine_similarity(np.array(literal_embedding).reshape(1,-1), np.array(nl_embedding).reshape(1,-1))[0][0]
                # need to record stl and its similarity
                syntactically_valid_translations.append((entry, sim))

    res[row['input statement']] = syntactically_valid_translations

for key in res.keys():
    print(key)
    print()
print(len(res.keys()))
print()

# TODO: comment this back in when you need to do the annotations
# top_sentences = [
#     "Following day 10, IL-6 remains increased whereas IFN-α tapered.",
#     "In line with previous reports, IL-1β levels were mostly low or at the limit of detection of 0.1pg ml−1, even though the assay was able to detect various levels of recombinant control cytokines (Extended Data Fig. 1b).",
#     "We also found that IL-1 receptor antagonist (IL-1RA) levels were elevated in both severe and mild cases and remained at a high level during the 4 weeks of follow-up."
# ]
# bottom_sentences = [
#     "Significantly higher levels of MCP-1 in severe cases were observed when compared with mild cases at early an time point of the infection (week 1 and 2; P = 0.047 and 8.62 × 10–5, respectively) but not at later time points (week 3 and 4; P = 0.136 and 0.030, respectively, Supplemental Table 1 and Figure 2).",
#     "This is the reason that seroconversion (undetectable stage to production of IgM followed by IgG) in 100% of infected people (with positive virus-specific IgG) is achieved 17–19 days after commencement of indications [7].",
#     "Monocyte chemotactic factor chemokine(C-C motif) ligand 2 (CCL2) was increased in the blood of infected patients as well as the transcripts of its receptor CCR2; this was associated with low counts of circulating inflammatory monocytes (Fig. 4I), suggesting a rolefor the CCL2/CCR2 axis in the monocyte chemo-attraction into the inflamed lungs."
# ]

# uncomment for qwen
# top_sentences = [
#     "Following day 10, IL-6 remains increased whereas IFN-α tapered.",
#     "In line with previous reports, IL-1β levels were mostly low or at the limit of detection of 0.1pg ml−1, even though the assay was able to detect various levels of recombinant control cytokines (Extended Data Fig. 1b).",
#     "Circulating IL-1α also was not detected (fig. S9F)."]
# bottom_sentences = [
#     "Two days postinfection, permissive Vero cells produced high peak titers of 5 x 10^6 TCID_50s/ml and 1 x 10^7 TCID_50s/ml of MERS- and SARS-CoV, respectively (Fig. 1B, panel i)",
#     "This is the reason that seroconversion (undetectable stage to production of IgM followed by IgG) in 100% of infected people (with positive virus-specific IgG) is achieved 17–19 days after commencement of indications [7].",
#     "Monocyte chemotactic factor chemokine(C-C motif) ligand 2 (CCL2) was increased in the blood of infected patients as well as the transcripts of its receptor CCR2; this was associated with low counts of circulating inflammatory monocytes (Fig. 4I), suggesting a rolefor the CCL2/CCR2 axis in the monocyte chemo-attraction into the inflamed lungs."]

# from res remove keys that aren't in top or bottom
# res_top = defaultdict(list)
# res_bottom = defaultdict(list)
# for key in res.keys():
#     for s in top_sentences:
#         if s[:15] == key[:15]:
#             res_top[key] = res[key]
#     for s in bottom_sentences:
#         if s[:15] == key[:15]:
#             res_bottom[key] = res[key]
#
# for key in res_top.keys():
#     print(key)
#     print(len(res_top[key]))
#     print()
# print(len(res_top.keys()))
#
# for key in res_bottom.keys():
#     print(key)
#     print(len(res_bottom[key]))
#     print()
# print(len(res_bottom.keys()))
#
# # print these out to the user and have them mark whether they think they're good or not
# translations_total = 0
# for key in res_top.keys():
#     translations_total += len(res_top[key])
# for key in res_bottom.keys():
#     translations_total += len(res_bottom[key])
#
# translations_count = 0
#
# for key in res_top.keys():
#     new_syn_valid_arr = []
#     for stl, sim in res_top[key]:
#         print(f"{translations_count}/{translations_total} annotations completed.")
#         translations_count += 1
#         # need to ask the user to mark the annotation as a 0 or 1
#         print(f"Sentence: {key}")
#         print(f"STL: {stl}")
#         choice = input("1 for yes, 0 for no: ")
#         # then need to construct a new array that we will replace the current one in the dictionary with
#         # but this array will have the user's annotation
#         new_syn_valid_arr.append((stl,sim,choice))
#     res_top[key] = new_syn_valid_arr
#
# for key in res_bottom.keys():
#     new_syn_valid_arr = []
#     for stl, sim in res_bottom[key]:
#         print(f"{translations_count}/{translations_total} annotations completed.")
#         translations_count += 1
#         # need to ask the user to mark the annotation as a 0 or 1
#         print(f"Sentence: {key}")
#         print(f"STL: {stl}")
#         choice = input("1 for yes, 0 for no: ")
#         # then need to construct a new array that we will replace the current one in the dictionary with
#         # but this array will have the user's annotation
#         new_syn_valid_arr.append((stl,sim,choice))
#     res_bottom[key] = new_syn_valid_arr

try:
    with open(f'../pkl/qd_redo_all_test_set_histogram_distribution_comparison_{model_name}_shots_{shot_count}_syntax_{syntax_count}_semantic_{semantic_count}.pkl', 'wb') as r:
        pickle.dump(res, r)
except Exception as e:
    print("there was a pickle problem")
    print(e)

# try:
#     with open(f'../pkl/qd_redo_top_3_test_set_histogram_distribution_comparison_{model_name}_shots_{shot_count}_syntax_{syntax_count}_semantic_{semantic_count}.pkl', 'wb') as r:
#         pickle.dump(res_top, r)
#     with open(f'../pkl/qd_redo_bottom_3_test_set_histogram_distribution_comparison_{model_name}_shots_{shot_count}_syntax_{syntax_count}_semantic_{semantic_count}.pkl', 'wb') as r:
#         pickle.dump(res_bottom, r)
# except Exception as e:
#     print("there was a pickle problem")
#     print(e)