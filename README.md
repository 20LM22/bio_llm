Overview of the filesystem: # not done yet

1) Config. Specifies all model, feedback, etc. parameters. There are many versions, but the newest is [config_nx_0_ny_0_nz_0_test_set.json](https://github.com/hannakrasowski/bio_llm/blob/main/config/config_nx_0_ny_0_nz_0_test_set.json), and new experiments will use copies of this version with the nx (num_correction_attempts_per_shot), ny (num_semantic_checks), nz (num_shots_per_input_sentence), and "set_name" (test set vs. val set) updated.
2) CSV_inputs. ``input_sentences.csv`` contains the input sentences. There are two versions, test and val.
3) Evaluations.
   4) ``stl_evaluation_v6.py``. Produces tables of statistics regarding model performance by reading the "{set_name}_translations_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl" file produced by stl_generator_v7.py and stl_generator_gpt.py. The important tables include:
      5) {set_name}_stats_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.csv .pkl # This produces number of syntactically correct,
      6) {set_name}_improvements_nx_{syntaxs}_ny_{semantics}_nz_{shots}_{time}.csv'
      7) {set_name}_improvements_nx_{syntaxs}_ny_{semantics}_nz_{shots}_{time}.csv' # Same thing as above but on a per-sentence basis
   4) ``generate_semantic_distribution_dict.py``. Interactive program to assign labels to results of STL generation.
   5) ``generate_semantic_distribution_plots.py``. Using labeled results, produces histograms.
5) Images. Contains figures organized per-model.
6) Pkl. Contains intermediate data structures organized per-model.
7) Stats. Contains statistics organized per-model.
8) STL_generators.
   9) ``generate_datasets.py``. Produces the curated dataset.
   10) ``stl_base.py``. Randomly generates STL that conforms to the grammar.
   11) ``stl_generator_v7.py``. The main file responsible for producing STL.
   12) ``smaller_run.sh``. Bash script for running the STL generator and evaluation metrics.
9) ``STL2literal.py``. Responsible for literal backtranslation.

