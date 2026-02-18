#!/bin/bash
# Stage 2 顺序测试所有模型 - 每次测试一个，不切换
# 用法: ./run_stage2_all_models_sequential.sh

set -e

MODELS=(
    "Qwen3-Coder-Next-Q4_K_M"
    "Qwen3VL-4B-Instruct-Q8_0"
    "Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0"
    "MiniCPM-o-4_5-Q4_K_M"
    "Qwen3-4B-Instruct-2507-UD-Q4_K_XL"
    "GLM-4.7-Flash-Q4_K_M"
    "GLM-4.7-Flash-REAP-23B-A3B-IQ4_NL"
    "MiroThinker-v1.5-30B.Q8_0"
)

BASE_DIR="/mnt/volume3/llama_cpp"
RESULTS_DIR="$BASE_DIR/eval_results/stage2"
LOG_DIR="$RESULTS_DIR/logs"

mkdir -p "$RESULTS_DIR"
mkdir -p "$LOG_DIR"

echo "================================================================================"
echo "🧪 Stage 2 顺序测试 - 所有模型 (逐个测试，不切换)"
echo "⏰ 开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================================"

TOTAL=${#MODELS[@]}
COMPLETED=0
FAILED=0

for i in "${!MODELS[@]}"; do
    MODEL="${MODELS[$i]}"
    NUM=$((i + 1))

    echo ""
    echo "################################################################################"
    echo "# [$NUM/$TOTAL] 测试模型: $MODEL"
    echo "################################################################################"

    # 等待服务就绪
    echo "⏳ 等待服务就绪..."
    for retry in {1..30}; do
        if curl -s http://localhost:8400/v1/models >/dev/null 2>&1; then
            echo "✅ 服务已就绪"
            break
        fi
        if [ $retry -eq 30 ]; then
            echo "❌ 服务未就绪，跳过此模型"
            FAILED=$((FAILED + 1))
            continue 2
        fi
        sleep 2
    done

    # 运行测试
    LOG_FILE="$LOG_DIR/${MODEL}_stage2.log"
    echo "📝 运行测试 (日志: $LOG_FILE)..."

    if python3 "$BASE_DIR/eval/run_stage2_single_model.py" "$MODEL" 2>&1 | tee "$LOG_FILE"; then
        echo "✅ 测试完成: $MODEL"
        COMPLETED=$((COMPLETED + 1))
    else
        echo "⚠️  测试可能有问题: $MODEL (查看日志)"
        # 继续测试下一个
    fi

    # 测试间等待，让服务稳定
    if [ $NUM -lt $TOTAL ]; then
        echo "⏳ 等待10秒让服务稳定..."
        sleep 10
    fi
done

echo ""
echo "================================================================================"
echo "📊 测试完成汇总"
echo "================================================================================"
echo "总模型数: $TOTAL"
echo "成功完成: $COMPLETED"
echo "失败/跳过: $FAILED"
echo ""
echo "💾 结果保存: $RESULTS_DIR/"
echo "📝 日志保存: $LOG_DIR/"
echo "================================================================================"

# 生成对比报告
echo ""
echo "📈 生成对比报告..."
python3 << 'EOF'
import json
import os
from glob import glob

results_dir = "/mnt/volume3/llama_cpp/eval_results/stage2"
result_files = sorted(glob(f"{results_dir}/*_stage2.json"))

if not result_files:
    print("没有找到结果文件")
    exit(0)

results = []
for f in result_files:
    try:
        with open(f) as fp:
            data = json.load(fp)
            if 'summary' in data and data['summary'].get('total_tests', 0) > 0:
                results.append(data)
    except:
        pass

if not results:
    print("没有有效的结果数据")
    exit(0)

# 排序
results.sort(key=lambda x: x['summary']['total_pass_rate'], reverse=True)

print("\n" + "="*80)
print("🏅 Stage 2 模型排名")
print("="*80)
print(f"{'排名':<4} {'模型名称':<45} {'通过率':<8} {'评级':<10}")
print("-"*80)

for i, r in enumerate(results, 1):
    rate = r['summary']['total_pass_rate'] * 100
    grade = "⭐⭐⭐⭐⭐" if rate >= 80 else "⭐⭐⭐⭐" if rate >= 60 else "⭐⭐⭐" if rate >= 40 else "⭐⭐"
    name = r['model'][:43]
    print(f"{i:<4} {name:<45} {rate:>6.1f}%  {grade:<10}")

print("="*80)

# 各类别冠军
print("\n📊 各类别 TOP 1:")
code_best = max(results, key=lambda x: x['code']['pass_rate'])
math_best = max(results, key=lambda x: x['math']['pass_rate'])
text_best = max(results, key=lambda x: x['text']['pass_rate'])

print(f"  💻 代码能力: {code_best['model']} ({code_best['code']['pass_rate']*100:.1f}%)")
print(f"  🔢 数学推理: {math_best['model']} ({math_best['math']['pass_rate']*100:.1f}%)")
print(f"  📚 文本理解: {text_best['model']} ({text_best['text']['pass_rate']*100:.1f}%)")

if results:
    overall_best = results[0]
    print(f"\n🥇 综合能力最强: {overall_best['model']} ({overall_best['summary']['total_pass_rate']*100:.1f}%)")
EOF

echo ""
echo "✅ 所有测试完成！"
