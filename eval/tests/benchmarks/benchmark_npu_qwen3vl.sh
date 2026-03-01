#!/bin/bash
#
# Qwen3-VL-4B NPU 吞吐量性能测试脚本
#
# 使用方法:
# 1. 准备 ONNX 模型 (参见 ../docs/guides/qwen3vl-onnx-conversion.md)
# 2. export LLAMA_NPU_MODEL=/path/to/qwen3-vl-4b.onnx
# 3. ./tests/benchmark_npu_qwen3vl.sh
#

set -e

# 配置
URL="http://localhost:8404"
LOG_DIR="/mnt/volume3/llama_cpp/logs"
LOG_FILE="$LOG_DIR/npu_benchmark.log"
PID_FILE="$LOG_DIR/llama-npu-server.pid"

# 模型路径（需要用户设置）
MODEL_PATH="${LLAMA_NPU_MODEL:-}"

# NPU 服务器
NPU_SERVER="/mnt/volume3/llama_cpp/src/ryzenai/llama-npu-server"
MANAGER_SCRIPT="/mnt/volume3/llama_cpp/bin/llama-npu-server.sh"

# 测试参数
NUM_RUNS=5
MAX_TOKENS=200
CTX_SIZE=4096

# 测试提示词（纯文本，Qwen3-VL 支持视觉和文本输入）
TEST_PROMPTS=(
    "请介绍一下你自己"
    "解释一下量子计算的基本原理"
    "写一首关于春天的诗"
    "什么是人工智能？"
    "请描述一下机器学习的工作流程"
)

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "[$(date '+%H:%M:%S')] $1"
}

pass() {
    echo -e "${GREEN}✓${NC} $1"
}

fail() {
    echo -e "${RED}✗${NC} $1"
}

info() {
    echo -e "${BLUE}→${NC} $1"
}

# 检查模型文件
check_model() {
    if [ -z "$MODEL_PATH" ]; then
        fail "未设置模型路径"
        echo ""
        echo "请设置环境变量 LLAMA_NPU_MODEL:"
        echo "  export LLAMA_NPU_MODEL=/path/to/qwen3-vl-4b.onnx"
        echo ""
        echo "可用的 ONNX 模型位置:"
        find /mnt/volume3 -name "*.onnx" 2>/dev/null | head -10 || echo "  未找到 .onnx 文件"
        echo ""
        echo "如需转换 Qwen3-VL 模型到 ONNX，请参照："
        echo "  docs/guides/qwen3vl-onnx-conversion.md"
        echo ""
        exit 1
    fi

    if [ ! -f "$MODEL_PATH" ]; then
        fail "模型文件不存在：$MODEL_PATH"
        exit 1
    fi

    pass "模型文件：$MODEL_PATH"
}

# 检查 ryzenai-server 是否已下载
check_ryzenai_server() {
    local install_dir="$HOME/.cache/llama.cpp/ryzenai-server"
    if [ ! -f "$install_dir/ryzenai-server" ]; then
        info "ryzenai-server 未下载，正在下载..."
        "$MANAGER_SCRIPT" download
    fi
    pass "ryzenai-server 已安装"
}

# 停止现有服务
stop_server() {
    log "停止现有服务..."
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null || true
            sleep 2
            kill -9 "$PID" 2>/dev/null || true
        fi
        rm -f "$PID_FILE"
    fi
    pkill -9 -f "llama-npu-server" 2>/dev/null || true
    pkill -9 -f "ryzenai-server" 2>/dev/null || true
    sleep 2
    pass "服务已停止"
}

# 启动服务
start_server() {
    log "启动 llama-npu-server..."

    mkdir -p "$LOG_DIR"

    export LLAMA_NPU_MODEL="$MODEL_PATH"
    export LLAMA_NPU_PORT=8404
    export LLAMA_NPU_HOST="127.0.0.1"
    export LLAMA_NPU_CTX_SIZE="$CTX_SIZE"

    nohup "$NPU_SERVER" \
        --model "$MODEL_PATH" \
        --host 127.0.0.1 \
        --port 8404 \
        --ctx-size "$CTX_SIZE" \
        > "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"

    # 等待服务器启动
    log "等待服务器启动 (最多 120 秒)..."
    for i in {1..120}; do
        if curl -s "$URL/health" > /dev/null 2>&1; then
            pass "服务器已就绪 (PID: $(cat $PID_FILE))"
            return 0
        fi

        # 检查进程是否还在运行
        if ! kill -0 $(cat "$PID_FILE") 2>/dev/null; then
            fail "服务器进程已终止"
            cat "$LOG_FILE"
            return 1
        fi

        if [ $((i % 10)) -eq 0 ]; then
            info "等待中... (${i}s)"
        fi
        sleep 1
    done

    fail "服务器启动超时"
    cat "$LOG_FILE"
    return 1
}

