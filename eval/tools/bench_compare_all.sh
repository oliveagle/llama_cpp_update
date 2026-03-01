#!/usr/bin/env bash
# 综合性能对比测试 - 运行所有基准测试并生成报告

_SROOT="$( cd "$(dirname "$(realpath "$0")")/.." ; pwd -P )"

echo "=========================================="
echo "Qwen3-Coder-Next Performance Benchmark"
echo "=========================================="
echo ""
echo "This will run benchmark scripts:"
echo "  1. Vulkan Multi-GPU split mode"
echo "  2. V100 + CPU offload"
echo "  3. AMD GPU only (Vulkan)"
echo ""
echo "Estimated time: 10-15 minutes"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "Starting benchmarks..."
echo ""

# Run Vulkan multi-GPU benchmark
echo "=========================================="
echo "Phase 1: Vulkan Multi-GPU Split Mode"
echo "=========================================="
$_SROOT/scripts/bench_vulkan_multi_gpu.sh

echo ""
echo "=========================================="
echo "Phase 2: V100 + CPU Offload"
echo "=========================================="
$_SROOT/scripts/bench_v100_cpu_offload.sh

echo ""
echo "=========================================="
echo "Phase 3: AMD GPU Only (Vulkan)"
echo "=========================================="
$_SROOT/scripts/bench_amd_gpu_only.sh

echo ""
echo "=========================================="
echo "Generating Final Report"
echo "=========================================="
echo ""

REPORT_FILE="/tmp/benchmark_report_$(date +%Y%m%d_%H%M%S).txt"

cat > "$REPORT_FILE" << EOF
Qwen3-Coder-Next Performance Benchmark Report
Generated: $(date)
Hardware:
  - NVIDIA Tesla PG503-216 (V100) 32GB
  - AMD Radeon 8060S (Integrated)
  - AMD Ryzen AI MAX+ 395
  - 124GB System RAM

========================================
VULKAN MULTI-GPU SPLIT MODE RESULTS
========================================

75% V100 + 25% AMD Split:
$(grep -E "(pp|tg)" /tmp/bench_vulkan_75_25.log 2>/dev/null | tail -5)

50% V100 + 50% AMD Split:
$(grep -E "(pp|tg)" /tmp/bench_vulkan_50_50.log 2>/dev/null | tail -5)

90% V100 + 10% AMD Split:
$(grep -E "(pp|tg)" /tmp/bench_vulkan_90_10.log 2>/dev/null | tail -5)

========================================
V100 + CPU OFFLOAD RESULTS
========================================

25 GPU Layers:
$(grep -E "(pp|tg)" /tmp/bench_v100_25_layers.log 2>/dev/null | tail -5)

40 GPU Layers:
$(grep -E "(pp|tg)" /tmp/bench_v100_40_layers.log 2>/dev/null | tail -5)

50 GPU Layers:
$(grep -E "(pp|tg)" /tmp/bench_v100_50_layers.log 2>/dev/null | tail -5)

60 GPU Layers:
$(grep -E "(pp|tg)" /tmp/bench_v100_60_layers.log 2>/dev/null | tail -5)

========================================
AMD GPU ONLY (VULKAN) RESULTS
========================================

AMD GPU Basic:
$(grep -E "^[0-9]+," /tmp/benchmark_amd_gpu_*/amd_basic.txt 2>/dev/null | tail -1)

AMD GPU Code Generation:
$(grep -E "^[0-9]+," /tmp/benchmark_amd_gpu_*/amd_codegen.txt 2>/dev/null | tail -1)

AMD GPU Long Context:
$(grep -E "^[0-9]+," /tmp/benchmark_amd_gpu_*/amd_longctx.txt 2>/dev/null | tail -1)

========================================
RECOMMENDATIONS
========================================

Based on benchmark results:

1. If multi-GPU Vulkan split provides better pp/tg (prompt/evaluation) 
   performance than single GPU + CPU offload, use it.

2. Otherwise, use V100 + CPU offload with optimal ngl value.

3. For production, consider the stability (OOM risk) vs performance tradeoff.

EOF

echo "Report saved to: $REPORT_FILE"
echo ""
cat "$REPORT_FILE"
