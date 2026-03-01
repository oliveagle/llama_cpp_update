#!/bin/bash
# Qwen3-VL-8B RoPE 缩放服务器
set -e

_SROOT="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"
SERVER_BIN="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
PORT=8401
LOG_FILE="$_SROOT/logs/qwen3-vl-8b-rope.log"
PID_FILE="$_SROOT/logs/qwen3-vl-8b-rope.pid"

MODEL_PATH="/mnt/volume3/modelscope_models/prithivMLmods/Qwen3-VL-8B-Instruct-abliterated-v2-GGUF/Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0.gguf"
ROPE_SCALE=4.0

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

    log_info "启动 Qwen3-VL-8B + RoPE (32K->128K)..."
    log_info "模型: 8B 参数, Q8_0 量化"

    CUDA_VISIBLE_DEVICES=0 \
    PATH=/usr/local/cuda-12.5/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda-12.5/lib64:$LD_LIBRARY_PATH \
    nohup "$SERVER_BIN" \
        -m "$MODEL_PATH" \
        --host 0.0.0.0 \
        --port $PORT \
        -c 16384 \
        -n 4096 \
        -ngl 99 \
        --chat-template qwen2 \
        --rope-scaling yarn \
        --rope-scale $ROPE_SCALE \
        --yarn-orig-ctx 32768 \
        -np 1 \
        >> "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"
    sleep 8

    if is_running; then
        log_info "服务器启动成功"
    else
        log_error "启动失败"
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

case "${1:-}" in
    start) start ;;
    stop) stop ;;
    restart) stop; sleep 2; start ;;
    *) echo "用法: $0 {start|stop|restart}"; exit 1 ;;
esac
