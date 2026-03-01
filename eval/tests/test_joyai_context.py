#!/usr/bin/env python3
"""
JoyAI-LLM-Flash Context 大小测试
测试不同 context 长度下的性能表现
"""

import requests
import time
import json
from pathlib import Path

MODEL_URL = "http://localhost:8401"
MODEL_NAME = "JoyAI-LLM-Flash-Q4_K_M"
OUTPUT_FILE = Path("/mnt/volume3/llama_cpp/eval_results/stage1/joyai_context_test.jsonl")


def generate_prompt(tokens: int) -> str:
    """生成大约指定 token 数的 prompt"""
    base_text = "测试文本。这是一段用于测试的中文文本。我们需要生成足够长的内容来测试不同的context长度。"
    multiplier = max(1, tokens // 10)
    return base_text * multiplier


def test_context_length(ctx_length: int) -> dict:
    """测试指定的 context 长度"""
    print(f"\n{'='*60}")
    print(f"Testing context length: {ctx_length}")
    print(f"{'='*60}")

    prompt = generate_prompt(ctx_length)

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1,
        "temperature": 0.0
    }

    start_time = time.time()

    try:
        response = requests.post(
            f"{MODEL_URL}/v1/chat/completions",
            json=payload,
            timeout=300
        )
        response.raise_for_status()
        elapsed = (time.time() - start_time) * 1000

        data = response.json()
        usage = data.get('usage', {})
        timings = data.get('timings', {})

        prompt_tokens = usage.get('prompt_tokens', 0)
        prompt_ms = timings.get('prompt_ms', elapsed)
        prompt_tps = prompt_tokens / (prompt_ms / 1000) if prompt_ms > 0 else 0

        result = {
            "ctx_length": ctx_length,
            "success": True,
            "prompt_tokens": prompt_tokens,
            "prompt_ms": prompt_ms,
            "prompt_tps": prompt_tps,
            "elapsed_ms": elapsed,
            "timings": timings
        }

        print(f"  Success!")
        print(f"  Prompt tokens: {prompt_tokens}")
        print(f"  Prompt time: {prompt_ms:.1f} ms")
        print(f"  Prompt speed: {prompt_tps:.1f} t/s")

        return result

    except Exception as e:
        elapsed = (time.time() - start_time) * 1000
        print(f"  Failed: {e}")
        return {
            "ctx_length": ctx_length,
            "success": False,
            "error": str(e),
            "elapsed_ms": elapsed
        }


def main():
    print("="*60)
    print("JoyAI-LLM-Flash Context 大小测试")
    print("="*60)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # 测试的 context 长度（JoyAI 支持到 16384）
    ctx_lengths = [
        512, 1024, 2048, 4096, 8192, 16384
    ]

    results = []

    for ctx_len in ctx_lengths:
        result = test_context_length(ctx_len)
        results.append(result)

        # 保存结果
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(result, ensure_ascii=False) + '\n')

        if not result['success']:
            print(f"\nStopping at {ctx_len} due to failure")
            break

    print("\n" + "="*60)
    print("Summary")
    print("="*60)

    print(f"\n{'Context':>10} | {'Success':>7} | {'Tokens':>8} | {'Time(ms)':>10} | {'T/s':>8}")
    print("-" * 60)

    for r in results:
        if r['success']:
            print(f"{r['ctx_length']:>10} | {'YES':>7} | {r['prompt_tokens']:>8} | {r['prompt_ms']:>10.1f} | {r['prompt_tps']:>8.1f}")
        else:
            print(f"{r['ctx_length']:>10} | {'NO':>7} | {'-':>8} | {'-':>10} | {'-':>8}")

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
