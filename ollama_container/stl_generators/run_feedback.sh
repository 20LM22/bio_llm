#!/bin/bash
if [ "$1" = "0" ]; then 
	python stl_generator_v2.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B'
	python ../heatmap_generators/stl_evaluation.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' '../pkl/translations_DeepSeek-R1-Distill-Qwen-1.5B.pkl'
elif [ "$1" = "1" ]; then
	python stl_generator_v2.py 'Qwen/Qwen3-0.6B'
	python ../heatmap_generators/stl_evaluation.py 'Qwen/Qwen3-0.6B' '../pkl/translations_Qwen3-0.6B.pkl'
else
	python stl_generator_v2.py 'Qwen/Qwen3-1.7B'
	python ../heatmap_generators/stl_evaluation.py 'Qwen/Qwen3-1.7B' '../pkl/translations_Qwen3-1.7B.pkl'
fi
