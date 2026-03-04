#!/usr/bin/env python3
"""
验证：测试多个 prompt 长度时，后面的测试是否更快
"""

import os
import sys
import subprocess
import time
import requests

# 配置
MODEL_PATH = "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-27B-GGUF/Qwen3.5-27B-Q4_K_M.gguf"
LLAMA_SERVER = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
PORT = 8409
BASE_URL = f"http://localhost:{PORT}"


def start_server():
    """启动服务器"""
    cmd = [
        LLAMA_SERVER,
        "-m", MODEL_PATH,
        "--ctx-size", "16384",
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


def test_prompt(length):
    """测试指定长度"""
    prompt = "测试 " * (length // 2 + 10)

    payload = {
        "model": "test",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1,
        "temperature": 0.0
    }

    start = time.time()
    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, timeout=300)
    elapsed = time.time() - start

    data = response.json()
    usage = data.get('usage', {})
    actual = usage.get('prompt_tokens', 0)
    tps = actual / elapsed if elapsed > 0 and actual > 0 else 0

    return actual, elapsed, tps


def main():
    print("="*70)
    print("验证：递增测试是否有预热效应")
    print("="*70)

    process = start_server()
    if not process:
        print("启动失败")
        return 1

    try:
        print("\n第一轮：冷启动，直接测试 8K")
        actual, elapsed, tps = test_prompt(8000)
        print(f"  {actual} tokens, {elapsed*1000:.1f} ms, {tps:.1f} t/s")

        print("\n第二轮：递增测试 (2K → 4K → 6K → 8K)")
        for length in [2000, 4000, 6000, 8000]:
            actual, elapsed, tps = test_prompt(length)
            print(f"  {length:4d}: {actual:5d} tokens, {elapsed*1000:7.1f} ms, {tps:7.1f} t/s")

        print("\n第三轮：再测试一次 8K")
        actual, elapsed, tps = test_prompt(8000)
        print(f"  {actual} tokens, {elapsed*1000:.1f} ms, {tps:.1f} t/s")

    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except:
            process.kill()

    return 0


if __name__ == "__main__":
    sys.exit(main())
