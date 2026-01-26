#!/bin/bash

# TODO: make sure that official model names and models line up correctly
#experiments=("nx_1_ny_2_nz_18" "nx_2_ny_2_nz_18" "nx_3_ny_1_nz_18" "nx_3_ny_2_nz_18" "nx_4_ny_2_nz_18")
#set_name="val_set"
#
## Optional safety check
#if [ ${#models[@]} -ne ${#official_model_names[@]} ]; then
#  echo "Error: 'models' and 'official_model_names' arrays must have the same length."
#  exit 1
#fi
#
#for experiment in "${experiments[@]}"
#do
#  config="config_${experiment}_${set_name}.json"
#  echo "$config"
#
#  i=0
#  for model in "${models[@]}"
#  do
#    # time='2025-10-17_09-55-23'
#    time=$(/usr/bin/date +%F_%H-%M-%S)
#    convo="../stats/${model}/convo_${experiment}_${time}.txt"
#    translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
#
#    echo "$config"
#    python stl_generator_gpt.py "${official_model_names[i]}" "$config" "$experiment" "$time" >| "$convo"
#    echo "Done with config: $config"
#    python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
#
##    python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
##    python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
#    ((i++))
#  done
#done

models=('gpt-4o-2024-08-06') # ('gpt-5.2-2025-12-11')
official_model_names=('gpt-4o-2024-08-06') # ('gpt-5.2-2025-12-11')

experiments=("nx_3_ny_1_nz_18")
set_name="final_test_set" 
# times=("2025-12-30_00-35-54")

i=0
for experiment in "${experiments[@]}"
do
  config="config_${experiment}_${set_name}.json"
  echo "$config"
  for model in "${models[@]}"
  do
    time=$(/usr/bin/date +%F_%H-%M-%S) # "${times[$i]}"
    convo="../stats/${model}/convo_${experiment}_${time}.txt"
    translations="${set_name}_translations_${model}_${experiment}_${time}.pkl"
    consolidated_pkl="../pkl/${set_name}_consolidated_${model}_${experiment}_${time}.pkl"
    filtered_pkl="../pkl/${set_name}_cosine_filtered_${model}_${experiment}_${time}.pkl"
    
    python stl_generator_gpt.py "$model" "$config" "$experiment" "$time" >| "$convo"
    python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
    python ../consolidate/consolidate.py "$model" "$translations" "$config" "$time"
    python ../consolidate/filter_by_cosine_similarity.py "$model" "$consolidated_pkl" "$config" "$time"       
    python ../consolidate/annotate_after_cosine_filter.py "$model" "$filtered_pkl" "$config" "$time"       
  
    # python stl_generator_gpt.py "$model" "$config" "$experiment" "$time" >| "$convo"
    # python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
    # python ../evaluations/generate_semantic_distribution_dict.py "$model" "$translations" "$config" "$time"
  done
  ((++i))
done


  File "/home/llm/llms/bio_llm/stl_generators/stl_generator_gpt.py", line 90, in generate_example_prompt
    literal_translations.append(STL2literal(sample, grammar))
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/llm/llms/bio_llm/stl_generators/../stl2literal.py", line 690, in STL2literal
    tester.visit(tree)
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 423, in visit
    return self._visit_tree(tree)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 431, in _visit_tree
    return f(tree)
           ^^^^^^^
  File "/home/llm/llms/bio_llm/stl_generators/../stl2literal.py", line 183, in omega
    self.visit(node.children[0].children[1])
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 423, in visit
    return self._visit_tree(tree)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 431, in _visit_tree
    return f(tree)
           ^^^^^^^
  File "/home/llm/llms/bio_llm/stl_generators/../stl2literal.py", line 186, in omega
    self.visit(node.children[0])
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 423, in visit
    return self._visit_tree(tree)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 431, in _visit_tree
    return f(tree)
           ^^^^^^^
  File "/home/llm/llms/bio_llm/stl_generators/../stl2literal.py", line 378, in temp_op_g
    self.visit(node.children[2])
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 423, in visit
    return self._visit_tree(tree)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 431, in _visit_tree
    return f(tree)
           ^^^^^^^
  File "/home/llm/llms/bio_llm/stl_generators/../stl2literal.py", line 319, in d_gt
    self.sentence.append(signal_names_dict[node.children[0].children[0]]) # SPECIES
                         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

KeyError: Token('__ANON_1', 'IL8')
model name: gpt-4o-2024-08-06
there was an exception
[Errno 2] No such file or directory: '../pkl/gpt-4o-2024-08-06/final_test_set_translations_gpt-4o-2024-08-06_nx_3_ny_1_nz_18_2026-01-25_16-52-50.pkl'
just loaded the translations
Traceback (most recent call last):
  File "/home/llm/llms/bio_llm/stl_generators/../evaluations/stl_evaluation_v6.py", line 22, in <module>
    print(translations)









'SARSCoV2'
SARSCoV2
getting species name feedback
feedback is bad signal names
Traceback (most recent call last):
  File "/home/llm/llms/bio_llm/stl_generators/stl_generator_gpt.py", line 546, in <module>
    m = feedback + '\n\n' + generate_example_prompt(params['num_examples'])
                            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/llm/llms/bio_llm/stl_generators/stl_generator_gpt.py", line 90, in generate_example_prompt
    literal_translations.append(STL2literal(sample, grammar))
                                ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/llm/llms/bio_llm/stl_generators/../stl2literal.py", line 690, in STL2literal
    tester.visit(tree)
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 423, in visit
    return self._visit_tree(tree)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 431, in _visit_tree
    return f(tree)
           ^^^^^^^
  File "/home/llm/llms/bio_llm/stl_generators/../stl2literal.py", line 183, in omega
    self.visit(node.children[0].children[1])
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 423, in visit
    return self._visit_tree(tree)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 431, in _visit_tree
    return f(tree)
           ^^^^^^^
  File "/home/llm/llms/bio_llm/stl_generators/../stl2literal.py", line 186, in omega
    self.visit(node.children[0])
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 423, in visit
    return self._visit_tree(tree)
           ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/llm/llms/.venv/lib/python3.12/site-packages/lark/visitors.py", line 431, in _visit_tree
    return f(tree)
           ^^^^^^^
  File "/home/llm/llms/bio_llm/stl_generators/../stl2literal.py", line 270, in lt
    self.sentence.append(signal_names_dict[node.children[0].children[0].value]) # name of species --> would need to find and replace using the LLM's dictionary
                         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
KeyError: 'IL8'
model name: gpt-4o-2024-08-06
there was an exception
[Errno 2] No such file or directory: '../pkl/gpt-4o-2024-08-06/final_test_set_translations_gpt-4o-2024-08-06_nx_3_ny_1_nz_18_2026-01-25_16-56-11.pkl'
just loaded the translations
Traceback (most recent call last):
  File "/home/llm/llms/bio_llm/stl_generators/../evaluations/stl_evaluation_v6.py", line 22, in <module>
    print(translations)    
