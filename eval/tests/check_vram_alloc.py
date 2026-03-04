#!/usr/bin/env python3
"""
检查不同 ctx-size 下的显存分配和层 offload 情况
"""

import os
import sys
import subprocess
import time
import requests
import re

# 配置
MODEL_PATH = "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-27B-GGUF/Qwen3.5-27B-Q4_K_M.gguf"
LLAMA_SERVER = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
PORT = 8405
BASE_URL = f"http://localhost:{PORT}"


def test_ctx_size(ctx_size, test_prompt_len):
    """测试指定 ctx-size 的显存使用情况"""
    print(f"\n{'='*70}")
    print(f"测试 ctx-size: {ctx_size}")
    print('='*70)

    cmd = [
        LLAMA_SERVER,
        "-m", MODEL_PATH,
        "--ctx-size", str(ctx_size),
        "--n-gpu-layers", "99",
        "--port", str(PORT),
        "--flash-attn", "on",
        "--verbose"
    ]

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"

    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # 等待服务器启动并捕获输出
    startup_output = []
    server_ready = False
    start_time = time.time()

    while time.time() - start_time < 120:
        line = process.stdout.readline()
        if not line:
            time.sleep(0.1)
            continue
        startup_output.append(line)

        # 检查关键信息
        if "offloaded" in line and "layers" in line:
            print(f"  {line.strip()}")
        if "CUDA0 model buffer size" in line:
            print(f"  {line.strip()}")
        if "KV buffer size" in line:
            print(f"  {line.strip()}")
        if "failed" in line.lower():
            print(f"  {line.strip()}")

        # 检查健康检查
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=1)
            if response.status_code == 200:
                server_ready = True
                break
        except:
            pass

    if not server_ready:
        print("  服务器启动失败或超时")
        process.terminate()
        try:
            process.wait(timeout=10)
        except:
            process.kill()
        return None

    # 测试 prompt processing
    print(f"\n  测试 prompt 长度: {test_prompt_len}")
    prompt = "测试 " * (test_prompt_len // 2 + 10)

    payload = {
        "model": "test",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1,
        "temperature": 0.0
    }

    try:
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=300
        )
        elapsed = time.time() - start

        if response.status_code == 200:
            data = response.json()
            usage = data.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            tps = prompt_tokens / elapsed if elapsed > 0 else 0
            print(f"  ✅ {prompt_tokens} tokens, {tps:.1f} t/s, {elapsed:.2f}s")
            result = {"ctx_size": ctx_size, "tokens": prompt_tokens, "tps": tps, "elapsed": elapsed}
        else:
            print(f"  ❌ 失败: {response.status_code}")
            result = None
    except Exception as e:
        print(f"  ❌ 错误: {e}")
        result = None

    # 停止服务器
    process.terminate()
    try:
        process.wait(timeout=10)
    except:
        process.kill()

    return result


def main():
    print("="*70)
    print("Qwen3.5-27B 不同 Context 长度下的显存分配检查")
    print("="*70)

    results = []

    # 测试几个关键点
    test_cases = [
        (8192, 8000),
        (16384, 16000),
        (32768, 32000),
        (64536, 64000),
    ]

    for ctx_size, prompt_len in test_cases:
        result = test_ctx_size(ctx_size, prompt_len)
        if result:
            results.append(result)
        time.sleep(2)

    # 总结
    print("\n" + "="*70)
    print("性能对比")
    print("="*70)
    for r in results:
        print(f"  {r['ctx_size']:6d}: {r['tps']:6.1f} t/s")

    return 0


if __name__ == "__main__":
    sys.exit(main())
