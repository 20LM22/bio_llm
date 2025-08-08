#!/bin/bash
# python stl_generator_v7.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' 'stl_generator_v4_config.json' > deepseek_convo.txt
python ../heatmap_generators/stl_evaluation_v6.py 'deepseek' 'translations_rollback_DeepSeek-R1-Distill-Qwen-1.5B.pkl' 'stl_generator_rollback_config.json'
python ../heatmap_generators/generate_semantic_distribution_dict.py 'deepseek'
python ../heatmap_generators/generate_semantic_distribution_plots.py 'deepseek'

# python stl_generator_v7.py 'Qwen/Qwen3-1.7B' 'stl_generator_v4_config.json' > qwen_convo.txt
python ../heatmap_generators/stl_evaluation_v6.py 'qwen' 'translations_rollback_Qwen3-1.7B.pkl' 'stl_generator_rollback_config.json'
python ../heatmap_generators/generate_semantic_distribution_dict.py 'qwen'
python ../heatmap_generators/generate_semantic_distribution_plots.py 'qwen'

# note: did not run the distributions on the rollback version yet
# need to git commit this as "ran the semantic