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

# Set up structures, parameters
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

# Load from input files
model_name = sys.argv[1]
sentences = pandas.read_csv(params['sentences_csv'])

# Additional setup
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

    feedback = ""
    feedback_dict = params['feedback']
    # need to include a feedback dictionary


    # do num_translations_per_input_sentence-many translations for this one input sentence
    for i in range(num_translations_per_input_sentence): # these are the m shots
        response = llm.chat([{"role": "user", "content": prompt+feedback}], sampling_params)[0].outputs[0].text

        # try to extract the STL statement, if unsuccessful, put a None into the translations dataframe entry
        try:
            output_dict = json.loads(response)
            extracted_response = output_dict["output_STL"]
            label1 = 'STL-'+ str(i)
            translations.at[sentence_index, label1] = extracted_response
        except Exception as e:
            label1 = 'STL-'+ str(i)
            translations.at[sentence_index, label1] = "STL could not be extracted"
            feedback = feedback_dict['extraction error']
            continue
            
        # try to parse the STL statement, if unsuccessful, put a None into the translations dataframe entry
        try:
            parsed_STL = parser.parse(extracted_response) # not used in stl2literal but to check syntax
            syntactically_correct_responses.append((extracted_response, sentence_index, i))
            label1 = 'STL-'+ str(i)
            translations.at[sentence_index, label1] = extracted_response
        except Exception as e:
            label1 = 'STL-'+ str(i)
            if translations.at[sentence_index, label1] != 'STL could not be extracted':
                translations.at[sentence_index, label1] = "STL could not be parsed"
            syntactically_correct_responses.append(("STL could not be parsed", sentence_index, i))
            continue


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
