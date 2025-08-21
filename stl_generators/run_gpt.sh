#!/bin/bash
gpt='gpt-4o-2024-08-06'

# check that there's 8 things listed here
experiments=("shots_5_syntax_3_semantic_2")

# "shots_18_syntax_1_semantic_2" "shots_18_syntax_2_semantic_2" "shots_18_syntax_3_semantic_2" "shots_18_syntax_4_semantic_2" "shots_5_syntax_3_semantic_2" "shots_18_syntax_3_semantic_0" "shots_18_syntax_3_semantic_1" "shots_50_syntax_3_semantic_2")

for experiment in "${experiments[@]}"
do
  config="gpt_config_${experiment}.json"
  gpt_convo="../stats/${gpt}/convo_${experiment}.txt"
  echo $config
  translations_gpt="translations_${gpt}_${experiment}.pkl"
  python stl_generator_v7.py 'gpt-4o-2024-08-06' "gpt_config_shots_5_syntax_3_semantic_2.json" "shots_5_syntax_3_semantic_2"
  # > $deepseek_convo
done
