#!/usr/bin/env bash
# Qwen3-Coder-Next AMD GPU (Vulkan) 性能测试
# 单独测试 AMD Radeon 8060S 核显性能

_SROOT="$( cd "$(dirname "$(realpath "$0")")/.." ; pwd -P )"
MODEL_PATH="/mnt/volume3/modelscope_models/Qwen/Qwen3-Coder-Next-GGUF/Q4_K_M/Qwen3-Coder-Next-Q4_K_M-00001-of-00004.gguf"
RESULT_DIR="/tmp/benchmark_amd_gpu_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULT_DIR"

echo "=========================================="
echo "Qwen3-Coder-Next AMD GPU (Vulkan) Test"
echo "=========================================="
echo ""
echo "Hardware: AMD Radeon 8060S (Integrated GPU)"
echo "Backend: Vulkan"
echo "Note: Uses shared system memory"
echo ""

# Stop running llama-server to free model file
echo "Stopping llama-server..."
$_SROOT/kill_auto_switch.sh > /dev/null 2>&1
sleep 2

# 检查 AMD GPU 是否可用
echo "Detecting AMD GPU..."
GGML_VULKAN_DEBUG=1 $_SROOT/current/llama-server --help 2>&1 | grep -A 2 "Radeon"

echo ""
echo "Starting benchmarks on AMD GPU only..."
echo ""

# Test 1: 基础性能测试
echo "Test 1: Basic Performance (512 prompt, 256 gen)"
echo "------------------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 512 -n 256 \
  -ngl 99 \
  -sm none \
  -mg 1 \
  -t 8 \
  -r 3 2>&1 | tee "$RESULT_DIR/amd_basic.txt"

# Test 2: 代码生成场景
echo ""
echo "Test 2: Code Generation (1024 prompt, 512 gen)"
echo "-----------------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 1024 -n 512 \
  -ngl 99 \
  -sm none \
  -mg 1 \
  -t 8 \
  -r 2 2>&1 | tee "$RESULT_DIR/amd_codegen.txt"

# Test 3: 长上下文
echo ""
echo "Test 3: Long Context (2048 prompt, 256 gen)"
echo "--------------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 2048 -n 256 \
  -ngl 99 \
  -sm none \
  -mg 1 \
  -t 8 \
  -r 1 2>&1 | tee "$RESULT_DIR/amd_longctx.txt"

# Test 4: 最大层数测试 (可能OOM)
echo ""
echo "Test 4: Maximum Layers (testing memory limit)"
echo "----------------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 512 -n 128 \
  -ngl 99 \
  -sm none \
  -mg 1 \
  -t 8 \
  -r 1 2>&1 | tee "$RESULT_DIR/amd_max_layers.txt" || echo "Note: May OOM due to integrated GPU memory limit"

echo ""
echo "=========================================="
echo "AMD GPU Results Summary"
echo "=========================================="
echo ""

for test in basic codegen longctx max_layers; do
    file="$RESULT_DIR/amd_${test}.txt"
    if [ -f "$file" ]; then
        echo "Test: $test"
        grep -E "^[0-9]+," "$file" | tail -1
        echo ""
    fi
done

echo ""
echo "Comparison Notes:"
echo "  - AMD 8060S is integrated GPU (shares system memory)"
echo "  - Expected to be slower than NVIDIA V100"
echo "  - Useful for comparison with V100 and multi-GPU setups"
echo ""
echo "Results saved to: $RESULT_DIR"
echo ""
echo "Restarting llama-server..."
nohup $_SROOT/auto_switch.sh >> /home/oliveagle/data/log/llama_cpp.log 2>&1 &
echo "Server restarted."
