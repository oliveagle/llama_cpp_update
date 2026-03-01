#!/bin/bash
#
# llama.cpp 统一更新脚本
# 支持 Vulkan 和 CUDA 版本自动更新
#
# 用法:
#   ./update-llama-cpp.sh vulkan           # 更新 Vulkan 版本
#   ./update-llama-cpp.sh cuda             # 更新 CUDA 版本
#   ./update-llama-cpp.sh vulkan list      # 列出 Vulkan 可用版本
#   ./update-llama-cpp.sh cuda list        # 列出 CUDA 可用版本
#   ./update-llama-cpp.sh vulkan 8069      # 更新到指定版本
#   ./update-llama-cpp.sh status           # 查看当前版本状态

set -e

_SROOT="$(cd "$(dirname "$(realpath "$0")")" && pwd -P)"

# 配置
REPO_URL="https://github.com/ggml-org/llama.cpp"
RELEASES_URL="https://api.github.com/repos/ggml-org/llama.cpp/releases"
PROXY="http://127.0.0.1:1080"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

log_blue() {
    echo -e "${BLUE}[*]${NC} $1" >&2
}

# 获取最新版本号
get_latest_version() {
    curl -x "$PROXY" -s "$RELEASES_URL/latest" | grep -o '"tag_name": "b[0-9]*"' | head -1 | grep -o 'b[0-9]*' | sed 's/b//'
}

# 列出可用版本
list_versions() {
    local backend=$1
    local filename_pattern=$2

    log_info "获取 $backend 可用版本..."

    # CUDA (Linux) 特殊处理：没有预编译包
    if [ "$backend" = "CUDA" ]; then
        echo ""
        echo "=========================================="
        echo "llama.cpp CUDA 版本"
        echo "=========================================="
        echo ""
        echo -e "${YELLOW}注意：Linux 下没有 CUDA 预编译包${NC}"
        echo "CUDA 版本需要从源码编译"
        echo ""
        echo "使用方法:"
        echo "  ./update-llama-cpp.sh cuda           # 编译最新版本"
        echo "  ./update-llama-cpp.sh cuda 8069      # 编译指定版本"
        echo ""
        echo "编译过程会自动:"
        echo "  1. 克隆指定版本的源码"
        echo "  2. 使用 CMake 配置 CUDA (sm_70 for V100)"
        echo "  3. 并行编译"
        echo "  4. 安装到 /home/oliveagle/opt/llama.cpp/"
        echo "  5. 重启 llama-server-8401.service"
        echo ""
        return 0
    fi

    # 获取最近 30 个 release
    local releases=$(curl -x "$PROXY" -s "$RELEASES_URL" | grep -o '"tag_name": "b[0-9]*"' | head -30 | grep -o 'b[0-9]*' | sed 's/b//')

    if [ -z "$releases" ]; then
        log_error "无法获取版本列表"
        exit 1
    fi

    echo ""
    echo "=========================================="
    echo "llama.cpp $backend 可用版本（预编译）"
    echo "=========================================="

    local count=0
    local available_count=0

    for version in $releases; do
        count=$((count + 1))
        local version_tag="b$version"
        local filename="llama-${version_tag}-bin-${filename_pattern}.tar.gz"
        local download_url="${REPO_URL}/releases/download/${version_tag}/${filename}"

        # 检查预编译包是否存在
        local http_code=$(curl -x "$PROXY" -sI -o /dev/null -w "%{http_code}" "$download_url" 2>/dev/null || echo "000")

        if [ "$http_code" = "200" ]; then
            available_count=$((available_count + 1))
            if [ $available_count -le 15 ]; then
                printf "  %2d. b%s ${GREEN}✓${NC}\n" "$available_count" "$version"
            fi
        fi
    done

    echo "=========================================="
    echo ""
    echo "共找到 $available_count 个带 $backend 预编译包的版本"
    echo ""
    echo "使用方法:"
    echo "  ./update-llama-cpp.sh $backend        # 更新到最新"
    echo "  ./update-llama-cpp.sh $backend <版本> # 更新到指定版本"
    echo ""
}

