#!/usr/bin/env python3
"""
Stage 2 100-case测试 - gfx1151 (Vulkan端口8400)

测试模型的10个基础能力类别，每类10个案例:
1. 代码能力 (code) - HumanEval风格
2. 数学推理 (math) - GSM8K风格
3. 文本理解 (text) - 理解问答
4. 工具使用 (tool) - 工具调用
5. 逻辑推理 (reasoning) - 逻辑谜题
6. 知识问答 (knowledge) - 常识知识
7. 翻译能力 (translation) - 中英互译
8. 摘要总结 (summarization) - 文本摘要
9. 安全合规 (safety) - 安全检查
10. 多轮对话 (multiturn) - 上下文保持

用法: python3 run_stage2_gfx1151.py <模型名称>
"""

import sys
import os
import json
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from eval.tests.stage2_basic.code_eval import run_code_test
from eval.tests.stage2_basic.math_eval import run_math_test
from eval.tests.stage2_basic.text_eval import run_text_test
from eval.tests.stage2_basic.tool_eval import run_tool_test
from eval.tests.stage2_basic.reasoning_eval import run_reasoning_test
from eval.tests.stage2_basic.knowledge_eval import run_knowledge_test
from eval.tests.stage2_basic.translation_eval import run_translation_test
from eval.tests.stage2_basic.summarization_eval import run_summarization_test
from eval.tests.stage2_basic.safety_eval import run_safety_test
from eval.tests.stage2_basic.multiturn_eval import run_multiturn_test

BASE_URL = "http://localhost:8400"


def test_single_model(model_name: str):
    """测试单个模型 - 不切换"""
    print("=" * 80)
    print(f"🧪 Stage 2 100-case测试 - gfx1151")
    print(f"📊 模型: {model_name}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 端点: {BASE_URL}")
    print(f"📊 测试用例: 100 (10类别 × 10案例)")
    print("=" * 80)

    results = {}
    test_categories = [
        ("代码能力", "code", run_code_test),
        ("数学推理", "math", run_math_test),
        ("文本理解", "text", run_text_test),
        ("工具使用", "tool", run_tool_test),
        ("逻辑推理", "reasoning", run_reasoning_test),
        ("知识问答", "knowledge", run_knowledge_test),
        ("翻译能力", "translation", run_translation_test),
        ("摘要总结", "summarization", run_summarization_test),
        ("安全合规", "safety", run_safety_test),
        ("多轮对话", "multiturn", run_multiturn_test),
    ]

    for i, (name, key, test_func) in enumerate(test_categories, 1):
        print(f"\n[{i}/10] {name}测试 (10 cases)...")
        try:
            result = test_func(BASE_URL, model_name)
            results[key] = result
            print(f"✅ {name}: {result['passed_tests']}/{result['total_tests']} ({result['pass_rate']:.1f}%)")
        except Exception as e:
            print(f"❌ {name}测试失败: {e}")
            results[key] = {
                'passed_tests': 0,
                'total_tests': 10,
                'pass_rate': 0.0,
                'duration_seconds': 0,
                'tests': [],
                'error': str(e)
            }

    # 汇总
    total_tests = sum(r['total_tests'] for r in results.values())
    total_passed = sum(r['passed_tests'] for r in results.values())
    total_time = sum(r['duration_seconds'] for r in results.values())

    summary = {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "endpoint": BASE_URL,
        "backend": "vulkan",
        "device": "gfx1151",
        "total_tests": total_tests,
        "total_passed": total_passed,
        "total_pass_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
        "total_duration": total_time,
        "categories": results
    }

    # 保存结果
    output_dir = "/mnt/volume3/llama_cpp/eval_results/stage2/vulkan"
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"{output_dir}/{model_name}_stage2_100case_{timestamp}.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # 打印汇总
    print("\n" + "=" * 80)
    print("📊 测试结果汇总")
    print("=" * 80)
    print(f"模型: {model_name}")
    print(f"总测试数: {total_tests}")
    print(f"通过数: {total_passed}")
    print(f"通过率: {total_passed/total_tests*100:.1f}%")
    print(f"总用时: {total_time:.1f}秒")
    print("\n各类别得分:")
    for key, result in results.items():
        print(f"  {key}: {result['passed_tests']}/{result['total_tests']} ({result['pass_rate']:.1f}%)")
    print(f"\n结果保存: {output_file}")
    print("=" * 80)

    return summary


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 run_stage2_gfx1151.py <模型名称>")
        print("\n可用模型:")
        # List available models from presets
        import subprocess
        try:
            result = subprocess.run(['curl', '-s', 'http://localhost:8400/v1/models'],
                                  capture_output=True, text=True)
            if result.returncode == 0:
                data = json.loads(result.stdout)
                for model in data.get('data', []):
                    print(f"  - {model['id']}")
        except:
            print("  (无法获取模型列表，请检查服务是否运行)")
        sys.exit(1)

    model_name = sys.argv[1]
    test_single_model(model_name)
