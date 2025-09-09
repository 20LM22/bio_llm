from vllm import LLM, SamplingParams
from lark import Lark
import numpy as np
import os
import pandas
from collections import defaultdict
import pickle
from sentence_transformers import SentenceTransformer
import re
from sklearn.metrics.pairwise import cosine_similarity
from stl2literal import STL2literal
import logging
from vllm.sampling_params import GuidedDecodingParams
from pydantic import BaseModel
import json
import csv
import sys
import traceback

# Set up the output formatting for STL generation
class STLResponse(BaseModel):
     thinking: str
     input_statement: str
     output_STL: str
     explanation: str
guided_decoding_params = GuidedDecodingParams(json=STLResponse.model_json_schema())
stl_response_json = STLResponse.model_json_schema()

# IMPORTANT: Evaluation parameters to set
sampling_params = SamplingParams(
        temperature=0.6, # CAN CHANGE
        top_p=0.95, # CAN CHANGE
        top_k=40, # CAN CHANGE
        min_p=0, # CAN CHANGE
        presence_penalty=1.5, # CAN CHANGE
        max_tokens=int(sys.argv[2]), # 1024, # CAN CHANGE
        guided_decoding=guided_decoding_params)

# IMPORTANT: Evaluation parameters to set
model_dtype='half'
max_model_len=int(sys.argv[3]) # 6000 # works well with deepseek 24000
gpu_memory_utilization=float(sys.argv[4]) # 0.8
num_translations_per_input_sentence = 3
embedding_model_name = 'all-MiniLM-L6-v2'

# Input paths
# model_names_csv = '../csv_inputs/stl_generation_model_names.csv'
sentences_csv = '../csv_inputs/validation_sentences.csv'

# Load from input files
model_name = sys.argv[1]
sentences = pandas.read_csv(sentences_csv) # Make sure to include a header

# Additional setup
embedding_model = SentenceTransformer(embedding_model_name, device='cpu')

grammar = r"""
    ?start: omega
    ?u : gt
        | lt
        | err_bnd
        | d_gt
        | d_lt
        | d_err_bnd
    gt : s "(t)" ">" c
    lt : s "(t)" "<" c 
    err_bnd : "abs(" s "(t)" "-" c ")" "<" e
    d_gt : "d_" s "(t)" ">" D_C
    d_lt : "d_" s "(t)" "<" D_C
    d_err_bnd : "abs(" "d_" s "(t)" "-" D_C ")" "<" e

    ?e : ERROR
        | /[0-9]+/
    ERROR : "e"
    
    c : s "(" t_a ")"
        | C_LOW
        | C_MID
        | C_HIGH
        
    C_LOW : "c(low)"
    C_MID : "c(mid)"
    C_HIGH : "c(high)"
    
    D_C : "0"
        | "d_c(low)"
        | "d_c(high)"
        | "-d_c(low)" 
        | "-d_c(high)"
        
    ?phi : u
        | u_and_phi
        
    ?nu : u | u_implies_u | u_and_phi
    
    u_implies_u : u "→" u | psi "→" psi | psi "→" u | u "→" psi
    u_and_phi : u "^" phi | u "∧" phi
        
    ?psi : temp_op_fg | temp_op_g | temp_op_f
    
    temp_op_fg : "F" "[" t_a "," t_a "]" "G" "(" nu ")"
    temp_op_f : "F" "[" t_a "," t_a "]" "(" nu ")"
    temp_op_g : "G" "[" t_a "," t_a "]" "(" nu ")"
    
    ?omega : nu
        | psi
        | omega "^" omega | omega "∧" omega
    t_a : /[0-9]+/
        | /T/
    s : /[\w]+/
    d_s : /d_[\w]+/

    %import common.WS
    %ignore WS
"""
parser = Lark(grammar)

