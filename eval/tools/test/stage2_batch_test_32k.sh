#!/bin/bash
# 批量第二层能力测试 - 所有模型 (32K Context)
# 使用单模型模式逐个测试

set -e

SROOT="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"
SERVER_BIN="/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
RESULTS_DIR="$SROOT/eval_results/stage2_32k"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$RESULTS_DIR"

# 模型配置列表
# 格式: "显示名称|模型文件路径|chat-template|rope配置(可选)"
MODELS=(
    "Qwen3-0.6B|/mnt/volume3/modelscope_models/unsloth/Qwen3-0.6B-GGUF/Qwen3-0.6B-Q4_0.gguf|qwen2|--rope-scaling yarn --rope-scale 2.0 --yarn-orig-ctx 32768"
    "Qwen3-4B|/mnt/volume3/modelscope_models/unsloth/Qwen3-4B-Instruct-2507-GGUF/Qwen3-4B-Instruct-2507-UD-Q4_K_XL.gguf|qwen2|--rope-scaling yarn --rope-scale 2.0 --yarn-orig-ctx 32768"
    "MiniCPM-o-4.5|/mnt/volume3/modelscope_models/OpenBMB/MiniCPM-o-4_5-gguf/MiniCPM-o-4_5-Q4_K_M.gguf|qwen2|--rope-scaling yarn --rope-scale 1.6 --yarn-orig-ctx 40960"
    "JoyAI-LLM-Flash|/mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf|chatglm3|"
    "GLM-4.7-Flash-REAP|/mnt/volume3/modelscope_models/unsloth/GLM-4___7-Flash-REAP-23B-A3B-GGUF/GLM-4.7-Flash-REAP-23B-A3B-IQ4_NL.gguf|chatglm3|"
)

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 启动单模型服务器
start_model_server() {
    local model_path="$1"
    local chat_template="$2"
    local extra_params="$3"
    local log_file="$4"

    log_info "启动服务器: $model_path"

    CUDA_VISIBLE_DEVICES=0 \
    PATH=/usr/local/cuda-12.5/bin:$PATH \
    LD_LIBRARY_PATH=/usr/local/cuda-12.5/lib64:$LD_LIBRARY_PATH \
    nohup "$SERVER_BIN" \
        -m "$model_path" \
        --host 0.0.0.0 \
        --port 8401 \
        -c 32768 \
        -n 4096 \
        -ngl 99 \
        --chat-template "$chat_template" \
        $extra_params \
        -np 1 \
        >> "$log_file" 2>&1 &

    echo $!
}

# 等待服务器就绪
wait_for_server() {
    local max_wait=60
    local waited=0

    while [ $waited -lt $max_wait ]; do
        if curl -s http://localhost:8401/health > /dev/null 2>&1 || \
           curl -s http://localhost:8401/v1/models > /dev/null 2>&1; then
            return 0
        fi
        sleep 1
        ((waited++))
    done
    return 1
}

# 测试单个模型
test_model() {
    local model_display="$1"
    local model_path="$2"
    local chat_template="$3"
    local extra_params="$4"

    log_info "=========================================="
    log_info "测试模型: $model_display"
    log_info "模型路径: $model_path"
    log_info "=========================================="

    local log_file="$RESULTS_DIR/${model_display}_${TIMESTAMP}.log"
    local result_file="$RESULTS_DIR/${model_display}_${TIMESTAMP}.json"

    # 启动服务器
    local pid=$(start_model_server "$model_path" "$chat_template" "$extra_params" "$log_file")
    log_info "服务器 PID: $pid"

    # 等待服务器就绪
    log_info "等待服务器就绪..."
    if ! wait_for_server; then
        log_error "服务器启动超时"
        kill $pid 2>/dev/null || true
        return 1
    fi
    log_info "服务器就绪"

    # 运行第二层测试
    log_info "开始第二层能力测试..."
    python3 "$SROOT/stage2_single_model_test.py" \
        --model-name "$model_display" \
        --output "$result_file" \
        2>&1 | tee "$RESULTS_DIR/${model_display}_${TIMESTAMP}_test.log"

    # 停止服务器
    log_info "停止服务器..."
    kill $pid 2>/dev/null || true
    sleep 2

    log_info "模型 $model_display 测试完成"
    echo ""
}

# 主流程
main() {
    log_info "=========================================="
    log_info "V100 CUDA 第二层能力测试 (32K Context)"
    log_info "开始时间: $(date)"
    log_info "=========================================="

    for model_config in "${MODELS[@]}"; do
        IFS='|' read -r model_display model_path chat_template extra_params <<< "$model_config"
        test_model "$model_display" "$model_path" "$chat_template" "$extra_params"
    done

    log_info "=========================================="
    log_info "所有模型测试完成"
    log_info "结果目录: $RESULTS_DIR"
    log_info "结束时间: $(date)"
    log_info "=========================================="
}

main "$@"
