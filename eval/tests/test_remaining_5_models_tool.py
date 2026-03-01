#!/usr/bin/env python3
"""
测试剩余5个模型的工具使用能力
Qwen3-4B, MiniCPM-o-4_5, JoyAI-LLM-Flash, DASD-4B-Thinking, Qwen3-0.6B
"""

import sys
import os
import json
import subprocess
import time
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, '/mnt/volume3/llama_cpp/eval')
from tests.stage2_basic.tool_eval import run_tool_test

# 5个待测试模型
MODELS = [
    {
        "name": "Qwen3-4B-Instruct-2507-UD-Q4_K_XL.gguf",
        "display": "Qwen3-4B",
        "size": "4B",
        "path": "/mnt/volume3/modelscope_models/unsloth/Qwen3-4B-Instruct-2507-GGUF/Qwen3-4B-Instruct-2507-UD-Q4_K_XL.gguf"
    },
    {
        "name": "MiniCPM-o-4_5-Q4_K_M.gguf",
        "display": "MiniCPM-o-4_5",
        "size": "4.5B",
        "path": "/mnt/volume3/hf_models/openbmb/MiniCPM-o-4_5-Q4_K_M.gguf"
    },
    {
        "name": "JoyAI-LLM-Flash-Q4_K_M.gguf",
        "display": "JoyAI-LLM-Flash",
        "size": "8B",
        "path": "/mnt/volume3/hf_models/nvidia-svc/JoyAI-LLM-Flash-Q4_K_M.gguf"
    },
    {
        "name": "Alibaba-Apsara.DASD-4B-Thinking.Q8_0.gguf",
        "display": "DASD-4B-Thinking",
        "size": "4B",
        "path": "/mnt/volume3/modelscope_models/Alibaba-Apsara-Research/DASD-4B-Thinking-GGUF/Alibaba-Apsara.DASD-4B-Thinking.Q8_0.gguf"
    },
    {
        "name": "Qwen3-0.6B-Q4_0.gguf",
        "display": "Qwen3-0.6B",
        "size": "0.6B",
        "path": "/mnt/volume3/modelscope_models/unsloth/Qwen3-0.6B-GGUF/Qwen3-0.6B-Q4_0.gguf"
    },
]

SERVER_BIN = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
BASE_URL = "http://localhost:8401"

