#!/bin/bash
# llama-server HIP (ROCm) 优化启动脚本 - AMD gfx1151
# 端口: 8402
# 版本: 优化版 (启用 HIP Graphs, 环境变量调优)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HIP_BIN="/home/oliveagle/opt/llama.cpp/build-hip/bin/llama-server"
PRESETS_FILE="${SCRIPT_DIR}/presets/mypresets-hip.ini"
LOG_DIR="${SCRIPT_DIR}/logs"
PID_FILE="${LOG_DIR}/hip-server.pid"
LOG_FILE="${LOG_DIR}/hip-server.log"

# ========== ROCm 环境 ==========
export ROCM_PATH=/opt/rocm-7.12-gfx1151
export HIP_PATH=/opt/rocm-7.12-gfx1151
export PATH="${HIP_PATH}/bin:${PATH}"
export LD_LIBRARY_PATH="${HIP_PATH}/lib:${LD_LIBRARY_PATH}"

# ========== gfx1151 优化 ==========
# 统一内存优化 (APU 关键)
export HSA_XNACK=1
export HSA_FORCE_FINE_GRAIN_PCIE=1

# 内存分配
export GPU_MAX_HEAP_SIZE=100
export GPU_MAX_ALLOC_PERCENT=100

# HSA 队列优化
export GPU_MAX_HW_QUEUES=4
export LIBOMPTARGET_AMDGPU_NUM_HSA_QUEUES=4

# ROCm 库优化
export ROCBLAS_USE_HIPBLASLT=1

# gfx1151 架构确认
export HSA_OVERRIDE_GFX_VERSION=11.5.1

# ========== 创建日志目录 ==========
mkdir -p "${LOG_DIR}"

start() {
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "HIP 服务已在运行 (PID: $(cat $PID_FILE))"
        return 0
    fi

    echo "启动 llama-server HIP 优化版 (端口 8402)..."
    echo "优化项:"
    echo "  - HIP Graphs 启用"
    echo "  - 统一内存优化 (HSA_XNACK=1)"
    echo "  - gfx1151 架构优化"
    echo "  - --fit off (避免内存适配卡住)"
    echo ""

    # 记录环境变量
    echo "=== 环境变量 ===" > "${LOG_FILE}"
    echo "HSA_XNACK=$HSA_XNACK" >> "${LOG_FILE}"
    echo "HSA_OVERRIDE_GFX_VERSION=$HSA_OVERRIDE_GFX_VERSION" >> "${LOG_FILE}"
    echo "GPU_MAX_HW_QUEUES=$GPU_MAX_HW_QUEUES" >> "${LOG_FILE}"
    echo "" >> "${LOG_FILE}"

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
        -ngl 999 \
        >> "${LOG_FILE}" 2>&1 &

    echo $! > "$PID_FILE"
    echo "服务已启动，PID: $(cat $PID_FILE)"
    echo "日志: ${LOG_FILE}"
    sleep 2
    tail -30 "${LOG_FILE}"
}

stop() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo "停止 HIP 服务 (PID: $PID)..."
            kill -TERM "$PID"
            # 同时停止所有子进程
            pkill -f "llama-server.*alias.*hip"
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
            echo ""
            echo "最近日志:"
            tail -10 "${LOG_FILE}"
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
