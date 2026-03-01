#!/usr/bin/env bash

_SROOT="$( cd "$(dirname "$(realpath "$0")")" ; pwd -P )"

$_SROOT/current/llama-bench \
  -m /mnt/volume3/modelscope_models/ngxson/GLM-4___7-Flash-GGUF/GLM-4.7-Flash-Q4_K_M.gguf \
  -p 0 -n 512 \
  --no-warmup \
	--mmap 0 \
  --flash-attn 0
