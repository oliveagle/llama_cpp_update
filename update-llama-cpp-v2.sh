#!/bin/bash
#
# llama.cpp 统一更新脚本 v2
# 支持 Vulkan、ROCm 和 CUDA 版本更新
#
# 用法:
#   ./update-llama-cpp-v2.sh all           # 更新所有版本
#   ./update-llama-cpp-v2.sh vulkan        # 更新 Vulkan 版本
#   ./update-llama-cpp-v2.sh rocm          # 更新 ROCm 版本
#   ./update-llama-cpp-v2.sh cuda          # 更新 CUDA 版本
#   ./update-llama-cpp-v2.sh list          # 列出可用版本

set -e

# 配置
ROOT_DIR="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"
DOWNLOADS_DIR="$ROOT_DIR/downloads"
REPO_URL="https://github.com/ggml-org/llama.cpp"
RELEASES_API="https://api.github.com/repos/ggml-org/llama.cpp/releases"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

log_blue() {
    echo -e "${BLUE}[*]${NC} $1"
}

log_cyan() {
    echo -e "${CYAN}[+]${NC} $1"
}

# 获取最新版本号
get_latest_version() {
    curl -s "$RELEASES_API" | grep -o '"tag_name": "b[0-9]*"' | head -1 | grep -o 'b[0-9]*' | sed 's/b//'
}

# 列出可用版本
list_versions() {
    log_info "获取可用版本..."

    # 获取最近的 release
    local releases=$(curl -s "$RELEASES_API" | grep -o '"tag_name": "b[0-9]*"' | head -30 | grep -o 'b[0-9]*' | sed 's/b//')

    if [ -z "$releases" ]; then
        log_error "无法获取版本列表"
        exit 1
    fi

    echo ""
    echo "=========================================="
    echo "llama.cpp 可用版本"
    echo "=========================================="
    echo ""

    local count=0
    for version in $releases; do
        count=$((count + 1))
        local version_tag="b$version"

        # 检查预编译包
        local vulkan_exists="  "
        local rocm_exists="   "

        if check_asset_exists "$version_tag" "ubuntu-vulkan-x64"; then
            vulkan_exists="${GREEN}✓${NC} "
        fi

        if check_asset_exists "$version_tag" "ubuntu-rocm-7.2-x64"; then
            rocm_exists="${GREEN}✓${NC}  "
        fi

        # CUDA 总是可以通过源码编译
        printf "  %2d. b%-5s  Vulkan: [%s]  ROCm: [%s]  CUDA: [✓]\n" \
            "$count" "$version" "$vulkan_exists" "$rocm_exists"
    done

    echo "=========================================="
    echo ""
    echo "使用方法:"
    echo "  ./update-llama-cpp-v2.sh all           # 更新所有版本"
    echo "  ./update-llama-cpp-v2.sh vulkan        # 更新 Vulkan"
    echo "  ./update-llama-cpp-v2.sh rocm          # 更新 ROCm"
    echo "  ./update-llama-cpp-v2.sh cuda          # 更新 CUDA"
    echo ""
}