def start_model_server(model_info):
    """启动模型服务器"""
    print(f"\n{'='*70}")
    print(f"🚀 启动服务器: {model_info['display']}")
    print(f"{'='*70}")

    # 停止现有服务器
    subprocess.run("pkill -f 'llama-server.*port 8401' 2>/dev/null || true", shell=True)
    time.sleep(2)

    # 启动新服务器
    cmd = [
        SERVER_BIN,
        "-m", model_info['path'],
        "--host", "0.0.0.0",
        "--port", "8401",
        "-c", "32768",
        "-n", "4096",
        "-ngl", "99",
        "-np", "1"
    ]

    log_file = f"/mnt/volume3/llama_cpp/logs/{model_info['display']}.log"

    with open(log_file, "w") as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)

    # 等待服务器启动
    print(f"  PID: {proc.pid}")
    print(f"  等待服务器启动...", end="", flush=True)

    for i in range(30):
        time.sleep(1)
        try:
            import requests
            resp = requests.get(f"{BASE_URL}/v1/models", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('data') and len(data['data']) > 0:
                    print(f" ✅ 就绪")
                    return proc
        except:
            pass
        print(".", end="", flush=True)

    print(" ❌ 启动失败")
    return None

def test_model(model_info):
    """测试单个模型"""
    print(f"\n{'#'*70}")
    print(f"# 🔧 工具使用测试: {model_info['display']}")
    print(f"{'#'*70}")

    # 启动服务器
    proc = start_model_server(model_info)
    if not proc:
        return {
            "model": model_info['display'],
            "size": model_info['size'],
            "passed": 0,
            "total": 20,
            "pass_rate": 0,
            "error": "Server failed to start"
        }

    # 等待模型完全加载
    time.sleep(3)

    try:
        # 运行工具测试
        result = run_tool_test(BASE_URL, model_info['name'])

        print(f"\n  ✅ 测试完成: {result['passed_tests']}/{result['total_tests']}")
        print(f"  通过率: {result['pass_rate']*100:.1f}%")

        # 分类统计
        categories = {}
        for test in result['tests']:
            cat = test['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'passed': 0}
            categories[cat]['total'] += 1
            if test['passed']:
                categories[cat]['passed'] += 1

        print("  分类统计:")
        for cat, stats in categories.items():
            rate = stats['passed'] / stats['total'] * 100
            print(f"    {cat}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")

        return {
            "model": model_info['display'],
            "size": model_info['size'],
            "passed": result['passed_tests'],
            "total": result['total_tests'],
            "pass_rate": result['pass_rate'],
            "duration": result['duration_seconds'],
            "categories": categories,
            "tests": result['tests']
        }

    except Exception as e:
        print(f"\n  ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return {
            "model": model_info['display'],
            "size": model_info['size'],
            "passed": 0,
            "total": 20,
            "pass_rate": 0,
            "error": str(e)
        }

    finally:
        # 停止服务器
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()

def print_results(results):
    """打印结果汇总"""
    print("\n\n" + "="*90)
    print("📊 V100 CUDA - 剩余5个模型工具使用测试结果")
    print("="*90)
    print(f"{'模型':^25}│{'工具理解':^12}│{'工具调用':^12}│{'工具选择':^12}│{'总计':^10}│{'评级':^10}")
    print("─"*90)

    for r in results:
        cats = r.get('categories', {})

        understand = cats.get('工具理解', {'passed': 0, 'total': 1})
        call = cats.get('工具调用', {'passed': 0, 'total': 1})
        select = cats.get('工具选择', {'passed': 0, 'total': 1})

        u_rate = understand['passed'] / understand['total'] * 100 if understand['total'] > 0 else 0
        c_rate = call['passed'] / call['total'] * 100 if call['total'] > 0 else 0
        s_rate = select['passed'] / select['total'] * 100 if select['total'] > 0 else 0

        total_rate = r['pass_rate'] * 100

        if total_rate >= 80:
            grade = "⭐⭐⭐⭐⭐"
        elif total_rate >= 60:
            grade = "⭐⭐⭐⭐"
        elif total_rate >= 40:
            grade = "⭐⭐⭐"
        else:
            grade = "⭐⭐"

        name = r['model'][:23] + ".." if len(r['model']) > 25 else r['model']

        print(f"{name:<25}│{u_rate:>10.0f}% │{c_rate:>10.0f}% │{s_rate:>10.0f}% │{total_rate:>8.1f}% │{grade:^10}")

    print("─"*90)

    # 保存结果
    output_dir = "/mnt/volume3/llama_cpp/eval_results/stage2"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/V100_remaining_5_models_tool_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "endpoint": BASE_URL,
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n💾 结果已保存: {output_file}")

def main():
    print("="*70)
    print("🔧 V100 CUDA - 剩余5个模型工具使用测试")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

    results = []

    for i, model_info in enumerate(MODELS, 1):
        print(f"\n\n{'='*70}")
        print(f"模型 {i}/5: {model_info['display']}")
        print(f"{'='*70}")

        result = test_model(model_info)
        results.append(result)

        # 保存单个结果
        output_dir = "/mnt/volume3/llama_cpp/eval_results/stage2"
        safe_name = model_info['display'].replace('/', '_').replace(' ', '_')
        with open(f"{output_dir}/V100_{safe_name}_tool_test.json", "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        # 间隔冷却
        if i < len(MODELS):
            print(f"\n  ⏳ 冷却3秒...")
            time.sleep(3)

    # 打印汇总
    print_results(results)

    print("\n" + "="*70)
    print("✅ 所有5个模型测试完成")
    print("="*70)

if __name__ == "__main__":
    main()
