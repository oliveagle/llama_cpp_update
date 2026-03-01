#!/bin/bash
# llama-server HIP (ROCm) 启动脚本 - AMD gfx1151
# 端口: 8402

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HIP_BIN="/home/oliveagle/opt/llama.cpp/build-hip/bin/llama-server"
PRESETS_FILE="${SCRIPT_DIR}/presets/mypresets-hip.ini"
LOG_DIR="${SCRIPT_DIR}/logs"
PID_FILE="${LOG_DIR}/hip-server.pid"
LOG_FILE="${LOG_DIR}/hip-server.log"

# ROCm 环境
export ROCM_PATH=/opt/rocm-7.12-gfx1151
export HIP_PATH=/opt/rocm-7.12-gfx1151
export PATH="${HIP_PATH}/bin:${PATH}"
export LD_LIBRARY_PATH="${HIP_PATH}/lib:${LD_LIBRARY_PATH}"

# 创建日志目录
mkdir -p "${LOG_DIR}"

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "HIP 服务已在运行 (PID: $(cat $PID_FILE))"
        return 0
    fi

    echo "启动 llama-server HIP (端口 8402)..."
    nohup "${HIP_BIN}" \
        --models-max 1 \
        --models-preset "${PRESETS_FILE}" \
        --host 0.0.0.0 \
        --port 8402 \
        --no-warmup \
        -fa on \
        --jinja \
        --reasoning-format auto \
        --fit off \
        > "${LOG_FILE}" 2>&1 &

    echo $! > "$PID_FILE"
    echo "服务已启动，PID: $(cat $PID_FILE)"
    echo "日志: ${LOG_FILE}"
    sleep 2
    tail -20 "${LOG_FILE}"
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "停止 HIP 服务 (PID: $PID)..."
            kill -TERM "$PID"
            rm -f "$PID_FILE"
            echo "服务已停止"
        else
            echo "服务未运行"
            rm -f "$PID_FILE"
        fi
    else
        echo "PID 文件不存在"
    fi
}

status() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "HIP 服务运行中 (PID: $PID)"
            echo "端口: 8402"
            tail -5 "${LOG_FILE}"
        else
            echo "服务未运行 (PID 文件存在但进程不存在)"
        fi
    else
        echo "服务未运行"
    fi
}

logs() {
    if [ -f "${LOG_FILE}" ]; then
        tail -f "${LOG_FILE}"
    else
        echo "日志文件不存在"
    fi
}

case "${1:-start}" in
    start) start ;;
    stop) stop ;;
    restart) stop; sleep 2; start ;;
    status) status ;;
    logs) logs ;;
    *) echo "Usage: $0 {start|stop|restart|status|logs}"
       exit 1 ;;
esac
