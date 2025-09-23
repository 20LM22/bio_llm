#!/bin/bash

# TODO: make sure that official model names and models line up correctly
models=('Qwen3-1.7B')
official_model_names=('Qwen/Qwen3-1.7B')
experiments=("nx_2_ny_2_nz_18")
set_name="prelim_set"

for experiment in "${experiments[@]}"
do
  config="config_${experiment}_${set_name}.json"
  echo $config

  i=0 #TODO switch back to 0 when needed
  for model in "${models[@]}"
    do
      time=2025-09-22_10:33:05 #$(/usr/bin/date +%F_%T)
      convo="../stats/${model}/config_${experiment}_${time}.txt"
      translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
      echo $config
#      python stl_generator_v7.py ${official_model_names[i]} $config $experiment $time >| $convo
      python ../evaluations/stl_evaluation_v6.py $model $translations $config $time
#      python ../evaluations/generate_semantic_distribution_dict.py $model $translations $config $time
#      python ../evaluations/generate_semantic_distribution_plots.py $model $config $time
      ((i++))
    done
done
