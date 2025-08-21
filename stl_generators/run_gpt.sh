#!/bin/bash
gpt='gpt-4o-2024-08-06'

# check that there's 8 things listed here
experiments=("shots_18_syntax_1_semantic_2" "shots_18_syntax_2_semantic_2" "shots_18_syntax_3_semantic_2" "shots_18_syntax_4_semantic_2" "shots_5_syntax_3_semantic_2" "shots_18_syntax_3_semantic_0" "shots_18_syntax_3_semantic_1" "shots_50_syntax_3_semantic_2")

for experiment in "${experiments[@]}"
do
  config="config_${experiment}.json"
  echo $config
  translations_gpt="translations_${gpt}_${experiment}.pkl"
  python ../evaluations/stl_evaluation_v6.py $gpt $translations_gpt $config
done
