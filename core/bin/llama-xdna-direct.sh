#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Config
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8409}"
VENV="${VENV:-$HOME/venvs/py312}"
LOG_DIR="${LOG_DIR:-$PROJECT_ROOT/logs}"
LOG_FILE="$LOG_DIR/xdna-direct-npu.log"
PID_FILE="$LOG_DIR/xdna-direct-npu.pid"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

show_help() {
    cat << 'HELP'
Usage: $0 {start|stop|restart|status|logs|check}

Commands:
  start   - Start AMD XDMA NPU inference server
  stop    - Stop server
  restart - Restart server
  status  - Show server status
  logs    - Show server logs
  check   - Check amdxdna driver status

Environment variables:
  HOST    - Bind address (default: $HOST)
  PORT    - Port number (default: $PORT)
  VENV    - Python virtual environment (default: $VENV)
  LOG_DIR - Log directory (default: $LOG_DIR)
HELP
}

check_xdna_driver() {
    echo -e "${CYAN}Checking AMD XDMA NPU driver...${NC}"

    if lsmod | grep -q amdxdna; then
        echo -e "${GREEN}amdxdna module loaded${NC}"
    else
        echo -e "${RED}amdxdna module not loaded${NC}"
        return 1
    fi

    if [ -f /sys/module/amdxdna/initstate ]; then
        state=$(cat /sys/module/amdxdna/initstate 2>/dev/null || echo "unknown")
        if [ "$state" = "live" ]; then
            echo -e "${GREEN}amdxdna module state: live${NC}"
        else
            echo -e "${YELLOW}amdxdna module state: $state${NC}"
        fi
    else
        echo -e "${YELLOW}Cannot read amdxdna state${NC}"
    fi

    echo -e "\n${CYAN}Module Information:${NC}"
    if [ -d /sys/module/amdxdna ]; then
        for attr in coresize initsize initstate refcnt; do
            attr_path="/sys/module/amdxdna/$attr"
            if [ -f "$attr_path" ]; then
                value=$(cat "$attr_path" 2>/dev/null || echo "N/A")
                echo "  $attr: $value"
        done
    fi
}

# Start server
start_server() {
    check_venv

    mkdir -p "$LOG_DIR"

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}Server already running (PID: $PID)${NC}"
            exit 0
        else
            rm -f "$PID_FILE"
        fi
    fi

    check_xdna_driver || echo -e "${YELLOW}Warning: amdxdna driver not available, server will run in limited mode${NC}"

    echo -e "${GREEN}Starting AMD XDMA NPU inference server...${NC}"
    echo "Address: $HOST:$PORT"
    echo "Environment: $VENV"

    echo -e "\n${CYAN}Implementation Details:${NC}"
    echo "Direct amdxdna driver communication (experimental)"
    echo "NumPy vectorized inference simulation"
    echo "OpenAI-compatible API"
    echo -e "${YELLOW}Note: This is an experimental implementation${NC}"
    echo "Actual NPU execution requires:"
    echo "  - AMD official RyzenAI SDK for Linux"
    echo "  - amdxdna driver API documentation"

    nohup "$VENV/bin/python3" \
        "$PROJECT_ROOT/src/amdxdna_npu/xdna_direct_infer.py" \
        --host "$HOST" \
        --port "$PORT" \
        > "$LOG_FILE" 2>&1 &

    PID=$!
    echo $PID > "$PID_FILE"

    sleep 3

    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}Server started successfully (PID: $PID)${NC}"
        echo "Logs: $LOG_FILE"
        echo "Health check: curl http://$HOST:$PORT/health"
        echo "XDNA info: curl http://$HOST:$PORT/xdna/info"
    else
        echo -e "${RED}Server failed to start${NC}"
        echo "Check logs: tail -f $LOG_FILE"
        exit 1
    fi
}

# Stop server
stop_server() {
    if [ ! -f "$PID_FILE" ]; then
        echo -e "${YELLOW}Server not running${NC}"
        exit 0
    fi

    PID=$(cat "$PID_FILE")

    if ps -p "$PID" > /dev/null 2>&1; then
        echo -e "${GREEN}Stopping server (PID: $PID)...${NC}"
        kill "$PID"
        sleep 2

        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${YELLOW}Force killing process${NC}"
            kill -9 "$PID"
        fi

        rm -f "$PID_FILE"
        echo -e "${GREEN}Server stopped${NC}"
    else
        rm -f "$PID_FILE"
        echo -e "${YELLOW}Server already stopped${NC}"
    fi
}

# Restart server
restart_server() {
    stop_server
    sleep 1
    start_server
}

# Show status
show_status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            echo -e "${GREEN}Server running${NC}"
            echo "PID: $PID"
            echo "Address: $HOST:$PORT"

            check_xdna_driver
        else
            rm -f "$PID_FILE"
            echo -e "${YELLOW}Server not running (PID file exists but process dead)${NC}"
        fi
    else
        echo -e "${YELLOW}Server not running${NC}"
    fi
}

# Show logs
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo -e "${RED}Log file not found: $LOG_FILE${NC}"
        exit 1
    fi
}

# Main
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
    check)
        check_xdna_driver
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        echo
        show_help
        exit 1
        ;;
esac
