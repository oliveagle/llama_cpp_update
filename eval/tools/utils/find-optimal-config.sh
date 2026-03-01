#!/bin/bash
# JoyAI-LLM-Flash V100 最佳参数组合寻找脚本
# 目标: 在 32GB V100 上运行 28GB 模型，最大化 context 和性能

set -e

MODEL="/mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf"
PORT=8402  # 使用不同端口避免冲突
LLAMA_SERVER="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
RESULT_FILE="/tmp/joyai-optimal-results.csv"

echo "ctx_size,gpu_layers,flash_attn,kv_offload,cache_k,cache_v,split_mode,vram_mb,status,tokens_per_sec,notes" > "$RESULT_FILE"

test_config() {
    local ctx=$1
    local ngl=$2
    local fa=$3
    local kvo=$4
    local ctk=$5
    local ctv=$6
    local split=$7

    echo ""
    echo "=========================================="
    echo "Config: ctx=$ctx, ngl=$ngl, fa=$fa, kvo=$kvo, cache=$ctk/$ctv, split=$split"

    # 构建参数
    local args="-m $MODEL -c $ctx --host 0.0.0.0 --port $PORT -np 1"

    # GPU layers
    if [ "$ngl" = "-1" ]; then
        args="$args -ngl 999"
    else
        args="$args -ngl $ngl"
    fi

    # Flash attention
    args="$args -fa $fa"

    # KV offload
    if [ "$kvo" = "off" ]; then
        args="$args --no-kv-offload"
    fi

    # Cache types
    args="$args -ctk $ctk -ctv $ctv"

    # Split mode
    args="$args -sm $split"

    # 清理之前的进程
    pkill -f "llama-server.*$PORT" 2>/dev/null || true
    sleep 1

    # 启动服务器
    $LLAMA_SERVER $args > /tmp/llama-test-$PORT.log 2>&1 &
    local pid=$!

    # 等待启动
    local started=0
    local oom=0
    for i in {1..90}; do
        sleep 1

        # 检查进程是否还在
        if ! kill -0 $pid 2>/dev/null; then
            # 进程已退出
            if grep -q "out of memory\|OOM\|CUDA out of memory\|failed to allocate" /tmp/llama-test-$PORT.log 2>/dev/null; then
                oom=1
            fi
            break
        fi

        # 检查是否成功启动
        if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
            started=1
            break
        fi
    done

    if [ $started -eq 0 ]; then
        kill $pid 2>/dev/null || true
        wait $pid 2>/dev/null || true

        local status="FAILED"
        local notes=""
        if [ $oom -eq 1 ]; then
            status="OOM"
            notes="Out of memory"
        elif grep -q "cannot offload" /tmp/llama-test-$PORT.log 2>/dev/null; then
            notes="Offload not supported"
        fi

        echo "$ctx,$ngl,$fa,$kvo,$ctk,$ctv,$split,0,$status,0,$notes" >> "$RESULT_FILE"
        echo "❌ $status - $notes"
        return 1
    fi

    # 获取显存使用
    sleep 2
    local vram=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)

    # 测试推理
    echo "Testing inference..."
    local result=$(curl -s http://localhost:$PORT/completion \
        -H "Content-Type: application/json" \
        -d '{"prompt": "Hello, please write a paragraph about artificial intelligence:", "n_predict": 128, "temperature": 0.7}' 2>/dev/null | \
        python3 -c "import json,sys; d=json.load(sys.stdin); ts=d.get('timings',{}).get('predicted_per_second',0); t=d.get('tokens_predicted',0); print(f'{ts:.2f}' if ts else '0')" 2>/dev/null || echo "0")

    # 停止服务器
    kill $pid 2>/dev/null || true
    wait $pid 2>/dev/null || true

    local status="OK"
    local notes=""
    if [ "$result" = "0" ] || [ -z "$result" ]; then
        status="INFERENCE_FAILED"
        notes="Inference test failed"
        result=0
    fi

    echo "$ctx,$ngl,$fa,$kvo,$ctk,$ctv,$split,$vram,$status,$result,$notes" >> "$RESULT_FILE"

    if [ "$status" = "OK" ]; then
        echo "✅ VRAM: ${vram}MiB, Speed: ${result} t/s"
    else
        echo "⚠️  $status - $notes"
    fi

    return 0
}

echo "=========================================="
echo "JoyAI-LLM-Flash V100 参数优化"
echo "=========================================="
echo "模型: 28GB Q4_K_M"
echo "GPU: V100 32GB"
echo ""

# 阶段 1: 找到最大 context（使用全 GPU 和量化 KV cache）
echo "=== 阶段 1: 测试最大 Context 大小 ==="
echo "策略: 全 GPU 层 + Flash Attention + Q8_0 KV cache"

for ctx in 8192 12288 16384 20480 24576 28672 32768; do
    test_config $ctx -1 on on q8_0 q8_0 layer || echo "跳过"
done

# 阶段 2: 找到最佳 GPU 层数
# 基于阶段 1 找到的最大 ctx，测试不同 GPU 层数
echo ""
echo "=== 阶段 2: 测试 GPU 层数影响 (ctx=16384) ==="

MAX_CTX=16384
for ngl in -1 60 50 40 30 20 10 0; do
    test_config $MAX_CTX $ngl on on q8_0 q8_0 layer || echo "跳过"
done

# 阶段 3: KV cache 量化对比
echo ""
echo "=== 阶段 3: KV Cache 量化对比 (ctx=24576) ==="

TEST_CTX=24576
# 不同 KV cache 量化级别
for cache in "f16,f16" "q8_0,q8_0" "q4_0,q4_0"; do
    IFS=',' read -r ctk ctv <<< "$cache"
    test_config $TEST_CTX -1 on on $ctk $ctv layer || echo "跳过"
done

# 阶段 4: 关闭 KV offload 测试（如果显存不足）
echo ""
echo "=== 阶段 4: KV Offload 策略 (大 context) ==="

for ctx in 32768 65536; do
    # 尝试关闭 KV offload，让 KV 留在 CPU
    test_config $ctx -1 on off q8_0 q8_0 layer || echo "跳过"
done

# 输出结果汇总
echo ""
echo "=========================================="
echo "测试结果汇总"
echo "=========================================="
echo ""
echo "成功的配置:"
awk -F',' 'NR>1 && $9=="OK" {printf "  ctx=%-6s ngl=%-4s cache=%s/%s vram=%sMiB speed=%s t/s\n", $1, $2, $5, $6, $8, $10}' "$RESULT_FILE" | sort -t'=' -k4 -n -r | head -10

echo ""
echo "最大成功的 context:"
awk -F',' 'NR>1 && $9=="OK" {print $1}' "$RESULT_FILE" | sort -n | tail -1

echo ""
echo "完整结果保存在: $RESULT_FILE"
cat "$RESULT_FILE"
