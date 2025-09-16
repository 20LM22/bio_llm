from lark import Lark
import json, sys, pickle, pandas, random

sys.path.insert(1, '..')
from stl2literal import STL2literal

with open(f'../config/config_nx_0_ny_0_nz_0_test_set.json', 'r') as f:
    params = json.load(f)

grammar = params['grammar']
parser = Lark(grammar)

curated_dataset = []
try:
    with open(f'{params['curated_dataset']}', 'rb') as f:
        curated_dataset = pickle.load(f)
        print(f'Loaded curated dataset')
except Exception as e:
    print(e)

samples = []
for n in range(16):
    samples.append(random.choice(curated_dataset))

for _id, sample in enumerate(samples):
    sample = sample.replace('and',' and ')
    sample = sample.replace('<',' < ')
    sample = sample.replace('>',' > ')
    sample = sample.replace('-',' - ')
    sample = sample.replace('∞','inf')
    sample = sample.replace('implies',' implies ')
    samples[_id] = sample

literal_translations = []
for _id, sample in enumerate(samples):
    print(sample)
    literal_translations.append(STL2literal(sample, grammar))

p = pandas.DataFrame(columns=["input statement", "STL"])
p['input statement']=pandas.Series(literal_translations)
p['STL']=pandas.Series(samples)

p.to_csv(f'../csv_inputs/prelim_input_sentences.csv', index=False)

