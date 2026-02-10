#!/bin/bash

models=('gemini-3-flash-preview') 
official_model_names=('gemini-3-flash-preview')

experiments=("nx_3_ny_1_nz_18")
set_name="final_test_set" 
# times=("2026-02-08_14-30-39") # ("2026-01-25_17-47-50")

i=0
for experiment in "${experiments[@]}"
do
  config="config_${experiment}_${set_name}.json"
  echo "$config"
  for model in "${models[@]}" 
  do 
    time=$(/usr/bin/date +%F_%H-%M-%S) # "${times[$i]}" 
    convo="../stats/${model}/convo_${experiment}_${time}.txt"
    
    translations="../pkl/${model}/${set_name}_translations_${model}_${experiment}_${time}.pkl"
    translations_annotations_stats="../pkl/${set_name}_semantic_labels_${model}_${experiment}_${time}.pkl"
    
    filtered_output="../pkl/${model}/${set_name}_filtered_output_${model}_${experiment}_${time}.pkl"
    filtered_annotations_output="../pkl/${model}/${set_name}_filtered_output_annotations_${model}_${experiment}_${time}.pkl"

    consolidated_output="../stats/${model}/${set_name}_consolidated_output_${model}_${experiment}_${time}.json"
    consolidated_annotations_output="../stats/${model}/${set_name}_annotate_consolidated_${model}_${experiment}_${time}.json"
  
    echo "$model"
    echo "$translations"
    echo "$config"
    echo "$time"

    python stl_generator_gemini.py "$model" "$config" "$experiment" "$time" >| "$convo"
    # python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
    # python ../consolidate/filter_by_cosine_similarity.py "$model" "$translations" "$config" "$time"       
    # python ../consolidate/consolidate.py "$model" "$filtered_output" "$config" "$time"
    # python ../consolidate/annotate_consolidated.py "$model" "$consolidated_output" "$config" "$time"
    # "$translations" "$filtered_annotations_output" "$consolidated_annotations_output"      

  done
  ((++i))
done