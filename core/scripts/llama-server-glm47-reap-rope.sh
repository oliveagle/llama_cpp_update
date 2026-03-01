#!/bin/bash
# GLM-4.7-Flash-REAP-23B-A3B RoPE 服务器 (原生200K context)
set -e

_SROOT="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"
SERVER_BIN="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
PORT=8401
LOG_FILE="$_SROOT/logs/glm47-reap-rope.log"
PID_FILE="$_SROOT/logs/glm47-reap-rope.pid"

MODEL_PATH="/mnt/volume3/modelscope_models/unsloth/GLM-4___7-Flash-REAP-23B-A3B-GGUF/GLM-4.7-Flash-REAP-23B-A3B-IQ4_NL.gguf"

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

    log_info "启动 GLM-4.7-Flash-REAP (32K)..."
    log_info "模型: DeepSeek2架构, 13GB"

    CUDA_VISIBLE_DEVICES=0 \
    PATH=/usr/local/cuda-12.5/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda-12.5/lib64:$LD_LIBRARY_PATH \
    nohup "$SERVER_BIN" \
        -m "$MODEL_PATH" \
        --host 0.0.0.0 \
        --port $PORT \
        -c 32768 \
        -n 4096 \
        -ngl 30 \
        --chat-template chatglm3 \
        -np 1 \
        >> "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"
    sleep 10

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
    echo "GLM-4.7-Flash-REAP Server (端口 $PORT)"
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
