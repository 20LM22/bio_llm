# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: Copyright contributors to the vLLM project
    # Generate texts from the prompts.
    # The output is a list of RequestOutput objects
    # that contain the prompt, generated text, and other information.

from vllm import LLM, SamplingParams

prompt = 'What color is the sky?'

# Create a sampling params object.
sampling_params = SamplingParams(
        temperature=0.7,
        top_p=0.95,
        max_tokens=1024)
llm = LLM(model="deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
    dtype="half",
    max_model_len=8192,
    gpu_memory_utilization=0.8)

output = llm.generate(prompt, sampling_params)
print(output[0].outputs[0].text)
print(len(output[0].outputs[0].text))

# for output in outputs:
#    prompt = output.prompt
#    generated_text = output.outputs[0].text
