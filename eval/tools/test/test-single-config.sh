#!/bin/bash
# 手动测试单个配置
# 用法: ./test-single-config.sh [ctx_size] [gpu_layers] [cache_type]

MODEL="/mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf"
PORT=8403
LLAMA_SERVER="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"

CTX=${1:-16384}
NGL=${2:--1}
CACHE=${3:-q8_0}

echo "测试配置:"
echo "  Context: $CTX"
echo "  GPU Layers: $NGL (-1=所有)"
echo "  KV Cache: $CACHE"
echo "  Flash Attention: ON"
echo "  KV Offload: ON"
echo ""

# 构建参数
ARGS="-m $MODEL -c $CTX --host 0.0.0.0 --port $PORT -np 1 -fa on -ctk $CACHE -ctv $CACHE -sm layer"

if [ "$NGL" = "-1" ]; then
    ARGS="$ARGS -ngl 999"
else
    ARGS="$ARGS -ngl $NGL"
fi

echo "启动命令:"
echo "$LLAMA_SERVER $ARGS"
echo ""

# 清理
pkill -f "llama-server.*$PORT" 2>/dev/null || true
sleep 1

# 启动
$LLAMA_SERVER $ARGS &
PID=$!

echo "等待服务器启动 (PID: $PID)..."
for i in {1..60}; do
    sleep 1
    if ! kill -0 $PID 2>/dev/null; then
        echo "服务器启动失败!"
        exit 1
    fi
    if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
        break
    fi
    echo -n "."
done
echo ""

# 检查显存
VRAM=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
echo "显存使用: ${VRAM}MiB"
echo ""

# 测试推理
echo "测试推理..."
curl -s http://localhost:$PORT/completion \
    -H "Content-Type: application/json" \
    -d '{"prompt": "Hello, how are you?", "n_predict": 64, "temperature": 0.7}' | \
    python3 -c "import json,sys; d=json.load(sys.stdin); ts=d.get('timings',{}).get('predicted_per_second',0); t=d.get('tokens_predicted',0); print(f'Tokens: {t}, Speed: {ts:.2f} t/s' if ts else 'Failed')"

# 停止服务器
kill $PID 2>/dev/null || true

echo ""
echo "测试完成"
