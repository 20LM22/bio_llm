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

# Create the LLM for this model
llm = LLM(model=model_name,
    dtype=model_dtype,
    max_model_len=max_model_len,
    gpu_memory_utilization=gpu_memory_utilization)

# feedback dictionary
feedback_dict=params['old_prompt_feedback']

# final output dictionary
results = {}

####################################################################################
# Helper function: generate examples
####################################################################################

def generate_example_prompt(num_examples):
    samples = []
    for i in range(num_examples):
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

    return params['example_prompt']['prompt_1'] + examples + params['example_prompt']['prompt_2']

####################################################################################
# Helper function: get hole feedback
####################################################################################

def get_hole_feedback(e):
    error_char = int(str(e).split('\n')[0].split(',')[1].split(' ')[5]) - 1
    left_bound_found = False
    right_bound_found = False
    left_bound = 0
    right_bound = 0

    print(f'error char: {error_char}')
    print(f'extracted_response[error_char]: {extracted_response[error_char]}')

    # search to left and right for nearest } ) ]
    if extracted_response[error_char] == '(' or extracted_response[error_char] == '[' or extracted_response[error_char] == '{':
        left_bound_found = True
        left_bound = error_char
    else:
        left_bound = error_char - 1
        left_bound_found = False
        while left_bound >= 0:
            if extracted_response[left_bound] == '{' or extracted_response[left_bound] == '[' or extracted_response[left_bound] == '(':
                left_bound_found = True
                break
            left_bound -= 1

    if extracted_response[error_char] == ')' or extracted_response[error_char] == ']' or extracted_response[error_char] == '}':
        right_bound_found = True
        right_bound = error_char
    else:
        right_bound_found = False
        right_bound = error_char + 1
    while right_bound < len(extracted_response):
        if extracted_response[right_bound] == '}' or extracted_response[right_bound] == ']' or extracted_response[right_bound] == ')':
            right_bound_found = True
            break
            right_bound += 1

    if left_bound_found and right_bound_found:
        end_response = extracted_response[right_bound+1:] if right_bound < len(extracted_response)-1 else ''
        extracted_response = extracted_response[:left_bound] + '<??>' + end_response
        return params['feedback_prompt']['hole_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['hole_prompt_2'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['hole_prompt_3']

    return None

####################################################################################
# Helper function: check signal names
####################################################################################

def check_signal_names(parsed_stl):
    signals = re.findall(r"tree\(token\('rule', 's'\), \[token\('\w+', '\w+'\)\]\)", str(parsed_stl))  
    for s in signals:
        s = s.split("tree(token('rule', 's'), [token('__anon_3',")
        s = re.findall(r"'.*'", s)[0]
        if s not in signal_names:
            response = f"{s} is not an allowed signal name." # TODO: expand into feedback prompt
            return response
    return None

####################################################################################
# Helper function: check parentheses
####################################################################################

def check_parentheses(extracted_response):
    left_count = re.findall(r"\(", extracted_response)
    right_count = re.findall(r"\)", extracted_response)
    if left_count != right_count:
        response = f'Your response has an unmatched number of parentheses. There are {left_count} left parentheses and {right_count} right parentheses. Fix this.'
        return params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['default_prompt_2'] + '\n' + response + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4'] 

    left_count = re.findall(r"\{", extracted_response)
    right_count = re.findall(r"\}", extracted_response)
    if left_count != right_count:
        response = f'Unmatched number of curly brackets. There are {left_count} left curly brackets and {right_count} right curly brackets.'
        return params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['default_prompt_2'] + '\n' + response + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4'] 

    left_count = re.findall(r"\[", extracted_response)
    right_count = re.findall(r"\]", extracted_response)
    if left_count != right_count:
        response = f'Unmatched number of square brackets. There are {left_count} left square brackets and {right_count} right square brackets.'
        return params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['default_prompt_2'] + '\n' + response + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4'] 

    return None

####################################################################################
# Helper function: check json
####################################################################################

def check_json(extracted_response):
    try:
        json.loads(extracted_response)
        if extracted_response in '{' and extracted_response in '}' and extracted_response in ':':
            error = 'It looks like you formatted the output STL incorrectly. The JSON format should have three fields: (1) your thinking, (2) the input sentence, and (3) your output STL. However, the output STL field should not contain JSON, it should be a single string. Here is an example of correct formatting:\n' + generate_example_prompt(1)

            return params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['default_prompt_2'] + '\n' + error + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4'] 

        return None
    except Exception as e:
        return None

####################################################################################
# Helper function: produce default error feedback
####################################################################################

def default_feedback(e):
    try:
        error_char = str(e).split('\n')[0].split(',')[1].split(' ')[5]
        error_message_more_descriptive = str(e).split('Expected')[0]
        return params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['default_prompt_2'] + '\n' + error_message_more_descriptive + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4'] 
    except Exception as e:
        return params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['default_prompt_2a'] + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4'] 
        

####################################################################################
# Translation of each sentence
####################################################################################

for sentence_index, sentence in sentences['input statement'].items():
    # Under new scheme, each sentence gets m shots at translation, but each 'shot' can have up to n attempts at correction
    # Prompt order:
    # Thinking --> STL --> Feedback --> Feedback --> Feedback --> Semantic --> Feedback --> Feedback --> Feedback --> Semantic --> etc.

    nl_embedding = embedding_model.encode(sentence, normalize_embeddings=True)

    # start the current feedback as nothing at the beginning of each shot
    feedback = ""

    ####################################################################
    # M shots at producing valid STL
    ####################################################################

    for i in range(num_shots_per_input_sentence):
        # Each shot ends once max attempts reached or a syntactically correct statement has been reached
        syntax_passed = False

        ####################################################################
        # 1) Thinking prompt
        ####################################################################

        thinking_prompt = params['thinking_prompt']['prompt_1'] + '\n' + sentence + '\n\n' + params['thinking_prompt']['prompt_2']
        response = llm.chat([{"role": "user", "content": thinking_prompt}], sampling_params_thinking)[0].outputs[0].text
        
        ####################################################################
        # 2a) STL Prompt
        ####################################################################

        stl_prompt = params['stl_prompt']['prompt_1'] + '\n' + sentence + '\n\n' + params['stl_prompt']['prompt_2'] + "\n\n" + generate_example_prompt(params['num_examples'])
        response = llm.chat([{"role": "user", "content": stl_prompt}], sampling_params)[0].outputs[0].text

        ####################################################################
        # 2b) Process the STL response
        ####################################################################
       
        # Try extraction
        try:
            extracted_response = json.loads(response)["output_STL"]
            print('successfully extracted')
        except Exception as e:
            print('extraction failed')
            continue # if no stl can be extracted, then just go to the next shot
            
        # Try parsing
        parsed_stl = ''
        try:            
            parsed_stl = parser.parse(extracted_response)    
            print('successfully parsed')
        except Exception as e:
            syntax_passed = False 
            print('parsing failed')

            error_feedback = ''
                   
            # Types of feedback:
            # (1) JSON-like
            # (2) Wrong parentheses
            # (3) Bad signal names
            # (4) Fill in hole
            # (5) None of the above --> just give it the parsing error message

            if check_json(extracted_response) is not None:
                feedback = check_json(extracted_response)
            elif check_parentheses(extracted_response) is not None:
                feedback = check_parentheses(extracted_response)
            elif parsed_stl is not '' and check_signal_names(parsed_stl) is not None:
                feedback = check_signal_names(parsed_stl)
            elif get_hole_feedback(extracted_response) is not None:
                feedback = get_hole_feedback(extracted_response)
            else:
                feedback = default_feedback(extracted_response)
        
        ####################################################################
        # 3) Feedback prompts for this shot if necessary
        ####################################################################

        feedback_attempts_remaining = params["num_correction_attempts_per_shot"]
        
        while not syntax_passed and feedback_attempts_remaining > 0:
            
            print('retrying with feedback')
            
            feedback_attempts_remaining -= 1
            syntax_passed = False

            response = llm.chat([{"role": "user", "content": feedback}], sampling_params)[0].outputs[0].text

            # Try extraction
            try:
                extracted_response = json.loads(response)["output_STL"]
                print('successfully extracted')
            except Exception as e:
                print('extraction failed')
                syntax_passed =  False
                break # if no stl can be extracted, then just go to the next shot

            # Try parsing
            parsed_stl = ''
            try:            
                parsed_stl = parser.parse(extracted_response)    
                print('successfully parsed')
                syntax_passed = True
            except Exception as e:
                syntax_passed = False 
                print('parsing failed')

                error_feedback = ''
                   
                if check_json(extracted_response) is not None:
                    feedback = check_json(extracted_response)
                elif check_parentheses(extracted_response) is not None:
                    feedback = check_parentheses(extracted_response)
                elif parsed_stl is not '' and check_signal_names(parsed_stl) is not None:
                    feedback = check_signal_names(parsed_stl)
                elif get_hole_feedback(extracted_response) is not None:
                    feedback = get_hole_feedback(extracted_response)
                else:
                    feedback = default_feedback(extracted_response)

        ####################################################################
        # 4) Perform semantic checks
        ####################################################################

        # After you obtain a good syntax statement, do semantic checks
        num_semantic_checks = params['num_semantic_checks']

        last_stl = extracted_response
        best_stl = extracted_response

        if not syntax_passed: # go to next shot - semantic is only meaningful with a good syntax statement
            continue

        for i in range(num_semantic_checks):
            # first get the embedding of the stl that was just produced 
            stl_embedding = embedding_model.encode(STL2literal(extracted_response, grammar), normalize_embeddings=True)
            current_sim = cosine_similarity(np.array(stl_embedding).reshape(1,-1), np.array(nl_embedding).reshape(1,-1))

            # need to update last_stl and best_stl accordingly
            # TODO: update them LEFT OFF HERE

            semantic_prompt = params['semantic_prompt']['prompt_1'] + '\n' + sentence + '\n\n' + params['semantic_prompt']['prompt_2'] + '\n' + last_stl + '\n' + params['semantic_prompt']['prompt_3'] + '\n' + last_literal + '\n\n' + params['semantic_prompt']['prompt_4'] + '\n' + best_stl + '\n' + params['semantic_prompt']['prompt_3'] + '\n' + best_literal + '\n\n' + params['semantic_prompt']['prompt_5'] + '\n\n' + params['semantic_prompt']['prompt_6']

            response = llm.chat([{"role": "user", "content": semantic_prompt}], sampling_params)[0].outputs[0].text
            full_translations.append(feedback_prompt)
            full_translations.append(response)

            # get the semantic response
            try:
                output_dict = json.loads(response)
                extracted_response = output_dict["output_stl"]
                translations.at[sentence_index, f'stl-{i}'] = extracted_response
            except Exception as e:
                translations.at[sentence_index, f'stl-{i}'] = "stl could not be extracted"
                continue # if no stl can be extracted, then no need to update the best/most recent stl --> just go to next iteration

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

                    # locate hole
                    error_char = int(str(e).split('\n')[0].split(',')[1].split(' ')[5]) - 1
                    left_bound_found = False
                    right_bound_found = False
                    left_bound = 0
                    right_bound = 0

                    print(f"here is the extracted response: {extracted_response}")

                    # search to left and right for nearest } ) ]
                    if extracted_response[error_char] == '(' or extracted_response[error_char] == '[' or extracted_response[error_char] == '{':
                        left_bound_found = True
                        left_bound = error_char
                    else:
                        left_bound = error_char - 1
                        left_bound_found = False
                        while left_bound >= 0:
                            if extracted_response[left_bound] == '{' or extracted_response[left_bound] == '[' or extracted_response[left_bound] == '(':
                                left_bound_found = True
                                break
                            left_bound -= 1

                    if extracted_response[error_char] == ')' or extracted_response[error_char] == ']' or extracted_response[error_char] == '}':
                        right_bound_found = True
                        right_bound = error_char
                    else:
                        right_bound_found = False
                        right_bound = error_char + 1
                        while right_bound < len(extracted_response): 
                            if extracted_response[right_bound] == '}' or extracted_response[right_bound] == ']' or extracted_response[right_bound] == ')':
                                right_bound_found = True
                                break
                            right_bound += 1

                    if left_bound_found and right_bound_found:
                        end_response = extracted_response[right_bound+1:] if right_bound < len(extracted_response)-1 else ''
                        extracted_response = extracted_response[:left_bound] + '<??>' + end_response
                        print("left and right bounds identified")
                        
                        feedback = params['feedback_prompt']['hole_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['hole_prompt_2'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['hole_prompt_3']
                    else:
                        error_message_less_descriptive = str(e).split('\n')[0].split(',')[0] 
                        error_char = str(e).split('\n')[0].split(',')[1].split(' ')[5]
                        error_message_more_descriptive = str(e).split('Expected')[0]
                        feedback = params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['default_prompt_2'] + '\n' + error_message_more_descriptive + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4'] 
                except Exception as e:
                    feedback = params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['default_prompt_2'] + '\n' + error_message_more_descriptive + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4'] 

            # Done attempting to parse and construct feedback, at this point feedback should be ready and syntax_passed should be set up
        
            feedback_attempts_remaining = params["num_correction_attempts_per_shot"]

            print("right before asking for feedback on the response to the first semantic ask")
            print(f'syntax_passed: {syntax_passed}')
            print(f'extracted reponse: {extracted_response}')
       
            while not syntax_passed and feedback_attempts_remaining > 0:
            
                print('------------------------------------------------------------')
                print('retrying with feedback')
            
                feedback_attempts_remaining -= 1
                syntax_passed = True

                feedback_prompt = feedback # params['feedback_prompt']['prompt_1'] + '\n' + feedback + '\n' + params['feedback_prompt']['prompt_2']            

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

                        # locate hole
                        error_char = int(str(e).split('\n')[0].split(',')[1].split(' ')[5]) - 1
                        left_bound_found = False
                        right_bound_found = False
                        left_bound = 0
                        right_bound = 0

                        print(f"here is the extracted response: {extracted_response}")

                        # search to left and right for nearest } ) ]
                        if extracted_response[error_char] == '(' or extracted_response[error_char] == '[' or extracted_response[error_char] == '{':
                            left_bound_found = True
                            left_bound = error_char
                        else:
                            left_bound = error_char - 1
                            left_bound_found = False
                            while left_bound >= 0:
                                if extracted_response[left_bound] == '{' or extracted_response[left_bound] == '[' or extracted_response[left_bound] == '(':
                                    left_bound_found = True
                                    break
                                left_bound -= 1

                        if extracted_response[error_char] == ')' or extracted_response[error_char] == ']' or extracted_response[error_char] == '}':
                            right_bound_found = True
                            right_bound = error_char
                        else:
                            right_bound_found = False
                            right_bound = error_char + 1
                            while right_bound < len(extracted_response): 
                                if extracted_response[right_bound] == '}' or extracted_response[right_bound] == ']' or extracted_response[right_bound] == ')':
                                    right_bound_found = True
                                    break
                                right_bound += 1

                        if left_bound_found and right_bound_found:
                            end_response = extracted_response[right_bound+1:] if right_bound < len(extracted_response)-1 else ''
                            extracted_response = extracted_response[:left_bound] + '<??>' + end_response
                            print("left and right bounds identified")
                        
                            feedback = params['feedback_prompt']['hole_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['hole_prompt_2'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['hole_prompt_3']
                        else:
                            error_message_less_descriptive = str(e).split('\n')[0].split(',')[0] 
                            error_char = str(e).split('\n')[0].split(',')[1].split(' ')[5]
                            error_message_more_descriptive = str(e).split('Expected')[0]
                            feedback = params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['default_prompt_2'] + '\n' + error_message_more_descriptive + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4'] 
                    except Exception as e:
                        feedback = params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['default_prompt_2'] + '\n' + error_message_more_descriptive + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4'] 

            # TODO: make sure syntax problems that occur on last attempt are discarded of
            if syntax_passed:
                results[sentence].append(extracted_response)
            
                # At this point, feedback has been exhausted on the statement        
                nl_embedding = embedding_model.encode(sentence, normalize_embeddings=True)
                stl_embedding = embedding_model.encode(STL2literal(extracted_response, grammar), normalize_embeddings=True)
                current_sim = cosine_similarity(np.array(stl_embedding).reshape(1,-1), np.array(nl_embedding).reshape(1,-1))
                best_sim = cosine_similarity(np.array(nl_embedding).reshape(1,-1), np.array(best_embedding).reshape(1,-1))

                last_stl = extracted_response
                last_literal = STL2literal(last_stl, grammar)
                if current_sim > best_sim:
                    best_stl = last_stl
                    best_literal = last_literal


    print('####################################################################')
    print('# Sentence Done')
    print('####################################################################')
    print(f'results: {results}')

    """
    ####################################################################
    # 4) Translate syntactically correct responses to literal
    ####################################################################

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
    """

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
    with open(f'../pkl/results_{model_name}.pkl', 'wb') as results: # this is the main useful one
        pickle.dump(translations, results)
except Exception as e:
    print(e)

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
