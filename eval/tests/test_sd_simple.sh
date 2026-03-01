#!/bin/bash
# Simple Speculative Decoding Benchmark
# Tests performance with and without draft model speculative decoding

set -e

URL="http://localhost:8401"
MAIN_MODEL="/mnt/volume3/modelscope_models/prithivMLmods/Qwen3-VL-8B-Instruct-abliterated-v2-GGUF/Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0.gguf"
DRAFT_MODEL="/mnt/volume3/modelscope_models/unsloth/Qwen3-0.6B-GGUF/Qwen3-0.6B-Q4_0.gguf"
CUDA_BIN="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
LOG_DIR="/mnt/volume3/llama_cpp/logs"
PORT=8401

# Test prompt (Chinese)
TEST_PROMPT="请解释什么是 speculative decoding 技术，它如何提高大语言模型的推理速度？"
NUM_TOKENS=150

log() { echo "[INFO] $1"; }

stop_server() {
    pkill -f "llama-server.*--port.*$PORT" 2>/dev/null || true
    sleep 3
}

wait_server() {
    for i in {1..60}; do
        curl -s "$URL/v1/models" > /dev/null 2>&1 && return 0
        sleep 1
    done
    return 1
}

start_server() {
    local mode="$1"
    stop_server
    if [ "$mode" = "normal" ]; then
        nohup $CUDA_BIN --model "$MAIN_MODEL" --ctx-size 4096 -ngl 99 --port $PORT --host 127.0.0.1 -t 16 --temp 0.6 -fa on --jinja > "$LOG_DIR/sd_test_normal.log" 2>&1 &
    else
        nohup $CUDA_BIN --model "$MAIN_MODEL" --model-draft "$DRAFT_MODEL" --ctx-size 4096 -ngl 99 --gpu-layers-draft all --draft-max 16 --draft-min 1 --draft-p-min 0.5 --port $PORT --host 127.0.0.1 -t 16 --temp 0.6 -fa on --jinja > "$LOG_DIR/sd_test_sd.log" 2>&1 &
    fi
    if wait_server; then
        log "Server ready ($mode)"
        return 0
    fi
    return 1
}

benchmark() {
    local mode="$1"
    local runs=3
    local total_tps=0
    local total_time=0

    echo ""
    echo "=== Testing: $mode ==="

    for i in 1 2 3; do
        local t0=$(date +%s.%N)
        local resp=$(curl -s -X POST "$URL/v1/chat/completions" \
            -H "Content-Type: application/json" \
            -d "{\"model\": \"Qwen3-VL-8B\", \"messages\": [{\"role\": \"user\", \"content\": \"$TEST_PROMPT\"}], \"max_tokens\": $NUM_TOKENS}")

        local t1=$(date +%s.%N)
        local dur=$(echo "$t1 - $t0" | bc)

        local toks=$(echo "$resp" | jq -r '.usage.completion_tokens // 0')
        local tps=$(echo "scale=2; $toks / $dur" | bc 2>/dev/null || echo "0")

        echo "  Run $i: ${dur}s ($toks tokens, $tps tok/s)"
        total_tps=$(echo "$total_tps + $tps" | bc)
        total_time=$(echo "$total_time + $dur" | bc)
    done

    RESULT_TPS=$(echo "scale=2; $total_tps / $runs" | bc)
    RESULT_TIME=$(echo "scale=2; $total_time / $runs" | bc)
    echo "  Average: ${RESULT_TIME}s ($RESULT_TPS tok/s)"
}

# Main
mkdir -p "$LOG_DIR"
ts=$(date +%Y%m%d_%H%M%S)
csv="$LOG_DIR/sd_result_$ts.csv"

echo "============================================================"
echo "Speculative Decoding Benchmark (CUDA V100)"
echo "Model: Qwen3-VL-8B (Q8_0)"
echo "Draft: Qwen3-0.6B (Q4_0)"
echo "============================================================"

# Test 1: Normal (no SD)
log "Starting normal server..."
start_server "--model $MAIN_MODEL --ctx-size 4096 -ngl 99 --port $PORT --host 127.0.0.1 -t 16 --temp 0.6 -fa on --jinja"
sleep 5
benchmark "Normal"
normal_tps=$RESULT_TPS
normal_time=$RESULT_TIME

# Test 2: With SD
log "Starting SD server..."
start_server "--model $MAIN_MODEL --model-draft $DRAFT_MODEL --ctx-size 4096 -ngl 99 --gpu-layers-draft all --draft-max 16 --draft-min 1 --draft-p-min 0.5 --port $PORT --host 127.0.0.1 -t 16 --temp 0.6 -fa on --jinja"
sleep 5
benchmark "Speculative"
sd_tps=$RESULT_TPS
sd_time=$RESULT_TIME

# Results
echo ""
echo "============================================================"
echo "RESULTS"
echo "============================================================"
echo ""
echo "Normal Mode:"
echo "  Avg Time: ${normal_time}s"
echo "  Avg TPS: $normal_tps"
echo ""
echo "Speculative Mode:"
echo "  Avg Time: ${sd_time}s"
echo "  Avg TPS: $sd_tps"
echo ""

if [ -n "$normal_tps" ] && [ -n "$sd_tps" ] && [ "$normal_tps" != "0" ]; then
    speedup=$(echo "scale=2; $sd_tps / $normal_tps" | bc 2>/dev/null)
    improve=$(echo "scale=2; ($normal_time - $sd_time) * 100 / $normal_time" | bc 2>/dev/null)
    echo "Performance:"
    echo "  Speedup: ${speedup}x"
    echo "  Time saved: ${improve}%"
fi

# Save CSV
echo "mode,avg_time,avg_tps,speedup" > "$csv"
echo "Normal,$normal_time,$normal_tps,1.0" >> "$csv"
echo "Speculative,$sd_time,$sd_tps,$speedup" >> "$csv"

echo ""
echo "Saved to: $csv"
echo "============================================================"
