#!/bin/bash
# Qwen3-Coder-Next (80B) Speculative Decoding Test
# Testing on Vulkan gfx1151

MODEL="/mnt/volume3/modelscope_models/Qwen/Qwen3-Coder-Next-GGUF/Q4_K_M/Qwen3-Coder-Next-Q4_K_M-00001-of-00004.gguf"
DRAFT="/mnt/volume3/modelscope_models/unsloth/Qwen3-0.6B-GGUF/Qwen3-0.6B-Q4_0.gguf"
PORT=8400
URL="http://localhost:$PORT"
SERVER_BIN="/mnt/volume3/llama_cpp/current/llama-server"

log() { echo "[$(date '+%H:%M:%S')] $1"; }

stop_server() {
    log "Stopping server..."
    pkill -9 -f "llama-server.*$PORT" 2>/dev/null || true
    sleep 3
}

benchmark() {
    local mode=$1
    log "=== Benchmark: $mode ==="
    for i in 1 2 3; do
        t0=$(date +%s.%N)
        resp=$(curl -s -X POST "$URL/v1/chat/completions" \
            -H "Content-Type: application/json" \
            -d '{"model": "Qwen3-Coder-Next", "messages": [{"role": "user", "content": "Hello"}], "max_tokens": 100}')
        t1=$(date +%s.%N)
        dur=$(echo "$t1 - $t0" | bc)
        toks=$(echo "$resp" | jq -r '.usage.completion_tokens // 0')
        tps=$(echo "scale=2; $toks / $dur" | bc 2>/dev/null || echo "0")
        draft_n=$(echo "$resp" | jq -r '.timings.draft_n // 0' 2>/dev/null || echo "0")
        draft_acc=$(echo "$resp" | jq -r '.timings.draft_n_accepted // 0' 2>/dev/null || echo "0")
        echo "  Run $i: ${dur}s ($toks tok, $tps tok/s, draft: $draft_n, acc: $draft_acc)"
    done
}

echo "============================================================"
echo "Qwen3-Coder-Next (80B) SD Test - Vulkan gfx1151"
echo "============================================================"

# Test 1: Normal mode
log "Starting NORMAL mode..."
stop_server
nohup $SERVER_BIN --model "$MODEL" --ctx-size 4096 -ngl 99 --port $PORT -fa on --jinja > /tmp/llama_80b_normal.log 2>&1 &
log "Waiting for model load..."
for i in {1..180}; do
    curl -s "$URL/v1/models" > /dev/null 2>&1 && break
    sleep 1
done
sleep 10
benchmark "Normal"

# Test 2: SD mode
log "Starting SPECULATIVE mode..."
stop_server
nohup $SERVER_BIN --model "$MODEL" --model-draft "$DRAFT" --ctx-size 4096 -ngl 99 --gpu-layers-draft all --draft-max 16 --draft-min 1 --draft-p-min 0.5 --port $PORT -fa on --jinja > /tmp/llama_80b_sd.log 2>&1 &
log "Waiting for model load..."
for i in {1..180}; do
    curl -s "$URL/v1/models" > /dev/null 2>&1 && break
    sleep 1
done
sleep 10
benchmark "Speculative"

echo "============================================================"
echo "Done!"
