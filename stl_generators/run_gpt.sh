#!/bin/bash
gpt='gpt-4o-2024-08-06'

# check that there's 8 things listed here
experiments=("shots_18_syntax_2_semantic_2" "shots_18_syntax_3_semantic_2" "shots_18_syntax_4_semantic_2" "shots_5_syntax_3_semantic_2" "shots_18_syntax_3_semantic_0" "shots_18_syntax_3_semantic_1" "shots_50_syntax_3_semantic_2")

for experiment in "${experiments[@]}"
do
  config="config_${experiment}.json"
  echo $config

  gpt_convo="../stats/${gpt}/convo_${experiment}.txt"
  translations_gpt="translations_${gpt}_${experiment}.pkl"

  python stl_generator_gpt.py $gpt $config $experiment > $gpt_convo
  echo 'done with ${experiment}'
#  python ../evaluations/stl_evaluation_v6.py $deepseek $translations_deepseek $config
#  python ../evaluations/generate_semantic_distribution_dict.py $deepseek $translations_deepseek $config
#  python ../evaluations/generate_semantic_distribution_plots.py $deepseek $config

#  echo "Done running GPT generator: ${experiment}, but evals not run yet"
#  git add ..
#  git commit -m "Done running GPT generator: ${experiment}, but evals not run yet"
#  git push origin
#  echo "Pushed: done running GPT generator: ${experiment}, but evals not run yet"
done
