#!/bin/bash
# LFM2.5-Audio-1.5B GGUF 模型下载脚本

set -e

# 配置
MODEL_REPO="ggml-org/LFM2.5-Audio-1.5B-GGUF"
HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
MODEL_DIR="/mnt/volume3/llama_cpp/models/lfm2.5-audio"

# 创建目录
mkdir -p "$MODEL_DIR"
cd "$MODEL_DIR"

echo "============================================================"
echo "LFM2.5-Audio-1.5B GGUF 模型下载"
echo "============================================================"
echo ""
echo "模型目录: $MODEL_DIR"
echo "使用镜像: $HF_ENDPOINT"
echo ""

# 检查下载工具
DOWNLOAD_TOOL=""
if command -v wget &> /dev/null; then
    DOWNLOAD_TOOL="wget"
    echo "使用工具: wget"
elif command -v curl &> /dev/null; then
    DOWNLOAD_TOOL="curl"
    echo "使用工具: curl"
else
    echo "错误: 未找到 wget 或 curl，请先安装下载工具"
    exit 1
fi

# 下载函数
download_file() {
    local fname="$1"
    local url="${HF_ENDPOINT}/${MODEL_REPO}/resolve/main/${fname}"
    local dest="${MODEL_DIR}/${fname}"

    echo ""
    echo "下载: $fname"
    echo "  URL: $url"

    if [ "$DOWNLOAD_TOOL" = "wget" ]; then
        if wget -c --progress=bar:force -O "$dest" "$url" 2>&1; then
            local size=$(du -h "$dest" 2>/dev/null | cut -f1)
            echo "  ✓ 完成 ($size)"
            return 0
        else
            echo "  ✗ 下载失败"
            rm -f "$dest" 2>/dev/null || true
            return 1
        fi
    else
        if curl -L -C - -o "$dest" "$url" --progress-bar 2>&1; then
            local size=$(du -h "$dest" 2>/dev/null | cut -f1)
            echo "  ✓ 完成 ($size)"
            return 0
        else
            echo "  ✗ 下载失败"
            rm -f "$dest" 2>/dev/null || true
            return 1
        fi
    fi
}

# 第一步：下载主模型 (Q4_K_M)
echo ""
echo "[1/2] 下载 GGUF 模型 (Q4_K_M - 推荐)..."
TARGET_GGUF="LFM2.5-Audio-1.5B-Q4_K_M.gguf"

if download_file "$TARGET_GGUF"; then
    GGUF_DOWNLOADED=1
else
    GGUF_DOWNLOADED=0
    echo ""
    echo "Q4_K_M 下载失败，尝试其他版本..."

    # 尝试其他量化版本
    for fname in \
        "LFM2.5-Audio-1.5B-Q8_0.gguf" \
        "LFM2.5-Audio-1.5B-Q4_K_S.gguf" \
        "LFM2.5-Audio-1.5B-Q5_K_M.gguf" \
        "LFM2.5-Audio-1.5B-IQ4_XS.gguf" \
        "LFM2.5-Audio-1.5B-F16.gguf"; do
        echo ""
        echo "尝试: $fname"
        if download_file "$fname"; then
            GGUF_DOWNLOADED=1
            TARGET_GGUF="$fname"
            break
        fi
    done
fi

# 第二步：下载配置文件
echo ""
echo "[2/2] 下载配置和 tokenizer 文件..."
for fname in \
    "README.md" \
    "config.json" \
    "tokenizer.json" \
    "tokenizer.model" \
    "tokenizer_config.json" \
    "preprocessor_config.json" \
    "generation_config.json"; do
    download_file "$fname" || true  # 可选文件，失败继续
done

# 总结
echo ""
echo "============================================================"
echo "下载完成"
echo "============================================================"
echo ""
echo "目录内容:"
ls -lh "$MODEL_DIR" 2>/dev/null || echo "  (无法列出)"
echo ""

# 检查是否有 GGUF
HAS_GGUF=0
for f in "$MODEL_DIR"/*.gguf; do
    if [ -f "$f" ]; then
        HAS_GGUF=1
        break
    fi
done

if [ $HAS_GGUF -eq 1 ]; then
    echo "✓ 成功！模型已下载到: $MODEL_DIR"
    echo ""
    echo "使用方法 (llama.cpp):"
    echo "  cd /mnt/volume3/llama_cpp"
    echo "  ./current/llama-cli --model $MODEL_DIR/$TARGET_GGUF --prompt \"Hello\""
    exit 0
else
    echo "✗ 错误：未下载到 GGUF 模型文件"
    exit 1
fi
