#!/usr/bin/env python3
"""
对比测试两个脚本的差异，检查 llama.cpp 返回的 timings
"""

import os
import sys
import subprocess
import time
import requests

# 配置
MODEL_PATH = "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-27B-GGUF/Qwen3.5-27B-Q4_K_M.gguf"
LLAMA_SERVER = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
PORT = 8406
BASE_URL = f"http://localhost:{PORT}"


def start_server(ctx_size=8192):
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

    # 等待就绪
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


def test_with_timings(prompt_length):
    """测试并返回详细 timings"""
    prompt = "测试 " * (prompt_length // 2 + 10)

    payload = {
        "model": "test",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1,
        "temperature": 0.0
    }

    # 方法1: 总时间
    start_total = time.time()
    response = requests.post(f"{BASE_URL}/v1/chat/completions", json=payload, timeout=300)
    elapsed_total = time.time() - start_total

    data = response.json()
    usage = data.get('usage', {})
    timings = data.get('timings', {})

    prompt_tokens = usage.get('prompt_tokens', 0)

    print(f"\nPrompt 长度: {prompt_length} (实际: {prompt_tokens})")
    print(f"  总时间 (requests): {elapsed_total*1000:.1f} ms")
    print(f"  总时间 TPS: {prompt_tokens/elapsed_total:.1f} t/s")

    if timings:
        print(f"\n  llama.cpp timings:")
        print(f"    prompt_ms: {timings.get('prompt_ms', 0):.1f} ms")
        print(f"    predicted_ms: {timings.get('predicted_ms', 0):.1f} ms")
        prompt_tps = prompt_tokens / (timings.get('prompt_ms', 1) / 1000) if timings.get('prompt_ms', 0) > 0 else 0
        print(f"    prompt TPS: {prompt_tps:.1f} t/s")

    return {
        "prompt_tokens": prompt_tokens,
        "total_time_ms": elapsed_total * 1000,
        "timings": timings
    }


def main():
    print("="*70)
    print("测试 llama.cpp timings 差异")
    print("="*70)

    process = start_server(ctx_size=8192)
    if not process:
        print("无法启动服务器")
        return 1

    try:
        print("\n第一次测试 (预热):")
        test_with_timings(2048)

        print("\n" + "="*70)
        print("正式测试:")

        for length in [1024, 2048, 4096, 8192]:
            test_with_timings(length)

    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except:
            process.kill()

    return 0


if __name__ == "__main__":
    sys.exit(main())
