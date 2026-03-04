#!/usr/bin/env python3
"""
Context Window 阶梯测试脚本
测试阶梯: 4K, 8K, 12K, 16K, 24K, 32K, 48K, 64K, 96K, 128K
特殊模型可测试至 1M

Usage:
    python3 test_context_window.py --model-url http://localhost:8400 --model-name MODEL
"""

import argparse
import json
import time
import requests
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# Context 测试阶梯 (tokens)
CONTEXT_STEPS = [4096, 8192, 12288, 16384, 24576, 32768, 49152, 65536, 98304, 131072]

# 特殊模型可扩展至 1M
EXTENDED_STEPS = [262144, 524288, 1048576]


def generate_context(target_tokens: int) -> Tuple[str, str]:
    """
    生成指定长度的上下文（使用"大海捞针"方法）
    返回: (完整提示词, 需要找回的needle信息)
    """
    # 创建一个 needle（关键信息）
    needle = "【重要信息：1970年诺贝尔物理学奖得主是汉内斯·阿尔文】"
    needle_tokens = len(needle) // 4  # 粗略估算

    # 填充文本（每个token约4个字符）
    remaining_tokens = target_tokens - needle_tokens - 100  # 预留提示词token
    char_count = remaining_tokens * 4

    # 使用重复文本填充
    filler_text = "这是一段用于测试长上下文能力的填充文本。其中包含各种信息和数据，用于验证模型是否能够正确处理长序列输入。"
    repeats = (char_count // len(filler_text)) + 1
    haystack = (filler_text * repeats)[:char_count]

    # 将 needle 放在中间位置
    mid_pos = len(haystack) // 2
    context = haystack[:mid_pos] + needle + haystack[mid_pos:]

    # 构建提示词
    prompt = f"""以下是一些背景信息，请仔细阅读：

{context}

请回答：1970年诺贝尔物理学奖得主是谁？只回答人名。"""

    expected = "汉内斯·阿尔文"
    return prompt, expected


def test_context_size(
    model: str,
    base_url: str,
    target_tokens: int,
    timeout: int = 300
) -> Dict:
    """测试指定 context 大小"""
    prompt, expected = generate_context(target_tokens)

    url = f"{base_url}/v1/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 50,
        "temperature": 0.1,
    }

    try:
        start = time.time()
        resp = requests.post(url, json=payload, timeout=timeout)
        elapsed = time.time() - start

        if resp.status_code == 200:
            data = resp.json()
            content = data["choices"][0].get("message", {}).get("content", "")
            usage = data.get("usage", {})

            # 检查答案是否正确
            correct = expected in content or "阿尔文" in content

            return {
                "target_tokens": target_tokens,
                "actual_tokens": usage.get("prompt_tokens", 0),
                "status": "success",
                "response_time": elapsed,
                "correct": correct,
                "answer": content[:100],
            }
        else:
            return {
                "target_tokens": target_tokens,
                "status": "failed",
                "error": f"HTTP {resp.status_code}: {resp.text[:200]}",
            }
    except requests.exceptions.Timeout:
        return {
            "target_tokens": target_tokens,
            "status": "timeout",
            "error": f"Timeout after {timeout}s",
        }
    except Exception as e:
        return {
            "target_tokens": target_tokens,
            "status": "error",
            "error": str(e),
        }


def run_context_tests(
    model: str,
    base_url: str,
    extended: bool = False,
    output_dir: str = "./eval_results/context"
) -> Dict:
    """运行完整的 context 阶梯测试"""
    os.makedirs(output_dir, exist_ok=True)

    steps = CONTEXT_STEPS.copy()
    if extended:
        steps.extend(EXTENDED_STEPS)

    print(f"\n{'='*60}")
    print(f"Context Window 测试: {model}")
    print(f"{'='*60}")
    print(f"测试阶梯: {steps}")
    print(f"测试端点: {base_url}")
    print()

    results = {
        "model": model,
        "timestamp": datetime.now().isoformat(),
        "base_url": base_url,
        "tests": [],
        "max_successful": 0,
        "max_correct": 0,
    }

    for step in steps:
        print(f"  测试 {step//1024}K context... ", end="", flush=True)

        result = test_context_size(model, base_url, step)
        results["tests"].append(result)

        if result["status"] == "success":
            status_str = f"✅ {result['response_time']:.1f}s"
            if result.get("correct"):
                status_str += " (答案正确)"
                results["max_correct"] = step
            else:
                status_str += " (答案错误)"
            print(status_str)
            results["max_successful"] = step
        elif result["status"] == "timeout":
            print(f"⏱️  超时")
            break  # 后续更大的context肯定也会超时
        else:
            print(f"❌ {result.get('error', 'Unknown')[:50]}")
            break

    # 保存结果
    json_file = os.path.join(output_dir, f"{model.replace('/', '_')}_context.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # 生成报告
    report_file = os.path.join(output_dir, f"{model.replace('/', '_')}_context_report.md")
    generate_report(results, report_file)

    print(f"\n{'='*60}")
    print(f"最大成功 Context: {results['max_successful']//1024}K")
    print(f"最大正确召回: {results['max_correct']//1024}K")
    print(f"报告: {report_file}")
    print(f"{'='*60}")

    return results


def generate_report(results: Dict, report_file: str):
    """生成 Markdown 报告"""
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(f"# Context Window 测试报告 - {results['model']}\n\n")
        f.write(f"> **测试时间**: {results['timestamp']}\n")
        f.write(f"> **测试端点**: {results['base_url']}\n")
        f.write(f"> **测试 Agent**: gfx1151-Tester\n\n")
        f.write("---\n\n")

        f.write("## 测试结果\n\n")
        f.write("| Context 大小 | 状态 | 实际 Tokens | 响应时间 | 答案正确 |\n")
        f.write("|-------------|------|------------|----------|----------|\n")

        for test in results["tests"]:
            size = f"{test['target_tokens']//1024}K"
            if test["status"] == "success":
                status = "✅"
                actual = test.get("actual_tokens", 0)
                time_str = f"{test['response_time']:.1f}s"
                correct = "✅" if test.get("correct") else "❌"
            elif test["status"] == "timeout":
                status = "⏱️"
                actual = "-"
                time_str = "超时"
                correct = "-"
            else:
                status = "❌"
                actual = "-"
                time_str = "-"
                correct = "-"

            f.write(f"| {size} | {status} | {actual} | {time_str} | {correct} |\n")

        f.write("\n")
        f.write(f"**最大成功 Context**: {results['max_successful']//1024}K tokens\n\n")
        f.write(f"**最大正确召回**: {results['max_correct']//1024}K tokens\n\n")

        f.write("## 详细结果\n\n")
        f.write("```json\n")
        f.write(json.dumps(results, indent=2, ensure_ascii=False))
        f.write("\n```\n")


def main():
    parser = argparse.ArgumentParser(description="Context Window 阶梯测试")
    parser.add_argument("--model-url", default="http://localhost:8400", help="模型API地址")
    parser.add_argument("--model-name", required=True, help="模型名称")
    parser.add_argument("--extended", action="store_true", help="扩展测试至1M tokens")
    parser.add_argument("--output-dir", default="./eval_results/vulkan/context", help="输出目录")

    args = parser.parse_args()

    run_context_tests(
        model=args.model_name,
        base_url=args.model_url,
        extended=args.extended,
        output_dir=args.output_dir
    )


if __name__ == "__main__":
    main()