# 检查预编译包是否存在
check_build_exists() {
    local version=$1
    local filename_pattern=$2
    local version_tag="b$version"
    local filename="llama-${version_tag}-bin-${filename_pattern}.tar.gz"
    local download_url="${REPO_URL}/releases/download/${version_tag}/${filename}"

    # 跟随重定向并获取最终 HTTP 状态码
    local http_code=$(curl -x "$PROXY" -sL -I -o /dev/null -w "%{http_code}" "$download_url" 2>/dev/null || echo "000")
    # 接受 200 或 302（GitHub 重定向）
    [ "$http_code" = "200" ] || [ "$http_code" = "302" ]
}

# 下载版本
download_version() {
    local version=$1
    local filename_pattern=$2
    local downloads_dir=$3
    local version_tag="b$version"
    local filename="llama-${version_tag}-bin-${filename_pattern}.tar.gz"
    local download_url="${REPO_URL}/releases/download/${version_tag}/${filename}"

    log_info "准备下载 $version_tag (${filename_pattern})"

    # 检查文件是否已存在
    if [ -f "$downloads_dir/$filename" ]; then
        log_warn "文件已存在: $filename"
        read -p "是否重新下载? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "使用现有文件"
            return 0
        fi
    fi

    log_info "下载地址: $download_url"
    log_info "开始下载..."

    if curl -x "$PROXY" -L --progress-bar -o "$downloads_dir/$filename" "$download_url"; then
        log_info "下载完成: $filename"
        return 0
    else
        log_error "下载失败"
        return 1
    fi
}

# 解压版本
extract_version() {
    local version=$1
    local filename_pattern=$2
    local downloads_dir=$3
    local target_dir=$4

    local version_tag="b$version"
    local filename="llama-${version_tag}-bin-${filename_pattern}.tar.gz"

    log_info "解压到: $target_dir"

    # 如果目录已存在，先删除
    if [ -d "$target_dir" ]; then
        rm -rf "$target_dir"
    fi

    mkdir -p "$target_dir"

    if tar -xzf "$downloads_dir/$filename" -C "$target_dir" --strip-components=1; then
        log_info "解压完成"
        return 0
    else
        log_error "解压失败"
        return 1
    fi
}

# 更新符号链接
update_symlink() {
    local target_dir=$1
    local link_path=$2

    log_info "更新符号链接: $link_path -> $target_dir"

    if [ -L "$link_path" ]; then
        rm "$link_path"
    elif [ -e "$link_path" ]; then
        rm -rf "$link_path"
    fi

    ln -s "$target_dir" "$link_path"
}

