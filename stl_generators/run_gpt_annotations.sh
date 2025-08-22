#!/bin/bash
gpt='gpt-4o-2024-08-06'

# check that there's 8 things listed here
experiments=("shots_18_syntax_2_semantic_2")

for experiment in "${experiments[@]}"
do
  config="gpt_test_set_config_${experiment}.json"

  echo $config
  translations_gpt="redo_gpt_test_translations_${gpt}_${experiment}.pkl"

  # python ../evaluations/generate_semantic_distribution_dict.py $gpt $translations_gpt $config
  python ../evaluations/generate_semantic_distribution_plots.py 'gpt-4o-2024-08-06' $config
done
