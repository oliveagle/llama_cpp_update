#!/bin/bash
# Test script for V-L Embedding model support fix
# PR: https://github.com/ggml-org/llama.cpp/pull/19694

set -e

echo "=============================================="
echo "V-L Embedding Model Support - Test Report"
echo "=============================================="
echo ""

# Model paths
MODEL_2B="/mnt/volume3/modelscope_models/poloniumrock/Qwen3-VL-Embedding-2B-Q8_0.gguf"
MODEL_8B="/mnt/volume3/hf_models/dam2452/Qwen3-VL-Embedding-8B-GGUF/Qwen3-VL-Embedding-8B-Q8_0.gguf"

# Test function
test_embedding_model() {
    local model_path=$1
    local model_name=$(basename "$model_path")

    echo "Testing: $model_name"
    echo "-------------------------------------------"

    # Check if model exists
    if [ ! -f "$model_path" ]; then
        echo "SKIP: Model not found at $model_path"
        return 1
    fi

    # Start server with embedding mode
    echo "Starting llama-server with embedding mode..."
    local server_pid
    ./build/bin/llama-server \
        -m "$model_path" \
        --embedding \
        --pooling mean \
        -port 8765 \
        --nobrowser \
        -np 1 \
        > /tmp/llama_embedding_test.log 2>&1 &
    server_pid=$!

    # Wait for server to start
    echo "Waiting for server to start..."
    sleep 15

    # Check if server is running
    if ! kill -0 $server_pid 2>/dev/null; then
        echo "FAIL: Server failed to start"
        echo "Log output:"
        cat /tmp/llama_embedding_test.log
        return 1
    fi

    # Test health endpoint
    echo "Testing /health endpoint..."
    if curl -s http://localhost:8765/health | jq -e '.status == "ok"' > /dev/null; then
        echo "PASS: Health check succeeded"
    else
        echo "FAIL: Health check failed"
        kill $server_pid 2>/dev/null
        return 1
    fi

    # Test embeddings endpoint
    echo "Testing /v1/embeddings endpoint..."
    local response=$(curl -s http://localhost:8765/v1/embeddings \
        -H "Content-Type: application/json" \
        -d '{"content": "你好，世界", "model": "'"$model_name"'"}')

    if echo "$response" | jq -e '.embedding' > /dev/null; then
        local dim=$(echo "$response" | jq '.embedding | length')
        echo "PASS: Embedding generated (dimension: $dim)"
    else
        echo "FAIL: Embedding generation failed"
        echo "Response: $response"
        kill $server_pid 2>/dev/null
        return 1
    fi

    # Stop server
    echo "Stopping server..."
    kill $server_pid 2>/dev/null
    wait $server_pid 2>/dev/null

    echo ""
    return 0
}

# Run tests
cd /mnt/volume3/llama_cpp

pass_count=0
fail_count=0
skip_count=0

if test_embedding_model "$MODEL_2B"; then
    ((pass_count++))
else
    if [ ! -f "$MODEL_2B" ]; then
        ((skip_count++))
    else
        ((fail_count++))
    fi
fi

if test_embedding_model "$MODEL_8B"; then
    ((pass_count++))
else
    if [ ! -f "$MODEL_8B" ]; then
        ((skip_count++))
    else
        ((fail_count++))
    fi
fi

# Summary
echo "=============================================="
echo "Test Summary"
echo "=============================================="
echo "PASS: $pass_count"
echo "FAIL: $fail_count"
echo "SKIP: $skip_count"
echo ""

if [ $fail_count -eq 0 ] && [ $pass_count -gt 0 ]; then
    echo "Result: ALL TESTS PASSED"
    exit 0
else
    echo "Result: TESTS FAILED"
    exit 1
fi
