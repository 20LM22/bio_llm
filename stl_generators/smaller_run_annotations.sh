#!/bin/bash
deepseek='DeepSeek-R1-Distill-Qwen-1.5B'
qwen='Qwen3-1.7B'

experiments=("shots_18_syntax_2_semantic_1")

for experiment in "${experiments[@]}"
do
  config="qd_test_set_config_shots_18_syntax_2_semantic_1.json"
  echo $config

  translations_deepseek="test_set_translations_${deepseek}_${experiment}.pkl"
  translations_qwen="test_set_translations_${qwen}_${experiment}.pkl"

  # python ../evaluations/generate_semantic_distribution_dict.py "DeepSeek-R1-Distill-Qwen-1.5B" "test_set_translations_DeepSeek-R1-Distill-Qwen-1.5B_shots_18_syntax_2_semantic_1.pkl" "qd_test_set_config_shots_18_syntax_2_semantic_1.json"
  python ../evaluations/generate_semantic_distribution_dict.py $qwen $translations_qwen $config

  # python ../evaluations/generate_semantic_distribution_plots.py "DeepSeek-R1-Distill-Qwen-1.5B" "qd_test_set_config_shots_18_syntax_2_semantic_1.json"
  python ../evaluations/generate_semantic_distribution_plots.py $qwen $config

done
