#!/usr/bin/env python3
"""
模型综合能力评估脚本
- 基础能力 (C-Eval, CMMLU, MMLU, GSM8K)
- 代码能力 (HumanEval, MBPP)
- 工具使用能力
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from golden_benchmarks import compare_with_golden, print_comparison


def run_llm_eval(model_path: str, model_name: str, output_dir: str, base_url: str = "http://localhost:8401") -> dict:
    """运行基础LLM评估"""
    print("\n" + "=" * 60)
    print("1. 基础能力评估 (GSM8K, HumanEval, MBPP)")
    print("=" * 60)

    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    eval_llm_path = os.path.join(script_dir, "eval_llm.py")

    cmd = [
        sys.executable, eval_llm_path,
        "--model-path", model_path,
        "--model-name", model_name,
        "--output-dir", output_dir,
        "--base-url", base_url,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        if result.returncode != 0:
            print(f"基础评估出错: {result.stderr}")
            return {"error": result.stderr}

        # 读取结果文件
        results_file = os.path.join(output_dir, "results.json")
        if os.path.exists(results_file):
            with open(results_file, 'r') as f:
                return json.load(f)
        return {"status": "completed"}
    except Exception as e:
        return {"error": str(e)}


def run_tools_eval(model_url: str, model_name: str, output_dir: str) -> dict:
    """运行工具使用能力评估"""
    print("\n" + "=" * 60)
    print("2. 工具使用能力评估")
    print("=" * 60)

    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    eval_tools_path = os.path.join(script_dir, "eval_tools_capability.py")

    cmd = [
        sys.executable, eval_tools_path,
        "--model-url", model_url,
        "--model-name", model_name,
        "--output-dir", output_dir,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        # 读取报告文件
        report_file = os.path.join(output_dir, f"{model_name}_tools_eval.md")
        if os.path.exists(report_file):
            with open(report_file, 'r') as f:
                content = f.read()
            # 提取准确率
            if "准确率" in content:
                return {"status": "completed", "report": report_file}
        return {"status": "unknown"}
    except Exception as e:
        return {"error": str(e)}


def generate_comprehensive_report(
    model_name: str,
    model_path: str,
    llm_results: dict,
    tools_results: dict,
    output_dir: str
) -> str:
    """生成综合评估报告"""

    report = f"""# {model_name} 综合能力评估报告

> **评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> **模型路径**: {model_path}

---

## 评估项目

| 能力维度 | 评估工具 | 状态 |
|---------|---------|------|
| 基础能力 | lm-eval-harness | {'✅' if 'error' not in llm_results else '❌'} |
| 代码生成 | HumanEval, MBPP | {'✅' if 'error' not in llm_results else '❌'} |
| 工具使用 | 自定义测试集 | {'✅' if 'error' not in tools_results else '❌'} |

---

## 详细报告

### 1. 基础能力评估

"""

    # 添加LLM评估结果
    if 'error' in llm_results:
        report += f"**错误**: {llm_results['error']}\n\n"
    else:
        report += "见独立报告文件。\n\n"

    report += f"""### 2. 工具使用能力评估

"""

    if 'error' in tools_results:
        report += f"**错误**: {tools_results['error']}\n\n"
    else:
        report += f"报告文件: `{tools_results.get('report', 'N/A')}`\n\n"

    report += f"""---

## 与黄金标杆对比

基础能力评测完成后，请运行对比脚本:

```bash
python3 -c "
from golden_benchmarks import compare_with_golden, print_comparison
results = {{'C-Eval': 0.75, 'GSM8K': 0.80}}  # 填入实际结果
comparison = compare_with_golden('LLM', results)
print_comparison(comparison)
"
```

---

## 结论

待填写...

"""

    return report


def main():
    parser = argparse.ArgumentParser(description="模型综合能力评估")
    parser.add_argument("--model-path", required=True, help="模型路径")
    parser.add_argument("--model-name", default=None, help="模型名称")
    parser.add_argument("--model-url", default="http://localhost:8401", help="模型API地址")
    parser.add_argument("--output-dir", default="./eval_results", help="输出目录")
    parser.add_argument("--skip-tools", action="store_true", help="跳过工具使用评估")

    args = parser.parse_args()

    model_name = args.model_name or os.path.basename(args.model_path).replace(".gguf", "")
    output_dir = os.path.join(args.output_dir, model_name)
    os.makedirs(output_dir, exist_ok=True)

    print("=" * 60)
    print(f"综合能力评估: {model_name}")
    print("=" * 60)
    print(f"模型路径: {args.model_path}")
    print(f"模型API: {args.model_url}")
    print(f"输出目录: {output_dir}")

    # 1. 基础能力评估
    llm_results = run_llm_eval(args.model_path, model_name, output_dir, args.model_url)

    # 2. 工具使用评估
    tools_results = {}
    if not args.skip_tools:
        tools_results = run_tools_eval(args.model_url, model_name, output_dir)
    else:
        print("\n跳过工具使用评估 (--skip-tools)")

    # 生成综合报告
    report = generate_comprehensive_report(
        model_name, args.model_path, llm_results, tools_results, output_dir
    )

    report_file = os.path.join(output_dir, f"{model_name}_comprehensive_eval.md")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    print("\n" + "=" * 60)
    print("评估完成!")
    print(f"综合报告: {report_file}")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    sys.exit(main())
