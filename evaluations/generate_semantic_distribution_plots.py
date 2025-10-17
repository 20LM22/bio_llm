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

res_top = {}
res_bottom = {}
res = {}
try:
    with open(f'../pkl/{set_name}_semantic_labels_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl', 'rb') as f:
        res = pickle.load(f)
        print(f'Loaded distribution')
    # with open(f'../pkl/{set_name}_top_3_histogram_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl', 'rb') as f:
    #     res_top = pickle.load(f)
    #     print(f'Loaded histogram distribution')
    # with open(f'../pkl/{set_name}_bottom_3_histogram_{model_name}_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl', 'rb') as f:
    #     res_bottom = pickle.load(f)
    #     print(f'Loaded histogram distribution')
except Exception as e:
    print(e)

# TODO: uncomment when you have annotations for top3/bottom3
# zeroes_top = [] # list of sim values
# ones_top = []
# ones_and_zeroes_top = []
#
# zeroes_bottom = [] # list of sim values
# ones_bottom = []
# ones_and_zeroes_bottom = []
#
# for key in res_top.keys():
#     for stl, sim, choice in res_top[key]:
#         ones_and_zeroes_top.append(sim)
#         if choice is None or choice == '':
#             continue
#         elif int(choice) == 0:
#             zeroes_top.append(sim)
#         elif int(choice) == 1:
#             ones_top.append(sim)
#         else:
#             raise Exception(f'no choice associated with {stl}')
#
# for key in res_bottom.keys():
#     for stl, sim, choice in res_bottom[key]:
#         ones_and_zeroes_bottom.append(sim)
#         if choice is None or choice == '':
#             continue
#         elif int(choice) == 0:
#             zeroes_bottom.append(sim)
#         elif int(choice) == 1:
#             ones_bottom.append(sim)
#         else:
#             raise Exception(f'no choice associated with {stl}')

for _id, sentence in enumerate(res.keys()): # key is sentence
    print(f'the sentence is: {sentence}')

    zeroes = []  # list of sim values
    ones = []
    ones_and_zeroes = []

    for stl, sim, choice in res[sentence]:
        ones_and_zeroes.append(sim)
        if choice is None or choice == '':
            continue
        elif int(choice) == 0:
            zeroes.append(sim)
        elif int(choice) == 1:
            ones.append(sim)
        else:
            raise Exception(f'no choice associated with {stl}')

    plt.rcParams['font.size'] = 14
    plt.rcParams['axes.titlesize'] = 10

    max_sim = 0
    min_sim = 0
    first_time_max = first_time_min = True
    for stl, sim, choice in res[sentence]:
        if first_time_max or sim > max_sim:
            max_sim = sim
            first_time_max = False
        if first_time_min or sim < min_sim:
            min_sim = sim
            first_time_min = False

    bins = np.linspace(min_sim, max_sim, 10)
    plt.figure(figsize=(10, 6))
    plt.hist(ones, bins=bins, alpha=0.5, color='forestgreen', edgecolor='black')
    plt.hist(zeroes, bins=bins, alpha=0.5, color='firebrick', edgecolor='black')
    if len(ones_and_zeroes) > 0:
        plt.axvline(np.average(ones_and_zeroes), color='blue', linestyle='dashed', linewidth=1)
        plt.axvline(np.median(ones_and_zeroes), color='orange', linestyle='dashed', linewidth=1)
        plt.axvline(np.percentile(ones_and_zeroes, 80), color='purple', linestyle='dashed', linewidth=1)

    median = np.median(ones_and_zeroes)

    plt.xlabel('Similarity')
    plt.ylabel('Frequency')
    plt.ylim(0, 12)
    plt.title(
        f'Hi/Lo Similarity Distribution with Semantic Correctness Labels\nmodel: {model_name}\nnx: {syntax_count}, ny: {semantic_count}, nz: {shot_count}, median: {median}\nsentence: {sentence[0:10]}')
    plt.savefig(
        f'../images/{model_name}/{set_name}_hi_lo_sentence_{sentence[0:10]}_histogram_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}.pdf')
    plt.close()

