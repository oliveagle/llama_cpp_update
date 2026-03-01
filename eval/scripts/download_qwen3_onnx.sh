#!/bin/bash
#
# 下载 Qwen3 ONNX 模型
# 支持：
#   - Qwen3-0.6B-ONNX (onnx-community)
#   - Qwen3-1.7B-ONNX (如有)
#

set -e

# 使用 HuggingFace 镜像
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"

# 输出目录
OUTPUT_DIR="${1:-$HOME/models/qwen3-onnx}"

# 模型选择
MODEL="${2:-0.6B}"

echo "============================================================"
echo "Qwen3 ONNX 模型下载工具"
echo "============================================================"
echo ""

case "$MODEL" in
    "0.6B"|"qwen3-0.6b")
        MODEL_REPO="onnx-community/Qwen3-0.6B-ONNX"
        MODEL_DIR="Qwen3-0.6B-ONNX"
        ;;
    "1.7B"|"qwen3-1.7b")
        MODEL_REPO="onnx-community/Qwen3-1.7B-ONNX"
        MODEL_DIR="Qwen3-1.7B-ONNX"
        ;;
    *)
        echo "❌ 未知模型：$MODEL"
        echo "可用模型：0.6B, 1.7B"
        exit 1
        ;;
esac

echo "模型：$MODEL_REPO"
echo "输出目录：$OUTPUT_DIR"
echo ""

# 检查 git-lfs
if ! command -v git-lfs &> /dev/null; then
    echo "❌ git-lfs 未安装"
    echo "   sudo apt install git-lfs"
    echo "   git lfs install"
    exit 1
fi

# 创建目录
mkdir -p "$OUTPUT_DIR"

# 下载
MODEL_OUTPUT="$OUTPUT_DIR/$MODEL_DIR"
echo "开始下载：$MODEL_OUTPUT"

if [ -d "$MODEL_OUTPUT" ]; then
    echo "⚠ 目录已存在，更新..."
    cd "$MODEL_OUTPUT"
    git pull
else
    git clone "$HF_ENDPOINT/$MODEL_REPO" "$MODEL_OUTPUT"
fi

echo ""
echo "✓ 下载完成!"
echo ""
echo "目录结构:"
ls -lh "$MODEL_OUTPUT"
echo ""

# 查找 ONNX 文件
echo "ONNX 文件:"
find "$MODEL_OUTPUT" -name "*.onnx" -exec ls -lh {} \;
echo ""

echo "使用方法:"
echo "  export LLAMA_NPU_MODEL=$MODEL_OUTPUT/model.onnx"
echo "  cd /mnt/volume3/llama_cpp"
echo "  ./src/ryzenai/llama-npu-server --model \$LLAMA_NPU_MODEL --port 8404"
echo ""
echo "或:"
echo "  ./bin/llama-npu-server.sh start"
