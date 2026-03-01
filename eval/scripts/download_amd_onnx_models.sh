#!/bin/bash
#
# 下载 AMD Ryzen AI 官方 ONNX 模型
#

set -e

# 使用 HuggingFace 镜像
export HF_ENDPOINT="${HF_ENDPOINT:-https://hf-mirror.com}"

# 模型列表
declare -A MODELS=(
    ["llama-3.2-1b"]="amd/Llama-3.2-1B-Instruct-onnx-ryzenai-npu"
    ["llama-3.2-3b"]="amd/Llama-3.2-3B-Instruct-onnx-ryzenai-npu"
    ["qwen2.5-0.5b"]="amd/Qwen2.5-0.5B-Instruct-onnx-ryzenai-npu"
)

# 输出目录
OUTPUT_DIR="${1:-$HOME/models/ryzenai-onnx}"

echo "============================================================"
echo "AMD Ryzen AI ONNX 模型下载工具"
echo "============================================================"
echo ""
echo "可用模型:"
i=1
for key in "${!MODELS[@]}"; do
    echo "  $i. $key - ${MODELS[$key]}"
    ((i++))
done
echo ""

# 如果没有指定模型名称，显示选择菜单
if [ -z "$2" ]; then
    echo "用法：$0 <输出目录> <模型名称>"
    echo ""
    echo "示例:"
    echo "  $0 ~/models/ryzenai-onnx llama-3.2-1b"
    echo "  $0 ~/models/ryzenai-onnx llama-3.2-3b"
    echo ""
    exit 0
fi

MODEL_KEY="$2"
MODEL_REPO="${MODELS[$MODEL_KEY]}"

if [ -z "$MODEL_REPO" ]; then
    echo "❌ 未知模型：$MODEL_KEY"
    echo "可用模型：${!MODELS[@]}"
    exit 1
fi

echo "下载模型：$MODEL_REPO"
echo "输出目录：$OUTPUT_DIR"
echo ""

# 检查 git-lfs
if ! command -v git-lfs &> /dev/null; then
    echo "❌ git-lfs 未安装，请先安装："
    echo "   sudo apt install git-lfs"
    echo "   git lfs install"
    exit 1
fi

# 创建输出目录
mkdir -p "$OUTPUT_DIR"

# 下载模型
MODEL_OUTPUT="$OUTPUT_DIR/$MODEL_KEY"
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
echo "使用方法:"
echo "  export LLAMA_NPU_MODEL=$MODEL_OUTPUT/model.onnx"
echo "  cd /mnt/volume3/llama_cpp"
echo "  ./src/ryzenai/llama-npu-server --model \$LLAMA_NPU_MODEL --port 8404"
