#!/bin/bash
# Quick Speculative Decoding Performance Test
# Tests speculative decoding performance using ngram-cache

set -e

# Configuration
URL="http://localhost:8400"
TEST_PROMPT="请解释 speculative decoding 的工作原理和性能优势。"
NUM_TOKENS=200

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${BLUE}[INFO]${NC} $1"; }
success() { echo -e "${GREEN}[OK]${NC} $1"; }

echo "============================================================"
echo "Speculative Decoding Performance Test"
echo "============================================================"
echo ""

# Check server status
log "Checking server status..."
if ! curl -s "$URL/v1/models" > /dev/null; then
    echo "Error: Server not responding at $URL"
    exit 1
fi
success "Server is running"

# Get current model
current_model=$(curl -s "$URL/v1/models" | jq -r '.data[0].id')
log "Current model: $current_model"
echo ""

# Benchmark function
run_benchmark() {
    local mode=$1
    local label=$2
    local total_time=0
    local total_tps=0
    local runs=3

    echo "------------------------------------------------------------"
    echo "Mode: $label"
    echo "------------------------------------------------------------"

    for i in $(seq 1 $runs); do
        local start=$(date +%s.%N)

        local response=$(curl -s -X POST "$URL/v1/chat/completions" \
            -H "Content-Type: application/json" \
            -d "{\"model\": \"$current_model\", \"messages\": [{\"role\": \"user\", \"content\": \"$TEST_PROMPT\"}], \"max_tokens\": $NUM_TOKENS, \"stream\": false}")

        local end=$(date +%s.%N)
        local duration=$(echo "$end - $start" | bc)

        local completion_tokens=$(echo "$response" | jq -r '.usage.completion_tokens // 0')
        local tps=$(echo "scale=2; $completion_tokens / $duration" | bc 2>/dev/null || echo "0")

        echo "  Run $i: ${duration}s (${tps} tok/s)"

        total_time=$(echo "$total_time + $duration" | bc)
        total_tps=$(echo "$total_tps + $tps" | bc)
    done

    local avg_time=$(echo "scale=2; $total_time / $runs" | bc)
    local avg_tps=$(echo "scale=2; $total_tps / $runs" | bc)

    echo ""
    echo "  Average: ${avg_time}s (${avg_tps} tok/s)"
    echo "$avg_tps"
}

# Current server already has speculative decoding enabled via systemd config
# The systemd service has: --spec-type ngram-cache --draft-max 16 --draft-p-min 0.75

echo "Running benchmarks..."
echo ""

# The server is configured with speculative decoding at systemd level
# We'll test the current configuration
tps_sd=$(run_benchmark "sd" "With Speculative Decoding (ngram-cache)")

echo ""
echo "============================================================"
echo "Test Complete!"
echo "============================================================"
echo ""
echo "Current server configuration:"
echo "  - spec-type: ngram-cache"
echo "  - draft-max: 16"
echo "  - draft-p-min: 0.75"
echo ""
echo "Note: This test runs on the current server configuration."
echo "For a proper A/B comparison, you would need to restart the"
echo "server with and without speculative decoding parameters."
echo ""

# Save results
results_file="/mnt/volume3/llama_cpp/logs/sd_quick_test_$(date +%Y%m%d_%H%M%S).txt"
mkdir -p /mnt/volume3/llama_cpp/logs
cat > "$results_file" << EOF
Speculative Decoding Quick Test Results
========================================
Date: $(date)
Server: $URL
Model: $current_model
Prompt: $TEST_PROMPT
Max Tokens: $NUM_TOKENS

Results (with SD enabled):
$(run_benchmark "sd" "With SD")

Server Config:
  --spec-type ngram-cache
  --draft-max 16
  --draft-p-min 0.75
EOF

success "Results saved to: $results_file"
