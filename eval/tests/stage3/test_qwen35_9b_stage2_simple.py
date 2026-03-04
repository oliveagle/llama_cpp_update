#!/usr/bin/env python3
"""
Qwen3.5 9B - Stage 2 综合能力测试
直接使用 eval.tests 下的评估器
"""

import sys
import os
import json
from datetime import datetime

# 确保能找到 eval 模块
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

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

BASE_URL = "http://localhost:8401"


def test_single_model(model_name: str):
    """测试单个模型"""
    print("=" * 80)
    print(f"🧪 Stage 2 单模型测试 - {model_name}")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 测试端点: {BASE_URL}")
    print(f"📊 测试用例: 100 (10个类别 × 10个案例)")
    print("=" * 80)

    # 运行10类测试
    print("\n[1/10] 💻 代码能力测试 (10 cases)...")
    code_result = run_code_test(BASE_URL, model_name)

    print("\n[2/10] 🔢 数学推理测试 (10 cases)...")
    math_result = run_math_test(BASE_URL, model_name)

    print("\n[3/10] 📚 文本理解测试 (10 cases)...")
    text_result = run_text_test(BASE_URL, model_name)

    print("\n[4/10] 🔧 工具使用测试 (10 cases)...")
    tool_result = run_tool_test(BASE_URL, model_name)

    print("\n[5/10] 🧠 逻辑推理测试 (10 cases)...")
    reasoning_result = run_reasoning_test(BASE_URL, model_name)

    print("\n[6/10] 🌍 知识问答测试 (10 cases)...")
    knowledge_result = run_knowledge_test(BASE_URL, model_name)

    print("\n[7/10] 🌐 翻译能力测试 (10 cases)...")
    translation_result = run_translation_test(BASE_URL, model_name)

    print("\n[8/10] 📝 摘要总结测试 (10 cases)...")
    summarization_result = run_summarization_test(BASE_URL, model_name)

    print("\n[9/10] 🛡️ 安全合规测试 (10 cases)...")
    safety_result = run_safety_test(BASE_URL, model_name)

    print("\n[10/10] 💬 多轮对话测试 (10 cases)...")
    multiturn_result = run_multiturn_test(BASE_URL, model_name)

    # 汇总
    results = {
        'code': code_result,
        'math': math_result,
        'text': text_result,
        'tool': tool_result,
        'reasoning': reasoning_result,
        'knowledge': knowledge_result,
        'translation': translation_result,
        'summarization': summarization_result,
        'safety': safety_result,
        'multiturn': multiturn_result
    }

    total_tests = sum(r['total_tests'] for r in results.values())
    total_passed = sum(r['passed_tests'] for r in results.values())
    total_time = sum(r['duration_seconds'] for r in results.values())

    result = {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "endpoint": BASE_URL,
        "code": {
            "passed": code_result['passed_tests'],
            "total": code_result['total_tests'],
            "pass_rate": code_result['pass_rate'],
            "duration": code_result['duration_seconds'],
            "details": code_result['tests']
        },
        "math": {
            "passed": math_result['passed_tests'],
            "total": math_result['total_tests'],
            "pass_rate": math_result['pass_rate'],
            "duration": math_result['duration_seconds'],
            "details": math_result['tests']
        },
        "text": {
            "passed": text_result['passed_tests'],
            "total": text_result['total_tests'],
            "pass_rate": text_result['pass_rate'],
            "duration": text_result['duration_seconds'],
            "details": text_result['tests']
        },
        "tool": {
            "passed": tool_result['passed_tests'],
            "total": tool_result['total_tests'],
            "pass_rate": tool_result['pass_rate'],
            "duration": tool_result['duration_seconds'],
            "details": tool_result['tests']
        },
        "reasoning": {
            "passed": reasoning_result['passed_tests'],
            "total": reasoning_result['total_tests'],
            "pass_rate": reasoning_result['pass_rate'],
            "duration": reasoning_result['duration_seconds'],
            "details": reasoning_result['tests']
        },
        "knowledge": {
            "passed": knowledge_result['passed_tests'],
            "total": knowledge_result['total_tests'],
            "pass_rate": knowledge_result['pass_rate'],
            "duration": knowledge_result['duration_seconds'],
            "details": knowledge_result['tests']
        },
        "translation": {
            "passed": translation_result['passed_tests'],
            "total": translation_result['total_tests'],
            "pass_rate": translation_result['pass_rate'],
            "duration": translation_result['duration_seconds'],
            "details": translation_result['tests']
        },
        "summarization": {
            "passed": summarization_result['passed_tests'],
            "total": summarization_result['total_tests'],
            "pass_rate": summarization_result['pass_rate'],
            "duration": summarization_result['duration_seconds'],
            "details": summarization_result['tests']
        },
        "safety": {
            "passed": safety_result['passed_tests'],
            "total": safety_result['total_tests'],
            "pass_rate": safety_result['pass_rate'],
            "duration": safety_result['duration_seconds'],
            "details": safety_result['tests']
        },
        "multiturn": {
            "passed": multiturn_result['passed_tests'],
            "total": multiturn_result['total_tests'],
            "pass_rate": multiturn_result['pass_rate'],
            "duration": multiturn_result['duration_seconds'],
            "details": multiturn_result['tests']
        },
        "summary": {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_pass_rate": total_passed / total_tests if total_tests > 0 else 0,
            "total_duration": total_time
        }
    }

    # 打印报告
    print_report(result)

    # 保存结果
    output_dir = "/mnt/volume3/llama_cpp/eval/results/stage2"
    os.makedirs(output_dir, exist_ok=True)
    safe_name = model_name.replace('/', '_').replace(' ', '_')
    output_file = f"{output_dir}/{safe_name}_stage2.json"

    with open(output_file, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n💾 结果已保存: {output_file}")

    return result


def print_report(result):
    """打印测试报告"""
    print("\n" + "=" * 80)
    print("📊 测试报告")
    print("=" * 80)

    summary = result['summary']

    print(f"\n  ┌─────────────────────────────────────────────────────────────┐")
    print(f"  │  测试类别    │   通过/总计   │   通过率    │   耗时(秒)   │")
    print(f"  ├─────────────────────────────────────────────────────────────┤")

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
        cat = result[cat_key]
        print(f"  │  {icon} {cat_name:6s} │   {cat['passed']:2d}/{cat['total']:2d}       │   {cat['pass_rate']*100:5.1f}%   │   {cat['duration']:8.1f}   │")

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

    # 分类详情
    print("\n  📋 分类详情")
    print("  " + "-" * 76)

    for cat_name, cat_key, icon in categories:
        cat = result[cat_key]
        print(f"\n  {icon} {cat_name} ({cat['passed']}/{cat['total']}):")
        for test in cat['details']:
            status = "✅" if test['passed'] else "❌"
            print(f"    {status} {test['name']}")


def main():
    # 选择要测试的后端
    global BASE_URL
    backend = "cuda" if len(sys.argv) < 2 else sys.argv[1].lower()

    if backend == "vulkan":
        BASE_URL = "http://localhost:8400"
    else:  # cuda
        BASE_URL = "http://localhost:8401"

    model_name = "Qwen3.5-9B-UD-Q4_K_XL"

    try:
        result = test_single_model(model_name)

        # 返回码：通过门槛 60%
        if result['summary']['total_pass_rate'] >= 0.6:
            sys.exit(0)
        else:
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
