from lark import Lark
from test import STL2literal
import json, pickle, re

file_name = f'../config/stl_generator_v4_config.json'

with open(file_name, 'r') as f:
    params = json.load(f)

grammar = params['grammar']
parser = Lark(grammar)

curated_dataset = []
try:
    with open(f'../pkl/curated_dataset.pkl', 'rb') as f:
        curated_dataset = pickle.load(f)
        print(f'Loaded curated dataset')
except Exception as e:
    print(e)

for i in range(100):
    print("aa")

extracted_response = 'globally[0,7](IL6(t) = c(mid) and IL6(t) = c(mild)) and eventually[7,∞](d_IL6(t) < d_c(high))'
# STL2literal(extracted_response,grammar)

sentence = "test"

try:
    STL2literal(extracted_response, grammar)
except Exception as e:
  #  try:
    print("the original error:")
    print(e)
    print("now we handle the error")
    error_char = int(re.findall(r'at line \d+ col \d+', str(e))[0].split(' ')[4]) - 1

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

    print(f'left found: {left_bound_found}')
    print(f'left: {extracted_response[left_bound]}')

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
        print(params['feedback_prompt']['hole_prompt_1'] + '\n' + extracted_response + '\n\n' + params['feedback_prompt']['hole_prompt_2'] + '\n' + sentence + '\n\n' + params['feedback_prompt']['hole_prompt_3'])
    else:
        print("no left and right bounds found")
    # except Exception as e:
      #  print("a new exception while trying to find left and right parentheses")
       # print(e)











def check_signal_names(parsed_stl):
    signals = re.findall(r"Tree\(Token\('RULE', 's'\), \[Token\('\w+', '\w+'\)\]\)", str(parsed_stl))  
    for s in signals:
        s = s.split("Tree(Token('RULE', 's'), [Token('__ANON_3',")
        print(f"after split: {s}")
        s = re.findall(r"'.*'", s[1])[0]
        if s not in signal_names:
            response = f"{s} is not an allowed signal name." # TODO: expand into feedback prompt
            return response
    return None





"""
for c in curated_dataset:
    # print(c)
    STL2literal(c, grammar)
    print('---------------------------------------------------------------------------------------------------------------')
"""

