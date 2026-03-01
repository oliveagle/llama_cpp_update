#!/usr/bin/env bash
# Qwen3-Coder-Next 综合性能基准测试
# 测试不同 prompt 长度和生成长度下的性能

_SROOT="$( cd "$(dirname "$(realpath "$0")")/.." ; pwd -P )"
MODEL_PATH="/mnt/volume3/modelscope_models/Qwen/Qwen3-Coder-Next-GGUF/Q4_K_M/Qwen3-Coder-Next-Q4_K_M-00001-of-00004.gguf"
RESULT_DIR="/tmp/benchmark_qwen3_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULT_DIR"

echo "=========================================="
echo "Qwen3-Coder-Next Comprehensive Benchmark"
echo "=========================================="
echo ""
echo "Model: Qwen3-Coder-Next-Q4_K_M"
echo "Quantization: Q4_K_M"
echo "Size: ~46GB (80B MoE, ~3B active)"
echo "Date: $(date)"
echo ""

# 使用官方推荐的 generation config
echo "官方推荐配置: temp=1.0, top_p=0.95, top_k=40, min_p=0.01"
echo ""

# Test 1: 短代码生成 (典型的代码补全场景)
echo "Test 1: Short Code Generation (Coding Completion)"
echo "  Prompt: 512 tokens | Generation: 256 tokens"
echo "--------------------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 512 -n 256 \
  -ngl 50 \
  -t 16 \
  -r 3 \
  -o csv 2>&1 | tee "$RESULT_DIR/test1_short_code.txt"

# Test 2: 中等代码块生成 (函数实现)
echo ""
echo "Test 2: Medium Code Generation (Function Implementation)"
echo "  Prompt: 1024 tokens | Generation: 512 tokens"
echo "-----------------------------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 1024 -n 512 \
  -ngl 50 \
  -t 16 \
  -r 3 \
  -o csv 2>&1 | tee "$RESULT_DIR/test2_medium_code.txt"

# Test 3: 长上下文代码审查
echo ""
echo "Test 3: Long Context Code Review"
echo "  Prompt: 4096 tokens | Generation: 1024 tokens"
echo "------------------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 4096 -n 1024 \
  -ngl 50 \
  -t 16 \
  -r 2 \
  -o csv 2>&1 | tee "$RESULT_DIR/test3_long_context.txt"

# Test 4: 超长上下文 (接近 100K)
echo ""
echo "Test 4: Ultra Long Context (100K)"
echo "  Prompt: 8192 tokens | Generation: 2048 tokens"
echo "------------------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 8192 -n 2048 \
  -ngl 50 \
  -t 16 \
  -r 1 \
  -o csv 2>&1 | tee "$RESULT_DIR/test4_ultra_context.txt"

# 生成汇总报告
echo ""
echo "=========================================="
echo "Benchmark Summary"
echo "=========================================="
echo ""

echo "Test 1 (Short Code):"
grep -E "^[0-9]" "$RESULT_DIR/test1_short_code.txt" | tail -1

echo ""
echo "Test 2 (Medium Code):"
grep -E "^[0-9]" "$RESULT_DIR/test2_medium_code.txt" | tail -1

echo ""
echo "Test 3 (Long Context):"
grep -E "^[0-9]" "$RESULT_DIR/test3_long_context.txt" | tail -1

echo ""
echo "Test 4 (Ultra Context):"
grep -E "^[0-9]" "$RESULT_DIR/test4_ultra_context.txt" | tail -1

echo ""
echo "Results saved to: $RESULT_DIR"
