# import ollama, time
# from ollama import chat
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

sampling_params = SamplingParams(
        temperature=0.4,
        max_tokens=4096)

llm = LLM(model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    dtype="half",
    max_model_len=8192,
    gpu_memory_utilization=0.8)

# let's set up some parameters
# ollama.base_url = "http://localhost:11434" # this is the default port, can be changed on ollama serve & startup
# model_name = "deepseek-r1:1.5b"
num_semantic_attempts = 1 # allow each sentence to get translated 3 times before declaring the translation a failure
num_batch = 1 # when prompting the LLM for a translation, have it produce 6 STL statements, then process them 
regex = r'\*\*.*\*\*' # for matching the STL statement in the response returned by the LLM

# first need a bank of sentences to translate
sentences = [
    'In the mild and moderate groups, IL-6 concentrations were at their highest level in the first week after the symptom onset and then exhibited a decreasing trend.',
    'Remarkably, in the mild group, the amount of these cytokines (IL-1β and IL-1Ra) increased at the day 1–7, reached a peak at the day 8–14, and diminished after >14 days.',
    'TNF-α levels elevated at the day 1–7 and 8–14 times intervals, then decreased at the day>14.',
    'We detected that IL-8 was significantly elevated in all COVID-19 subgroups at three studied time intervals compared to the control group.',
    'We found that although there was no difference in the production of IFN-β in all patients with COVID-19 compared to the control group at the day 1–7, IFN-β levels were higher in moderate, severe, and critical subjects at the day 8–14 or >14 compared to the healthy control and themselves at the day 1–7.',
    'IL-12 reached its maximum level at the day>14 in mild patients.',
    'It is reported that in recovered cases, within a few hrs of virus entry, both α and β IFNs (at first day of infection) are rapidly produced and an antiviral state is soon reached [23]',
    'By day 14, we detected no viral reads for SARS-CoV-2, and the observed cytokines returned to baseline, with the exception of IL-6 and IL1RN or IL1RA, which remained elevated, similar to results observed with MERS (Pascal et al., 2015; Figures 3B and 3C).'
] # this can also be replaced with input from the csv file

# for now, let's assume that we use one prompt to go directly from NL to STL
# we can also try to extend this by doing a NL to literal translation, then literal to STL
# not only might that approach have the benefit of being more robust since it decomposes the semantic
# and the syntactic translation, but it also has the benefit of filtering out sentences that
# aren't any good for STL anyways.
core_prompt_1 = """Translate the following natural language statement into a signal temporal logic (STL) statement: """
core_prompt_2 = """          
            It is extremely important to follow these rules:
            Rule: The time unit is days.
            Rule: You must return the STL statement like this: **your STL response**
            Rule: You must accept feedback on your previous responses and amend them if asked to.
            
            Your response must conform to these rules:
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
            
            Here is an example of natural language to signal temporal logic output for reference; however, make sure the STL statements you generate are specific to the NL statement you are currently being asked to translate: {input: "From 4 to 8 days after infection, IL-6 levels were significantly elevated until day 9, at which point they steadily decreased.", output: "G[4,8] (IL6(t) > c(high)) ^ G[8,T] (d_IL6(t) < 0)"}
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

parser = Lark(grammar)
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

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
            response = llm.generate(prompt, sampling_params)[0].outputs[0].text
            # print("done with response")
            # need to extract the **STL** part
            # print(f"response: {response}")
            extracted_response = re.search(regex, response)
            print(f"extracted: {extracted_response}")
            # now put the STL through
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
