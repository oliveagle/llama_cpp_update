#!/usr/bin/env python3
"""
诊断 Context 性能悬崖原因
使用 Qwen3-0.6B-Q4_0 研究 12K+ 性能下降

监控指标:
1. GPU 显存使用 (nvidia-smi)
2. 实际 token 处理速度
3. 批处理大小变化
4. 不同 prompt 长度的对比
"""

import requests
import time
import json
import subprocess
import threading
from datetime import datetime

MODEL_URL = "http://localhost:8401"
MODEL_NAME = "Qwen3-0.6B-Q4_0"
TEST_CONTEXTS = [4096, 8192, 12288, 16384, 24576]
MAX_TOKENS = 128

# 存储诊断结果
diagnosis_results = []

def get_gpu_memory():
    """获取 GPU 显存使用情况"""
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(", ")
            return {
                "memory_used_mb": int(parts[0]),
                "memory_total_mb": int(parts[1]),
                "gpu_util": int(parts[2]),
                "timestamp": time.time()
            }
    except Exception as e:
        print(f"  GPU监控错误: {e}")
    return None


def generate_prompt(target_tokens: int) -> str:
    """生成指定token数量的prompt"""
    char_count = target_tokens * 3
    base_text = "这是一个用于测试大语言模型长上下文处理能力的标准测试文本。"
    repeat_times = (char_count // len(base_text)) + 1
    return (base_text * repeat_times)[:char_count]


def test_with_monitoring(context_size: int):
    """测试并监控各项指标"""
    print(f"\n{'='*60}")
    print(f"测试 Context: {context_size} tokens")
    print(f"{'='*60}")

    prompt = generate_prompt(context_size)

    # 记录测试前 GPU 状态
    gpu_before = get_gpu_memory()
    print(f"  GPU 测试前: {gpu_before['memory_used_mb']}MB / {gpu_before['memory_total_mb']}MB "
          f"(利用率: {gpu_before['gpu_util']}%)")

    # 构造请求
    url = f"{MODEL_URL}/v1/chat/completions"
    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
        "temperature": 0.1,
        "stream": False
    }

    # 发送请求并计时
    timestamps = {
        "start": time.time(),
        "first_token": None,
        "prompt_done": None,
        "generation_done": None
    }

    try:
        # 监控 GPU 在请求过程中的状态
        gpu_during = []
        stop_monitoring = threading.Event()

        def monitor_gpu():
            while not stop_monitoring.is_set():
                info = get_gpu_memory()
                if info:
                    gpu_during.append(info)
                time.sleep(0.1)

        monitor_thread = threading.Thread(target=monitor_gpu)
        monitor_thread.start()

        # 发送请求
        resp = requests.post(url, json=payload, timeout=300)

        timestamps["end"] = time.time()
        stop_monitoring.set()
        monitor_thread.join()

        # 记录测试后 GPU 状态
        gpu_after = get_gpu_memory()
        print(f"  GPU 测试后: {gpu_after['memory_used_mb']}MB / {gpu_after['memory_total_mb']}MB "
              f"(利用率: {gpu_after['gpu_util']}%)")

        # 计算显存使用峰值
        if gpu_during:
            max_memory = max(g['memory_used_mb'] for g in gpu_during)
            avg_util = sum(g['gpu_util'] for g in gpu_during) / len(gpu_during)
            print(f"  GPU 峰值显存: {max_memory}MB")
            print(f"  GPU 平均利用率: {avg_util:.1f}%")

        if resp.status_code == 200:
            data = resp.json()
            usage = data.get("usage", {})
            prompt_tokens = usage.get("prompt_tokens", 0)
            completion_tokens = usage.get("completion_tokens", 0)

            total_time = timestamps["end"] - timestamps["start"]
            prompt_speed = prompt_tokens / total_time if total_time > 0 else 0
            gen_speed = completion_tokens / total_time if total_time > 0 else 0

            print(f"\n  结果:")
            print(f"    Prompt tokens: {prompt_tokens}")
            print(f"    Completion tokens: {completion_tokens}")
            print(f"    总耗时: {total_time:.2f}s")
            print(f"    预填充速度: {prompt_speed:.2f} t/s")
            print(f"    生成速度: {gen_speed:.2f} t/s")

            result = {
                "context_size": context_size,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_time_sec": round(total_time, 2),
                "prompt_speed_tps": round(prompt_speed, 2),
                "gen_speed_tps": round(gen_speed, 2),
                "gpu_memory_before_mb": gpu_before['memory_used_mb'] if gpu_before else None,
                "gpu_memory_after_mb": gpu_after['memory_used_mb'] if gpu_after else None,
                "gpu_memory_peak_mb": max(g['memory_used_mb'] for g in gpu_during) if gpu_during else None,
                "gpu_util_avg": round(avg_util, 1) if gpu_during else None,
                "status": "success"
            }
            diagnosis_results.append(result)
            return result
        else:
            print(f"  ❌ HTTP {resp.status_code}")
            result = {
                "context_size": context_size,
                "status": f"HTTP_{resp.status_code}",
                "error": resp.text[:200]
            }
            diagnosis_results.append(result)
            return result

    except Exception as e:
        print(f"  ❌ 错误: {e}")
        result = {
            "context_size": context_size,
            "status": "error",
            "error": str(e)
        }
        diagnosis_results.append(result)
        return result


