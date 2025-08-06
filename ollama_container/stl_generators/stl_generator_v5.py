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

sampling_params_semantic = SamplingParams(
        temperature=0.6,
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

signal_names = params['signal_names']

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

# columns needed: STL-shot{number of shots per sentence}-S{number of semantic attempts per shot+1}-F{number of feedback attempts during each semantic attempt+1}

for i in range(num_shots_per_input_sentence):
    for j in range(params['num_semantic_checks']+1):
        for k in range(params['num_correction_attempts_per_shot']+1):
            translations[f'STL-shot{i}-S{j}-F{k}'] = None

# Create the LLM for this model
llm = LLM(model=model_name,
    dtype=model_dtype,
    max_model_len=max_model_len,
    gpu_memory_utilization=gpu_memory_utilization)

# feedback dictionary
feedback_dict=params['old_prompt_feedback']

# final output dictionary
results = defaultdict(list)

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
        examples += (f"\n{{'thinking:' 'Hmm, first I should...',\n'input_sentence:' '{literal_translations[_id]}',\n'output_STL': '{sample}'}}\n")

    return params['example_prompt']['prompt_1'] + examples + params['example_prompt']['prompt_2']

####################################################################################
# Helper function: get hole feedback
####################################################################################

def get_hole_feedback(e, extracted_response, sentence):
    try:
   #     print("the original error:")
    #    print(e)
     #   print("now we handle the error")
        error_char = int(re.findall(r'at line \d+ col \d+', str(e))[0].split(' ')[4]) - 1

        left_bound_found = False
        right_bound_found = False
        left_bound = 0
        right_bound = 0

    #    print(f'error char: {error_char}')
   #     print(f'extracted_response[error_char]: {extracted_response[error_char]}')

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

   #     print(f'left found: {left_bound_found}')
    #    print(f'left: {extracted_response[left_bound]}')

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
            print('getting hole feedback')
            end_response = extracted_response[right_bound+1:] if right_bound < len(extracted_response)-1 else ''
            extracted_response = extracted_response[:left_bound] + '<??>' + end_response
            return params['feedback_prompt']['hole_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['hole_prompt_2'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['hole_prompt_3']
        
        return None
    except Exception as e:
        return None


####################################################################################
# Helper function: check signal names
####################################################################################

def check_signal_names(parsed_stl, extracted_response, sentence):
    print(" ")
    signals = re.findall(r"Tree\(Token\('RULE', 's'\), \[Token\('\w+', '\w+'\)\]\)", str(parsed_stl)) 
    print(f'signals is: {signals}')
    for s in signals:
        s = s.split("Tree(Token('RULE', 's'), [Token('__ANON_3',")
        # print(f"after split: {s}")
        s = re.findall(r"'.*'", s[1])[0]
        try:
            s = s[1:-1]
            if s not in signal_names:
                print('getting species name feedback')
                # TODO: try a hole approach, could do all bad names at once
                response = 'You are trying to translate this sentence to STL:\n' + sentence + '\n\n' + 'Your previous response was:\n' + extracted_response + '\n\n' + 'However, you used ' + s + ' as a species name in your response, which is not allowed. Fix your response so it uses the allowed species names.\n\n' + "Format your response in JSON. Include (1) your thinking process, (2) the input statement, and (3) your STL response.\nYour STL response must conform to the following rules\n:[BEGIN RULES]\nu : less_than | greater_than | is | derivative_greater_than | derivative_less_than | derivative_is\nless_than : s(t) < c # Species s is less than c\ngreater_than : s(t) > c # Species s is greater than c\nis : s(t) = c # Species s is close to c\nderivative_greater_than : d_s(t) > d_c # The rate of change of species s is greater than d_c\nderivative_less_than : d_s(t) < d_c # The rate of change of species s is less than d_c\nderivative_is : d_s(t) = d_c # The rate of change species s is close to d_c\nc : s(t_a) | \"c(low)\" | \"c(mid)\" | \"c(high)\" # c is the level of a species, it can be a specific value or generally just low, moderate, or high\nd_c : 0 # Rate of change is 0\n\t| \"d_c(low)\" # Species is slowly increasing\n\t| \"d_c(high)\" # Species is rapidly increasing\n\t| \"-d_c(low)\" # Species is slowly decreasing\n\t| \"-d_c(high)\" # Species is quickly decreasing\npredicate : u | u1 and u2 | u1 implies u2 # You can combine predicates with Boolean operators\ntemporal_operator : eventually[t_a,t_b]globally(predicate) # This means that between day t_a and t_b, there is a point when the predicate becomes true for the rest of the interval\n\t| globally[t_a,t_b](phi) # This means the predicate is true over the entire interval from day t_a to t_b\n\t| eventually[t_a,t_b](phi) # This means there is at least 1 time between days t_a and t_b that the predicate is true\nt_a : number | ∞ # Time in days\ns : IL6 | IL12 | IL1β | IL1Ra | TNFα | IL8 | IFNα | IFNβ | SARSCoV2 | IL1RN # Species names you can use\nd_IL6 | d_IL12 | d_IL1β | d_IL1Ra | d_TNFα | d_IL8 | d_IFNα | d_IFNβ | d_SARSCoV2 | d_IL1RN # Names for derivatives of the species\n[END RULES]\n\nThe d_s terms represent the derivative of a signal, so you may find those terms helpful for describing how signals increase or decrease. For general statements describing the levels of some species as \"high\" or \"low\" for example, you may find comparison statements helpful."
                return response
        except Exception as e:
            print('getting species name feedback')
            response = 'You are trying to translate this sentence to STL:\n' + sentence + '\n\n' + 'Your previous response was:\n' + extracted_response + '\n\n' + 'However, you used ' + s + ' as a species name in your response, which is not allowed. Fix your response so it uses the allowed species names.\n\n' + "Format your response in JSON. Include (1) your thinking process, (2) the input statement, and (3) your STL response.\nYour STL response must conform to the following rules\n:[BEGIN RULES]\nu : less_than | greater_than | is | derivative_greater_than | derivative_less_than | derivative_is\nless_than : s(t) < c # Species s is less than c\ngreater_than : s(t) > c # Species s is greater than c\nis : s(t) = c # Species s is close to c\nderivative_greater_than : d_s(t) > d_c # The rate of change of species s is greater than d_c\nderivative_less_than : d_s(t) < d_c # The rate of change of species s is less than d_c\nderivative_is : d_s(t) = d_c # The rate of change species s is close to d_c\nc : s(t_a) | \"c(low)\" | \"c(mid)\" | \"c(high)\" # c is the level of a species, it can be a specific value or generally just low, moderate, or high\nd_c : 0 # Rate of change is 0\n\t| \"d_c(low)\" # Species is slowly increasing\n\t| \"d_c(high)\" # Species is rapidly increasing\n\t| \"-d_c(low)\" # Species is slowly decreasing\n\t| \"-d_c(high)\" # Species is quickly decreasing\npredicate : u | u1 and u2 | u1 implies u2 # You can combine predicates with Boolean operators\ntemporal_operator : eventually[t_a,t_b]globally(predicate) # This means that between day t_a and t_b, there is a point when the predicate becomes true for the rest of the interval\n\t| globally[t_a,t_b](phi) # This means the predicate is true over the entire interval from day t_a to t_b\n\t| eventually[t_a,t_b](phi) # This means there is at least 1 time between days t_a and t_b that the predicate is true\nt_a : number | ∞ # Time in days\ns : IL6 | IL12 | IL1β | IL1Ra | TNFα | IL8 | IFNα | IFNβ | SARSCoV2 | IL1RN # Species names you can use\nd_IL6 | d_IL12 | d_IL1β | d_IL1Ra | d_TNFα | d_IL8 | d_IFNα | d_IFNβ | d_SARSCoV2 | d_IL1RN # Names for derivatives of the species\n[END RULES]\n\nThe d_s terms represent the derivative of a signal, so you may find those terms helpful for describing how signals increase or decrease. For general statements describing the levels of some species as \"high\" or \"low\" for example, you may find comparison statements helpful."
            return response

    return None

####################################################################################
# Helper function: check parentheses
####################################################################################

def check_parentheses(extracted_response, sentence):
    # print("at start of check parentheses")
    # print(f'extracted_response: {extracted_response}')
    left_count = len(re.findall(r"\(", extracted_response))
    # print(f'left_count: {left_count}')
    right_count = len(re.findall(r"\)", extracted_response))
    # print(f'right_count: {right_count}')
    if left_count != right_count:
        print('getting parentheses feedback')
        response = f'Your response has an unmatched number of parentheses. There are {left_count} left parentheses and {right_count} right parentheses. Fix your response so that there are not any unmatched parentheses.'
        return params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + response + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4']

    left_count = len(re.findall(r"\{", extracted_response))
    right_count = len(re.findall(r"\}", extracted_response))
    if left_count != right_count:
        print('getting parentheses feedback')
        response = f'Your response has an unmatched number of curly brackets. There are {left_count} left curly brackets and {right_count} right curly brackets. Fix your response so that there are not any unmatched curly brackets.'
        return params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + response + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4']
    left_count = len(re.findall(r"\[", extracted_response))
    right_count = len(re.findall(r"\]", extracted_response))
    if left_count != right_count:
        print('getting parentheses feedback')
        response = f'Your response has an unmatched number of square brackets. There are {left_count} left square brackets and {right_count} right square brackets. Fix your response so that there are not any unmatched square brackets.'
        return params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + response + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4']
    print('no problems with parentheses')
    return None

####################################################################################
# Helper function: check json
####################################################################################

def check_json(extracted_response, sentence):
    try:
        json.loads(extracted_response)
        if extracted_response in '{' and extracted_response in '}' and extracted_response in ':':
            error = 'It looks like you formatted the output STL incorrectly. The JSON format should have three fields: (1) your thinking, (2) the input sentence, and (3) your output STL. However, the output STL field should not contain JSON inside of it, but instead it should be a single string. Here is an example of correct formatting:\n' + generate_example_prompt(1)
            print("getting json feedback")
            return params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['default_prompt_2'] + '\n' + error + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4'] 

        return None
    except Exception as e:
        return None

####################################################################################
# Helper function: produce default error feedback
####################################################################################

def default_feedback(e, extracted_response, sentence):
    print('inside default feedback')
    print(f'extracted response: {extracted_response}')
    print(f'{e}')
    try:
        error_char = int(re.findall(r'at line \d+ col \d+', str(e))[0].split(' ')[4]) - 1
        error_message_more_descriptive = str(e).split('Expected')[0]

        return params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['default_prompt_2'] + '\n' + error_message_more_descriptive + '\n\n' + params['feedback_prompt']['default_prompt_2a'] + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4']
    
    except Exception as e:
        return params['feedback_prompt']['default_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['default_prompt_2'] + '\n' + str(e) + '\n\n' + params['feedback_prompt']['default_prompt_2a'] + '\n\n' + params['feedback_prompt']['default_prompt_3'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['default_prompt_4']


####################################################################################
# Translation of each sentence
####################################################################################

all_responses_all_sentences = []

for sentence_index, sentence in sentences['input statement'].items():
    print(f'sentence being translated: {sentence}')
    # Under new scheme, each sentence gets m shots at translation, but each 'shot' can have up to n attempts at correction
    # Prompt order:
    # Thinking --> STL --> Feedback --> Feedback --> Feedback --> Semantic --> Feedback --> Feedback --> Feedback --> Semantic --> etc.

    # start the current feedback as nothing at the beginning of each shot
    feedback = ""

    all_responses_this_sentence = []

    ####################################################################
    # M shots at producing valid STL
    ####################################################################

    for i in range(num_shots_per_input_sentence):
        print(f"beginning of shot {i}")

        responses_this_shot = {
            f'shot-{i}': []
        }

        # Each shot ends once max attempts reached or a syntactically correct statement has been reached
        syntax_passed = False

        ####################################################################
        # 1) Thinking prompt
        ####################################################################

        print('thinking prompt')
        thinking_prompt = params['thinking_prompt']['prompt_1'] + '\n' + sentence + '\n\n' + params['thinking_prompt']['prompt_2']
        print(f'thinking prompt: {thinking_prompt}')
        response = llm.chat([{"role": "user", "content": thinking_prompt}], sampling_params_thinking)[0].outputs[0].text
        print(f'response: {response}')
        
        ####################################################################
        # 2a) STL Prompt
        ####################################################################

        print('stl prompt')
        stl_prompt = params['stl_prompt']['prompt_1'] + '\n' + sentence + '\n\n' + params['stl_prompt']['prompt_2'] + "\n\n" + generate_example_prompt(params['num_examples'])
        print(f'stl prompt: {stl_prompt}')
        response = llm.chat([{"role": "user", "content": stl_prompt}], sampling_params)[0].outputs[0].text
        print(f'response: {response}')

        ####################################################################
        # 2b) Process the STL response
        ####################################################################
       
        # Try extraction
        try:
            extracted_response = json.loads(response)["output_STL"]
            print('stl extracted')
            translations.at[sentence_index, f'STL-shot{i}-S0-F0'] = extracted_response
        except Exception as e:
            print('extraction failed')
            translations.at[sentence_index, f'STL-shot{i}-S0-F0'] = "STL could not be extracted"
            continue # if no stl can be extracted, then just go to the next shot
            
        # Try parsing
        parsed_stl = ''
        try:           
            # TODO: REMOVE THIS WHEN DONE lksdjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj
            extracted_response = 'globally[1,∞](d_IL6(t) < c(high))'
            parsed_stl = parser.parse(extracted_response)
            print('right before checking signal names')
            if check_signal_names(parsed_stl, extracted_reponse, sentence) is not None:
                print(f'first check of shot, signal name is getting flagged')
                raise Exception("bad signal name")
            syntax_passed = True
            print('stl parsed')
            translations.at[sentence_index, f'STL-shot{i}-S0-F0'] = extracted_response
        except Exception as e:
            if translations.at[sentence_index, f'STL-shot{i}-S0-F0'] != 'STL could not be extracted':
                translations.at[sentence_index, f'STL-shot{i}-S0-F0'] = "STL could not be parsed"
            syntax_passed = False 
            print('parsing failed')

            error_feedback = ''
                   
            # Types of feedback:
            # (1) JSON-like
            # (2) Wrong parentheses
            # (3) Bad signal names
            # (4) Fill in hole
            # (5) None of the above --> just give it the parsing error message

            print(f'extracted_response: {extracted_response}')

            if check_json(extracted_response, sentence) is not None:
                print('feedback is check json')
                feedback = check_json(extracted_response, sentence)
            elif check_parentheses(extracted_response, sentence) is not None:
                print('feedback is parentheses')
                feedback = check_parentheses(extracted_response, sentence)
            elif parsed_stl != '' and check_signal_names(parsed_stl, extracted_response, sentence) is not None:
                feedback = check_signal_names(parsed_stl, extracted_response, sentence)
                print('feedback is bad signal names')
            elif get_hole_feedback(e, extracted_response, sentence) is not None:
                feedback = get_hole_feedback(e, extracted_response, sentence)
                print('feedback is fix hole')
            else:
                feedback = default_feedback(e, extracted_response, sentence)
                print('feedback is default')
        
        ####################################################################
        # 3) Feedback prompts for this shot if necessary
        ####################################################################

        feedback_attempts_remaining = params["num_correction_attempts_per_shot"]
        count = 0
        
        while not syntax_passed and feedback_attempts_remaining > 0:
            count += 1

            feedback_attempts_remaining -= 1
            syntax_passed = False

            print('now prompting with the feedback')
            m = feedback + '\n\n' + generate_example_prompt(params['num_examples'])
            print(f'feedback prompt: {m}')

            response = llm.chat([{"role": "user", "content": m }], sampling_params)[0].outputs[0].text
            print(f'response: {response}')

            # Try extraction
            try:
                extracted_response = json.loads(response)["output_STL"]
                translations.at[sentence_index, f'STL-shot{i}-S0-F{count}'] = extracted_response
                print('stl extracted')
            except Exception as e:
                translations.at[sentence_index, f'STL-shot{i}-S0-F{count}'] = "STL could not be extracted"
                print('extraction failed')
                syntax_passed =  False
                break # if no stl can be extracted, then just go to the next shot

            # Try parsing
            parsed_stl = ''
            
            try:
                print('right before trying to parse')
                parsed_stl = parser.parse(extracted_response)    
                print('right before checking signal names')
                if check_signal_names(parsed_stl, extracted_response, sentence) is not None:
                    raise Exception("bad signal name")
                print('stl parsed')
                syntax_passed = True
                translations.at[sentence_index, f'STL-shot{i}-S0-F{count}'] = extracted_response
            except Exception as e:
                if translations.at[sentence_index, f'STL-shot{i}-S0-F{count}'] != 'STL could not be extracted':
                    translations.at[sentence_index, f'STL-shot{i}-S0-F{count}'] = "STL could not be parsed"
                syntax_passed = False 
                print('parsing failed')

                if check_json(extracted_response, sentence) is not None:
                    print('feedback is check json')
                    feedback = check_json(extracted_response, sentence)
                elif check_parentheses(extracted_response, sentence) is not None:
                    print('feedback is parentheses')
                    feedback = check_parentheses(extracted_response, sentence)
                elif parsed_stl != '' and check_signal_names(parsed_stl, extracted_response, sentence) is not None:
                    feedback = check_signal_names(parsed_stl, extracted_response, sentence)
                    print('feedback is bad signal names')
                elif get_hole_feedback(e, extracted_response, sentence) is not None:
                    feedback = get_hole_feedback(e, extracted_response, sentence)
                    print('feedback is fix hole')
                else:
                    feedback = default_feedback(e, extracted_response, sentence)
                    print('feedback is default')


        ####################################################################
        # 4) perform semantic checks
        ####################################################################

        # after you obtain a good syntax statement, do semantic checks
        num_semantic_checks = params['num_semantic_checks']

        last_stl = extracted_response
        best_stl = extracted_response

        if not syntax_passed: # go to next shot - semantic is only meaningful with a good syntax statement
            print(f'out of attempts at feedback but still wrong OR extraction failed, moving onto next shot')
            continue

        # Add this first valid syntax response to the list
        responses_this_shot[f'shot-{i}'].append(extracted_response)

        for j in range(num_semantic_checks):
            print(f'prompting semantic iteration {j}')

            last_literal = STL2literal(last_stl, grammar)
            best_literal = STL2literal(best_stl, grammar)

            if last_literal == best_literal:
                semantic_prompt = params['semantic_prompt']['prompt_1'] + '\n' + sentence + '\n\n' + params['semantic_prompt']['prompt_4'] + '\n' + best_stl + '\n' + params['semantic_prompt']['prompt_3'] + '\n' + best_literal + '\n\n' + params['semantic_prompt']['prompt_5'] + '\n\n' + params['semantic_prompt']['prompt_6'] + '\n\n' + generate_example_prompt(params['num_examples'])
            else:
                semantic_prompt = params['semantic_prompt']['prompt_1'] + '\n' + sentence + '\n\n' + params['semantic_prompt']['prompt_2'] + '\n' + last_stl + '\n' + params['semantic_prompt']['prompt_3'] + '\n' + last_literal + '\n\n' + params['semantic_prompt']['prompt_4'] + '\n' + best_stl + '\n' + params['semantic_prompt']['prompt_3'] + '\n' + best_literal + '\n\n' + params['semantic_prompt']['prompt_5'] + '\n\n' + params['semantic_prompt']['prompt_6'] + '\n\n' + generate_example_prompt(params['num_examples'])

            print(f'semantic prompt is: {semantic_prompt}')
            response = llm.chat([{"role": "user", "content": semantic_prompt}], sampling_params_semantic)[0].outputs[0].text
            print(f'semantic response is: {response}')

            # extract STL
            try:
                extracted_response = json.loads(response)["output_STL"]
                print('STL extracted')
                translations.at[sentence_index, f'STL-shot{i}-S{j+1}-F0'] = extracted_response
            except Exception as e:
                print('extraction failed')
                translations.at[sentence_index, f'STL-shot{i}-S{j+1}-F0'] = "STL could not be extracted"
                continue # if no stl can be extracted, then no need to update the best/most recent stl --> just go to next iteration

            # parse STL
            parsed_stl = ''
            try:            
                parsed_stl = parser.parse(extracted_response)    
                if check_signal_names(parsed_stl, extracted_response, sentence) is not None:
                    raise Exception("bad signal name")
                print('STL parsed')
                translations.at[sentence_index, f'STL-shot{i}-S{j+1}-F0'] = extracted_response
                syntax_passed = True
            except Exception as e:
                if translations.at[sentence_index, f'STL-shot{i}-S{j+1}-F0'] != 'STL could not be extracted':
                    translations.at[sentence_index, f'STL-shot{i}-S{j+1}-F0'] = "STL could not be parsed"
                syntax_passed = False 
                print('parsing failed')

                if check_json(extracted_response, sentence) is not None:
                    print('feedback is check json')
                    feedback = check_json(extracted_response, sentence)
                elif check_parentheses(extracted_response, sentence) is not None:
                    print('feedback is parentheses')
                    feedback = check_parentheses(extracted_response, sentence)
                elif parsed_stl != '' and check_signal_names(parsed_stl, extracted_response, sentence) is not None:
                    feedback = check_signal_names(parsed_stl, extracted_response, sentence)
                    print('feedback is bad signal names')
                elif get_hole_feedback(e, extracted_response, sentence) is not None:
                    feedback = get_hole_feedback(e, extracted_response, sentence)
                    print('feedback is fix hole')
                else:
                    feedback = default_feedback(e, extracted_response, sentence)
                    print('feedback is default')


            feedback_attempts_remaining = params["num_correction_attempts_per_shot"]
 
            count = 0
            while not syntax_passed and feedback_attempts_remaining > 0:
                count += 1

                feedback_attempts_remaining -= 1
                syntax_passed = False

                m = feedback + '\n\n' + generate_example_prompt(params['num_examples'])
                print(f'feedback prompt: {m}')

                print('prompting with feedback')
                response = llm.chat([{"role": "user", "content": m }], sampling_params)[0].outputs[0].text
            
                # extract STL
                try:
                    extracted_response = json.loads(response)["output_stl"]
                    print('STL extracted')
                    translations.at[sentence_index, f'STL-shot{i}-S{j+1}-F{count}'] = extracted_response
                except Exception as e:
                    print('extraction failed')
                    translations.at[sentence_index, f'STL-shot{i}-S{j+1}-F{count}'] = "STL could not be extracted"
                    continue # if no stl can be extracted, then no need to update the best/most recent stl --> just go to next iteration

                # parse STL
                parsed_stl = ''
                try:            
                    parsed_stl = parser.parse(extracted_response)    
                    if check_signal_names(parsed_stl, extracted_response, sentence) is not None:
                        raise Exception("bad signal name")
                    print('STL parsed')
                    syntax_passed = True
                    translations.at[sentence_index, f'STL-shot{i}-S{j+1}-F{count}'] = extracted_response
                except Exception as e:
                    syntax_passed = False 
                    if translations.at[sentence_index, f'STL-shot{i}-S{j+1}-F{count}'] != 'STL could not be extracted':
                        translations.at[sentence_index, f'STL-shot{i}-S{j+1}-F{count}'] = "STL could not be parsed"
                    print('parsing failed')


                    if check_json(extracted_response, sentence) is not None:
                        print('feedback is check json')
                        feedback = check_json(extracted_response, sentence)
                    elif check_parentheses(extracted_response, sentence) is not None:
                        print('feedback is parentheses')
                        feedback = check_parentheses(extracted_response, sentence)
                    elif parsed_stl != '' and check_signal_names(parsed_stl, extracted_response, sentence) is not None:
                        feedback = check_signal_names(parsed_stl, extracted_response, sentence)
                        print('feedback is bad signal names')
                    elif get_hole_feedback(e, extracted_response, sentence) is not None:
                        feedback = get_hole_feedback(e, extracted_response, sentence)
                        print('feedback is fix hole')
                    else:
                        feedback = default_feedback(e, extracted_response, sentence)
                        print('feedback is default')

                 
            if syntax_passed:
                print(f'feedback was able to correct this semantic attempt')
                # Add this first valid syntax response to the list
                responses_this_shot[f'shot-{i}'].append(extracted_response)
 
                # Update the last/best result        
                nl_embedding = embedding_model.encode(sentence, normalize_embeddings=True)
                stl_embedding = embedding_model.encode(STL2literal(extracted_response, grammar), normalize_embeddings=True)
                best_embedding = embedding_model.encode(STL2literal(best_stl, grammar), normalize_embeddings=True)
                current_sim = cosine_similarity(np.array(stl_embedding).reshape(1,-1), np.array(nl_embedding).reshape(1,-1))
                best_sim = cosine_similarity(np.array(nl_embedding).reshape(1,-1), np.array(best_embedding).reshape(1,-1))

                last_stl = extracted_response
                if current_sim > best_sim:
                    best_stl = last_stl
                    print(f'this semantic attempt was better, updating last and best stl')
                else:
                    print(f'attempt was not better, no update')
            else:
                print(f'out of attempts at feedback but still wrong, moving onto next shot')

        # Done with the semantic checks - record the best response as the one to take for this shot
        # results[sentence].append(extracted_response) # at this point, extracted_response is the best response

        all_responses_this_sentence.append(responses_this_shot)
        print('####################################################################')
        print(f'# One Shot Done for sentence: {sentence}')
        print('####################################################################')
        print(f"all results for this shot: {responses_this_shot}")
        print(f'results: {results}')

    all_responses_all_sentences.append(all_responses_this_sentence)
    print('####################################################################')
    print(f'# All Shots Done for sentence: {sentence}')
    print('####################################################################')

model_name = model_name.split('/')[1]

# writing to pkl
try:
    # with open(f'../pkl/results_{model_name}.pkl', 'wb') as r:
    #     pickle.dump(results, r)
    with open(f'../pkl/all_responses_all_sentences_{model_name}.pkl', 'wb') as r:
        pickle.dump(all_responses_all_sentences, r)
    with open(f'../pkl/translations_{model_name}.pkl', 'wb') as r:
        pickle.dump(translations, r)
except Exception as e:
    print("there was a pickle problem")
    print(e)
