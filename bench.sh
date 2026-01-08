#!/usr/bin/env bash

_SROOT="$( cd "$(dirname "$(realpath "$0")")" ; pwd -P )"

$_SROOT/current/llama-bench \
  -m /mnt/volume3/modelscope_models/lefromage/Qwen3-Next-80B-A3B-Instruct-GGUF/Qwen__Qwen3-Next-80B-A3B-Instruct-MXFP4_MOE.gguf \
  -p 0 -n 512 \
  --no-warmup \
	--mmap 0 \
  --flash-attn 0
