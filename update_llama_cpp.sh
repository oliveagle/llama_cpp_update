#!/bin/bash

# llama.cpp 自动更新脚本
# 用于下载并更新指定版本或最新版本的 Vulkan Linux 版本
#
# 用法:
#   ./update_llama_cpp.sh           # 更新到最新版本
#   ./update_llama_cpp.sh 7600      # 更新到指定版本 b7600
#   ./update_llama_cpp.sh b7600     # 更新到指定版本 b7600（带 b 前缀）
#   ./update_llama_cpp.sh list      # 列出所有可用版本

set -e

_SROOT="$( cd "$(dirname "$(realpath "$0")")" ; pwd -P )"

# 配置
REPO_URL="https://github.com/ggml-org/llama.cpp"
RELEASES_URL="https://api.github.com/repos/ggml-org/llama.cpp/releases"
DOWNLOAD_DIR="/tmp"
BASE_DIR="$_SROOT"
DOWNLOADS_DIR="$BASE_DIR/downloads"
CURRENT_LINK="$BASE_DIR/current"
PROXY="http://127.0.0.1:1080"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1" >&2
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1" >&2
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

# 获取当前版本号
get_current_version() {
    if [ -L "$CURRENT_LINK" ]; then
        current_dir=$(basename "$(readlink -f "$CURRENT_LINK")")
        echo "$current_dir" | sed 's/llama-b//'
    else
        echo "none"
    fi
}

