import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt
import pickle, sys
import pandas
from thefuzz import fuzz
from sentence_transformers import SentenceTransformer
from matplotlib.patches import Rectangle

embedding_model_name = 'all-MiniLM-L6-v2'
embedding_model = SentenceTransformer(embedding_model_name, device='cpu')

try:
    with open(f'../pkl/{sys.argv[1]}', 'rb') as f:
        translations = pickle.load(f)
        print(f'Loaded {f}')
except Exception as e:
    print("there was an exception")
    print(e)

try:
    with open(f'../pkl/{sys.argv[2]}', 'rb') as f:
        final_sentence = pickle.load(f)
        print(f'Loaded {f}')
except Exception as e:
    print(e)

per_sentence_success_rate_table = pandas.DataFrame(columns=['Input Sentence', 'STL Extraction Success Rate', 'STL Parsing Success Rate', 'Literal Translation Success Rate'])
per_sentence_success_rate_table['Input Sentence'] = translations['input statement']
per_sentence_success_rate_table['STL Extraction Success Rate'] = 0
per_sentence_success_rate_table['STL Parsing Success Rate'] = 0
per_sentence_success_rate_table['Literal Translation Success Rate'] = 0

total_sentences_success_rate_table = pandas.DataFrame(index=[0])
total_sentences_success_rate_table['Input Sentence'] = 'Overall'

# count number of translations
num_translations = 0
for col in translations.columns:
    if 'STL-' in col:
        num_translations += 1

for i in range(num_translations): # aggregate over all n columns
    col_name = 'STL-' + str(i)
    literal_col_name = 'Literal-' + str(i)

    per_sentence_success_rate_table['STL Extraction Success Rate'] += np.where(translations[col_name] == 'STL could not be extracted', 1, 0)
    per_sentence_success_rate_table['STL Parsing Success Rate'] += np.where(translations[col_name] == 'STL could not be parsed', 1, 0)
    per_sentence_success_rate_table['Literal Translation Success Rate'] += np.where(translations[literal_col_name] == 'STL to literal failed', 1, 0)

total_sentences_success_rate_table['STL Extraction Success Rate'] = per_sentence_success_rate_table['STL Extraction Success Rate'].sum()
total_sentences_success_rate_table['STL Parsing Success Rate'] = per_sentence_success_rate_table['STL Parsing Success Rate'].sum()
total_sentences_success_rate_table['Literal Translation Success Rate'] = per_sentence_success_rate_table['Literal Translation Success Rate'].sum()

num_passed_extraction = np.zeros(translations.shape[0])
num_passed_extraction = num_translations - per_sentence_success_rate_table['STL Extraction Success Rate']
num_passed_parsing = np.zeros(translations.shape[0])
num_passed_parsing = num_passed_extraction - per_sentence_success_rate_table['STL Parsing Success Rate']

num_total_translations = translations.shape[0] * num_translations
num_total_passed_extraction = num_total_translations - per_sentence_success_rate_table['STL Extraction Success Rate'].sum()
num_total_passed_parsing = num_total_passed_extraction - per_sentence_success_rate_table['STL Parsing Success Rate'].sum()

per_sentence_success_rate_table['STL Extraction Success Rate'] = np.where(num_translations==0, 0, 1-(per_sentence_success_rate_table['STL Extraction Success Rate'] / num_translations))
per_sentence_success_rate_table['STL Parsing Success Rate'] = np.where(num_passed_extraction==0, 0, 1-(per_sentence_success_rate_table['STL Parsing Success Rate'] / num_passed_extraction))
per_sentence_success_rate_table['Literal Translation Success Rate'] = np.where(num_passed_parsing==0, 0, 1-(per_sentence_success_rate_table['Literal Translation Success Rate'] / num_passed_parsing))

total_sentences_success_rate_table['STL Extraction Success Rate'] = np.where(num_total_translations==0, 0, 1-(total_sentences_success_rate_table['STL Extraction Success Rate'] / num_total_translations))
total_sentences_success_rate_table['STL Parsing Success Rate'] = np.where(num_total_passed_extraction==0, 0, 1-(total_sentences_success_rate_table['STL Parsing Success Rate'] / num_total_passed_extraction))
total_sentences_success_rate_table['Literal Translation Success Rate'] = np.where(num_total_passed_parsing==0, 0, 1-(total_sentences_success_rate_table['Literal Translation Success Rate'] / num_total_passed_parsing))

translations.to_csv('mmm.csv')

stats = pandas.concat([per_sentence_success_rate_table, total_sentences_success_rate_table], ignore_index=True)
print(stats)
stats.to_csv('stats.csv', index=False)

# Produce similarity heatmaps

# remove all columns from the table that don't correspond to actual translations
nl_sentence_embeddings = embedding_model.encode(translations['input statement'], normalize_embeddings=True)
literal_sentence_embeddings = embedding_model.encode(translations.filter(regex='Literal-').copy().to_numpy().flatten(), normalize_embeddings=True)

nl_sentences = np.array(translations['input statement'].str[:10])

