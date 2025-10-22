#!/bin/bash

# TODO: make sure that official model names and models line up correctly
models=('gpt-4o-2024-08-06')
official_model_names=('gpt-4o-2024-08-06')
#experiments=("nx_1_ny_2_nz_18" "nx_2_ny_2_nz_18" "nx_3_ny_1_nz_18" "nx_3_ny_2_nz_18" "nx_4_ny_2_nz_18")
#set_name="val_set"
#
## Optional safety check
#if [ ${#models[@]} -ne ${#official_model_names[@]} ]; then
#  echo "Error: 'models' and 'official_model_names' arrays must have the same length."
#  exit 1
#fi
#
#for experiment in "${experiments[@]}"
#do
#  config="config_${experiment}_${set_name}.json"
#  echo "$config"
#
#  i=0
#  for model in "${models[@]}"
#  do
#    # time='2025-10-17_09-55-23'
#    time=$(/usr/bin/date +%F_%H-%M-%S)
#    convo="../stats/${model}/convo_${experiment}_${time}.txt"
#    translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
#
#    echo "$config"
#    python stl_generator_gpt.py "${official_model_names[i]}" "$config" "$experiment" "$time" >| "$convo"
#    echo "Done with config: $config"
#    python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
#
##    python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
##    python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
#    ((i++))
#  done
#done

experiments=("nx_3_ny_1_nz_18")
set_name="val_set"

# Optional safety check
if [ ${#models[@]} -ne ${#official_model_names[@]} ]; then
  echo "Error: 'models' and 'official_model_names' arrays must have the same length."
  exit 1
fi

for experiment in "${experiments[@]}"
do
  config="config_${experiment}_${set_name}.json"
  echo "$config"

  i=0
  for model in "${models[@]}"
  do
    time="2025-10-19_21-39-51" #$(/usr/bin/date +%F_%H-%M-%S)
    convo="../stats/${model}/convo_${experiment}_${time}.txt"
    translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
#test_set_stats_nx_3_ny_1_nz_18_2025-10-21_10-01-14.csv
# test_set_translations_gpt-4o-2024-08-06_nx_3_ny_1_nz_18_2025-10-21_10-01-14
    echo "$config"
#    python stl_generator_gpt.py "${official_model_names[i]}" "$config" "$experiment" "$time" >| "$convo"
#    echo "Done with config: $config"
#    python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
    python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
    ((i++))
  done
done

# annotations:
# GPT: 2025-10-21_10-01-14
# Qwen: 2025-10-21_13-21-56
# Deepseek: 2025-10-21_11-49-17