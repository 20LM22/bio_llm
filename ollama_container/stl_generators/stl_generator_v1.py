import ollama, time
from ollama import ChatResponse
from ollama import chat
from lark import Lark
import numpy as np
import os
import pandas
from collections import defaultdict
import pickle
from sentence_transformers import SentenceTransformer
import re
from sklearn.metrics.pairwise import cosine_similarity

# let's set up some parameters
ollama.base_url = "http://localhost:11434" # this is the default port, can be changed on ollama serve & startup
model_name = "deepseek-r1:1.5b"
num_semantic_attempts = 3 # allow each sentence to get translated 3 times before declaring the translation a failure
num_batch = 6 # when prompting the LLM for a translation, have it produce 6 STL statements, then process them 
regex = '\*\*.*\*\*' # for matching the STL statement in the response returned by the LLM

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
core_prompt_1 = """... Translate the following natural language statement into a signal temporal logic (STL) statement:
            ..."""
core_prompt_2 = """          
            ...
            ... It is extremely important to follow these rules:
            ... Rule: The time unit is days.
            ... Rule: You must return the STL statement like this: **your STL response**
            ... Rule: You must accept feedback on your previous responses and amend them if asked to.
            ...
            ... Your response must conform to these rules:
            ... [BEGIN RULES]
            ... u : s"(t) < "c | s"(t) > "c | "abs("s"(t) - "c") < "e | d_s"(t) > "d_c | d_s"(t) < "d_c | "abs("d_s"(t) - "d_c") < "e
            ... e : "e" | [0-9]+
            ... c : "s("t_a")" | "c(low)" | "c(mid)" | "c(high)"
            ... d_c : "0" | "d_c(low)" | "d_c(high)" | "-d_c(low)" | "-d_c(high)"
            ... phi : u | phi" ^ "phi | phi" → "phi
            ... psi : "F["t_a","t_a"]G("phi")" | "G["t_a","t_a"]("phi")" | "F["t_a","t_a"]("phi")"
            ... omega : phi | psi | omega" ^ "omega
            ... t_a : [0-9]+ | "T"
            ... s : [a-zA-z0-9]+
            ... d_s : "d_"[a-zA-z0-9]+
            ... [END RULES]
            ...
            ... The d_s terms represent the derivative of a signal, so you may find those terms helpful for describing how signals increase or decrease. For general statements describing the levels of some species as “high” or “low” for example, you may find comparison statements helpful.
            ...
            ... Here are examples of natural language-signal temporal logic pairs for reference; however, make sure the STL statements you generate are specific to the NL statement you are currently being asked to translate.
            ...
            ... {input: "TNF-α levels elevated at the day 1–7 and 8–14 times intervals, then decreased at the day>14", output: "**G[1,14] (tnf(t) < c(mid)) ^ G[15, T]  (d_tnf(t) < 0)**"}
            ... {input: "IL-12 reached its maximum level at the day>14 in mild patients.”, output: "**F[15,T] ( l(t) > c(high)) ^ G[1,14] ( l(t) < c(high))**"}
            ...
"""

### TODO: NEED TO CHANGE THE EXAMPLES ABOVE SO THEY ARE SYNTHETIC ###

grammar = """
    u : s"(t) < "c
        | s"(t) > "c 
        | "abs("s"(t) - "c") < "e
        | d_s"(t) > "d_c
        | d_s"(t) < "d_c
        | "abs("d_s"(t) - "d_c") < "e
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
    t_a : /[0-9]+/
        | "T"
    s : /[a-zA-z0-9]+/
    d_s : "d_"/[a-zA-z0-9]+/
"""

output_translations = []

def stl2literal(parsed_stl):
    # using the parse tree and some sort of dictionary, reconstruct a literal translation



for sentence in sentences:
    # change the prompt for each sentence
    prompt = core_prompt_1 + sentence + core_prompt_2

    # allow each sentence to be translated up n times to get the semantic meaning correct --> n = num_semantic_attempts
    for i in range(num_semantic_attempts):
        # this scope works at the sentence level
        syntactically_correct_responses = []
        
        # need to produce m translations to STL --> m = num_batch
        for j in range(num_batch):
            # for now, let's just use the original prompt without syntactic modification based on the previous responses
            response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}], stream=False).message.content
            # need to extract the **STL** part
            extracted_response = re.search(regex, response)
            # now put the STL through
            if extracted_response is None:
                # TODO: modify prompt to note that response was not included in ****
            
            try:
                parsed_STL = grammar.parse(extracted_response)
                # TODO: need to do extra syntactic check: are the intervals correct?
                syntactically_correct_responses.append(parsed_STL)
            except Exception as e:
                # TODO: if not parsed correctly? --> update the prompt with exception information
                print(e)

        # at this point syntactically_correct_responses should be filled with responses
        literal_translations = [] # np.zeroes_like(syntactically_correct_responses)
        for stl in syntactically_correct_responses:
            # TODO: translate these to literal STL --> write the stl2literal function
            literal_translation.append(stl2literal(parsed_STL))

        # these literal translations need to be evaluated for semantic integrity
        # obtain embeddings of the original sentence and all of the literal translations
        literal_embeddings = [] # np.zeroes_like(literal_translations)
        nl_embedding = np.array(model.encode(sentence, normalize_embeddings=True))
        for i, literal in enumerate(literal_translations):
            embedding_literal = np.array(model.encode(literal_translations[i], normalize_embeddings=True))
            literal_embeddings.append(embedding_literal)
        
        # now compare the embeddings using cosine similarity, take max of the produced array
        sim_matrix = cosine_similarity(np.array(literal_embeddings), np.array(nl_embedding))
        best_stl_id = np.argmax(sim_matrix)

        # only accept what is above similarity threshold
        # the final output is in the form [['nl', 'stl'],['nl', 'stl']]
        if sim_matrix[best_stl_id] < semantic_threshold:
            # reject
            output_translations.append([sentence, None])
        else:
            # accept
            output_translations.append([sentence, syntactically_correct_responses[best_stl_id]])   
