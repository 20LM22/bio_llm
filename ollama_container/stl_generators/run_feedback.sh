#!/bin/bash
if ["$0" = 0]; then 
	python stl_generator_v2.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B'
elif ["$1" = 1]; then
	python stl_generator_v2.py 'Qwen/Qwen3-0.6B'
else
	python stl_generator_v2.py 'Qwen/Qwen3-1.7B'
fi
