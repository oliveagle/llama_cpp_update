#!/usr/bin/env python3
"""
Qwen3.6-27B-MTP Stage 1 性能测试
测试 llama.cpp 的 --spec-type draft-mtp 推测解码性能

测试内容:
1. Prompt Processing (吞入速度)
2. Token Generation (吐出速度) - 对比 MTP 开/关
3. MTP 参数调优

模型: Qwen3.6-27B-MTP-Q4_K_M.gguf (15.3GB)
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
MODEL_PATH = "/mnt/eaget-4tb/modelscope_models/Qwen3.6-27B-MTP-GGUF/Qwen3.6-27B-Q4_K_M.gguf"
LLAMA_SERVER_VULKAN = "/mnt/eaget-4tb/llama_cpp/current/llama-server"
LLAMA_SERVER_CUDA = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
BASE_PORT = 8480
RESULTS_DIR = "/mnt/eaget-4tb/llama_cpp/eval/results/stage1_mtp"


def ensure_results_dir():
    """确保结果目录存在"""
    os.makedirs(RESULTS_DIR, exist_ok=True)


def start_server(backend, ctx_size, port, mtp_enabled=False, mtp_n_max=3, mtp_p_min=0.75):
    """
    启动 llama-server

    Args:
        backend: "vulkan" 或 "cuda"
        ctx_size: context size
        port: 端口号
        mtp_enabled: 是否启用 MTP
        mtp_n_max: MTP 最大 draft token 数
        mtp_p_min: MTP 最小接受概率

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

    # MTP 配置
    if mtp_enabled:
        cmd.append("--spec-type")
        cmd.append("draft-mtp")
        cmd.extend(["--spec-draft-n-max", str(mtp_n_max)])
        cmd.extend(["--spec-draft-p-min", str(mtp_p_min)])

    print(f"  启动命令：{' '.join(cmd[:6])} ...")
    if mtp_enabled:
        print(f"  MTP: n_max={mtp_n_max}, p_min={mtp_p_min}")

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
    print(f"  等待服务器启动 (最多 180 秒，模型较大)...")

    start_wait = time.time()
    server_output = []

    for i in range(180):
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
    base_prompt = "这是一个测试句子，用于测量 prompt 处理速度。"
    multiplier = max(1, target_tokens // 8)
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
        "response": data.get('choices', [{}])[0].get('message', {}).get('content', '')[:100]
    }


def test_mtp_config(backend, mtp_enabled, mtp_n_max, mtp_p_min, port_offset=0):
    """测试一个 MTP 配置的性能

    Args:
        backend: "vulkan" 或 "cuda"
        mtp_enabled: 是否启用 MTP
        mtp_n_max: MTP 最大 draft token 数
        mtp_p_min: MTP 最小接受概率
        port_offset: 端口偏移
    """
    ctx_size = 8192
    port = BASE_PORT + port_offset

    mtp_label = "MTP" if mtp_enabled else "Baseline"
    config_label = f"{mtp_label} (n={mtp_n_max}, p={mtp_p_min})" if mtp_enabled else "Baseline"

    print(f"\n{'='*80}")
    print(f"🚀 测试 Qwen3.6-27B - {config_label}")
    print(f"{'='*80}")

    process, base_url = start_server(backend, ctx_size, port, mtp_enabled, mtp_n_max, mtp_p_min)
    if not process:
        print(f"  ❌ 启动失败，跳过此配置")
        return None

    results = {
        "mtp_enabled": mtp_enabled,
        "mtp_n_max": mtp_n_max,
        "mtp_p_min": mtp_p_min,
        "ctx_size": ctx_size,
        "backend": backend,
    }

    try:
        # 预热
        print(f"\n  [预热] 运行一次短请求...")
        warmup_payload = {
            "model": "test",
            "messages": [{"role": "user", "content": "你好"}],
            "max_tokens": 10,
            "temperature": 0.7
        }
        requests.post(f"{base_url}/v1/chat/completions", json=warmup_payload, timeout=120)
        time.sleep(2)

        # Prompt Processing 测试
        print(f"\n  [Prompt Processing] 测试 2048 tokens...")
        pp = test_prompt_processing(base_url, 2048)
        if pp:
            print(f"    ✅ {pp['prompt_tokens']} tokens @ {pp['tps']:.1f} tokens/s")
            results["prompt_processing"] = pp

        # Token Generation 测试 - 多次运行取平均
        print(f"\n  [Token Generation] 测试 256 tokens (运行 3 次)...")
        tg_results = []
        for i in range(3):
            print(f"\n  第 {i+1} 次:")
            tg = test_token_generation(base_url, 256)
            if tg:
                print(f"    ✅ {tg['completion_tokens']} tokens @ {tg['tps']:.1f} tokens/s")
                tg_results.append(tg)
            time.sleep(1)

        if tg_results:
            # 计算平均值
            avg_tps = sum(r['tps'] for r in tg_results) / len(tg_results)
            avg_predicted_ms = sum(r['predicted_ms'] for r in tg_results) / len(tg_results)
            results["token_generation"] = {
                "avg_tps": avg_tps,
                "avg_predicted_ms": avg_predicted_ms,
                "runs": tg_results
            }
            print(f"\n  📊 平均: {avg_tps:.1f} tokens/s")

    finally:
        # 停止服务器
        print(f"\n  停止服务器...")
        process.terminate()
        try:
            process.wait(timeout=30)
        except:
            process.kill()

    return results


