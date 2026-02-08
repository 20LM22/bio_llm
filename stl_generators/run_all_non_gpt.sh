#!/bin/bash

# TODO: make sure that official model names and models line up correctly
models=('Llama-3.1-3B-Instruct') # ('DeepSeek-R1-Distill-Qwen-1.5B' 'Qwen3-1.7B')
official_model_names=('meta-llama/Llama-3.1-3B-Instruct') # ('deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' 'Qwen/Qwen3-1.7B')
experiments=("nx_3_ny_1_nz_18")
set_name="final_test_set"
# times=("2025-10-19_22-39-33" "2025-10-21_09-52-46")

# Optional: check that arrays line up
if [ ${#models[@]} -ne ${#official_model_names[@]} ]; then
  echo "Error: 'models' and 'official_model_names' arrays must have the same length."
  exit 1
fi

for experiment in "${experiments[@]}"
do
  config="config_${experiment}_${set_name}.json"
  echo "$config"

  for ((i=0; i<${#models[@]}; i++)); do
    model="${models[i]}"
    official_model_name="${official_model_names[i]}"
    time="${times[i]}"

    #time=$(/usr/bin/date +%F_%H-%M-%S) # Example: 2025-10-05_20-07-09
    convo="../stats/${model}/convo_${experiment}_${time}.txt"
    translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"

    echo "$config"
    python stl_generator_v7.py "${official_model_names[i]}" "$config" "$experiment" "$time" >| "$convo"
#    echo "Done with version: $config"
#    python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
#    python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
  
  done
done

# TODO: make sure that official model names and models line up correctly
#experiments=("nx_2_ny_2_nz_18" "nx_3_ny_2_nz_18" "nx_4_ny_2_nz_18")
#set_name="test_set"

# Optional: check that arrays line up
#if [ ${#models[@]} -ne ${#official_model_names[@]} ]; then
 # echo "Error: 'models' and 'official_model_names' arrays must have the same length."
  #exit 1
#fi

#for experiment in "${experiments[@]}"
#do
 # config="config_${experiment}_${set_name}.json"
 # echo "$config"

#  i=0
#  for model in "${models[@]}"
#  do
#    time=$(/usr/bin/date +%F_%H-%M-%S) # Example: 2025-10-05_20-07-09
#    convo="../stats/${model}/convo_${experiment}_${time}.txt"
#    translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
#
 #   echo "$config"
  #  python stl_generator_v7.py "${official_model_names[i]}" "$config" "$experiment" "$time" >| "$convo"
#    echo "Done with version: $config"
#    python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"

#   python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
#   python ../evaluations/generate_semantic_distribution_plots.py "$model" "$config" "$time"
  #  ((i++))
 # done
#done


##!/bin/bash
#
#models=('Qwen3-1.7B') # 'DeepSeek-R1-Distill-Qwen-1.5B'
#official_model_names=('Qwen/Qwen3-1.7B') # 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B'
#experiments=("nx_4_ny_2_nz_18")
#set_name="test_set"
#times=('2025-10-17_12-42-22') # '2025-10-17_10-25-53'
#
#for experiment in "${experiments[@]}"
#do
#  config="config_${experiment}_${set_name}.json"
#  echo "$config"
#
#  i=0
#  for i in "${!models[@]}"
#  do
#    model="${models[$i]}"
#    time="${times[$i]}"
#    translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
#    python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
#    # python ../evaluations/generate_semantic_distribution_plots.py "$model" "$config" "$time" > 'output.txt'
#  done
#done
#
### for the embeddings, we're comparing
##python nl_vs_literal.py 'DeepSeek-R1-Distill-Qwen-1.5B' "val_set_translations_DeepSeek-R1-Distill-Qwen-1.5B_nx_4_ny_2_nz_18_2025-10-13_23-11-29.pkl" "config_nx_4_ny_2_nz_18_val_set.json" '2025-10-13_23-11-29'
##python nl_vs_literal.py 'Qwen3-1.7B' "val_set_translations_Qwen3-1.7B_nx_4_ny_2_nz_18_2025-10-14_00-20-08.pkl" "config_nx_4_ny_2_nz_18_val_set.json" '2025-10-14_00-20-08'
##python nl_vs_literal.py 'gpt-4o-2024-08-06' "val_set_translations_gpt-4o-2024-08-06_nx_4_ny_2_nz_18_2025-10-13_21-16-58.pkl" "config_nx_4_ny_2_nz_18_val_set.json" '2025-10-13_21-16-58'


# TODO:
# (1) make the validation graphs --> already have the annotations so need to edit the plots file - DONE
# how to edit the plots file? Make sure that only the 2 sentences are being processed
# need to find the times
# val_set, nx_3_ny_1_nz_18, 2025-10-21

# /val_set_semantic_labels_DeepSeek-R1-Distill-Qwen-1.5B_nx_3_ny_1_nz_18_2025-10-19_22-39-33.pkl
# /val_set_semantic_labels_Qwen3-1.7B_nx_3_ny_1_nz_18_2025-10-21_09-52-46.pkl
# /val_set_semantic_labels_gpt-4o-2024-08-06_nx_3_ny_1_nz_18_2025-10-19_21-39-51.pkl

# (2) get the test semantic numbers --> check what file they're in - DONE
# (3) make the test graphs

# first, change the times
# /test_set_semantic_labels_DeepSeek-R1-Distill-Qwen-1.5B_nx_3_ny_1_nz_18_2025-10-21_11-49-17.pkl
# /test_set_semantic_labels_Qwen3-1.7B_nx_3_ny_1_nz_18_2025-10-21_13-21-56.pkl
# /test_set_semantic_labels_gpt-4o-2024-08-06_nx_3_ny_1_nz_18_2025-10-21_10-01-14.pkl

# now the plot file needs to be run 2x to tell us which are the top 3 and bottom 3 for each file
# comment out the stuff to do with creating the plots <-- here
# say that they're top and bottom 3 with at least 1 example produced

# (4) rerun the spearman correlation stuff on the test set outputs across 3x models

