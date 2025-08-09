1) Config. Specifies all model, feedback, etc. parameters.
2) CSV_inputs. ``input_sentences.csv`` contains the input sentences.
3) Evaluations.
   4) ``stl_evaluation_v6.py``. Produces tables of statistics regarding model performance.
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

