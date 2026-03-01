#!/usr/bin/env python3
"""
Qwen3.5-35B-A3B-UD Stage 1 吞吐量测试

测试 Qwen3.5-35B-A3B-UD 在不同 context size 下的性能表现
支持 Vulkan (gfx1151) 和 CUDA (V100) 后端

Usage:
    python test_qwen35_35b_a3b.py --backend vulkan --ctx-sizes 4096 8192 16384 32768 65536
    python test_qwen35_35b_a3b.py --backend cuda --ctx-sizes 4096 8192 16384 32768
"""

import argparse
import json
import time
import sys
import subprocess
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# 模型配置
MODEL_FILE = "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-35B-A3B-GGUF/Qwen3.5-35B-A3B-UD-Q4_K_XL.gguf"
MODEL_NAME = "Qwen3.5-35B-A3B-UD-Q4_K_XL"
TEST_PORT = 9995  # 使用独立端口避免冲突

# Vulkan 环境
VULKAN_ENV = {
    **os.environ,
    "MESA_VK_DEVICE_NAME": "AMD Radeon Graphics",
}


def start_server(backend: str, port: int, ctx_size: int) -> subprocess.Popen:
    """启动 llama-server"""
    if backend == "cuda":
        binary_path = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
    else:
        binary_path = "/mnt/volume3/llama_cpp/current/llama-server"

    cmd = [
        binary_path,
        "-m", MODEL_FILE,
        "--ctx-size", str(ctx_size),
        "--batch-size", "2048",
        "--ubatch-size", "512",
        "--threads", "16",
        "--threads-batch", "16",
        "-ngl", "99",
        "--port", str(port),
        "--flash-attn", "on",
        "--jinja",
    ]

    env = VULKAN_ENV if backend == "vulkan" else os.environ.copy()

    print(f"Starting server: {' '.join(cmd)}")
    process = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # 等待服务器就绪
    import urllib.request
    for _ in range(120):  # 增加等待时间，大模型加载慢
        try:
            urllib.request.urlopen(f"http://localhost:{port}/health", timeout=1)
            print(f"Server ready on port {port}")
            return process
        except:
            time.sleep(1)

    raise RuntimeError("Server failed to start")


def stop_server(process: subprocess.Popen):
    """停止服务器"""
    if process:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
        print("Server stopped")


def run_benchmark(backend: str, port: int, ctx_size: int, iterations: int = 3) -> Dict[str, Any]:
    """运行基准测试"""
    import urllib.request

    base_url = f"http://localhost:{port}"
    results = []

    for i in range(iterations):
        print(f"\n  Iteration {i+1}/{iterations}...")

        # 准备测试数据 - 生成指定长度的上下文
        # 使用简单的重复文本作为 context (与 JoyAI 测试保持一致)
        test_text = "测试 " * (ctx_size // 3)

        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "user", "content": test_text}
            ],
            "max_tokens": 1,
            "temperature": 0.0,
        }

        start_time = time.time()

        try:
            req = urllib.request.Request(
                f"{base_url}/v1/chat/completions",
                data=json.dumps(payload).encode('utf-8'),
                headers={"Content-Type": "application/json"}
            )
            response = urllib.request.urlopen(req, timeout=600)  # 增加超时时间
            data = json.loads(response.read().decode('utf-8'))

            elapsed_ms = (time.time() - start_time) * 1000

            # 提取指标
            usage = data.get("usage", {})
            timings = data.get("timings", {})

            prompt_tokens = usage.get("prompt_tokens", 0)
            prompt_ms = timings.get("prompt_ms", elapsed_ms)

            # 计算吞吐量
            if prompt_ms > 0:
                tps = (prompt_tokens / prompt_ms) * 1000
            else:
                tps = 0

            result = {
                "iteration": i + 1,
                "ctx_size": ctx_size,
                "prompt_tokens": prompt_tokens,
                "prompt_ms": prompt_ms,
                "tps": tps,
                "total_ms": elapsed_ms,
            }
            results.append(result)

            print(f"    Tokens: {prompt_tokens}, Time: {prompt_ms:.1f}ms, TPS: {tps:.1f}")

        except Exception as e:
            print(f"    Error: {e}")
            results.append({
                "iteration": i + 1,
                "ctx_size": ctx_size,
                "error": str(e)
            })

    # 计算平均值
    valid_results = [r for r in results if "error" not in r]
    if valid_results:
        avg_tps = sum(r["tps"] for r in valid_results) / len(valid_results)
        avg_prompt_ms = sum(r["prompt_ms"] for r in valid_results) / len(valid_results)
        avg_tokens = sum(r["prompt_tokens"] for r in valid_results) / len(valid_results)
    else:
        avg_tps = 0
        avg_prompt_ms = 0
        avg_tokens = 0

    return {
        "ctx_size": ctx_size,
        "iterations": iterations,
        "results": results,
        "avg_tps": avg_tps,
        "avg_prompt_ms": avg_prompt_ms,
        "avg_tokens": avg_tokens,
        "success": len(valid_results) > 0
    }


