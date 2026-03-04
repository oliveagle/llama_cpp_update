#!/usr/bin/env python3
"""
批量评估脚本 - 评估所有符合条件的模型
"""

import argparse
import json
import os
import sys
from datetime import datetime
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from golden_benchmarks import GOLDEN_BENCHMARKS, get_all_categories


def find_gguf_models(search_paths: List[str]) -> List[Dict]:
    """在指定路径查找GGUF模型"""
    models = []

    for path in search_paths:
        if not os.path.exists(path):
            continue

        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith('.gguf'):
                    full_path = os.path.join(root, file)
                    models.append({
                        "name": file.replace('.gguf', ''),
                        "path": full_path,
                        "size_gb": os.path.getsize(full_path) / (1024**3),
                    })

    return models


def categorize_model(model_name: str) -> str:
    """根据名称推测模型类别"""
    name_lower = model_name.lower()

    if any(kw in name_lower for kw in ['coder', 'code', 'dev']):
        return 'Code'
    if any(kw in name_lower for kw in ['vl', 'vision', 'image']):
        return 'Vision'
    if any(kw in name_lower for kw in ['ocr', 'text-recognition']):
        return 'OCR'
    if any(kw in name_lower for kw in ['tts', 'speech', 'voice']):
        return 'TTS'
    if any(kw in name_lower for kw in ['reason', 'think', 'r1']):
        return 'Reasoning'

    return 'LLM'


def should_evaluate(model: Dict, category: str) -> bool:
    """判断是否应该评估该模型"""
    # 大小限制: 1GB - 40GB
    if model['size_gb'] < 1 or model['size_gb'] > 40:
        return False

    # 排除临时文件
    if model['name'].startswith('.') or 'temp' in model['name'].lower():
        return False

    # 排除embedding模型
    if 'embedding' in model['name'].lower():
        return False

    return True


def run_evaluation(model: Dict, category: str, output_dir: str) -> Dict:
    """运行单个模型评估"""
    print(f"\n评估模型: {model['name']}")
    print(f"  路径: {model['path']}")
    print(f"  大小: {model['size_gb']:.2f}GB")
    print(f"  类别: {category}")

    # 根据类别选择评估脚本
    eval_script = f"eval_{category.lower()}.py"
    eval_path = os.path.join(os.path.dirname(__file__), eval_script)

    if not os.path.exists(eval_path):
        # 使用通用的LLM评估
        if category == 'LLM':
            eval_path = os.path.join(os.path.dirname(__file__), "eval_llm.py")
        else:
            print(f"  跳过: 暂无{category}类别的评估脚本")
            return {"skipped": True, "reason": f"No eval script for {category}"}

    # 这里应该调用实际的评估脚本
    # 暂时返回占位结果
    return {
        "model": model['name'],
        "path": model['path'],
        "category": category,
        "size_gb": model['size_gb'],
        "status": "todo",
    }


def generate_summary_report(results: List[Dict], output_dir: str) -> str:
    """生成汇总报告"""

    report = f"""# GGUF模型批量评估汇总报告

> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 评估模型列表

| 模型 | 类别 | 大小 | 状态 | 备注 |
|------|------|------|------|------|
"""

    for r in results:
        status = r.get('status', 'unknown')
        if status == 'todo':
            status_str = '⬜ 待评估'
        elif status == 'done':
            status_str = '✅ 已完成'
        elif 'skipped' in r:
            status_str = '⏭️ 已跳过'
        else:
            status_str = status

        model_name = r.get('model', r.get('name', 'Unknown'))
        report += f"| {model_name} | {r.get('category', '-')} | {r.get('size_gb', 0):.1f}GB | {status_str} | {r.get('reason', '-')} |\n"

    report += """

---

## 黄金标杆对比

"""

    for category in get_all_categories():
        benchmark = GOLDEN_BENCHMARKS.get(category, {})
        baseline = benchmark.get('baseline')

        if baseline:
            report += f"### {category}\n\n"
            report += f"**黄金标杆**: {baseline['model']} ({baseline['size_gb']}GB)\n\n"

            metrics = benchmark.get('metrics', {})
            if metrics:
                report += "| 指标 | 标杆值 | 目标值 |\n"
                report += "|------|--------|--------|\n"
                for metric, config in metrics.items():
                    report += f"| {metric} | {config['baseline']} | {config['target']} |\n"

            report += "\n"

    return report


def main():
    parser = argparse.ArgumentParser(description="批量评估GGUF模型")
    parser.add_argument(
        "--search-paths",
        type=str,
        nargs="+",
        default=[
            "/mnt/volume3/modelscope_models",
            "/mnt/volume3/hf_models",
        ],
        help="搜索模型的路径",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./eval_results",
        help="输出目录",
    )
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        help="仅评估指定类别",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("GGUF模型批量评估")
    print("=" * 60)

    # 查找模型
    print("\n查找模型...")
    all_models = find_gguf_models(args.search_paths)
    print(f"找到 {len(all_models)} 个GGUF模型")

    # 分类并过滤
    models_to_eval = []
    for model in all_models:
        category = categorize_model(model['name'])

        if args.category and category != args.category:
            continue

        if should_evaluate(model, category):
            models_to_eval.append({
                **model,
                "category": category,
            })

    print(f"其中 {len(models_to_eval)} 个模型符合评估条件")

    # 运行评估
    results = []
    for model in models_to_eval:
        result = run_evaluation(model, model['category'], args.output_dir)
        results.append(result)

    # 生成汇总报告
    report = generate_summary_report(results, args.output_dir)
    report_file = os.path.join(args.output_dir, "eval_summary.md")

    os.makedirs(args.output_dir, exist_ok=True)
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n汇总报告已保存: {report_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
