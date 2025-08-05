from lark import Lark
from test import STL2literal
import json, pickle

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

for c in curated_dataset:
    print(c)
    print(STL2literal(c, grammar))
    print('---------------------------------------------------------------------------------------------------------------')

