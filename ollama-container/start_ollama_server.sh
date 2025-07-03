#!/bin/bash

# Configuration
CONTAINER_IMAGE="/global/home/users/laurenmalek/bio_llm/ollama-container/ollama.sif"
INSTANCE_NAME="ollama-apptainer"
MODEL_PATH="/global/home/users/laurenmalek/bio_llm/ollama-container/models"
PORT=11434

# Start Apptainer instance without GPU and writable tempfs
apptainer instance start \
  --nv \
  --writable-tmpfs \
  --bind "$MODEL_PATH" \
  "$CONTAINER_IMAGE" "$INSTANCE_NAME"

# Start Ollama serve inside the container in the background
apptainer exec instance://$INSTANCE_NAME \
  bash -c "export OLLAMA_MODELS=$MODEL_PATH && ollama serve &"
echo "🦙 Ollama is now serving at http://localhost:$PORT"
