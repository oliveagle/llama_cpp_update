#!/usr/bin/env python3
"""
完整测试：分别测试 Prompt Processing 和 Token Generation
"""

import os
import sys
import subprocess
import time
import requests

# 配置
MODEL_PATH = "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-27B-GGUF/Qwen3.5-27B-Q4_K_M.gguf"
LLAMA_SERVER = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
BASE_PORT = 8700


def start_server(ctx_size, port):
    """启动服务器"""
    cmd = [
        LLAMA_SERVER,
        "-m", MODEL_PATH,
        "--ctx-size", str(ctx_size),
        "--n-gpu-layers", "99",
        "--port", str(port),
        "--flash-attn", "on"
    ]

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"

    process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # 等待就绪
    base_url = f"http://localhost:{port}"
    for _ in range(120):
        try:
            r = requests.get(f"{base_url}/health", timeout=1)
            if r.status_code == 200:
                return process, base_url
        except:
            pass
        time.sleep(1)

    process.terminate()
    return None, None


def test_prompt_processing(base_url, word_count):
    """测试 Prompt Processing - 长prompt，只生成1个token"""
    prompt = "测试 " * (word_count + 10)

    payload = {
        "model": "test",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1,
        "temperature": 0.0
    }

    start = time.time()
    response = requests.post(f"{base_url}/v1/chat/completions", json=payload, timeout=600)
    elapsed = time.time() - start

    data = response.json()
    usage = data.get('usage', {})
    timings = data.get('timings', {})

    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0)

    # 用 llama.cpp 返回的 prompt_ms 计算更准确
    tps = 0
    if timings and timings.get('prompt_ms', 0) > 0:
        tps = prompt_tokens / (timings['prompt_ms'] / 1000)

    return {
        "type": "prompt_processing",
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_time_ms": elapsed * 1000,
        "prompt_ms": timings.get('prompt_ms', 0) if timings else 0,
        "tps": tps,
    }


def test_token_generation(base_url, prompt_words, max_tokens):
    """测试 Token Generation - 短prompt，生成多个token"""
    prompt = "测试 " * (prompt_words + 10)

    payload = {
        "model": "test",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    start = time.time()
    response = requests.post(f"{base_url}/v1/chat/completions", json=payload, timeout=900)
    elapsed = time.time() - start

    data = response.json()
    usage = data.get('usage', {})
    timings = data.get('timings', {})

    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0)

    # 用 llama.cpp 返回的 predicted_ms 计算
    tps = 0
    if timings and timings.get('predicted_ms', 0) > 0:
        tps = completion_tokens / (timings['predicted_ms'] / 1000)

    return {
        "type": "token_generation",
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_time_ms": elapsed * 1000,
        "predicted_ms": timings.get('predicted_ms', 0) if timings else 0,
        "tps": tps,
    }


def test_ctx_size(ctx_size):
    """完整测试一个 ctx-size"""
    port = BASE_PORT + ctx_size // 1000
    print(f"\n{'='*80}")
    print(f"ctx-size: {ctx_size}")
    print('='*80)

    # 启动服务器
    process, base_url = start_server(ctx_size, port)
    if not process:
        print("  启动失败")
        return None

    try:
        # 测试1: Prompt Processing - 约 ctx_size 的 90%
        prompt_words = (ctx_size * 9 // 10) // 2
        print(f"\n  [Prompt Processing] 测试 ~{ctx_size * 9 // 10} tokens")
        r1 = test_prompt_processing(base_url, prompt_words)
        print(f"      Prompt: {r1['prompt_tokens']:5d} tokens | {r1['prompt_ms']:8.1f} ms | {r1['tps']:8.1f} t/s")

        # 测试2: Token Generation - 短prompt，生成 256 tokens
        print(f"\n  [Token Generation] 测试生成 256 tokens")
        r2 = test_token_generation(base_url, 50, 256)
        print(f"      Prompt: {r2['prompt_tokens']:4d} tokens | Gen: {r2['completion_tokens']:4d} tokens | {r2['predicted_ms']:8.1f} ms | {r2['tps']:6.1f} t/s")

        # 测试3: Token Generation - 生成 512 tokens
        print(f"\n  [Token Generation] 测试生成 512 tokens")
        r3 = test_token_generation(base_url, 50, 512)
        print(f"      Prompt: {r3['prompt_tokens']:4d} tokens | Gen: {r3['completion_tokens']:4d} tokens | {r3['predicted_ms']:8.1f} ms | {r3['tps']:6.1f} t/s")

        return {
            "ctx_size": ctx_size,
            "prompt_processing": r1,
            "token_gen_256": r2,
            "token_gen_512": r3,
        }

    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except:
            process.kill()


def main():
    print("="*80)
    print("完整测试 - Prompt Processing + Token Generation")
    print("="*80)

    results = []

    for ctx_size in [8192, 16384, 32768, 65536]:
        r = test_ctx_size(ctx_size)
        if r:
            results.append(r)
        time.sleep(3)

    # 总结
    print("\n" + "="*80)
    print("总结")
    print("="*80)

    print("\n[1] Prompt Processing (冷启动，吞进去的速度):")
    print(f"{'ctx_size':>8} | {'tokens':>8} | {'ms':>10} | {'TPS':>10}")
    print("-"*55)
    for r in results:
        pp = r['prompt_processing']
        print(f"{r['ctx_size']:8d} | {pp['prompt_tokens']:8d} | {pp['prompt_ms']:10.1f} | {pp['tps']:10.1f}")

    print("\n[2] Token Generation (吐出来的速度):")
    print(f"{'ctx_size':>8} | {'gen 256':>10} | {'gen 512':>10}")
    print("-"*40)
    for r in results:
        t256 = r['token_gen_256']['tps']
        t512 = r['token_gen_512']['tps']
        print(f"{r['ctx_size']:8d} | {t256:10.1f} | {t512:10.1f}")

    print("\n详细说明:")
    print("  - Prompt Processing: 长prompt, 生成1个token - 测量吞入速度")
    print("  - Token Generation: 短prompt, 生成256/512 tokens - 测量输出速度")

    return 0


if __name__ == "__main__":
    sys.exit(main())
