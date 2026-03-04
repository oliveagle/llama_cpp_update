#!/usr/bin/env python3
"""
用统一的方法重新测试 - 用英文避免 tokenizer 问题
"""

import os
import sys
import subprocess
import time
import requests

# 配置
MODEL_PATH = "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-27B-GGUF/Qwen3.5-27B-Q4_K_M.gguf"
LLAMA_SERVER = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
PORT = 8408
BASE_URL = f"http://localhost:{PORT}"


def start_server(ctx_size):
    """启动服务器"""
    cmd = [
        LLAMA_SERVER,
        "-m", MODEL_PATH,
        "--ctx-size", str(ctx_size),
        "--n-gpu-layers", "99",
        "--port", str(PORT),
        "--flash-attn", "on"
    ]

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"

    process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    for _ in range(120):
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=1)
            if r.status_code == 200:
                return process
        except:
            pass
        time.sleep(1)

    process.terminate()
    return None


def test_prompt(word_count):
    """测试指定词数的 prompt"""
    # 用简单的英文重复
    words = "Hello world. " * word_count
    prompt = "Please answer the following question: " + words

    payload = {
        "model": "test",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1,
        "temperature": 0.0
    }

    start = time.time()
    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, timeout=600)
    elapsed = time.time() - start

    data = response.json()
    usage = data.get('usage', {})
    timings = data.get('timings', {})

    actual_tokens = usage.get('prompt_tokens', 0)

    # 两种计算方式
    tps_total = actual_tokens / elapsed if elapsed > 0 and actual_tokens > 0 else 0
    tps_prompt = 0
    if timings and timings.get('prompt_ms', 0) > 0 and actual_tokens > 0:
        tps_prompt = actual_tokens / (timings['prompt_ms'] / 1000)

    return {
        "word_count": word_count,
        "actual": actual_tokens,
        "elapsed_ms": elapsed * 1000,
        "prompt_ms": timings.get('prompt_ms', 0) if timings else 0,
        "tps_total": tps_total,
        "tps_prompt": tps_prompt
    }


def main():
    print("="*70)
    print("统一测试 - 不同 ctx-size 下的性能")
    print("="*70)

    results = []

    for ctx_size in [8192, 16384, 32768, 65536]:
        print(f"\n{'='*70}")
        print(f"ctx-size: {ctx_size}")
        print('='*70)

        process = start_server(ctx_size)
        if not process:
            print("启动失败")
            continue

        try:
            # 预热
            print("  预热...")
            test_prompt(100)

            # 测试 - 用足够的词数达到目标 token 数
            # 英文单词:token 比例大概 1:1.3
            target_tokens = min(ctx_size - 500, 64000)
            word_count = int(target_tokens / 1.5)
            print(f"  测试词数: {word_count}, 目标 tokens: ~{target_tokens}")

            r = test_prompt(word_count)

            print(f"\n  结果:")
            print(f"    实际 tokens: {r['actual']}")
            print(f"    总时间: {r['elapsed_ms']:.1f} ms")
            print(f"    prompt_ms: {r['prompt_ms']:.1f} ms")
            print(f"    TPS (总时间): {r['tps_total']:.1f}")
            print(f"    TPS (prompt_ms): {r['tps_prompt']:.1f}")

            results.append({
                "ctx_size": ctx_size,
                "actual_tokens": r['actual'],
                "tps_total": r['tps_total'],
                "tps_prompt": r['tps_prompt'],
                "elapsed_ms": r['elapsed_ms'],
                "prompt_ms": r['prompt_ms']
            })

        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except:
                process.kill()

        time.sleep(2)

    # 总结
    print("\n" + "="*70)
    print("总结")
    print("="*70)
    print()
    print(f"{'ctx_size':>8} {'tokens':>8} {'TPS(total)':>12} {'TPS(prompt)':>12} {'elapsed(ms)':>12} {'prompt(ms)':>12}")
    print("-"*80)
    for r in results:
        print(f"{r['ctx_size']:8d} {r['actual_tokens']:8d} {r['tps_total']:12.1f} {r['tps_prompt']:12.1f} {r['elapsed_ms']:12.1f} {r['prompt_ms']:12.1f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
