#!/bin/bash
gpt='gpt-4o-2024-08-06'

experiments=("shots_18_syntax_2_semantic_2")

for experiment in "${experiments[@]}"
do
  config="gpt_test_set_config_${experiment}.json"
  gpt_convo="../stats/${gpt}/redo_gpt_test_convo_${experiment}.txt"
  echo $config
  translations_gpt="redo_gpt_test_translations_${gpt}_${experiment}.pkl"
  python stl_generator_gpt.py $gpt $config $experiment >| $gpt_convo
  python ../evaluations/stl_evaluation_v6.py $gpt $translations_gpt $config
done