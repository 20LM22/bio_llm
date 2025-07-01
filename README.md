Models should be placed in ``~/ollama-container/models`` and downloaded from [(ollama.com/library)]. 

When running Ollama models on Savio, first activate Ollama within an Apptainer using:
``
bash start_ollama_server.sh
``

This requires first obtaining the file ``~/ollama-container/ollama.sif`` by running:
``
apptainer build ollama.sif docker://ollama/ollama
``