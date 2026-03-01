#!/bin/bash

set -e

_SROOT="$( cd "$(dirname "$(realpath "$0")")" ; pwd -P )"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo ""
    echo "=========================================="
    echo "$1"
    echo "=========================================="
}

log_step "步骤 1/3: 更新模型配置"

if [ -f "$_SROOT/check_invalid_models.sh" ]; then
    log_info "执行 check_invalid_models.sh"
    echo "y" | "$_SROOT/check_invalid_models.sh" 2>/dev/null || true
    echo ""
else
    log_warn "未找到 check_invalid_models.sh，跳过此步骤"
    echo ""
fi

log_step "步骤 2/3: 更新 llama.cpp"

if [ -f "$_SROOT/update_llama_cpp.sh" ]; then
    echo -e "y\ny\ny" | "$_SROOT/update_llama_cpp.sh" "$@" || {
        log_warn "llama.cpp 更新失败，继续执行后续步骤"
        echo ""
    }
fi

log_step "步骤 3/4: 杀掉旧进程"

if [ -f "$_SROOT/kill_auto_switch.sh" ]; then
    log_info "执行 kill_auto_switch.sh"
    "$_SROOT/kill_auto_switch.sh"
    echo ""
else
    log_warn "未找到 kill_auto_switch.sh，跳过此步骤"
    echo ""
fi

log_step "步骤 4/4: 重启服务"

if [ -f "$_SROOT/auto_switch.sh" ]; then
    log_info "执行 auto_switch.sh"
    nohup "$_SROOT/auto_switch.sh" > /dev/null 2>&1 &
    log_info "服务已在后台启动"
    echo ""
else
    log_warn "未找到 auto_switch.sh，跳过此步骤"
    echo ""
fi

log_step "全部完成！"
