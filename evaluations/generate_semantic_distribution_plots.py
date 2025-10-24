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
time = sys.argv[3]
set_name = params['set_name']

res = {}
try:
    with open(f'../pkl/{set_name}_semantic_labels_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl', 'rb') as f:
        res = pickle.load(f)
        print(f'Loaded distribution')
except Exception as e:
    print(e)

sentence_results = []
for _id, sentence in enumerate(res.keys()): # key is sentence
    zeroes = []  # list of sim values
    ones = []
    ones_and_zeroes = []

    for stl, sim, choice in res[sentence]:
        ones_and_zeroes.append(sim)
        try:
            if choice == "":
                raise Exception()
            if int(choice) == 1:
                ones.append(sim)
            elif int(choice) == 0:
                zeroes.append(sim)
        except Exception as e:
            zeroes.append(sim)

    if len(ones_and_zeroes) <= 0:
        continue
    median = np.median(ones_and_zeroes)
    mean = np.average(ones_and_zeroes)
    sentence_result = [sentence, median, mean]
    sentence_results.append(sentence_result)

df = pandas.DataFrame(sentence_results, columns=["Sentence", "Median", "Mean"])
sorted_df = df.sort_values(by='Median')

# take rows 1-3 and put them into low, take rows length-3 to length-1 and put them into high
# get the sentence names and put them into an array
top_sentences = sorted_df['Sentence'].tail(3).to_numpy()
bottom_sentences = sorted_df['Sentence'].head(3).to_numpy()


zeroes_top = [] # list of sim values
ones_top = []
ones_and_zeroes_top = []

zeroes_bottom = [] # list of sim values
ones_bottom = []
ones_and_zeroes_bottom = []

for _id, sentence in enumerate(res.keys()): # key is sentence
    if sentence not in top_sentences and sentence not in bottom_sentences:
        continue

    for stl, sim, choice in res[sentence]:
        if sentence in top_sentences:
            ones_and_zeroes_top.append(sim)
        elif sentence in bottom_sentences:
            ones_and_zeroes_bottom.append(sim)
        else:
            continue

        try:
            if choice == "":
                raise Exception()
            if int(choice) == 1:
                if sentence in top_sentences:
                    ones_top.append(sim)
                elif sentence in bottom_sentences:
                    ones_bottom.append(sim)
            elif int(choice) == 0:
                if sentence in top_sentences:
                    zeroes_top.append(sim)
                elif sentence in bottom_sentences:
                    zeroes_bottom.append(sim)
        except Exception as e:
            if sentence in top_sentences:
                zeroes_top.append(sim)
            elif sentence in bottom_sentences:
                zeroes_bottom.append(sim)

# Top histogram
plt.rcParams['font.size'] = 14
plt.rcParams['axes.titlesize'] = 10

max_sim = np.max(ones_and_zeroes_top)
min_sim = np.min(ones_and_zeroes_top)

bins = np.linspace(min_sim, max_sim, 10)
plt.figure(figsize=(10,6))
plt.hist(ones_top, bins=bins, alpha=0.5, color='forestgreen', edgecolor='black')
plt.hist(zeroes_top, bins=bins, alpha=0.5, color='firebrick', edgecolor='black')
if len(ones_and_zeroes_top) > 0:
    plt.axvline(np.average(ones_and_zeroes_top), color='blue', linestyle='dashed', linewidth=1)
    plt.axvline(np.median(ones_and_zeroes_top), color='orange', linestyle='dashed', linewidth=1)
    plt.axvline(np.percentile(ones_and_zeroes_top,80), color='purple', linestyle='dashed', linewidth=1)

top_median = np.median(ones_and_zeroes_top)

plt.xlabel('Similarity', fontsize=22)
plt.ylabel('Frequency', fontsize=22)
plt.ylim(0, 15) # 15
plt.tick_params(axis='both', which='major', labelsize=22)
plt.title(f'Top Sentences Semantic Pass/Fail Distribution\nmodel: {model_name}\nnx: {syntax_count}, ny: {semantic_count}, nz: {shot_count}, median: {top_median}\n')
plt.savefig(f'../images/{model_name}/{set_name}_top_histogram_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pdf')
plt.close()

# Bottom histogram
max_sim = np.max(ones_and_zeroes_bottom)
min_sim = np.min(ones_and_zeroes_bottom)

bins = np.linspace(min_sim, max_sim, 10)
plt.figure(figsize=(10,6.5))
plt.hist(ones_bottom, bins=bins, alpha=0.5, color='forestgreen', edgecolor='black')
plt.hist(zeroes_bottom, bins=bins, alpha=0.5, color='firebrick', edgecolor='black')
if len(ones_and_zeroes_bottom) > 0:
    plt.axvline(np.average(ones_and_zeroes_bottom), color='blue', linestyle='dashed', linewidth=1)
    plt.axvline(np.median(ones_and_zeroes_bottom), color='orange', linestyle='dashed', linewidth=1)
    plt.axvline(np.percentile(ones_and_zeroes_bottom,80), color='purple', linestyle='dashed', linewidth=1)

bottom_median = np.median(ones_and_zeroes_bottom)

