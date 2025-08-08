import numpy as np
import pickle, sys, os, pandas
import matplotlib.pyplot as plt

model_name = 'DeepSeek-R1-Distill-Qwen-1.5B' if sys.argv[1] == 'deepseek' else 'Qwen3-1.7B'

res = {}
try:
    with open(f'../pkl/histogram_distribution_comparison_{model_name}.pkl', 'rb') as f:
        res = pickle.load(f)
        print(f'Loaded histogram distribution')
except Exception as e:
    print(e)

# do them all together
zeroes = [] # list of sim values
ones = []
for key in res.keys():
    for stl, sim, choice in res[key]:
        if choice is None or choice == '':
            continue
        elif int(choice) == 0:
            zeroes.append(sim)
        elif int(choice) == 1:
            ones.append(sim)
        else:
            raise Exception(f'no choice associated with {stl}')

# Plot histogram
# bins = np.linspace(min(res[sentence]), max(res[sentence]), 10)
bins = np.linspace(0, 1, 10) # change bin count if needed
plt.hist(ones, bins=bins, alpha=0.5, label='Semantically correct', color='forestgreen', edgecolor='black')
plt.hist(zeroes, bins=bins, alpha=0.5, label='Semantically incorrect', color='firebrick', edgecolor='black')

plt.xlabel('Similarity')
plt.ylabel('Frequency')
plt.ylim(0, 50)
plt.title(f'All Sentences Semantic Pass/Fail Distribution\nmodel: {model_name}')
plt.legend()

plt.savefig(f"../images/{model_name}/histogram_distribution_comparison.png")
    
# do them as sentences
fig, axs = plt.subplots(len(res.keys()), 1, figsize=(20,60)) # TODO: change fig size if needed
axs = np.atleast_1d(axs)

for _id, sentence in enumerate(res.keys()): # key is sentence
    zeroes = []
    ones = []
    
    max_sim = 0
    min_sim = 0
    first_time = True

    for stl, sim, choice in res[sentence]:
        if first_time or sim > max_sim:
            max_sim = sim
            first_time = False
        if first_time or sim < min_sim:
            min_sim = sim
            first_time = False

        if choice is None or choice == '':
            continue
        elif int(choice) == 0:
            zeroes.append(sim)
        elif int(choice) == 1:
            ones.append(sim)
        else:
            raise Exception(f'no choice associated with {stl}')

    bins = np.linspace(min_sim, max_sim, 10)

    axs[_id].hist(ones, bins=bins, alpha=0.5, label='Semantically correct', color='forestgreen', edgecolor='black')
    axs[_id].hist(zeroes, bins=bins, alpha=0.5, label='Semantically incorrect', color='firebrick', edgecolor='black')

    axs[_id].set_title(f'Semantic Pass/Fail Distribution\nsentence: {sentence}\nmodel: {model_name}')
    axs[_id].set_xlabel('Similarity')
    axs[_id].set_ylabel('Frequency')
    axs[_id].set_ylim(0,15)
    axs[_id].legend()

fig.tight_layout()
plt.savefig(f'../images/{model_name}/per_sentence_histogram_distribution_comparison.png')
