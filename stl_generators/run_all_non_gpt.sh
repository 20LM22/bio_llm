##!/bin/bash
#
### TODO: make sure that official model names and models line up correctly
models=('DeepSeek-R1-Distill-Qwen-1.5B' 'Qwen3-1.7B')
official_model_names=('deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' 'Qwen/Qwen3-1.7B')
#experiments=("nx_4_ny_2_nz_18")
#set_name="val_set"
#
## Optional: check that arrays line up
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
#    time=$(/usr/bin/date +%F_%H-%M-%S) # Example: 2025-10-05_20-07-09
#    convo="../stats/${model}/convo_${experiment}_${time}.txt"
#    translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
#
#    echo "$config"
##    python stl_generator_v7.py "${official_model_names[i]}" "$config" "$experiment" "$time" >| "$convo"
##    echo "Done with version: $config"
##    python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
#    python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
##    python ../evaluations/generate_semantic_distribution_plots.py "$model" "$config" "$time"
#    ((i++))
#  done
#done

#
## TODO: make sure that official model names and models line up correctly
#experiments=("nx_3_ny_2_nz_18" "nx_4_ny_2_nz_18")
#set_name="test_set"
#
## Optional: check that arrays line up
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
#    time=$(/usr/bin/date +%F_%H-%M-%S) # Example: 2025-10-05_20-07-09
#    convo="../stats/${model}/convo_${experiment}_${time}.txt"
#    translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
#
#    echo "$config"
#    python stl_generator_v7.py "${official_model_names[i]}" "$config" "$experiment" "$time" >| "$convo"
#    echo "Done with version: $config"
#    python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
##   python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
##   python ../evaluations/generate_semantic_distribution_plots.py "$model" "$config" "$time"
#    ((i++))
#  done
#done
#
##!/bin/bash
#
#models=('DeepSeek-R1-Distill-Qwen-1.5B' 'Qwen3-1.7B')
#official_model_names=('deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' 'Qwen/Qwen3-1.7B')
experiments=("nx_4_ny_2_nz_18")
set_name="val_set"
times=('2025-10-13_23-11-29' '2025-10-14_00-20-08')

for experiment in "${experiments[@]}"
do
  config="config_${experiment}_${set_name}.json"
  echo "$config"

  i=0
  for i in "${!models[@]}"
  do
    model="${models[$i]}"
    time="${times[$i]}"
    translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
    python ../evaluations/generate_semantic_distribution_plots.py "$model" "$config" "$time"
  done
done

# test_set_stats_nx_4_ny_2_nz_18_2025-10-17_03-24-49.csv <-- deepseek test set redo
# test_set_stats_nx_4_ny_2_nz_18_2025-10-17_05-38-17.csv <-- qwen test set redo

'../pkl/DeepSeek-R1-Distill-Qwen-1.5B/val_set_translations_DeepSeek-R1-Distill-Qwen-1.5B_nx_4_ny_2_nz_18_2025-10-17_03-24-49.pkl'

