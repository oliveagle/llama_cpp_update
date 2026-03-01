#!/bin/bash
# JoyAI-LLM-Flash V100 Context 上限测试脚本

PRESET_FILE="/mnt/volume3/llama_cpp/presets/mypresets-cuda.ini"
MODEL_NAME="JoyAI-LLM-Flash-Q4_K_M"
PORT=8401

test_ctx_size() {
    local ctx_size=$1
    echo "=========================================="
    echo "Testing ctx-size: $ctx_size"

    # 更新配置
    sed -i "s/\[JoyAI-LLM-Flash-Q4_K_M\]/[TEMP]/" "$PRESET_FILE"
    sed -i "s/ctx-size = .*/ctx-size = $ctx_size/" "$PRESET_FILE"
    sed -i "s/\[TEMP\]/[JoyAI-LLM-Flash-Q4_K_M]/" "$PRESET_FILE"

    # 重启服务
    sudo systemctl restart llama-server-8401.service

    # 等待服务启动
    for i in {1..30}; do
        sleep 2
        if curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
            break
        fi
        echo -n "."
    done
    echo ""

    # 检查服务状态
    if ! curl -s http://localhost:$PORT/health > /dev/null 2>&1; then
        echo "❌ 服务启动失败 (ctx=$ctx_size)"
        return 1
    fi

    # 获取显存使用
    local vram=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits 2>/dev/null | head -1)
    echo "显存使用: ${vram}MiB"

    # 测试推理
    local result=$(curl -s http://localhost:$PORT/v1/chat/completions \
        -H "Content-Type: application/json" \
        -d "{\"model\": \"$MODEL_NAME\", \"messages\": [{\"role\": \"user\", \"content\": \"你好\"}], \"max_tokens\": 30}" 2>/dev/null | \
        python3 -c "import json,sys; d=json.load(sys.stdin); c=d.get('choices',[{}])[0].get('message',{}).get('content',''); print('OK' if c else 'FAIL')")

    if [ "$result" = "OK" ]; then
        echo "✅ 推理成功 (ctx=$ctx_size)"
        return 0
    else
        echo "❌ 推理失败 (ctx=$ctx_size)"
        return 1
    fi
}

echo "开始测试 JoyAI-LLM-Flash 在 V100 上的 Context 上限"
echo "模型大小: ~28GB, V100 显存: 32GB"
echo ""

# 测试不同 context 大小
test_sizes=(8192 12288 16384 20480 24576 28672 30720 32768)

last_success=0
for size in "${test_sizes[@]}"; do
    if test_ctx_size "$size"; then
        last_success=$size
    else
        echo ""
        echo "=========================================="
        echo "找到上限: 最大成功 ctx-size = $last_success"
        echo "=========================================="
        break
    fi
    echo ""
done

# 恢复最优配置
if [ $last_success -gt 0 ]; then
    echo ""
    echo "恢复最优配置 ctx-size = $last_success"
    sed -i "s/\[JoyAI-LLM-Flash-Q4_K_M\]/[TEMP]/" "$PRESET_FILE"
    sed -i "s/ctx-size = .*/ctx-size = $last_success/" "$PRESET_FILE"
    sed -i "s/\[TEMP\]/[JoyAI-LLM-Flash-Q4_K_M]/" "$PRESET_FILE"
    sudo systemctl restart llama-server-8401.service
fi
