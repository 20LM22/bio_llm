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
# prompt = """... Translate the following natural language statement into a signal temporal logic (STL) statement:
#             ... IL-12 reached its maximum level at the day>14 in mild patients. 
#             ...
#             ... It is extremely important to follow these rules:
#             ... Rule: The time unit is days.
#             ... Rule: Limit the produced STL statement to 10 operators and 5 predicates.
#             ... Rule: If you cannot find a translation that conforms to all rules, return “No translation found.”
#             ... Rule: Accept feedback on your previous responses and amend them if asked to.
#             ...
#             ... Your response must conform to these rules:
#             ... [BEGIN RULES]
#             ... u ::= s(t_a) < c | s(t_a) > c | "abs"(s(t_a) - c) < e | d_s(t_a) > d_c | d_s(t_a) < d_c | "abs"(d_s(t_a) - d_c) < e |
#             ... e ::= “e” | [0-9]+
#             ... c ::= s(t_a) | “c(low)” | “c(mid)” | “c(high)”
#             ... d_c ::= 0 | “d_c(low)” | “d_c(high)” | “-d_c(low)” | “-d_c(high)”
#             ... phi ::= u | phi ^ phi | phi → phi
#             ... psi ::= F[t_a,t_a] G phi | G[t_a,t_a] phi | F[t_a,t_a] phi
#             ... Phi ::= phi | psi | Phi ^ Phi | Phi → Phi
#             ... t_a ::= [0-9]+ | “t” | “T”
#             ... s ::= [a-zA-z0-9]+
#             ... d_s ::= d_[a-zA-z0-9]+
#             ... [END RULES]
#             ...
#             ... The d_s terms represent the derivative of a signal, so you may find those terms helpful for describing how signals increase or decrease. For general statements describing the levels of some species as “high” or “low” for example, you may find comparison statements helpful.
#             ...
#             ... Here are examples of natural language-signal temporal logic pairs:
#             ...
#             ... {input: "TNF-α levels elevated at the day 1–7 and 8–14 times intervals, then decreased at the day>14", output: "G[1,14] (tnf(t) < c(mid)) ^ G[15, T]  (d_tnf(t) < 0)"}
#             ... {input: "IL-12 reached its maximum level at the day>14 in mild patients.”, output: "F[15,T] ( l(t) > c(high)) ^ G[1,14] ( l(t) < c(high))"}
#             ..."""

# print("Prompting Ollama...")
# start = time.time()

# response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}], stream=False)

# print(response.message.content)

# print("*************************************************")
# print(f'Ollama responds in {time.time()-start} seconds')
# print("*************************************************")

# Parse the 
'''
json_parser = Lark(r
    u : s"("t_a") < "c
        | s"("t_a") > "c 
        | "abs("s"("t_a") - "c") < "e
        | d_s"("t_a") > "d_c
        | d_s"("t_a") < "d_c
        | "abs("d_s"("t_a") - "d_c") < "e
    e : "e"
        | /[0-9]+/
    c : "s("t_a")"
        | "c(low)"
        | "c(mid)"
        | "c(high)"
    d_c : "0" 
        | "d_c(low)"
        | "d_c(high)" 
        | "-d_c(low)" 
        | "-d_c(high)"
    phi : u
        | phi" ^ "phi
        | phi" → "phi
    psi : "F["t_a","t_a"]G("phi")"
        | "G["t_a","t_a"]("phi")"
        | "F["t_a","t_a"]("phi")"
    omega : phi
        | psi
        | omega" ^ "omega
        | omega" → "omega
    t_a : /[0-9]+/
        | "t"
        | "T"
    s : /[a-zA-z0-9]+/
    d_s : "d_"/[a-zA-z0-9]+/

    , start='omega')
'''

csvFile = pandas.read_csv('text_input.csv', header=None)
embedding_dict = defaultdict(dict)

# loop over all of the rows of the file
# for unique NL statements: first get their embedding, then get embedding of stl and literal, package into dict
# for already-seen NL statements: get embedding of stl and literal, package into dict

# uncomment this to generate

start = time.time()

for _id, row in csvFile.iterrows():
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

# this is always commented out
"""
    embedding_dict = {
        nl: {
            "embedding": embedding[row[0]]
            "stl": [ (row[0], embedding[row[0]]) ]
            "literal": [ (row[0], embedding[row[0]]) ]
        }
    }     
"""

# this is for opening file and printing contents
"""
nd = {}
try:
    with open('ollama_nomic.pkl', 'rb') as file:
       nd = pickle.load(file)
except Exception as e:
    print(e)

print(nd)
"""

# this is for writing to file
try:
    with open('ollama_nomic_v2.pkl', 'wb') as results:
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


