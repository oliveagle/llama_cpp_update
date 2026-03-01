#!/usr/bin/env python3
"""
探索 Qwen3-0.6B 突破 Context 16K 限制
目标: 128K context

测试梯度: 16K, 24K, 32K, 48K, 64K, 96K, 128K
"""

import requests
import time
import json
import subprocess
from datetime import datetime

MODEL_URL = "http://localhost:8401"
MODEL_NAME = "Qwen3-0.6B-Q4_0"

# 扩展测试梯度到 128K
CONTEXT_STEPS = [16384, 24576, 32768, 49152, 65536, 98304, 131072]

def get_gpu_memory():
    """获取 GPU 显存使用情况"""
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
    """生成指定token数量的prompt"""
    char_count = target_tokens * 3
    base_text = "这是一个用于测试大语言模型长上下文处理能力的标准测试文本。我们需要生成足够长的内容来填充指定的上下文窗口大小，以便准确测量模型在不同上下文长度下的预填充速度和生成速度。"
    repeat_times = (char_count // len(base_text)) + 1
    return (base_text * repeat_times)[:char_count]

def test_context(model_name: str, context_size: int, max_tokens: int = 128):
    """测试指定 context 大小"""
    print(f"\n{'='*60}")
    print(f"测试 Context: {context_size:,} tokens ({context_size//1024}K)")
    print(f"{'='*60}")

    prompt = generate_prompt(context_size)

    # 记录 GPU 状态
    gpu_before = get_gpu_memory()
    if gpu_before:
        print(f"  GPU 测试前: {gpu_before['memory_used_mb']}MB / {gpu_before['memory_total_mb']}MB")

    url = f"{MODEL_URL}/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.8,
        "top_k": 20
    }

    start_time = time.time()
    try:
        resp = requests.post(url, json=payload, timeout=600)
        elapsed = time.time() - start_time

        # 记录 GPU 状态
        gpu_after = get_gpu_memory()
        if gpu_after:
            print(f"  GPU 测试后: {gpu_after['memory_used_mb']}MB / {gpu_after['memory_total_mb']}MB")
            mem_increase = gpu_after['memory_used_mb'] - gpu_before['memory_used_mb']
            print(f"  显存增加: {mem_increase:+d} MB")

        if resp.status_code == 200:
            data = resp.json()
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)
            finish_reason = data['choices'][0].get('finish_reason', 'unknown')
            content = data['choices'][0]['message']['content']

            prompt_speed = prompt_tokens / elapsed if elapsed > 0 else 0
            gen_speed = completion_tokens / elapsed if elapsed > 0 else 0

            print(f"\n  ✅ 成功!")
            print(f"     Prompt tokens: {prompt_tokens:,}")
            print(f"     Completion tokens: {completion_tokens}")
            print(f"     总耗时: {elapsed:.2f}s")
            print(f"     预填充速度: {prompt_speed:.2f} t/s")
            print(f"     生成速度: {gen_speed:.2f} t/s")
            print(f"     Finish reason: {finish_reason}")
            print(f"     内容长度: {len(content)} 字符")

            return {
                "context_size": context_size,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "elapsed_sec": round(elapsed, 2),
                "prompt_speed_tps": round(prompt_speed, 2),
                "gen_speed_tps": round(gen_speed, 2),
                "finish_reason": finish_reason,
                "content_len": len(content),
                "status": "success"
            }
        else:
            print(f"  ❌ HTTP {resp.status_code}: {resp.text[:200]}")
            return {
                "context_size": context_size,
                "status": f"HTTP_{resp.status_code}",
                "error": resp.text[:200]
            }

    except requests.exceptions.Timeout:
        print(f"  ❌ 超时 (>600s)")
        return {
            "context_size": context_size,
            "status": "timeout",
            "error": "Request timeout"
        }
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        return {
            "context_size": context_size,
            "status": "error",
            "error": str(e)
        }

def main():
    print("="*60)
    print("Qwen3-0.6B 128K Context 探索")
    print("="*60)
    print(f"模型: {MODEL_NAME}")
    print(f"目标: 突破 16K 限制，探索 128K")
    print(f"测试梯度: {CONTEXT_STEPS}")
    print("="*60)

    results = []
    max_successful = 0

    for ctx in CONTEXT_STEPS:
        result = test_context(MODEL_NAME, ctx)
        results.append(result)

        if result.get("status") == "success":
            max_successful = ctx
            print(f"  ✓ 当前最大支持: {max_successful:,} tokens")
        else:
            print(f"  ✗ {ctx:,} tokens 失败")
            # 失败就停止，因为更大的肯定也会失败
            if ctx >= 32768:
                print(f"\n  在 {ctx:,} 停止测试 (已达极限或失败)")
                break

    # 生成报告
    print(f"\n{'='*60}")
    print("测试结果汇总")
    print(f"{'='*60}")

    success_results = [r for r in results if r.get("status") == "success"]

    if success_results:
        print(f"\n  成功测试:")
        print(f"  {'Context':>10} | {'生成速度':>10} | {'耗时':>8} | {'状态':>10}")
        print(f"  {'-'*10}-+-{'-'*10}-+-{'-'*8}-+-{'-'*10}")
        for r in success_results:
            print(f"  {r['context_size']:>10,} | {r['gen_speed_tps']:>10.2f} | {r['elapsed_sec']:>8.2f} | {'✅':>10}")

        max_ctx = max(r['context_size'] for r in success_results)
        print(f"\n  🎯 最大支持 Context: {max_ctx:,} tokens ({max_ctx//1024}K)")

        if max_ctx >= 131072:
            print(f"  🎉 成功突破 128K！")
        elif max_ctx >= 65536:
            print(f"  ✅ 达到 64K，接近目标")
        elif max_ctx >= 32768:
            print(f"  ⚠️  达到 32K，需要进一步优化")
        else:
            print(f"  ❌ 未能突破 16K 限制")

    # 保存结果
    output_file = f"eval_results/qwen3_0.6b_128k_explore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "model": MODEL_NAME,
            "timestamp": datetime.now().isoformat(),
            "max_context_supported": max_successful,
            "results": results
        }, f, indent=2)

    print(f"\n  结果保存: {output_file}")

if __name__ == "__main__":
    main()
