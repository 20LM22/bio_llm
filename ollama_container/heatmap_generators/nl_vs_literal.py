import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt
import pickle

# Generates 1 16x16 NL vs. Literal heatmap for all pkl files (<filename>) included in 'filenames'
# Saves heatmaps as 'ambiguous_mod_nl_vs_literal_<filename>' in ../images/<filename>_images/nl_vs_literal_<filename>.png

filenames = ['ollama_nomic_v2.pkl', 'st_mini_lm_v3.pkl', 'st_qwen_p6_v2.pkl'] # specify pkl files

for file in filenames:

  # load the data
  results_dict = {}
  try:
    with open(filename, 'rb') as file:
      results_dict = pickle.load(f'pkl/{file}')
      print(f'Loaded {file}')
  except Exception as e:
    print(e)

  sim_arr = []
  nl_statements = [] # labels on the y-axis
  literal_statements = [] # labels on the x-axis
  A = [] # array of all literal embeddings 
  B = [] # array of all nl embeddings

  for _id, (key, value) in enumerate(results_dict.items()):
    # record the nl statement
    nl_statement = key[:10]
    num_stl = len(value['stl'])
    for i in range(num_stl): # for each STL statement
      # add the nl, literal statements for the axis labels
      nl_statements.append(f"{nl_statement}-{i+1}")
      literal_statements.append(f"{value['literal'][i][0][:10]}")
      A.append(value['literal'][i][1]) # literal embedding
      B.append(value['embedding']) # nl embedding

  # compute similarity matrix
  sim_matrix = cosine_similarity(np.array(A), np.array(B))

  # export heatmap
  plt.figure(figsize=(10,10))
  ax = sns.heatmap(sim_matrix, annot=True, vmin=0, vmax=1)
  plt.title(f'NL vs. Literal Cosine Similarities\nModel:{file}')
  ax.set_yticklabels(nl_statements, rotation=0)
  ax.set_xticklabels(literal_statements, rotation=45)
  plt.savefig(f'../images/{file[:-4]}_images/ambiguous_mod_nl_vs_literal_{file[:-4]}.png')