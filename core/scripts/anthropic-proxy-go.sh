#!/bin/bash
# Anthropic Proxy (Go Version) Management Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
GO_PROXY_DIR="$PROJECT_ROOT/core/go-proxy"
BINARY="$GO_PROXY_DIR/anthropic-proxy"
PID_FILE="$PROJECT_ROOT/core/logs/anthropic-proxy-go.pid"
LOG_FILE="$PROJECT_ROOT/core/logs/anthropic-proxy-go.log"
JSONL_LOG_FILE="$PROJECT_ROOT/core/logs/anthropic-proxy-requests.jsonl"

mkdir -p "$PROJECT_ROOT/core/logs"

# Start proxy
start() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE" 2>/dev/null || true)
        if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
            echo "Proxy is already running (PID: $PID)"
            return 1
        fi
        rm -f "$PID_FILE"
    fi

    echo "Starting Anthropic proxy (Go version)..."
    cd "$GO_PROXY_DIR"
    nohup "$BINARY" > "$LOG_FILE" 2>&1 &
    PID=$!
    echo $PID > "$PID_FILE"
    cd - > /dev/null

    sleep 2
    if kill -0 "$PID" 2>/dev/null; then
        echo "Proxy started successfully (PID: $PID)"
        echo "Logs: $LOG_FILE"
        echo "JSONL Log: $JSONL_LOG_FILE"
    else
        echo "Failed to start proxy"
        echo "Check logs: $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

# Stop proxy
stop() {
    if [ ! -f "$PID_FILE" ]; then
        echo "PID file not found. Trying to find and kill proxy..."
        pkill -f "./anthropic-proxy" 2>/dev/null || true
        return 0
    fi

    PID=$(cat "$PID_FILE" 2>/dev/null || true)
    if [ -z "$PID" ]; then
        echo "Invalid PID file"
        rm -f "$PID_FILE"
        return 1
    fi

    if kill -0 "$PID" 2>/dev/null; then
        echo "Stopping proxy (PID: $PID)..."
        kill "$PID"
        for i in {1..10}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        if kill -0 "$PID" 2>/dev/null; then
            echo "Force stopping..."
            kill -9 "$PID" 2>/dev/null || true
        fi
    fi

    rm -f "$PID_FILE"
    echo "Proxy stopped"
}

# Restart proxy
restart() {
    stop
    sleep 1
    start
}

# Status
status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE" 2>/dev/null || true)
        if [ -n "$PID" ] && kill -0 "$PID" 2>/dev/null; then
            echo "Proxy is running (PID: $PID)"
            echo "Binary: $BINARY"
            echo "Logs: $LOG_FILE"
            echo "JSONL Log: $JSONL_LOG_FILE"
            return 0
        fi
    fi
    echo "Proxy is not running"
    return 1
}

# Build
build() {
    echo "Building Go proxy..."
    cd "$GO_PROXY_DIR"
    go build -o anthropic-proxy main.go
    cd - > /dev/null
    echo "Build complete: $BINARY"
}

# View logs
logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        echo "Log file not found: $LOG_FILE"
    fi
}

# View JSONL log tail
jsonl-tail() {
    if [ -f "$JSONL_LOG_FILE" ]; then
        echo "=== Last 10 JSONL entries ==="
        tail -n 10 "$JSONL_LOG_FILE" | python3 -m json.tool 2>/dev/null || tail -n 10 "$JSONL_LOG_FILE"
    else
        echo "JSONL log file not found: $JSONL_LOG_FILE"
    fi
}

# Quick metrics
metrics() {
    METRICS_URL="http://localhost:8402/metrics"
    if ! curl -s --max-time 5 "$METRICS_URL" > /dev/null 2>&1; then
        echo "Proxy is not running or metrics endpoint unavailable"
        return 1
    fi

    echo "=============================================="
    echo "Anthropic Proxy Metrics (from /metrics endpoint)"
    echo "=============================================="
    echo

    # Parse Prometheus metrics using grep and awk
    requests=$(curl -s "$METRICS_URL" | grep "^anthropic_proxy_requests_total" | awk '{print $NF}')
    responses=$(curl -s "$METRICS_URL" | grep "^anthropic_proxy_responses_total" | awk '{print $NF}')
    errors=$(curl -s "$METRICS_URL" | grep "^anthropic_proxy_errors_total" | awk '{print $NF}')
    success_rate=$(curl -s "$METRICS_URL" | grep "^anthropic_proxy_success_rate" | awk '{print $NF}')
    error_rate=$(curl -s "$METRICS_URL" | grep "^anthropic_proxy_error_rate" | awk '{print $NF}')
    file_size=$(curl -s "$METRICS_URL" | grep "^anthropic_proxy_log_file_size" | awk '{print $NF}')
    last_update=$(curl -s "$METRICS_URL" | grep "^anthropic_proxy_last_update_time" | awk '{print $NF}')

    echo "Total Requests: ${requests:-N/A}"
    echo "Total Responses: ${responses:-N/A}"
    echo "Total Errors: ${errors:-N/A}"
    echo "Success Rate: ${success_rate:-N/A}%"
    echo "Error Rate: ${error_rate:-N/A}%"
    if [ -n "$file_size" ]; then
        size_mb=$(echo "scale=2; $file_size / 1024 / 1024" | bc 2>/dev/null)
        echo "Log File Size: ${size_mb:-N/A} MB"
    fi
    if [ -n "$last_update" ]; then
        update_time=$(date -d "@$last_update" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || echo "N/A")
        echo "Last Update: $update_time"
    fi

    echo ""
    echo "For full Prometheus metrics:"
    echo "  curl $METRICS_URL"
    echo ""
}

# Export Prometheus metrics (now just proxies to built-in endpoint)
export-prometheus() {
    METRICS_URL="http://localhost:8402/metrics"
    if ! curl -s --max-time 5 "$METRICS_URL" > /dev/null 2>&1; then
        echo "Proxy is not running or metrics endpoint unavailable"
        return 1
    fi

    echo "Exporting Prometheus metrics from http://localhost:8402/metrics"
    echo ""
    curl -s "$METRICS_URL"
}

# Help
usage() {
    echo "Usage: $0 {start|stop|restart|status|build|logs|jsonl-tail|metrics|export-prometheus}"
    echo
    echo "Commands:"
    echo "  start            - Start the proxy"
    echo "  stop             - Stop the proxy"
    echo "  restart          - Restart the proxy"
    echo "  status           - Show proxy status"
    echo "  build            - Build the proxy binary"
    echo "  logs             - View proxy logs (tail -f)"
    echo "  jsonl-tail       - View JSONL log (last 10 entries)"
    echo "  metrics          - Show quick metrics"
    echo "  export-prometheus - Export Prometheus format metrics"
}

# Main
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
    build)
        build
        ;;
    logs)
        logs
        ;;
    jsonl-tail)
        jsonl-tail
        ;;
    metrics)
        metrics
        ;;
    export-prometheus)
        export-prometheus
        ;;
    *)
        usage
        exit 1
        ;;
esac
