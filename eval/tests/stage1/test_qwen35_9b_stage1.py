#!/usr/bin/env python3
"""
Qwen3.5 9B GGUF - Stage 1 性能测试
测试内容：
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

# ============== 配置 ==============
MODEL_PATH = "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-9B-GGUF/Qwen3.5-9B-UD-Q4_K_XL.gguf"
LLAMA_SERVER_VULKAN = "/mnt/volume3/llama_cpp/core/downloads/llama-b8069/llama-server"
LLAMA_SERVER_CUDA = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
BASE_PORT = 8450
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

    print(f"  启动命令: {' '.join(cmd[:5])} ...")

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
    print(f"  等待服务器启动 (最多120秒)...")

    start_wait = time.time()
    server_output = []

    for i in range(120):
        # 检查进程是否还在运行
        if process.poll() is not None:
            print(f"  ❌ 服务器进程意外退出，返回码: {process.returncode}")
            # 读取输出
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
                    if i % 20 == 0:  # 每20秒打印一点进度
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
    """测试 Prompt Processing - 长prompt，只生成1个token"""
    # 生成足够长的提示词
    # 每个中文词约2个token
    base_prompt = "这是一个测试句子。"
    multiplier = max(1, target_tokens // 5)  # 保守估计
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
            print(f"    ❌ API 返回错误: {response.status_code}")
            print(f"    响应: {response.text[:200]}")
            return None

        data = response.json()
    except requests.exceptions.Timeout:
        print(f"    ❌ 请求超时")
        return None
    except Exception as e:
        print(f"    ❌ 请求异常: {e}")
        return None

    usage = data.get('usage', {})
    timings = data.get('timings', {})

    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0)

    # 用 llama.cpp 返回的 prompt_ms 计算更准确
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
    """测试 Token Generation - 短prompt，生成多个token"""
    prompt = "请写一篇关于人工智能的短文，包含以下要点：\n1. 什么是人工智能\n2. 人工智能的应用领域\n3. 未来发展趋势"

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
            print(f"    ❌ API 返回错误: {response.status_code}")
            print(f"    响应: {response.text[:200]}")
            return None

        data = response.json()
    except requests.exceptions.Timeout:
        print(f"    ❌ 请求超时")
        return None
    except Exception as e:
        print(f"    ❌ 请求异常: {e}")
        return None

    usage = data.get('usage', {})
    timings = data.get('timings', {})

    prompt_tokens = usage.get('prompt_tokens', 0)
    completion_tokens = usage.get('completion_tokens', 0)

    # 用 llama.cpp 返回的 predicted_ms 计算
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
    """
    测试一个后端的完整性能

    Args:
        backend: "vulkan" 或 "cuda"
    """
    print(f"\n{'='*80}")
    print(f"🚀 开始测试 Qwen3.5 9B - {backend.upper()} 后端")
    print(f"{'='*80}")
    print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 模型: {MODEL_PATH}")
    print()

    results = {
        "model": "Qwen3.5-9B-UD-Q4_K_XL",
        "backend": backend,
        "timestamp": datetime.now().isoformat(),
        "ctx_sizes": {}
    }

    # 测试不同的 context size
    ctx_sizes = [8192, 16384, 32768]

    for ctx_size in ctx_sizes:
        port = BASE_PORT + ctx_size // 1000
        print(f"\n{'-'*80}")
        print(f"📊 Context Size: {ctx_size}")
        print(f"{'-'*80}")

        # 启动服务器
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
            try:
                requests.post(f"{base_url}/v1/chat/completions", json=warmup_payload, timeout=60)
                print(f"  ✅ 预热完成")
            except Exception as e:
                print(f"  ⚠️  预热可能失败: {e}")

            # 测试1: Prompt Processing - 约 ctx_size 的 75%
            target_pp_tokens = int(ctx_size * 0.75)
            print(f"\n  [1/3] Prompt Processing - 目标 ~{target_pp_tokens} tokens")
            r1 = test_prompt_processing(base_url, target_pp_tokens)
            if r1:
                print(f"      ✅ 实际: {r1['prompt_tokens']:5d} tokens | {r1['prompt_ms']:8.1f} ms | {r1['tps']:8.1f} t/s")
                ctx_result["prompt_processing"] = r1
            else:
                print(f"      ❌ 测试失败")

            # 测试2: Token Generation - 生成 256 tokens
            print(f"\n  [2/3] Token Generation - 生成 256 tokens")
            r2 = test_token_generation(base_url, 256)
            if r2:
                print(f"      ✅ Prompt: {r2['prompt_tokens']:4d} | Gen: {r2['completion_tokens']:4d} | {r2['predicted_ms']:8.1f} ms | {r2['tps']:6.1f} t/s")
                ctx_result["token_gen_256"] = r2
            else:
                print(f"      ❌ 测试失败")

            # 测试3: Token Generation - 生成 512 tokens
            print(f"\n  [3/3] Token Generation - 生成 512 tokens")
            r3 = test_token_generation(base_url, 512)
            if r3:
                print(f"      ✅ Prompt: {r3['prompt_tokens']:4d} | Gen: {r3['completion_tokens']:4d} | {r3['predicted_ms']:8.1f} ms | {r3['tps']:6.1f} t/s")
                ctx_result["token_gen_512"] = r3
            else:
                print(f"      ❌ 测试失败")

            results["ctx_sizes"][str(ctx_size)] = ctx_result

        finally:
            # 停止服务器
            print(f"\n  停止服务器...")
            process.terminate()
            try:
                process.wait(timeout=15)
                print(f"  ✅ 服务器已停止")
            except:
                print(f"  ⚠️  强制杀死服务器")
                process.kill()
                try:
                    process.wait(timeout=5)
                except:
                    pass

        # 休息一下
        time.sleep(3)

    return results


def print_summary_report(all_results):
    """打印汇总报告"""
    print("\n" + "="*80)
    print("📊 Stage 1 测试汇总报告")
    print("="*80)

    for backend, results in all_results.items():
        if not results or "ctx_sizes" not in results or not results["ctx_sizes"]:
            continue

        print(f"\n\n{'─'*80}")
        print(f"📌 后端: {backend.upper()}")
        print(f"{'─'*80}")

        ctx_sizes = sorted(results["ctx_sizes"].keys(), key=int)

        # Prompt Processing 表格
        print(f"\n[1] Prompt Processing (吞入速度):")
        print(f"{'ctx_size':>8} | {'tokens':>8} | {'ms':>10} | {'TPS':>10}")
        print("-"*55)
        for ctx_size_str in ctx_sizes:
            ctx_result = results["ctx_sizes"][ctx_size_str]
            if "prompt_processing" in ctx_result:
                pp = ctx_result["prompt_processing"]
                print(f"{ctx_size_str:>8} | {pp['prompt_tokens']:8d} | {pp['prompt_ms']:10.1f} | {pp['tps']:10.1f}")

        # Token Generation 表格
        print(f"\n[2] Token Generation (吐出速度):")
        print(f"{'ctx_size':>8} | {'gen 256':>10} | {'gen 512':>10}")
        print("-"*40)
        for ctx_size_str in ctx_sizes:
            ctx_result = results["ctx_sizes"][ctx_size_str]
            t256 = ctx_result.get("token_gen_256", {}).get("tps", 0)
            t512 = ctx_result.get("token_gen_512", {}).get("tps", 0)
            print(f"{ctx_size_str:>8} | {t256:10.1f} | {t512:10.1f}")

        # 详细数据
        print(f"\n[3] 详细数据:")
        for ctx_size_str in ctx_sizes:
            ctx_result = results["ctx_sizes"][ctx_size_str]
            print(f"\n  ctx_size = {ctx_size_str}:")

            if "prompt_processing" in ctx_result:
                pp = ctx_result["prompt_processing"]
                print(f"    Prompt Processing: {pp['prompt_tokens']} tokens @ {pp['tps']:.1f} t/s ({pp['prompt_ms']:.1f} ms)")

            if "token_gen_256" in ctx_result:
                tg = ctx_result["token_gen_256"]
                print(f"    Token Gen (256): {tg['completion_tokens']} tokens @ {tg['tps']:.1f} t/s ({tg['predicted_ms']:.1f} ms)")

            if "token_gen_512" in ctx_result:
                tg = ctx_result["token_gen_512"]
                print(f"    Token Gen (512): {tg['completion_tokens']} tokens @ {tg['tps']:.1f} t/s ({tg['predicted_ms']:.1f} ms)")


def save_results(all_results):
    """保存结果到文件"""
    ensure_results_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for backend, results in all_results.items():
        if not results:
            continue

        filename = f"{RESULTS_DIR}/qwen35_9b_{backend}_{timestamp}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print(f"\n💾 {backend.upper()} 结果已保存: {filename}")

    # 保存汇总
    summary_filename = f"{RESULTS_DIR}/qwen35_9b_summary_{timestamp}.json"
    with open(summary_filename, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"💾 汇总结果已保存: {summary_filename}")


def main():
    print("="*80)
    print("🧪 Qwen3.5 9B - Stage 1 性能测试")
    print("="*80)

    # 确认模型存在
    if not os.path.exists(MODEL_PATH):
        print(f"❌ 模型文件不存在: {MODEL_PATH}")
        return 1

    print(f"✅ 模型文件: {MODEL_PATH}")
    print(f"   大小: {os.path.getsize(MODEL_PATH) / (1024**3):.2f} GB")

    all_results = {}

    # 询问要测试哪个后端 (支持命令行参数)
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ["vulkan", "1"]:
            backends_to_test = ["vulkan"]
        elif arg in ["cuda", "2"]:
            backends_to_test = ["cuda"]
        else:
            backends_to_test = ["vulkan", "cuda"]
    else:
        print("\n请选择要测试的后端:")
        print("  1. Vulkan (AMD gfx1151)")
        print("  2. CUDA (NVIDIA V100)")
        print("  3. 两者都测试")

        choice = input("\n请输入选择 (1/2/3, 默认 3): ").strip() or "3"

        if choice == "1":
            backends_to_test = ["vulkan"]
        elif choice == "2":
            backends_to_test = ["cuda"]
        else:
            backends_to_test = ["vulkan", "cuda"]

    # 运行测试
    for backend in backends_to_test:
        try:
            results = test_backend(backend)
            all_results[backend] = results
        except KeyboardInterrupt:
            print(f"\n⚠️  {backend.upper()} 测试被用户中断")
            continue
        except Exception as e:
            print(f"\n❌ {backend.upper()} 测试出错: {e}")
            import traceback
            traceback.print_exc()
            continue

    # 打印报告
    if all_results:
        print_summary_report(all_results)
        save_results(all_results)
    else:
        print("\n❌ 没有完成任何测试")
        return 1

    print("\n" + "="*80)
    print("✅ Stage 1 测试完成")
    print("="*80)

    return 0


if __name__ == "__main__":
    sys.exit(main())
