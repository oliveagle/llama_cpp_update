#!/bin/bash
#
# RuvLTRA Agent 路由服务
# 端口：8402
# 模型：ruvltra-claude-code-0.5b-q4_k_m.gguf
# 用途：Claude Code Agent 智能调度
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MODEL_PATH="$PROJECT_ROOT/models/ruvltra/ruvltra-claude-code-0.5b-q4_k_m.gguf"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/ruvltra-8402.log"
PID_FILE="$LOG_DIR/ruvltra-8402.pid"

# 端口配置
PORT=8402
HOST="0.0.0.0"

# 查找 llama-server
find_llama_server() {
    if [ -f "$PROJECT_ROOT/downloads/llama-b8069/llama-server" ]; then
        echo "$PROJECT_ROOT/downloads/llama-b8069/llama-server"
    elif [ -f "$PROJECT_ROOT/downloads/llama-b7952/llama-server" ]; then
        echo "$PROJECT_ROOT/downloads/llama-b7952/llama-server"
    elif command -v llama-server &> /dev/null; then
        command -v llama-server
    else
        echo "错误：找不到 llama-server" >&2
        exit 1
    fi
}

LLAMA_SERVER=$(find_llama_server)

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "RuvLTRA 服务已在运行 (PID: $(cat $PID_FILE))"
        return 0
    fi

    if [ ! -f "$MODEL_PATH" ]; then
        echo "错误：模型文件不存在：$MODEL_PATH" >&2
        exit 1
    fi

    mkdir -p "$LOG_DIR"

    echo "启动 RuvLTRA 路由服务 (端口 $PORT)..."
    echo "模型：$MODEL_PATH"
    echo "日志：$LOG_FILE"

    nohup "$LLAMA_SERVER" \
        --model "$MODEL_PATH" \
        --host "$HOST" \
        --port "$PORT" \
        --ctx-size 4096 \
        --n-predict 512 \
        -t 4 \
        -tb 4 \
        --batch-size 2048 \
        --ubatch-size 512 \
        --cache-type-k q8_0 \
        --cache-type-v q8_0 \
        --embeddings \
        --log-file "$LOG_FILE" \
        > "$LOG_FILE" 2>&1 &

    echo $! > "$PID_FILE"
    sleep 2

    if kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "✓ RuvLTRA 服务已启动 (PID: $(cat $PID_FILE))"
        echo "API 地址：http://localhost:$PORT"
    else
        echo "✗ 启动失败，查看日志：$LOG_FILE" >&2
        exit 1
    fi
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "停止 RuvLTRA 服务 (PID: $PID)..."
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

restart() {
    stop
    sleep 1
    start
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "✓ RuvLTRA 服务运行中 (PID: $PID)"
            echo "端口：$PORT"
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

logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "日志文件不存在：$LOG_FILE"
        exit 1
    fi
}

case "${1:-status}" in
    start)   start ;;
    stop)    stop ;;
    restart) restart ;;
    status)  status ;;
    logs)    logs ;;
    *)
        echo "用法：$0 {start|stop|restart|status|logs}"
        echo ""
        echo "命令:"
        echo "  start   - 启动 RuvLTRA 路由服务"
        echo "  stop    - 停止服务"
        echo "  restart - 重启服务"
        echo "  status  - 查看服务状态"
        echo "  logs    - 查看实时日志"
        exit 1
        ;;
esac
