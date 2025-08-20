#!/bin/bash
deepseek='DeepSeek-R1-Distill-Qwen-1.5B'
qwen='Qwen3-1.7B'

# check that there's 8 things listed here
experiments=("shots_5_syntax_3_semantic_2")

for experiment in "${experiments[@]}"
do
  config="config_${experiment}.json"
  echo $config

#  deepseek_convo="../stats/DeepSeek-R1-Distill-Qwen-1.5B/test_set_convo_${experiment}.txt"
#  qwen_convo="../stats/Qwen3-1.7B/test_set_convo_${experiment}.txt"
  translations_deepseek="translations_${deepseek}_${experiment}.pkl"
  translations_qwen="translations_${qwen}_${experiment}.pkl"

#  python stl_generator_v7.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' $config $experiment > $deepseek_convo
  python ../evaluations/stl_evaluation_v6.py $deepseek $translations_deepseek $config
#  python ../evaluations/generate_semantic_distribution_dict.py $deepseek $translations_deepseek $config
#  python ../evaluations/generate_semantic_distribution_plots.py $deepseek $config

#  python stl_generator_v7.py 'Qwen/Qwen3-1.7B' $config $experiment > $qwen_convo

#  python ../evaluations/stl_evaluation_v6.py $qwen $translations_qwen $config
#  python ../evaluations/generate_semantic_distribution_dict.py $qwen $translations_qwen $config

#  python ../evaluations/generate_semantic_distribution_plots.py $qwen $config

#  echo "Done running dict for test set: ${experiment}, but evals not run yet"
#  git add ..
#  git commit -m "Done running generator for test set: ${experiment}, but evals not run yet"
#  git push origin
#  echo "Pushed: done running generator for test set: ${experiment}, but evals not run yet"
done