sentences = []
median_sim = []
mean_sim = []
variance_sim = []
num_syntax_correct = [] # number of semantically correct translations for this sentence

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
    # for stl, sim in res[sentence]:
    for stl, sim, choice in res[sentence]: # TODO: uncomment when annotations ready
        sim_arr.append(sim)
        if first_time_max or sim > max_sim:
            max_sim = sim
            max_choice = choice # TODO uncomment when annotations ready
            first_time_max = False
        if first_time_min or sim < min_sim:
            min_sim = sim
            first_time_min = False

        # TODO uncomment when annotations ready
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

     # TODO uncomment when annotations ready
    plt.rcParams['font.size'] = 14
    plt.rcParams['axes.titlesize'] = 10
    bins = np.linspace(min_sim, max_sim, 10) # try 11 instead of 10, gnu-plot
    plt.figure(figsize=(10, 8))
    plt.hist(ones, bins=bins, alpha=0.5, color='forestgreen', edgecolor='black')
    plt.hist(zeroes, bins=bins, alpha=0.5, color='firebrick', edgecolor='black')
    # print(f'len(sim_arr): {len(sim_arr)}')
    if len(sim_arr) > 0:
        plt.axvline(np.average(sim_arr), color='blue', linestyle='dashed', linewidth=1)
        plt.axvline(np.median(sim_arr), color='orange', linestyle='dashed', linewidth=1)
        plt.axvline(np.percentile(sim_arr,80), color='purple', linestyle='dashed', linewidth=1)

    plt.ylim(0, 30) # important to change
    if len(sentence) >= 100:
        m = sentence[:99]
    else:
        m = sentence

    plt.xlabel('Similarity')
    plt.ylabel('Frequency')
    plt.title(
        f'Hi/Lo Similarity Distribution with Semantic Correctness Labels\nmodel: {model_name}\nnx: {syntax_count}, ny: {semantic_count}, nz: {shot_count}, median: {median}\n')
    plt.savefig(
        f'../images/{model_name}/{set_name}_hi_lo_histogram_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pdf')
    plt.close()















# Top histogram
# plt.rcParams['font.size'] = 14
# plt.rcParams['axes.titlesize'] = 10
#
# max_sim = 0
# min_sim = 0
# first_time_max = first_time_min = True
# for key in res_top.keys():
#     for stl, sim, choice in res_top[key]:
#         if first_time_max or sim > max_sim:
#             max_sim = sim
#             first_time_max = False
#         if first_time_min or sim < min_sim:
#             min_sim = sim
#             first_time_min = False
#
# bins = np.linspace(min_sim, max_sim, 10)
# plt.figure(figsize=(10,6))
# plt.hist(ones_top, bins=bins, alpha=0.5, color='forestgreen', edgecolor='black')
# plt.hist(zeroes_top, bins=bins, alpha=0.5, color='firebrick', edgecolor='black')
# if len(ones_and_zeroes_top) > 0:
#     plt.axvline(np.average(ones_and_zeroes_top), color='blue', linestyle='dashed', linewidth=1)
#     plt.axvline(np.median(ones_and_zeroes_top), color='orange', linestyle='dashed', linewidth=1)
#     plt.axvline(np.percentile(ones_and_zeroes_top,80), color='purple', linestyle='dashed', linewidth=1)
#
# top_median = np.median(ones_and_zeroes_top)
#
# plt.xlabel('Similarity')
# plt.ylabel('Frequency')
# plt.ylim(0, 70)
# plt.title(f'Top Sentences Semantic Pass/Fail Distribution\nmodel: {model_name}\nnx: {syntax_count}, ny: {semantic_count}, nz: {shot_count}, median: {top_median}\n')
# plt.savefig(f'../images/{model_name}/{set_name}_top_histogram_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}.pdf')
# plt.close()
#
# # Bottom histogram
# plt.rcParams['font.size'] = 14
# plt.rcParams['axes.titlesize'] = 10
#
# max_sim = 0
# min_sim = 0
# first_time_max = first_time_min = True
# for key in res_bottom.keys():
#     for stl, sim, choice in res_bottom[key]:
#         if first_time_max or sim > max_sim:
#             max_sim = sim
#             first_time_max = False
#         if first_time_min or sim < min_sim:
#             min_sim = sim
#             first_time_min = False
#
# bins = np.linspace(min_sim, max_sim, 10)
# plt.figure(figsize=(10,6))
# plt.hist(ones_bottom, bins=bins, alpha=0.5, color='forestgreen', edgecolor='black')
# plt.hist(zeroes_bottom, bins=bins, alpha=0.5, color='firebrick', edgecolor='black')
# if len(ones_and_zeroes_bottom) > 0:
#     plt.axvline(np.average(ones_and_zeroes_bottom), color='blue', linestyle='dashed', linewidth=1)
#     plt.axvline(np.median(ones_and_zeroes_bottom), color='orange', linestyle='dashed', linewidth=1)
#     plt.axvline(np.percentile(ones_and_zeroes_bottom,80), color='purple', linestyle='dashed', linewidth=1)
#
# bottom_median = np.median(ones_and_zeroes_bottom)
#
# plt.xlabel('Similarity')
# plt.ylabel('Frequency')
# plt.ylim(0, 70)
# plt.title(f'Bottom Sentences Semantic Pass/Fail Distribution\nmodel: {model_name}\nnx: {syntax_count}, ny: {semantic_count}, nz: {shot_count}, median: {bottom_median}\n')
# plt.savefig(f'../images/{model_name}/{set_name}_bottom_histogram_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}.pdf')
# plt.close()



#
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
