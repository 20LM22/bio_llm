#!/bin/bash

python stl_generator_v2.py 'deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B'
echo 'Deepseek Completed'
python stl_generator_v2.py 'Qwen/Qwen3-0.6B'
echo 'Qwen 0.6B Completed'
python stl_generator_v2.py 'Qwen/Qwen3-1.7B'
echo 'Qwen 1.7B Completed'

