#!/bin/bash
# 单模型 benchmark 脚本
# 用法: ./benchmark_single.sh <模型路径> [模型别名]

set -e

MODEL_PATH="$1"
MODEL_ALIAS="${2:-$(basename "$MODEL_PATH" .gguf)}"
PORT=8403
LLAMA_SERVER="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
BENCH_DIR="/mnt/volume3/llama_cpp/benchmarks"
RESULT_FILE="$BENCH_DIR/${MODEL_ALIAS}-V100-benchmark.md"

if [ -z "$MODEL_PATH" ] || [ ! -f "$MODEL_PATH" ]; then
    echo "错误: 请提供有效的模型路径"
    echo "用法: $0 <模型路径> [模型别名]"
    exit 1
fi

echo "========================================"
echo "Benchmark: $MODEL_ALIAS"
echo "模型路径: $MODEL_PATH"
echo "开始时间: $(date)"
echo "========================================"
echo ""

# 清理之前的进程
pkill -f "llama-server.*$PORT" 2>/dev/null || true
sleep 2

# 启动 server
echo "启动 llama-server..."
$LLAMA_SERVER \
    -m "$MODEL_PATH" \
    -c 16384 \
    -ngl 999 \
    --flash-attn on \
    -ctk q8_0 -ctv q8_0 \
    --host 127.0.0.1 \
    --port $PORT \
    --no-warmup \
    --alias "$MODEL_ALIAS" > /tmp/bench_${MODEL_ALIAS}.log 2>&1 &

SERVER_PID=$!

# 等待启动
echo -n "等待服务启动"
for i in {1..60}; do
    sleep 1
    if curl -s http://localhost:$PORT/health >/dev/null 2>&1; then
        echo " ✅"
        break
    fi
    echo -n "."
done

if ! curl -s http://localhost:$PORT/health >/dev/null 2>&1; then
    echo " ❌ 启动失败"
    kill $SERVER_PID 2>/dev/null || true
    exit 1
fi

# 获取显存
VRAM=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits | head -1)
echo "显存使用: ${VRAM}MiB"
echo ""

# 运行测试
echo "运行 benchmark..."
python3 << 'EOF' > /tmp/bench_result.json 2>&1
import requests
import json
import time

PORT = 8403
MODEL = "$MODEL_ALIAS"
results = {}

# 预填充测试
for words, label in [(200, '1K'), (800, '4K'), (1600, '8K'), (3200, '16K')]:
    msg = 'The quick brown fox jumps over the lazy dog. ' * words
    start = time.time()
    try:
        resp = requests.post(
            f'http://localhost:{PORT}/v1/chat/completions',
            json={'model': MODEL, 'messages': [{'role': 'user', 'content': msg}], 'max_tokens': 1},
            timeout=300
        )
        elapsed = (time.time() - start) * 1000
        data = resp.json()
        usage = data.get('usage', {})
        prompt_tokens = usage.get('prompt_tokens', 0)
        if prompt_tokens > 0:
            speed = prompt_tokens * 1000 / elapsed
            results[f'prompt_{label}'] = {
                'tokens': prompt_tokens,
                'ms': elapsed,
                'tps': round(speed, 1)
            }
    except Exception as e:
        results[f'prompt_{label}'] = {'error': str(e)}

# 生成速度测试
try:
    start = time.time()
    resp = requests.post(
        f'http://localhost:{PORT}/v1/chat/completions',
        json={'model': MODEL, 'messages': [{'role': 'user', 'content': 'Tell me a story:'}], 'max_tokens': 128},
        timeout=300
    )
    elapsed = (time.time() - start) * 1000
    data = resp.json()
    usage = data.get('usage', {})
    comp_tokens = usage.get('completion_tokens', 0)
    if comp_tokens > 0:
        speed = comp_tokens * 1000 / elapsed
        results['gen_128'] = {
            'tokens': comp_tokens,
            'ms': elapsed,
            'tps': round(speed, 2)
        }
except Exception as e:
    results['gen_128'] = {'error': str(e)}

print(json.dumps(results, indent=2))
EOF

# 读取结果
cat /tmp/bench_result.json
echo ""

# 停止 server
kill $SERVER_PID 2>/dev/null || true
wait $SERVER_PID 2>/dev/null || true

# 生成报告
echo "生成报告: $RESULT_FILE"

cat > "$RESULT_FILE" << EOF
# ${MODEL_ALIAS} V100 性能测试报告

## 测试环境
- **GPU**: NVIDIA V100 32GB
- **模型**: ${MODEL_ALIAS}
- **框架**: llama.cpp
- **测试时间**: $(date +%Y-%m-%d/%H:%M)

## 原始测试数据

\`\`\`json
$(cat /tmp/bench_result.json)
\`\`\`

## GPU 状态
\`\`\`
显存使用: ${VRAM}MiB
\`\`\`

## 测试命令
\`\`\`bash
llama-server \\
  -m ${MODEL_PATH} \\
  -c 16384 -ngl 999 \\
  --flash-attn on -ctk q8_0 -ctv q8_0 \\
  --host 127.0.0.1 --port ${PORT} --no-warmup
\`\`\`
EOF

echo ""
echo "========================================"
echo "Benchmark 完成: $MODEL_ALIAS"
echo "报告: $RESULT_FILE"
echo "结束时间: $(date)"
echo "========================================"
