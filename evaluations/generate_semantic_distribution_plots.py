import numpy as np
import pickle, sys, json
import matplotlib.pyplot as plt
import pandas

model_name = sys.argv[1]

# Load config specified by the script
with open(f'../config/{sys.argv[2]}') as f:
    params = json.load(f)

shot_count = params['num_shots_per_input_sentence']
syntax_count = params['num_correction_attempts_per_shot']
semantic_count = params['num_semantic_checks']

res = {}
try:
    with open(f'../pkl/{model_name}/histogram_distribution_comparison_{model_name}_shots_{shot_count}_syntax_{syntax_count}_semantic_{semantic_count}.pkl', 'rb') as f:
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
plt.figure(figsize=(10,6))
plt.hist(ones, bins=bins, alpha=0.5, label='Semantically correct', color='forestgreen', edgecolor='black')
plt.hist(zeroes, bins=bins, alpha=0.5, label='Semantically incorrect', color='firebrick', edgecolor='black')

plt.xlabel('Similarity')
plt.ylabel('Frequency')
plt.ylim(0, 50)
plt.title(f'All Sentences Semantic Pass/Fail Distribution\nmodel: {model_name}\nshots: {shot_count}, syntax: {syntax_count}, semantic: {semantic_count}')
plt.legend()

plt.savefig(f'../images/{model_name}/histogram_distribution_comparison_shots_{shot_count}_syntax_{syntax_count}_semantic_{semantic_count}.png')
plt.close()

# do them as sentences
sentences = []
median_sim = []
mean_sim = []
variance_sim = []
top_sim_is_correct = []
num_syntax_correct = [] # number of semantically correct translations for this sentence
category = [
    'medium',
    'easy',
    'easy',
    'medium',
    'hard',
    'medium',
    'hard',
    'hard'
] # can be filled out ahead of time

for _id, sentence in enumerate(res.keys()): # key is sentence
    zeroes = []
    ones = []
    sim_arr = []
    sentences.append(sentence)

    max_sim = 0
    min_sim = 0
    max_choice = None
    max_stl = None
    first_time_max = first_time_min = True
    for stl, sim, choice in res[sentence]:
        sim_arr.append(sim)
        if first_time_max or sim > max_sim:
            max_sim = sim
            max_choice = choice
            first_time_max = False
        if first_time_min or sim < min_sim:
            min_sim = sim
            first_time_min = False

        if choice is None or choice == '':
            continue
        elif int(choice) == 0:
            zeroes.append(sim)
        elif int(choice) == 1:
            ones.append(sim)
        else:
            raise Exception(f'no valid value associated with {stl}')

    # process the sim_arr
    if len(sim_arr) > 0:
        median_sim.append(np.median(sim_arr))
        mean_sim.append(np.average(sim_arr))
        variance_sim.append(np.var(sim_arr))
    else:
        median_sim.append(None)
        mean_sim.append(None)
        variance_sim.append(None)

    num_syntax_correct.append(len(res[sentence]))

    # process choice that corresponded to top sim. stl
    # print(type(max_choice))
    if max_choice is None or max_choice == '':
        # print('none')
        top_sim_is_correct.append('N/A')
    elif int(max_choice) == 0: # then the max sim. stl is not considered to actually be good
        # print('zero')
        top_sim_is_correct.append(0)
    elif int(max_choice) == 1:
        # print('one')
        top_sim_is_correct.append(1)
    else:
        raise Exception(f'problem with max choice: {e}')

    bins = np.linspace(min_sim, max_sim, 10) # try 11 instead of 10, gnu-plot
    plt.figure(figsize=(10, 8))
    plt.hist(ones, bins=bins, alpha=0.5, label='Semantically correct', color='forestgreen', edgecolor='black')
    plt.hist(zeroes, bins=bins, alpha=0.5, label='Semantically incorrect', color='firebrick', edgecolor='black')

    plt.xlabel('Similarity')
    plt.ylabel('Frequency')
    plt.ylim(0, 15)
    if len(sentence) >= 100:
        m = sentence[:99]
    else:
        m = sentence
    plt.title(f'Semantic Pass/Fail Distribution\nsentence: {m}\nmodel: {model_name}\nshots: {shot_count}, syntax: {syntax_count}, semantic: {semantic_count}')
    plt.legend()
    plt.savefig(f'../images/{model_name}/new_histogram_distribution_sentence_{sentence[0:15]}_shots_{shot_count}_syntax_{syntax_count}_semantic_{semantic_count}.png')
    plt.close()

df = pandas.DataFrame(data={
    'Sentence' : sentences,
    'Median Similarity' : median_sim,
    'Mean Similarity' : mean_sim,
    'Variance Similarity' : variance_sim,
    'Top Similarity Result Is Correct?' : top_sim_is_correct,
    'Number Translations Syntactically Correct' : num_syntax_correct,
    'Category' : category
})

# now convert the "top sim is correct" to a dataframe
# top_sim_is_correct_all_sentences = pandas.DataFrame(data=top_sim_is_correct_all_sentences, columns=['Sentence', 'Top Sim. is Correct'])
# top_sim_is_correct_all_sentences.loc['Total'] = top_sim_is_correct_all_sentences.apply(pandas.to_numeric, errors='coerce')['Top Sim. is Correct'].sum()
# top_sim_is_correct_all_sentences.to_csv(f'../stats/{model_name}/top_sim_is_correct_all_sentences_shots_{shot_count}_syntax_{syntax_count}_semantic_{semantic_count}.csv')
df.to_csv(f'../stats/{model_name}/stats_v2_shots_{shot_count}_syntax_{syntax_count}_semantic_{semantic_count}.csv')
