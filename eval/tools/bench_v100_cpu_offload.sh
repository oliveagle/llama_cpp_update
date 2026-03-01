#!/usr/bin/env bash
# 验证 V100 + CPU 卸载性能测试脚本
# Test V100 GPU + CPU offload performance

_SROOT="$( cd "$(dirname "$(realpath "$0")")/.." ; pwd -P )"
MODEL_PATH="/mnt/volume3/modelscope_models/Qwen/Qwen3-Coder-Next-GGUF/Q4_K_M/Qwen3-Coder-Next-Q4_K_M-00001-of-00004.gguf"

echo "=========================================="
echo "V100 + CPU Offload Benchmark"
echo "=========================================="
echo ""
echo "Hardware:"
echo "  GPU: NVIDIA Tesla PG503-216 (V100) - 32GB"
echo "  CPU: AMD Ryzen AI MAX+ 395 (16 cores)"
echo "  RAM: 124GB System Memory"
echo ""

# Stop running llama-server to free model file
echo "Stopping llama-server..."
$_SROOT/kill_auto_switch.sh > /dev/null 2>&1
sleep 2

# 测试不同的 GPU 层数配置
echo "Test 1: 25 GPU Layers (约 15GB VRAM)"
echo "--------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -ngl 25 \
  -sm none \
  -mg 0 \
  -p 512,1024,2048 \
  -n 128 \
  -t 16 \
  -fa on 2>&1 | tee /tmp/bench_v100_25_layers.log

echo ""
echo "Test 2: 40 GPU Layers (约 24GB VRAM)"
echo "--------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -ngl 40 \
  -sm none \
  -mg 0 \
  -p 512,1024,2048 \
  -n 128 \
  -t 16 \
  -fa on 2>&1 | tee /tmp/bench_v100_40_layers.log

echo ""
echo "Test 3: 50 GPU Layers (约 30GB VRAM) - 接近极限"
echo "--------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -ngl 50 \
  -sm none \
  -mg 0 \
  -p 512,1024,2048 \
  -n 128 \
  -t 16 \
  -fa on 2>&1 | tee /tmp/bench_v100_50_layers.log

echo ""
echo "Test 4: 60 GPU Layers (约 36GB VRAM) - 可能OOM"
echo "--------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -ngl 60 \
  -sm none \
  -mg 0 \
  -p 512,1024,2048 \
  -n 128 \
  -t 16 \
  -fa on 2>&1 | tee /tmp/bench_v100_60_layers.log || echo "OOM - 60 layers exceeds V100 memory"

echo ""
echo "=========================================="
echo "Comparison Summary"
echo "=========================================="
echo ""
echo "Extracting performance metrics..."

echo ""
echo "25 GPU Layers:"
grep -E "(pp|tg)" /tmp/bench_v100_25_layers.log 2>/dev/null | tail -5

echo ""
echo "40 GPU Layers:"
grep -E "(pp|tg)" /tmp/bench_v100_40_layers.log 2>/dev/null | tail -5

echo ""
echo "50 GPU Layers:"
grep -E "(pp|tg)" /tmp/bench_v100_50_layers.log 2>/dev/null | tail -5

echo ""
echo "60 GPU Layers (if successful):"
grep -E "(pp|tg)" /tmp/bench_v100_60_layers.log 2>/dev/null | tail -5

echo ""
echo "=========================================="
echo "Recommendations"
echo "=========================================="
echo ""
echo "Based on benchmark results, recommended config:"
echo "  - For speed: Use highest ngl that doesn't OOM"
echo "  - For stability: Use ngl=40 (leaves ~8GB buffer)"
echo "  - Context size: Can use full 102400 with CPU offload"
echo ""
echo "Logs saved to /tmp/bench_v100_*.log"
