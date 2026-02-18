#!/usr/bin/env python3
"""
256K Context Window 测试脚本 (Extended Timeout)
测试阶梯: 32K, 48K, 64K, 96K, 128K (600s timeout)

Usage:
    python3 test_context_256k.py --model-url http://localhost:8400 --model-name MODEL
"""

import argparse
import json
import time
import requests
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# 256K 测试阶梯
test_steps = [32768, 49152, 65536, 98304, 131072]

def generate_context(target_tokens: int) -> Tuple[str, str]:
    """生成指定长度的上下文（使用"大海捞针"方法）"""
    needle = "【重要信息：1970年诺贝尔物理学奖得主是汉内斯·阿尔文】"
    needle_tokens = len(needle) // 4
    remaining_tokens = target_tokens - needle_tokens - 100
    char_count = remaining_tokens * 4
    filler_text = "这是一段用于测试长上下文能力的填充文本。其中包含各种信息和数据，用于验证模型是否能够正确处理长序列输入。"
    repeats = (char_count // len(filler_text)) + 1
    haystack = (filler_text * repeats)[:char_count]
    mid_pos = len(haystack) // 2
    context = haystack[:mid_pos] + needle + haystack[mid_pos:]
    prompt = f"""以下是一些背景信息，请仔细阅读：

{context}

请回答：1970年诺贝尔物理学奖得主是谁？只回答人名。"""
    expected = "汉内斯·阿尔文"
    return prompt, expected

def test_context_size(
    model: str,
    base_url: str,
    target_tokens: int,
    timeout: int = 600
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
    output_dir: str = "./eval_results/vulkan/context_256k",
    timeout: int = 600
) -> Dict:
    """运行 256K context 阶梯测试"""
    os.makedirs(output_dir, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"256K Context Window 测试: {model}")
    print(f"{'='*60}")
    print(f"测试阶梯: {test_steps}")
    print(f"测试端点: {base_url}")
    print(f"超时时间: {timeout}s")
    print()

    results = {
        "model": model,
        "timestamp": datetime.now().isoformat(),
        "base_url": base_url,
        "timeout": timeout,
        "tests": [],
        "max_successful": 0,
        "max_correct": 0,
    }

    for step in test_steps:
        print(f"  测试 {step//1024}K context... ", end="", flush=True)
        result = test_context_size(model, base_url, step, timeout)
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
            print(f"⏱️  超时 ({timeout}s)")
            break
        else:
            print(f"❌ {result.get('error', 'Unknown')[:50]}")
            break

    # 保存结果
    json_file = os.path.join(output_dir, f"{model.replace('/', '_')}_256k.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # 生成报告
    report_file = os.path.join(output_dir, f"{model.replace('/', '_')}_256k_report.md")
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
        f.write(f"# 256K Context Window 测试报告 - {results['model']}\n\n")
        f.write(f"> **测试时间**: {results['timestamp']}\n")
        f.write(f"> **测试端点**: {results['base_url']}\n")
        f.write(f"> **超时时间**: {results.get('timeout', 600)}s\n")
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
                time_str = f"超时({results.get('timeout', 600)}s)"
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
    parser = argparse.ArgumentParser(description="256K Context Window 测试")
    parser.add_argument("--model-url", default="http://localhost:8400", help="模型API地址")
    parser.add_argument("--model-name", required=True, help="模型名称")
    parser.add_argument("--timeout", type=int, default=600, help="超时时间(秒)")
    parser.add_argument("--output-dir", default="./eval_results/vulkan/context_256k", help="输出目录")

    args = parser.parse_args()

    run_context_tests(
        model=args.model_name,
        base_url=args.model_url,
        output_dir=args.output_dir,
        timeout=args.timeout
    )

if __name__ == "__main__":
    main()
