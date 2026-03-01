#!/bin/bash
# llama-onnx-server.sh - ONNX Runtime Server 管理脚本
#
# 支持 AMD XDNA NPU、CUDA、ROCm、OpenVINO 等多种 Execution Provider

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_ROOT/tmp/onnx-server.pid"
LOG_FILE="$PROJECT_ROOT/logs/onnx-server.log"

# 默认配置
DEFAULT_HOST="0.0.0.0"
DEFAULT_PORT=8406
DEFAULT_MODEL="$PROJECT_ROOT/models/qwen3-onnx/Qwen3-0.6B-ONNX/onnx/model_int8.onnx"
DEFAULT_EP="cpu"
DEFAULT_THREADS=1

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }

# 环境变量
export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"
export LLAMA_ONNX_HOST="${LLAMA_ONNX_HOST:-$DEFAULT_HOST}"
export LLAMA_ONNX_PORT="${LLAMA_ONNX_PORT:-$DEFAULT_PORT}"
export LLAMA_ONNX_MODEL="${LLAMA_ONNX_MODEL:-$DEFAULT_MODEL}"
export LLAMA_ONNX_EP="${LLAMA_ONNX_EP:-$DEFAULT_EP}"
export LLAMA_ONNX_THREADS="${LLAMA_ONNX_THREADS:-$DEFAULT_THREADS}"

# 虚拟环境
VENV_NAME="${LLAMA_ONNX_VENV:-py312}"
VENV_PATH="$HOME/venvs/$VENV_NAME"

# 检查虚拟环境
check_venv() {
    if [ ! -d "$VENV_PATH" ]; then
        log_error "Virtual environment not found: $VENV_PATH"
        log_info "Create with: uv venv $VENV_PATH --seed --python python3.12"
        return 1
    fi
}

# 检查依赖
check_deps() {
    log_info "Checking dependencies..."

    source "$VENV_PATH/bin/activate"

    if ! python -c "import onnxruntime" 2>/dev/null; then
        log_error "onnxruntime not installed"
        log_info "Install with: pip install onnxruntime"
        return 1
    fi

    if ! python -c "import flask" 2>/dev/null; then
        log_error "flask not installed"
        log_info "Install with: pip install flask"
        return 1
    fi

    if ! python -c "import numpy" 2>/dev/null; then
        log_error "numpy not installed"
        log_info "Install with: pip install numpy"
        return 1
    fi

    log_success "Dependencies OK"
}

