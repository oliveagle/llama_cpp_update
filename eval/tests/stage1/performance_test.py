#!/usr/bin/env python3
"""
Stage 1 - 性能基准测试
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, Any


def run_performance_test(
    model_name: str,
    base_url: str = "http://localhost:8400",
    ctx_size: int = 8192,
) -> Dict[str, Any]:
    """
    运行性能基准测试

    Args:
        model_name: 模型名称
        base_url: API 地址
        ctx_size: Context 大小

    Returns:
        性能测试结果
    """
    results = {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "ctx_size": ctx_size,
        "tests": []
    }

    # 测试 1: Prefill 速度 (短 prompt)
    print("测试 1: Prefill 速度 (短 prompt)...")
    test1 = test_prefill_speed(base_url, model_name, "你好")
    results["tests"].append(test1)
    print(f"  结果：{test1.get('prefill_speed', 0):.0f} tokens/s")

    # 测试 2: Prefill 速度 (长 prompt)
    print("测试 2: Prefill 速度 (长 prompt 8K)...")
    long_prompt = "你好 " * 4000  # 约 8K tokens
    test2 = test_prefill_speed(base_url, model_name, long_prompt)
    results["tests"].append(test2)
    print(f"  结果：{test2.get('prefill_speed', 0):.0f} tokens/s")

    # 测试 3: 生成速度
    print("测试 3: 生成速度...")
    test3 = test_generation_speed(base_url, model_name, "写一篇 100 字的文章")
    results["tests"].append(test3)
    print(f"  结果：{test3.get('generation_speed', 0):.1f} tokens/s")

    # 计算汇总
    results["summary"] = calculate_summary(results["tests"])

    return results


def test_prefill_speed(
    base_url: str,
    model_name: str,
    prompt: str,
    max_tokens: int = 10
) -> Dict[str, Any]:
    """测试预填充速度"""
    url = f"{base_url}/v1/chat/completions"

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0,
        "stream": False,
    }

    start = time.perf_counter()
    try:
        resp = requests.post(url, json=payload, timeout=60)
        elapsed = time.perf_counter() - start

        if resp.status_code == 200:
            data = resp.json()
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            prefill_speed = prompt_tokens / elapsed if elapsed > 0 else 0

            return {
                "name": "prefill_speed",
                "prompt_length": len(prompt),
                "prompt_tokens": prompt_tokens,
                "elapsed_seconds": elapsed,
                "prefill_speed": prefill_speed,
                "success": True,
            }
        else:
            return {
                "name": "prefill_speed",
                "success": False,
                "error": f"HTTP {resp.status_code}",
            }
    except Exception as e:
        return {
            "name": "prefill_speed",
            "success": False,
            "error": str(e),
        }


def test_generation_speed(
    base_url: str,
    model_name: str,
    prompt: str,
    max_tokens: int = 200
) -> Dict[str, Any]:
    """测试生成速度"""
    url = f"{base_url}/v1/chat/completions"

    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "stream": False,
    }

    start = time.perf_counter()
    try:
        resp = requests.post(url, json=payload, timeout=120)
        elapsed = time.perf_counter() - start

        if resp.status_code == 200:
            data = resp.json()
            usage = data.get("usage", {})
            completion_tokens = usage.get("completion_tokens", 0)
            generation_speed = completion_tokens / elapsed if elapsed > 0 else 0

            return {
                "name": "generation_speed",
                "prompt": prompt[:50] + "..." if len(prompt) > 50 else prompt,
                "completion_tokens": completion_tokens,
                "elapsed_seconds": elapsed,
                "generation_speed": generation_speed,
                "success": True,
            }
        else:
            return {
                "name": "generation_speed",
                "success": False,
                "error": f"HTTP {resp.status_code}",
            }
    except Exception as e:
        return {
            "name": "generation_speed",
            "success": False,
            "error": str(e),
        }


def calculate_summary(tests: list) -> Dict[str, float]:
    """计算汇总统计"""
    prefill_speeds = [t.get("prefill_speed", 0) for t in tests if t.get("prefill_speed")]
    generation_speeds = [t.get("generation_speed", 0) for t in tests if t.get("generation_speed")]

    return {
        "avg_prefill_speed": sum(prefill_speeds) / len(prefill_speeds) if prefill_speeds else 0,
        "avg_generation_speed": sum(generation_speeds) / len(generation_speeds) if generation_speeds else 0,
        "total_tests": len(tests),
        "successful_tests": sum(1 for t in tests if t.get("success")),
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stage 1 性能测试")
    parser.add_argument("--model", type=str, required=True, help="模型名称")
    parser.add_argument("--url", type=str, default="http://localhost:8400", help="API 地址")
    parser.add_argument("--ctx-size", type=int, default=8192, help="Context 大小")

    args = parser.parse_args()

    results = run_performance_test(
        model_name=args.model,
        base_url=args.url,
        ctx_size=args.ctx_size,
    )

    print("\n" + "="*60)
    print("性能测试结果汇总")
    print("="*60)
    print(f"模型：{args.model}")
    print(f"平均预填充速度：{results['summary']['avg_prefill_speed']:.0f} tokens/s")
    print(f"平均生成速度：{results['summary']['avg_generation_speed']:.1f} tokens/s")
