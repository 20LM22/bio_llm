import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import pickle, sys, os, pandas
from sentence_transformers import SentenceTransformer
import json
from collections import defaultdict
from stl2literal import STL2literal
import matplotlib.pyplot as plt

# arg 1 is the model choice
# arg 2 is the all vs sentence choice

model_name = 'DeepSeek-R1-Distill-Qwen-1.5B' if int(sys.argv[1]) == 1 else 'Qwen3-1.7B'

res = {}
try:
    with open(f'../pkl/histogram_distribution_comparison_{model_name}.pkl', 'rb') as f:
        res = pickle.load(f)
        print(f'Loaded histogram distribution')
except Exception as e:
    print(e)

print(res)

if sys.argv[2] == 1: # do them all together
    zeroes = [] # list of sim values
    ones = []
    for key in res.keys():
        for stl, sim, choice in res[key]:
            if choice == 0:
                zeroes.append(sim)
            elif choice == 1:
                ones.append(sim)
            else:
                raise Exception(f'no choice associated with {stl}')
    
    # Plot histogram
    bins = np.linspace(0, 1, 10) # change bin count if needed
    plt.hist(ones, bins=bins, alpha=0.5, label='Semantically correct', color='forestgreen', edgecolor='black')
    plt.hist(zeroes, bins=bins, alpha=0.5, label='Semantically incorrect', color='firebrick', edgecolor='black')

    plt.xlabel('Similarity')
    plt.ylabel('Frequency')
    plt.title('All Sentences Semantic Pass/Fail Distribution\nmodel: {model_name}')
    plt.legend()

    plt.savefig("../images/{model_name}/histogram_distribution_comparison.png")
    
elif sys.argv[2] == 2: # do them as sentences
    fig, axs = plt.subplots(len(res.keys()), 1, figsize=(20,60)) # TODO: change fig size if needed
    axs = np.atleast_1d(axs)
    bins = np.linspace(0, 1, 10) # change bin count if needed

    for _id, sentence in enumerate(res.keys()): # key is sentence
        zeroes = []
        ones = []
        for stl, sim, choice in res[sentence]:
            if choice == 0:
                zeroes.append(sim)
            elif choice == 1:
                ones.append(sim)
            else:
                raise Exception(f'no choice associated with {stl}')
        axs[_id].hist(ones, bins=bins, alpha=0.5, label='Semantically correct', color='forestgreen', edgecolor='black')
        axs[_id].hist(zeroes, bins=bins, alpha=0.5, label='Semantically incorrect', color='firebrick', edgecolor='black')
            
        axs[_id].set_title(f'Semantic Pass/Fail Distribution\nsentence: {sentence}\nmodel: {model_name}')
        axs[_id].set_xlabel('Similarity')
        axs[_id].set_ylabel('Frequency')
        axs[_id].legend()
    
    fig.tight_layout()
    plt.savefig(f'../images/{model_name}/per_sentence_histogram_distribution_comparison.png')


