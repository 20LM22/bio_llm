import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import seaborn as sns
import matplotlib.pyplot as plt
import pickle

# first load the data
filename = 'st_qwen_p6_v2.pkl' # let's work with the ollama model first
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
nl_statements = [] # these will be labels on the y-axis now
literal_statements = [] # these will be labels on the x-axis
A = [] # all stl
B = [] # all nl

for _id, (key, value) in enumerate(results_dict.items()):
  # value = a dictionary
  # record the nl statement
  nl_statement = key[:10]
  # need to iterate however many times there are STL statements: len(value['stl'])
  num_stl = len(value['stl'])
  for i in range(num_stl): # for each STL statement
    # add the nl, stl statements for the axes
    nl_statements.append(f"{nl_statement}-{i+1}")
    literal_statements.append(f"{value['literal'][i][0][:10]}")

    # value['stl'] = an array, value['stl'][0] = a tuple, value['stl'][0][1] = an element of a tuple
    # the 1 must stay the same, the 0 should be replaced by a variable
    A.append(value['literal'][i][1])
    B.append(value['embedding'])

A = np.array(A)
B = np.array(B)
print("Done computing A, B")
print(f"The A arr has shape: {A.shape}\nThe A arr is: {A}")
print(f"The B arr has shape: {B.shape}\nThe B arr is: {B}")

# once the vectors are loaded onto the axes, this gives us a 2d matrix of cosine sims
# need to produce an arr of matrices, one element per element in the sim_arr
sim_matrix = cosine_similarity(A,B)

print("Done computing sim matrix")
print(f"The sim matrix has shape: {sim_matrix.shape}\nThe sim matrix is: {sim_matrix}")

# now make the plots
plt.figure(figsize=(10,10))
ax = sns.heatmap(sim_matrix, annot=True)
plt.title(f"NL vs. Literal Similarities")
# ax.set(xlabel='x-label', ylabel='y-label', title='sample-title')
ax.set_yticklabels(nl_statements, rotation=0)
ax.set_xticklabels(literal_statements, rotation=45)
plt.savefig('nl_vs_literal_st_qwen_p6_v2.png')

# results_dict = {
#     "nl": {
#       "embedding": embedding,
#       "stl": [(stl, embedding)],
#       "literal": [(literal, embedding)]
#     }
# }