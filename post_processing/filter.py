# Below supports filtering -> consolidation or consolidated -> filtering

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

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from stl2literal import STL2literal


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


def extract_candidate_formulas(raw_input):
    stl_by_sentence = defaultdict(list)

    if isinstance(raw_input, pd.DataFrame):
        relevant_cols = [col for col in raw_input.columns if col.startswith('shot')]
        for _, row in raw_input.iterrows():
            sentence = row['input statement']
            for entry in row[relevant_cols]:
                if (
                    entry is None or
                    entry == 'STL could not be extracted' or
                    entry == 'STL could not be parsed' or
                    pd.isna(entry)
                ):
                    continue
                stl_by_sentence[sentence].append(str(entry).replace('∞', 'inf'))
        return stl_by_sentence

    if isinstance(raw_input, dict):
        for sentence, entries in raw_input.items():
            if isinstance(entries, dict):
                entries = [entries]
            for entry in entries:
                stl = normalize_entry(entry)
                if stl is None:
                    continue
                stl_by_sentence[sentence].append(str(stl).replace('∞', 'inf'))
        return stl_by_sentence

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
                stl_by_sentence[sentence].append(str(stl).replace('∞', 'inf'))
        return stl_by_sentence

    raise ValueError('Unsupported input format for filtering')


model_name = sys.argv[1]
input_path = sys.argv[2]
config_name = sys.argv[3]
time = sys.argv[4]
filtered_pkl_path = sys.argv[5] if len(sys.argv) > 5 else None
stats_csv_path = sys.argv[6] if len(sys.argv) > 6 else None

try:
    raw_input = load_input(input_path)
    print(f"Loaded input from {input_path}")
except Exception as e:
    print(f"Failed to load input: {e}")
    sys.exit(1)

with open(f"./config/{config_name}") as f:
    params = json.load(f)

set_name = params['set_name']
grammar = params['grammar']
shot_count = params['num_shots_per_input_sentence']
syntax_count = params['num_correction_attempts_per_shot']
semantic_count = params['num_semantic_checks']

if filtered_pkl_path is None:
    filtered_pkl_path = (
        f"./pkl/{model_name}/{set_name}_filtered_output_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl"
    )

if stats_csv_path is None:
    stats_csv_path = (
        f"./stats/{model_name}/{set_name}_filtered_stats_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.csv"
    )

os.makedirs(os.path.dirname(filtered_pkl_path), exist_ok=True)
os.makedirs(os.path.dirname(stats_csv_path), exist_ok=True)

candidate_map = extract_candidate_formulas(raw_input)

model = SentenceTransformer(
    params['embedding_model_name'],
    device='cpu'
)

res_all = defaultdict(list)
res_top = defaultdict(list)

for sentence, stl_candidates in candidate_map.items():
    nl_embedding = np.array(model.encode(sentence, normalize_embeddings=True))
    for entry in stl_candidates:
        literal = STL2literal(entry, grammar)
        literal_embedding = np.array(model.encode(literal, normalize_embeddings=True))
        sim = cosine_similarity(
            literal_embedding.reshape(1, -1),
            nl_embedding.reshape(1, -1)
        )[0][0]
        res_all[sentence].append((entry, sim))

# ------------------------------------------------------------
# Percentile-based filtering
# ------------------------------------------------------------
total_before = 0
total_after = 0
per_sentence_stats = []

for sentence, stl_sims in res_all.items():
    if not stl_sims:
        continue

    sims = np.array([sim for _, sim in stl_sims])
    mean_sim = float(np.mean(sims))
    percentile = 80.0
    threshold = np.percentile(sims, percentile)
    kept = [(stl, sim) for stl, sim in stl_sims if sim >= threshold]
    res_top[sentence] = kept
    total_before += len(stl_sims)
    total_after += len(kept)

    per_sentence_stats.append({
        'input_sentence': sentence,
        'mean_sim': mean_sim,
        'percentile_used': percentile,
        'threshold': threshold,
        'before': len(stl_sims),
        'after': len(kept),
    })

# ------------------------------------------------------------
# Save outputs
# ------------------------------------------------------------
pd.DataFrame(per_sentence_stats).to_csv(
    stats_csv_path,
    index=False
)

with open(filtered_pkl_path, 'wb') as f:
    pickle.dump(res_top, f)
