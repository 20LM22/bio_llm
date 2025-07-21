import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt
import pickle, sys
import pandas

translations = []
try:
    with open(f'../pkl/{sys.argv[0]}', 'rb') as f:
        translations = pickle.load(f)
        print(f'Loaded {file}')
    except Exception as e:
        print(e)

translations_sim = []
try:
    with open(f'../pkl/{sys.argv[1]}', 'rb') as f:
        translations_sim = pickle.load(f)
        print(f'Loaded {file}')
    except Exception as e:
        print(e)

final_sentence = {}
try:
    with open(f'../pkl/{sys.argv[2]}', 'rb') as f:
        final_sentence = pickle.load(f)
        print(f'Loaded {file}')
    except Exception as e:
        print(e)

per_sentence_success_rate_table = pandas.DataFrame(columns=['Input Sentence', 'STL Extraction Success Rate', 'STL Parsing Success Rate', 'Literal Translation Success Rate'])
per_sentence_success_rate_table['Input Sentence'] = translations['input sentence']
per_sentence_success_rate_table['STL Extraction Success Rate'] = 0
per_sentence_success_rate_table['STL Parsing Success Rate'] = 0
per_sentence_success_rate_table['Literal Translation Success Rate'] = 0

total_sentences_success_rate_table = pandas.DataFrame(columns=['Input Sentence', 'STL Extraction Success Rate', 'STL Parsing Success Rate', 'Literal Translation Success Rate'])
total_sentences_success_rate_table['Input Sentence'] = translations['input sentence']
total_sentences_success_rate_table['STL Extraction Success Rate'] = 0
total_sentences_success_rate_table['STL Parsing Success Rate'] = 0
total_sentences_success_rate_table['Literal Translation Success Rate'] = 0

# count number of translations
num_translations = 0
for col in df.columns:
    if 'STL-' in col:
        num_translations += 1

for i in range(num_translations): # aggregate over all n columns
    col_name = 'STL-' + str(i)
    literal_col_name = 'Literal-' + str(i)

    per_sentence_success_rate_table['STL Extraction Success Rate'] = translations[col_name].apply(
            lambda x: per_sentence_success_rate_table['STL Extraction Success Rate']+1 if x == 'STL could not be extracted' else per_sentence_success_rate_table['STL Extraction Success Rate'] )

    per_sentence_success_rate_table['STL Parsing Success Rate'] = translations[col_name].apply(
            lambda x: per_sentence_success_rate_table['STL Parsing Success Rate']+1 if x == 'STL could not be parsed' else per_sentence_success_rate_table['STL Parsing Success Rate'] )

    per_sentence_success_rate_table['Literal Translation Success Rate'] = translations[literal_col_name].apply(
            lambda x: per_sentence_success_rate_table['Literal Translation Success Rate']+1 if x == 'STL to literal failed' else per_sentence_success_rate_table['Literal Translation Success Rate'] )

total_sentences_success_rate_table['STL Extraction Success Rate'] = per_sentence_success_rate_table['STL Extraction Success Rate'].sum()
total_sentences_success_rate_table['STL Parsing Success Rate'] = per_sentence_success_rate_table['STL Parsing Success Rate'].sum()
total_sentences_success_rate_table['Literal Translation Success Rate'] = per_sentence_success_rate_table['Literal Translation Success Rate'].sum()

num_passed_extraction = np.zeroes(translations.shape[0])
num_passed_extraction = num_translations - per_sentence_success_rate_table['STL Extraction Success Rate']
num_passed_parsing = np.zeroes(translations.shape[0])
num_passed_parsing = num_passed_extraction - per_sentence_success_rate_table['STL Parsing Success Rate']

num_total_translations = translations.shape[0] * num_translations
num_total_passed_extraction = num_total_translations - per_sentence_success_rate_table['STL Extraction Success Rate'].sum()
num_total_passed_parsing = num_total_passed_extraction - per_sentence_success_rate_table['STL Parsing Success Rate'].sum()

per_sentence_success_rate_table['STL Extraction Success Rate'] = per_sentence_success_rate_table['STL Extraction Success Rate'] / num_translations
per_sentence_success_rate_table['STL Parsing Success Rate'] = per_sentence_success_rate_table['STL Parsing Success Rate'] / num_passed_extraction
per_sentence_success_rate_table['Literal Translation Success Rate'] = per_sentence_success_rate_table['Literal Translation Success Rate'] / num_passed_parsing

per_sentence_success_rate_table['STL Extraction Success Rate'] = 1 - per_sentence_success_rate_table['STL Extraction Success Rate']
per_sentence_success_rate_table['STL Parsing Success Rate'] = 1 - per_sentence_success_rate_table['STL Parsing Success Rate']
per_sentence_success_rate_table['Literal Translation Success Rate'] = 1 - per_sentence_success_rate_table['Literal Translation Success Rate'] 

total_sentences_success_rate_table['STL Extraction Success Rate'] = total_sentences_success_rate_table['STL Extraction Success Rate'] / num_total_translations
total_sentences_success_rate_table['STL Parsing Success Rate'] = total_sentences_success_rate_table['STL Parsing Success Rate'] / num_total_passed_extraction
total_sentences_success_rate_table['Literal Translation Success Rate'] = total_sentences_success_rate_table['Literal Translation Success Rate'] / num_total_passed_parsing

# can also pickle results later
print(per_sentence_success_rate_table)

# can also pickle/append to per_sentence table later
print(total_sentences_success_rate_table)

# Produce similarity heatmaps
# remove all columns from the table that don't correspond to actual translations


for _id, file in enumerate(filenames):

  sim_arr = []
  nl_statements = [] # labels on the y-axis
  stl_statements = [] # labels on the x-axis
  A = [] # array of all stl embeddings 
  B = [] # array of all nl embeddings

  for _id, (key, value) in enumerate(results_dict.items()):
    # record the nl statement
    nl_statement = key[:10]
    num_stl = len(value['stl'])
    for i in range(num_stl): # for each STL statement
      # add the nl, stl statements for the axis labels
      nl_statements.append(f"{nl_statement}-{i+1}")
      stl_statements.append(f"{value['stl'][i][0][:10]}")
      A.append(value['stl'][i][1]) # stl embedding
      B.append(value['embedding']) # nl embedding

  # compute similarity matrix
  sim_matrix = cosine_similarity(np.array(A), np.array(B))

  # export heatmap
  plt.figure(figsize=(10,10))
  ax = sns.heatmap(sim_matrix, annot=True, vmin=0, vmax=1)
  plt.title(f'NL vs. STL Cosine Similarities\nModel:{file}')
  ax.set_yticklabels(nl_statements, rotation=0)
  ax.set_xticklabels(stl_statements, rotation=45)
  plt.savefig(f'../images/{file[14:-4]}_images/ambiguous_mod_nl_vs_stl_{file[14:-4]}.png')
