#!/bin/bash

python stl_generator_v3.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B-1.5B'
python ../heatmap_generators/stl_evaluation.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B-1.5B' 'translations_DeepSeek-R1-Distill-Qwen-1.5B.pkl' > ../stats/DeepSeek-R1-Distill-Qwen-1.5B-1.5B/generation_problems.txt
echo 'Deepseek Completed'

python stl_generator_v3.py 'Qwen/Qwen3-0.6B'
python ../heatmap_generators/stl_evaluation.py 'Qwen/Qwen3-0.6B' 'translations_Qwen3-0.6B.pkl' > ../stats/Qwen3-0.6B/generation_problems.txt
echo 'Qwen 0.6B Completed'

python stl_generator_v3.py 'Qwen/Qwen3-1.7B'
python ../heatmap_generators/stl_evaluation.py 'Qwen/Qwen3-1.7B' 'translations_Qwen3-1.7B.pkl' > ../stats/Qwen3-1.7B/generation_problems.txt
echo 'Qwen 1.7B Completed'

