#!/bin/bash
# deepseek='DeepSeek-R1-Distill-Qwen-1.5B'
qwen='Qwen3-1.7B'

experiment="shots_18_syntax_2_semantic_1"
config="qd_test_set_config_${experiment}.json"
echo $config

qwen_convo="../stats/${qwen}/test_set_convo_${experiment}.txt"
# deepseek_convo="../stats/${deepseek}/test_set_convo_${experiment}.txt"

# translations_deepseek="test_set_translations_${deepseek}_${experiment}.pkl"
translations_qwen="test_set_translations_${qwen}_${experiment}.pkl"

# python stl_generator_v7.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' $config $experiment >| $deepseek_convo # gpt is using the gpt generator
python stl_generator_v7.py 'Qwen/Qwen3-1.7B' $config $experiment >| $qwen_convo # gpt is using the gpt generator

# python ../evaluations/stl_evaluation_v6.py $deepseek $translations_deepseek $config
python ../evaluations/stl_evaluation_v6.py $qwen $translations_qwen $config
