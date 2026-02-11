#!/bin/bash

models=('gemini-3-flash-preview') 
official_model_names=('gemini-3-flash-preview')

experiments=("nx_3_ny_1_nz_18")
set_name="final_test_set" 
times=("2026-02-09_18-13-44") # ("2026-01-25_17-47-50")

i=0
for experiment in "${experiments[@]}"
do
  config="config_${experiment}_${set_name}.json"
  echo "$config"
  for model in "${models[@]}" 
  do 
    time="${times[$i]}" # $(/usr/bin/date +%F_%H-%M-%S)
    convo="../stats/${model}/convo_${experiment}_${time}.txt"
    
    translations="../pkl/${model}/${set_name}_translations_${model}_${experiment}_${time}.pkl"
    translations_annotations_stats="../pkl/${set_name}_semantic_labels_${model}_${experiment}_${time}.pkl"
    
    filtered_output="../pkl/${model}/${set_name}_filtered_output_${model}_${experiment}_${time}.pkl"
    filtered_annotations_output="../pkl/${model}/${set_name}_filtered_output_annotations_${model}_${experiment}_${time}.pkl"

    consolidated_output="../stats/${model}/${set_name}_consolidated_output_${model}_${experiment}_${time}.json"
    consolidated_annotations_output="../stats/${model}/${set_name}_annotate_consolidated_${model}_${experiment}_${time}.json"
  
    input_sentences_csv="../csv_inputs/final_test_set_sentences.csv"

    echo "$model"
    echo "$translations"
    echo "$config"
    echo "$time"

    # python stl_generator_gemini.py "$model" "$config" "$experiment" "$time" >| "$convo"
    # python ../evaluations/stl_evaluation_v6.py "$model" "$translations" "$config" "$time"
    # python ../consolidate/filter_by_cosine_similarity.py "$model" "$translations" "$config" "$time"       
    # python ../consolidate/consolidate.py "$model" "$filtered_output" "$config" "$time"
    # python ../consolidate/annotate_consolidated.py "$model" "$consolidated_output" "$config" "$time"
    # "$translations" "$filtered_annotations_output" "$consolidated_annotations_output"      
    python ../consolidate/annotate_consolidated_stats.py "$translations" "$consolidated_annotations_output" "$input_sentences_csv"

  done
  ((++i))
done

# Sentences NOT in consolidated:
# - Most cytokines observed in previous publications of “cytokine storms” in association with disease severity (9, 10, 14) were observed only in the late stage of severe cases, mostly at 4 weeks after onset of symptom — for example, IL-6, IL-12, IL-1β, IFN-γ, IL-17, and IL-27.
# - These asymptomatic infections were characterized by transiently high levels of IL-1b, IL-6, TNFα, the b chemokine macrophage chemotactic protein-1, MIP-1α, and MIP-1β in plasma about one week after the first potentially infectious contact, followed two weeks later by the emergence of EboZ-specific IgG [11].
# - IFNα, IL-12 and IL-8 were undetectable in all the plasma samples tested.
# - Elevated plasma concentrations of IL-1RA or neopterin from a few days after disease onset are potential markers for fatal outcome, while high levels of sTNF-RI are only significant the last days before death.
# - IL-6 and MCP-1 showed marked increases by day 4 after infection; and MIP1α and MIP-1β exhibited moderate increases on day 4, coinciding with gene expression data. By day 5 these four cytokines were elevated, and there was also an increase in TNF-α and IL-18 in serum.
# - The earliest major transcriptional response apparent in all animals by day 2 or 3 was an increase in transcript levels of a large set of interferon (IFN) regulated genes (Figure 1), including the following: myxovirus resistance protein (MX)1 and MX2, IFN-γ inducible protein-10, 2'-5' oligoadenylate synthetase-1, -2, and -3, guanylate binding protein-1 and -2, signal transducer and activators of transcription (STAT)-1, double-stranded DNA activated protein kinase, and IFN-γ receptors 1 and 2.
# - In addition, several chemokines (macrophage inflammatory protein [MIP]-1α, MIP-1β, growth related oncogene-α, growth related oncogene-β, monocyte chemoattractant protein [MCP]-1, MCP-2, MCP-3, and MCP-4) exhibited increased transcript levels at days 4 to 6 after infection in all animals (Figure 2a).
# - A significant increase in cytokine and chemokine transcripts was observed at days 4 to 6 after infection (Figure 2a). Transcripts encoding the proinflammatory cytokines IL-1β, IL-6, IL-8, and tumor necrosis factor (TNF)-α were markedly increased in late-stage animals (average fold increase at day 5 after infection: IL-1β, 3.9; IL-6, 4.3; IL-8, 11.3; and TNF-α, 5.2; Figure 2b).
# - Transcripts for several other cytokines (IL-2, IL-4, IL-10, and IL-12) were detected on the array, but their levels did not change significantly during the course of infection.
# - We first examined the relative cytokine and chemokine levels in serum samples collected 6 days following EBOV challenge by using a multiplex-based bead assay. Quantitative analysis revealed that multiple Th1 cytokines, including gamma interferon (IFN-γ), interleukin-2 (IL-2), and tumor necrosis factor alpha (TNF-α), were significantly reduced in Tim-1/ mice compared to EBOV-infected wild-type mice (Fig. 2A to C), while IL-12p40 was increased (Fig. 2B).      
# - Flow cytometry analysis demonstrated that at day 6, gated CD4 T cells from Tim-1/ mice appeared to produce elevated levels of IL-2, IFN-γ, and TNF-α compared to wild-type, EBOV-infected mice (Fig. 2D).
# - In this previous study, levels of all pro-inflammatory cytokines tested (IL-1b , TNFα , IL-6, MCP and, MIP-1α /β ) fell to normal within two to three days of their initial observation [14].
# - The IL-1 receptor antagonist (IL-1RA) and the two soluble TNF receptors (sTNFRI and sTNFRII) were found at moderate to high concentrations (3±7 ng/ml IL-1RA versus 1¥6 ng/ml in 10 endemic controls; 1¥3±2¥6 ng/ml sTNFRI versus 1¥8 ng/ml; 3¥5± 7 ng/ml sTNFRII versus 5 ng/ml) 7 days after initial exposure. Values fell two days later to normal endemic control levels, simultaneously with the fall in pro-inflammatory cytokines.
# - No T-cell-derived cytokines (IL-2, IL-4, IL-5, IL-12 and, IFNγ ) were detected in the plasma of the 7 asymptomatic subjects at any time.
# - IL-2, IL-4 and IL-10 and IL-12 showed identical mRNA expression profiles, peaking 9 days after initial exposure (i.e. at the end of the inflammatory process), and falling below the detection limit 7 days later (Fig. 3).
# - At days 4 and 5 postinfection, platelets, lymphocytes, reticulocytes, and monocyte counts and percentages all began to gradually decrease, while neutrophil counts/percentages increased.
# - In following up of viremia, there was no viral RNA detected in the plasma of group A and group B animals on day 2, while on day 3 viral RNA loads were measurable in almost all assayed animals and increased thereafter.
# - In the CSF, levels of MCP-1, IL1Ra, IL-2, G-CSF, and IL-18 started increasing on day 5 postinfection.
# - Increases in IL-15, IL-1β, IL-6, and TNF-α levels were slightly more delayed in the CSF, beginning closer to day 6 postinfection.
# - There is increased VP40, CC3/PARP1, GLUT1 and GLUT3 staining in the brainstem, more so on days 6 and 7 compared to day 4 post inoculation (n = 10 animals).
# - Therefore, we analyzed control and TIM-1-/- organs following EBOV GPΔO/rVSV infection for the chemokines, CXCL10 (IP-10) and CCL2 (MCP-1). At least one of the two transcripts for these proinflammatory chemokines in all three organs was elevated in the control mice at both day 3 and/or 5 of infection compared to the TIM-1-/- mouse tissues (Fig 4).
# - The animal that survived challenge experienced a 3.7-fold increase in triglycerides over baseline on day 10, which returned to baseline by day 14 (data not shown).