# 获取最新版本号
get_latest_version() {
    log_info "检查最新版本..."

    # 获取最新发布版本（不包括预发布版本）
    latest_release=$(curl -x "$PROXY" -s "$RELEASES_URL/latest" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

    if [ -z "$latest_release" ]; then
        log_error "无法获取最新版本信息"
        exit 1
    fi

    # 移除 'b' 前缀得到纯数字版本号
    version_number=$(echo "$latest_release" | sed 's/b//')
    echo "$version_number"
}

# 列出所有可用版本
list_versions() {
    log_info "获取所有可用版本..."

    # 获取所有发布版本
    releases=$(curl -x "$PROXY" -s "$RELEASES_URL" | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/' | head -20)

    if [ -z "$releases" ]; then
        log_error "无法获取版本列表"
        exit 1
    fi

    echo ""
    echo "=========================================="
    echo "可用的 llama.cpp 版本（最近 20 个）："
    echo "=========================================="

    # 显示版本列表
    local count=0
    for release in $releases; do
        count=$((count + 1))
        version_number=$(echo "$release" | sed 's/b//')
        printf "  %2d. b%s\n" "$count" "$version_number"
    done

    echo "=========================================="
    echo ""
    echo "使用方法: ./update_llama_cpp.sh <版本号>"
    echo "例如:     ./update_llama_cpp.sh b7600"
}

# 下载并解压新版本
download_and_extract() {
    local version=$1
    local version_tag="b$version"
    local filename="llama-${version_tag}-bin-ubuntu-vulkan-x64.tar.gz"
    local download_url="${REPO_URL}/releases/download/${version_tag}/${filename}"

    log_info "准备下载版本: $version_tag"
    log_info "下载地址: $download_url"

    # 检查文件是否已存在
    if [ -f "$DOWNLOADS_DIR/$filename" ]; then
        log_warn "文件已存在: $filename"
        read -p "是否重新下载? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "使用现有文件"
            return
        fi
    fi

    # 下载文件
    log_info "开始下载（通过代理 $PROXY）..."
    if curl -x "$PROXY" -L -o "$DOWNLOADS_DIR/$filename" "$download_url"; then
        log_info "下载完成: $filename"
    else
        log_error "下载失败"
        exit 1
    fi
}

# 安装新版本
install_new_version() {
    local version=$1
    local filename="llama-b${version}-bin-ubuntu-vulkan-x64.tar.gz"
    local new_dir="$DOWNLOADS_DIR/llama-b${version}"

    # 检查是否已解压
    if [ -d "$new_dir" ]; then
        log_warn "目录已存在: $new_dir"
        read -p "是否重新解压? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            return
        fi
        rm -rf "$new_dir"
    fi

    # 解压文件
    log_info "解压到: $new_dir"
    mkdir -p "$new_dir"
    tar -xzf "$DOWNLOADS_DIR/$filename" -C "$new_dir" --strip-components=1

    if [ $? -eq 0 ]; then
        log_info "解压完成"
    else
        log_error "解压失败"
        exit 1
    fi
}

# 更新符号链接
update_symlink() {
    local version=$1
    local new_dir="$DOWNLOADS_DIR/llama-b${version}"

    log_info "更新 current 符号链接..."

    # 删除旧的符号链接
    if [ -L "$CURRENT_LINK" ]; then
        rm "$CURRENT_LINK"
    fi

    # 创建新的符号链接
    ln -s "$new_dir" "$CURRENT_LINK"

    log_info "符号链接已更新: $CURRENT_LINK -> $new_dir"
}

# 清理旧版本（可选）
cleanup_old_versions() {
    log_warn "是否清理旧版本? (保留最近 5 个版本)"
    read -p "清理旧版本? (y/N): " -n 1 -r
    echo

    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi

    local versions=()
    for dir in "$DOWNLOADS_DIR"/llama-b*; do
        if [ -d "$dir" ] && [ ! -L "$dir" ]; then
            dir_version=$(basename "$dir" | sed 's/llama-b//')
            versions+=("$dir_version")
        fi
    done

    IFS=$'\n' sorted_versions=($(sort -rn <<<"${versions[*]}"))
    unset IFS

    local keep_count=5
    for i in "${!sorted_versions[@]}"; do
        version="${sorted_versions[$i]}"

        if [ $i -lt $keep_count ]; then
            log_info "保留版本: b$version"
        else
            log_info "删除旧版本: llama-b$version"
            rm -rf "$DOWNLOADS_DIR/llama-b$version"
            rm -f "$DOWNLOADS_DIR/llama-b${version}-bin-ubuntu-vulkan-x64.tar.gz"
        fi
    done

    log_info "清理完成"
}

# 主流程
main() {
    # 检查是否列出版本
    if [ "$1" = "list" ]; then
        list_versions
        exit 0
    fi

    # 解析命令行参数
    TARGET_VERSION=""

    if [ -n "$1" ]; then
        # 去掉可能存在的 'b' 前缀
        TARGET_VERSION=$(echo "$1" | sed 's/^b//')
        log_info "指定目标版本: b$TARGET_VERSION"
    fi

    log_info "=========================================="
    log_info "llama.cpp 自动更新脚本"
    log_info "=========================================="

    # 获取当前版本
    current_version=$(get_current_version)
    log_info "当前版本: b$current_version"

    # 确定目标版本
    if [ -z "$TARGET_VERSION" ]; then
        # 获取最新版本
        latest_version=$(get_latest_version)
        log_info "最新版本: b$latest_version"
        target_version="$latest_version"

        # 检查是否需要更新
        if [ "$current_version" = "$latest_version" ]; then
            log_info "已经是最新版本，无需更新"
            exit 0
        fi

        log_info "发现新版本，准备更新..."
    else
        target_version="$TARGET_VERSION"
        log_info "目标版本: b$target_version"

        # 检查是否已经是目标版本
        if [ "$current_version" = "$target_version" ]; then
            log_info "当前版本已是目标版本，无需更新"
            exit 0
        fi
    fi

    # 下载
    download_and_extract "$target_version"

    # 安装
    install_new_version "$target_version"

    # 更新符号链接
    update_symlink "$target_version"

    log_info "=========================================="
    log_info "更新完成！"
    log_info "当前版本: b$target_version"
    log_info "=========================================="

    # 询问是否清理
    cleanup_old_versions
}

# 运行主流程
main "$@"
