#!/usr/bin/env bash
# 验证 Vulkan 多 GPU 层分割性能测试脚本
# Test Vulkan multi-GPU split mode performance

_SROOT="$( cd "$(dirname "$(realpath "$0")")/.." ; pwd -P )"
MODEL_PATH="/mnt/volume3/modelscope_models/Qwen/Qwen3-Coder-Next-GGUF/Q4_K_M/Qwen3-Coder-Next-Q4_K_M-00001-of-00004.gguf"

echo "=========================================="
echo "Vulkan Multi-GPU Split Mode Benchmark"
echo "=========================================="
echo ""
echo "Hardware Detected:"
echo "  GPU 0: NVIDIA Tesla PG503-216 (V100) - 32GB"
echo "  GPU 1: AMD Radeon 8060S - Shared Memory"
echo ""

# Stop running llama-server to free model file
echo "Stopping llama-server..."
$_SROOT/kill_auto_switch.sh > /dev/null 2>&1
sleep 2

# 测试不同的分割比例
echo "Test 1: 75% V100 + 25% AMD (Layer Split)"
echo "----------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -ngl 99 \
  -sm layer \
  -ts 0.75,0.25 \
  -p 512,1024,2048 \
  -n 128 \
  -t 4 2>&1 | tee /tmp/bench_vulkan_75_25.log

echo ""
echo "Test 2: 50% V100 + 50% AMD (Layer Split)"
echo "----------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -ngl 99 \
  -sm layer \
  -ts 0.5,0.5 \
  -p 512,1024,2048 \
  -n 128 \
  -t 4 2>&1 | tee /tmp/bench_vulkan_50_50.log

echo ""
echo "Test 3: 90% V100 + 10% AMD (Layer Split)"
echo "----------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -ngl 99 \
  -sm layer \
  -ts 0.9,0.1 \
  -p 512,1024,2048 \
  -n 128 \
  -t 4 2>&1 | tee /tmp/bench_vulkan_90_10.log

echo ""
echo "=========================================="
echo "Comparison Summary"
echo "=========================================="
echo ""
echo "Extracting performance metrics..."

echo ""
echo "75/25 Split:"
grep -E "(pp|tg)" /tmp/bench_vulkan_75_25.log | tail -5

echo ""
echo "50/50 Split:"
grep -E "(pp|tg)" /tmp/bench_vulkan_50_50.log | tail -5

echo ""
echo "90/10 Split:"
grep -E "(pp|tg)" /tmp/bench_vulkan_90_10.log | tail -5

echo ""
echo "Logs saved to /tmp/bench_vulkan_*.log"
echo ""
echo "Restarting llama-server..."
nohup $_SROOT/auto_switch.sh >> /home/oliveagle/data/log/llama_cpp.log 2>&1 &
echo "Server restarted."
