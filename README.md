These are the steps to running Ollama on Savio:

1) Go to [https://ood.brc.berkeley.edu/pun/sys/dashboard](https://ood.brc.berkeley.edu/pun/sys/dashboard), click on "Clusters -> BRC Shell Access"

2) Request a GPU using:

  ``
  srun --pty -A fc_control -p savio2_1080ti -t 01:00:00 bash -i
  ``
  
  Note that other GPU partitions can be found [here](https://docs-research-it.berkeley.edu/services/high-performance-computing/user-guide/hardware-config/); however, they tend to take a long time to be ready.

3) To test that everything is working, navigate to ``~/ollama-container``, then run:

```apptainer build ollama.sif docker://ollama/ollama # If ollama.sif already exists, no need to build it again
apptainer run --nv ollama.sif serve & # Start the Ollama server, should be available at http://localhost:11434
curl http://localhost:11434 # Make sure that the Ollama server is running
apptainer run --nv ollama.sif run deepseek-r1:1.5b # If the deepseek model is not already downloaded, running this will pull the model, then open an interactive chat session; otherwise, the chat session should start immediately
# When done using the model, use /bye to exit the chat
```

Alternatively, if you just want to download new models from [ollama.com/library](ollama.com/library), but you don't need to run them, after starting the Ollama server, run the following:

``apptainer run --nv ollama.sif pull <model name>``

4 )  After you are sure that the right models have been downloaded and the Ollama server is running, activate a virtual environment and make sure ``ollama`` is pip installed:

``conda activate ollama_venv # Or 'conda activate <your choice of name for virtual environment>'`` 

5) Run ``python test.py``. It connects to the Ollama server and sends a prompt. It returns the model response and how long it took. Using vim, you can change the prompt, the type of model (make sure you download any models you need).

### Note: still need to figure out a cleaner way to do this, but to shut down the Ollama server, use:
```
htop -u <your username>
# F5 to search for "ollama"
# F? to delete all "ollama/serve" related lines
q to exit
```

### Note: also need to figure out where the models are being saved --> I think it's in ``<user_name>/.ollama/models``. If the models are too large for the 30GB of Savio space, we can also explore putting them in the scratch space.

