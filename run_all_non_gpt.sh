#!/bin/bash

models=('DeepSeek-R1-Distill-Qwen-1.5B' 'Qwen3-1.7B')
official_model_names=('deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' 'Qwen/Qwen3-1.7B')
experiments=("nx_1_ny_0_nz_1")
set_name="sample_test_set"
consolidation_type="general" # Can be "general" or "specific" - determines how the consolidation is performed

if [ ${#models[@]} -ne ${#official_model_names[@]} ]; then
  echo "Error: 'models' and 'official_model_names' arrays must have the same length."
  exit 1
fi

for experiment in "${experiments[@]}"; do
  config="config_${experiment}_${set_name}.json"
  echo "$config"

  for ((i=0; i<${#models[@]}; i++)); do
    model="${models[i]}"
    official_model_name="${official_model_names[i]}"

    mkdir -p "./stats/${model}"
    mkdir -p "./pkl/${model}"

    time=$(/usr/bin/date +%F_%H-%M-%S) # gives each experiment a unique timestamp

    convo="./stats/${model}/convo_${experiment}_${time}.txt" # full log of the model conversation
    translations="./pkl/${model}/${set_name}_translations_${model}_${experiment}_${time}.pkl" # raw output, i.e., model's STL-NL translations    
    filtered_output="./pkl/${model}/${set_name}_filtered_output_${model}_${experiment}_${time}.pkl" # filtered output
    consolidated_output="./stats/${model}/${set_name}_consolidated_output_${consolidation_type}_${model}_${experiment}_${time}.json" # consolidated output

    # Generate the STL-NL translations, record basic stats, and annotate the initial translations with semantic labels  
    python ./stl_generators/stl_generator_v7.py "$model" "$config" "$experiment" "$time" >| "$convo"
    python ./evaluations/generate_basic_stats.py "$model" "$translations" "$config" "$time" 
    python ./evaluations/annotate_initial.py "$model" "$translations" "$config" "$time"

    # Filter the translations based on cosine similarity and annotate the filtered output with semantic labels
    python ./post_processing/filter.py "$model" "$translations" "$config" "$time" "$filtered_output"
    python ./evaluations/annotate_filtered.py "$model" "$filtered_output" "$config" "$time" 

    # Consolidate the filtered translations and annotate the consolidated output with semantic labels
    python ./post_processing/consolidate.py "$model" "$filtered_output" "$config" "$time" "$consolidation_type" "$consolidated_output"
    python ./evaluations/annotate_consolidated.py "$model" "$consolidated_output" "$config" "$time" "$consolidation_type"

  done
done