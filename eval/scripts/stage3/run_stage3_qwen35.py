#!/usr/bin/env python3
"""
Stage 3 综合能力测试 - Qwen3.5-35B-A3B
测试10项深度能力，每项100个测试用例 (共1000 cases)

用法:
  python3 run_stage3_qwen35.py              # 默认测试 Qwen3.5-35B-A3B-UD-Q4_K_XL
  python3 run_stage3_qwen35.py <模型名>     # 测试指定模型
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, '/mnt/volume3/llama_cpp')
from eval.tests.stage3_deep import (
    run_math_test, run_code_test, run_logic_test,
    run_commonsense_test, run_text_test, run_shell_test,
    run_reasoning_test, run_knowledge_test, run_safety_test, run_multiturn_test
)

BASE_URL = "http://localhost:8401"


def test_single_model(model_name: str) -> dict:
    """测试单个模型的所有Stage 3能力"""
    print(f"\n{'='*80}")
    print(f"🧪 Stage 3 综合能力测试: {model_name}")
    print(f"{'='*80}")

    results = {}

    # 1. 数学推理 (100 cases)
    print("\n  [1/10] 数学推理测试 (100 cases)...")
    try:
        results['math'] = run_math_test(BASE_URL, model_name)
        print(f"       通过: {results['math']['passed_tests']}/{results['math']['total_tests']} ({results['math']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['math'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0, 'duration_seconds': 0, 'tests': []}

    # 2. 代码生成 (100 cases)
    print("\n  [2/10] 代码生成测试 (100 cases)...")
    try:
        results['code'] = run_code_test(BASE_URL, model_name)
        print(f"       通过: {results['code']['passed_tests']}/{results['code']['total_tests']} ({results['code']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['code'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0, 'duration_seconds': 0, 'tests': []}

    # 3. 逻辑推理 (100 cases)
    print("\n  [3/10] 逻辑推理测试 (100 cases)...")
    try:
        results['logic'] = run_logic_test(BASE_URL, model_name)
        print(f"       通过: {results['logic']['passed_tests']}/{results['logic']['total_tests']} ({results['logic']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['logic'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0, 'duration_seconds': 0, 'tests': []}

    # 4. 常识问答 (100 cases)
    print("\n  [4/10] 常识问答测试 (100 cases)...")
    try:
        results['commonsense'] = run_commonsense_test(BASE_URL, model_name)
        print(f"       通过: {results['commonsense']['passed_tests']}/{results['commonsense']['total_tests']} ({results['commonsense']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['commonsense'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0, 'duration_seconds': 0, 'tests': []}

    # 5. 文本理解 (100 cases)
    print("\n  [5/10] 文本理解测试 (100 cases)...")
    try:
        results['text'] = run_text_test(BASE_URL, model_name)
        print(f"       通过: {results['text']['passed_tests']}/{results['text']['total_tests']} ({results['text']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['text'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0, 'duration_seconds': 0, 'tests': []}

    # 6. Linux Shell (100 cases)
    print("\n  [6/10] Linux Shell测试 (100 cases)...")
    try:
        results['shell'] = run_shell_test(BASE_URL, model_name)
        print(f"       通过: {results['shell']['passed_tests']}/{results['shell']['total_tests']} ({results['shell']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['shell'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0, 'duration_seconds': 0, 'tests': []}

    # 7. 推理规划 (100 cases)
    print("\n  [7/10] 推理规划测试 (100 cases)...")
    try:
        results['reasoning'] = run_reasoning_test(BASE_URL, model_name)
        print(f"       通过: {results['reasoning']['passed_tests']}/{results['reasoning']['total_tests']} ({results['reasoning']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['reasoning'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0, 'duration_seconds': 0, 'tests': []}

    # 8. 知识问答 (100 cases)
    print("\n  [8/10] 知识问答测试 (100 cases)...")
    try:
        results['knowledge'] = run_knowledge_test(BASE_URL, model_name)
        print(f"       通过: {results['knowledge']['passed_tests']}/{results['knowledge']['total_tests']} ({results['knowledge']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['knowledge'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0, 'duration_seconds': 0, 'tests': []}

    # 9. 安全评估 (100 cases)
    print("\n  [9/10] 安全评估测试 (100 cases)...")
    try:
        results['safety'] = run_safety_test(BASE_URL, model_name)
        print(f"       通过: {results['safety']['passed_tests']}/{results['safety']['total_tests']} ({results['safety']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['safety'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0, 'duration_seconds': 0, 'tests': []}

    # 10. 多轮对话 (100 cases)
    print("\n  [10/10] 多轮对话测试 (100 cases)...")
    try:
        results['multiturn'] = run_multiturn_test(BASE_URL, model_name)
        print(f"       通过: {results['multiturn']['passed_tests']}/{results['multiturn']['total_tests']} ({results['multiturn']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['multiturn'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0, 'duration_seconds': 0, 'tests': []}

    # 汇总
    total_tests = sum(r['total_tests'] for r in results.values())
    total_passed = sum(r['passed_tests'] for r in results.values())
    total_duration = sum(r.get('duration_seconds', 0) for r in results.values())

    summary = {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "endpoint": BASE_URL,
        "math": results['math'],
        "code": results['code'],
        "logic": results['logic'],
        "commonsense": results['commonsense'],
        "text": results['text'],
        "shell": results['shell'],
        "reasoning": results['reasoning'],
        "knowledge": results['knowledge'],
        "safety": results['safety'],
        "multiturn": results['multiturn'],
        "summary": {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_pass_rate": total_passed / total_tests if total_tests > 0 else 0,
            "total_duration": total_duration
        }
    }

    # 打印报告
    print_report(summary)

    return summary


def print_report(result: dict):
    """打印测试报告"""
    print(f"\n{'='*80}")
    print("📊 Stage 3 测试报告")
    print(f"{'='*80}")

    categories = [
        ('math', '数学推理', '🔢'),
        ('code', '代码生成', '💻'),
        ('logic', '逻辑推理', '🧠'),
        ('commonsense', '常识问答', '🌍'),
        ('text', '文本理解', '📚'),
        ('shell', 'Linux Shell', '🐧'),
        ('reasoning', '推理规划', '📐'),
        ('knowledge', '知识问答', '📖'),
        ('safety', '安全评估', '🛡️'),
        ('multiturn', '多轮对话', '💬')
    ]

    print(f"\n  ┌─────────────────────────────────────────────────────────────┐")
    print(f"  │  测试类别      │   通过/总计   │   通过率    │   耗时(秒)   │")
    print(f"  ├─────────────────────────────────────────────────────────────┤")

    for key, name, icon in categories:
        cat = result[key]
        passed = cat.get('passed_tests', 0)
        total = cat.get('total_tests', 100)
        rate = cat.get('pass_rate', 0) * 100
        duration = cat.get('duration_seconds', 0)
        print(f"  │  {icon} {name:<8}  │   {passed:3d}/{total:3d}     │   {rate:5.1f}%   │   {duration:8.1f}   │")

    summary = result['summary']
    total_rate = summary['total_pass_rate'] * 100
    total_duration = summary.get('total_duration', 0)
    print(f"  ├─────────────────────────────────────────────────────────────┤")
    print(f"  │  📊 总计        │   {summary['total_passed']:3d}/{summary['total_tests']:3d}     │   {total_rate:5.1f}%   │   {total_duration:8.1f}   │")
    print(f"  └─────────────────────────────────────────────────────────────┘")

    # 评级
    if total_rate >= 80:
        grade = "⭐⭐⭐⭐⭐ 优秀"
    elif total_rate >= 60:
        grade = "⭐⭐⭐⭐ 良好"
    elif total_rate >= 40:
        grade = "⭐⭐⭐ 及格"
    else:
        grade = "⭐⭐ 需改进"

    print(f"\n  🏆 评级: {grade}")


def save_result(result: dict):
    """保存测试结果"""
    output_dir = "/mnt/volume3/llama_cpp/eval/eval_results/stage3"
    os.makedirs(output_dir, exist_ok=True)

    model_name = result['model']
    safe_name = model_name.replace('/', '_').replace(' ', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"{output_dir}/{safe_name}_{timestamp}_stage3.json"

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n  💾 结果已保存: {output_file}")
    return output_file


def main():
    model_name = sys.argv[1] if len(sys.argv) > 1 else "Qwen3.5-35B-A3B-UD-Q4_K_XL"

    print("="*80)
    print("🧪 Qwen3.5 Stage 3 综合能力测试")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 测试端点: {BASE_URL}")
    print(f"📊 测试用例: 1000 (每项100 × 10项)")
    print(f"🎯 测试模型: {model_name}")
    print("="*80)

    try:
        result = test_single_model(model_name)
        save_result(result)

        # 返回码：通过门槛 60%
        if result['summary']['total_pass_rate'] >= 0.6:
            print("\n✅ 测试通过 (>= 60%)")
            sys.exit(0)
        else:
            print("\n❌ 测试未通过 (< 60%)")
            sys.exit(1)

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)


if __name__ == "__main__":
    main()
