#!/bin/bash

# TODO: make sure that official model names and models line up correctly
models=('gpt-4o-2024-08-06')
official_model_names=('gpt-4o-2024-08-06')
experiments=("nx_2_ny_2_nz_18")
set_name="prelim_set"

for experiment in "${experiments[@]}"
do
  config="config_${experiment}_${set_name}.json"
  echo $config

  i=0
  for model in "${models[@]}"
    do
      time=$(date +%F_%T)
      convo="../stats/${model}/config_${experiment}_${time}.txt"
      translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
      python stl_generator_gpt.py ${official_model_names[i]} $config $experiment $time >| $convo
#      python ../evaluations/stl_evaluation_v6.py $model $translations $config $time
#      python ../evaluations/generate_semantic_distribution_dict.py $model $translations $config $time
#      python ../evaluations/generate_semantic_distribution_plots.py $model $config $time
      i=i+1
    done
done
