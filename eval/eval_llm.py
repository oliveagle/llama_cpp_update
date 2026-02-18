#!/usr/bin/env python3
"""
LLM 综合能力评估脚本
使用 lm-eval-harness 进行标准化评测
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Optional

# 添加eval目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from golden_benchmarks import (
    get_golden_benchmark,
    compare_with_golden,
    print_comparison,
    get_recommended_eval_tasks,
)

# 默认评测任务 (所有LLM必须测试的项目)
# 注意: 使用 generate_until 模式的任务，与 llama.cpp API 兼容
DEFAULT_TASKS = [
    "gsm8k",            # 数学推理 (generate_until 模式)
    "humaneval",        # 代码生成 (所有模型必测)
    "mbpp",             # 多语言代码 (所有模型必测)
    # 注意: ceval/cmmlu/mmlu 需要 loglikelihood 模式，与 llama.cpp 不兼容
    # 这些任务需要使用其他方式评估
]

# 需要 tokenizer 的任务配置
TASK_TOKENIZERS = {
    "gsm8k": "Qwen/Qwen2.5-7B-Instruct",
    "humaneval": "Qwen/Qwen2.5-7B-Instruct",
    "mbpp": "Qwen/Qwen2.5-7B-Instruct",
}

# 工具使用评估 (通过自定义方式，因为lm-eval不支持直接测试工具调用)
TOOLS_EVAL_SCRIPT = "eval_tools_capability.py"


def check_lm_eval() -> bool:
    """检查lm-eval是否安装"""
    try:
        subprocess.run(["lm-eval", "--help"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def run_lm_eval(
    tasks: List[str],
    batch_size: int = 1,
    num_fewshot: Optional[int] = None,
    output_dir: str = "./eval_results",
    model_name: str = "model",
    base_url: str = "http://localhost:8401",
) -> Dict:
    """
    运行lm-eval评测
    使用 local-completions 模型类型，与 llama.cpp server API 兼容

    Args:
        tasks: 评测任务列表
        batch_size: 批处理大小
        num_fewshot: few-shot数量
        output_dir: 输出目录
        model_name: API 调用使用的模型名称
        base_url: llama.cpp server 地址

    Returns:
        评测结果
    """
    if not check_lm_eval():
        print("错误: lm-eval未安装")
        print("请运行: pip install lm-eval")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # 确定 tokenizer
    tokenizer = "Qwen/Qwen2.5-7B-Instruct"  # 默认 tokenizer

    # 构建命令 (使用 local-completions 模型类型，兼容 llama.cpp)
    cmd = [
        sys.executable, "-m", "lm_eval",
        "--model", "local-completions",
        "--model_args", f"model={model_name},base_url={base_url}/v1/completions,num_concurrent=1,max_retries=3,tokenized_requests=False,tokenizer={tokenizer}",
        "--tasks", ",".join(tasks),
        "--batch_size", str(batch_size),
        "--output_path", output_dir,
    ]

    if num_fewshot is not None:
        cmd.extend(["--num_fewshot", str(num_fewshot)])

    print(f"运行评测: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)

        if result.returncode != 0:
            print(f"评测失败: {result.stderr}")
            return {"error": result.stderr}

        # 解析结果
        return parse_lm_eval_output(result.stdout, output_dir)

    except subprocess.TimeoutExpired:
        print("评测超时 (1小时)")
        return {"error": "timeout"}
    except Exception as e:
        print(f"评测出错: {e}")
        return {"error": str(e)}


def parse_lm_eval_output(stdout: str, output_dir: str) -> Dict:
    """解析lm-eval输出"""
    # 读取结果文件
    results_file = os.path.join(output_dir, "results.json")

    if not os.path.exists(results_file):
        return {"raw_output": stdout}

    with open(results_file, 'r') as f:
        results = json.load(f)

    return results


def extract_key_metrics(results: Dict) -> Dict[str, float]:
    """
    提取关键指标

    Returns:
        {metric_name: value}
    """
    metrics = {}

    if "results" not in results:
        return metrics

    for task, data in results["results"].items():
        # 常见的指标名
        for metric_name in ["acc", "acc_norm", "exact_match", "pass@1", "f1"]:
            if metric_name in data:
                metrics[task] = data[metric_name]
                break

    return metrics


def generate_report(
    model_name: str,
    model_path: str,
    results: Dict,
    comparison: Optional[Dict] = None,
) -> str:
    """生成评测报告"""

    report = f"""# {model_name} LLM能力评估报告

