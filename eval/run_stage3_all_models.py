#!/usr/bin/env python3
"""
Stage 3 综合能力测试 - 所有模型
测试所有模型的6项深度能力，每项100个测试用例 (共600 cases)

用法:
  python3 run_stage3_all_models.py              # 测试所有模型
  python3 run_stage3_all_models.py <模型名>     # 测试单个模型
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.stage3_deep import (
    run_math_test, run_code_test, run_logic_test,
    run_commonsense_test, run_text_test, run_shell_test
)

BASE_URL = "http://localhost:8400"

# 模型列表
MODELS = [
    {"name": "MiniCPM-o-4_5-Q4_K_M", "size": "4.5B"},
    {"name": "Qwen3-Coder-Next-Q4_K_M", "size": "15B"},
    {"name": "Qwen3VL-4B-Instruct-Q8_0", "size": "4B"},
    {"name": "Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0", "size": "8B"},
    {"name": "GLM-4.7-Flash-Q4_K_M", "size": "4.7B"},
    {"name": "GLM-4.7-Flash-REAP-23B-A3B-IQ4_NL", "size": "23B"},
    {"name": "Qwen3-4B-Instruct-2507-UD-Q4_K_XL", "size": "4B"},
    {"name": "MiroThinker-v1.5-30B.Q8_0", "size": "30B"},
    {"name": "Youtu-VL-4B-Instruct-Q8_0", "size": "4B"},
    {"name": "Step3-VL-10B-Q4_K_M", "size": "10B"},
    {"name": "Nanbeige4.1-3B-Q8_0", "size": "3B"},
]


def test_single_model(model_name: str) -> dict:
    """测试单个模型的所有Stage 3能力"""
    print(f"\n{'='*80}")
    print(f"🧪 Stage 3 综合能力测试: {model_name}")
    print(f"{'='*80}")

    results = {}

    # 1. 数学推理 (100 cases)
    print("\n  [1/6] 数学推理测试 (100 cases)...")
    try:
        results['math'] = run_math_test(BASE_URL, model_name)
        print(f"       通过: {results['math']['passed_tests']}/{results['math']['total_tests']} ({results['math']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['math'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0}

    # 2. 代码生成 (100 cases)
    print("\n  [2/6] 代码生成测试 (100 cases)...")
    try:
        results['code'] = run_code_test(BASE_URL, model_name)
        print(f"       通过: {results['code']['passed_tests']}/{results['code']['total_tests']} ({results['code']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['code'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0}

    # 3. 逻辑推理 (100 cases)
    print("\n  [3/6] 逻辑推理测试 (100 cases)...")
    try:
        results['logic'] = run_logic_test(BASE_URL, model_name)
        print(f"       通过: {results['logic']['passed_tests']}/{results['logic']['total_tests']} ({results['logic']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['logic'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0}

    # 4. 常识问答 (100 cases)
    print("\n  [4/6] 常识问答测试 (100 cases)...")
    try:
        results['commonsense'] = run_commonsense_test(BASE_URL, model_name)
        print(f"       通过: {results['commonsense']['passed_tests']}/{results['commonsense']['total_tests']} ({results['commonsense']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['commonsense'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0}

    # 5. 文本理解 (100 cases)
    print("\n  [5/6] 文本理解测试 (100 cases)...")
    try:
        results['text'] = run_text_test(BASE_URL, model_name)
        print(f"       通过: {results['text']['passed_tests']}/{results['text']['total_tests']} ({results['text']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['text'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0}

    # 6. Linux Shell (100 cases)
    print("\n  [6/6] Linux Shell测试 (100 cases)...")
    try:
        results['shell'] = run_shell_test(BASE_URL, model_name)
        print(f"       通过: {results['shell']['passed_tests']}/{results['shell']['total_tests']} ({results['shell']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['shell'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0}

    # 汇总
    total_tests = sum(r['total_tests'] for r in results.values())
    total_passed = sum(r['passed_tests'] for r in results.values())

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
        "summary": {
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_pass_rate": total_passed / total_tests if total_tests > 0 else 0
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
        ('math', '数学推理'),
        ('code', '代码生成'),
        ('logic', '逻辑推理'),
        ('commonsense', '常识问答'),
        ('text', '文本理解'),
        ('shell', 'Linux Shell')
    ]

    print(f"\n  ┌─────────────────────────────────────────────────────────────┐")
    print(f"  │  测试类别    │   通过/总计   │   通过率    │               │")
    print(f"  ├─────────────────────────────────────────────────────────────┤")

    for key, name in categories:
        cat = result[key]
        passed = cat.get('passed_tests', 0)
        total = cat.get('total_tests', 100)
        rate = cat.get('pass_rate', 0) * 100
        print(f"  │  {name:<8}    │   {passed:3d}/{total:3d}     │   {rate:5.1f}%   │               │")

    summary = result['summary']
    total_rate = summary['total_pass_rate'] * 100
    print(f"  ├─────────────────────────────────────────────────────────────┤")
    print(f"  │  总计        │   {summary['total_passed']:3d}/{summary['total_tests']:3d}     │   {total_rate:5.1f}%   │               │")
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
    output_dir = "/mnt/volume3/llama_cpp/eval_results/stage3"
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
    if len(sys.argv) > 1:
        # 测试单个模型
        model_name = sys.argv[1]
        result = test_single_model(model_name)
        save_result(result)
    else:
        # 测试所有模型
        print("="*80)
        print("🧪 GFX1151 Stage 3 综合能力测试 - 所有模型")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📍 测试端点: {BASE_URL}")
        print(f"📊 测试用例: 600 (每项100 × 6项)")
        print("="*80)

        all_results = []

        for i, model_info in enumerate(MODELS, 1):
            print(f"\n{'#'*80}")
            print(f"# [{i}/{len(MODELS)}] {model_info['name']}")
            print(f"{'#'*80}")

            try:
                result = test_single_model(model_info['name'])
                all_results.append(result)
                save_result(result)
            except Exception as e:
                print(f"\n  ❌ 测试失败: {e}")
                import traceback
                traceback.print_exc()

        print(f"\n\n{'='*80}")
        print("✅ 所有模型Stage 3测试完成")
        print(f"💾 结果保存: /mnt/volume3/llama_cpp/eval_results/stage3/")
        print("="*80)


if __name__ == "__main__":
    main()
