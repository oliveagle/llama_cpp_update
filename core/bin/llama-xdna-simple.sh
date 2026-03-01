#!/bin/bash
# AMD XDMA NPU Server - Simple Version

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Config
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8409}"
VENV="${VENV:-$HOME/venvs/py312}"
LOG_DIR="${LOG_DIR:-$PROJECT_ROOT/logs}"
LOG_FILE="$LOG_DIR/xdna-npu.log"
PID_FILE="$LOG_DIR/xdna-npu.pid"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Commands
start() {
    echo -e "${GREEN}Starting AMD XDNA NPU server...${NC}"

    if [ ! -d "$VENV" ]; then
        echo -e "${RED}Virtual environment not found: $VENV${NC}"
        exit 1
    fi

    # Check driver
    if lsmod | grep -q amdxdna; then
        echo -e "${GREEN}amdxdna module loaded${NC}"
    else
        echo -e "${YELLOW}amdxdna module not loaded${NC}"
    fi

    mkdir -p "$LOG_DIR"

    # Start server
    nohup "$VENV/bin/python3" \
        "$PROJECT_ROOT/src/amdxdna_npu/xdna_direct_infer.py" \
        --host "$HOST" --port "$PORT" \
        > "$LOG_FILE" 2>&1 &

    PID=$!
    echo $PID > "$PID_FILE"

    sleep 3

    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}Server started successfully${NC}"
        echo "Address: $HOST:$PORT"
        echo "Logs: $LOG_FILE"
    else
        echo -e "${RED}Server failed${NC}"
        exit 1
    fi
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        kill "$PID" 2>/dev/null
        rm -f "$PID_FILE"
        echo -e "${GREEN}Server stopped${NC}"
    else
        echo -e "${YELLOW}Server not running${NC}"
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
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${GREEN}Running${NC}"
        else
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${YELLOW}Not running${NC}"
    fi

    if lsmod | grep -q amdxdna; then
        echo -e "${GREEN}amdxdna driver: loaded${NC}"
    else
        echo -e "${RED}amdxdna driver: not loaded${NC}"
    fi

    if [ -f /sys/module/amdxdna/initstate ]; then
        state=$(cat /sys/module/amdxdna/initstate 2>/dev/null)
        echo "State: $state"
    fi
}

logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}Log not found${NC}"
        exit 1
    fi
}

case "${1:-help}" in
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
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo
        exit 0
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        ;;
esac
