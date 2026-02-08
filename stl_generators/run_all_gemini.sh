#!/bin/bash

models=('gemini-3-flash-preview') 
official_model_names=('gemini-3-flash-preview')

experiments=("nx_3_ny_1_nz_18")
set_name="final_test_set" 
times=("2026-02-08_13-40-42") # ("2026-01-25_17-47-50")

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

    consolidated_output="../stats/${model}/${set_name}_consolidated_output_${model}_${experiment}_${time}.json"
    consolidated_annotations_output="../stats/${model}/${set_name}_annotate_consolidated_${model}_${experiment}_${time}.json"
  
    echo "$model"
    echo "$translations"
    echo "$config"
    echo "$time"

    python stl_generator_gemini.py "$model" "$config" "$experiment" "$time" # >| "$convo"
    # python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
    # python ../consolidate/filter_by_cosine_similarity.py "$model" "$translations" "$config" "$time"       
    # python ../consolidate/consolidate.py "$model" "$filtered_output" "$config" "$time"
    # python ../consolidate/annotate_consolidated_stats.py "$translations" "$filtered_annotations_output" "$consolidated_annotations_output"      

# response: {'thinking': "The sentence indicates that within two weeks (days 0 to 14) of symptom onset, SARS-CoV-2-specific T-cells (represented by the 'tcells' species) begin to appear in peripheral blood, implying that at some point in this interval their levels or rate of increase becomes significant. I will translate this as the species 'tcells' eventually having a positive rate of change between day 0 and day 14.",
#  'input_statement': 'In patients with COVID-19, SARS-CoV-2-specific T-cells appear in peripheral blood within two weeks of symptom onset (31).',
#  'output_STL': 'eventually[0,14](d_tcells(t) > 0)'}
# class STLResponse(BaseModel):
#     thinking: str
#     input_statement: str
#     output_STL: str

  done
  ((++i))
done