#!/bin/bash

python ../heatmap_generators/stl_evaluation.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B-1.5B' 'translations_DeepSeek-R1-Distill-Qwen-1.5B.pkl'
echo 'Deepseek Completed'

python ../heatmap_generators/stl_evaluation.py 'Qwen/Qwen3-0.6B' 'translations_Qwen3-0.6B.pkl'
echo 'Qwen 0.6B Completed'

python ../heatmap_generators/stl_evaluation.py 'Qwen/Qwen3-1.7B' 'translations_Qwen3-1.7B.pkl'
echo 'Qwen 1.7B Completed'

