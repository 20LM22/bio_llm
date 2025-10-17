import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle, os, pandas, sys, json
from sentence_transformers import SentenceTransformer
import json, requests
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
from scipy.stats import spearmanr

sys.path.insert(1, '../..')
from stl2literal import STL2literal

model_name = sys.argv[1]

for i in range(0,4):
    print(f'{i}: {sys.argv[i]}')

try:
    with open(f'../../pkl/{model_name}/{sys.argv[2]}', 'rb') as f:
        translations = pickle.load(f)
        print(f'Loaded {f}')
except Exception as e:
    print(e)

# Make sure model folder is available
os.makedirs(f'../../stats/{model_name}', exist_ok=True)

# Load config specified by the script
with open(f'../../config/{sys.argv[3]}') as f:
    params = json.load(f)

model = SentenceTransformer(params['embedding_model_name'], device='cpu')
shot_count = params['num_shots_per_input_sentence']
syntax_count = params['num_correction_attempts_per_shot']
semantic_count = params['num_semantic_checks']
time = sys.argv[4]
set_name = params["set_name"]

grammar = params['grammar']

res = defaultdict(list)

ollama_url = "http://localhost:11434/api/embeddings"
ollama_model_2 = "nomic-embed-text"
ollama_model_3 = "qwen3-embedding:0.6b"

model_1 = []
model_2 = []
model_3 = []

for index, row in translations.iterrows():
    print(f"row['input statement']: {row['input statement']}")

    nl_embedding_1 = np.array(model.encode(row['input statement'], normalize_embeddings=True))

    nl_response_2 = requests.post(
        ollama_url,
        json={"model": ollama_model_2, "prompt": row['input statement']}
    )
    if nl_response_2.status_code != 200:
        raise RuntimeError(f"Ollama error: {nl_response_2.text}")
    nl_embedding_2 = nl_response_2.json()["embedding"]

    nl_response_3 = requests.post(
        ollama_url,
        json={"model": ollama_model_3, "prompt": row['input statement']}
    )
    if nl_response_3.status_code != 200:
        raise RuntimeError(f"Ollama error: {nl_response_3.text}")
    nl_embedding_3 = nl_response_3.json()["embedding"]

    row_subset = pandas.DataFrame()
    row_counter = 0

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
                # TODO: for each embedding model that i want to try, update it here
                literal_embedding_1 = ( np.array(model.encode(literal, normalize_embeddings=True)) )
                sim_1 = cosine_similarity(np.array(literal_embedding_1).reshape(1,-1), np.array(nl_embedding_1).reshape(1,-1))[0][0]
                model_1.append(sim_1)

                response_2 = requests.post(
                    ollama_url,
                    json={"model": ollama_model_2, "prompt": literal}
                )
                if response_2.status_code != 200:
                    raise RuntimeError(f"Ollama error: {response_2.text}")
                literal_embedding_2 = response_2.json()["embedding"]
                sim_2 = cosine_similarity(np.array(literal_embedding_2).reshape(1,-1), np.array(nl_embedding_2).reshape(1,-1))[0][0]
                model_2.append(sim_2)

                response_3 = requests.post(
                    ollama_url,
                    json={"model": ollama_model_3, "prompt": literal}
                )
                if response_3.status_code != 200:
                    raise RuntimeError(f"Ollama error: {response_3.text}")
                literal_embedding_3 = response_3.json()["embedding"]
                sim_3 = cosine_similarity(np.array(literal_embedding_3).reshape(1,-1), np.array(nl_embedding_3).reshape(1,-1))[0][0]
                model_3.append(sim_3)

from scipy.stats import spearmanr
import pandas as pd

# Compute correlation and p-values
r_12, p_12 = spearmanr(model_1, model_2)
r_13, p_13 = spearmanr(model_1, model_3)
r_23, p_23 = spearmanr(model_2, model_3)

# Correlation matrix (r-values)
r_df = pd.DataFrame(
    data=[
        [1.0, r_12, r_13],
        [r_12, 1.0, r_23],
        [r_13, r_23, 1.0]
    ],
    columns=["Sentence Embeddings", "Nomic-Embed-Text", "Qwen Embeddings"],
    index=["Sentence Embeddings", "Nomic-Embed-Text", "Qwen Embeddings"]
)

# P-value matrix
p_df = pd.DataFrame(
    data=[
        [0.0, p_12, p_13],
        [p_12, 0.0, p_23],
        [p_13, p_23, 0.0]
    ],
    columns=["Sentence Embeddings", "Nomic-Embed-Text", "Qwen Embeddings"],
    index=["Sentence Embeddings", "Nomic-Embed-Text", "Qwen Embeddings"]
)

# Save both to CSV
r_df.to_csv(f"../../stats/{model_name}/{set_name}_embedding_rvalues_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.csv", float_format="%.4f")
p_df.to_csv(f"../../stats/{model_name}/{set_name}_embedding_pvalues_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.csv", float_format="%.4g")
