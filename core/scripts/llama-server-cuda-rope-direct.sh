#!/bin/bash

# llama.cpp CUDA 服务器 - RoPE 缩放 (单模型直接模式)
# 直接使用 -m 加载 Qwen3-0.6B 并应用 RoPE 缩放

set -e

_SROOT="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"

SERVER_BIN="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
PORT=8401
LOG_FILE="$_SROOT/logs/cuda-server-rope-direct.log"
PID_FILE="$_SROOT/logs/cuda-server-rope-direct.pid"

MODEL_PATH="/mnt/volume3/modelscope_models/unsloth/Qwen3-0.6B-GGUF/Qwen3-0.6B-Q4_0.gguf"

# RoPE 配置
# Qwen3-0.6B 原生 32K，目标 32K，无需缩放
ROPE_FREQ_BASE=1000000.0
ROPE_FREQ_SCALE=1.0

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1" >&2; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

mkdir -p "$_SROOT/logs"

get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE" 2>/dev/null
    else
        pgrep -f "llama-server.*port $PORT" || echo ""
    fi
}

is_running() {
    local pid=$(get_pid)
    [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null
}

start() {
    if is_running; then
        log_info "服务器已在运行"
        return 0
    fi

    log_info "启动 Qwen3-0.6B (32K Context)..."
    log_info "RoPE: freq_base=$ROPE_FREQ_BASE, scale=$ROPE_FREQ_SCALE"

    # 原生 32K，使用 YaRN 保持稳定性
    ROPE_SCALE=1.0

    CUDA_VISIBLE_DEVICES=0 \
    PATH=/usr/local/cuda-12.5/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda-12.5/lib64:$LD_LIBRARY_PATH \
    nohup "$SERVER_BIN" \
        -m "$MODEL_PATH" \
        --host 0.0.0.0 \
        --port $PORT \
        -c 32768 \
        -n 4096 \
        -ngl 99 \
        --chat-template qwen2 \
        --rope-scaling yarn \
        --rope-scale 1.0 \
        --yarn-orig-ctx 32768 \
        -np 1 \
        >> "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"
    sleep 3

    if is_running; then
        log_info "服务器启动成功 (PID: $(get_pid))"
    else
        log_error "启动失败，查看日志: $LOG_FILE"
        return 1
    fi
}

stop() {
    local pid=$(get_pid)
    if [ -z "$pid" ]; then
        echo "服务器未运行"
        return 0
    fi
    kill -TERM "$pid" 2>/dev/null || true
    sleep 2
    rm -f "$PID_FILE"
    log_info "服务器已停止"
}

status() {
    echo "=========================================="
    echo "llama-server (RoPE Direct Mode - 端口 $PORT)"
    echo "=========================================="
    if is_running; then
        echo -e "状态: ${GREEN}运行中${NC} (PID: $(get_pid))"
    else
        echo -e "状态: ${RED}已停止${NC}"
    fi
    echo ""
}

case "${1:-}" in
    start) start ;;
    stop) stop ;;
    restart) stop; sleep 2; start ;;
    status) status ;;
    *) echo "用法: $0 {start|stop|restart|status}"; exit 1 ;;
esac