def analyze_results():
    """分析结果，找出性能悬崖原因"""
    print(f"\n{'='*60}")
    print("分析结果")
    print(f"{'='*60}")

    # 筛选成功的结果
    success_results = [r for r in diagnosis_results if r.get("status") == "success"]

    if len(success_results) < 2:
        print("  数据不足，无法分析")
        return

    print("\n  性能对比表:")
    print(f"  {'Context':>10} | {'生成速度':>10} | {'显存峰值':>10} | {'GPU利用率':>10}")
    print(f"  {'-'*10}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}")

    for r in success_results:
        print(f"  {r['context_size']:>10} | {r['gen_speed_tps']:>10.2f} | "
              f"{r.get('gpu_memory_peak_mb', 'N/A'):>10} | {r.get('gpu_util_avg', 'N/A'):>10.1f}")

    # 查找悬崖点
    print("\n  性能下降分析:")
    for i in range(1, len(success_results)):
        prev = success_results[i-1]
        curr = success_results[i]

        speed_drop = (prev['gen_speed_tps'] - curr['gen_speed_tps']) / prev['gen_speed_tps'] * 100
        memory_increase = curr.get('gpu_memory_peak_mb', 0) - prev.get('gpu_memory_peak_mb', 0)

        print(f"\n  {prev['context_size']} -> {curr['context_size']}:")
        print(f"    生成速度下降: {speed_drop:.1f}% ({prev['gen_speed_tps']:.2f} -> {curr['gen_speed_tps']:.2f} t/s)")
        print(f"    显存增加: {memory_increase} MB")

        # 判断可能原因
        if speed_drop > 80:
            print(f"    ⚠️  性能悬崖检测!")
            if memory_increase > 1000:
                print(f"    🔍 可能原因: 显存不足导致频繁内存交换")
            elif curr.get('gpu_util_avg', 0) < 50:
                print(f"    🔍 可能原因: GPU利用率低，可能是计算瓶颈或等待")
            else:
                print(f"    🔍 可能原因: 算法复杂度增加 (Attention计算O(n²))")


def test_different_batch_sizes():
    """测试不同 batch 大小的影响"""
    print(f"\n{'='*60}")
    print("测试 Batch Size 影响")
    print(f"{'='*60}")

    # 使用固定 12K context，变化 max_tokens
    context_size = 12288
    max_tokens_list = [16, 32, 64, 128, 256]

    prompt = generate_prompt(context_size)

    for max_tokens in max_tokens_list:
        print(f"\n  测试 max_tokens={max_tokens}")

        url = f"{MODEL_URL}/v1/chat/completions"
        payload = {
            "model": MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.1
        }

        start = time.time()
        try:
            resp = requests.post(url, json=payload, timeout=300)
            elapsed = time.time() - start

            if resp.status_code == 200:
                data = resp.json()
                usage = data.get("usage", {})
                completion_tokens = usage.get("completion_tokens", 0)
                gen_speed = completion_tokens / elapsed if elapsed > 0 else 0
                print(f"    生成 {completion_tokens} tokens in {elapsed:.2f}s = {gen_speed:.2f} t/s")
            else:
                print(f"    ❌ HTTP {resp.status_code}")
        except Exception as e:
            print(f"    ❌ 错误: {e}")


def check_server_config():
    """检查服务器配置"""
    print(f"\n{'='*60}")
    print("服务器配置检查")
    print(f"{'='*60}")

    # 检查 llama-server 进程参数
    try:
        result = subprocess.run(
            ["pgrep", "-a", "llama-server"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print(f"  进程信息:")
            for line in result.stdout.strip().split('\n'):
                if '8401' in line:
                    print(f"    {line}")
    except Exception as e:
        print(f"  无法获取进程信息: {e}")

    # 检查当前加载的模型
    try:
        resp = requests.get(f"{MODEL_URL}/v1/models", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"\n  当前加载的模型:")
            for model in data.get("data", []):
                print(f"    - {model.get('id', 'unknown')}")
    except Exception as e:
        print(f"  无法获取模型信息: {e}")


def main():
    print("="*60)
    print("Context 性能悬崖诊断")
    print("="*60)
    print(f"目标模型: {MODEL_NAME}")
    print(f"测试梯度: {TEST_CONTEXTS}")
    print(f"服务器: {MODEL_URL}")
    print("="*60)

    # 1. 检查服务器配置
    check_server_config()

    # 2. 运行主要测试
    for ctx in TEST_CONTEXTS:
        test_with_monitoring(ctx)

    # 3. 分析结果
    analyze_results()

    # 4. 测试 batch size 影响
    test_different_batch_sizes()

    # 5. 保存结果
    output_file = f"eval_results/context_cliff_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, "w") as f:
        json.dump({
            "model": MODEL_NAME,
            "timestamp": datetime.now().isoformat(),
            "results": diagnosis_results
        }, f, indent=2)

    print(f"\n{'='*60}")
    print(f"诊断完成! 结果保存: {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
