#!/bin/bash
deepseek='DeepSeek-R1-Distill-Qwen-1.5B'
qwen='Qwen3-1.7B'

# check that there's 8 things listed here
experiments=("shots_18_syntax_1_semantic_2" "shots_18_syntax_2_semantic_2" "shots_18_syntax_3_semantic_2" "shots_18_syntax_4_semantic_2" "shots_5_syntax_3_semantic_2" "shots_18_syntax_3_semantic_0" "shots_18_syntax_3_semantic_1" "shots_50_syntax_3_semantic_2")

for experiment in "${experiments[@]}"
do
  config="test_set_config_${experiment}.json"
  echo $config

  deepseek_convo="../stats/DeepSeek-R1-Distill-Qwen-1.5B/test_set_convo_${experiment}.txt"
  qwen_convo="../stats/Qwen3-1.7B/test_set_convo_${experiment}.txt"
  translations_deepseek="translations_test_set_${deepseek}_${experiment}.pkl"
  translations_qwen="translations_test_set_${qwen}_${experiment}.pkl"

  python stl_generator_v7.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' $config $experiment > $deepseek_convo
#  python ../evaluations/stl_evaluation_v6.py $deepseek $translations_deepseek $config
#  python ../evaluations/generate_semantic_distribution_dict.py $deepseek $translations_deepseek $config
#  python ../evaluations/generate_semantic_distribution_plots.py $deepseek $config

  python stl_generator_v7.py 'Qwen/Qwen3-1.7B' $config $experiment > $qwen_convo
#  python ../evaluations/stl_evaluation_v6.py $qwen $translations_qwen $config
#  python ../evaluations/generate_semantic_distribution_dict.py $qwen $config
#  python ../evaluations/generate_semantic_distribution_plots.py $qwen $config

  echo "Done running generator for test set: ${experiment}, but evals not run yet"
  git add ..
  git commit -m "Done running generator for test set: ${experiment}, but evals not run yet"
  git push origin
  echo "Pushed: done running generator for test set: ${experiment}, but evals not run yet"
done

 distribution
should see 18 of these
Loaded histogram distribution
C:\Users\etoil\stl-project\.venv\Lib\site-packages\numpy\lib\_function_base_impl.py:571: RuntimeWarning: Mean of empty slice.
  avg = a.mean(axis, **keepdims_kw)
C:\Users\etoil\stl-project\.venv\Lib\site-packages\numpy\_core\_methods.py:144: RuntimeWarning: invalid value encountered in scalar divide
  ret = ret.dtype.type(ret / rcount)
C:\Users\etoil\stl-project\.venv\Lib\site-packages\numpy\_core\fromnumeric.py:3860: RuntimeWarning: Mean of empty slice.
  return _methods._mean(a, axis=axis, dtype=dtype,
config_shots_50_syntax_3_semantic_2.json
should see 18 of these
Loaded histogram distribution


config_shots_18_syntax_1_semantic_2.json
should see 18 of these
Loaded histogram distribution
should see 18 of these
Loaded histogram distribution
C:\Users\etoil\stl-project\.venv\Lib\site-packages\numpy\lib\_function_base_impl.py:571: RuntimeWarning: Mean of empty slice.
  avg = a.mean(axis, **keepdims_kw)
C:\Users\etoil\stl-project\.venv\Lib\site-packages\numpy\_core\_methods.py:144: RuntimeWarning: invalid value encountered in scalar divide
  ret = ret.dtype.type(ret / rcount)
C:\Users\etoil\stl-project\.venv\Lib\site-packages\numpy\_core\fromnumeric.py:3860: RuntimeWarning: Mean of empty slice.
  return _methods._mean(a, axis=axis, dtype=dtype,
config_shots_18_syntax_2_semantic_2.json
should see 18 of these
Loaded histogram distribution

len(sim_arr): 15
len(sim_arr): 0
C:\Users\etoil\stl-project\.venv\Lib\site-packages\numpy\lib\_function_base_impl.py:571: RuntimeWarning: Mean of empty slice.
  avg = a.mean(axis, **keepdims_kw)
C:\Users\etoil\stl-project\.venv\Lib\site-packages\numpy\_core\_methods.py:144: RuntimeWarning: invalid value encountered in scalar divide
  ret = ret.dtype.type(ret / rcount)
C:\Users\etoil\stl-project\.venv\Lib\site-packages\numpy\_core\fromnumeric.py:3860: RuntimeWarning: Mean of empty slice.
  return _methods._mean(a, axis=axis, dtype=dtype,
config_shots_18_syntax_2_semantic_2.json
should see 18 of these

