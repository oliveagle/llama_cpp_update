#!/usr/bin/env python3
"""
Qwen3.5 0.8B - Stage 2 综合能力测试
使用现有的 Stage 2 测试框架，包含 10 个类别 × 10 个案例 = 100 个测试
"""

import sys
import os
import json
import subprocess
import time
import requests
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入 Stage 2 测试评估器
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


# 配置
MODEL_NAME = "Qwen3.5-0.8B-UD-Q8_K_XL"
BASE_URL_VULKAN = "http://localhost:8400"
BASE_URL_CUDA = "http://localhost:8401"
RESULTS_DIR = "/mnt/volume3/llama_cpp/eval/results/stage2"


def ensure_results_dir():
    """确保结果目录存在"""
    os.makedirs(RESULTS_DIR, exist_ok=True)


def test_single_backend(backend, base_url):
    """测试单个后端的完整能力"""
    print(f"\n{'='*80}")
    print(f"🚀 开始测试 Qwen3.5 9B - {backend.upper()} 后端")
    print(f"{'='*80}")
    print(f"📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 测试端点: {base_url}")
    print(f"📊 测试用例: 100 (10个类别 × 10个案例)")
    print()

    results = {}

    try:
        # 运行 10 类测试
        print("[1/10] 💻 代码能力测试 (10 cases)...")
        results['code'] = run_code_test(base_url, MODEL_NAME)

        print("\n[2/10] 🔢 数学推理测试 (10 cases)...")
        results['math'] = run_math_test(base_url, MODEL_NAME)

        print("\n[3/10] 📚 文本理解测试 (10 cases)...")
        results['text'] = run_text_test(base_url, MODEL_NAME)

        print("\n[4/10] 🔧 工具使用测试 (10 cases)...")
        results['tool'] = run_tool_test(base_url, MODEL_NAME)

        print("\n[5/10] 🧠 逻辑推理测试 (10 cases)...")
        results['reasoning'] = run_reasoning_test(base_url, MODEL_NAME)

        print("\n[6/10] 🌍 知识问答测试 (10 cases)...")
        results['knowledge'] = run_knowledge_test(base_url, MODEL_NAME)

        print("\n[7/10] 🌐 翻译能力测试 (10 cases)...")
        results['translation'] = run_translation_test(base_url, MODEL_NAME)

        print("\n[8/10] 📝 摘要总结测试 (10 cases)...")
        results['summarization'] = run_summarization_test(base_url, MODEL_NAME)

        print("\n[9/10] 🛡️ 安全合规测试 (10 cases)...")
        results['safety'] = run_safety_test(base_url, MODEL_NAME)

        print("\n[10/10] 💬 多轮对话测试 (10 cases)...")
        results['multiturn'] = run_multiturn_test(base_url, MODEL_NAME)

    except KeyboardInterrupt:
        print("\n⚠️  测试被用户中断")
        return None
    except Exception as e:
        print(f"\n❌ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        return None

    # 计算汇总信息
    total_tests = sum(r['total_tests'] for r in results.values())
    total_passed = sum(r['passed_tests'] for r in results.values())
    total_time = sum(r['duration_seconds'] for r in results.values())

    summary = {
        "model": MODEL_NAME,
        "backend": backend,
        "timestamp": datetime.now().isoformat(),
        "total_tests": total_tests,
        "total_passed": total_passed,
        "total_time_seconds": total_time,
        "pass_rate": total_passed / total_tests if total_tests > 0 else 0,
        "results": results
    }

    return summary


def print_report(summary):
    """打印测试报告"""
    print(f"\n{'='*80}")
    print(f"📊 Qwen3.5 9B - {summary['backend'].upper()} 测试报告")
    print(f"{'='*80}")

    # 表格标题
    print(f"\n{'':<2} {'测试类别':<8} | {'通过/总计':<8} | {'通过率':<8} | {'耗时(秒)':<8}")
    print(f"{'-'*65}")

    categories = [
        ("代码能力", "code", "💻"),
        ("数学推理", "math", "🔢"),
        ("文本理解", "text", "📚"),
        ("工具使用", "tool", "🔧"),
        ("逻辑推理", "reasoning", "🧠"),
        ("知识问答", "knowledge", "🌍"),
        ("翻译能力", "translation", "🌐"),
        ("摘要总结", "summarization", "📝"),
        ("安全合规", "safety", "🛡️"),
        ("多轮对话", "multiturn", "💬"),
    ]

    for cat_name, cat_key, icon in categories:
        if cat_key in summary['results']:
            r = summary['results'][cat_key]
            pass_rate = r['pass_rate'] * 100
            print(f"{icon:<2} {cat_name:<8} | {r['passed_tests']:<2}/{r['total_tests']:<2}       | {pass_rate:>5.1f}%      | {r['duration_seconds']:>8.1f}")

    print(f"{'-'*65}")

    # 汇总
    summary_line = (f"📊{'总计':<8} | {summary['total_passed']:<2}/{summary['total_tests']:<2}       "
                   f"| {summary['pass_rate']*100:>5.1f}%      | {summary['total_time_seconds']:>8.1f}")
    print(summary_line)

    # 评级
    if summary['pass_rate'] >= 0.8:
        grade = "⭐⭐⭐⭐⭐ 优秀"
    elif summary['pass_rate'] >= 0.6:
        grade = "⭐⭐⭐⭐  良好"
    elif summary['pass_rate'] >= 0.4:
        grade = "⭐⭐⭐    及格"
    else:
        grade = "⭐⭐      需改进"

    print(f"\n🏆 综合评级: {grade}")


def save_results(summary, filename):
    """保存结果到文件"""
    ensure_results_dir()
    output_file = os.path.join(RESULTS_DIR, filename)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2, default=str)

    print(f"\n💾 结果已保存: {output_file}")


