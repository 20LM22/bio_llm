# Translating Biomedical Literature to STL

Using LLMs, this project translates biomedical natural language statements to signal temporal logic (STL). The pipeline generates, filters, and consolidates the STL statements, and between steps a manual evaluation of the semantic correctness of remaining statements can be performed.

If you use any part of this project in your work, please cite: 
```
Hanna Krasowski, Lauren E. Malek, Sanjit A. Seshia, Murat Arcak; Proceedings of the International Conference on Neuro-symbolic Systems, PMLR X:X-X
```
Additionally, further details on the structure and purpose of the tool may be found within the paper.

## Project Structure

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
- `consolidate.py`: Consolidates results and removes duplicates using Z3 SMT solver

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

#### Output files:
- `stats/{model_name}/*_raw_results_*.csv` - Raw STL results
- `stats/{model_name}/convo_*.txt` - Full conversation log
- `stats/{model_name}/*_extraction_parsing_stats_*.csv` - STL extraction and syntactic parsing correctness rates
- `stats/{model_name}/*_semantic_improvements_*.csv` - Semantic improvements between semantic feedback attempts
- `stats/{model_name}/*_annotations_*.csv` - Annotated results at each pipeline stage

---

### `run_all_non_gpt.sh` - For Local LLMs

**Use this script to generate STL using local models via vLLM (DeepSeek, Qwen, etc.)**

#### Setup:
1. Edit the script variables at the top:

```bash
# Make sure these two arrays have the same length!
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
Same as `run_all_gpt.sh`, but uses local models via vLLM

#### Output files:
Same as GPT script, organized by short model name in `models` array

---

## Summary of Key Workflow Parameters

- **nx** (syntactic correction attempts): Number of syntax correction attempts per shot (0-3+)
- **ny** (semantic correction attempts): Number of semantic feedback iterations (0-3+)
- **nz** (shots): Number of shots per input sentence to run (1-5+)
- **consolidation_type**: 
  - `"general"`: Keep STL formulas that are superset of other STL formulas, i.e., the most general ones
  - `"specific"`: Keep STL formulas that are a subset of other STL formulas, i.e., the most specific ones
- **filter_first**: 
  - `true`: Filter first, then consolidate
  - `false`: Consolidate first, then filter

---

## Interactive Annotation Steps

Both scripts include **interactive annotation** steps where you manually label results:
- **1** = correct STL translation
- **0** or ENTER = incorrect STL translation