# 启动服务
start() {
    check_venv || exit 1
    check_deps || exit 1

    # 检查是否已运行
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            log_warning "Server already running (PID: $PID)"
            return 0
        else
            log_warning "Removing stale PID file"
            rm -f "$PID_FILE"
        fi
    fi

    # 检查模型文件
    if [ ! -f "$LLAMA_ONNX_MODEL" ]; then
        log_error "Model not found: $LLAMA_ONNX_MODEL"
        log_info "Set LLAMA_ONNX_MODEL environment variable"
        log_info "Available models:"
        find "$PROJECT_ROOT/models/qwen3-onnx" -name "*.onnx" -type f 2>/dev/null || true
        return 1
    fi

    # 创建日志目录
    mkdir -p "$(dirname "$LOG_FILE")"

    # 启动服务
    log_info "Starting ONNX Runtime server..."
    log_info "  Host: $LLAMA_ONNX_HOST"
    log_info "  Port: $LLAMA_ONNX_PORT"
    log_info "  Model: $LLAMA_ONNX_MODEL"
    log_info "  EP: $LLAMA_ONNX_EP"
    log_info "  Threads: $LLAMA_ONNX_THREADS"

    source "$VENV_PATH/bin/activate"

    nohup python "$PROJECT_ROOT/scripts/onnx_runtime_server.py" \
        --host "$LLAMA_ONNX_HOST" \
        --port "$LLAMA_ONNX_PORT" \
        --model "$LLAMA_ONNX_MODEL" \
        --ep "$LLAMA_ONNX_EP" \
        --threads "$LLAMA_ONNX_THREADS" \
        >> "$LOG_FILE" 2>&1 &

    PID=$!
    echo "$PID" > "$PID_FILE"

    # 等待启动
    sleep 2

    if ps -p "$PID" > /dev/null 2>&1; then
        log_success "Server started (PID: $PID)"
        log_info "Logs: $LOG_FILE"
        log_info "API: http://$LLAMA_ONNX_HOST:$LLAMA_ONNX_PORT"
    else
        log_error "Server failed to start"
        log_info "Check logs: tail -f $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

# 停止服务
stop() {
    if [ ! -f "$PID_FILE" ]; then
        log_warning "PID file not found, server may not be running"
        return 0
    fi

    PID=$(cat "$PID_FILE")

    if ! ps -p "$PID" > /dev/null 2>&1; then
        log_warning "Server not running (stale PID file)"
        rm -f "$PID_FILE"
        return 0
    fi

    log_info "Stopping server (PID: $PID)..."
    kill "$PID"

    # 等待进程结束
    for i in {1..10}; do
        if ! ps -p "$PID" > /dev/null 2>&1; then
            break
        fi
        sleep 1
    done

    # 强制杀死
    if ps -p "$PID" > /dev/null 2>&1; then
        log_warning "Force killing..."
        kill -9 "$PID"
    fi

    rm -f "$PID_FILE"
    log_success "Server stopped"
}

# 重启服务
restart() {
    stop
    sleep 1
    start
}

# 查看状态
status() {
    if [ ! -f "$PID_FILE" ]; then
        log_info "Server: stopped"
        return 1
    fi

    PID=$(cat "$PID_FILE")

    if ! ps -p "$PID" > /dev/null 2>&1; then
        log_info "Server: stopped (stale PID file)"
        rm -f "$PID_FILE"
        return 1
    fi

    log_success "Server: running (PID: $PID)"
    log_info "  Host: $LLAMA_ONNX_HOST:$LLAMA_ONNX_PORT"
    log_info "  Model: $LLAMA_ONNX_MODEL"
    log_info "  EP: $LLAMA_ONNX_EP"

    # 检查 HTTP 端口
    if command -v curl &> /dev/null; then
        if curl -s "http://$LLAMA_ONNX_HOST:$LLAMA_ONNX_PORT/health" > /dev/null 2>&1; then
            log_success "HTTP API: responding"
        else
            log_warning "HTTP API: not responding"
        fi
    fi
}

# 查看日志
logs() {
    if [ ! -f "$LOG_FILE" ]; then
        log_warning "Log file not found: $LOG_FILE"
        return 1
    fi

    if command -v tail &> /dev/null; then
        tail -f "$LOG_FILE"
    else
        cat "$LOG_FILE"
    fi
}

# 测试模型
test() {
    check_venv || exit 1
    check_deps || exit 1

    log_info "Testing ONNX Runtime..."

    if [ ! -f "$LLAMA_ONNX_MODEL" ]; then
        log_error "Model not found: $LLAMA_ONNX_MODEL"
        return 1
    fi

    source "$VENV_PATH/bin/activate"

    python "$PROJECT_ROOT/scripts/onnx_runtime_server.py" \
        --test \
        --model "$LLAMA_ONNX_MODEL" \
        --ep "$LLAMA_ONNX_EP" \
        --threads "$LLAMA_ONNX_THREADS"
}

# 列出可用模型
list_models() {
    log_info "Available ONNX models:"
    echo ""

    if [ -d "$PROJECT_ROOT/models/qwen3-onnx" ]; then
        find "$PROJECT_ROOT/models/qwen3-onnx" -name "*.onnx" -type f | while read -r model; do
            size=$(du -h "$model" | cut -f1)
            echo "  - $model ($size)"
        done
    else
        log_warning "No models found in $PROJECT_ROOT/models/qwen3-onnx"
    fi

    echo ""
    log_info "Set model with: export LLAMA_ONNX_MODEL=/path/to/model.onnx"
}

# 显示帮助
usage() {
    cat << EOF
Usage: $0 <command> [options]

Commands:
  start     Start the ONNX Runtime server
  stop      Stop the server
  restart   Restart the server
  status    Show server status
  logs      Show server logs (tail -f)
  test      Test model loading
  list      List available models

Environment Variables:
  LLAMA_ONNX_HOST      Server host (default: 0.0.0.0)
  LLAMA_ONNX_PORT      Server port (default: 8406)
  LLAMA_ONNX_MODEL     ONNX model path
  LLAMA_ONNX_EP       Execution Provider: cpu|cuda|rocm|xdna|openvino|tensorrt
  LLAMA_ONNX_THREADS   CPU threads (default: 1)
  LLAMA_ONNX_VENV     Python virtual environment (default: py312)

Examples:
  # Start with CPU EP
  $0 start

  # Start with specific model
  LLAMA_ONNX_MODEL=/path/to/model.onnx $0 start

  # Start with XDNA EP (requires ONNX Runtime with XDNA support)
  LLAMA_ONNX_EP=xdna $0 start

  # Check status
  $0 status

  # View logs
  $0 logs

  # Test model
  $0 test

EOF
}

# 主函数
main() {
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
        test)
            test
            ;;
        list)
            list_models
            ;;
        help|--help|-h)
            usage
            ;;
        *)
            log_error "Unknown command: $1"
            echo ""
            usage
            exit 1
            ;;
    esac
}

main "$@"
