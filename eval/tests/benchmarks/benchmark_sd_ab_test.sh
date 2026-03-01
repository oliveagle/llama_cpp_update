#!/bin/bash
# Speculative Decoding A/B Performance Benchmark
# Compares performance with and without speculative decoding

set -e

# Configuration - Using GLM-4.7-Flash (3B) which fits in Vulkan memory
URL="http://localhost:8400"
PORT=8400
PRESET_FILE="/mnt/volume3/llama_cpp/config/presets/mypresets.ini"
# Using Qwen3-0.6B as draft model for speculative decoding
DRAFT_MODEL="/mnt/volume3/modelscope_models/unsloth/Qwen3-0.6B-GGUF/Qwen3-0.6B-Q4_0.gguf"
# Main model to test (smaller model that fits in Vulkan memory)
MAIN_MODEL="/mnt/volume3/modelscope_models/unsloth/GLM-4___7-Flash-GGUF/GLM-4.7-Flash-Q4_K_M.gguf"
MAIN_MODEL_NAME="GLM-4.7-Flash-Q4_K_M"
TEST_PROMPT="请详细解释什么是 speculative decoding 技术？它的工作原理是什么？请用中文回答。"
NUM_TOKENS=200
LOG_DIR="/mnt/volume3/llama_cpp/logs"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Stop any running llama-server on port 8400
stop_server() {
    log "Stopping any running llama-server on port $PORT..."
    pkill -f "llama-server.*--port.*$PORT" 2>/dev/null || true
    systemctl stop llama-server-$PORT.service 2>/dev/null || true
    sleep 3
}

# Start server without speculative decoding
start_normal() {
    log "Starting server WITHOUT speculative decoding..."
    stop_server

    nohup /mnt/volume3/llama_cpp/current/llama-server \
        --model "$MAIN_MODEL" \
        --ctx-size 4096 \
        --n-gpu-layers 99 \
        --port $PORT \
        --host 0.0.0.0 \
        -fa on \
        --jinja \
        > "$LOG_DIR/llama_normal.log" 2>&1 &

    echo $! > /tmp/llama_normal.pid
    wait_for_server
}

# Start server with speculative decoding (draft model)
start_sd() {
    log "Starting server WITH speculative decoding (draft model)..."
    stop_server

    nohup /mnt/volume3/llama_cpp/current/llama-server \
        --model "$MAIN_MODEL" \
        --model-draft "$DRAFT_MODEL" \
        --ctx-size 4096 \
        --n-gpu-layers 99 \
        --gpu-layers-draft all \
        --draft-max 16 \
        --draft-min 1 \
        --draft-p-min 0.5 \
        --port $PORT \
        --host 0.0.0.0 \
        -fa on \
        --jinja \
        > "$LOG_DIR/llama_sd.log" 2>&1 &

    echo $! > /tmp/llama_sd.pid
    wait_for_server
}

# Wait for server to be ready
wait_for_server() {
    log "Waiting for server to start (max 60 seconds)..."
    for i in {1..60}; do
        if curl -s "$URL/v1/models" > /dev/null 2>&1; then
            success "Server is ready!"
            return 0
        fi
        sleep 1
    done
    error "Server failed to start within 60 seconds"
    return 1
}

# Run benchmark
run_benchmark() {
    local mode=$1
    local runs=3
    local total_time=0
    local total_tps=0
    local total_ttft=0

    echo ""
    echo "============================================================"
    echo "Benchmark: $mode Mode (Model: $MAIN_MODEL_NAME)"
    echo "============================================================"

    for i in $(seq 1 $runs); do
        log "  Run $i..."
        local start=$(date +%s.%N)

        local response=$(curl -s -X POST "$URL/v1/chat/completions" \
            -H "Content-Type: application/json" \
            -d "{\"model\": \"$MAIN_MODEL_NAME\", \"messages\": [{\"role\": \"user\", \"content\": \"$TEST_PROMPT\"}], \"max_tokens\": $NUM_TOKENS, \"stream\": false}")

        local end=$(date +%s.%N)
        local duration=$(echo "$end - $start" | bc)

        local completion_tokens=$(echo "$response" | jq -r '.usage.completion_tokens // 0')
        local prompt_tokens=$(echo "$response" | jq -r '.usage.prompt_tokens // 0')

        # Check for error response
        if echo "$response" | jq -e '.error' > /dev/null 2>&1; then
            local error_msg=$(echo "$response" | jq -r '.error.message // "Unknown error"')
            warn "  Error: $error_msg"
            echo "  Response: $response"
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

    # Return values via global variables
    RESULT_AVG_TIME=$avg_time
    RESULT_AVG_TPS=$avg_tps
}

# Main
main() {
    mkdir -p "$LOG_DIR"
    timestamp=$(date '+%Y%m%d_%H%M%S')
    results_file="$LOG_DIR/sd_ab_benchmark_$timestamp.csv"

    echo "============================================================"
    echo "Speculative Decoding A/B Benchmark"
    echo "============================================================"
    echo "Timestamp: $(date)"
    echo "Test Prompt: ${TEST_PROMPT:0:50}..."
    echo "Num Tokens: $NUM_TOKENS"
    echo "Draft Model: $DRAFT_MODEL"
    echo "Results File: $results_file"
    echo ""

    # CSV Header
    echo "timestamp,mode,avg_time,avg_tps,runs" > "$results_file"

    # Test 1: Normal mode (no SD)
    start_normal
    run_benchmark "Normal"
    echo "$timestamp,Normal,$RESULT_AVG_TIME,$RESULT_AVG_TPS,3" >> "$results_file"
    normal_tps=$RESULT_AVG_TPS
    normal_time=$RESULT_AVG_TIME

    # Test 2: Speculative decoding mode
    start_sd
    run_benchmark "Speculative"
    echo "$timestamp,Speculative,$RESULT_AVG_TIME,$RESULT_AVG_TPS,3" >> "$results_file"
    sd_tps=$RESULT_AVG_TPS
    sd_time=$RESULT_AVG_TIME

    # Calculate improvement
    echo ""
    echo "============================================================"
    echo "FINAL RESULTS"
    echo "============================================================"
    echo ""
    echo "Normal Mode:"
    echo "  Average Time: ${normal_time}s"
    echo "  Average TPS: $normal_tps"
    echo ""
    echo "Speculative Decoding Mode:"
    echo "  Average Time: ${sd_time}s"
    echo "  Average TPS: $sd_tps"
    echo ""

    # Calculate speedup
    if [ -n "$normal_tps" ] && [ -n "$sd_tps" ] && [ "$normal_tps" != "0" ]; then
        speedup=$(echo "scale=2; $sd_tps / $normal_tps" | bc 2>/dev/null || echo "N/A")
        time_improve=$(echo "scale=2; ($normal_time - $sd_time) * 100 / $normal_time" | bc 2>/dev/null || echo "N/A")
        echo "Performance Improvement:"
        echo "  Speedup Factor: ${speedup}x"
        echo "  Time Reduction: ${time_improve}%"
    fi

    echo ""
    echo "Results saved to: $results_file"
    echo "============================================================"

    # Print detailed log
    echo ""
    echo "Detailed Results:"
    cat "$results_file"
}

main
