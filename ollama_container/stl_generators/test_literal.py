from lark import Lark
from test import STL2literal
import json

file_name = f'../config/stl_generator_v4_config.json'

with open(file_name, 'r') as f:
    params = json.load(f)

grammar = params['grammar']
parser = Lark(grammar)

print(STL2literal('', grammar))

