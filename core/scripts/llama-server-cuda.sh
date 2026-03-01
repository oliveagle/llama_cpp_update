#!/bin/bash

# llama.cpp CUDA 服务器管理脚本 (V100 - 端口 8401)

set -e

_SROOT="$(cd "$(dirname "$(realpath "$0")")/../.." && pwd -P)"

# 配置
SERVER_BIN="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
PRESETS_FILE="$_SROOT/presets/mypresets.ini"
PORT=8401
LOG_FILE="$_SROOT/logs/cuda-server.log"
PID_FILE="$_SROOT/logs/cuda-server.pid"

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

# 启动服务器
start() {
    if is_running; then
        log_warn "CUDA 服务器 (端口 $PORT) 已在运行 (PID: $(get_pid))"
        return 0
    fi

    if [ ! -f "$SERVER_BIN" ]; then
        log_error "服务器可执行文件不存在: $SERVER_BIN"
        return 1
    fi

    log_info "启动 CUDA 服务器 (端口 $PORT, GPU: V100)..."

    # 使用 systemd 服务启动
    if systemctl --user is-enabled llama-server-8401.service &>/dev/null || \
       systemctl --user is-active llama-server-8401.service &>/dev/null; then
        systemctl --user start llama-server-8401.service
        sleep 2
        if systemctl --user is-active llama-server-8401.service &>/dev/null; then
            log_info "CUDA 服务器已通过 systemd 启动"
            return 0
        fi
    fi

    # 直接启动 - 多模型模式 (支持动态切换)
    local PRESETS_CUDA="$_SROOT/config/presets/mypresets-cuda.ini"

    CUDA_VISIBLE_DEVICES=0 \
    PATH=/usr/local/cuda-12.5/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda-12.5/lib64:$LD_LIBRARY_PATH \
    nohup "$SERVER_BIN" \
        --models-max 4 \
        --models-preset "$PRESETS_CUDA" \
        --host 0.0.0.0 \
        --port $PORT \
        -c 4096 \
        -n 2048 \
        -ngl 99 \
        >> "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"
    sleep 2

    if is_running; then
        log_info "CUDA 服务器启动成功 (PID: $(get_pid))"
    else
        log_error "CUDA 服务器启动失败，查看日志: $LOG_FILE"
        return 1
    fi
}

# 停止服务器
stop() {
    local pid=$(get_pid)
    if [ -z "$pid" ]; then
        log_warn "CUDA 服务器 (端口 $PORT) 未运行"
        return 0
    fi

    log_info "停止 CUDA 服务器 (PID: $pid)..."

    # 先尝试 systemd 停止
    if systemctl --user is-active llama-server-8401.service &>/dev/null; then
        systemctl --user stop llama-server-8401.service
    fi

    # 然后直接 kill
    if kill -0 "$pid" 2>/dev/null; then
        kill -TERM "$pid" 2>/dev/null || true
        sleep 2
        if kill -0 "$pid" 2>/dev/null; then
            kill -KILL "$pid" 2>/dev/null || true
        fi
    fi

    rm -f "$PID_FILE"
    log_info "CUDA 服务器已停止"
}

# 查看状态
status() {
    echo "=========================================="
    echo "llama.cpp CUDA 服务器 (V100 - 端口 $PORT)"
    echo "=========================================="

    if is_running; then
        local pid=$(get_pid)
        echo -e "状态: ${GREEN}运行中${NC} (PID: $pid)"
        if [ -f "$LOG_FILE" ]; then
            echo "日志: $LOG_FILE"
            echo ""
            echo "最近日志:"
            tail -5 "$LOG_FILE" 2>/dev/null | sed 's/^/  /' || true
        fi
    else
        echo -e "状态: ${RED}已停止${NC}"
    fi

    # 检查 systemd 服务
    if systemctl --user list-unit-files 2>/dev/null | grep -q llama-server-8403; then
        local service_status=$(systemctl --user is-active llama-server-8401.service 2>/dev/null || echo "inactive")
        echo ""
        if [ "$service_status" = "active" ]; then
            echo -e "Systemd 服务: ${GREEN}$service_status${NC}"
        else
            echo -e "Systemd 服务: ${YELLOW}$service_status${NC}"
        fi
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

# 查看日志
logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        log_warn "日志文件不存在: $LOG_FILE"
    fi
}

# 显示帮助
help() {
    cat << EOF
llama.cpp CUDA 服务器管理脚本 (V100 - 端口 $PORT)

用法:
  $0 {start|stop|restart|status|logs}

命令:
  start     启动 CUDA 服务器
  stop      停止 CUDA 服务器
  restart   重启 CUDA 服务器
  status    查看服务器状态
  logs      查看实时日志 (tail -f)

配置:
  可执行文件: $SERVER_BIN
  预设文件:   $PRESETS_FILE
  日志文件:   $LOG_FILE

API 端点:
  http://localhost:$PORT/v1/chat/completions

EOF
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
    logs)
        logs
        ;;
    help|--help|-h)
        help
        ;;
    *)
        log_error "未知命令: ${1:-}"
        help
        exit 1
        ;;
esac