core_prompt_1 = """Translate the following natural language statement into a signal temporal logic (STL) statement: """
core_prompt_2 = """          
            It is extremely important to follow these rules:
            Rule: The time unit is days.
            Rule: You must accept feedback on your previous responses and amend them if asked to.
            Rule: Format your response in JSON. Include your thinking, the input statement, your STL response, and an explanation of how the input statement and STL output are related.

            Your STL response must conform to these rules:
            [BEGIN RULES]
            u : s"(t) < "c | s"(t) > "c | "abs("s"(t) - "c") < "e | d_s"(t) > "d_c | d_s"(t) < "d_c | "abs("d_s"(t) - "d_c") < "e
            e : "e" | [0-9]+
            c : "s("t_a")" | "c(low)" | "c(mid)" | "c(high)"
            d_c : "0" | "d_c(low)" | "d_c(high)" | "-d_c(low)" | "-d_c(high)"
            phi : u | phi" ^ "phi | phi" → "phi
            psi : "F["t_a","t_a"]G("phi")" | "G["t_a","t_a"]("phi")" | "F["t_a","t_a"]("phi")"
            omega : phi | psi | omega" ^ "omega
            t_a : [0-9]+ | "T"
            s : [a-zA-z0-9]+
            d_s : "d_"[a-zA-z0-9]+
            [END RULES]
            
            The d_s terms represent the derivative of a signal, so you may find those terms helpful for describing how signals increase or decrease. For general statements describing the levels of some species as “high” or “low” for example, you may find comparison statements helpful.
            
            Here are 2 reference examples of natural language to STL translations, but don't copy them. Instead, make sure the STL statements you produce are specific to the input statement that you are currently being asked to translate:

            {example input: "From 4 to 8 days after infection, IL-6 levels were significantly elevated until day 9, at which point they steadily decreased.", output: "G[4,8] (IL6(t) > c(high)) ^ G[8,T] (d_IL6(t) < 0)"}
            {example input: "Once TNF levels stabilized at low levels, within 2 days the concentration of IL-12 became persistently higher compared to its original concentration.", output: "abs(TNF(t) - c(low)) < e → F[0,2]G( IL12(t) > IL12(0) )" }
"""

# Create a file which contains all the relevant output related to this model
# Augment the input file with correct number of stl and literal rows
translations = sentences.copy()

for i in range(num_translations_per_input_sentence):
    label1 = 'STL-'+ str(i)
    label2 = 'Literal-' + str(i)
    translations[label1] = None
    translations[label2] = None

print("-------------------------------------------------------------------------------------")
print(f'i is: {i}')
print(translations.columns.tolist())
print("-------------------------------------------------------------------------------------")

# Create the LLM for this model
llm = LLM(model=model_name,
    dtype=model_dtype,
    max_model_len=max_model_len,
    gpu_memory_utilization=gpu_memory_utilization)

# storage for output sentences
final_sentences = []

# do translations of each sentence
for sentence_index, sentence in sentences['input statement'].items():
    prompt = core_prompt_1 + sentence + core_prompt_2

    # accumulate syntactically valid responses
    syntactically_correct_responses = []

    # do num_translations_per_input_sentence-many translations for this one input sentence
    for i in range(num_translations_per_input_sentence):
        response = llm.chat([{"role": "user", "content": prompt}], sampling_params)[0].outputs[0].text

