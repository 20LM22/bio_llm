import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt
import pickle

# Generates 1 16x16 Literal vs. STL heatmap for all pkl files (<filename>) included in 'filenames'
# Saves heatmaps as 'ambiguous_mod_literal_vs_stl_<filename>' in ../images/<filename>_images/literal_vs_stl_<filename>.png

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
  stl_statements = [] # labels on the y-axis
  literal_statements = [] # labels on the x-axis
  A = [] # array of all literal embeddings 
  B = [] # array of all stl embeddings

  for _id, (key, value) in enumerate(results_dict.items()):
    # record the nl statement
    num_stl = len(value['stl'])
    for i in range(num_stl): # for each STL statement
      # add the stl, literal statements for the axis labels
      stl_statements.append(f"{value['stl'][i][0][:10]}")
      literal_statements.append(f"{value['literal'][i][0][:10]}")
      A.append(value['literal'][i][1])
      B.append(value['stl'][i][1])

  # compute similarity matrix
  sim_matrix = cosine_similarity(np.array(A), np.array(B))

  # export heatmap
  plt.figure(figsize=(10,10))
  ax = sns.heatmap(sim_matrix, annot=True)
  plt.title(f'Literal vs. STL Cosine Similarities\nModel:{file}')
  ax.set_yticklabels(stl_statements, rotation=0)
  ax.set_xticklabels(literal_statements, rotation=45)
  plt.savefig(f'../images/{file[:-4]}_images/ambiguous_mod_literal_vs_stl_{file[:-4]}.png')