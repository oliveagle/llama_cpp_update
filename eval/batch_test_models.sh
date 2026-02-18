#!/bin/bash
# 批量测试V100上的所有模型

MODEL_URL="http://localhost:8401"
OUTPUT_DIR="./eval_results/batch_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"

# 模型列表
MODELS=(
    "Qwen3-0.6B-Q4_0"
    "Alibaba-Apsara.DASD-4B-Thinking.Q8_0"
    "MiniCPM-o-4_5-Q4_K_M"
    "Qwen3-4B-Instruct-2507-UD-Q4_K_XL"
    "Qwen3VL-4B-Instruct-Q8_0"
    "Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0"
    "GLM-4.7-Flash-Q4_K_M"
    "JoyAI-LLM-Flash-Q4_K_M"
)

echo "=============================================="
echo "V100模型批量测试"
echo "输出目录: $OUTPUT_DIR"
echo "=============================================="

SUMMARY_FILE="$OUTPUT_DIR/summary.txt"
echo "模型名称, 通过数, 总数, 准确率" > "$SUMMARY_FILE"

for MODEL in "${MODELS[@]}"; do
    echo ""
    echo "=============================================="
    echo "测试模型: $MODEL"
    echo "=============================================="
    
    # 切换模型
    echo "加载模型: $MODEL"
    curl -s -X POST "${MODEL_URL}/v1/models/${MODEL}/load" -H "Content-Type: application/json" > /dev/null
    sleep 5
    
    # 运行测试
    python3 eval_linux_ops.py \
        --model-url "$MODEL_URL" \
        --model-name "$MODEL" \
        --basic-only \
        --output-dir "$OUTPUT_DIR" \
        2>&1 | tee "$OUTPUT_DIR/${MODEL}_test.log"
    
    # 提取结果
    ACCURACY=$(grep "准确率:" "$OUTPUT_DIR/${MODEL}_test.log" | tail -1 | sed 's/.*准确率: //')
    PASSED=$(grep "通过:" "$OUTPUT_DIR/${MODEL}_test.log" | tail -1 | sed 's/.*通过: //')
    TOTAL=$(grep "总计:" "$OUTPUT_DIR/${MODEL}_test.log" | tail -1 | sed 's/.*总计: //')
    
    echo "$MODEL, $PASSED, $TOTAL, $ACCURACY" >> "$SUMMARY_FILE"
done

echo ""
echo "=============================================="
echo "批量测试完成"
echo "汇总: $SUMMARY_FILE"
echo "=============================================="
cat "$SUMMARY_FILE"
