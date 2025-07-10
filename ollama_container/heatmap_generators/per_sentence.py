import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt
import pickle

# Generates 16 3x3 per sentence heatmaps for all pkl files (<filename>) included in 'filenames'
# Saves heatmaps as 'ambiguous_mod_per_sentence_<filename>' in ../images/<filename>_images/per_sentence_<filename>.png

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

  sim_arr = [] # an array of arrays with NL, STL, literal vectors for each sentence triple
  nl_statements = [] # an array of corresponding NL statements to match to heatmap titles

  # load each sentence triple's NL, STL, literal vectors
  for _id, (key, value) in enumerate(results_dict.items()):
    # record the nl statement
    nl_statement = key[:10]
    num_stl = len(value['stl'])
    for i in range(num_stl): # for each STL statement
      # add the nl statement to the list for the heatmap title
      nl_statements.append(f"{nl_statement}-{i+1}")
      # value['stl'] = an array, value['stl'][0] = a tuple, value['stl'][0][1] = an element of a tuple
      A = np.array([value['embedding'], value['stl'][i][1], value['literal'][i][1]])
      sim_arr.append(A)
  sim_arr = np.array(sim_arr)

  # once the vectors are loaded onto the axes, this gives us a 2d matrix of cosine sims
  sim_matrix_arr = [] # an array of cosine similarity matrices, one for each sentence triple
  for sim_arr_element in sim_arr:
    sim_matrix = cosine_similarity(sim_arr_element)
    sim_matrix_arr.append(sim_matrix)
  sim_matrix_arr = np.array(sim_matrix_arr)

  # export 16 3x3 plots
  fig, axs = plt.subplots(4, 4, figsize=(10,10))

  for _id, ax in enumerate(axs.flat):
    sns.heatmap(sim_matrix_arr[_id], ax=ax, annot=True)
    ax.set_title(f'{nl_statements[_id]} Cosine Similarities\nModel:{file}')
    ax.set_yticklabels(["NL", "STL", "Literal"], rotation=0)
    ax.set_xticklabels(["NL", "STL", "Literal"], rotation=45)
  fig.tight_layout()
  plt.savefig(f'../images/{file[:-4]}_images/ambiguous_mod_per_sentence_{file[:-4]}.png')