#        print(f"input: {sentence}")
#        print(f"output: {response}\n")

        # try to extract the STL statement, if unsuccessful, put a None into the translations dataframe entry
        try:
            output_dict = json.loads(response)
 #           print("output_dict success")
 #           print(output_dict)
            extracted_response = output_dict["output_STL"]
            label1 = 'STL-'+ str(i)
            translations.at[sentence_index, label1] = extracted_response
        except Exception as e:
            label1 = 'STL-'+ str(i)
            translations.at[sentence_index, label1] = "STL could not be extracted"
            continue
            
        # try to parse the STL statement, if unsuccessful, put a None into the translations dataframe entry
        try:
            parsed_STL = parser.parse(extracted_response) # not used in stl2literal but to check syntax
            syntactically_correct_responses.append((extracted_response, sentence_index, i))
            label1 = 'STL-'+ str(i)
            translations.at[sentence_index, label1] = extracted_response
        except Exception as e:
            label1 = 'STL-'+ str(i)
  #          print("HEREEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE")
  #          print(sentence_index)
  #          print(label1)
  #          print(translations.at[sentence_index, label1])
            if translations.at[sentence_index, label1] != 'STL could not be extracted':
                translations.at[sentence_index, label1] = "STL could not be parsed"
            syntactically_correct_responses.append(("STL could not be parsed", sentence_index, i))
            continue

   #     print(translations.at[sentence_index, label1])

    # at this point syntactically_correct_responses should be filled with responses and STL columns of 'translations' should also be full
    literal_translations = [] 
    for index, stl in enumerate(syntactically_correct_responses):
        if stl[0] != 'STL could not be extracted' and stl[0] != 'STL could not be parsed':
            # compute i --> find column it came from
            try:
                label1 = 'Literal-'+ str(stl[2])
                literal_translation = STL2literal(stl[0], grammar)
                print('----------------------------------------------------------------------------------------------------------------')
                print(f'literal translation: {literal_translation}\n')
                print('----------------------------------------------------------------------------------------------------------------')

                translations.at[sentence_index, label1] = literal_translation
                literal_translations.append(literal_translation)
            except Exception as e:
                label1 = 'Literal-'+ str(stl[2])
                translations.at[sentence_index, label1] = "STL to literal failed"
                print("ENCOUNTERED STL TO LITERAL FAILURE")
                print(f'the stl is: {stl[0]}')
                print(f'the error message is: {e}')
                traceback.print_exc()
        else:
            label1 = 'Literal-'+ str(stl[2])
            translations.at[sentence_index, label1] = "Literal could not be generated"

    # these literal translations need to be evaluated for semantic integrity
    # obtain embeddings of the original sentence and all of the literal translations
    literal_embeddings = []
    nl_embedding = embedding_model.encode(sentence, normalize_embeddings=True)
    for i, literal in enumerate(literal_translations):
        embedding_literal = np.array(embedding_model.encode(literal_translations[i], normalize_embeddings=True))
        literal_embeddings.append(embedding_literal)
        
    # now compare the embeddings using cosine similarity, take max of the produced array
    if len(literal_embeddings) != 0:
        sim_matrix = cosine_similarity(np.array(literal_embeddings), np.array(nl_embedding).reshape(1,-1))
        best_stl_id = np.argmax(sim_matrix)

        best_stl = syntactically_correct_responses[best_stl_id][0]
        best_input_sentence_index = syntactically_correct_responses[best_stl_id][1]

        # only accept what is above similarity threshold
        # the final output is in the form [['nl', 'stl'],['nl', 'stl']]
        # if sim_matrix[best_stl_id] >= 0.7: # semantic_threshold:
        final_sentences.append({stl: best_stl, sentence_index: best_input_sentence_index})
    
model_name = model_name.split('/')[0]
try:
    with open(f"../pkl/final_sentence_{model_name}", "wb") as f:
        pickle.dump(final_sentences, f) # only one sentence though
except Exception as e:
    print(e)

# writing to pkl
try:
    with open(f'../pkl/inputs_refs_translations_{model_name}', 'wb') as results:
        pickle.dump(translations, results)
except Exception as e:
    print(e)

# get embedding of everything in table so that similarities can be computed
translations = translations.astype(str)
data = translations.values.flatten().tolist()
embeddings_translations = embedding_model.encode(data, normalize_embeddings=True)
embeddings_translations = np.array(embeddings_translations).reshape(translations.shape + (-1,))

# writing to pkl
try:
    with open(f'../pkl/inputs_refs_translations_embeddings_{model_name}', 'wb') as results:
        pickle.dump(embeddings_translations, results)
except Exception as e:
    print(e)
