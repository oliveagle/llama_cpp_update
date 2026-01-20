#!/usr/bin/env bash

_SROOT="$( cd "$(dirname "$(realpath "$0")")" ; pwd -P )"

MODEL="/mnt/volume3/modelscope_models/ngxson/GLM-4___7-Flash-GGUF/GLM-4.7-Flash-Q4_K_M.gguf"

echo "========================================"
echo "GLM-4.7-Flash Benchmark"
echo "========================================"
echo ""

for ngen in 512 1024 2048 4096; do
    echo ">>> n-gen = $ngen"
    $_SROOT/current/llama-bench \
      -m "$MODEL" \
      -p 512 -n $ngen \
      --no-warmup \
      --mmap 0 \
      --flash-attn 0 2>&1 | grep -v "^load_backend\|^ggml_vulkan"
    echo ""
done
