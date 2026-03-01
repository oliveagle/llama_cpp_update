#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$(dirname "$(realpath "$0")")" ; pwd -P )"
_SROOT="$(dirname "$SCRIPT_DIR")"

$_SROOT/current/llama-server \
  -m /mnt/volume3/modelscope_models/prithivMLmods/Qwen3-VL-8B-Instruct-abliterated-v2-GGUF/Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0.gguf \
  --mmproj /mnt/volume3/modelscope_models/prithivMLmods/Qwen3-VL-8B-Instruct-abliterated-v2-GGUF/Qwen3-VL-8B-Instruct-abliterated-v2.mmproj-Q8_0.gguf \
  --models-max 1 \
  --models-preset presets/mypresets.ini \
	--host 0.0.0.0 --port 8000  \
	--no-warmup \
	-fa on --jinja --reasoning-format auto

	# --no-mmap \
  #dd--mlock -np 4 -kvu \
	# -cmoe \ crash
	# -c 40960 \
	# -b 1024 -ub 1024 \
	# -n -2 \
