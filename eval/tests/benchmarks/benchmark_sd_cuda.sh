#!/bin/bash
# Speculative Decoding Performance Test - CUDA Server
# Tests Qwen3-VL-8B with and without speculative decoding

set -e

URL="http://localhost:8401"
DRAFT_MODEL="/mnt/volume3/modelscope_models/unsloth/Qwen3-0.6B-GGUF/Qwen3-0.6B-Q4_0.gguf"
MAIN_MODEL="/mnt/volume3/modelscope_models/prithivMLmods/Qwen3-VL-8B-Instruct-abliterated-v2-GGUF/Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0.gguf"
MAIN_MODEL_NAME="Qwen3-VL-8B"
TEST_PROMPT="请解释 speculative decoding 技术的工作原理和性能优势。"
NUM_TOKENS=200
LOG_DIR="/mnt/volume3/llama_cpp/logs"
CUDA_BIN="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

stop_server() {
    log "Stopping llama-server on port $PORT..."
    pkill -f "llama-server.*--port.*$PORT" 2>/dev/null || true
    sleep 3
}

wait_for_server() {
    log "Waiting for server to start (max 90 seconds)..."
    for i in {1..90}; do
        if curl -s "$URL/v1/models" > /dev/null 2>&1; then
            success "Server is ready!"
            return 0
        fi
        sleep 1
    done
    error "Server failed to start within 90 seconds"
    return 1
}

start_normal() {
    log "Starting server WITHOUT speculative decoding..."
    stop_server

    nohup $CUDA_BIN \
        --model "$MAIN_MODEL" \
        --ctx-size 4096 \
        -ngl 99 \
        --port $PORT \
        --host 127.0.0.1 \
        -t 16 \
        --temp 0.6 \
        -fa on \
        --jinja \
        > "$LOG_DIR/cuda_normal.log" 2>&1 &

    wait_for_server
}

start_sd() {
    log "Starting server WITH speculative decoding (Qwen3-0.6B as draft)..."
    stop_server

    nohup $CUDA_BIN \
        --model "$MAIN_MODEL" \
        --model-draft "$DRAFT_MODEL" \
        --ctx-size 4096 \
        -ngl 99 \
        --gpu-layers-draft all \
        --draft-max 16 \
        --draft-min 1 \
        --draft-p-min 0.5 \
        --port $PORT \
        --host 127.0.0.1 \
        -t 16 \
        --temp 0.6 \
        -fa on \
        --jinja \
        > "$LOG_DIR/cuda_sd.log" 2>&1 &

    wait_for_server
}

run_benchmark() {
    local mode=$1
    local runs=3
    local total_time=0
    local total_tps=0

    echo ""
    echo "------------------------------------------------------------"
    echo "Mode: $mode"
    echo "------------------------------------------------------------"

    for i in $(seq 1 $runs); do
        log "  Run $i..."
        local start=$(date +%s.%N)

        local response=$(curl -s -X POST "$URL/v1/chat/completions" \
            -H "Content-Type: application/json" \
            -d "{\"model\": \"$MAIN_MODEL_NAME\", \"messages\": [{\"role\": \"user\", \"content\": \"$TEST_PROMPT\"}], \"max_tokens\": $NUM_TOKENS, \"stream\": false}")

        local end=$(date +%s.%N)
        local duration=$(echo "$end - $start" | bc)

        local completion_tokens=$(echo "$response" | jq -r '.usage.completion_tokens // 0')

        if echo "$response" | jq -e '.error' > /dev/null 2>&1; then
            local error_msg=$(echo "$response" | jq -r '.error.message // "Unknown error"')
            warn "  Error: $error_msg"
            continue
        fi

        local tps=$(echo "scale=2; $completion_tokens / $duration" | bc 2>/dev/null || echo "0")
        echo "  Run $i: ${duration}s | Tokens: $completion_tokens | TPS: $tps"

        total_time=$(echo "$total_time + $duration" | bc)
        total_tps=$(echo "$total_tps + $tps" | bc)
    done

    local avg_time=$(echo "scale=2; $total_time / $runs" | bc)
    local avg_tps=$(echo "scale=2; $total_tps / $runs" | bc)

    echo ""
    echo "  Average: ${avg_time}s | ${avg_tps} tok/s"

    RESULT_AVG_TIME=$avg_time
    RESULT_AVG_TPS=$avg_tps
}

main() {
    PORT=8401
    mkdir -p "$LOG_DIR"
    timestamp=$(date '+%Y%m%d_%H%M%S')
    results_file="$LOG_DIR/sd_cuda_benchmark_$timestamp.csv"

    echo "============================================================"
    echo "Speculative Decoding A/B Benchmark (CUDA/V100)"
    echo "============================================================"
    echo "Timestamp: $(date)"
    echo "Model: Qwen3-VL-8B (Q8_0)"
    echo "Draft Model: Qwen3-0.6B (Q4_0)"
    echo "Test Prompt: $TEST_PROMPT"
    echo "Max Tokens: $NUM_TOKENS"
    echo "Results File: $results_file"
    echo ""

    echo "timestamp,mode,avg_time,avg_tps,runs" > "$results_file"

    # Test 1: Normal mode
    start_normal
    sleep 5  # Extra warmup time
    run_benchmark "Normal"
    echo "$timestamp,Normal,$RESULT_AVG_TIME,$RESULT_AVG_TPS,3" >> "$results_file"
    normal_tps=$RESULT_AVG_TPS
    normal_time=$RESULT_AVG_TIME

    # Test 2: Speculative mode
    start_sd
    sleep 5
    run_benchmark "Speculative"
    echo "$timestamp,Speculative,$RESULT_AVG_TIME,$RESULT_AVG_TPS,3" >> "$results_file"
    sd_tps=$RESULT_AVG_TPS
    sd_time=$RESULT_AVG_TIME

    # Summary
    echo ""
    echo "============================================================"
    echo "FINAL RESULTS"
    echo "============================================================"
    echo ""
    echo "| Metric | Normal | Speculative |"
    echo "|--------|--------|-------------|"
    printf "| Avg Time | %ss | %ss |\n" "$normal_time" "$sd_time"
    printf "| Avg TPS | %s | %s |\n" "$normal_tps" "$sd_tps"
    echo ""

    if [ -n "$normal_tps" ] && [ -n "$sd_tps" ] && [ "$normal_tps" != "0" ] && [ -n "$normal_time" ] && [ -n "$sd_time" ]; then
        speedup=$(echo "scale=2; $sd_tps / $normal_tps" | bc 2>/dev/null || echo "N/A")
        time_improve=$(echo "scale=2; ($normal_time - $sd_time) * 100 / $normal_time" | bc 2>/dev/null || echo "N/A")
        echo "Performance Improvement:"
        echo "  Speedup Factor: ${speedup}x"
        echo "  Time Reduction: ${time_improve}%"
    fi

    echo ""
    echo "Results saved to: $results_file"
    echo "============================================================"

    cat "$results_file"
}

main
