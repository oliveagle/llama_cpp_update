#!/usr/bin/env python3
"""
Qwen3.5-0.8B-UD-Q8_K_XL - Stage 1 性能测试
测试内容:
1. Prompt Processing (吞入速度)
2. Token Generation (吐出速度)
3. 不同 Context Size 下的性能表现
"""

import os
import sys
import subprocess
import time
import requests
import json
from datetime import datetime
from pathlib import Path

# ============== 配置 ==============
MODEL_PATH = "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-0___8B-GGUF/Qwen3.5-0.8B-UD-Q8_K_XL.gguf"
LLAMA_SERVER_VULKAN = "/mnt/volume3/llama_cpp/core/downloads/llama-b8069/llama-server"
LLAMA_SERVER_CUDA = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
BASE_PORT = 8470
RESULTS_DIR = "/mnt/volume3/llama_cpp/eval/results/stage1"


def ensure_results_dir():
    """确保结果目录存在"""
    os.makedirs(RESULTS_DIR, exist_ok=True)


def start_server(backend, ctx_size, port):
    """
    启动 llama-server

    Args:
        backend: "vulkan" 或 "cuda"
        ctx_size: context size
        port: 端口号

    Returns:
        (process, base_url) 或 (None, None)
    """
    if backend == "vulkan":
        llama_server = LLAMA_SERVER_VULKAN
        env = os.environ.copy()
        env["AMD_VULKAN_ICD"] = "/usr/share/vulkan/icd.d/amdvlk64.json"
    else:  # cuda
        llama_server = LLAMA_SERVER_CUDA
        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = "0"

    cmd = [
        llama_server,
        "-m", MODEL_PATH,
        "--ctx-size", str(ctx_size),
        "--n-gpu-layers", "99",
        "--port", str(port),
        "--threads", "8",
        "--threads-batch", "8",
    ]

    print(f"  启动命令：{' '.join(cmd[:5])} ...")

    process = subprocess.Popen(
        cmd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    # 等待就绪
    base_url = f"http://localhost:{port}"
    print(f"  等待服务器启动 (最多 120 秒)...")

    start_wait = time.time()
    server_output = []

    for i in range(120):
        # 检查进程是否还在运行
        if process.poll() is not None:
            print(f"  ❌ 服务器进程意外退出，返回码：{process.returncode}")
            if process.stdout:
                remaining_output = process.stdout.read()
                if remaining_output:
                    print(f"  服务器输出:\n{remaining_output}")
            return None, None

        # 尝试健康检查
        try:
            r = requests.get(f"{base_url}/health", timeout=2)
            if r.status_code == 200:
                elapsed = time.time() - start_wait
                print(f"  ✅ 服务器已就绪 (耗时 {elapsed:.1f}s)")
                return process, base_url
        except:
            pass

        # 读取一些输出
        try:
            if process.stdout:
                line = process.stdout.readline()
                if line:
                    server_output.append(line.strip())
                    if i % 20 == 0:
                        print(f"  等待中... ({i}s)")
        except:
            pass

        time.sleep(1)

    # 超时
    print(f"  ❌ 服务器启动超时")
    print(f"  最近的服务器输出:")
    for line in server_output[-20:]:
        print(f"    {line}")

    process.terminate()
    try:
        process.wait(timeout=10)
    except:
        process.kill()

    return None, None


def test_prompt_processing(base_url, target_tokens):
    """测试 Prompt Processing - 长 prompt，只生成 1 个 token"""
    base_prompt = "这是一个测试句子。"
    multiplier = max(1, target_tokens // 5)
    prompt = base_prompt * multiplier

    payload = {
        "model": "test",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1,
        "temperature": 0.0,
        "cache_prompt": True
    }

    start = time.time()
    try:
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=payload,
            timeout=600
        )
        elapsed = time.time() - start

        if response.status_code != 200:
            print(f"    ❌ API 返回错误：{response.status_code}")
            return None

        data = response.json()
    except requests.exceptions.Timeout:
        print(f"    ❌ 请求超时")
        return None
    except Exception as e:
        print(f"    ❌ 请求异常：{e}")
        return None

    usage = data.get('usage', {})
    timings = data.get('timings', {})

    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0)

    tps = 0
    prompt_ms = 0
    if timings and timings.get('prompt_ms', 0) > 0:
        prompt_ms = timings['prompt_ms']
        tps = prompt_tokens / (prompt_ms / 1000)

    return {
        "type": "prompt_processing",
        "target_tokens": target_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_time_ms": elapsed * 1000,
        "prompt_ms": prompt_ms,
        "tps": tps,
    }


def test_token_generation(base_url, max_tokens):
    """测试 Token Generation - 短 prompt，生成多个 token"""
    prompt = "请写一篇关于人工智能的短文。"

    payload = {
        "model": "test",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.7,
        "top_p": 0.9,
        "cache_prompt": True
    }

    start = time.time()
    try:
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=payload,
            timeout=900
        )
        elapsed = time.time() - start

        if response.status_code != 200:
            print(f"    ❌ API 返回错误：{response.status_code}")
            return None

        data = response.json()
    except requests.exceptions.Timeout:
        print(f"    ❌ 请求超时")
        return None
    except Exception as e:
        print(f"    ❌ 请求异常：{e}")
        return None

    usage = data.get('usage', {})
    timings = data.get('timings', {})

    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0)

    tps = 0
    predicted_ms = 0
    if timings and timings.get('predicted_ms', 0) > 0:
        predicted_ms = timings['predicted_ms']
        tps = completion_tokens / (predicted_ms / 1000)

    return {
        "type": "token_generation",
        "target_max_tokens": max_tokens,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_time_ms": elapsed * 1000,
        "predicted_ms": predicted_ms,
        "tps": tps,
    }


