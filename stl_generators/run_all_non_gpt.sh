##!/bin/bash
#
## TODO: make sure that official model names and models line up correctly
#models=('DeepSeek-R1-Distill-Qwen-1.5B' 'Qwen3-1.7B')
#official_model_names=('deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' 'Qwen/Qwen3-1.7B')
#experiments=("nx_2_ny_2_nz_18")
#set_name="prelim_set"
#
#for experiment in "${experiments[@]}"
#do
#  config="config_${experiment}_${set_name}.json"
#  echo $config
#
#  i=0 #TODO switch back to 0 when needed
#  for model in "${models[@]}"
#    do
#      time=$(/usr/bin/date +%F_%H-%M-%S)
#      convo="../stats/${model}/config_${experiment}_${time}.txt"
#      translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
#      echo $config
##      python stl_generator_v7.py ${official_model_names[i]} $config $experiment $time # >| $convo
##      python ../evaluations/stl_evaluation_v6.py $model $translations $config $time
##      python ../evaluations/generate_semantic_distribution_dict.py $model $translations $config $time
##      python ../evaluations/generate_semantic_distribution_plots.py $model $config $time
#      ((i++))
#    done
#done

# TODO: make sure that official model names and models line up correctly
models=('DeepSeek-R1-Distill-Qwen-1.5B' 'Qwen3-1.7B')
experiments=("nx_2_ny_2_nz_18")
set_name="prelim_set"

for experiment in "${experiments[@]}"
do
  config="config_${experiment}_${set_name}.json"
  echo $config

  time='2025-09-29_22-27-42'
  model='DeepSeek-R1-Distill-Qwen-1.5B'
  translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
  echo "trying to run first eval"
  python ../evaluations/generate_semantic_distribution_dict.py $model $translations $config $time 2>| errors.txt

  time='2025-09-30_00-19-58'
  model='Qwen3-1.7B'
  translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
  python ../evaluations/generate_semantic_distribution_dict.py $model $translations $config $time

done
