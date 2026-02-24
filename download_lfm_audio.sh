#!/bin/bash
# Download LFM2.5-Audio-1.5B GGUF model from HuggingFace

set -e

# Configuration
MODEL_REPO="ggml-org/LFM2.5-Audio-1.5B-GGUF"
HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"
MODEL_DIR="/mnt/volume3/llama_cpp/models/lfm2.5-audio"

echo "============================================================"
echo "LFM2.5-Audio-1.5B GGUF 模型下载"
echo "============================================================"

# Create model directory
mkdir -p "$MODEL_DIR"
echo -e "\n模型目录: $MODEL_DIR"

# Files to download (based on typical ggml-org repo structure)
GGUF_FILES=(
    "LFM2.5-Audio-1.5B-Q4_K_M.gguf"
    "LFM2.5-Audio-1.5B-Q8_0.gguf"
    "LFM2.5-Audio-1.5B-IQ4_XS.gguf"
    "LFM2.5-Audio-1.5B-Q4_K_S.gguf"
    "LFM2.5-Audio-1.5B-Q5_K_M.gguf"
    "LFM2.5-Audio-1.5B-Q2_K.gguf"
    "LFM2.5-Audio-1.5B-F16.gguf"
)

# Other useful files
OTHER_FILES=(
    "README.md"
    "config.json"
    "generation_config.json"
    "tokenizer.json"
    "tokenizer.model"
    "tokenizer_config.json"
    "preprocessor_config.json"
)

# Try to download a directory listing first to see what's available
echo -e "\n尝试获取仓库文件列表..."
TEMP_HTML=$(mktemp /tmp/lfm_repo.XXXXXX.html)

# Cleanup on exit
cleanup() {
    rm -f "$TEMP_HTML"
}
trap cleanup EXIT

# Function to download a file with progress
download_file() {
    local fname="$1"
    local url="${HF_ENDPOINT}/${MODEL_REPO}/resolve/main/${fname}"
    local dest="${MODEL_DIR}/${fname}"

    echo -e "\n下载: $fname"

    # Try wget first
    if command -v wget &> /dev/null; then
        if wget -c --progress=bar:force:noscroll -O "$dest" "$url" 2>&1; then
            local size=$(du -h "$dest" 2>/dev/null | cut -f1)
            echo "  ✓ 完成 ($size)"
            return 0
        else
            echo "  wget 失败，尝试 curl..."
            rm -f "$dest"
        fi
    fi

    # Try curl
    if command -v curl &> /dev/null; then
        if curl -L -C - -o "$dest" "$url" --progress-bar 2>&1; then
            local size=$(du -h "$dest" 2>/dev/null | cut -f1)
            echo "  ✓ 完成 ($size)"
            return 0
        else
            echo "  curl 失败"
            rm -f "$dest"
        fi
    fi

    echo "  ✗ 下载失败: $fname"
    return 1
}

# First, try to download Q4_K_M (most popular)
echo -e "\n第一步: 下载 Q4_K_M 量化版本 (推荐)"
TARGET_Q4=""
for f in "${GGUF_FILES[@]}"; do
    if [[ "$f" == *"Q4_K_M"* ]]; then
        TARGET_Q4="$f"
        break
    fi
done

if [ -z "$TARGET_Q4" ]; then
    TARGET_Q4="${GGUF_FILES[0]}"
fi

DOWNLOADED=()
FAILED=()

# Try to download the primary model
if download_file "$TARGET_Q4"; then
    DOWNLOADED+=("$TARGET_Q4")
else
    FAILED+=("$TARGET_Q4")
    # Try other GGUF files
    echo -e "\n尝试其他量化版本..."
    for f in "${GGUF_FILES[@]}"; do
        if [ "$f" != "$TARGET_Q4" ]; then
            if download_file "$f"; then
                DOWNLOADED+=("$f")
                break  # Got at least one
            else
                FAILED+=("$f")
            fi
        fi
    done
fi

# Try to download other useful files
echo -e "\n第二步: 下载配置和 tokenizer 文件..."
for f in "${OTHER_FILES[@]}"; do
    if download_file "$f"; then
        DOWNLOADED+=("$f")
    else
        FAILED+=("$f")
    fi
done

# Summary
echo -e "\n============================================================"
echo "下载完成"
echo "============================================================"

echo -e "\n成功下载 (${#DOWNLOADED[@]} 个):"
for f in "${DOWNLOADED[@]}"; do
    if [ -f "${MODEL_DIR}/${f}" ]; then
        size=$(du -h "${MODEL_DIR}/${f}" 2>/dev/null | cut -f1)
        echo "  ✓ ${f} (${size})"
    fi
done

if [ ${#FAILED[@]} -gt 0 ]; then
    echo -e "\n失败 (${#FAILED[@]} 个):"
    for f in "${FAILED[@]}"; do
        echo "  ✗ ${f}"
    done
fi

# Show directory contents
echo -e "\n模型目录内容:"
ls -lh "$MODEL_DIR" 2>/dev/null || echo "  (无法列出目录)"

# Check if we have at least one GGUF
HAS_GGUF=0
for f in "${MODEL_DIR}"/*.gguf 2>/dev/null; do
    if [ -f "$f" ]; then
        HAS_GGUF=1
        break
    fi
done

if [ $HAS_GGUF -eq 1 ]; then
    echo -e "\n✓ 成功: 模型已下载到 $MODEL_DIR"
    exit 0
else
    echo -e "\n✗ 错误: 没有下载到 GGUF 模型文件"
    exit 1
fi
