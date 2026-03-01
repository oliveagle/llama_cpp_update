#!/bin/bash

# llama.cpp Vulkan 服务器管理脚本 (AMD gfx1151 - 端口 8400)

set -e

_SROOT="$(cd "$(dirname "$(realpath "$0")")/../.." && pwd -P)"

# 配置
SERVER_BIN="$_SROOT/current/llama-server"
PRESETS_FILE="$_SROOT/config/presets/mypresets.ini"
PORT=8400
LOG_FILE="$_SROOT/logs/vulkan-server.log"
PID_FILE="$_SROOT/logs/vulkan-server.pid"

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

# 查找可用的 Vulkan 版本
find_vulkan_binary() {
    local vulkan_dir=$(readlink -f "$_SROOT/current")

    # 检查当前版本是否有 Vulkan 库 (in root dir, not lib/)
    if [ ! -f "$vulkan_dir/libggml-vulkan.so" ]; then
        # 尝试找到有 Vulkan 库的版本
        for dir in $_SROOT/downloads/llama-b*; do
            if [ -f "$dir/libggml-vulkan.so" ]; then
                echo "$dir/llama-server"
                return 0
            fi
        done
        return 1
    fi
    echo "$vulkan_dir/llama-server"
    return 0
}

# 启动服务器
start() {
    if is_running; then
        log_warn "Vulkan 服务器 (端口 $PORT) 已在运行 (PID: $(get_pid))"
        return 0
    fi

    # 查找可用的 Vulkan 二进制文件
    local vulkan_bin=$(find_vulkan_binary)
    if [ -z "$vulkan_bin" ] || [ ! -f "$vulkan_bin" ]; then
        log_error "未找到可用的 Vulkan 服务器可执行文件"
        log_error "请先运行 ./update_llama_cpp.sh 安装 Vulkan 版本"
        return 1
    fi

    log_info "使用 Vulkan 版本: $vulkan_bin"
    log_info "启动 Vulkan 服务器 (端口 $PORT, GPU: gfx1151)..."

    # 设置 AMD GPU 环境
    local amd_icd="/etc/vulkan/icd.d/amd_icd64.json"
    if [ -f "$amd_icd" ]; then
        export VK_ICD_FILENAMES="$amd_icd"
    fi

    # 获取第一个预设模型作为默认模型
    local default_model=""
    if [ -f "$PRESETS_FILE" ]; then
        default_model=$(grep "^m = " "$PRESETS_FILE" | head -1 | cut -d'=' -f2 | tr -d ' ')
    fi

    if [ -z "$default_model" ] || [ ! -f "$default_model" ]; then
        default_model="/mnt/volume3/modelscope_models/Qwen/Qwen3-Coder-Next-GGUF/Q4_K_M/Qwen3-Coder-Next-Q4_K_M-00001-of-00004.gguf"
    fi

    nohup "$vulkan_bin" \
        -m "$default_model" \
        --host 0.0.0.0 \
        --port $PORT \
        -c 8192 \
        -n 2048 \
        -ngl 99 \
        >> "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"
    sleep 2

    if is_running; then
        log_info "Vulkan 服务器启动成功 (PID: $(get_pid))"
    else
        log_error "Vulkan 服务器启动失败，查看日志: $LOG_FILE"
        return 1
    fi
}

# 停止服务器
stop() {
    local pid=$(get_pid)
    if [ -z "$pid" ]; then
        log_warn "Vulkan 服务器 (端口 $PORT) 未运行"
        return 0
    fi

    log_info "停止 Vulkan 服务器 (PID: $pid)..."
    kill -TERM "$pid" 2>/dev/null || true
    sleep 2
    if kill -0 "$pid" 2>/dev/null; then
        kill -KILL "$pid" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
    log_info "Vulkan 服务器已停止"
}

# 查看状态
status() {
    echo "=========================================="
    echo "llama.cpp Vulkan 服务器 (gfx1151 - 端口 $PORT)"
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
    echo ""
}

# 重启服务器
restart() {
    log_info "重启 Vulkan 服务器..."
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
llama.cpp Vulkan 服务器管理脚本 (AMD gfx1151 - 端口 $PORT)

用法:
  $0 {start|stop|restart|status|logs}

命令:
  start     启动 Vulkan 服务器
  stop      停止 Vulkan 服务器
  restart   重启 Vulkan 服务器
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