def test_mtp_parameter_sweep(backend):
    """MTP 参数扫频测试"""
    print(f"\n{'='*80}")
    print(f"🔬 MTP 参数扫频测试")
    print(f"{'='*80}")

    all_results = []

    # 基线测试 (无 MTP)
    print("\n[1/5] 基线测试 (无 MTP)...")
    result = test_mtp_config(backend, mtp_enabled=False, mtp_n_max=0, mtp_p_min=0, port_offset=0)
    if result:
        all_results.append(result)

    # MTP n_max=2 测试
    print("\n[2/5] MTP n_max=2 测试...")
    result = test_mtp_config(backend, mtp_enabled=True, mtp_n_max=2, mtp_p_min=0.75, port_offset=1)
    if result:
        all_results.append(result)

    # MTP n_max=3 测试
    print("\n[3/5] MTP n_max=3 测试...")
    result = test_mtp_config(backend, mtp_enabled=True, mtp_n_max=3, mtp_p_min=0.75, port_offset=2)
    if result:
        all_results.append(result)

    # MTP n_max=4 测试
    print("\n[4/5] MTP n_max=4 测试...")
    result = test_mtp_config(backend, mtp_enabled=True, mtp_n_max=4, mtp_p_min=0.75, port_offset=3)
    if result:
        all_results.append(result)

    # MTP n_max=3, p_min=0.90 测试
    print("\n[5/5] MTP n_max=3, p_min=0.90 测试...")
    result = test_mtp_config(backend, mtp_enabled=True, mtp_n_max=3, mtp_p_min=0.90, port_offset=4)
    if result:
        all_results.append(result)

    return all_results


def generate_report(results, filename):
    """生成 Markdown 格式报告"""
    report_lines = [
        f"# Qwen3.6-27B-MTP Stage 1 性能测试报告",
        f"",
        f"> **模型**: Qwen3.6-27B-MTP-Q4_K_M",
        f"> **后端**: {results[0]['backend'].upper() if results else 'N/A'}",
        f"> **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"> **模型文件**: {MODEL_PATH}",
        f"",
        f"## 测试结果",
        f"",
        f"| 配置 | MTP | n_max | p_min | Token Gen (t/s) | 加速比 |",
        f"|------|-----|-------|-------|----------------|--------|",
    ]

    baseline_tps = None
    for r in results:
        mtp_status = "✅" if r["mtp_enabled"] else "❌"
        n_max = r["mtp_n_max"] if r["mtp_enabled"] else "-"
        p_min = r["mtp_p_min"] if r["mtp_enabled"] else "-"

        if "token_generation" in r:
            tps = r["token_generation"]["avg_tps"]
            if baseline_tps is None and not r["mtp_enabled"]:
                baseline_tps = tps
            speedup = f"{tps/baseline_tps:.2f}x" if baseline_tps else "-"
            report_lines.append(
                f"| {r['mtp_enabled'] and 'MTP' or 'Baseline':8s} | {mtp_status} | {n_max} | {p_min} | {tps:.1f} | {speedup} |"
            )

    if baseline_tps:
        report_lines.append(f"")
        report_lines.append(f"## 总结")
        report_lines.append(f"")
        best = max(results, key=lambda x: x.get("token_generation", {}).get("avg_tps", 0))
        if best["mtp_enabled"]:
            best_tps = best["token_generation"]["avg_tps"]
            report_lines.append(f"- **最佳配置**: MTP n_max={best['mtp_n_max']}, p_min={best['mtp_p_min']}")
            report_lines.append(f"- **最佳速度**: {best_tps:.1f} tokens/s")
            report_lines.append(f"- **加速比**: {best_tps/baseline_tps:.2f}x vs 基线 {baseline_tps:.1f} tokens/s")
        else:
            report_lines.append(f"- **基线速度**: {baseline_tps:.1f} tokens/s")

    report_lines.append(f"")
    report_lines.append(f"---")
    report_lines.append(f"*测试脚本: test_qwen36_27b_mtp_stage1.py*")

    report_path = filename.replace(".json", "_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    return report_path


def main():
    ensure_results_dir()

    # 检查模型文件
    if not os.path.exists(MODEL_PATH):
        print(f"❌ 错误：模型文件不存在 '{MODEL_PATH}'")
        print(f"请先下载模型: huggingface.co/unsloth/Qwen3.6-27B-MTP-GGUF")
        return False

    print(f"✅ 模型文件存在：{os.path.getsize(MODEL_PATH) / (1024*1024*1024):.2f} GB")

    print("="*80)
    print("🎯 Qwen3.6-27B-MTP Stage 1 性能测试")
    print("="*80)
    print("请选择测试后端:")
    print("1. CUDA (NVIDIA V100)")
    print("2. Vulkan (AMD gfx1151)")

    choice = input("\n请输入选择 (1/2): ").strip()

    if choice == "1":
        backend = "cuda"
    else:
        backend = "vulkan"

    print(f"\n🚀 开始 {backend.upper()} 后端测试...")

    # MTP 参数扫频测试
    results = test_mtp_parameter_sweep(backend)

    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"qwen3_6_27b_mtp_{backend}_{timestamp}.json"
    filepath = os.path.join(RESULTS_DIR, filename)

    report_data = {
        "model": "Qwen3.6-27B-MTP-Q4_K_M",
        "backend": backend,
        "timestamp": datetime.now().isoformat(),
        "results": results
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)

    print(f"\n💾 结果已保存：{filepath}")

    # 生成报告
    report_path = generate_report(results, filepath)
    print(f"📄 报告已生成：{report_path}")

    print(f"\n✅ 测试完成!")
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