def check_server(base_url):
    """检查服务器是否可用"""
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            return True
    except Exception:
        pass

    return False


def wait_for_server(base_url, max_wait=300):
    """等待服务器启动"""
    print(f"⏳ 等待服务器启动: {base_url}")

    for i in range(max_wait):
        if check_server(base_url):
            print(f"✅ 服务器已就绪")
            return True
        time.sleep(2)
        if i % 30 == 0:
            print(f"  等待 {i+2} 秒...")

    print(f"❌ 服务器启动超时")
    return False


def start_server(backend):
    """启动服务器"""
    if backend == "cuda":
        cmd = [
            "/home/oliveagle/opt/llama.cpp/build/bin/llama-server",
            "-m", "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-9B-GGUF/Qwen3.5-0.8B-UD-Q8_K_XL.gguf",
            "-c", "32768",
            "-ngl", "99",
            "-p", "8401",
            "-t", "4",
            "--batch-size", "512",
            "--mlock"
        ]
        env = os.environ.copy()
        env["CUDA_VISIBLE_DEVICES"] = "0"
        port = 8401
    else:  # vulkan
        cmd = [
            "/mnt/volume3/llama_cpp/core/downloads/llama-b8069/llama-server",
            "-m", "/mnt/volume3/modelscope_models/unsloth/Qwen3___5-9B-GGUF/Qwen3.5-0.8B-UD-Q8_K_XL.gguf",
            "-c", "32768",
            "-ngl", "99",
            "-p", "8400",
            "-t", "4",
            "--batch-size", "512",
            "--mlock"
        ]
        env = os.environ.copy()
        env["AMD_VULKAN_ICD"] = "/usr/share/vulkan/icd.d/amdvlk64.json"
        port = 8400

    print(f"🚀 启动服务器: {' '.join(cmd)}")
    process = subprocess.Popen(cmd, env=env,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              text=True)

    # 等待服务器启动
    base_url = f"http://localhost:{port}"
    if wait_for_server(base_url):
        return process, base_url
    else:
        process.terminate()
        try:
            process.wait(timeout=10)
        except:
            process.kill()
        return None, None


def stop_server(process):
    """停止服务器"""
    if process:
        print("⏹️ 停止服务器...")
        process.terminate()
        try:
            process.wait(timeout=15)
            print("✅ 服务器已停止")
        except:
            print("⚠️ 强制杀死服务器...")
            process.kill()
            try:
                process.wait(timeout=5)
            except:
                pass


def main():
    """主函数"""
    print(f"{'='*80}")
    print(f"🧪 Qwen3.5 9B - Stage 2 综合能力测试")
    print(f"{'='*80}")
    print(f"📅 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📊 测试用例: 100 (10个类别 × 10个案例)")
    print()

    # 选择后端
    if len(sys.argv) > 1:
        backend = sys.argv[1].lower()
        if backend == "cuda":
            base_url = BASE_URL_CUDA
        else:  # vulkan
            base_url = BASE_URL_VULKAN
    else:
        # 自动检测可用的后端
        if check_server(BASE_URL_VULKAN):
            backend = "vulkan"
            base_url = BASE_URL_VULKAN
            print(f"✅ 发现运行中的 Vulkan 服务器: {base_url}")
        elif check_server(BASE_URL_CUDA):
            backend = "cuda"
            base_url = BASE_URL_CUDA
            print(f"✅ 发现运行中的 CUDA 服务器: {base_url}")
        else:
            print("⏳ 未发现运行中的服务器。将启动 Vulkan 后端...")
            process, base_url = start_server("vulkan")
            if not process:
                print("❌ 服务器启动失败")
                return 1

    process = None  # 初始化 process 变量

    try:
        # 运行测试
        summary = test_single_backend(backend, base_url)

        if summary:
            print_report(summary)

            # 保存结果
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"qwen3.5-9b_{backend}_{timestamp}.json"
            save_results(summary, filename)

            return 0 if summary['pass_rate'] >= 0.6 else 1

    finally:
        # 停止服务器（如果是我们启动的）
        if process:
            stop_server(process)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
        sys.exit(1)
