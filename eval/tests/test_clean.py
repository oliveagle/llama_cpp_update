#!/usr/bin/env python3
"""
统一测试：每个 ctx-size 单独启动服务器，测试冷启动和预热后的速度
"""

import os
import sys
import subprocess
import time
import requests

# 配置
MODEL_PATH = "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-27B-GGUF/Qwen3.5-27B-Q4_K_M.gguf"
LLAMA_SERVER = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
BASE_PORT = 8500


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


def test_prompt(base_url, word_count):
    """测试指定词数"""
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
    actual = usage.get('prompt_tokens', 0)
    tps = actual / elapsed if elapsed > 0 and actual > 0 else 0

    return actual, elapsed, tps


def test_ctx_size(ctx_size):
    """测试一个 ctx-size 的冷启动和预热"""
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
        target_words = (ctx_size - 500) // 2

        # 测试1: 冷启动，直接测试目标长度
        print(f"\n  [1] 冷启动 - 直接测试 ~{ctx_size} tokens")
        actual1, elapsed1, tps1 = test_prompt(base_url, target_words)
        print(f"      {actual1:5d} tokens | {elapsed1*1000:8.1f} ms | {tps1:8.1f} t/s")

        # 测试2: 预热后，再测一次目标长度
        print(f"\n  [2] 预热 - 先测小长度")
        for small_words in [500, 1000, 2000, 4000]:
            test_prompt(base_url, small_words)
        print("      预热完成")

        print(f"\n  [3] 预热后 - 再测 ~{ctx_size} tokens")
        actual3, elapsed3, tps3 = test_prompt(base_url, target_words)
        print(f"      {actual3:5d} tokens | {elapsed3*1000:8.1f} ms | {tps3:8.1f} t/s")

        # 测试4: 再测一次，验证稳定性
        print(f"\n  [4] 再测一次 ~{ctx_size} tokens")
        actual4, elapsed4, tps4 = test_prompt(base_url, target_words)
        print(f"      {actual4:5d} tokens | {elapsed4*1000:8.1f} ms | {tps4:8.1f} t/s")

        return {
            "ctx_size": ctx_size,
            "cold": {"tokens": actual1, "ms": elapsed1*1000, "tps": tps1},
            "warm": {"tokens": actual3, "ms": elapsed3*1000, "tps": tps3},
            "warm2": {"tokens": actual4, "ms": elapsed4*1000, "tps": tps4},
        }

    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except:
            process.kill()


def main():
    print("="*80)
    print("统一测试 - 每个 ctx-size 单独启动，分别测试冷启动和预热")
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
    print()
    print(f"{'ctx_size':>8} | {'冷启动 TPS':>12} | {'预热后 TPS':>12} | {'提升':>8} |")
    print("-"*60)
    for r in results:
        cold_tps = r['cold']['tps']
        warm_tps = r['warm']['tps']
        speedup = warm_tps / cold_tps if cold_tps > 0 else 0
        print(f"{r['ctx_size']:8d} | {cold_tps:12.1f} | {warm_tps:12.1f} | {speedup:7.1f}x |")

    print()
    print("详细数据 (冷启动):")
    print(f"{'ctx_size':>8} | {'tokens':>8} | {'ms':>12} | {'TPS':>12}")
    print("-"*55)
    for r in results:
        c = r['cold']
        print(f"{r['ctx_size']:8d} | {c['tokens']:8d} | {c['ms']:12.1f} | {c['tps']:12.1f}")

    print()
    print("详细数据 (预热后):")
    print(f"{'ctx_size':>8} | {'tokens':>8} | {'ms':>12} | {'TPS':>12}")
    print("-"*55)
    for r in results:
        w = r['warm']
        print(f"{r['ctx_size']:8d} | {w['tokens']:8d} | {w['ms']:12.1f} | {w['tps']:12.1f}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
