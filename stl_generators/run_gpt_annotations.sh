#!/bin/bash
gpt='gpt-4o-2024-08-06'

# check that there's 8 things listed here
experiments=("shots_18_syntax_2_semantic_1")

for experiment in "${experiments[@]}"
do
  config="gpt_config_${experiment}.json"
  # gpt_convo="../stats/${gpt}/test_set_convo_${experiment}.txt"
  echo $config
  translations_gpt="translations_${gpt}_${experiment}.pkl"
  # python stl_generator_gpt.py $gpt $config $experiment >| $gpt_convo
  # python ../evaluations/stl_evaluation_v6.py $gpt $translations_gpt $config
  # python ../evaluations/generate_semantic_distribution_dict.py $gpt $translations_gpt $config
  python ../evaluations/generate_semantic_distribution_plots.py $gpt $config
  python ../evaluations/generate_semantic_distribution_plots.py 'gpt-4o-2024-08-06' "gpt_config_shots_18_syntax_2_semantic_1.json"
done
