#!/usr/bin/env bash
# Qwen3-Coder-Next 上下文扩展性能测试
# 测试不同上下文长度下的 prompt processing 性能

_SROOT="$( cd "$(dirname "$(realpath "$0")")/.." ; pwd -P )"
MODEL_PATH="/mnt/volume3/modelscope_models/Qwen/Qwen3-Coder-Next-GGUF/Q4_K_M/Qwen3-Coder-Next-Q4_K_M-00001-of-00004.gguf"
RESULT_DIR="/tmp/benchmark_context_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULT_DIR"

echo "=========================================="
echo "Qwen3-Coder-Next Context Scaling Test"
echo "=========================================="
echo ""
echo "Testing prompt processing speed at different context sizes"
echo "Model supports up to 256K context window"
echo ""

# 测试不同上下文大小的 prompt processing 性能
echo "Test 1: 4K Context (Small file analysis)"
echo "-----------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 4096 -n 128 \
  -ngl 50 \
  -t 16 \
  -r 3 2>&1 | tee "$RESULT_DIR/context_4k.txt"

echo ""
echo "Test 2: 16K Context (Medium codebase)"
echo "--------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 16384 -n 128 \
  -ngl 50 \
  -t 16 \
  -r 2 2>&1 | tee "$RESULT_DIR/context_16k.txt"

echo ""
echo "Test 3: 32K Context (Large codebase)"
echo "-------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 32768 -n 128 \
  -ngl 50 \
  -t 16 \
  -r 1 2>&1 | tee "$RESULT_DIR/context_32k.txt"

echo ""
echo "Test 4: 64K Context (Very large file)"
echo "--------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 65536 -n 128 \
  -ngl 50 \
  -t 16 \
  -r 1 2>&1 | tee "$RESULT_DIR/context_64k.txt" || echo "Skipped - may OOM"

echo ""
echo "Test 5: 100K Context (Near limit)"
echo "----------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 100000 -n 128 \
  -ngl 50 \
  -t 16 \
  -r 1 2>&1 | tee "$RESULT_DIR/context_100k.txt" || echo "Skipped - may OOM"

# 分析结果
echo ""
echo "=========================================="
echo "Context Scaling Analysis"
echo "=========================================="
echo ""

echo "Prompt Processing Speed (tokens/sec):"
echo ""

for size in 4k 16k 32k 64k 100k; do
    if [ -f "$RESULT_DIR/context_${size}.txt" ]; then
        speed=$(grep -E "^[0-9]+," "$RESULT_DIR/context_${size}.txt" | tail -1 | cut -d',' -f3)
        if [ ! -z "$speed" ]; then
            echo "  ${size}: $speed t/s"
        fi
    fi
done

echo ""
echo "Notes:"
echo "  - Speed typically decreases as context grows"
echo "  - Memory usage increases with context size"
echo "  - Flash Attention (-fa) helps maintain speed"
echo ""
echo "Results saved to: $RESULT_DIR"
