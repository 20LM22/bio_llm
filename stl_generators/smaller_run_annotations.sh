#!/bin/bash
deepseek='DeepSeek-R1-Distill-Qwen-1.5B'
qwen='Qwen3-1.7B'

experiments=("shots_18_syntax_2_semantic_1")

for experiment in "${experiments[@]}"
do
  config="config_shots_18_syntax_2_semantic_1.json" # it's ok that it says gpt here
  echo $config

  translations_deepseek="translations_${deepseek}_${experiment}.pkl" # these are the right translation files
  translations_qwen="translations_${qwen}_${experiment}.pkl"

#  python ../evaluations/stl_evaluation_redo.py $deepseek $translations_deepseek $config
#  python ../evaluations/generate_semantic_distribution_dict.py $deepseek $translations_deepseek $config
  python ../evaluations/generate_semantic_distribution_plots.py $deepseek $config
  # python ../evaluations/generate_semantic_distribution_plots.py 'DeepSeek-R1-Distill-Qwen-1.5B' "config_shots_18_syntax_2_semantic_1.json"

#  python ../evaluations/stl_evaluation_redo.py $qwen $translations_qwen $config
#  python ../evaluations/generate_semantic_distribution_dict.py $qwen $translations_qwen $config
  python ../evaluations/generate_semantic_distribution_plots.py $qwen $config

done
