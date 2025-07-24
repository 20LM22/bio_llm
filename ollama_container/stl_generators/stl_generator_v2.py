from vllm import LLM, SamplingParams
from lark import Lark
import numpy as np
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from stl2literal import STL2literal
from vllm.sampling_params import GuidedDecodingParams
from pydantic import BaseModel
import json, csv, sys, traceback, re, logging, pickle, pandas, os

####################################################################################
# Debugging logging
####################################################################################

import logging
logging.basicConfig(filename='output.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s')

####################################################################################
# Set up structures, parameters
####################################################################################

class STLResponse(BaseModel):
     thinking: str
     input_statement: str
     output_STL: str
     explanation: str
guided_decoding_params = GuidedDecodingParams(json=STLResponse.model_json_schema())
stl_response_json = STLResponse.model_json_schema()

with open('../config/stl_generator_config.json') as f:
    params = json.load(f)

sampling_params = SamplingParams(
        temperature=params['model_parameters']['temperature'],
        top_p=params['model_parameters']['top_p'],
        top_k=params['model_parameters']['top_k'],
        min_p=params['model_parameters']['min_p'],
        presence_penalty=params['model_parameters']['presence_penalty'],
        max_tokens=params['model_parameters']['max_tokens'],
        guided_decoding=guided_decoding_params)

model_dtype=params['model_parameters']['model_dtype']
max_model_len=params['model_parameters']['max_model_len']
gpu_memory_utilization=params['model_parameters']['gpu_memory_utilization']
num_translations_per_input_sentence=params['num_translations_per_input_sentence']

model_name = sys.argv[1]
sentences = pandas.read_csv(params['sentences_csv'])
embedding_model = SentenceTransformer(params['embedding_model_name'], device='cpu')
grammar = params['grammar']
parser = Lark(grammar)

core_prompt_1 = params['core_prompt_1']
core_prompt_2 = params['core_prompt_2']

# Create a file which contains all the relevant output related to this model
# Augment the input file with correct number of stl and literal rows
translations = sentences.copy()

for i in range(num_translations_per_input_sentence):
    translations[f'STL-{i}'] = None
    translations[f'Literal-{i}'] = None

u_translations = translations.copy()

# Create the LLM for this model
llm = LLM(model=model_name,
    dtype=model_dtype,
    max_model_len=max_model_len,
    gpu_memory_utilization=gpu_memory_utilization)

# storage for output sentences
final_sentences = []

# feedback dictionary
feedback_dict=params['feedback']

####################################################################################
# Translation
####################################################################################

# do translations of each sentence
for sentence_index, sentence in sentences['input statement'].items():
    prompt = core_prompt_1 + sentence + core_prompt_2

    # accumulate syntactically valid responses
    syntactically_correct_responses = []

    # start the current feedback as nothing for the first attempt at this sentence
    feedback = ""

    # do the m shots
    for i in range(num_translations_per_input_sentence):
        response = llm.chat([{"role": "user", "content": prompt+feedback}], sampling_params)[0].outputs[0].text
        u_translations.at[sentence_index, f'STL-{i}'] = response

        # extract STL, if unsuccessful, put None into translations dataframe entry
        try:
            output_dict = json.loads(response)
            extracted_response = output_dict["output_STL"]
            translations.at[sentence_index, f'STL-{i}'] = extracted_response
        except Exception as e:
            translations.at[sentence_index, f'STL-{i}'] = "STL could not be extracted"
            feedback = feedback_dict['extraction_error']
            continue
            
        # parse STL, if unsuccessful, put None into translations dataframe entry
        try:
            parsed_STL = parser.parse(extracted_response)
            syntactically_correct_responses.append((extracted_response, sentence_index, i))
            translations.at[sentence_index, f'STL-{i}'] = extracted_response
        except Exception as e:
            if translations.at[sentence_index, f'STL-{i}'] != 'STL could not be extracted':
                translations.at[sentence_index, f'STL-{i}'] = "STL could not be parsed"
            syntactically_correct_responses.append(("STL could not be parsed", sentence_index, i))
            logging.error(f'response is: {extracted_response}\nerror is: {e}\n')
            
            # FORMAT THE ERROR MESSAGE IN A USEFUL WAY
            error_feedback = ''
            try:
                error_subsets = str(e).split('\n')[0].split(',')
                error_char = error_subsets[1].split(' ')[4] # 'at line x col x'
                feedback = feedback_dict['prev_response_setup'] + extracted_response + feedback_dict['parsing_error_0'] + error_char + feedback_dict['parsing_error_1'] + error_subsets[0]
            except:
                feedback = 'This response had at least one syntax error.'
            continue

        # at this point, parsing and extraction should have gone well, so the feedback can be positive
        feedback = feedback_dict['prev_response_setup'] + extracted_response + feedback_dict['syntactically_correct']


    # at this point syntactically_correct_responses should be filled with responses and STL columns of 'translations' should also be full
    literal_translations = [] 
    for index, stl in enumerate(syntactically_correct_responses):
        if stl[0] != 'STL could not be extracted' and stl[0] != 'STL could not be parsed':
            try:
                label1 = 'Literal-'+ str(stl[2])
                literal_translation = STL2literal(stl[0], grammar)

                translations.at[sentence_index, label1] = literal_translation
                literal_translations.append(literal_translation)
            except Exception as e:
                label1 = 'Literal-'+ str(stl[2])
                translations.at[sentence_index, label1] = "STL to literal failed"
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

# For now, no selection of best result

model_name = model_name.split('/')[1]
"""
try:
    with open(f"../pkl/final_sentence_{model_name}", "wb") as f:
        pickle.dump(final_sentences, f) # only one sentence though
except Exception as e:
    print(e)
"""

# writing to pkl
try:
    with open(f'../pkl/translations_{model_name}.pkl', 'wb') as results:
        pickle.dump(translations, results)
except Exception as e:
    print(e)

try:
    with open(f'../pkl/u_translations_{model_name}.pkl', 'wb') as results:
        pickle.dump(u_translations, results)
except Exception as e:
    print(e)

"""
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
"""
