from vllm import LLM, SamplingParams
from lark import Lark
import numpy as np
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from stl2literal import STL2literal
from stl_base import STLBase
from vllm.sampling_params import GuidedDecodingParams
from pydantic import BaseModel
import json, csv, sys, traceback, re, logging, pickle, pandas, os, random

####################################################################################
# Debugging logging
####################################################################################

import logging
logging.basicConfig(filename='output.log', level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s: %(message)s')

####################################################################################
# Set up structures, parameters
####################################################################################

stl_base_instance = STLBase()

class STLResponse(BaseModel):
    thinking: str
    input_statement: str
    output_STL: str
guided_decoding_params = GuidedDecodingParams(json=STLResponse.model_json_schema())
stl_response_json = STLResponse.model_json_schema()

file_name = f'../config/{sys.argv[2]}'

with open(file_name, 'r') as f:
    params = json.load(f)

sampling_params = SamplingParams(
        temperature=params['model_parameters']['temperature'],
        top_p=params['model_parameters']['top_p'],
        top_k=params['model_parameters']['top_k'],
        min_p=params['model_parameters']['min_p'],
        presence_penalty=params['model_parameters']['presence_penalty'],
        max_tokens=params['model_parameters']['max_tokens'],
        guided_decoding=guided_decoding_params)

sampling_params_thinking = SamplingParams(
        temperature=params['model_parameters']['temperature'],
        top_p=params['model_parameters']['top_p'],
        top_k=params['model_parameters']['top_k'],
        min_p=params['model_parameters']['min_p'],
        presence_penalty=params['model_parameters']['presence_penalty'],
        max_tokens=params['model_parameters']['max_tokens'])

model_dtype=params['model_parameters']['model_dtype']
max_model_len=params['model_parameters']['max_model_len']
gpu_memory_utilization=params['model_parameters']['gpu_memory_utilization']
num_shots_per_input_sentence=params['num_shots_per_input_sentence']

model_name = sys.argv[1]
sentences = pandas.read_csv(params['sentences_csv'])
embedding_model = SentenceTransformer(params['embedding_model_name'], device='cpu')
grammar = params['grammar']
parser = Lark(grammar)

curated_dataset = []
try:
    with open(f'../pkl/curated_dataset.pkl', 'rb') as f:
        curated_dataset = pickle.load(f)
        print(f'Loaded curated dataset')
except Exception as e:
    print(e)

# Create a file which contains all the relevant output related to this model
# Augment the input file with correct number of stl and literal rows
translations = sentences.copy()

for i in range(num_shots_per_input_sentence):
    translations[f'STL-{i}'] = None

for i in range(num_shots_per_input_sentence):
    translations[f'Literal-{i}'] = None

full_translations = []

# Create the LLM for this model
llm = LLM(model=model_name,
    dtype=model_dtype,
    max_model_len=max_model_len,
    gpu_memory_utilization=gpu_memory_utilization)

# storage for output sentences
final_sentences = []

# feedback dictionary
feedback_dict=params['old_prompt_feedback']

####################################################################################
# Translation
# Translation
####################################################################################

# do translations of each sentence
for sentence_index, sentence in sentences['input statement'].items():
    # Under new scheme, each sentence still gets m shots at translation, but each 'shot' can have up to n attempts at correction
    # Prompt order:
    # Thinking --> STL --> Feedback --> Feedback --> Feedback 

    # accumulate syntactically valid responses across each shot (so max size of syntactically correct responses is m)
    syntactically_correct_responses = []

    # start the current feedback as nothing at the beginning of each shot
    feedback = ""

    # take m shots at producing a syntactically valid response
    for i in range(num_shots_per_input_sentence):
        # Each shot ends once max attempts reached or a syntactically correct statement has been reached
        syntax_passed = True

        ####################################################################
        # 1) Thinking prompt
        ####################################################################

        thinking_prompt = params['thinking_prompt']['prompt_1'] + '\n' + sentence + '\n\n' + params['thinking_prompt']['prompt_2']
        response = llm.chat([{"role": "user", "content": thinking_prompt}], sampling_params_thinking)[0].outputs[0].text
        full_translations.append(thinking_prompt)
        full_translations.append(response)
        
        """
        print('------------------------------------------------------------')
        print(thinking_prompt)
        print('------------------------------------------------------------')
        print(response)
        """

        ####################################################################
        # 2a) Produce examples for the STL prompt
        ####################################################################

        samples = []
        for i in range(params['num_examples']):
            samples.append(random.choice(curated_dataset))

        for _id, sample in enumerate(samples):
            sample = sample.replace('and',' and ')
            sample = sample.replace('<',' < ')
            sample = sample.replace('>',' > ')
            sample = sample.replace('-',' - ')
            sample = sample.replace('implies',' implies ')
            samples[_id] = sample

        literal_translations = []
        for _id, sample in enumerate(samples):
            literal_translations.append(STL2literal(sample, grammar))

        examples = ""
        for _id, sample in enumerate(samples):
            examples += (f"\n{{'thinking:' 'I need to translate this natural language into STL...',\n'input_sentence:' '{literal_translations[_id]}',\n'output_STL': '{sample}'}}\n")

        examples = params['example_prompt']['prompt_1'] + examples + params['example_prompt']['prompt_2']

        ####################################################################
        # 2b) STL Prompt
        ####################################################################

        stl_prompt = params['stl_prompt']['prompt_1'] + '\n' + sentence + '\n\n' + params['stl_prompt']['prompt_2'] + "\n\n" + examples
        response = llm.chat([{"role": "user", "content": stl_prompt}], sampling_params)[0].outputs[0].text
        full_translations.append(stl_prompt)
        full_translations.append(response)

        # print('------------------------------------------------------------')
        # print(stl_prompt)
        # print('------------------------------------------------------------')
        # print(response)

        print('------------------------------------------------------------')
        print('right after stl response')

        ####################################################################
        # 2c) process the stl response
        ####################################################################
        
        # extract stl, if unsuccessful, put none into translations dataframe entry
        try:
            output_dict = json.loads(response)
            # print(f'output_dict: {output_dict}')
            extracted_response = output_dict["output_STL"]
            translations.at[sentence_index, f'stl-{i}'] = extracted_response
            print('------------------------------------------------------------')
            print('successfully extracted')
        except Exception as e:
            translations.at[sentence_index, f'stl-{i}'] = "stl could not be extracted"
            print('------------------------------------------------------------')
            print('extraction failed')
            continue # if no stl can be extracted, then just go to the next shot
            
        # parse stl, if unsuccessful, put none into translations dataframe entry
        try:            
            parsed_stl = parser.parse(extracted_response)
          
            # need to add manual layer for checking the signals name
            signals = re.findall(r"tree\(token\('rule', 's'\), \[token\('\w+', '\w+'\)\]\)", str(parsed_stl))  
            for s in signals:
                s = s.split("tree(token('rule', 's'), [token('__anon_3',")
                s = re.findall(r"'.*'", s)[0]
                if s not in signal_names:
                    raise Exception(f"{s} is not an allowed signal name.")

            print('------------------------------------------------------------')
            print('successfully parsed')
            
            syntactically_correct_responses.append((extracted_response, sentence_index, i))
            translations.at[sentence_index, f'STL-{i}'] = extracted_response
        except Exception as e:
            # Syntax check failed
            syntax_passed = False

            if translations.at[sentence_index, f'STL-{i}'] != 'STL could not be extracted':
                translations.at[sentence_index, f'STL-{i}'] = "STL could not be parsed"
            syntactically_correct_responses.append(("STL could not be parsed", sentence_index, i))
            
            print('------------------------------------------------------------')
            print('parsing failed')
            
            error_feedback = ''
            try:
                # The response ends up here if it there is a syntax problem --> thus feedback should be constructed at this stage
                # TODO: THIS IS WHERE MORE COMPLEX FEEDBACK CAN BE CONSTRUCTED, FORMULATE THE FEEDBACK FOR THE NEXT PROMPT BASED ON THE CURRENT EXTRACTED RESPOSNE
                error_message_less_descriptive = str(e).split('\n')[0].split(',')[0] 
                error_char = str(e).split('\n')[0].split(',')[1].split(' ')[5]
                error_message_more_descriptive = str(e).split('Expected')[0]
                feedback = feedback_dict['parsing_error_0'] + error_char + feedback_dict['parsing_error_1'] + error_message_more_descriptive + '\n[END FEEDBACK]'
            except Exception as e:
                pass
        
        ####################################################################
        # 3) Feedback prompts for this shot if necessary
        ####################################################################

        feedback_attempts_remaining = params["num_correction_attempts_per_shot"]
        
        while not syntax_passed and feedback_attempts_remaining > 0:
            
            print('------------------------------------------------------------')
            print('retrying with feedback')
            
            feedback_attempts_remaining -= 1
            syntax_passed = True

            feedback_prompt = params['feedback_prompt']['prompt_1'] + '\n' + feedback + '\n' + params['feedback_prompt']['prompt_2']            

            response = llm.chat([{"role": "user", "content": feedback_prompt}], sampling_params)[0].outputs[0].text
            full_translations.append(feedback_prompt)
            full_translations.append(response)

            print('------------------------------------------------------------')
            print(feedback_prompt)
            print('------------------------------------------------------------')
            print(response)
            
            # extract stl, if unsuccessful, put none into translations dataframe entry
            try:
                output_dict = json.loads(response)
                extracted_response = output_dict["output_stl"]
                translations.at[sentence_index, f'stl-{i}'] = extracted_response
            except Exception as e:
                translations.at[sentence_index, f'stl-{i}'] = "stl could not be extracted"
                continue # if no stl can be extracted, then just go to the next shot
            
            # parse stl, if unsuccessful, put none into translations dataframe entry
            try:            
                parsed_stl = parser.parse(extracted_response)
            
                # need to add manual layer for checking the signals name
                signals = re.findall(r"tree\(token\('rule', 's'\), \[token\('\w+', '\w+'\)\]\)", str(parsed_stl))  
                for s in signals:
                    s = s.split("tree(token('rule', 's'), [token('__anon_3',")
                    s = re.findall(r"'.*'", s)[0]
                    if s not in signal_names:
                        raise Exception(f"{s} is not an allowed signal name.")

                syntactically_correct_responses.append((extracted_response, sentence_index, i))
                translations.at[sentence_index, f'STL-{i}'] = extracted_response
            except Exception as e:
                # Syntax check failed
                syntax_passed = False

                if translations.at[sentence_index, f'STL-{i}'] != 'STL could not be extracted':
                    translations.at[sentence_index, f'STL-{i}'] = "STL could not be parsed"
                syntactically_correct_responses.append(("STL could not be parsed", sentence_index, i))
            
                error_feedback = ''
                try:
                    # The response ends up here if it there is a syntax problem --> thus feedback should be constructed at this stage
                    # TODO: THIS IS WHERE MORE COMPLEX FEEDBACK CAN BE CONSTRUCTED

                    error_message_less_descriptive = str(e).split('\n')[0].split(',')[0] 
                    error_char = str(e).split('\n')[0].split(',')[1].split(' ')[5]
                    error_message_more_descriptive = str(e).split('Expected')[0]
                    feedback = feedback_dict['parsing_error_0'] + error_char + feedback_dict['parsing_error_1'] + error_message_more_descriptive + '\n[END FEEDBACK]'
                except Exception as e:
                    feedback = ''

    ####################################################################
    # 4) Translate syntactically correct responses to literal
    ####################################################################

    print('####################################################################')
    print('# Sentence Done')
    print('####################################################################')
    print(f'syntactically_correct_responses: {syntactically_correct_responses}')

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
                print(e)
                label1 = 'Literal-'+ str(stl[2])
                translations.at[sentence_index, label1] = "STL to literal failed"
        else:
            label1 = 'Literal-'+ str(stl[2])
            translations.at[sentence_index, label1] = "Literal could not be generated"

    # obtain embeddings of the original sentence and all of the literal translations
    literal_embeddings = []
    nl_embedding = embedding_model.encode(sentence, normalize_embeddings=True)
    for i, literal in enumerate(literal_translations):
        embedding_literal = np.array(embedding_model.encode(literal_translations[i], normalize_embeddings=True))
        literal_embeddings.append(embedding_literal)

    ####################################################################
    # 5) Compare embedding similarity
    ####################################################################

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
    with open(f'../pkl/full_translations_{model_name}.pkl', 'wb') as results:
        pickle.dump(full_translations, results)
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