# Sentences NOT in consolidated:
# - Seen in 22 set: Most cytokines observed in previous publications of “cytokine storms” in association with disease severity (9, 10, 14) were observed only in the late stage of severe cases, mostly at 4 weeks after onset of symptom — for example, IL-6, IL-12, IL-1β, IFN-γ, IL-17, and IL-27.
# - Seen in 22 set: These asymptomatic infections were characterized by transiently high levels of IL-1b, IL-6, TNFα, the b chemokine macrophage chemotactic protein-1, MIP-1α, and MIP-1β in plasma about one week after the first potentially infectious contact, followed two weeks later by the emergence of EboZ-specific IgG [11].
# - Seen in 22 set: IL-6 and MCP-1 showed marked increases by day 4 after infection; and MIP1α and MIP-1β exhibited moderate increases on day 4, coinciding with gene expression data. By day 5 these four cytokines were elevated, and there was also an increase in TNF-α and IL-18 in serum.
# - Seen in 22 set: In addition, several chemokines (macrophage inflammatory protein [MIP]-1α, MIP-1β, growth related oncogene-α, growth related oncogene-β, monocyte chemoattractant protein [MCP]-1, MCP-2, MCP-3, and MCP-4) exhibited increased transcript levels at days 4 to 6 after infection in all animals (Figure 2a).
# - Seen in 22 set: In this previous study, levels of all pro-inflammatory cytokines tested (IL-1b , TNFα , IL-6, MCP and, MIP-1α /β ) fell to normal within two to three days of their initial observation [14].
# - Seen in 22 set: No T-cell-derived cytokines (IL-2, IL-4, IL-5, IL-12 and, IFNγ ) were detected in the plasma of the 7 asymptomatic subjects at any time.
# - Seen in 22 set: IL-2, IL-4 and IL-10 and IL-12 showed identical mRNA expression profiles, peaking 9 days after initial exposure (i.e. at the end of the inflammatory process), and falling below the detection limit 7 days later (Fig. 3).
# - Seen in 22 set: At days 4 and 5 postinfection, platelets, lymphocytes, reticulocytes, and monocyte counts and percentages all began to gradually decrease, while neutrophil counts/percentages increased.
# - Seen in 22 set: There is increased VP40, CC3/PARP1, GLUT1 and GLUT3 staining in the brainstem, more so on days 6 and 7 compared to day 4 post inoculation (n = 10 animals).