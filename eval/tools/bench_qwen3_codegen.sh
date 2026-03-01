#!/usr/bin/env bash
# Qwen3-Coder-Next 代码生成性能测试
# 测试典型编程场景下的 token generation 速度

_SROOT="$( cd "$(dirname "$(realpath "$0")")/.." ; pwd -P )"
MODEL_PATH="/mnt/volume3/modelscope_models/Qwen/Qwen3-Coder-Next-GGUF/Q4_K_M/Qwen3-Coder-Next-Q4_K_M-00001-of-00004.gguf"
RESULT_DIR="/tmp/benchmark_codegen_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULT_DIR"

echo "=========================================="
echo "Qwen3-Coder-Next Code Generation Speed"
echo "=========================================="
echo ""
echo "Testing token generation speed for coding tasks"
echo "Official settings: temp=1.0, top_p=0.95, top_k=40"
echo ""

# 使用实际的 prompt 长度配置
echo "Scenario 1: Quick Code Completion"
echo "  Task: Complete a function signature"
echo "  Prompt: 256 tokens | Generate: 128 tokens"
echo "------------------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 256 -n 128 \
  -ngl 50 \
  -t 16 \
  -r 5 2>&1 | tee "$RESULT_DIR/codegen_quick.txt"

echo ""
echo "Scenario 2: Function Implementation"
echo "  Task: Write a complete function with docs"
echo "  Prompt: 512 tokens | Generate: 512 tokens"
echo "------------------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 512 -n 512 \
  -ngl 50 \
  -t 16 \
  -r 3 2>&1 | tee "$RESULT_DIR/codegen_function.txt"

echo ""
echo "Scenario 3: Class/Module Generation"
echo "  Task: Generate a complete class with methods"
echo "  Prompt: 1024 tokens | Generate: 1024 tokens"
echo "------------------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 1024 -n 1024 \
  -ngl 50 \
  -t 16 \
  -r 3 2>&1 | tee "$RESULT_DIR/codegen_class.txt"

echo ""
echo "Scenario 4: Large Code Block (Algorithm)"
echo "  Task: Implement complex algorithm"
echo "  Prompt: 2048 tokens | Generate: 2048 tokens"
echo "------------------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 2048 -n 2048 \
  -ngl 50 \
  -t 16 \
  -r 2 2>&1 | tee "$RESULT_DIR/codegen_algorithm.txt"

echo ""
echo "Scenario 5: Full File Generation"
echo "  Task: Generate complete source file"
echo "  Prompt: 1024 tokens | Generate: 4096 tokens"
echo "------------------------------------------------"
$_SROOT/current/llama-bench \
  -m "$MODEL_PATH" \
  -p 1024 -n 4096 \
  -ngl 50 \
  -t 16 \
  -r 1 2>&1 | tee "$RESULT_DIR/codegen_fullfile.txt"

# 生成详细报告
echo ""
echo "=========================================="
echo "Code Generation Performance Report"
echo "=========================================="
echo ""

printf "%-25s %-15s %-15s %-15s\n" "Scenario" "Prompt t/s" "Gen t/s" "Time (ms)"
echo "--------------------------------------------------------------------"

for scenario in quick function class algorithm fullfile; do
    file="$RESULT_DIR/codegen_${scenario}.txt"
    if [ -f "$file" ]; then
        line=$(grep -E "^[0-9]+," "$file" | tail -1)
        if [ ! -z "$line" ]; then
            pp=$(echo "$line" | cut -d',' -f3)
            tg=$(echo "$line" | cut -d',' -f4)
            time_ms=$(echo "$line" | cut -d',' -f5)
            printf "%-25s %-15s %-15s %-15s\n" "$scenario" "$pp" "$tg" "$time_ms"
        fi
    fi
done

echo ""
echo "Performance Metrics:"
echo "  pp = Prompt processing speed (tokens/sec)"
echo "  tg = Token generation speed (tokens/sec)"
echo ""
echo "Typical expectations for coding models:"
echo "  - tg > 30 t/s: Good real-time experience"
echo "  - tg > 50 t/s: Excellent performance"
echo "  - tg < 20 t/s: Noticeable delay"
echo ""
echo "Results saved to: $RESULT_DIR"