# 检查 asset 是否存在
check_asset_exists() {
    local version_tag=$1
    local filename=$2
    local url="${REPO_URL}/releases/download/${version_tag}/llama-${version_tag}-bin-${filename}.tar.gz"

    local http_code=$(curl -sI -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")
    [ "$http_code" = "200" ] || [ "$http_code" = "302" ]
}

# 下载版本
download_version() {
    local version=$1
    local backend=$2

    local version_tag="b$version"

    case "$backend" in
        vulkan)
            local filename_pattern="ubuntu-vulkan-x64"
            local service_name="llama-server-8400.service"
            ;;
        rocm)
            local filename_pattern="ubuntu-rocm-7.2-x64"
            local service_name="llama-server-8405.service"
            ;;
        cuda)
            log_warn "CUDA 版本需要源码编译，请使用 compile_cuda"
            return 1
            ;;
        *)
            log_error "未知后端: $backend"
            return 1
            ;;
    esac

    local filename="llama-${version_tag}-bin-${filename_pattern}.tar.gz"
    local download_url="${REPO_URL}/releases/download/${version_tag}/${filename}"
    local target_dir="$DOWNLOADS_DIR/llama-$version_tag"

    log_blue "========== $backend 版本更新 =========="
    log_info "版本: $version_tag"
    log_info "后端: $filename_pattern"

    # 检查是否已是最新版本
    local current_link="$ROOT_DIR/current"
    if [ -L "$current_link" ]; then
        local current_target=$(readlink "$current_link")
        local current_version=$(basename "$current_target" | grep -o 'b[0-9]*' | sed 's/b//' || echo "unknown")

        if [ "$current_version" = "$version" ]; then
            log_info "已是当前版本 (b$version)，无需更新"
            return 0
        fi
    fi

    # 下载
    if [ -f "$DOWNLOADS_DIR/$filename" ]; then
        log_warn "文件已存在: $filename"
        log_info "使用现有文件"
    else
        log_info "下载: $filename"
        log_info "URL: $download_url"

        if curl -L --progress-bar -o "$DOWNLOADS_DIR/$filename" "$download_url"; then
            log_info "下载完成"
        else
            log_error "下载失败"
            return 1
        fi
    fi

    # 解压
    log_info "解压到: $target_dir"

    if [ -d "$target_dir" ]; then
        rm -rf "$target_dir"
    fi

    mkdir -p "$target_dir"

    if tar -xzf "$DOWNLOADS_DIR/$filename" -C "$target_dir" --strip-components=1; then
        log_info "解压完成"
    else
        log_error "解压失败"
        return 1
    fi

    # 更新符号链接
    log_info "更新符号链接: $current_link -> $target_dir"

    if [ -L "$current_link" ]; then
        rm "$current_link"
    elif [ -e "$current_link" ]; then
        rm -rf "$current_link"
    fi

    ln -s "$target_dir" "$current_link"

    # 重启服务
    if systemctl is-active --quiet "$service_name" 2>/dev/null; then
        log_info "重启服务: $service_name"
        sudo systemctl restart "$service_name"
        sleep 1
        local status=$(systemctl is-active "$service_name" 2>/dev/null || echo "unknown")
        log_info "服务状态: $status"
    else
        log_warn "服务 $service_name 未运行"
    fi

    log_blue "========== $backend 更新完成 =========="
    log_info "版本: $version_tag"
    log_info "路径: $target_dir"

    # 清理旧版本
    cleanup_old_versions "$backend"

    return 0
}

# 编译 CUDA 版本
compile_cuda() {
    local version=${1:-$(get_latest_version)}
    local version_tag="b$version"
    local install_dir="/home/oliveagle/opt/llama.cpp"
    local service_name="llama-server-8401.service"

    log_blue "========== CUDA 版本编译 =========="
    log_info "版本: $version_tag"
    log_info "安装路径: $install_dir"

    # 获取当前版本
    local current_version="unknown"
    if [ -f "$install_dir/build/bin/llama-server" ]; then
        current_version=$($install_dir/build/bin/llama-server --version 2>&1 | grep -o 'version: [0-9]*' | head -1 | awk '{print $2}' || echo "unknown")
    fi
    log_info "当前版本: ${current_version:-unknown}"

    if [ "$current_version" = "$version" ]; then
        log_info "已是当前版本 (b$version)，无需更新"
        return 0
    fi

    # 确认编译
    read -p "开始编译 b$version? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_info "取消编译"
        return 0
    fi

    local build_dir="/tmp/llama-cpp-cuda-build-$$"

    # 克隆代码
    log_info "克隆 llama.cpp 源码..."
    if [ -d "$build_dir" ]; then
        rm -rf "$build_dir"
    fi
    mkdir -p "$build_dir"

    git clone --depth 1 --branch "$version_tag" "$REPO_URL" "$build_dir" 2>&1 | tail -3

    if [ ! -f "$build_dir/CMakeLists.txt" ]; then
        log_error "源码克隆失败"
        return 1
    fi

    cd "$build_dir"

    # 配置编译
    log_info "配置编译选项 (CUDA sm_70 for V100)..."
    cmake -B build \
        -DGGML_CUDA=ON \
        -DCMAKE_CUDA_ARCHITECTURES=70 \
        -DLLAMA_CUDA_F16=ON \
        -DCMAKE_BUILD_TYPE=Release 2>&1 | tail -10

    # 编译
    log_info "开始编译（可能需要几分钟）..."
    local jobs=$(nproc)
    log_info "使用 $jobs 线程并行编译"

    if cmake --build build --config Release -j$jobs 2>&1 | tail -20; then
        log_info "编译成功"
    else
        log_error "编译失败"
        cd "$OLDPWD"
        rm -rf "$build_dir"
        return 1
    fi

    # 安装
    log_info "安装到: $install_dir"
    mkdir -p "$install_dir"

    # 复制二进制文件
    cp -v build/bin/llama-server "$install_dir/" 2>&1 | tail -1
    cp -v build/bin/llama-cli "$install_dir/" 2>/dev/null || true

    # 复制库文件
    if [ -d "build/ggml/src" ]; then
        find build -name "libggml*.so*" -exec cp -v {} "$install_dir/" \; 2>&1 | tail -5
        find build -name "libllama*.so*" -exec cp -v {} "$install_dir/" \; 2>&1 | tail -2
    fi

    # 清理
    cd "$OLDPWD"
    rm -rf "$build_dir"

    # 重启服务
    if systemctl is-active --quiet "$service_name" 2>/dev/null; then
        log_info "重启服务: $service_name"
        sudo systemctl restart "$service_name"
        sleep 1
        local status=$(systemctl is-active "$service_name" 2>/dev/null || echo "unknown")
        log_info "服务状态: $status"
    else
        log_warn "服务 $service_name 未运行"
    fi

    log_blue "========== CUDA 更新完成 =========="
    log_info "版本: $version_tag"
    log_info "路径: $install_dir/build/bin/"

    return 0
}

