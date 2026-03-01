#!/bin/bash
# 定时分析 HuggingFace Trending GGUF 模型
# 建议添加到 crontab: 0 9 * * * /mnt/volume3/llama_cpp/cron_analyze.sh

set -e

cd /mnt/volume3/llama_cpp

LOG_FILE="logs/analyze_$(date +%Y%m%d_%H%M).log"
mkdir -p logs

echo "========================================" | tee -a "$LOG_FILE"
echo "Trending GGUF 分析 - $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# 运行分析
export HF_ENDPOINT=https://hf-mirror.com
python3 analyze_trending_models.py 2>&1 | tee -a "$LOG_FILE"

echo "" | tee -a "$LOG_FILE"
echo "分析完成: $(date)" | tee -a "$LOG_FILE"

# 发送通知 (如果配置了)
if [ -f "trending_analysis.md" ]; then
    # 检查是否有高优先级推荐
    HIGH_PRIORITY=$(grep -c "\[9/10\]\|\[10/10\]" trending_analysis.md || true)

    if [ "$HIGH_PRIORITY" -gt 0 ]; then
        echo "" | tee -a "$LOG_FILE"
        echo "⚠️  发现 $HIGH_PRIORITY 个高优先级模型推荐测试!" | tee -a "$LOG_FILE"

        # 可以在这里添加邮件/钉钉通知
        # echo "有新模型需要测试" | mail -s "GGUF模型推荐" admin@example.com
    fi
fi

# 运行自动化评估 (每天一次)
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "开始自动化模型评估 - $(date)" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 激活虚拟环境
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    python3 auto_eval_models.py --limit 3 2>&1 | tee -a "$LOG_FILE"
else
    echo "虚拟环境不存在，跳过评估" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "评估完成: $(date)" | tee -a "$LOG_FILE"

# 保留最近30天日志
find logs -name "analyze_*.log" -mtime +30 -delete 2>/dev/null || true

echo "日志保存: $LOG_FILE"
