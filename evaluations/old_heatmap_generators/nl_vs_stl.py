import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt
import pickle

# Generates 1 16x16 NL vs. STL heatmap for all pkl files (<filename>) included in 'filenames'
# Saves heatmaps as 'ambiguous_mod_nl_vs_stl_<filename>' in ../images/<filename>_images/nl_vs_stl_<filename>.png

filenames = ['ambiguous_mod_ollama_nomic_v2.pkl', 'ambiguous_mod_st_mini_lm_v2.pkl', 'ambiguous_mod_st_qwen_p6_v2.pkl'] # specify pkl files

for _id, file in enumerate(filenames):

  # load the data
  results_dict = {}
  try:
    with open(f'../pkl/{filenames[_id]}', 'rb') as f:
      results_dict = pickle.load(f)
      print(f'Loaded {file}')
  except Exception as e:
    print(e)

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
