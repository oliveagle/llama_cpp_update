#!/usr/bin/env python3
"""
V100 CUDA 全模型性能基准测试
测试梯度: 4K, 8K, 12K, 16K, 24K, 32K, 48K, 64K, 96K, 128K
记录指标: 预填充速度 (t/s), 生成速度 (t/s), 首token延迟 (TTFT)
"""

import time
import requests
import json
import os
from typing import Dict, List, Optional
from datetime import datetime

# 测试配置
MODEL_URL = "http://localhost:8401"
CONTEXT_STEPS = [4096, 8192, 12288, 16384, 24576, 32768, 49152, 65536, 98304, 131072]
MAX_TOKENS = 128
TEMPERATURE = 0.1

# 模型列表 (从 mypresets-cuda.ini)
MODELS = [
    {"name": "Qwen3-0.6B-Q4_0", "display": "Qwen3-0.6B (Q4_0)", "ctx_default": 12288},
    {"name": "Alibaba-Apsara.DASD-4B-Thinking.Q8_0", "display": "Apsara-4B (Q8_0)", "ctx_default": 12288},
    {"name": "MiniCPM-o-4_5-Q4_K_M", "display": "MiniCPM-o-4.5 (Q4_K_M)", "ctx_default": 12288},
    {"name": "Qwen3-4B-Instruct-2507-UD-Q4_K_XL", "display": "Qwen3-4B (Q4_K_XL)", "ctx_default": 12288},
    {"name": "Qwen3VL-4B-Instruct-Q8_0", "display": "Qwen3VL-4B (Q8_0)", "ctx_default": 12288},
    {"name": "Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0", "display": "Qwen3-VL-8B (Q8_0)", "ctx_default": 12288},
    {"name": "GLM-4.7-Flash-Q4_K_M", "display": "GLM-4.7-Flash (Q4_K_M)", "ctx_default": 12288},
    {"name": "JoyAI-LLM-Flash-Q4_K_M", "display": "JoyAI-Flash (Q4_K_M)", "ctx_default": 16384},
]


