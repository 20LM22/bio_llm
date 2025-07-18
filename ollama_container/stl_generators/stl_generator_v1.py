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
        temperature=0.6, # was 0.4 with deepseek
        top_p=0.95,
        top_k=40,
        min_p=0,
        presence_penalty=1.5,
        max_tokens=1024, # 2048, # 32768,
        guided_decoding=guided_decoding_params)

# IMPORTANT: Evaluation parameters to set
model_dtype='half'
max_model_len=24000
gpu_memory_utilization=0.8
num_translations_per_input_sentence = 6

# Input paths
model_names_csv = '../csv_inputs/stl_generation_model_names.csv'
inputs_and_refs_csv = '../csv_inputs/stl_generation_inputs_and_refs.csv'
core_prompt_csv = '../csv_inputs/stl_generation_core_prompt.csv'

# Load large text sections in from csv files
model_names = pandas.read_csv(model_names_csv, header=None)
inputs_and_refs = pandas.read_csv(inputs_and_refs_csv) # Make sure to include a header

for index, model_name in model_names.iterrows():
    # Create a file which contains all the relevant output related to this model
    # Augment the input file with correct number of stl and literal rows
    for i in range(num_translations_per_input_sentence):
        translations = inputs_and_refs.assign(f'STL-{i}': None, f'Literal-{i}': None)

    # Create the LLM for this model
    llm = LLM(model=model_name,
        dtype=model_dtype,
        max_model_len=max_model_len,
        gpu_memory_utilization=gpu_memory_utilization)

core_prompt_1 = """Translate the following natural language statement into a signal temporal logic (STL) statement: """
core_prompt_2 = """          
            It is extremely important to follow these rules:
            Rule: The time unit is days.
            Rule: You must accept feedback on your previous responses and amend them if asked to.
            Rule: Format your response in JSON. Include your thinking, the input statement, your STL response, and an explanation of how the input statement and STL output are relatedi.

            Your STL response must conform to these rules:
            [BEGIN RULES]
            u : s(t) < c | s(t) > c | abs(s(t) - c) < e | d_s(t) > d_c | d_s(t) < d_c | abs(d_s(t) - d_c) < e
            e : "e" | [0-9]+
            c : s(t_a) | "c(low)" | "c(mid)" | "c(high)"
            d_c : 0 | "d_c(low)" | "d_c(high)" | "-d_c(low)" | "-d_c(high)"
            phi : u | u ^ phi
            psi : F[t_a,t_a]G(nu) | G[t_a,t_a](nu) | F[t_a,t_a](nu)
            nu : u | u ^ phi | u → u | psi → psi | psi → u | u → psi
            omega : nu | psi | omega ^ omega
            t_a : [0-9]+ | "T"
            s : [a-zA-z0-9]+
            d_s : "d_"[a-zA-z0-9]+
            [END RULES]
            
            The d_s terms represent the derivative of a signal, so you may find those terms helpful for describing how signals increase or decrease. For general statements describing the levels of some species as “high” or “low” for example, you may find comparison statements helpful.
            
            Here are 2 reference examples of natural language to STL translations, but don't copy them. Instead, make sure the STL statements you produce are specific to the input statement that you are currently being asked to translate:

            {example input: "From 4 to 8 days after infection, IL-6 levels were significantly elevated until day 9, at which point they steadily decreased.", output: "G[4,8] (IL6(t) > c(high)) ^ G[8,T] (d_IL6(t) < 0)"}
            {example input: "Once TNF levels stabilized at low levels, within 2 days the concentration of IL-12 became persistently higher compared to its original concentration.", output: "abs(TNF(t) - c(low)) < e → F[0,2]G( IL12(t) > IL12(0) )" }
"""

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

logging.basicConfig(
    filename="bio_logs_qwen",
    encoding="utf-8",
    level=logging.INFO,
    filemode="a"
)

parser = Lark(grammar)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')

output_translations = [[[ "" for _ in range(6)] for _ in range(len(sentences))] for _ in range(3)]
# array_3d[z][y][x] = depth z, row y, column x
final_sentences = [ "" for _ in range(len(sentences))]

for k, sentence in enumerate(sentences):
    print(f"sentence: {sentence}")
    # change the prompt for each sentence
    prompt = core_prompt_1 + sentence + core_prompt_2
    # print(f"the prompt is: {prompt}")
    # allow each sentence to be translated up n times to get the semantic meaning correct --> n = num_semantic_attempts
    for i in range(num_semantic_attempts):
        # this scope works at the sentence level
        syntactically_correct_responses = []
        # need to produce m translations to STL --> m = num_batch
        for j in range(num_batch):  
            # for now, let's just use the original prompt without syntactic modification based on the previous responses
            # print("about to generate a response") # messages=[{"role": "user", "content": prompt}]
            # print("generating response")
            # response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}], stream=False).message.content
            response = llm.chat([{"role": "user", "content": prompt}], sampling_params) # [0].outputs[0].text
            print(f"response is: {response[0].outputs[0].text}")
            # print(f"type of response: {type(response)}")
            """
            completion = client.chat.completions.create(
                model=model,
                prompt=prompt,
                temperature=0.6,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": stl_response_json
                }
            )
            print("reasoning_content: ", completion.choices[0].message.reasoning_content)
            print("content: ", completion.choices[0].message.content)
            """
            # print("done with response")
            # need to extract the **STL** part
            # print(f"response: {response}")
            # extracted_response = re.search(regex, response[0].outputs[0].text)
            # print(f"regular response: {response}\n")
            # now put the STL through
            
            # testing json parsing
            try:
                output_dict = json.loads(response)
                extracted_response = output_dict["output_STL:"]
            except Exception as e:
                extracted_response = None

            if extracted_response is None:
                # TODO: modify prompt to note that response was not included in ****
                output_translations[i][k][j] = response
                continue # for now, skip over the rest of this iteration
            try:
                parsed_STL = parser.parse(extracted_response.group(0))
                output_translations[i][k][j] = extracted_response + "\n" + "Success"
                # TODO: need to do extra syntactic check: are the intervals correct?
                syntactically_correct_responses.append(parsed_STL)
            except Exception as e:
                # TODO: if not parsed correctly? --> update the prompt with exception information
                # print(e)
                output_translations[i][k][j] = extracted_response.group(0) + "\n" + str(e) # put the exception as the value --> couldn't be parsed correctly
                continue # continue for now

        # at this point syntactically_correct_responses should be filled with responses
        literal_translations = [] # np.zeroes_like(syntactically_correct_responses)
        for stl in syntactically_correct_responses:
            # TODO: translate these to literal STL --> write the stl2literal function
            literal_translation.append(STL2literal(parsed_STL, grammar))

        # these literal translations need to be evaluated for semantic integrity
        # obtain embeddings of the original sentence and all of the literal translations
        literal_embeddings = [] # np.zeroes_like(literal_translations)
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
            if sim_matrix[best_stl_id] < 0.7: # semantic_threshold:
                # reject
                final_sentences[k] = "Failure" # ([sentence, None])
            else:
                # accept
                final_sentences[k] = ([sentence, syntactically_correct_responses[best_stl_id]])   
        else:
            final_sentences[k] = None


with open("output_sentences.txt", "w") as f:
    f.write(repr(output_translations))

with open("final_sentences.txt", "w") as f:
    f.write(repr(final_sentences)) 
