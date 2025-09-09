import pickle, pandas
from collections import defaultdict

model_names = ["DeepSeek-R1-Distill-Qwen-1.5B", "gpt-4o-2024-08-06", "Qwen3-1.7B"]

for model_name in model_names:
    try:
        with open(f'../pkl/{model_name}/redo_gpt_test_translations_{model_name}_shots_18_syntax_2_semantic_2.pkl', 'rb') as f:
            translations = pickle.load(f)
            print(f'Loaded {f}')
    except Exception as e:
        print(e)

    res = defaultdict(list)

    # fill in semantic successes
    for index, row in translations.iterrows():

        row_subset = pandas.DataFrame()
        row_counter = 0

        syntactically_valid_translations = []

        for i in range(18):
            relevant_translations_cols = []
            for col in translations.columns:
                if f'shot{i}-' in col:
                    relevant_translations_cols.append(col)
            row_subset = row[relevant_translations_cols] # row subset has everything with shot-i in the column name

            for entry in row_subset:
                if entry != 'STL could not be extracted' and entry != 'STL could not be parsed' and entry is not None:
                    # add this entry
                    syntactically_valid_translations.append(entry)

        res[row['input statement']] = syntactically_valid_translations

    # # print these out to the user and have them mark whether they think they're good or not
    translations_total = 0
    for key in res.keys():
        translations_total += len(res[key])

    translations_count = 0

    for key in res.keys():
        new_syn_valid_arr = []
        for stl in res[key]:
            print(f"{translations_count}/{translations_total} annotations completed.")
            translations_count += 1
            # need to ask the user to mark the annotation as a 0 or 1
            print(f"Sentence: {key}")
            print(f"STL: {stl}")
            choice = input("1 for yes, 0 for no: ")
            # then need to construct a new array that we will replace the current one in the dictionary with
            # but this array will have the user's annotation
            new_syn_valid_arr.append((stl,choice))
        res[key] = new_syn_valid_arr

    correct = 0
    total = 0

    for key in res.keys():
        for stl, choice in res[key]:
            total += 1
            try:
                if int(choice) == 1:
                    correct += 1
            except Exception as e:
                pass

    print(f"Correct: {correct}")
    print(f"Total: {total}")

    p = pandas.DataFrame(data=[[correct, total]], columns=["correct", "total"]) # deepseek has 17/347 correct
    p.to_csv(f'../stats/{model_name}/semantic_correct_test_set_{model_name}_shots_18_syntax_2_semantic_2.csv', index=False)
