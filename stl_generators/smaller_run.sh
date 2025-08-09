#!/bin/bash
config='config_shots_18_syntax_3_semantic_2.json'
deepseek_convo='../stats/DeepSeek-R1-Distill-Qwen-1.5B/convo_shots_18_syntax_3_semantic_0.txt'
qwen_convo='../stats/Qwen3-1.7B/convo_18_syntax_3_semantic_0.txt'

# python stl_generator_v7.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' $config > $deepseek_convo
# python ../evaluations/stl_evaluation_v6.py 'DeepSeek-R1-Distill-Qwen-1.5B' 'translations_DeepSeek-R1-Distill-Qwen-1.5B_shots_18_syntax_3_semantic_0.pkl' $config
# python ../evaluations/generate_semantic_distribution_dict.py 'DeepSeek-R1-Distill-Qwen-1.5B' 'translations_DeepSeek-R1-Distill-Qwen-1.5B_shots_18_syntax_3_semantic_0.pkl' $config
python ../evaluations/generate_semantic_distribution_plots.py 'DeepSeek-R1-Distill-Qwen-1.5B' $config

# python stl_generator_v7.py 'Qwen/Qwen3-1.7B' $config > $qwen_convo
# python ../evaluations/stl_evaluation_v6.py 'Qwen3-1.7B' 'translations_Qwen3-1.7B_shots_18_syntax_3_semantic_0.pkl' $config
# python ../evaluations/generate_semantic_distribution_dict.py 'Qwen3-1.7B' 'translations_Qwen3-1.7B_shots_18_syntax_3_semantic_0.pkl' $config
python ../evaluations/generate_semantic_distribution_plots.py 'Qwen3-1.7B' $config
