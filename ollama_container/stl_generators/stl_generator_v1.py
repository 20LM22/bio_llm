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
        max_tokens=1024, # CAN CHANGE
        guided_decoding=guided_decoding_params)

# IMPORTANT: Evaluation parameters to set
model_dtype='half'
max_model_len=24000
gpu_memory_utilization=0.8
num_translations_per_input_sentence = 6
embedding_model_name = 'all-MiniLM-L6-v2'

# Input paths
model_names_csv = '../csv_inputs/stl_generation_model_names.csv'
sentences_csv = '../csv_inputs/stl_generation_sentences.csv'
core_prompt_csv = '../csv_inputs/stl_generation_core_prompt.csv'

# Load from input files
model_names = pandas.read_csv(model_names_csv, header=None)
sentences = pandas.read_csv(sentences_csv) # Make sure to include a header
core_prompt = pandas.read_csv(core_prompt_csv, header=None)

# Additional setup
parser = Lark(grammar)
embedding_model = SentenceTransformer(embedding_model_name, device='cpu')
grammar = """
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
    u_and_phi : u "^" phi
        
    ?psi : temp_op_fg | temp_op_g | temp_op_f
    
    temp_op_fg : "F" "[" t_a "," t_a "]" "G" "(" nu ")"
    temp_op_f : "F" "[" t_a "," t_a "]" "(" nu ")"
    temp_op_g : "G" "[" t_a "," t_a "]" "(" nu ")"
    
    ?omega : nu
        | psi
        | omega "^" omega
        
    t_a : /[0-9]+/
        | /T/
    s : /[a-zA-Z0-9]+/
    d_s : /d_[a-zA-Z0-9]+/

    %import common.WS
    %ignore WS
"""

for index, model_name in model_names.iterrows():
    # Create a file which contains all the relevant output related to this model
    # Augment the input file with correct number of stl and literal rows
    translations = sentences.copy()
    for i in range(num_translations_per_input_sentence):
        translations = translations.assign(f'STL-{i}': None, f'Literal-{i}': None)

    # Create the LLM for this model
    llm = LLM(model=model_name,
        dtype=model_dtype,
        max_model_len=max_model_len,
        gpu_memory_utilization=gpu_memory_utilization)

    # storage for output sentences
    final_sentences = []

    # do translations of each sentence
    for sentence_index, sentence in sentences['input sentence'].iterrows():
        prompt = core_prompt[0] + sentence + core_prompt[1]

        # accumulate syntactically valid responses
        syntactically_correct_responses = []

        # do num_translations_per_input_sentence-many translations for this one input sentence
        for i in range(num_translations_per_input_sentence):
            response = llm.chat([{"role": "user", "content": prompt}], sampling_params)[0].outputs[0].text
            
            # try to extract the STL statement, if unsuccessful, put a None into the translations dataframe entry
            try:
                output_dict = json.loads(response)
                extracted_response = output_dict["output_STL"]
                translations[sentence_index, f'STL-{i}'] = extracted_response
            except Exception as e:
                translations[sentence_index, f'STL-{i}'] = "STL could not be extracted"
                continue
            
            # try to parse the STL statement, if unsuccessful, put a None into the translations dataframe entry
            try:
                parsed_STL = parser.parse(extracted_response)
                syntactically_correct_responses.append(parsed_STL)
                translations[sentence_index, f'STL-{i}'] = parsed_STL
            except Exception as e:
                syntactically_correct_responses.append("STL could not be parsed")
                translations[sentence_index, f'STL-{i}'] = "STL could not be parsed"
                continue

        # at this point syntactically_correct_responses should be filled with responses and STL columns of 'translations' should also be full
        literal_translations = [] 
        for index, stl in enumerate(syntactically_correct_responses):
            if stl == "STL could not be parsed":
                translations[sentence_index, f'Literal-{i}'] = "Literal could not be generated"
            else:
                try:
                    literal_translation = STL2literal(stl, grammar)
                    translations[sentence_index, f'Literal-{i}'] = literal_translation
                    literal_translations.append(literal_translation)
                except Exception as e:
                    translations[sentence_index, f'Literal-{i}'] = "STL to literal translation failed"

        # these literal translations need to be evaluated for semantic integrity
        # obtain embeddings of the original sentence and all of the literal translations
        literal_embeddings = []
        nl_embedding = np.array(embedding_model.encode(sentence, normalize_embeddings=True))
        for i, literal in enumerate(literal_translations):
            embedding_literal = np.array(embedding_model.encode(literal_translations[i], normalize_embeddings=True))
            literal_embeddings.append(embedding_literal)
        
        # now compare the embeddings using cosine similarity, take max of the produced array
        if len(literal_embeddings) != 0:
            sim_matrix = cosine_similarity(np.array(literal_embeddings), np.array(nl_embedding))
            best_stl_id = np.argmax(sim_matrix)

            # only accept what is above similarity threshold
            # the final output is in the form [['nl', 'stl'],['nl', 'stl']]
            if sim_matrix[best_stl_id] >= 0.7: # semantic_threshold:
                final_sentences.append({sentence: syntactically_correct_rseponses[best_stl_id]})
        
    with open(f"final_sentences_{model_name}.txt", "w") as f:
        f.write(repr(final_sentences)) 

    # writing to pkl
    try:
        with open(f'../pkl/inputs_refs_translations_{model_name}', 'wb') as results:
            pickle.dump(translations, results)
    except Exception as e:
        print(e)

    # get embedding of everything in table so that similarities can be computed
    embeddings_translations = embedding_model.encode(translations.values.flatten().tolist(), normalize_embeddings=True)
    embeddings_translations = np.array(embeddings).reshape(translations.shape + (-1,))

    # writing to pkl
    try:
        with open(f'../pkl/inputs_refs_translations_embeddings_{model_name}', 'wb') as results:
            pickle.dump(embeddings_translations, results)
    except Exception as e:
        print(e)
    









