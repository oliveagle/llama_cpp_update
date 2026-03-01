#!/bin/bash

# llama.cpp CUDA 服务器管理脚本 - 带 RoPE 缩放支持 (V100 - 端口 8401)
# 使用 RoPE 缩放突破模型训练 context 限制

set -e

_SROOT="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"

# 配置
SERVER_BIN="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
PRESETS_FILE="$_SROOT/presets/mypresets.ini"
PORT=8401
LOG_FILE="$_SROOT/logs/cuda-server-rope.log"
PID_FILE="$_SROOT/logs/cuda-server-rope.pid"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# 确保日志目录存在
mkdir -p "$_SROOT/logs"

# 获取服务器 PID
get_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE" 2>/dev/null
    else
        pgrep -f "llama-server.*port $PORT" || echo ""
    fi
}

# 检查是否运行
is_running() {
    local pid=$(get_pid)
    if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
        return 0
    fi
    return 1
}

# 启动服务器 (带 RoPE 缩放)
start() {
    if is_running; then
        log_warn "CUDA 服务器 (端口 $PORT) 已在运行 (PID: $(get_pid))"
        return 0
    fi

    if [ ! -f "$SERVER_BIN" ]; then
        log_error "服务器可执行文件不存在: $SERVER_BIN"
        return 1
    fi

    log_info "启动 CUDA 服务器 (带 RoPE 缩放)..."
    log_info "目标: 突破 40K 限制，实现 128K context"

    # RoPE 缩放配置
    # Qwen3-0.6B 原生支持 40K (40960)
    # 目标 128K (131072)
    # scale = 40960 / 131072 ≈ 0.3125
    ROPE_FREQ_BASE=1000000.0  # Qwen3 默认值
    ROPE_FREQ_SCALE=0.3125    # 扩展 3.2 倍

    log_info "RoPE 配置: freq_base=$ROPE_FREQ_BASE, freq_scale=$ROPE_FREQ_SCALE"

    # 直接启动 - 多模型模式 (带 RoPE 缩放)
    local PRESETS_CUDA="$_SROOT/presets/mypresets-cuda.ini"

    CUDA_VISIBLE_DEVICES=0 \
    PATH=/usr/local/cuda-12.5/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda-12.5/lib64:$LD_LIBRARY_PATH \
    nohup "$SERVER_BIN" \
        --models-max 8 \
        --models-preset "$PRESETS_CUDA" \
        --host 0.0.0.0 \
        --port $PORT \
        -c 131072 \
        -n 4096 \
        -ngl 99 \
        --override-kv "qwen3.rope.freq_base=float:$ROPE_FREQ_BASE,qwen3.rope.freq_scale=float:$ROPE_FREQ_SCALE" \
        >> "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"
    sleep 3

    if is_running; then
        log_info "CUDA 服务器启动成功 (PID: $(get_pid))"
        log_info "RoPE 缩放已启用，尝试支持 128K context"
    else
        log_error "CUDA 服务器启动失败，查看日志: $LOG_FILE"
        return 1
    fi
}

# 停止服务器
stop() {
    local pid=$(get_pid)
    if [ -z "$pid" ]; then
        log_warn "CUDA 服务器未运行"
        return 0
    fi

    log_info "停止 CUDA 服务器..."
    kill -TERM "$pid" 2>/dev/null || true
    sleep 2
    if kill -0 "$pid" 2>/dev/null; then
        kill -KILL "$pid" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
    log_info "CUDA 服务器已停止"
}

# 查看状态
status() {
    echo "=========================================="
    echo "llama.cpp CUDA 服务器 (RoPE 模式)"
    echo "=========================================="
    if is_running; then
        echo -e "状态: ${GREEN}运行中${NC} (PID: $(get_pid))"
    else
        echo -e "状态: ${RED}已停止${NC}"
    fi
    echo ""
}

# 重启服务器
restart() {
    log_info "重启 CUDA 服务器..."
    stop
    sleep 2
    start
}

# 主流程
case "${1:-}" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        status
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
