Overview of the filesystem:

1) Config. Specifies all model, feedback, etc. parameters. There are many versions, but the newest is [config_nx_0_ny_0_nz_0_test_set.json](https://github.com/hannakrasowski/bio_llm/blob/main/config/config_nx_0_ny_0_nz_0_test_set.json), and new experiments will use copies of this version with the nx (num_correction_attempts_per_shot), ny (num_semantic_checks), nz (num_shots_per_input_sentence), and "set_name" (test set vs. val set) updated.
2) CSV_inputs. ``input_sentences.csv`` contains the input sentences. There are two versions, test and val.
3) Evaluations.
   - ``stl_evaluation_v6.py``. Produces tables of statistics regarding model performance by reading the ``{set_name}_translations_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.pkl`` file produced by ``stl_generator_v7.py`` and ``stl_generator_gpt.py``. The important tables include:
      - ``{set_name}_stats_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.csv .pkl`` # This produces extraction, syntactically correct rates/counts
      - ``{set_name}_improvements_nx_{syntaxs}_ny_{semantics}_nz_{shots}_{time}.csv`` # Number of times semantic feedback helps + how often it's reached
   - ``generate_semantic_distribution_dict.py``. Interactive program to assign labels to results of STL generation. Works on the top 3 and bottom 3 sentences seperately and also produces an overall count of how many correct/incorrect STL statements there were. This needs to run before you make the histograms with ``generate_semantic_distribution_plots.py``.
   - ``generate_semantic_distribution_plots.py``. Using labeled results, produces histogram of the top 3 sentences and bottom 3 sentences.
5) Images. Contains figures organized per-model. They are nested inside the corresponding model folder.
6) Pkl. Contains intermediate data structures organized per-model. The really important one is ``../pkl/{model_name}/{set_name}_translations_{model_name}_{config}_{time}.pkl`` because this is the results from the models that we work with in the evaluation parts.
7) Stats. Contains statistics organized per-model. The important ones are ``{set_name}_stats_nx_{syntax_count}_ny_{semantic_count}_nz_{shot_count}_{time}.csv .pkl`` and ``{set_name}_improvements_nx_{syntaxs}_ny_{semantics}_nz_{shots}_{time}.csv`` like I pointed out in (3).
8) STL_generators.
   - ``generate_datasets.py``. Produces the curated dataset. This is run infrequently.
   - ``stl_example_generator.py``. Randomly generates STL that conforms to the grammar. This is your code from earlier in the summer.
   - ``stl_generator_v7.py`` and ``stl_generator_gpt.py``. The main files responsible for producing STL. ``stl_generator_v7.py`` is for non-GPT models and ``stl_generator_gpt.py`` is for GPT models. They include all the feedback steps and querying of the models. The outputs are the main ``../pkl/{model_name}/{set_name}_translations_{model_name}_{config}_{time}.pkl`` file of the STL statements, and I also record the raw conversation by piping the output to ``../stats/${model}/config_${experiment}_${time}.txt`` so that it can be viewed in detail.
   - ``run_all_gpt.sh`` and ``run_all_non_gpt.sh``. Bash scripts for running the STL generator and evaluation metrics. They are set up to run the generator and then run ``stl_evaluation_v6.py`` followed by ``generate_semantic_distribution_dict.py`` and ``generate_semantic_distribution_dict.py``, but you can also comment out the later parts to only run the STL generation or individual steps of the evaluation.
9) ``STL2literal.py``. Responsible for literal backtranslation. The overall Tester class is used to walk the parsed tree. When you input a tree, it starts at the top and finds rules/terminals that match up with the function names inside the Tester, going to other functions if they are explicitly called (tree.visit()) within the function you're currently in.

