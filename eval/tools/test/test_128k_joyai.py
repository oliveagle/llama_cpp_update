#!/usr/bin/env python3
"""
先用 JoyAI-Flash 测试 128K Context 可行性
因为模型确认存在且支持长 context
"""

import requests
import time
import json
import subprocess
from datetime import datetime

MODEL_URL = "http://localhost:8401"
MODEL_NAME = "JoyAI-LLM-Flash-Q4_K_M"

# 测试梯度到 128K
CONTEXT_STEPS = [16384, 24576, 32768, 49152, 65536, 98304, 131072]

def get_gpu_memory():
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(", ")
            return {
                "memory_used_mb": int(parts[0]),
                "memory_total_mb": int(parts[1]),
                "gpu_util": int(parts[2])
            }
    except:
        pass
    return None

def generate_prompt(target_tokens: int) -> str:
    char_count = target_tokens * 3
    base_text = "这是一个用于测试大语言模型长上下文处理能力的标准测试文本。我们需要生成足够长的内容来填充指定的上下文窗口大小，以便准确测量模型在不同上下文长度下的预填充速度和生成速度。"
    repeat_times = (char_count // len(base_text)) + 1
    return (base_text * repeat_times)[:char_count]

def test_context(context_size: int):
    print(f"\n{'='*60}")
    print(f"测试 Context: {context_size:,} tokens ({context_size//1024}K)")
    print(f"{'='*60}")

    prompt = generate_prompt(context_size)

    gpu_before = get_gpu_memory()
    if gpu_before:
        print(f"  GPU: {gpu_before['memory_used_mb']}MB / {gpu_before['memory_total_mb']}MB")

    url = f"{MODEL_URL}/v1/chat/completions"
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 128,
        "temperature": 0.7
    }

    start = time.time()
    try:
        resp = requests.post(url, json=payload, timeout=600)
        elapsed = time.time() - start

        gpu_after = get_gpu_memory()

        if resp.status_code == 200:
            data = resp.json()
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            finish_reason = data['choices'][0].get('finish_reason', 'unknown')

            prompt_speed = prompt_tokens / elapsed if elapsed > 0 else 0
            gen_speed = completion_tokens / elapsed if elapsed > 0 else 0

            print(f"  ✅ 成功!")
            print(f"     Prompt: {prompt_tokens:,} tokens")
            print(f"     Completion: {completion_tokens} tokens")
            print(f"     耗时: {elapsed:.2f}s")
            print(f"     生成速度: {gen_speed:.2f} t/s")
            print(f"     Finish: {finish_reason}")
            if gpu_after:
                print(f"     显存: {gpu_after['memory_used_mb']}MB")

            return {
                "context": context_size,
                "prompt_tokens": prompt_tokens,
                "gen_tokens": completion_tokens,
                "speed": round(gen_speed, 2),
                "time": round(elapsed, 2),
                "finish": finish_reason,
                "status": "success"
            }
        else:
            print(f"  ❌ HTTP {resp.status_code}")
            return {"context": context_size, "status": f"HTTP_{resp.status_code}"}

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {"context": context_size, "status": "error", "error": str(e)}

def main():
    print("="*60)
    print("JoyAI-Flash 128K Context 可行性测试")
    print("="*60)
    print(f"模型: {MODEL_NAME}")
    print("目的: 验证 V100 + llama.cpp 能否支持 128K context")
    print("="*60)

    results = []
    for ctx in CONTEXT_STEPS:
        result = test_context(ctx)
        results.append(result)

        if result.get("status") != "success":
            print(f"\n  在 {ctx} 停止测试")
            break

    # 汇总
    success = [r for r in results if r.get("status") == "success"]
    print(f"\n{'='*60}")
    print("测试结果")
    print(f"{'='*60}")
    print(f"  成功: {len(success)}/{len(results)}")
    if success:
        max_ctx = max(r['context'] for r in success)
        print(f"  最大支持: {max_ctx:,} tokens ({max_ctx//1024}K)")

        if max_ctx >= 131072:
            print("  🎉 成功支持 128K!")
        elif max_ctx >= 65536:
            print("  ✅ 支持 64K")
        elif max_ctx >= 32768:
            print("  ⚠️  支持 32K")
        else:
            print("  ❌ 32K 以下")

if __name__ == "__main__":
    main()