def run_test(backend: str, ctx_sizes: List[int], iterations: int = 3):
    """运行完整测试"""
    port = TEST_PORT
    device = "gfx1151" if backend == "vulkan" else "V100"

    print("="*70)
    print(f"Qwen3.5-35B-A3B-UD Stage 1 吞吐量测试")
    print(f"Backend: {backend} | Device: {device} | Port: {port}")
    print(f"Context Sizes: {ctx_sizes}")
    print(f"Iterations: {iterations}")
    print("="*70)

    all_results = []
    server_process = None

    try:
        for ctx_size in ctx_sizes:
            print(f"\n{'='*60}")
            print(f"Testing Context Size: {ctx_size}")
            print("="*60)

            # 停止之前的服务器
            if server_process:
                stop_server(server_process)
                time.sleep(3)

            # 启动新服务器
            try:
                server_process = start_server(backend, port, ctx_size)
            except RuntimeError as e:
                print(f"Failed to start server: {e}")
                all_results.append({
                    "ctx_size": ctx_size,
                    "success": False,
                    "error": str(e)
                })
                continue

            # 运行基准测试
            result = run_benchmark(backend, port, ctx_size, iterations)
            all_results.append(result)

            if result["success"]:
                print(f"\n  Average: {result['avg_tps']:.1f} t/s ({result['avg_prompt_ms']:.1f} ms)")
            else:
                print(f"\n  Failed to complete benchmark")

        # 打印汇总
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"{'Context Size':<15} {'Avg TPS':<15} {'Avg Time (ms)':<15} {'Status':<10}")
        print("-"*70)

        for result in all_results:
            status = "OK" if result.get("success") else "FAILED"
            avg_tps = result.get("avg_tps", 0)
            avg_ms = result.get("avg_prompt_ms", 0)
            print(f"{result['ctx_size']:<15} {avg_tps:<15.1f} {avg_ms:<15.1f} {status:<10}")

        # 保存结果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path(__file__).parent.parent / "results"
        results_dir.mkdir(parents=True, exist_ok=True)
        output_file = results_dir / f"qwen35_35b_a3b_{backend}_{device}_{timestamp}.json"

        output_data = {
            "timestamp": datetime.now().isoformat(),
            "backend": backend,
            "device": device,
            "model": MODEL_NAME,
            "model_file": MODEL_FILE,
            "iterations": iterations,
            "results": all_results
        }

        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\nResults saved to: {output_file}")

        # 生成报告
        generate_report(output_data, output_file.with_suffix('.md'))

    finally:
        if server_process:
            stop_server(server_process)


def generate_report(data: Dict[str, Any], output_file: Path):
    """生成 Markdown 报告"""
    backend = data["backend"]
    device = data["device"]
    model = data["model"]
    timestamp = data["timestamp"]

    report = f"""# {model} Stage 1 性能评估报告

> **评测时间**: {timestamp}
> **模型名称**: {model}
> **测试类型**: Stage 1 - 吞吐量基准测试

---

## 执行摘要

| 后端 | 设备 | 测试配置 |
|------|------|----------|
| {backend} | {device} | ctx-sizes: {[r['ctx_size'] for r in data['results']]} |

---

## 详细测试结果

### {backend} 后端 ({device})

| Context Size | 平均 TPS | 平均延迟 | 状态 |
|-------------|----------|----------|------|
"""

    for result in data["results"]:
        ctx_size = result["ctx_size"]
        if result.get("success"):
            avg_tps = result["avg_tps"]
            avg_ms = result["avg_prompt_ms"]
            status = "✅"
        else:
            avg_tps = "-"
            avg_ms = "-"
            status = "❌"
        report += f"| {ctx_size} | {avg_tps} | {avg_ms} | {status} |\n"

    report += """
---

## 逐次迭代数据

"""

    for result in data["results"]:
        if not result.get("success"):
            continue

        ctx_size = result["ctx_size"]
        report += f"""
### {ctx_size} Context

| 迭代 | Prompt Tokens | 延迟 (ms) | TPS |
|------|---------------|-----------|-----|
"""
        for r in result["results"]:
            if "error" not in r:
                report += f"| {r['iteration']} | {r['prompt_tokens']} | {r['prompt_ms']:.1f} | {r['tps']:.1f} |\n"

    report += f"""
---

## 结论

- 测试完成时间: {datetime.now().isoformat()}
- 结果文件: {output_file}

---

*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}*
*测试框架：llama.cpp Stage 1 Throughput Benchmark*
"""

    with open(output_file, 'w') as f:
        f.write(report)

    print(f"Report saved to: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Qwen3.5-35B-A3B-UD Stage 1 吞吐量测试"
    )
    parser.add_argument(
        "--backend",
        choices=["vulkan", "cuda"],
        required=True,
        help="后端类型"
    )
    parser.add_argument(
        "--ctx-sizes",
        type=int,
        nargs="+",
        default=[4096, 8192, 16384, 32768],
        help="要测试的上下文长度列表"
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="每个测试的迭代次数"
    )

    args = parser.parse_args()

    run_test(args.backend, args.ctx_sizes, args.iterations)


if __name__ == "__main__":
    main()
