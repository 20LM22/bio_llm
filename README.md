# Translating Biomedical Literature to STL

Using LLMs, this project translates biomedical natural language statements to signal temporal logic (STL). The pipeline generates, filters, and consolidates the STL statements, and between steps a manual evaluation of the semantic correctness of remaining statements can be performed.

## Projct Structure

### 1. `config/`
Configuration files specify model and experiment parameters. Each config file includes:
- Model parameters (temperature, top_p, top_k, etc.)
- Grammar for STL generation
- Number of shots per input sentence, number of semantic correction attempts per shot, and number of syntactic correction attempts per shot
- Input/output dataset paths
- Allowed signal names
- Embedding models

To create a configuration for a new experiment, copy an existing config (e.g., `config_nx_1_ny_0_nz_1_sample_test_set.json`) and update:
- `nx`: number of syntactic correction attempts per shot
- `ny`: number of semantic correction attempts per shot
- `nz`: number of shots per input sentence
- `set_name`: dataset name (e.g., "sample_test_set", "final_test_set")

### 2. `csv_inputs/`
Input CSV files containing biomedical sentences to translate:
- `final_test_set_sentences.csv`: Full test dataset
- `sample_test_set_sentences.csv`: Small, selected sentences from full test dataset

### 3. `stl_generators/`
Main code for NL->STL translation:
- `stl_generator_gpt.py`: Generates STL using OpenAI GPT models (GPT-4o, GPT-5.4, etc.)
- `stl_generator_v7.py`: Generates STL using local LLMs via vLLM (DeepSeek, Qwen, etc.)
- `stl_example_generator.py`: Randomly generates STL examples conforming to specified grammar
- `generate_datasets.py`: Uses `stl_example_generator.py` to compile a curated dataset of examples for `stl_generator_gpt.py` and `stl_generator_v7.py` to include in model prompts

### 4. `post_processing/`
Post-processing pipeline to improve semantic correctness of final results:
- `filter.py`: Filters STL translations based on their semantic similarity to their original sentences
- `consolidate.py`: Consolidates filtered results and removes duplicates using Z3 SMT solver

### 5. `evaluations/`
Evaluation and annotation tools:
- `generate_basic_stats.py`: Produces success rate statistics for extracting and parsing syntactically correct STL from model prompts
- `annotate_initial.py`: Interactive tool to manually label initial STL translations
- `annotate_filtered.py`: Interactive tool to manuallly label filtered translations
- `annotate_consolidated.py`: Interactive tool to manually label consolidated translations

### 6. `pkl/`
Intermediate pickle files organized by model. Key outputs:
- `{model_name}/{set_name}_translations_{model_name}_{experiment}_{timestamp}.pkl`: Raw STL-NL translation pairs from the models
- `{model_name}/{set_name}_filtered_output_{model_name}_{experiment}_{timestamp}.pkl`: Filtered results

### 7. `stats/`
Statistics and analysis files organized by model:
- Extraction/parsing success rates
- Semantic correctness improvement metrics
- Results annotated by semantic correctness after each pipeline step

### 8. `STL2literal.py`
Utility that back-tranlsates STL formulas into its literal meaning in English. Used to compare cosine similarity of original sentences with their STL translations.

---

## How to Use the Main Scripts

### Quick Start

Before running either script, you need to:
1. **Set up your environment**: `pip install -r requirements.txt`
2. Decide which **config file** and **input dataset csv** you want to use

### `run_all_gpt.sh` - For OpenAI GPT Models

**Use this script to generate STL using OpenAI's GPT models (GPT-4o, GPT-5.4, etc.)**

#### Setup:
1. Set `OPENAI_API_KEY` environment variable with your OpenAI API key
2. Edit the script variables at the top:

```bash
models=('gpt-5.4')                              # GPT model name(s)
experiments=("nx_1_ny_0_nz_1")                  # Must match config filename
set_name="sample_test_set"                      # Must match config filename
consolidation_type="general"                    # "general" or "specific"
filter_first=true                               # Filter before consolidate (true) or after (false)
```

#### Running:
```bash
bash run_all_gpt.sh
```

#### What it does:
1. Generates STL translations from input sentences using GPT
2. Computes extraction and parsing statistics
3. Annotates initial translations (interactive - you manually label results)
4. Filters translations by semantic similarity - **note that you can choose to flip steps 4,5 with steps 6,7 by setting `filter_first=false`**
5. Annotates filtered results (interactive - you manually label results)
6. Consolidates results to remove semantic duplicates - **note that you can choose `general` or `specific` consolidation**
7. Annotates consolidated results  (interactive - you manually label results)

#### Output files: TODO update this
- `pkl/{model_name}/{set_name}_translations_{model_name}_{experiment}_{timestamp}.pkl` - Raw results
- `stats/{model_name}/convo_{experiment}_{timestamp}.txt` - Full conversation log
- `stats/{model_name}/*_annotations_*.json` - Annotated results at each stage

---

### `run_all_non_gpt.sh` - For Open-Source LLMs

**Use this script to generate STL using open-source models via vLLM (DeepSeek, Qwen, etc.)**

#### Setup:
1. Edit the script variables at the top:

```bash
# IMPORTANT: These two arrays MUST have the same length!
models=('DeepSeek-R1-Distill-Qwen-1.5B' 'Qwen3-1.7B')                    # Short names (for directories/filenames)
official_model_names=('deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B' 'Qwen/Qwen3-1.7B')  # Full HuggingFace names
experiments=("nx_1_ny_0_nz_1")                  # Must match config filename
set_name="sample_test_set"                      # Must match config filename
consolidation_type="general"                    # "general" or "specific"
filter_first=true                               # Filter before consolidate (true) or after (false)
```

#### Running:
```bash
bash run_all_non_gpt.sh
```

#### What it does:
Same as `run_all_gpt.sh`, but uses open-source models via vLLM

#### Output files:
Same as GPT script, organized by short model name in `models` array

---

## Key Workflow Parameters

- **nx** (correction attempts): Number of syntax correction attempts per shot (0-3+)
- **ny** (semantic checks): Number of semantic feedback iterations (0-3+)
- **nz** (shots): Number of few-shot examples to include (1-5+)
- **consolidation_type**: 
  - `"general"`: Removes formulas that are semantically equivalent using Z3 SMT solver
  - `"specific"`: Alternative consolidation strategy
- **filter_first**: 
  - `true`: Filter by similarity first, then consolidate
  - `false`: Consolidate first, then filter

---

## Interactive Annotation Steps

Both scripts include **interactive annotation** steps where you manually label results:
- **1** = correct STL translation
- **0** or ENTER = incorrect STL translation

You can skip these steps by commenting out the `annotate_*.py` lines in the bash scripts if you want to only run generation or post-processing.

---

## Troubleshooting

**GPT script fails**: Check that `OPENAI_API_KEY` is set and you have API credits
**Non-GPT script fails**: Ensure the model name exists on HuggingFace and you have disk space for model download
**"models" and "official_model_names" arrays must have the same length**: Make sure both arrays in `run_all_non_gpt.sh` have matching lengths

