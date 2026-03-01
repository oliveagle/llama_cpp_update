#!/bin/bash
# AMD XDNA NPU (Strix Halo) 推理服务器管理脚本
# 直接通过 amdxdna 驱动与 AMD XDNA NPU 通信

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# 配置
MODEL_PATH="${MODEL_PATH:-$PROJECT_ROOT/models/qwen3-onnx/Qwen3-0.6B-ONNX/onnx/model_int8.onnx}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8408}"
VENV="${VENV:-$HOME/venvs/py312}"
LOG_DIR="${LOG_DIR:-$PROJECT_ROOT/logs}"
LOG_FILE="$LOG_DIR/xdna-npu-server.log"
PID_FILE="$LOG_DIR/xdna-npu-server.pid"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 显示帮助
show_help() {
    cat << EOF
用法: $(basename "$0") {start|stop|restart|status|logs}

命令:
  start   - 启动 AMD XDNA NPU 推理服务器
  stop    - 停止服务器
  restart - 重启服务器
  status  - 查看服务器状态
  logs    - 查看服务器日志

环境变量:
  MODEL_PATH - ONNX 模型路径 (默认: $MODEL_PATH)
  HOST       - 绑定地址 (默认: $HOST)
  PORT       - 端口号 (默认: $PORT)
  VENV       - Python 虚拟环境 (默认: $VENV)
  LOG_DIR    - 日志目录 (默认: $LOG_DIR)

示例:
  MODEL_PATH=/path/to/model.onnx ./$(basename "$0") start
  PORT=8080 ./$(basename "$0") start
EOF
}

# 检查 XDNA NPU 是否可用
check_xdna() {
    if [ ! -d "/sys/module/amdxdna" ]; then
        echo -e "${RED}错误: amdxdna 模块未加载${NC}"
        echo "XDNA NPU 不可用"
        return 1
    fi

    local initstate
    initstate=$(cat /sys/module/amdxdna/initstate 2>/dev/null || echo "unknown")

    if [ "$initstate" != "live" ]; then
        echo -e "${YELLOW}警告: amdxdna 模块状态: $initstate${NC}"
        return 1
    fi

    echo -e "${GREEN}XDNA NPU 可用 (状态: $initstate)${NC}"
    return 0
}

# 检查虚拟环境
check_venv() {
    if [ ! -d "$VENV" ]; then
        echo -e "${RED}错误: 虚拟环境不存在: $VENV${NC}"
        exit 1
    fi

    if [ ! -f "$VENV/bin/python3" ]; then
        echo -e "${RED}错误: Python 不存在于虚拟环境: $VENV${NC}"
        exit 1
    fi
}

# 启动服务器
start_server() {
    check_venv

    # 创建日志目录
    mkdir -p "$LOG_DIR"

    # 检查是否已运行
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}服务器已在运行 (PID: $PID)${NC}"
            exit 0
        else
            rm -f "$PID_FILE"
        fi
    fi

    # 检查 XDNA NPU
    check_xdna || echo -e "${YELLOW}注意: XDNA NPU 不可用，将以演示模式运行${NC}"

    echo -e "${GREEN}启动 AMD XDNA NPU 推理服务器...${NC}"
    echo "模型: $MODEL_PATH"
    echo "地址: $HOST:$PORT"
    echo "虚拟环境: $VENV"

    # 启动服务器
    nohup "$VENV/bin/python3" \
        "$PROJECT_ROOT/src/amdxdna_npu/xdna_npu_infer.py" \
        --host "$HOST" \
        --port "$PORT" \
        --model "$MODEL_PATH" \
        > "$LOG_FILE" 2>&1 &

    PID=$!
    echo $PID > "$PID_FILE"

    # 等待启动
    sleep 3

    # 检查是否成功启动
    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}服务器启动成功 (PID: $PID)${NC}"
        echo "日志: $LOG_FILE"
        echo "健康检查: curl http://$HOST:$PORT/health"
        echo "NPU 信息: curl http://$HOST:$PORT/xdna/info"
    else
        echo -e "${RED}服务器启动失败${NC}"
        echo "查看日志: tail -f $LOG_FILE"
        exit 1
    fi
}

# 停止服务器
stop_server() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}服务器未运行${NC}"
        exit 0
    fi

    PID=$(cat "$PID_FILE")

    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}停止服务器 (PID: $PID)...${NC}"
        kill "$PID"
        sleep 2

        # 强制杀死（如果还在运行）
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}强制杀死进程${NC}"
            kill -9 "$PID"
        fi

        rm -f "$PID_FILE"
        echo -e "${GREEN}服务器已停止${NC}"
    else
        rm -f "$PID_FILE"
        echo -e "${YELLOW}服务器已停止${NC}"
    fi
}

# 重启服务器
restart_server() {
    stop_server
    sleep 1
    start_server
}

# 查看状态
show_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${GREEN}服务器运行中${NC}"
            echo "PID: $PID"
            echo "地址: $HOST:$PORT"
            echo "模型: $MODEL_PATH"

            # 检查 XDNA NPU 状态
            check_xdna

            # 尝试健康检查
            HEALTH=$(curl -s "http://$HOST:$PORT/health" 2>/dev/null || echo '{"status":"error"}')
            echo "健康: $HEALTH"
        else
            echo -e "${YELLOW}服务器未运行 (PID 文件存在但进程已死)${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${YELLOW}服务器未运行${NC}"
    fi
}

# 查看日志
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}日志文件不存在: $LOG_FILE${NC}"
        exit 1
    fi
}

# 主函数
case "${1:-help}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}错误: 未知命令 '$1'${NC}"
        echo
        show_help
        exit 1
        ;;
esac
