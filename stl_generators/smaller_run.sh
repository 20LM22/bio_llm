#!/bin/bash
deepseek='DeepSeek-R1-Distill-Qwen-1.5B'
qwen='Qwen3-1.7B'

# check that there's 8 things listed here
experiments=("shots_18_syntax_3_semantic_1" "shots_18_syntax_3_semantic_2")

for experiment in "${experiments[@]}"
do
  config="config_${experiment}.json"
  echo $config

  translations_deepseek="translations_${deepseek}_${experiment}.pkl"
  translations_qwen="translations_${qwen}_${experiment}.pkl"

  python ../evaluations/stl_evaluation_v6.py $qwen $translations_qwen $config
  python ../evaluations/stl_evaluation_v6.py $deepseek $translations_deepseek $config
done
