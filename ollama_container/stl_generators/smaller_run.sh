#!/bin/bash
# python stl_generator_v7.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' 'stl_generator_v4_config.json' > deepseek_convo.txt
python ../heatmap_generators/stl_evaluation_v6.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' 'translations_DeepSeek-R1-Distill-Qwen-1.5B.pkl' 'stl_generator_v4_config.json'
# python stl_generator_v7.py 'Qwen/Qwen3-1.7B' 'stl_generator_v4_config.json' > qwen_convo.txt
python ../heatmap_generators/stl_evaluation_v6.py 'Qwen/Qwen3-1.7B' 'translations_Qwen3-1.7B.pkl' 'stl_generator_v4_config.json'
