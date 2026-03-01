#!/bin/bash
# Speculative Decoding Benchmark - Qwen3-Coder-Next (80B)
# Tests performance with and without draft model speculative decoding

set -e

URL="http://localhost:8401"
MAIN_MODEL="/mnt/volume3/modelscope_models/Qwen/Qwen3-Coder-Next-GGUF/Q4_K_M/Qwen3-Coder-Next-Q4_K_M-00001-of-00004.gguf"
DRAFT_MODEL="/mnt/volume3/modelscope_models/unsloth/Qwen3-0.6B-GGUF/Qwen3-0.6B-Q4_0.gguf"
CUDA_BIN="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
LOG_DIR="/mnt/volume3/llama_cpp/logs"
PORT=8401
GPU_LAYERS=40  # Fit within V100 32GB

TEST_PROMPT="Please explain speculative decoding in detail."
NUM_TOKENS=100

log() { echo "[$(date '+%H:%M:%S')] $1"; }

stop_server() {
    log "Stopping server..."
    pkill -9 -f "llama-server.*--port.*$PORT" 2>/dev/null || true
    sleep 3
}

wait_server() {
    log "Waiting for server (max 120s)..."
    for i in {1..120}; do
        curl -s "$URL/v1/models" > /dev/null 2>&1 && return 0
        sleep 1
    done
    return 1
}

start_normal() {
    log "Starting NORMAL server (80B model, $GPU_LAYERS GPU layers)..."
    stop_server
    nohup $CUDA_BIN \
        --model "$MAIN_MODEL" \
        --ctx-size 4096 \
        -ngl $GPU_LAYERS \
        --port $PORT \
        --host 127.0.0.1 \
        -t 16 --temp 0.6 -fa on --jinja \
        > "$LOG_DIR/coder_normal.log" 2>&1 &
    wait_server
}

start_sd() {
    log "Starting SD server (80B + 0.6B draft, $GPU_LAYERS GPU layers)..."
    stop_server
    nohup $CUDA_BIN \
        --model "$MAIN_MODEL" \
        --model-draft "$DRAFT_MODEL" \
        --ctx-size 4096 \
        -ngl $GPU_LAYERS \
        --gpu-layers-draft $GPU_LAYERS \
        --draft-max 16 --draft-min 1 --draft-p-min 0.5 \
        --port $PORT \
        --host 127.0.0.1 \
        -t 16 --temp 0.6 -fa on --jinja \
        > "$LOG_DIR/coder_sd.log" 2>&1 &
    wait_server
}

benchmark() {
    local mode="$1"
    local runs=5
    local total_tps=0

    log "=== Benchmark: $mode (200 tokens) ==="

    for i in $(seq 1 $runs); do
        t0=$(date +%s.%N)
        curl -s -X POST "$URL/v1/chat/completions" \
            -H "Content-Type: application/json" \
            -d "{\"model\": \"Qwen3-Coder-Next\", \"messages\": [{\"role\": \"user\", \"content\": \"$TEST_PROMPT\"}], \"max_tokens\": 200}" \
            > /tmp/sd_resp.json 2>&1

        t1=$(date +%s.%N)
        dur=$(echo "$t1 - $t0" | bc)
        toks=$(jq -r '.usage.completion_tokens // 0' /tmp/sd_resp.json)

        if [ "$toks" != "0" ] && [ -n "$toks" ]; then
            tps=$(echo "scale=2; $toks / $dur" | bc)
            echo "  Run $i: ${dur}s ($toks tok, $tps tok/s)"
            total_tps=$(echo "$total_tps + $tps" | bc)
        else
            echo "  Run $i: FAILED - $(cat /tmp/sd_resp.json | head -1)"
        fi
    done

    RESULT_TPS=$(echo "scale=2; $total_tps / $runs" | bc)
    echo "  Avg TPS: $RESULT_TPS"
}

# Main
echo "============================================================"
echo "Qwen3-Coder-Next (80B) Speculative Decoding Benchmark"
echo "GPU: V100 (32GB), GPU Layers: $GPU_LAYERS"
echo "Draft: Qwen3-0.6B"
echo "============================================================"

start_normal
sleep 10
benchmark "Normal"
normal_tps=$RESULT_TPS

start_sd
sleep 10
benchmark "Speculative"
sd_tps=$RESULT_TPS

echo ""
echo "============================================================"
echo "RESULTS"
echo "============================================================"
echo "Normal: $normal_tps tok/s"
echo "SD:     $sd_tps tok/s"
if [ -n "$normal_tps" ] && [ -n "$sd_tps" ] && [ "$normal_tps" != "0" ]; then
    speedup=$(echo "scale=2; $sd_tps / $normal_tps" | bc)
    echo "Speedup: ${speedup}x"
fi
echo "============================================================"