# 单次测试
run_benchmark() {
    local prompt="$1"
    local run_num="$2"

    local start_time=$(date +%s.%N)

    # 发送请求
    local response=$(curl -s -X POST "$URL/v1/chat/completions" \
        -H "Content-Type: application/json" \
        -d "{
            \"messages\": [
                {\"role\": \"user\", \"content\": \"$prompt\"}
            ],
            \"max_tokens\": $MAX_TOKENS
        }" \
        --connect-timeout 10 \
        --max-time 300)

    local end_time=$(date +%s.%N)

    # 解析结果
    local tokens=$(echo "$response" | jq -r '.usage.completion_tokens // 0' 2>/dev/null)
    local prompt_tokens=$(echo "$response" | jq -r '.usage.prompt_tokens // 0' 2>/dev/null)
    local error=$(echo "$response" | jq -r '.error.message // empty' 2>/dev/null)

    local duration=$(echo "$end_time - $start_time" | bc)

    if [ "$tokens" != "0" ] && [ -n "$tokens" ] && [ "$tokens" != "null" ]; then
        local tps=$(echo "scale=2; $tokens / $duration" | bc 2>/dev/null || echo "N/A")
        local first_token_time=$(echo "scale=3; $duration / $tokens" | bc 2>/dev/null || echo "N/A")

        echo "  Run $run_num: ${duration}s | $tokens tok | ${tps} tok/s | ${first_token_time}s/token"

        # 返回 tokens/s 用于计算平均值
        echo "$tps"
    else
        if [ -n "$error" ]; then
            echo "  Run $run_num: FAILED - $error"
        else
            echo "  Run $run_num: FAILED - 无效的响应"
        fi
        echo "0"
    fi
}

# 主测试函数
benchmark() {
    local total_tps=0
    local valid_runs=0

    echo ""
    echo "============================================================"
    echo "Qwen3-VL-4B NPU 吞吐量测试"
    echo "============================================================"
    echo "模型：$MODEL_PATH"
    echo "上下文：$CTX_SIZE"
    echo "最大输出：$MAX_TOKENS tokens"
    echo "测试次数：$NUM_RUNS"
    echo "============================================================"
    echo ""

    for i in $(seq 1 $NUM_RUNS); do
        local prompt_idx=$((($i - 1) % ${#TEST_PROMPTS[@]}))
        local prompt="${TEST_PROMPTS[$prompt_idx]}"

        info "测试 $i/$NUM_RUNS: ${prompt:0:30}..."

        local result=$(run_benchmark "$prompt" "$i")

        # 提取 TPS (最后一行)
        local tps=$(echo "$result" | tail -1)

        if [ "$tps" != "0" ] && [ "$tps" != "N/A" ]; then
            total_tps=$(echo "$total_tps + $tps" | bc 2>/dev/null || echo "$total_tps")
            ((valid_runs++))
        fi

        echo ""
    done

    # 计算平均值
    if [ $valid_runs -gt 0 ]; then
        local avg_tps=$(echo "scale=2; $total_tps / $valid_runs" | bc)
        echo "============================================================"
        echo "结果汇总"
        echo "============================================================"
        echo "有效测试：$valid_runs / $NUM_RUNS"
        echo "平均吞吐量：${avg_tps} tokens/s"
        echo "============================================================"
    else
        echo "============================================================"
        echo "测试结果：所有测试均失败"
        echo "============================================================"
    fi
}

# 检查系统信息
show_system_info() {
    echo ""
    echo "============================================================"
    echo "系统信息"
    echo "============================================================"

    # 内核版本
    info "内核版本：$(uname -r)"

    # 检查 NPU
    if lsmod | grep -q amdxdna; then
        pass "AMD NPU 驱动：amdxdna 已加载"
    else
        info "AMD NPU 驱动：未加载 amdxdna (可能不在 AMD NPU 硬件上)"
    fi

    # 内存信息
    local total_mem=$(free -h | awk '/^Mem:/ {print $2}')
    local used_mem=$(free -h | awk '/^Mem:/ {print $3}')
    info "内存：$used_mem / $total_mem"

    echo ""
}

# 清理
cleanup() {
    log "清理..."
    # 不自动停止服务，方便用户继续测试
    # stop_server
}

trap cleanup EXIT

# 主流程
main() {
    echo ""
    echo -e "${GREEN}============================================================"
    echo "  AMD NPU Qwen3-VL-4B 吞吐量性能测试"
    echo -e "============================================================${NC}"

    show_system_info

    check_model
    check_ryzenai_server

    stop_server
    start_server

    # 等待模型加载
    sleep 5

    benchmark

    echo ""
    info "日志文件：$LOG_FILE"
    echo ""
}

# 运行
main
