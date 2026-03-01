#!/usr/bin/env bash
# 运行所有 GGUF 模型的 benchmark

_SROOT="$( cd "$(dirname "$(realpath "$0")")/.." ; pwd -P )"
LLAMA_BENCH="$_SROOT/current/llama-bench"

# 模型目录
MODEL_DIRS=(
    "/mnt/volume3/hf_models"
    "/mnt/volume3/modelscope_models"
)

# 过滤关键词
FILTER_KEYWORDS=(
    "z_image"
    "qwen-image"
    "Wan2.2"
)

# 结果目录
RESULT_DIR="/tmp/benchmark_all_models_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$RESULT_DIR"
RESULT_SUMMARY="$RESULT_DIR/summary.md"

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 检查是否应该过滤
should_filter() {
    local filename="$1"
    for keyword in "${FILTER_KEYWORDS[@]}"; do
        if [[ "$filename" == *"$keyword"* ]]; then
            return 0
        fi
    done
    return 1
}

# 检查是否是第一个分片
is_first_shard() {
    local filename="$1"
    if [[ "$filename" =~ -[0-9]+-of-[0-9]+\.gguf$ ]]; then
        local shard_num=$(echo "$filename" | sed -E 's/.*-([0-9]+)-of-[0-9]+\.gguf$/\1/')
        if [[ "$shard_num" == "00001" ]] || [[ "$shard_num" == "1" ]]; then
            return 0
        else
            return 1
        fi
    fi
    return 0
}

# 收集所有模型
models=()
for dir in "${MODEL_DIRS[@]}"; do
    if [[ -d "$dir" ]]; then
        while IFS= read -r -d '' file; do
            filename=$(basename "$file")
            if should_filter "$filename"; then
                continue
            fi
            if ! is_first_shard "$filename"; then
                continue
            fi
            if [[ "$file" != *"/.__"* ]]; then
                models+=("$file")
            fi
        done < <(find "$dir" -type f -name "*.gguf" -print0 | sort -z)
    fi
done

echo "=========================================="
echo "运行所有模型 Benchmark"
echo "=========================================="
echo ""
echo "找到 ${#models[@]} 个模型"
echo "结果将保存到: $RESULT_DIR"
echo ""
echo "预计时间: 约 30-60 分钟"
echo ""

# 开始测试
echo -e "# 全模型 Benchmark 结果" > "$RESULT_SUMMARY"
echo -e "生成时间: $(date)" >> "$RESULT_SUMMARY"
echo -e "模型数量: ${#models[@]}" >> "$RESULT_SUMMARY"
echo "" >> "$RESULT_SUMMARY"

for i in "${!models[@]}"; do
    model="${models[$i]}"
    filename=$(basename "$model")
    safe_name=$(echo "$filename" | sed 's/[^a-zA-Z0-9._-]/_/g' | sed 's/\.gguf$//')

    echo -e "${GREEN}[$((i+1))/${#models[@]}]${NC} 测试: $filename"

    # 获取模型大小
    model_size=$(du -h "$model" | cut -f1)

    # 创建结果文件
    result_file="$RESULT_DIR/${safe_name}.txt"

    # 运行 benchmark
    # 使用纯 CPU 模式（ngl=0）避免 GPU 内存冲突
    if timeout 300 "$LLAMA_BENCH" \
        -m "$model" \
        -p 128 -n 64 \
        --no-warmup \
        -ngl 0 \
        --mmap 1 \
        -t 16 \
        -o md \
        > "$result_file" 2>&1; then
        echo -e "  ${GREEN}✓ 完成${NC}"

        # 提取关键指标
        pp=$(grep -E "^\|" "$result_file" | grep -v "^|--" | awk '{print $5}' | head -1)
        tg=$(grep -E "^\|" "$result_file" | grep -v "^|--" | awk '{print $6}' | head -1)

        echo -e "  大小: $model_size | PP: $pp | TG: $tg"

        # 添加到汇总
        echo -e "## $filename" >> "$RESULT_SUMMARY"
        echo -e "- **大小**: $model_size" >> "$RESULT_SUMMARY"
        echo -e "- **路径**: $model" >> "$RESULT_SUMMARY"
        echo -e "- **Prompt Processing (t/s)**: $pp" >> "$RESULT_SUMMARY"
        echo -e "- **Text Generation (t/s)**: $tg" >> "$RESULT_SUMMARY"
        echo "" >> "$RESULT_SUMMARY"
        echo -e '```' >> "$RESULT_SUMMARY"
        cat "$result_file" >> "$RESULT_SUMMARY"
        echo -e '```' >> "$RESULT_SUMMARY"
        echo "" >> "$RESULT_SUMMARY"
    else
        echo -e "  ${RED}✗ 失败 (超时或错误)${NC}"
        echo -e "## $filename" >> "$RESULT_SUMMARY"
        echo -e "- **状态**: 测试失败" >> "$RESULT_SUMMARY"
        echo -e "- **路径**: $model" >> "$RESULT_SUMMARY"
        echo "" >> "$RESULT_SUMMARY"
    fi
    echo ""
done

echo "=========================================="
echo "Benchmark 完成！"
echo "=========================================="
echo ""
echo "结果保存位置:"
echo "  汇总: $RESULT_SUMMARY"
echo "  详细: $RESULT_DIR/"
echo ""
echo "查看汇总:"
cat "$RESULT_SUMMARY"
