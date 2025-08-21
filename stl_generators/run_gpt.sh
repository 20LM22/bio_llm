#!/bin/bash
gpt='gpt-4o-2024-08-06'

# check that there's 8 things listed here
experiments=("shots_18_syntax_1_semantic_2")
# "shots_18_syntax_2_semantic_2" "shots_18_syntax_3_semantic_2" "shots_18_syntax_4_semantic_2" "shots_18_syntax_3_semantic_0" "shots_18_syntax_3_semantic_1")

for experiment in "${experiments[@]}"
do
  config="gpt_config_${experiment}.json"
  gpt_convo="../stats/${gpt}/training_convo_${experiment}.txt"
  echo $config
  translations_gpt="translations_${gpt}_${experiment}.pkl"
  # python stl_generator_gpt.py $gpt $config $experiment
  python ../evaluations/stl_evaluation_v6.py $gpt $translations_gpt $config
done
