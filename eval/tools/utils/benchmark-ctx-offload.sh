#!/bin/bash
# JoyAI-LLM-Flash V100 参数优化脚本
# 测试不同 GPU 层数和 context 大小的组合

set -e

MODEL="/mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf"
PORT=8401
LLAMA_SERVER="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"

test_config() {
    local ctx=$1
    local ngl=$2      # GPU layers
    local fa=$3       # flash attention (on/off)
    local split_mode=$4  # row/layer/none

    echo "=========================================="
    echo "Testing: ctx=$ctx, ngl=$ngl, fa=$fa, split=$split_mode"

    # 构建参数
    local extra_args=""
    [ "$fa" = "on" ] && extra_args="$extra_args --flash-attn"

    case $split_mode in
        row)
            extra_args="$extra_args -sm row"
            ;;
        layer)
            extra_args="$extra_args -sm layer"
            ;;
    esac

    # 启动服务器
    $LLAMA_SERVER \
        -m "$MODEL" \
        -c $ctx \
        -ngl $ngl \
        --host 0.0.0.0 \
        --port $PORT \
        -np 1 \
        --timeout 300 \
        $extra_args > /tmp/llama-bench.log 2>&1 &

    local pid=$!

    # 等待启动
    local started=0
    for i in {1..60}; do
        sleep 1
        if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
            started=1
            break
        fi
        if ! kill -0 $pid 2>/dev/null; then
            break
        fi
    done

    if [ $started -eq 0 ]; then
        echo "❌ 启动失败"
        kill $pid 2>/dev/null || true
        return 1
    fi

    # 获取显存使用
    sleep 2
    local vram=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
    echo "VRAM: ${vram}MiB"

    # 测试推理速度
    echo "测试推理速度..."
    local start=$(date +%s%N)
    local result=$(curl -s http://localhost:$PORT/completion \
        -H "Content-Type: application/json" \
        -d '{"prompt": "Hello, how are you? Please write a detailed response about artificial intelligence.", "n_predict": 256, "temperature": 0.7}' 2>/dev/null | \
        python3 -c "import json,sys; d=json.load(sys.stdin); c=d.get('content',''); t=d.get('tokens_predicted',0); ts=d.get('timings',{}).get('predicted_per_second',0); print(f'{t} tokens, {ts:.2f} t/s')" 2>/dev/null || echo "failed")

    local end=$(date +%s%N)
    kill $pid 2>/dev/null || true
    wait $pid 2>/dev/null || true

    echo "结果: $result"
    echo "$ctx,$ngl,$fa,$split_mode,$vram,$result" >> /tmp/benchmark-results.csv
    echo ""

    return 0
}

# 准备结果文件
echo "ctx,ngl,fa,split_mode,vram,result" > /tmp/benchmark-results.csv

# 测试参数矩阵
# Context 大小: 8K, 16K, 24K, 32K
# GPU 层数: 0 (全CPU), 10, 20, 30, 40, 50, 60, -1 (全GPU)
# Flash Attention: on, off
# Split mode: layer (默认), row

echo "开始测试参数组合..."
echo "模型: JoyAI-LLM-Flash-Q4_K_M (~28GB)"
echo "GPU: V100 32GB"
echo ""

# 先测试关键组合
for ctx in 8192 16384 24576; do
    for ngl in -1 40 20 0; do
        for fa in on; do
            test_config $ctx $ngl $fa layer || echo "跳过失败配置"
            sleep 2
        done
    done
done

echo "=========================================="
echo "测试完成! 结果保存在 /tmp/benchmark-results.csv"
cat /tmp/benchmark-results.csv
