#!/bin/bash
if [ "$1" = "0" ]; then 
	python stl_generator_v5.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B-1.5B' 'config_v4.json' > deepseek_convo.txt
	python ../heatmap_generators/stl_evaluation_v5.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B-1.5B' 'translations_DeepSeek-R1-Distill-Qwen-1.5B.pkl' 'config_v4.json'
elif [ "$1" = "1" ]; then
	python stl_generator_v5.py 'Qwen/Qwen3-0.6B' 'config_v4.json'
	python ../heatmap_generators/stl_evaluation_v5.py 'Qwen/Qwen3-0.6B' 'translations_Qwen3-0.6B.pkl'
elif [ "$1" = "2" ]; then
	python stl_generator_v5.py 'Qwen/Qwen3-1.7B' 'config_v4.json' > qwen_convo.txt
	python ../heatmap_generators/stl_evaluation_v5.py 'Qwen/Qwen3-1.7B' 'translations_Qwen3-1.7B.pkl' 'config_v4.json'
elif [ "$1" = "3" ]; then
	python stl_generator_v5.py 'TheBloke/Mistral-7B-Instruct-v0.2-GPTQ' 'config_v4.json'
	python ../heatmap_generators/stl_evaluation_v5.py 'TheBloke/Mistral-7B-Instruct-v0.2-GPTQ' 'translations_Mistral-7B-Instruct-v0.2-GPTQ.pkl' 'config_v4.json'
elif [ "$1" = "4" ]; then
	python stl_generator_v5.py 'bartowski/Llama-3.2-3B-Instruct-GGUF' 'config_v4.json'
	# python ../heatmap_generators/stl_evaluation_v5.py 'bartowski/Llama-3.2-3B-Instruct-GGUF' 'translations_Llama-3.2-3B-Instruct-GGUF.pkl'
else
	echo "Must specify numbered arg for model name"
fi