def generate_prompt(target_tokens: int) -> str:
    """生成指定token数量的prompt (估算: 1 token ≈ 3 中文字符)"""
    char_count = target_tokens * 3
    # 使用重复的测试文本
    base_text = "这是一个用于测试大语言模型长上下文处理能力的标准测试文本。我们需要生成足够长的内容来填充指定的上下文窗口大小，以便准确测量模型在不同上下文长度下的预填充速度和生成速度。"
    repeat_times = (char_count // len(base_text)) + 1
    return (base_text * repeat_times)[:char_count]


def test_model_at_context(model_name: str, context_size: int) -> Optional[Dict]:
    """
    测试指定模型在指定context大小下的性能
    返回: {"prompt_tokens": int, "prompt_speed": float, "gen_speed": float, "ttft_ms": float, "status": str}
    """
    prompt = generate_prompt(context_size)

    url = f"{MODEL_URL}/v1/chat/completions"
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
        "temperature": TEMPERATURE,
        "stream": False
    }

    try:
        start_time = time.time()
        resp = requests.post(url, json=payload, timeout=300)
        elapsed = time.time() - start_time

        if resp.status_code == 200:
            data = resp.json()
            usage = data.get("usage", {})
            completion_tokens = usage.get("completion_tokens", 0)
            prompt_tokens = usage.get("prompt_tokens", 0)

            # 计算指标
            gen_speed = completion_tokens / elapsed if elapsed > 0 else 0
            prompt_speed = prompt_tokens / elapsed if elapsed > 0 else 0
            ttft_ms = elapsed * 1000  # 简化为总耗时（非流式）

            return {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "prompt_speed_tps": round(prompt_speed, 2),
                "gen_speed_tps": round(gen_speed, 2),
                "ttft_ms": round(ttft_ms, 2),
                "elapsed_sec": round(elapsed, 2),
                "status": "success"
            }
        else:
            return {
                "status": f"HTTP_{resp.status_code}",
                "error": resp.text[:200]
            }
    except requests.exceptions.Timeout:
        return {"status": "timeout", "error": "Request timeout (>300s)"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def find_max_context(model_name: str, default_ctx: int) -> int:
    """二分查找最大支持的context大小"""
    print(f"  探测 {model_name} 的最大Context...")

    low, high = 4096, 131072
    max_working = 4096

    for ctx in CONTEXT_STEPS:
        if ctx > high:
            break
        result = test_model_at_context(model_name, ctx)
        if result.get("status") == "success":
            max_working = ctx
            print(f"    ✅ {ctx}: OK (生成: {result.get('gen_speed_tps', 0):.1f} t/s)")
        else:
            print(f"    ❌ {ctx}: {result.get('status', 'failed')}")
            break

    return max_working


def run_full_benchmark(model: Dict) -> Dict:
    """对单个模型运行完整性能测试"""
    model_name = model["name"]
    display_name = model["display"]
    default_ctx = model["ctx_default"]

    print(f"\n{'='*60}")
    print(f"测试模型: {display_name}")
    print(f"{'='*60}")

    results = {
        "model": model_name,
        "display_name": display_name,
        "timestamp": datetime.now().isoformat(),
        "context_tests": []
    }

    # 1. 先探测最大支持的context
    max_ctx = find_max_context(model_name, default_ctx)
    results["max_context_supported"] = max_ctx

    # 2. 在所有支持的context大小上详细测试
    test_contexts = [ctx for ctx in CONTEXT_STEPS if ctx <= max_ctx]
    if max_ctx not in test_contexts and max_ctx >= 4096:
        test_contexts.append(max_ctx)

    print(f"\n  详细测试 (最大支持: {max_ctx} tokens)...")
    for ctx in test_contexts:
        result = test_model_at_context(model_name, ctx)
        result["context_size"] = ctx
        results["context_tests"].append(result)

        if result.get("status") == "success":
            print(f"    {ctx:6d}: 预填充 {result.get('prompt_speed_tps', 0):7.1f} t/s | "
                  f"生成 {result.get('gen_speed_tps', 0):5.1f} t/s | "
                  f"TTFT {result.get('ttft_ms', 0)/1000:.2f}s")
        else:
            print(f"    {ctx:6d}: {result.get('status', 'failed')}")

    return results


def generate_markdown_report(all_results: List[Dict]) -> str:
    """生成Markdown格式的性能报告"""
    report = f"""# V100 (CUDA) 全模型性能基准测试报告

> **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
> **测试对象**: llama.cpp CUDA 后端 (V100 GPU)
> **服务器端口**: 8401
> **测试梯度**: 4K, 8K, 12K, 16K, 24K, 32K, 48K, 64K, 96K, 128K
> **测试指标**: 预填充速度 (t/s), 生成速度 (t/s), 首Token延迟 (s)

---

## 性能概览表

| 模型 | 最大Context | 最佳预填充 | 最佳生成 | 平均生成 |
|------|------------|-----------|---------|---------|
"""

    # 概览行
    for result in all_results:
        model_name = result["display_name"]
        max_ctx = result.get("max_context_supported", 0)

        speeds = [t for t in result["context_tests"] if t.get("status") == "success"]
        if speeds:
            best_prompt = max(t.get("prompt_speed_tps", 0) for t in speeds)
            best_gen = max(t.get("gen_speed_tps", 0) for t in speeds)
            avg_gen = sum(t.get("gen_speed_tps", 0) for t in speeds) / len(speeds)
            report += f"| {model_name:25s} | {max_ctx:6d} | {best_prompt:8.1f} | {best_gen:6.1f} | {avg_gen:6.1f} |\n"
        else:
            report += f"| {model_name:25s} | {max_ctx:6d} | N/A | N/A | N/A |\n"

    # 详细表格
    report += """
---

## 详细性能数据

"""

    for result in all_results:
        model_name = result["display_name"]
        max_ctx = result.get("max_context_supported", 0)

        report += f"""### {model_name}

**最大支持Context**: {max_ctx} tokens

| Context | Prompt Tokens | 预填充(t/s) | 生成(t/s) | TTFT(s) | 状态 |
|---------|--------------|------------|----------|---------|------|
"""

        for test in result["context_tests"]:
            ctx = test.get("context_size", 0)
            prompt_tok = test.get("prompt_tokens", 0)
            prompt_speed = test.get("prompt_speed_tps", 0)
            gen_speed = test.get("gen_speed_tps", 0)
            ttft = test.get("ttft_ms", 0) / 1000
            status = test.get("status", "unknown")

            if status == "success":
                report += f"| {ctx:7d} | {prompt_tok:12d} | {prompt_speed:10.1f} | {gen_speed:8.1f} | {ttft:7.2f} | ✅ |\n"
            else:
                report += f"| {ctx:7d} | - | - | - | - | ❌ {status} |\n"

        report += "\n"

    report += """---

## 关键发现

### 速度排名 (生成速度)
"""

    # 按平均生成速度排序
    model_speeds = []
    for result in all_results:
        speeds = [t.get("gen_speed_tps", 0) for t in result["context_tests"] if t.get("status") == "success"]
        if speeds:
            avg_speed = sum(speeds) / len(speeds)
            model_speeds.append((result["display_name"], avg_speed, max(speeds)))

    model_speeds.sort(key=lambda x: x[1], reverse=True)
    for i, (name, avg, best) in enumerate(model_speeds, 1):
        report += f"{i}. **{name}**: 平均 {avg:.1f} t/s, 最佳 {best:.1f} t/s\n"

    report += """
### Context支持排名
"""

    model_ctx = [(r["display_name"], r.get("max_context_supported", 0)) for r in all_results]
    model_ctx.sort(key=lambda x: x[1], reverse=True)
    for i, (name, ctx) in enumerate(model_ctx, 1):
        report += f"{i}. **{name}**: {ctx} tokens\n"

    report += f"""
---

*报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*测试脚本: benchmark_all_models.py*
"""

    return report


def main():
    """主函数: 运行所有模型的完整性能测试"""
    print("="*70)
    print("V100 (CUDA) 全模型性能基准测试")
    print("="*70)
    print(f"测试URL: {MODEL_URL}")
    print(f"测试梯度: {CONTEXT_STEPS}")
    print(f"模型数量: {len(MODELS)}")
    print("="*70)

    all_results = []

    for model in MODELS:
        try:
            result = run_full_benchmark(model)
            all_results.append(result)

            # 保存中间结果
            os.makedirs("eval_results/performance", exist_ok=True)
            with open(f"eval_results/performance/{model['name']}_perf.json", "w") as f:
                json.dump(result, f, indent=2)

        except Exception as e:
            print(f"\n❌ 测试 {model['name']} 失败: {e}")
            import traceback
            traceback.print_exc()

    # 保存完整结果
    with open("eval_results/v100_all_models_performance.json", "w") as f:
        json.dump(all_results, f, indent=2)

    # 生成Markdown报告
    report = generate_markdown_report(all_results)
    with open("eval_results/V100_ALL_MODELS_PERFORMANCE_REPORT.md", "w") as f:
        f.write(report)

    print("\n" + "="*70)
    print("测试完成!")
    print("="*70)
    print(f"JSON结果: eval_results/v100_all_models_performance.json")
    print(f"Markdown报告: eval_results/V100_ALL_MODELS_PERFORMANCE_REPORT.md")
    print(f"单个模型结果: eval_results/performance/*.json")


if __name__ == "__main__":
    main()
