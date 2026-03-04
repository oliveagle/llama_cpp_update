#!/usr/bin/env python3
"""
Qwen3.5-27B Stage 2 基础能力测试
直接在 V100 上启动 llama-server 并运行 Stage 2 测试
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime
from pathlib import Path

# 配置
MODEL_PATH = "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-27B-GGUF/Qwen3.5-27B-Q4_K_M.gguf"
LLAMA_SERVER = "/home/oliveagle/opt/llama.cpp/build/bin/llama-server"
PORT = 8427  # 专用端口
BASE_URL = f"http://localhost:{PORT}"
MODEL_NAME = "Qwen3.5-27B-Q4_K_M"

# 添加 eval 模块路径
sys.path.insert(0, "/mnt/volume3/llama_cpp/eval")
from tests.stage2_basic.code_eval import run_code_test
from tests.stage2_basic.math_eval import run_math_test
from tests.stage2_basic.text_eval import run_text_test
from tests.stage2_basic.tool_eval import run_tool_test
from tests.stage2_basic.reasoning_eval import run_reasoning_test
from tests.stage2_basic.knowledge_eval import run_knowledge_test
from tests.stage2_basic.translation_eval import run_translation_test
from tests.stage2_basic.summarization_eval import run_summarization_test
from tests.stage2_basic.safety_eval import run_safety_test
from tests.stage2_basic.multiturn_eval import run_multiturn_test


def start_server():
    """启动 llama-server 加载 Qwen3.5-27B"""
    cmd = [
        LLAMA_SERVER,
        "-m", MODEL_PATH,
        "--ctx-size", "8192",
        "--n-gpu-layers", "99",
        "--port", str(PORT),
        "--flash-attn", "on",
        "--host", "127.0.0.1",
        "--jinja",
        "--reasoning-format", "auto",
        "--temp", "0.7",
        "--top-k", "20",
        "--top-p", "0.8",
    ]

    print(f"🚀 启动 llama-server...")
    print(f"   命令: {' '.join(cmd[:5])} ...")
    print(f"   模型: {MODEL_NAME}")
    print(f"   端口: {PORT}")
    print(f"   GPU: V100 (CUDA)")

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
    print("\n⏳ 等待服务器启动...")
    start_time = time.time()
    while time.time() - start_time < 300:  # 5分钟超时
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ 服务器就绪! (耗时 {time.time() - start_time:.1f}s)")
                return process
        except:
            pass

        # 检查进程是否还在运行
        if process.poll() is not None:
            print("❌ 服务器进程意外退出!")
            output = process.stdout.read()
            print(output)
            return None

        time.sleep(1)

    print("❌ 服务器启动超时!")
    return process


def stop_server(process):
    """停止服务器"""
    if process:
        print("\n🛑 停止服务器...")
        process.terminate()
        try:
            process.wait(timeout=10)
        except:
            process.kill()
            process.wait()
        print("✅ 服务器已停止")


def run_stage2_tests():
    """运行 Stage 2 测试"""
    print("\n" + "="*80)
    print(f"🧪 Stage 2 基础能力测试 - {MODEL_NAME}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 测试端点: {BASE_URL}")
    print(f"📊 测试用例: 100 (10个类别 × 10个案例)")
    print("="*80)

    results = {}
    categories = [
        ("代码能力", "code", run_code_test, "💻"),
        ("数学推理", "math", run_math_test, "🔢"),
        ("文本理解", "text", run_text_test, "📚"),
        ("工具使用", "tool", run_tool_test, "🔧"),
        ("逻辑推理", "reasoning", run_reasoning_test, "🧠"),
        ("知识问答", "knowledge", run_knowledge_test, "🌍"),
        ("翻译能力", "translation", run_translation_test, "🌐"),
        ("摘要总结", "summarization", run_summarization_test, "📝"),
        ("安全合规", "safety", run_safety_test, "🛡️"),
        ("多轮对话", "multiturn", run_multiturn_test, "💬"),
    ]

    for i, (name, key, test_func, icon) in enumerate(categories, 1):
        print(f"\n[{i}/10] {icon} {name}测试 (10 cases)...")
        try:
            result = test_func(BASE_URL, MODEL_NAME)
            results[key] = result
            print(f"   ✅ 通过: {result['passed_tests']}/{result['total_tests']} ({result['pass_rate']*100:.1f}%)")
        except Exception as e:
            print(f"   ❌ 测试失败: {e}")
            results[key] = {
                'passed_tests': 0,
                'total_tests': 10,
                'pass_rate': 0.0,
                'duration_seconds': 0,
                'tests': []
            }

    return results


def generate_report(results):
    """生成测试报告"""
    total_tests = sum(r['total_tests'] for r in results.values())
    total_passed = sum(r['passed_tests'] for r in results.values())
    total_time = sum(r['duration_seconds'] for r in results.values())

    report = {
        "model": MODEL_NAME,
        "timestamp": datetime.now().isoformat(),
        "endpoint": BASE_URL,
        "gpu": "V100",
        "backend": "CUDA",
        "stage": 2,
        "stage_name": "基础能力测试",
        "categories": {},
        "summary": {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_pass_rate": total_passed / total_tests if total_tests > 0 else 0,
            "total_duration": total_time
        }
    }

    category_names = {
        "code": "代码能力",
        "math": "数学推理",
        "text": "文本理解",
        "tool": "工具使用",
        "reasoning": "逻辑推理",
        "knowledge": "知识问答",
        "translation": "翻译能力",
        "summarization": "摘要总结",
        "safety": "安全合规",
        "multiturn": "多轮对话",
    }

    for key, result in results.items():
        report["categories"][key] = {
            "name": category_names.get(key, key),
            "passed": result['passed_tests'],
            "total": result['total_tests'],
            "pass_rate": result['pass_rate'],
            "duration": result['duration_seconds'],
            "details": result.get('tests', [])
        }

    return report


def print_report(report):
    """打印测试报告"""
    print("\n" + "="*80)
    print("📊 Stage 2 测试报告")
    print("="*80)

    summary = report['summary']

    print(f"\n  ┌─────────────────────────────────────────────────────────────┐")
    print(f"  │  测试类别    │   通过/总计   │   通过率    │   耗时(秒)   │")
    print(f"  ├─────────────────────────────────────────────────────────────┤")

    icons = {
        "code": "💻", "math": "🔢", "text": "📚", "tool": "🔧",
        "reasoning": "🧠", "knowledge": "🌍", "translation": "🌐",
        "summarization": "📝", "safety": "🛡️", "multiturn": "💬"
    }

    for key, cat in report['categories'].items():
        icon = icons.get(key, "📋")
        print(f"  │  {icon} {cat['name']:6s} │   {cat['passed']:2d}/{cat['total']:2d}       │   {cat['pass_rate']*100:5.1f}%   │   {cat['duration']:8.1f}   │")

    print(f"  ├─────────────────────────────────────────────────────────────┤")
    print(f"  │  📊 总计     │   {summary['total_passed']:2d}/{summary['total_tests']:2d}       │   {summary['total_pass_rate']*100:5.1f}%   │   {summary['total_duration']:8.1f}   │")
    print(f"  └─────────────────────────────────────────────────────────────┘")

    # 评级
    rate = summary['total_pass_rate']
    if rate >= 0.8:
        grade = "⭐⭐⭐⭐⭐ 优秀"
    elif rate >= 0.6:
        grade = "⭐⭐⭐⭐  良好"
    elif rate >= 0.4:
        grade = "⭐⭐⭐    及格"
    else:
        grade = "⭐⭐      需改进"

    print(f"\n  🏆 评级: {grade}")

    # Stage 2 门槛检查
    threshold = 0.6
    if rate >= threshold:
        print(f"  ✅ 通过 Stage 2 门槛 ({threshold*100:.0f}%)")
    else:
        print(f"  ❌ 未通过 Stage 2 门槛 ({threshold*100:.0f}%)")


def main():
    print("="*80)
    print(f"Qwen3.5-27B Stage 2 测试")
    print(f"模型: {MODEL_PATH}")
    print("="*80)

    # 检查模型文件
    if not os.path.exists(MODEL_PATH):
        print(f"❌ 模型文件不存在: {MODEL_PATH}")
        return 1

    # 启动服务器
    process = start_server()
    if not process:
        print("❌ 无法启动服务器")
        return 1

    try:
        # 运行测试
        results = run_stage2_tests()

        # 生成报告
        report = generate_report(results)

        # 打印报告
        print_report(report)

        # 保存结果
        output_dir = Path("/mnt/volume3/llama_cpp/eval/results")
        output_dir.mkdir(exist_ok=True)

        output_file = output_dir / f"qwen3.5-27b-v100-stage2.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 结果已保存: {output_file}")

        # 返回码
        if report['summary']['total_pass_rate'] >= 0.6:
            return 0
        else:
            return 1

    finally:
        stop_server(process)


if __name__ == "__main__":
    sys.exit(main())
