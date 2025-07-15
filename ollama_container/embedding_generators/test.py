import ollama, time
from ollama import ChatResponse
from ollama import chat
from lark import Lark
import numpy as np
import os
import pandas
from collections import defaultdict
import pickle

ollama.base_url = "http://localhost:11434"
model_name = "deepseek-r1:1.5b"
pkl_name = 'ollama_nomic_v2.pkl'

csv = '../csv_inputs/text_input_ambiguous_mod.csv' # specify csv input

csv_file = pandas.read_csv(csv, header=None)
embedding_dict = defaultdict(dict)

# loop over all of the rows of the file
# for unique NL statements: first get their embedding, then get embedding of stl and literal, package into dict
# for already-seen NL statements: get embedding of stl and literal, package into dict

start = time.time()

for _id, row in csv_file.iterrows():
    # obtain the nl statement
    nl = row[1]
    embedding_nl = np.array(ollama.embeddings(model='nomic-embed-text:latest', prompt=nl).embedding) if nl not in embedding_dict else embedding_dict[nl]['embedding']
        
    # attach embedding of stl and literal stl
    embedding_stl = np.array(ollama.embeddings(model='nomic-embed-text:latest', prompt=row[2]).embedding)
    embedding_literal = np.array(ollama.embeddings(model='nomic-embed-text:latest', prompt=row[3]).embedding)

    embedding_dict[nl]['embedding'] = embedding_nl
    if 'stl' in embedding_dict[nl]:
        embedding_dict[nl]['stl'].append((row[2], embedding_stl))
        embedding_dict[nl]['literal'].append((row[3], embedding_literal))
    else:
        embedding_dict[nl]['stl'] = [(row[2], embedding_stl)]
        embedding_dict[nl]['literal'] = [(row[3], embedding_literal)]

print("*************************************************")
print(f'Ollama responds in {time.time()-start} seconds')
print("*************************************************")

# writing to pkl
try:
    with open(f'../pkl/ambiguous_mod_{pkl_name}', 'wb') as results:
        pickle.dump(embedding_dict, results)
except Exception as e:
    print(e)



# print(arr_text_input)

# text = 'G[1,7](I(t) > c(high)) ^ F[7,T]G(I(t) < c(low))'
# # result = json_parser.parse(text)

# original_nl = "In the mild and moderate groups, IL-6 concentrations were at their highest level in the first week after the symptom onset and then exhibited a decreasing trend."

# stl = "G[1,7] (il6(t) > c(high)) ^ F[7,T] (d_il6(t) < 0)"

# translated_stl = "From days 1 to 7, the concentration of IL-6 was high and at some point from day 7 onwards, the concentration of IL-6 was decreasing."

# embedding_original = numpy.array(ollama.embeddings(model='nomic-embed-text:latest', prompt=original_nl).embedding)
# embedding_translation = numpy.array(ollama.embeddings(model='nomic-embed-text:latest', prompt=translated_stl).embedding)
# embedding_stl = numpy.array(ollama.embeddings(model='nomic-embed-text:latest', prompt=stl).embedding)

# print("********************************************")
# print(f"embedding_origin")
# print("*******************************************")

# sim_original_translated = (embedding_original @ embedding_translation) / (numpy.linalg.norm(embedding_original) * numpy.linalg.norm(embedding_translation))
# sim_original_stl = (embedding_original @ embedding_stl) / (numpy.linalg.norm(embedding_original) * numpy.linalg.norm(embedding_stl))
# print(f"Original-translated similarity: {sim_original_translated}")
# print(f"Original-STL similarity: {sim_original_stl}")


