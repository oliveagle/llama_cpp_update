#!/bin/bash
#
# llama-npu-server - AMD NPU 推理服务
# 基于 RyzenAI-Server (ONNX Runtime GenAI)
#
# ⚠️ 状态: 搁置 (2026-02-20)
#
# 官方 ryzenai-server 仅支持 Windows 11，无 Linux 版本
# 后续可使用 DragonNPU 或 ONNX Runtime 替代
#
# 用法：./llama-npu-server.sh {start|stop|restart|status|logs|download}
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 配置
NPU_SERVER="$PROJECT_ROOT/src/ryzenai/llama-npu-server"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/llama-npu-server.log"
PID_FILE="$LOG_DIR/llama-npu-server.pid"

# 默认参数
PORT="${LLAMA_NPU_PORT:-0}"  # 0 = 自动选择
HOST="${LLAMA_NPU_HOST:-127.0.0.1}"
CTX_SIZE="${LLAMA_NPU_CTX_SIZE:-8192}"
MODEL_PATH="${LLAMA_NPU_MODEL:-}"

# 查找 llama-npu-server 二进制
find_server() {
    if [ -f "$NPU_SERVER" ]; then
        echo "$NPU_SERVER"
    elif [ -f "$PROJECT_ROOT/downloads/llama-b8069/llama-npu-server" ]; then
        echo "$PROJECT_ROOT/downloads/llama-b8069/llama-npu-server"
    elif command -v llama-npu-server &> /dev/null; then
        command -v llama-npu-server
    else
        echo "错误：找不到 llama-npu-server" >&2
        echo "请先编译：cd src/ryzenai && make server" >&2
        exit 1
    fi
}

NPU_BIN=$(find_server)

# 下载 ryzenai-server
download() {
    local version="${1:-v1.7.0}"
    echo "下载 ryzenai-server $version..."
    export LLAMA_RYZENAI_SERVER_VERSION="$version"
    "$NPU_BIN" --download
    echo "下载完成！"
}

# 启动服务
start() {
    # 检查是否已在运行
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "llama-npu-server 已在运行 (PID: $(cat $PID_FILE))"
        return 0
    fi

    # 检查模型文件
    if [ -z "$MODEL_PATH" ]; then
        echo "错误：未设置模型路径" >&2
        echo "请设置环境变量 LLAMA_NPU_MODEL 或使用 --model 参数" >&2
        exit 1
    fi

    if [ ! -f "$MODEL_PATH" ]; then
        echo "错误：模型文件不存在：$MODEL_PATH" >&2
        exit 1
    fi

    # 检查 ryzenai-server 是否已下载
    local install_dir="$HOME/.cache/llama.cpp/ryzenai-server"
    if [ ! -f "$install_dir/ryzenai-server" ]; then
        echo "警告：ryzenai-server 未下载，正在下载..."
        download
    fi

    mkdir -p "$LOG_DIR"

    echo "启动 llama-npu-server..."
    echo "模型：$MODEL_PATH"
    echo "端口：${PORT:-auto}"
    echo "主机：$HOST"
    echo "上下文：$CTX_SIZE"
    echo "日志：$LOG_FILE"

    # 启动进程
    nohup "$NPU_BIN" \
        --model "$MODEL_PATH" \
        --host "$HOST" \
        --port "${PORT:-0}" \
        --ctx-size "$CTX_SIZE" \
        --log-file "$LOG_FILE" \
        > "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"
    sleep 3

    # 检查进程是否成功启动
    if kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "✓ llama-npu-server 已启动 (PID: $(cat $PID_FILE))"
        echo "API 地址：http://$HOST:${PORT:-auto}"
        echo "查看日志：tail -f $LOG_FILE"
    else
        echo "✗ 启动失败，查看日志：$LOG_FILE" >&2
        cat "$LOG_FILE" >&2
        exit 1
    fi
}

# 停止服务
stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "停止 llama-npu-server (PID: $PID)..."
            kill "$PID"
            sleep 2
            if kill -0 "$PID" 2>/dev/null; then
                kill -9 "$PID"
            fi
            rm -f "$PID_FILE"
            echo "✓ 服务已停止"
        else
            echo "服务未运行"
            rm -f "$PID_FILE"
        fi
    else
        echo "服务未运行 (无 PID 文件)"
    fi
}

# 重启服务
restart() {
    stop
    sleep 1
    start
}

# 查看状态
status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "✓ llama-npu-server 运行中 (PID: $PID)"
            echo "端口：${PORT:-auto}"
            echo "模型：$MODEL_PATH"
            return 0
        else
            echo "✗ 服务未运行 (PID 文件存在但进程不存在)"
            return 1
        fi
    else
        echo "✗ 服务未运行"
        return 1
    fi
}

# 查看实时日志
logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "日志文件不存在：$LOG_FILE"
        exit 1
    fi
}

# 显示用法
usage() {
    echo "用法：$0 {start|stop|restart|status|logs|download}"
    echo ""
    echo "命令:"
    echo "  start   - 启动 llama-npu-server"
    echo "  stop    - 停止服务"
    echo "  restart - 重启服务"
    echo "  status  - 查看服务状态"
    echo "  logs    - 查看实时日志"
    echo "  download [version] - 下载 ryzenai-server (可选版本)"
    echo ""
    echo "环境变量:"
    echo "  LLAMA_NPU_MODEL     ONNX 模型路径 (必需)"
    echo "  LLAMA_NPU_PORT      服务端口 (默认：0=自动选择)"
    echo "  LLAMA_NPU_HOST      绑定地址 (默认：127.0.0.1)"
    echo "  LLAMA_NPU_CTX_SIZE  上下文长度 (默认：8192)"
    echo ""
    echo "示例:"
    echo "  # 启动服务"
    echo "  export LLAMA_NPU_MODEL=/path/to/model.onnx"
    echo "  $0 start"
    echo ""
    echo "  # 下载指定版本的 ryzenai-server"
    echo "  $0 download v1.7.0"
    echo ""
    echo "  # 查看状态"
    echo "  $0 status"
}

# 主逻辑
case "${1:-status}" in
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
    download)
        download "${2:-v1.7.0}"
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    *)
        echo "错误：未知命令：$1" >&2
        usage
        exit 1
        ;;
esac