> **评测时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> **模型路径**: {model_path}

---

## 评测任务

"""

    if "error" in results:
        report += f"**评测失败**: {results['error']}\n"
        return report

    # 原始结果
    report += "## 原始评测结果\n\n```json\n"
    report += json.dumps(results, indent=2, ensure_ascii=False)
    report += "\n```\n\n"

    # 关键指标
    metrics = extract_key_metrics(results)
    if metrics:
        report += "## 关键指标\n\n| 任务 | 得分 |\n|------|------|\n"
        for task, score in metrics.items():
            report += f"| {task} | {score:.4f} |\n"

    # 与黄金标杆对比
    if comparison:
        report += "\n## 与黄金标杆对比\n\n"
        report += "| 指标 | 模型得分 | 黄金标杆 | 目标值 | 差距 | 状态 |\n"
        report += "|------|----------|----------|--------|------|------|\n"

        for metric, data in comparison.items():
            vs_baseline = data['vs_baseline_pct']
            sign = "+" if vs_baseline >= 0 else ""
            gap = f"{sign}{vs_baseline:.1f}%"

            if data['beats_baseline']:
                status = "🥇 超越"
            elif data['meets_target']:
                status = "✅ 达标"
            else:
                status = "❌ 未达标"

            report += f"| {metric} | {data['model_value']:.4f} | "
            report += f"{data['golden_baseline']:.4f} | {data['golden_target']:.4f} | "
            report += f"{gap} | {status} |\n"

    return report


def main():
    parser = argparse.ArgumentParser(description="LLM能力评估")
    parser.add_argument(
        "--model-path",
        type=str,
        required=True,
        help="模型路径或gguf文件路径",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=None,
        help="模型名称 (默认从路径提取)",
    )
    parser.add_argument(
        "--tasks",
        type=str,
        nargs="+",
        default=DEFAULT_TASKS,
        help=f"评测任务列表 (默认: {DEFAULT_TASKS})",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./eval_results",
        help="输出目录",
    )
    parser.add_argument(
        "--compare-golden",
        action="store_true",
        default=True,
        help="与黄金标杆对比",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1,
        help="批处理大小",
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8401",
        help="llama.cpp server 地址",
    )

    args = parser.parse_args()

    # 提取模型名称
    model_name = args.model_name or os.path.basename(args.model_path).replace(".gguf", "")

    # 任务已包含代码评测 (humaneval, mbpp 在 DEFAULT_TASKS 中)
    tasks = args.tasks.copy()

    print(f"=" * 60)
    print(f"LLM能力评估: {model_name}")
    print(f"=" * 60)
    print(f"模型路径: {args.model_path}")
    print(f"评测任务: {tasks}")
    print()

    # 运行评测
    results = run_lm_eval(
        tasks=tasks,
        batch_size=args.batch_size,
        output_dir=args.output_dir,
        model_name=model_name,
        base_url=args.base_url,
    )

    # 提取关键指标
    metrics = extract_key_metrics(results)

    # 与黄金标杆对比
    comparison = None
    if args.compare_golden and metrics:
        print("\n与黄金标杆对比...")
        comparison = compare_with_golden("LLM", metrics)
        print_comparison(comparison)

    # 生成报告
    report = generate_report(model_name, args.model_path, results, comparison)

    # 保存报告
    report_file = os.path.join(args.output_dir, f"{model_name}_eval_report.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n报告已保存: {report_file}")

    return 0 if "error" not in results else 1


if __name__ == "__main__":
    sys.exit(main())
