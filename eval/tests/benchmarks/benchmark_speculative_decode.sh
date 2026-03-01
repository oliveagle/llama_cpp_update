#!/bin/bash
# Speculative Decoding Performance Benchmark
# Compares performance between normal mode and speculative decoding mode
# using llama.cpp's ngram-cache speculative decoding

set -e

# Configuration
VULKAN_URL="http://localhost:8400"
TEST_PROMPT="请详细解释什么是 speculative decoding，它的工作原理是什么，以及它能带来多大的性能提升？请用中文回答。"
NUM_TOKENS=256

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to benchmark a model with specific parameters
benchmark_model() {
    local url=$1
    local model=$2
    local extra_args=$3
    local mode_name=$4
    local log_file=$5
    local run_number=$6

    echo ""
    echo "------------------------------------------------------------"
    echo "Benchmark: $model"
    echo "Mode: $mode_name"
    echo "Run: $run_number"
    echo "------------------------------------------------------------"

    # Build the request
    local request_data="{\"model\": \"$model\", \"messages\": [{\"role\": \"user\", \"content\": \"$TEST_PROMPT\"}], \"max_tokens\": $NUM_TOKENS, \"stream\": false}"

    # Record start time
    local start_time=$(date +%s.%N)

    # Make the request and capture response
    local response=$(curl -s -X POST "$url/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d "$request_data")

    # Record end time
    local end_time=$(date +%s.%N)
    local total_time=$(echo "$end_time - $start_time" | bc)

    # Extract metrics from response
    local prompt_tokens=$(echo "$response" | jq -r '.usage.prompt_tokens // 0')
    local completion_tokens=$(echo "$response" | jq -r '.usage.completion_tokens // 0')
    local total_tokens=$(echo "$response" | jq -r '.usage.total_tokens // 0')

    # Calculate tokens per second
    local tps=$(echo "scale=2; $completion_tokens / $total_time" | bc 2>/dev/null || echo "0")

    # Output results
    echo "Results:"
    echo "  Total Time: ${total_time}s"
    echo "  Completion Tokens: $completion_tokens"
    echo "  Tokens/Second: $tps"

    # Log to file
    echo "$(date '+%Y-%m-%d %H:%M:%S'),$model,$mode_name,$run_number,$total_time,$prompt_tokens,$completion_tokens,$tps" >> "$log_file"

    # Return TPS
    echo "$tps"
}

# Function to restart server with specific config
restart_server_with_config() {
    local config_type=$1
    local preset_file=$2

    log_info "Stopping current server..."
    systemctl stop llama-server-8400.service 2>/dev/null || pkill -f "llama-server.*8400" || true
    sleep 3

    log_info "Starting server with $config_type config..."

    if [ "$config_type" == "normal" ]; then
        # Normal mode - no speculative decoding
        systemctl stop llama-server-8400.service 2>/dev/null || true
        pkill -f "llama-server.*8400" || true
        sleep 2

        # Start manually without SD
        nohup /mnt/volume3/llama_cpp/current/llama-server \
            --models-max 1 \
            --models-preset "$preset_file" \
            --host 0.0.0.0 \
            --port 8400 \
            --no-warmup \
            -fa on \
            --jinja \
            --reasoning-format auto \
            > /mnt/volume3/llama_cpp/logs/llama-server-normal.log 2>&1 &
        echo $! > /tmp/llama_server_normal.pid
    else
        # Speculative decoding mode
        systemctl stop llama-server-8400.service 2>/dev/null || true
        pkill -f "llama-server.*8400" || true
        sleep 2

        # Start manually with SD
        nohup /mnt/volume3/llama_cpp/current/llama-server \
            --models-max 1 \
            --models-preset "$preset_file" \
            --host 0.0.0.0 \
            --port 8400 \
            --no-warmup \
            -fa on \
            --jinja \
            --reasoning-format auto \
            --spec-type ngram-cache \
            --draft-max 16 \
            --draft-p-min 0.75 \
            > /mnt/volume3/llama_cpp/logs/llama-server-sd.log 2>&1 &
        echo $! > /tmp/llama_server_sd.pid
    fi

    # Wait for server to start
    log_info "Waiting for server to start (30 seconds)..."
    for i in {1..30}; do
        if curl -s "$VULKAN_URL/v1/models" > /dev/null 2>&1; then
            log_success "Server is ready!"
            return 0
        fi
        sleep 1
    done

    log_error "Server failed to start within 30 seconds"
    return 1
}

# Main benchmark function
run_benchmark() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local log_dir="/mnt/volume3/llama_cpp/logs"
    local benchmark_log="$log_dir/speculative_benchmark_$timestamp.csv"

    mkdir -p "$log_dir"

    # Create CSV header
    echo "timestamp,model,mode,run,total_time,prompt_tokens,completion_tokens,tps" > "$benchmark_log"

    log_info "=========================================="
    log_info "Speculative Decoding Benchmark"
    log_info "Timestamp: $timestamp"
    log_info "=========================================="
    echo ""

    # Check if server is running
    if ! curl -s "$VULKAN_URL/v1/models" > /dev/null; then
        log_error "Vulkan server ($VULKAN_URL) not responding"
        exit 1
    fi

    log_success "Server is running, starting benchmarks..."
    echo ""

    # Models to test
    declare -a models=(
        "Qwen3-Coder-Next-Q4_K_M"
        "GLM-4.7-Flash-Q4_K_M"
        "MiniCPM-o-4_5-Q4_K_M"
        "Qwen3-4B-Instruct-2507-UD-Q4_K_XL"
    )

    # Test each model with normal and SD mode
    for model in "${models[@]}"; do
        log_info "Testing model: $model"
        echo ""

        # Run 3 iterations for each mode for averaging
        for run in 1 2 3; do
            # Normal mode
            benchmark_model "$VULKAN_URL" "$model" "" "Normal" "$benchmark_log" "$run"
            sleep 2
        done

        for run in 1 2 3; do
            # Speculative mode (server already configured with SD)
            benchmark_model "$VULKAN_URL" "$model" "" "Speculative" "$benchmark_log" "$run"
            sleep 2
        done

        echo ""
    done

    log_info "=========================================="
    log_info "Benchmark Complete!"
    log_info "Results saved to: $benchmark_log"
    log_info "=========================================="

    # Display summary
    echo ""
    echo "============================================================"
    echo "RESULTS SUMMARY"
    echo "============================================================"
    echo ""

    # Calculate averages for each model
    for model in "${models[@]}"; do
        echo "Model: $model"
        echo "----------------------------------------------------------"

        # Normal mode average
        local normal_avg=$(grep ",$model,Normal," "$benchmark_log" | awk -F',' '{sum+=$5; count++} END {if(count>0) printf "%.2f", sum/count; else print "N/A"}')
        local normal_tps=$(grep ",$model,Normal," "$benchmark_log" | awk -F',' '{sum+=$8; count++} END {if(count>0) printf "%.2f", sum/count; else print "N/A"}')

        # SD mode average
        local sd_avg=$(grep ",$model,Speculative," "$benchmark_log" | awk -F',' '{sum+=$5; count++} END {if(count>0) printf "%.2f", sum/count; else print "N/A"}')
        local sd_tps=$(grep ",$model,Speculative," "$benchmark_log" | awk -F',' '{sum+=$8; count++} END {if(count>0) printf "%.2f", sum/count; else print "N/A"}')

        echo "  Normal Mode:"
        echo "    Avg Time: ${normal_avg}s"
        echo "    Avg TPS: $normal_tps"
        echo "  Speculative Mode:"
        echo "    Avg Time: ${sd_avg}s"
        echo "    Avg TPS: $sd_tps"

        # Calculate improvement
        if [ "$normal_avg" != "N/A" ] && [ "$sd_avg" != "N/A" ] && [ "$normal_avg" != "0" ]; then
            local time_improve=$(echo "scale=2; ($normal_avg - $sd_avg) * 100 / $normal_avg" | bc 2>/dev/null || echo "N/A")
            local speedup=$(echo "scale=2; $sd_tps / $normal_tps" | bc 2>/dev/null || echo "N/A")
            echo "  Time Improvement: ${time_improve}%"
            echo "  Speedup Factor: ${speedup}x"
        fi
        echo ""
    done

    # Full results table
    echo "============================================================"
    echo "FULL RESULTS TABLE"
    echo "============================================================"
    cat "$benchmark_log"
}

# Run the benchmark
run_benchmark