literal_sentences = translations.filter(regex='Literal-').copy()
for col in literal_sentences.columns:
    literal_sentences[col] = np.where((pandas.isna(literal_sentences[col])) | (literal_sentences[col]=='Literal could not be generated') | (literal_sentences[col]=='STL to literal failed'), literal_sentences[col], "S-" + translations['input statement'].str[:10] + "-A-" + str(col.split('-')[1]))
literal_sentences = literal_sentences.to_numpy().flatten()

indices_to_remove = []
for _id,l in enumerate(literal_sentences):
    if l=='Literal could not be generated' or l=='STL to literal failed' or l==None:
        indices_to_remove.append(_id)
literal_sentences_clean = [x for x in literal_sentences if x != "Literal could not be generated" and x != 'STL to literal failed' and x != None ]
literal_sentence_embeddings_clean = [x for _id, x in enumerate(literal_sentence_embeddings) if _id not in indices_to_remove ]

# compute similarity matrix
sim_matrix = cosine_similarity(np.array(nl_sentence_embeddings), np.array(literal_sentence_embeddings_clean))

# export heatmap
plt.figure(figsize=(30,10))
ax = sns.heatmap(sim_matrix, annot=True, vmin=0, vmax=1)

# NEW BORDER AROUND HEATMAP
# ax.add_patch(Rectangle((3,4), 1,1,fill=False, edgecolor='blue', lw=3))

plt.title(f'Produced Literal STL vs. Original NL Cosine Similarity\nModel:Put model here')
ax.set_xticks(range(len(literal_sentences_clean)))
ax.set_yticklabels(nl_sentences, rotation=0)
ax.set_xticklabels(literal_sentences_clean, rotation=45)
plt.tight_layout()
plt.savefig(f'../images/produced_literal_vs_original_nl_test.png')

# compute similarity for the stl against the reference stl using fuzzy matching
stl_ref_statements = np.array(translations['reference STL'].str[:20]) # need to fix these names
stl_produced_statements = translations.filter(regex='STL-').copy()
for col in stl_produced_statements.columns:
    stl_produced_statements[col] = np.where((stl_produced_statements[col]=='STL could not be extracted') | (stl_produced_statements[col]=='STL could not be parsed'), stl_produced_statements[col], "STL-'" + translations['reference STL'].str[:10] + "'-A-" + str(col.split('-')[1]))
stl_produced_statements = stl_produced_statements.to_numpy().flatten()
stl_produced_clean_labels = [x for x in stl_produced_statements if x != "STL could not be extracted" and x != 'STL could not be parsed' ]

reference_stl = translations['reference STL']
produced_stl_subset = [x for x in translations.filter(regex='STL-').copy().to_numpy().flatten() if x != 'STL could not be extracted' and x != 'STL could not be parsed']
fuzz_matrix = np.zeros((reference_stl.shape[0], len(produced_stl_subset)))

print("--------------------------------------------------------------------------------------------")
print(f'stl ref statements: {reference_stl}')
print("--------------------------------------------------------------------------------------------")
print(reference_stl.shape)
print("--------------------------------------------------------------------------------------------")
print(f'stl produced statements: {produced_stl_subset}')
print("--------------------------------------------------------------------------------------------")
print(len(produced_stl_subset))
print("--------------------------------------------------------------------------------------------")
print(f'fuzz: {fuzz_matrix}')
print("--------------------------------------------------------------------------------------------")
print(fuzz_matrix.shape)
print("--------------------------------------------------------------------------------------------")

for i in range(fuzz_matrix.shape[0]):
    for j in range(fuzz_matrix.shape[1]):
        fuzz_matrix[i][j] = fuzz.ratio(produced_stl_subset[j], reference_stl[i])

fuzz_matrix = fuzz_matrix/100

# heatmap
plt.figure(figsize=(30,10))
ax = sns.heatmap(fuzz_matrix, annot=True, vmin=0, vmax=1)
plt.title(f'Produced STL vs. Reference STL Similarity\nModel:Test')
ax.set_xticks(range(len(stl_produced_statements)))
ax.set_yticklabels(stl_ref_statements, rotation=0)
ax.set_xticklabels(stl_produced_statements, rotation=45)
plt.tight_layout()
plt.savefig(f'../images/produced_vs_ref_stl_test.png')

"""
# final sentence comparison
final_stl = final_sentence['stl']
final_literal = final_sentence['literal']
corresponding_nl = translations[final_sentence['sentence_index'], 'input sentence']
corresponding_literal = translations[final_sentence['sentence_index'], 'Literal']
corresponding_stl = translation[final_sentence['sentence_index'], 'STL']
# compute sim between final literal and corresponding ground truth literal
literal_sim = cosine_similarity(np.array(embedding_model.encode(final_literal, normalize_embeddings=True)), np.array(embedding_model.encode(corresponding_literal, normalize_embeddings=True)))
# compute sim between final STL and corresponding ground truth STL
stl_sim = fuzz.ratio(final_stl, corresponding_stl)/100

final_dict = {
    'produced stl': final_stl,
    'produced literal': final_literal,
    'original nl': corresponding_nl,
    'reference literal': corresponding_literal,
    'reference stl': corresponding_stl,
    'ref. literal vs. produced literal': literal_sim,
    'ref. stl vs. produced stl': stl_sim
}
print(final_dict)
"""

