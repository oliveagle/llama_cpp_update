#!/usr/bin/env python3
"""
测试 Qwen3.5-27B 的最大 Context 长度
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

# 配置
MODEL_PATH = "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-27B-GGUF/Qwen3.5-27B-Q4_K_M.gguf"
LLAMA_SERVER = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
PORT = 8402  # 使用不同的端口避免冲突
BASE_URL = f"http://localhost:{PORT}"


def start_server(ctx_size):
    """启动 llama-server"""
    cmd = [
        LLAMA_SERVER,
        "-m", MODEL_PATH,
        "--ctx-size", str(ctx_size),
        "--n-gpu-layers", "99",
        "--port", str(PORT),
        "--flash-attn", "on"
    ]

    print(f"启动服务器 (ctx-size={ctx_size})...")

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
    start_time = time.time()
    while time.time() - start_time < 180:
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"  服务器就绪! (耗时 {time.time() - start_time:.1f}s)")
                return process
        except:
            time.sleep(1)

        if process.poll() is not None:
            print(f"  服务器启动失败!")
            return None

    print(f"  启动超时!")
    process.terminate()
    return None


def stop_server(process):
    """停止服务器"""
    if process:
        process.terminate()
        try:
            process.wait(timeout=10)
        except:
            process.kill()
            process.wait()


def test_context(prompt_length):
    """测试指定长度的 context"""
    prompt = "测试 " * (prompt_length // 2 + 10)

    payload = {
        "model": "test",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1,
        "temperature": 0.0
    }

    try:
        start_time = time.time()
        response = requests.post(
            f"{BASE_URL}/v1/chat/completions",
            json=payload,
            timeout=300
        )
        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            usage = data.get('usage', {})
            prompt_tokens = usage.get('prompt_tokens', 0)
            tps = prompt_tokens / elapsed if elapsed > 0 else 0
            return True, prompt_tokens, tps, elapsed
        else:
            return False, 0, 0, elapsed
    except Exception as e:
        return False, 0, 0, 0


def main():
    print("="*70)
    print("Qwen3.5-27B 最大 Context 长度测试")
    print("="*70)
    print()

    ctx_sizes_to_test = [8192, 16384, 24576, 32768, 49152, 65536]
    results = []

    for ctx_size in ctx_sizes_to_test:
        print(f"\n{'='*70}")
        print(f"测试 ctx-size: {ctx_size}")
        print('='*70)

        # 启动服务器
        process = start_server(ctx_size)
        if not process:
            print(f"❌ ctx-size={ctx_size}: 无法启动服务器")
            results.append({"ctx_size": ctx_size, "success": False, "reason": "startup_failed"})
            continue

        try:
            # 测试几个点
            test_lengths = [
                ctx_size // 4,
                ctx_size // 2,
                ctx_size * 3 // 4,
                ctx_size - 100  # 留点余量
            ]

            all_passed = True
            test_results = []

            for test_len in test_lengths:
                if test_len < 512:
                    continue
                print(f"  测试 prompt 长度: {test_len}...")
                success, tokens, tps, elapsed = test_context(test_len)
                if success:
                    print(f"    ✅ 成功! {tokens} tokens, {tps:.1f} t/s, {elapsed:.2f}s")
                    test_results.append({"length": test_len, "tokens": tokens, "tps": tps})
                else:
                    print(f"    ❌ 失败!")
                    all_passed = False
                    break

            if all_passed and test_results:
                max_tps = max(r['tps'] for r in test_results)
                print(f"\n✅ ctx-size={ctx_size}: 成功! 最大速度 {max_tps:.1f} t/s")
                results.append({
                    "ctx_size": ctx_size,
                    "success": True,
                    "max_tps": max_tps,
                    "tests": test_results
                })
            else:
                print(f"\n❌ ctx-size={ctx_size}: 测试失败")
                results.append({"ctx_size": ctx_size, "success": False, "reason": "test_failed"})

        finally:
            stop_server(process)

        # 小延时
        time.sleep(2)

    # 总结
    print()
    print("="*70)
    print("测试总结")
    print("="*70)
    print()

    for r in results:
        if r['success']:
            print(f"✅ {r['ctx_size']:6d}: 成功 (max {r['max_tps']:.1f} t/s)")
        else:
            print(f"❌ {r['ctx_size']:6d}: 失败 ({r.get('reason', 'unknown')})")

    # 找出最大成功的
    max_success = max([r['ctx_size'] for r in results if r['success']], default=0)
    print()
    print(f"最大成功的 Context 长度: {max_success}")

    # 保存结果
    import json
    output_file = Path("/mnt/volume3/llama_cpp/eval/results/qwen3.5-27b-max-context.json")
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n结果已保存到: {output_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