def test_backend(backend):
    """测试一个后端的完整性能"""
    print(f"\n{'='*80}")
    print(f"🚀 开始测试 Qwen3.5-4B - {backend.upper()} 后端")
    print(f"{'='*80}")
    print(f"📅 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 模型：{MODEL_PATH}")
    print(f"📦 文件大小：{os.path.getsize(MODEL_PATH) / (1024*1024*1024):.2f} GB")
    print()

    results = {
        "model": "Qwen3.5-0.8B-UD-Q8_K_XL",
        "backend": backend,
        "timestamp": datetime.now().isoformat(),
        "ctx_sizes": {}
    }

    ctx_sizes = [8192, 16384, 32768]

    for ctx_size in ctx_sizes:
        port = BASE_PORT + ctx_size // 1000
        print(f"\n{'-'*80}")
        print(f"📊 Context Size: {ctx_size}")
        print(f"{'-'*80}")

        process, base_url = start_server(backend, ctx_size, port)
        if not process:
            print(f"  ❌ 启动失败，跳过此 ctx_size")
            continue

        ctx_result = {}

        try:
            # 预热
            print(f"\n  [预热] 运行一次短请求...")
            warmup_payload = {
                "model": "test",
                "messages": [{"role": "user", "content": "你好"}],
                "max_tokens": 10,
                "temperature": 0.7
            }
            requests.post(f"{base_url}/v1/chat/completions", json=warmup_payload, timeout=60)
            time.sleep(1)

            # Prompt Processing 测试
            print(f"\n  [Prompt Processing] 测试 4096 tokens...")
            pp_4k = test_prompt_processing(base_url, 4096)
            if pp_4k:
                print(f"    ✅ {pp_4k['prompt_tokens']} tokens @ {pp_4k['tps']:.1f} tokens/s")
                ctx_result["prompt_processing"] = pp_4k

            # Token Generation 测试
            for tg_tokens in [256, 512]:
                print(f"\n  [Token Generation] 测试 {tg_tokens} tokens...")
                tg = test_token_generation(base_url, tg_tokens)
                if tg:
                    print(f"    ✅ {tg['completion_tokens']} tokens @ {tg['tps']:.1f} tokens/s")
                    if "token_generation" not in ctx_result:
                        ctx_result["token_generation"] = {}
                    ctx_result["token_generation"][str(tg_tokens)] = tg

        finally:
            # 停止服务器
            print(f"\n  停止服务器...")
            process.terminate()
            try:
                process.wait(timeout=30)
            except:
                process.kill()

        results["ctx_sizes"][str(ctx_size)] = ctx_result

    # 保存结果
    ensure_results_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"qwen3.5-4b_{backend}_{timestamp}.json"
    filepath = os.path.join(RESULTS_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 结果已保存：{filepath}")

    # 打印总结
    print(f"\n{'='*80}")
    print(f"📊 测试总结")
    print(f"{'='*80}")

    all_pp_tps = []
    all_tg_tps = []

    for ctx_size, ctx_data in results["ctx_sizes"].items():
        if "prompt_processing" in ctx_data:
            pp_tps = ctx_data["prompt_processing"]["tps"]
            if pp_tps > 0:
                all_pp_tps.append(pp_tps)
                print(f"Context {ctx_size}: Prompt Processing = {pp_tps:.1f} tokens/s")

        if "token_generation" in ctx_data:
            for tg_len, tg_data in ctx_data["token_generation"].items():
                tg_tps = tg_data["tps"]
                if tg_tps > 0:
                    all_tg_tps.append(tg_tps)
                    print(f"Context {ctx_size}: Token Gen {tg_len} = {tg_tps:.1f} tokens/s")

    if all_pp_tps:
        avg_pp_tps = sum(all_pp_tps) / len(all_pp_tps)
        print(f"\n平均 Prompt Processing: {avg_pp_tps:.1f} tokens/s")

    if all_tg_tps:
        avg_tg_tps = sum(all_tg_tps) / len(all_tg_tps)
        print(f"平均 Token Generation: {avg_tg_tps:.1f} tokens/s")

    print(f"\n✅ 测试完成!")
    return results


def main():
    ensure_results_dir()

    # 检查模型文件
    if not os.path.exists(MODEL_PATH):
        print(f"❌ 错误：模型文件不存在 '{MODEL_PATH}'")
        return False

    # 选择后端
    print("="*80)
    print("🎯 Qwen3.5-0.8B-UD-Q8_K_XL Stage 1 性能测试")
    print("="*80)
    print("请选择测试后端:")
    print("1. CUDA (NVIDIA V100)")
    print("2. Vulkan (AMD gfx1151)")
    print("3. 两者都测试")

    choice = input("\n请输入选择 (1/2/3): ").strip()

    if choice == "1":
        test_backend("cuda")
    elif choice == "2":
        test_backend("vulkan")
    elif choice == "3":
        test_backend("cuda")
        test_backend("vulkan")
    else:
        print("无效选择，默认测试 CUDA")
        test_backend("cuda")

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
        sys.exit(2)
    except Exception as e:
        print(f"\n❌ 测试失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)
