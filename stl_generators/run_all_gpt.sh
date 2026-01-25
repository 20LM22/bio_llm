#!/bin/bash

# TODO: make sure that official model names and models line up correctly
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

models=('gpt-4o-2024-08-06') # ('gpt-5.2-2025-12-11')
official_model_names=('gpt-4o-2024-08-06') # ('gpt-5.2-2025-12-11')

experiments=("nx_3_ny_1_nz_18")
set_name="final_test_set" 
# times=("2025-12-30_00-35-54")

i=0
for experiment in "${experiments[@]}"
do
  config="config_${experiment}_${set_name}.json"
  echo "$config"
  for model in "${models[@]}"
  do
    time=$(/usr/bin/date +%F_%H-%M-%S) # "${times[$i]}"
    convo="../stats/${model}/convo_${experiment}_${time}.txt"
    translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
    consolidated_pkl="../pkl/${set_name}_consolidated_${model}_${experiment}_${time}.pkl"
    filtered_pkl="../pkl/${set_name}_cosine_filtered_${model}_${experiment}_${time}.pkl"
    
    python stl_generator_gpt.py "$model" "$config" "$experiment" "$time" >| "$convo"
    python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
    python ../consolidate/consolidate.py "$model" "$translations" "$config" "$time"
    python ../consolidate/filter_by_cosine_similarity.py "$model" "$consolidated_pkl" "$config" "$time"       
    python ../consolidate/annotate_after_cosine_filter.py "$model" "$filtered_pkl" "$config" "$time"       
  
    # python stl_generator_gpt.py "$model" "$config" "$experiment" "$time" >| "$convo"
    # python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
    # python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
  done
  ((++i))
done

