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
times=("2026-01-25_17-47-50")

i=0
for experiment in "${experiments[@]}"
do
  config="config_${experiment}_${set_name}.json"
  echo "$config"
  for model in "${models[@]}" 
  do 
    time="${times[$i]}" # $(/usr/bin/date +%F_%H-%M-%S)
    convo="../stats/${model}/convo_${experiment}_${time}.txt"
    
    translations="../pkl/${model}/${set_name}_translations_${model}_${experiment}_${time}.pkl"
    translations_annotations_stats="../pkl/${set_name}_semantic_labels_${model}_${experiment}_${time}.pkl"
    
    filtered_output="../pkl/${model}/${set_name}_filtered_output_${model}_${experiment}_${time}.pkl"
    filtered_annotations_output="../pkl/${model}/${set_name}_filtered_output_annotations_${model}_${experiment}_${time}.pkl"

    # fix these
    consolidated_output="../stats/${model}/${set_name}_consolidated_output_${model}_${experiment}_${time}.json"
    consolidated_annotations_output="../stats/${model}/${set_name}_annotate_consolidated_${model}_${experiment}_${time}.json"
  
    echo "$model"
    echo "$translations"
    echo "$config"
    echo "$time"

    # python ../evaluations/generate_semantic_distribution_plots.py "$model" "$config" "$time"

    # python ../consolidate/annotate_after_initial_generation.py "$model" "$translations" "$config" "$time"       
    # python ../consolidate/annotate_after_initial_generation_stats.py "$translations_annotations_stats"      

    # python ../consolidate/filter_by_cosine_similarity.py "$model" "$translations" "$config" "$time"       
    # python ../consolidate/annotate_after_cosine_filter.py "$model" "$filtered_output" "$config" "$time"       
    # python ../consolidate/annotate_after_cosine_filter_stats.py "$filtered_annotations_output"       

    # python ../consolidate/consolidate.py "$model" "$filtered_output" "$config" "$time"
    # python ../consolidate/annotate_consolidated.py "$model" "$consolidated_output" "$config" "$time"       

    python ../consolidate/annotate_consolidated_stats.py "$translations" "$filtered_annotations_output" "$consolidated_annotations_output"      
    # python check_consolidated_structure.py "$consolidated_annotations_output"

    # python stl_generator_gpt.py "$model" "$config" "$experiment" "$time" >| "$convo"
    # python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
    # python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
  done
  ((++i))
done