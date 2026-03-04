#!/usr/bin/env python3
"""
简单的 Qwen3.5-27B 性能测试脚本 - 直接使用 llama.cpp
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

# 配置
MODEL_PATH = "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-27B-GGUF/Qwen3.5-27B-Q4_K_M.gguf"
LLAMA_SERVER = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
PORT = 8401
BASE_URL = f"http://localhost:{PORT}"


def start_server(ctx_size=8192):
    """启动 llama-server"""
    cmd = [
        LLAMA_SERVER,
        "-m", MODEL_PATH,
        "--ctx-size", str(ctx_size),
        "--n-gpu-layers", "99",
        "--port", str(PORT),
        "--flash-attn", "on"
    ]

    print(f"启动服务器: {' '.join(cmd)}")

    env = os.environ.copy()
    env["CUDA_VISIBLE_DEVICES"] = "0"

    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    # 等待服务器就绪
    print("等待服务器启动...")
    start_time = time.time()
    while time.time() - start_time < 120:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"服务器就绪! (耗时 {time.time() - start_time:.1f}s)")
                return process
        except:
            time.sleep(1)

        # 检查进程是否还在运行
        if process.poll() is not None:
            print("服务器进程意外退出!")
            output = process.stdout.read()
            print(output)
            return None

    print("服务器启动超时!")
    return process


def stop_server(process):
    """停止服务器"""
    if process:
        print("停止服务器...")
        process.terminate()
        try:
            process.wait(timeout=10)
        except:
            process.kill()
            process.wait()
        print("服务器已停止")


def generate_prompt(length):
    """生成指定长度的 prompt"""
    base_text = "请用中文回答以下问题："
    repeat_text = "这是一个测试文本。" * (length // 10)
    return base_text + repeat_text


def test_prompt_processing(prompt_length):
    """测试 Prompt Processing 速度"""
    prompt = generate_prompt(prompt_length)

    payload = {
        "model": "test",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1,
        "temperature": 0.0
    }

    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        json=payload,
        timeout=300
    )
    elapsed = time.time() - start_time

    data = response.json()
    usage = data.get('usage', {})

    prompt_tokens = usage.get('prompt_tokens', 0)
    tps = prompt_tokens / elapsed if elapsed > 0 else 0

    return {
        "prompt_length": prompt_length,
        "prompt_tokens": prompt_tokens,
        "time_ms": elapsed * 1000,
        "tps": tps
    }


def test_token_generation(prompt_length, max_tokens):
    """测试 Token Generation 速度"""
    prompt = generate_prompt(prompt_length)

    payload = {
        "model": "test",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7
    }

    start_time = time.time()
    response = requests.post(
        f"{BASE_URL}/v1/chat/completions",
        json=payload,
        timeout=600
    )
    elapsed = time.time() - start_time

    data = response.json()
    usage = data.get('usage', {})

    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0)

    # 估算生成速度 (总时间 - prompt 处理时间估算)
    # 这里简化处理，直接用总时间计算
    gen_tps = completion_tokens / elapsed if elapsed > 0 else 0

    return {
        "prompt_length": prompt_length,
        "max_tokens": max_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "time_ms": elapsed * 1000,
        "gen_tps": gen_tps
    }


def main():
    print("="*70)
    print("Qwen3.5-27B Stage 1 性能测试 (V100)")
    print("="*70)
    print()

    # 启动服务器
    process = start_server(ctx_size=8192)
    if not process:
        print("无法启动服务器，退出")
        return 1

    try:
        print()
        print("="*70)
        print("Test 1: Prompt Processing")
        print("="*70)

        prompt_lengths = [512, 1024, 2048, 4096, 8192]
        prompt_results = []

        for length in prompt_lengths:
            print(f"\n测试 Prompt length: {length}")
            # 运行 2 次取平均
            results = []
            for i in range(2):
                try:
                    r = test_prompt_processing(length)
                    results.append(r)
                    print(f"  Iter {i+1}: {r['tps']:.1f} t/s ({r['time_ms']:.0f} ms)")
                except Exception as e:
                    print(f"  Iter {i+1}: 失败 - {e}")

            if results:
                avg_tps = sum(r['tps'] for r in results) / len(results)
                avg_time = sum(r['time_ms'] for r in results) / len(results)
                prompt_results.append({
                    "length": length,
                    "avg_tps": avg_tps,
                    "avg_time_ms": avg_time
                })
                print(f"  Average: {avg_tps:.1f} t/s ({avg_time:.0f} ms)")

        print()
        print("="*70)
        print("Test 2: Token Generation")
        print("="*70)

        gen_lengths = [128, 256, 512]
        gen_results = []

        for max_tokens in gen_lengths:
            print(f"\n测试生成 Max tokens: {max_tokens}")
            results = []
            for i in range(2):
                try:
                    r = test_token_generation(1024, max_tokens)
                    results.append(r)
                    print(f"  Iter {i+1}: {r['gen_tps']:.1f} t/s, {r['completion_tokens']} tokens, {r['time_ms']:.0f} ms")
                except Exception as e:
                    print(f"  Iter {i+1}: 失败 - {e}")

            if results:
                avg_tps = sum(r['gen_tps'] for r in results) / len(results)
                avg_time = sum(r['time_ms'] for r in results) / len(results)
                gen_results.append({
                    "max_tokens": max_tokens,
                    "avg_tps": avg_tps,
                    "avg_time_ms": avg_time
                })
                print(f"  Average: {avg_tps:.1f} t/s ({avg_time:.0f} ms)")

        # 生成报告
        print()
        print("="*70)
        print("SUMMARY REPORT")
        print("="*70)
        print()
        print("模型: Qwen3.5-27B-Q4_K_M")
        print("GPU: NVIDIA V100")
        print("Backend: CUDA")
        print()
        print("Prompt Processing:")
        for r in prompt_results:
            print(f"  {r['length']:5d} tokens: {r['avg_tps']:6.1f} t/s ({r['avg_time_ms']:6.0f} ms)")
        print()
        print("Token Generation:")
        for r in gen_results:
            print(f"  {r['max_tokens']:4d} tokens: {r['avg_tps']:5.1f} t/s ({r['avg_time_ms']:6.0f} ms)")
        print()

        # 保存结果
        output_dir = Path("/mnt/volume3/llama_cpp/eval/results")
        output_dir.mkdir(exist_ok=True)

        report = {
            "model": "Qwen3.5-27B-Q4_K_M",
            "gpu": "V100",
            "backend": "CUDA",
            "timestamp": time.time(),
            "prompt_processing": prompt_results,
            "token_generation": gen_results
        }

        output_file = output_dir / "qwen3.5-27b-v100-stage1.json"
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"结果已保存到: {output_file}")

    finally:
        stop_server(process)

    return 0


if __name__ == "__main__":
    sys.exit(main())