# 清理旧版本
cleanup_old_versions() {
    local backend=$1
    local prefix=$2
    local keep_count=5

    log_info "清理旧版本（保留最近 $keep_count 个）..."

    local versions=()
    for dir in "$DOWNLOADS_DIR"/llama-b[0-9]*; do
        if [ -d "$dir" ] && [ ! -L "$dir" ]; then
            local version=$(basename "$dir" | sed 's/llama-b//')
            if [[ "$version" =~ ^[0-9]+$ ]]; then
                versions+=("$version")
            fi
        fi
    done 2>/dev/null || true

    if [ ${#versions[@]} -le $keep_count ]; then
        log_info "版本数量 (${#versions[@]}) 未超过保留数量，无需清理"
        return 0
    fi

    # 排序并删除旧版本
    IFS=$'\n' sorted_versions=($(sort -rn <<<"${versions[*]}"))
    unset IFS

    for i in "${!sorted_versions[@]}"; do
        local version="${sorted_versions[$i]}"
        if [ $i -lt $keep_count ]; then
            log_info "  保留: llama-b$version"
        else
            log_warn "  删除: llama-b$version"
            rm -rf "$DOWNLOADS_DIR/llama-b$version"
        fi
    done
}

# 显示状态
show_status() {
    echo ""
    echo "=========================================="
    echo "llama.cpp 版本状态"
    echo "=========================================="
    echo ""

    # 最新版本
    local latest=$(get_latest_version)
    log_info "GitHub 最新版本: b$latest"
    echo ""

    # Vulkan 状态
    echo -e "${BLUE}[Vulkan]${NC}"
    local vulkan_current="none"
    if [ -L "$ROOT_DIR/current" ]; then
        local target=$(readlink "$ROOT_DIR/current")
        vulkan_current=$(basename "$target" | grep -o 'b[0-9]*' | sed 's/b//' || echo "unknown")
    fi
    local vulkan_service=$(systemctl is-active llama-server-8400.service 2>/dev/null || echo "unknown")

    echo "  当前版本: ${vulkan_current:-none}"
    echo "  服务状态: $vulkan_service"
    echo "  符号链接: $ROOT_DIR/current"
    echo "  API 地址: http://localhost:8400"
    echo ""

    # ROCm 状态
    echo -e "${BLUE}[ROCm]${NC}"
    local rocm_current="none"
    local rocm_link="$DOWNLOADS_DIR/current-rocm"
    if [ -L "$rocm_link" ]; then
        local target=$(readlink "$rocm_link")
        rocm_current=$(basename "$target" | grep -o 'b[0-9]*' | sed 's/b//' || echo "unknown")
    fi
    local rocm_service=$(systemctl is-active llama-server-8405.service 2>/dev/null || echo "unknown")

    echo "  当前版本: ${rocm_current:-none}"
    echo "  服务状态: $rocm_service"
    echo "  符号链接: $rocm_link"
    echo "  API 地址: http://localhost:8405"
    echo ""

    # CUDA 状态
    echo -e "${BLUE}[CUDA]${NC}"
    local cuda_current="none"
    if [ -f "/home/oliveagle/opt/llama.cpp/build/bin/llama-server" ]; then
        cuda_current=$(/home/oliveagle/opt/llama.cpp/build/bin/llama-server --version 2>&1 | grep -o 'version: [0-9]*' | head -1 | awk '{print $2}' || echo "unknown")
    fi
    local cuda_service=$(systemctl is-active llama-server-8401.service 2>/dev/null || echo "unknown")

    echo "  当前版本: ${cuda_current:-none}"
    echo "  服务状态: $cuda_service"
    echo "  安装路径: /home/oliveagle/opt/llama.cpp/build/bin/"
    echo "  API 地址: http://localhost:8401"
    echo ""

    # 已安装版本
    echo -e "${BLUE}[已安装版本]${NC}"
    echo "  Vulkan/ROCm 版本:"
    for dir in "$DOWNLOADS_DIR"/llama-b[0-9]*; do
        if [ -d "$dir" ] && [ ! -L "$dir" ]; then
            local v=$(basename "$dir" | sed 's/llama-b//')
            echo "    - b$v"
        fi
    done 2>/dev/null || echo "    (无)"

    echo ""
    echo "=========================================="
    echo ""
    echo "使用方法:"
    echo "  ./update-llama-cpp-v2.sh all           # 更新所有版本"
    echo "  ./update-llama-cpp-v2.sh vulkan        # 更新 Vulkan"
    echo "  ./update-llama-cpp-v2.sh rocm          # 更新 ROCm"
    echo "  ./update-llama-cpp-v2.sh cuda          # 更新 CUDA"
    echo "  ./update-llama-cpp-v2.sh status        # 查看状态"
    echo "  ./update-llama-cpp-v2.sh list          # 列出可用版本"
    echo ""
}

# 主函数
main() {
    local cmd=${1:-}

    case "$cmd" in
        vulkan)
            download_version "$(get_latest_version)" "vulkan"
            ;;
        rocm)
            download_version "$(get_latest_version)" "rocm"
            ;;
        cuda)
            compile_cuda "$(get_latest_version)"
            ;;
        all)
            log_cyan "开始更新所有版本..."
            echo ""
            download_version "$(get_latest_version)" "vulkan" || true
            echo ""
            download_version "$(get_latest_version)" "rocm" || true
            echo ""
            compile_cuda "$(get_latest_version)" || true
            echo ""
            log_cyan "所有版本更新完成！"
            show_status
            ;;
        list)
            list_versions
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            echo "llama.cpp 统一更新脚本 v2"
            echo ""
            echo "用法:"
            echo "  $0 all           # 更新所有版本"
            echo "  $0 vulkan        # 更新 Vulkan 版本"
            echo "  $0 rocm          # 更新 ROCm 版本"
            echo "  $0 cuda          # 更新 CUDA 版本"
            echo "  $0 status        # 查看当前版本状态"
            echo "  $0 list          # 列出可用版本"
            echo ""
            ;;
        "")
            show_status
            ;;
        *)
            log_error "未知命令: $cmd"
            echo ""
            echo "使用方法:"
            echo "  $0 all           # 更新所有版本"
            echo "  $0 vulkan        # 更新 Vulkan 版本"
            echo "  $0 rocm          # 更新 ROCm 版本"
            echo "  $0 cuda          # 更新 CUDA 版本"
            echo "  $0 status        # 查看当前版本状态"
            echo "  $0 list          # 列出可用版本"
            exit 1
            ;;
    esac
}

main "$@"