# 清理旧版本
cleanup_old_versions() {
    local downloads_dir=$1
    local prefix=$2
    local keep_count=${3:-3}

    log_info "清理旧版本（保留最近 $keep_count 个）..."

    local versions=()
    for dir in "$downloads_dir"/${prefix}-b*; do
        if [ -d "$dir" ] && [ ! -L "$dir" ]; then
            local version=$(basename "$dir" | sed "s/${prefix}-b//")
            if [[ "$version" =~ ^[0-9]+$ ]]; then
                versions+=("$version")
            fi
        fi
    done

    if [ ${#versions[@]} -le $keep_count ]; then
        log_info "版本数量 (${#versions[@]}) 未超过保留数量 ($keep_count)，无需清理"
        return 0
    fi

    # 排序并删除旧版本
    IFS=$'\n' sorted_versions=($(sort -rn <<<"${versions[*]}"))
    unset IFS

    for i in "${!sorted_versions[@]}"; do
        local version="${sorted_versions[$i]}"
        if [ $i -lt $keep_count ]; then
            log_info "  保留: ${prefix}-b$version"
        else
            log_warn "  删除: ${prefix}-b$version"
            rm -rf "$downloads_dir/${prefix}-b$version"
            # 同时删除 tar.gz 文件
            local filename_pattern
            if [[ "$prefix" == *"cuda"* ]]; then
                filename_pattern="ubuntu-x64-cuda-cu12.4"
            else
                filename_pattern="ubuntu-vulkan-x64"
            fi
            rm -f "$downloads_dir/llama-b${version}-bin-${filename_pattern}.tar.gz"
        fi
    done
}

# 重启 systemd 服务
restart_service() {
    local service_name=$1

    log_info "重启 systemd 服务: $service_name"

    if systemctl is-active --quiet "$service_name" 2>/dev/null; then
        sudo systemctl restart "$service_name"
        log_info "服务已重启"
    else
        log_warn "服务 $service_name 未运行，尝试启动..."
        sudo systemctl start "$service_name" || log_warn "服务启动失败，请手动检查"
    fi

    # 显示服务状态
    sleep 1
    sudo systemctl status "$service_name" --no-pager 2>/dev/null | head -3
}

# 获取当前安装的版本
get_installed_version() {
    local link_path=$1
    if [ -L "$link_path" ]; then
        local target=$(readlink -f "$link_path")
        basename "$target" | grep -o 'b[0-9]*$' | sed 's/b//' || echo "unknown"
    else
        echo "none"
    fi
}

# 更新 Vulkan 版本
update_vulkan() {
    local target_version=$1

    local downloads_dir="$_SROOT/downloads"
    local link_path="$_SROOT/current"
    local filename_pattern="ubuntu-vulkan-x64"
    local service_name="llama-server-8400.service"

    log_blue "========== Vulkan 版本更新 =========="

    local current_version=$(get_installed_version "$link_path")
    log_info "当前版本: ${current_version:-none}"

    # 确定目标版本
    if [ -z "$target_version" ]; then
        log_info "检查最新版本..."
        local latest_version=$(get_latest_version)

        # 查找带 Vulkan 预编译包的最新版本
        local found_version=""
        local releases=$(curl -x "$PROXY" -s "$RELEASES_URL" | grep -o '"tag_name": "b[0-9]*"' | head -20 | grep -o 'b[0-9]*' | sed 's/b//')

        for v in $releases; do
            if check_build_exists "$v" "$filename_pattern"; then
                found_version="$v"
                break
            fi
        done

        if [ -z "$found_version" ]; then
            log_error "未找到带 Vulkan 预编译包的版本"
            exit 1
        fi

        target_version="$found_version"
        log_info "最新可用版本: b$target_version"
    fi

    # 检查是否已是最新版本
    if [ "$current_version" = "$target_version" ]; then
        log_info "已经是最新版本 (b$target_version)，无需更新"
        return 0
    fi

    # 下载并安装
    local version_tag="b$target_version"
    local target_dir="$downloads_dir/llama-$version_tag"

    download_version "$target_version" "$filename_pattern" "$downloads_dir" || exit 1
    extract_version "$target_version" "$filename_pattern" "$downloads_dir" "$target_dir" || exit 1
    update_symlink "$target_dir" "$link_path"

    # 清理旧版本
    cleanup_old_versions "$downloads_dir" "llama" 5

    # 重启服务
    restart_service "$service_name"

    log_blue "========== Vulkan 更新完成 =========="
    log_info "版本: b$target_version"
    log_info "路径: $target_dir"
    log_info "链接: $link_path"
}

# 编译 CUDA 版本
compile_cuda() {
    local version=$1
    local install_dir=$2
    local version_tag="b$version"

    log_blue "========== CUDA 版本编译 =========="
    log_info "版本: $version_tag"
    log_info "安装路径: $install_dir"

    local build_dir="/tmp/llama-cpp-cuda-build-$$"

    # 克隆代码
    log_info "克隆 llama.cpp 源码..."
    if [ -d "$build_dir" ]; then
        rm -rf "$build_dir"
    fi
    mkdir -p "$build_dir"

    git clone --depth 1 --branch "$version_tag" https://github.com/ggml-org/llama.cpp.git "$build_dir" 2>&1 | tail -3

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

    log_info "CUDA 版本编译完成"
    return 0
}

# 更新 CUDA 版本（源码编译）
update_cuda() {
    local target_version=$1
    local service_name="llama-server-8401.service"

    log_blue "========== CUDA 版本更新 =========="
    log_warn "Linux 下无 CUDA 预编译包，将从源码编译"

    # 获取当前版本
    local current_version="unknown"
    if [ -f "/home/oliveagle/opt/llama.cpp/build/bin/llama-server" ]; then
        current_version=$(/home/oliveagle/opt/llama.cpp/build/bin/llama-server --version 2>&1 | grep -o 'version: [0-9]*' | head -1 | awk '{print $2}' || echo "unknown")
    fi
    log_info "当前版本: ${current_version:-unknown}"

    # 确定目标版本
    if [ -z "$target_version" ]; then
        log_info "检查最新版本..."
        target_version=$(get_latest_version)
        log_info "最新版本: b$target_version"
    fi

    if [ "$current_version" = "$target_version" ]; then
        log_info "已经是最新版本 (b$target_version)，无需更新"
        return 0
    fi

    log_info "准备编译: b$target_version"
    read -p "开始编译? (Y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
        log_info "取消编译"
        return 0
    fi

    # 编译
    local install_dir="/home/oliveagle/opt/llama.cpp"
    if compile_cuda "$target_version" "$install_dir"; then
        log_info "编译完成"

        # 重启服务
        restart_service "$service_name"

        log_blue "========== CUDA 更新完成 =========="
        log_info "版本: b$target_version"
        log_info "路径: $install_dir/build/bin/"
    else
        log_error "更新失败"
        return 1
    fi
}

# 显示状态
show_status() {
    echo ""
    echo "=========================================="
    echo "llama.cpp 版本状态"
    echo "=========================================="
    echo ""

    # Vulkan 状态
    echo -e "${BLUE}[Vulkan]${NC}"
    local vulkan_current=$(get_installed_version "$_SROOT/current")
    local vulkan_service=$(systemctl is-active llama-server-8400.service 2>/dev/null || echo "unknown")

    echo "  当前版本: ${vulkan_current:-none}"
    echo "  服务状态: $vulkan_service"
    echo "  符号链接: $_SROOT/current"
    echo "  API 地址: http://localhost:8400"
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

    # 已安装版本列表
    echo -e "${BLUE}[已安装版本]${NC}"
    echo "  Vulkan 版本:"
    for dir in $_SROOT/downloads/llama-b[0-9]*; do
        if [ -d "$dir" ] && [ ! -L "$dir" ]; then
            local v=$(basename "$dir" | sed 's/llama-b//')
            echo "    - b$v"
        fi
    done 2>/dev/null || echo "    (无)"

    echo ""
    echo "  CUDA 版本: (源码编译)"
    if [ -f "/home/oliveagle/opt/llama.cpp/build/bin/llama-server" ]; then
        echo "    - b$cuda_current (当前运行)"
    else
        echo "    (未安装)"
    fi

    echo ""
    echo "=========================================="
    echo ""
    echo "使用方法:"
    echo "  ./update-llama-cpp.sh vulkan       # 更新 Vulkan"
    echo "  ./update-llama-cpp.sh cuda         # 更新 CUDA"
    echo "  ./update-llama-cpp.sh status       # 查看状态"
    echo ""
}

# 显示帮助
show_help() {
    echo "llama.cpp 统一更新脚本"
    echo ""
    echo "用法:"
    echo "  $0 vulkan [版本|list]    更新或列出 Vulkan 版本"
    echo "  $0 cuda [版本|list]      更新或列出 CUDA 版本"
    echo "  $0 status                查看当前版本状态"
    echo "  $0 help                  显示帮助"
    echo ""
    echo "示例:"
    echo "  $0 vulkan                更新 Vulkan 到最新版本"
    echo "  $0 vulkan list           列出 Vulkan 可用版本"
    echo "  $0 vulkan 8069           更新 Vulkan 到 b8069"
    echo "  $0 cuda                  更新 CUDA 到最新版本"
    echo "  $0 cuda list             列出 CUDA 可用版本"
    echo ""
}

# 主函数
main() {
    local cmd=${1:-}
    local arg=${2:-}

    case "$cmd" in
        vulkan)
            if [ "$arg" = "list" ]; then
                list_versions "Vulkan" "ubuntu-vulkan-x64"
            else
                update_vulkan "$arg"
            fi
            ;;
        cuda)
            if [ "$arg" = "list" ]; then
                list_versions "CUDA" "ubuntu-x64-cuda-cu12.4"
            else
                update_cuda "$arg"
            fi
            ;;
        status)
            show_status
            ;;
        help|--help|-h)
            show_help
            ;;
        "")
            show_help
            exit 1
            ;;
        *)
            log_error "未知命令: $cmd"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
