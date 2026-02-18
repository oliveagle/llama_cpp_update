#!/usr/bin/env python3
"""
测试3个路径错误的模型
MiniCPM-o-4_5, JoyAI-LLM-Flash, DASD-4B-Thinking
"""

import sys
import os
import json
import subprocess
import time
from datetime import datetime

sys.path.insert(0, '/mnt/volume3/llama_cpp/eval')
from tests.stage2_basic.tool_eval import run_tool_test

MODELS = [
    {
        "name": "MiniCPM-o-4_5-Q4_K_M.gguf",
        "display": "MiniCPM-o-4_5",
        "path": "/mnt/volume3/modelscope_models/OpenBMB/MiniCPM-o-4_5-gguf/MiniCPM-o-4_5-Q4_K_M.gguf"
    },
    {
        "name": "JoyAI-LLM-Flash-Q4_K_M.gguf",
        "display": "JoyAI-LLM-Flash",
        "path": "/mnt/volume3/modelscope_models/yairpatch/JoyAI-LLM-Flash-GGUF/JoyAI-LLM-Flash-Q4_K_M.gguf"
    },
    {
        "name": "Alibaba-Apsara.DASD-4B-Thinking.Q8_0.gguf",
        "display": "DASD-4B-Thinking",
        "path": "/mnt/volume3/modelscope_models/._____temp/DevQuasar/Alibaba-Apsara.DASD-4B-Thinking-GGUF/Alibaba-Apsara.DASD-4B-Thinking.Q8_0.gguf"
    },
]

SERVER_BIN = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
BASE_URL = "http://localhost:8401"

def test_model(model_info):
    """测试单个模型"""
    print(f"\n{'='*70}")
    print(f"🚀 启动: {model_info['display']}")
    print(f"{'='*70}")

    # 停止现有服务器
    subprocess.run("pkill -f 'llama-server.*port 8401' 2>/dev/null || true", shell=True)
    time.sleep(2)

    # 检查模型文件
    if not os.path.exists(model_info['path']):
        print(f"  ❌ 模型文件不存在: {model_info['path']}")
        return None

    # 启动服务器
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

    log_file = f"/mnt/volume3/llama_cpp/logs/{model_info['display']}_test.log"

    with open(log_file, "w") as f:
        proc = subprocess.Popen(cmd, stdout=f, stderr=subprocess.STDOUT)

    print(f"  PID: {proc.pid}")
    print(f"  等待启动...", end="", flush=True)

    for i in range(60):  # 增加到60秒
        time.sleep(1)
        if i % 10 == 0:
            print(f"{i}s", end="", flush=True)
        else:
            print(".", end="", flush=True)

        try:
            import requests
            resp = requests.get(f"{BASE_URL}/v1/models", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                if data.get('data') and len(data['data']) > 0:
                    print(f" ✅ 就绪")
                    break
        except:
            pass
    else:
        print(f" ❌ 超时")
        proc.terminate()
        return None

    # 测试
    time.sleep(2)
    try:
        result = run_tool_test(BASE_URL, model_info['name'])
        print(f"  ✅ 通过: {result['passed_tests']}/{result['total_tests']} ({result['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        result = {'passed_tests': 0, 'total_tests': 20, 'pass_rate': 0}

    # 停止服务器
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except:
        proc.kill()

    return {
        "model": model_info['display'],
        "passed": result['passed_tests'],
        "total": result['total_tests'],
        "pass_rate": result['pass_rate']
    }

def main():
    print("="*70)
    print("🔧 补测3个模型工具使用能力")
    print("="*70)

    results = []
    for model in MODELS:
        result = test_model(model)
        if result:
            results.append(result)
        time.sleep(3)

    print("\n" + "="*70)
    print("📊 结果汇总")
    print("="*70)
    for r in results:
        print(f"  {r['model']:<25} {r['passed']:>2}/{r['total']:>2} ({r['pass_rate']*100:>5.1f}%)")

if __name__ == "__main__":
    main()