plt.xlabel('Similarity', fontsize=22)
plt.ylabel('Frequency', fontsize=22)
plt.ylim(0, 15) # 15
plt.tick_params(axis='both', which='major', labelsize=22)
plt.title(f'Bottom Sentences Semantic Pass/Fail Distribution\nmodel: {model_name}\nnx: {syntax_count}, ny: {semantic_count}, nz: {shot_count}, median: {bottom_median}\n')
plt.savefig(f'../images/{model_name}/{set_name}_bottom_histogram_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pdf')
plt.close()

# #----------------------------------------------------------------------------------------------
# # # do them as sentences
# sentences = []
# median_sim = []
# mean_sim = []
# variance_sim = []
# # top_sim_is_correct = []
# num_syntax_correct = [] # number of semantically correct translations for this sentence
# #
# for _id, sentence in enumerate(res.keys()): # key is sentence
#     zeroes = []
#     ones = []
#     sim_arr = []
#     sentences.append(sentence)
#
#     max_sim = 0
#     min_sim = 0
#     max_choice = None
#     max_stl = None
#     first_time_max = first_time_min = True
#     for stl, sim in res[sentence]:
#     # for stl, sim, choice in res[sentence]: # TODO: uncomment when annotations ready
#         sim_arr.append(sim)
#         if first_time_max or sim > max_sim:
#             max_sim = sim
#             # max_choice = choice # TODO uncomment when annotations ready
#             first_time_max = False
#         if first_time_min or sim < min_sim:
#             min_sim = sim
#             first_time_min = False
#
#         # TODO uncomment when annotations ready
#         # if choice is None or choice == '':
#         #     continue
#         # elif int(choice) == 0:
#         #     zeroes.append(sim)
#         # elif int(choice) == 1:
#         #     ones.append(sim)
#         # else:
#         #     raise Exception(f'no valid value associated with {stl}')
#
#     # process the sim_arr
#     if len(sim_arr) > 0:
#         median_sim.append(np.median(sim_arr))
#         mean_sim.append(np.average(sim_arr))
#         variance_sim.append(np.var(sim_arr))
#     else:
#         median_sim.append(None)
#         mean_sim.append(None)
#         variance_sim.append(None)
#
#     num_syntax_correct.append(len(res[sentence]))
#
#     # TODO uncomment when annotations ready
#     # process choice that corresponded to top sim. stl
#     # print(type(max_choice))
#     # if max_choice is None or max_choice == '':
#     #     # print('none')
#     #     top_sim_is_correct.append('N/A')
#     # elif int(max_choice) == 0: # then the max sim. stl is not considered to actually be good
#     #     # print('zero')
#     #     top_sim_is_correct.append(0)
#     # elif int(max_choice) == 1:
#     #     # print('one')
#     #     top_sim_is_correct.append(1)
#     # else:
#     #     raise Exception(f'problem with max choice: {e}')
# #
# #     # TODO uncomment when annotations ready
# #     plt.rcParams['font.size'] = 14
# #     plt.rcParams['axes.titlesize'] = 10
# #     bins = np.linspace(min_sim, max_sim, 10) # try 11 instead of 10, gnu-plot
# #     plt.figure(figsize=(10, 8))
# #     plt.hist(ones, bins=bins, alpha=0.5, color='forestgreen', edgecolor='black')
# #     plt.hist(zeroes, bins=bins, alpha=0.5, color='firebrick', edgecolor='black')
# #     # print(f'len(sim_arr): {len(sim_arr)}')
# #     if len(sim_arr) > 0:
# #         plt.axvline(np.average(sim_arr), color='blue', linestyle='dashed', linewidth=1)
# #         plt.axvline(np.median(sim_arr), color='orange', linestyle='dashed', linewidth=1)
# #         plt.axvline(np.percentile(sim_arr,80), color='purple', linestyle='dashed', linewidth=1)
# #
# #     plt.xlabel('Similarity')
# #     plt.ylabel('Frequency')
# #     plt.ylim(0, 30)
# #     if len(sentence) >= 100:
# #         m = sentence[:99]
# #     else:
# #         m = sentence
# #     plt.title(f'Hi/Lo Semantic Pass/Fail Distribution\nsentence: {m}\nmodel: {model_name}\nshots: {shot_count}, syntax: {syntax_count}, semantic: {semantic_count}\n')
# #
# #     plt.savefig(f'../images/{model_name}/updated_high_bottom_histogram_distribution_sentence_{sentence[:15]}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}.pdf')
# #     plt.close()
# #
# df = pandas.DataFrame(data={
#     'Sentence' : sentences,
#     'Median Similarity' : median_sim,
#     'Mean Similarity' : mean_sim,
#     'Variance Similarity' : variance_sim,
#     # 'Top Similarity Result Is Correct?' : top_sim_is_correct,
#     'Number Translations Syntactically Correct' : num_syntax_correct,
# })
# #
# # # now convert the "top sim is correct" to a dataframe
# # # top_sim_is_correct_all_sentences = pandas.DataFrame(data=top_sim_is_correct_all_sentences, columns=['Sentence', 'Top Sim. is Correct'])
# # # top_sim_is_correct_all_sentences.loc['Total'] = top_sim_is_correct_all_sentences.apply(pandas.to_numeric, errors='coerce')['Top Sim. is Correct'].sum()
# # # top_sim_is_correct_all_sentences.to_csv(f'../stats/{model_name}/top_sim_is_correct_all_sentences_shots_{shot_count}_syntax_{syntax_count}_semantic_{semantic_count}.csv')
# df.to_csv(f'../stats/{model_name}/qd_redo_all_test_set_stats_v2_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}.csv')
