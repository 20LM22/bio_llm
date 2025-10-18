#!/bin/bash

# TODO: make sure that official model names and models line up correctly
models=('gpt-4o-2024-08-06')
official_model_names=('gpt-4o-2024-08-06')
experiments=("nx_4_ny_2_nz_18")
set_name="test_set"

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
    time='2025-10-17_09-55-23'
    convo="../stats/${model}/config_${experiment}_${time}.txt"
    translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"

    echo "$config"
#    python stl_generator_gpt.py "${official_model_names[i]}" "$config" "$experiment" "$time" >| "$convo"
#    echo "Done with config: $config"
#    python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
    # python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
    python ../evaluations/generate_semantic_distribution_plots.py "$model" "$config" "$time"

    ((i++))
  done
done

#experiments=("nx_4_ny_2_nz_18")
#set_name="val_set"
#times=('2025-10-14_00-20-08')
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
#    time='2025-10-13_21-16-58'
#    translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
#    python ../evaluations/generate_semantic_distribution_plots.py "$model" "$config" "$time"
#
#    ((i++))
#  done
#done
#
