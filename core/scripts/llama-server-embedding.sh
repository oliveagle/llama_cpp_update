#!/bin/bash

# llama.cpp Embedding 服务器管理脚本 (端口 13232)

set -e

_SROOT="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"

# 配置
# 使用修复后的 CUDA 版本（支持 V-L Embedding）
SERVER_BIN="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
PORT=13232
LOG_FILE="$_SROOT/logs/embedding-server.log"
PID_FILE="$_SROOT/logs/embedding-server.pid"

# 默认使用专用 embedding 模型 (Qwen3-Embedding-8B)
# 默认使用 Qwen3-Embedding-8B (纯文本，效果更好)
DEFAULT_MODEL="/mnt/volume3/modelscope_models/Qwen/Qwen3-Embedding-8B-GGUF/Qwen3-Embedding-8B-Q4_K_M.gguf"

# V-L Embedding 模型（支持图文，但纯文本效果一般）
# DEFAULT_MODEL="/home/oliveagle/.cache/modelscope/hub/models/poloniumrock/Qwen3-VL-Embedding-2B-Q8_0.gguf/Qwen3-VL-Embedding-2B-Q8_0.gguf"

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
    # 直接返回配置的服务器二进制文件
    if [ -f "$SERVER_BIN" ]; then
        echo "$SERVER_BIN"
        return 0
    fi
    return 1
}

# 启动服务器
start() {
    if is_running; then
        log_warn "Embedding 服务器 (端口 $PORT) 已在运行 (PID: $(get_pid))"
        return 0
    fi

    # 查找可用的 Vulkan 二进制文件
    local vulkan_bin=$(find_vulkan_binary)
    if [ -z "$vulkan_bin" ] || [ ! -f "$vulkan_bin" ]; then
        log_error "未找到可用的 Vulkan 服务器可执行文件"
        log_error "请先运行 ./update_llama_cpp.sh 安装 Vulkan 版本"
        return 1
    fi

    # 检查模型文件
    local model_path="${1:-$DEFAULT_MODEL}"
    if [ ! -f "$model_path" ]; then
        log_error "模型文件不存在: $model_path"
        log_info "使用方法: $0 start [模型路径]"
        return 1
    fi

    log_info "使用 Vulkan 版本: $vulkan_bin"
    log_info "使用模型: $model_path"
    log_info "启动 Embedding 服务器 (端口 $PORT, GPU: gfx1151)..."

    # 设置 AMD GPU 环境
    local amd_icd="/etc/vulkan/icd.d/amd_icd64.json"
    if [ -f "$amd_icd" ]; then
        export VK_ICD_FILENAMES="$amd_icd"
    fi

    # 设置库路径
    export LD_LIBRARY_PATH=/home/oliveagle/opt/llama.cpp/build:$LD_LIBRARY_PATH

    nohup "$SERVER_BIN" \
        -m "$model_path" \
        --host 0.0.0.0 \
        --port $PORT \
        -c 8192 \
        -n 512 \
        -ngl 99 \
        --embedding \
        --pooling mean \
        >> "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"
    sleep 2

    if is_running; then
        log_info "Embedding 服务器启动成功 (PID: $(get_pid))"
        log_info "API 端点: http://localhost:$PORT/v1/embeddings"
    else
        log_error "Embedding 服务器启动失败，查看日志: $LOG_FILE"
        return 1
    fi
}

# 停止服务器
stop() {
    local pid=$(get_pid)
    if [ -z "$pid" ]; then
        log_warn "Embedding 服务器 (端口 $PORT) 未运行"
        return 0
    fi

    log_info "停止 Embedding 服务器 (PID: $pid)..."
    kill -TERM "$pid" 2>/dev/null || true
    sleep 2
    if kill -0 "$pid" 2>/dev/null; then
        kill -KILL "$pid" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
    log_info "Embedding 服务器已停止"
}

# 查看状态
status() {
    echo "=========================================="
    echo "llama.cpp Embedding 服务器 (端口 $PORT)"
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
    log_info "重启 Embedding 服务器..."
    stop
    sleep 2
    start "$@"
}

# 查看日志
logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        log_warn "日志文件不存在: $LOG_FILE"
    fi
}

# 测试 embedding
test() {
    log_info "测试 Embedding API..."

    if ! is_running; then
        log_error "Embedding 服务器未运行，请先启动"
        return 1
    fi

    curl -s http://localhost:$PORT/v1/embeddings \
        -H "Content-Type: application/json" \
        -d '{
            "input": "Hello world",
            "encoding_format": "float"
        }' | head -c 500

    echo ""
    log_info "测试完成"
}

# 显示帮助
help() {
    cat << EOF
llama.cpp Embedding 服务器管理脚本 (端口 $PORT)

用法:
  $0 {start|stop|restart|status|logs|test} [模型路径]

命令:
  start [model]  启动 Embedding 服务器（可选指定模型）
  stop           停止 Embedding 服务器
  restart        重启 Embedding 服务器
  status         查看服务器状态
  logs           查看实时日志 (tail -f)
  test           测试 Embedding API

默认模型:
  $DEFAULT_MODEL

API 端点:
  POST http://localhost:$PORT/v1/embeddings

示例:
  # 使用默认模型启动
  $0 start

  # 使用指定模型启动
  $0 start /path/to/your/model.gguf

  # 测试 embedding
  $0 test

EOF
}

# 主流程
case "${1:-}" in
    start)
        shift
        start "$@"
        ;;
    stop)
        stop
        ;;
    restart)
        shift
        restart "$@"
        ;;
    status)
        status
        ;;
    logs)
        logs
        ;;
    test)
        test
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
