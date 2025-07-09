import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt
import pickle

# first load the data
filename = 'st_mini_lm_v3.pkl' # let's work with the ollama model first
results_dict = {}

try:
  with open(filename, "rb") as file:
    results_dict = pickle.load(file)
except Exception as e:
  print(e)

print("Loaded file")

# now we need to process the input in a way that's useful
# let's assume for now we only care about the first row
# what are we computing similarity between? the embedding and first stl

#     "nl": {
#       "embedding": embedding,
#       "stl": [(stl, embedding)],
#       "literal": [(literal, embedding)]
#     }

# in python, what's the best way to initialize things that you manipulate as local vars?
sim_arr = []
nl_statements = []

for _id, (key, value) in enumerate(results_dict.items()):
  # value = a dictionary
  # record the nl statement
  nl_statement = key[:10]
  # need to iterate however many times there are STL statements: len(value['stl'])
  num_stl = len(value['stl'])
  for i in range(num_stl): # for each STL statement
    # add the nl statement to the list for the heatmap title
    nl_statements.append(f"{nl_statement}-{i+1}")

    # value['stl'] = an array, value['stl'][0] = a tuple, value['stl'][0][1] = an element of a tuple
    # the 1 must stay the same, the 0 should be replaced by a variable
    A = np.array([value['embedding'], value['stl'][i][1], value['literal'][i][1]])

    # then add A to the sim_arr
    sim_arr.append(A)

sim_arr = np.array(sim_arr)

# print("Done computing sim arr")
# print(f"The sim arr has shape: {sim_arr.shape}\nThe sim arr is: {sim_arr}")

# once the vectors are loaded onto the axes, this gives us a 2d matrix of cosine sims
# need to produce an arr of matrices, one element per element in the sim_arr
sim_matrix_arr = []
for sim_arr_element in sim_arr:
  sim_matrix = cosine_similarity(sim_arr_element)
  sim_matrix_arr.append(sim_matrix)

sim_matrix_arr = np.array(sim_matrix_arr)
# print("Done computing sim matrices")
# print(f"The sim matrix arr has shape: {sim_matrix_arr.shape}\nThe sim matrix arr is: {sim_matrix_arr}")

# now make the plots
# fig, axs = plt.subplots(4, 4, figsize=(10,10)) # comment this back in once done with the poster

ax = sns.heatmap(sim_matrix_arr[0], annot=True, vmin=0, vmax=1)
ax.set_title(f"all-MiniLM-L6-v2")
# ax.set(xlabel='x-label', ylabel='y-label', title='sample-title')
ax.set_yticklabels(["NL", "STL", "Literal"], rotation=0)
ax.set_xticklabels(["NL", "STL", "Literal"], rotation=45)
# fig.tight_layout()
plt.savefig('mini_3x3_poster.png')
print(nl_statements[0])

# comment all of this back in once done with the poster
# for _id, ax in enumerate(axs.flat):
#   sns.heatmap(sim_matrix_arr[_id], ax=ax, annot=True)
#   ax.set_title(f"{nl_statements[_id]} Similarities")
#   # ax.set(xlabel='x-label', ylabel='y-label', title='sample-title')
#   ax.set_yticklabels(["NL", "STL", "Literal"], rotation=0)
#   ax.set_xticklabels(["NL", "STL", "Literal"], rotation=45)
# fig.tight_layout()
# plt.savefig('test_heatmap_st_qwen_p6_v2.png')

# results_dict = {
#     "nl": {
#       "embedding": embedding,
#       "stl": [(stl, embedding)],
#       "literal": [(literal, embedding)]
#     }
# }