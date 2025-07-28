#!/bin/bash
if [ "$1" = "0" ]; then 
	python stl_generator_v3.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B'
	python ../heatmap_generators/stl_evaluation.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' 'translations_DeepSeek-R1-Distill-Qwen-1.5B.pkl' 'config_DeepSeek'
elif [ "$1" = "1" ]; then
	python stl_generator_v3.py 'Qwen/Qwen3-0.6B'
	python ../heatmap_generators/stl_evaluation.py 'Qwen/Qwen3-0.6B' 'translations_Qwen3-0.6B.pkl' 'config_Qwen3-0.6B'
elif [ "$1" = "2" ]; then
	python stl_generator_v3.py 'Qwen/Qwen3-1.7B'
	python ../heatmap_generators/stl_evaluation.py 'Qwen/Qwen3-1.7B' 'translations_Qwen3-1.7B.pkl' 'config_Qwen3-1.7B'
elif [ "$1" = "3" ]; then
	python stl_generator_v3.py 'TheBloke/Mistral-7B-Instruct-v0.2-GPTQ'
	python ../heatmap_generators/stl_evaluation.py 'TheBloke/Mistral-7B-Instruct-v0.2-GPTQ' 'translations_Mistral-7B-Instruct-v0.2-GPTQ.pkl' 'config_Mistral'
elif [ "$1" = "4" ]; then
	python stl_generator_v3.py 'bartowski/Llama-3.2-3B-Instruct-GGUF'
	python ../heatmap_generators/stl_evaluation.py 'bartowski/Llama-3.2-3B-Instruct-GGUF' 'translations_Llama-3.2-3B-Instruct-GGUF.pkl' 'config_Llama'

else
	echo "Must specify numbered arg for model name"
fi

