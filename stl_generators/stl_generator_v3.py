from vllm import LLM, SamplingParams
from lark import Lark
import numpy as np
from collections import defaultdict
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from stl2literal import STL2literal
from stl_example_generator import STLBase
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
     explanation: str
guided_decoding_params = GuidedDecodingParams(json=STLResponse.model_json_schema())
stl_response_json = STLResponse.model_json_schema()

file_name = f'../config/{sys.argv[2]}.json'

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

for i in range(num_translations_per_input_sentence):
    translations[f'STL-{i}'] = None

for i in range(num_translations_per_input_sentence):
    translations[f'Literal-{i}'] = None

u_translations = translations.copy()

# Create the LLM for this model
llm = LLM(model=model_name,
    dtype=model_dtype,
    max_model_len=max_model_len,
    gpu_memory_utilization=gpu_memory_utilization)

# print(f"max_model_len is: {max_model_len}")
# print(f"max_tokens: {params['model_parameters']['max_tokens']}")

# storage for output sentences
final_sentences = []

# feedback dictionary
feedback_dict=params['feedback']

####################################################################################
# Translation
####################################################################################

# do translations of each sentence
for sentence_index, sentence in sentences['input statement'].items():
    prompt1 = core_prompt_1 + sentence

    # accumulate syntactically valid responses
    syntactically_correct_responses = []

    # start the current feedback as nothing for the first attempt at this sentence
    feedback = ""

    # do the m shots
    for i in range(num_translations_per_input_sentence):
        # change the sampling so that we check over all 3 of the designs to see at least one instance of: (1) F (2) G (3) abs (4) d_ and (5) c(
        # then post-process the output by adding spaces before and after ^, <, > <-- possibly others check that too
        # get random examples (2)
        satisfied = False
        samples = []
        
        """
        while not satisfied:
            satisfied = True
            g_missing = False
            f_missing = False
            abs_missing = False
            d_missing = False
            c_missing = False
            for _id, val in enumerate(samples):
                samples[_id] = stl_base_instance.sample('omega')
            if len(samples[0]) > 80 or len(samples[1]) > 80 or len(samples[2]) > 80:
                satisfied = False
            if ('globally' not in samples[0] and 'globally' not in samples[1] and 'globally' not in samples[2]):
                g_missing = True
            if ('eventually' not in samples[0] and 'eventually' not in samples[1] and 'eventually' not in samples[2]):
                f_missing = True
            if ('d_' not in samples[0] and 'd_' not in samples[1] and 'd_' not in samples[2]):
                d_missing = True
            if ('c(' not in samples[0] and 'c(' not in samples[1] and 'c(' not in samples[2]):
                c_missing = True
            if g_missing or f_missing or d_missing or c_missing:
                satisfied = False
            # also check for ranges time interval
            time_interval_num_num = r'\[\d+,\d+\]'
            time_interval_inf_num = r'\[∞,\d+\]'
            time_interval_inf_inf = r'\[∞,∞\]'

            for sample in samples:
                sample_flagged = False
                if len(re.findall(time_interval_inf_inf, sample)) > 0 or len(re.findall(time_interval_inf_num, sample)) > 0:
                    # print("there's a problem with the interval")
                    satisfied = False
                    break
                intervals = re.findall(time_interval_num_num, sample)
        
                if intervals is not None:
                    for interval in intervals:
                        t_a = interval.split(',')[1:]
                        t_b = interval.split(',')[:-1]
                        if t_b <= t_a:
                            sample_flagged = True
                            satisfied = False
                            break
                if sample_flagged:
                    break
        """
        ####################################################################
        #
        # Sample from curated dataset
        #
        ####################################################################
        for i in range(3):
            samples.append(random.choice(curated_dataset))

        for _id, sample in enumerate(samples):
            sample = sample.replace('and',' and ')
            sample = sample.replace('<',' < ')
            sample = sample.replace('>',' > ')
            sample = sample.replace('-',' - ')
            sample = sample.replace('implies',' implies ')
            samples[_id] = sample

        literal_translations = ["","",""]
        for _id, sample in enumerate(samples):
            print(f'inside sample literal generation')
            print(f'sample: {sample}')
            literal_translations[_id] = STL2literal(sample, grammar)

        # temporary thing to try: replacing F with eventually, G with globally
        """
        for _id, sample in enumerate(samples):
            sample = sample.replace('F[','eventually[')
            sample = sample.replace(']G(',']globally(')
            sample = sample.replace('G[','globally[')
            samples[_id] = sample
        """

        examples = "\n\n[BEGIN EXAMPLES]\nHere are reference examples of STL, but don't copy them. Instead, make sure the STL statements you produce are specific to the input statement that you are currently being asked to translate:\n"
        for _id, sample in enumerate(samples):
            examples += (f"\n{{'thinking': '<thinking>I need to translate the natural language into STL...',\n'input_sentence:' '{literal_translations[_id]}',\n'output_STL': '{sample}'}}\n")
        
        print(f"the prompt is: {prompt1+'\n\n'+feedback+core_prompt_2+examples+'[END EXAMPLES]'}")

        response = llm.chat([{"role": "user", "content": prompt1+feedback+core_prompt_2+examples+'[END EXAMPLES]'}], sampling_params)[0].outputs[0].text
        u_translations.at[sentence_index, f'STL-{i}'] = response
        print(f"the response is: {response}")

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
        pre_extracted_response = extracted_response
        try:
            print("trying to parse response")
            print(f'extracted_response: {extracted_response}')
        
            """
            extracted_response = extracted_response.replace('eventually[','F[')
            extracted_response = extracted_response.replace(']globally(',']G(')
            extracted_response = extracted_response.replace('globally[','G[')
            """
            
            parsed_STL = parser.parse(extracted_response)
            print(f'parsed STL: {parsed_STL}') 
          
            # need to add manual layer for checking the signal name
            signals = re.findall(r"Tree\(Token\('RULE', 's'\), \[Token\('\w+', '\w+'\)\]\)", str(parsed_STL))  
            for s in signals:
                s = s.split("Tree(Token('RULE', 's'), [Token('__ANON_3',")
                s = re.findall(r"'.*'", s)[0]
                if s not in signal_names:
                    raise Exception(f"{s} is not an allowed signal name.")

            d_signals = re.findall(r"Tree\(Token\('RULE', 'd_s'\), \[Token\('\w+', '\w+'\)\]\)", str(parsed_STL))  
            for d in d_signals:
                if len(d_signals) > 0:
                    raise Exception(f'THIS IS A D_ TERM: {str(parsed_STL)}')

                d = d.split("Tree(Token('RULE', 'd_s'), [Token('__ANON_3',")
                d = re.findall(r"'.*'", d)[0]
                if d not in signal_names:
                    raise Exception(f"{d} is not an allowed signal name.")

            # need to add manual layer for checking the signal name

            syntactically_correct_responses.append((extracted_response, sentence_index, i))
            translations.at[sentence_index, f'STL-{i}'] = extracted_response
        except Exception as e:
            if translations.at[sentence_index, f'STL-{i}'] != 'STL could not be extracted':
                translations.at[sentence_index, f'STL-{i}'] = "STL could not be parsed"
            syntactically_correct_responses.append(("STL could not be parsed", sentence_index, i))
            
            error_feedback = ''
            try:
                error_message_less_descriptive = str(e).split('\n')[0].split(',')[0] 
                error_char = str(e).split('\n')[0].split(',')[1].split(' ')[5]
                error_message_more_descriptive = str(e).split('Expected')[0]
                feedback = "[START FEEDBACK]\nYour previous STL response had a syntax error. You must accept this feedback and amend your new response." + feedback_dict['prev_response_setup'] + pre_extracted_response + feedback_dict['parsing_error_0'] + error_char + feedback_dict['parsing_error_1'] + error_message_more_descriptive + '\n[END FEEDBACK]'
            except:
                feedback = '[START FEEDBACK]\nThis response had at least one syntax error.\n[END FEEDBACK]'
            continue

        # at this point, parsing and extraction should have gone well, so the feedback can be positive
        feedback = '[START FEEDBACK]\n' + feedback_dict['prev_response_setup'] + extracted_response + feedback_dict['syntactically_correct'] + '\n[END FEEDBACK]'


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
