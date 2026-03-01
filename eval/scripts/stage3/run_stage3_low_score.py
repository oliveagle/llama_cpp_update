#!/usr/bin/env python3
"""
Stage 3 低分项目重测 - 文本理解 + 逻辑推理 + 推理规划
每项100个测试用例 (共300 cases)

用法:
  python3 run_stage3_low_score.py              # 默认测试 Qwen3.5-35B-A3B-UD-Q4_K_XL
  python3 run_stage3_low_score.py <模型名>     # 测试指定模型
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.stage3_deep import (
    run_text_test, run_logic_test, run_reasoning_test
)

BASE_URL = "http://localhost:8402"


def test_low_score_categories(model_name: str) -> dict:
    """测试三个低分类别"""
    print(f"\n{'='*80}")
    print(f"🧪 Stage 3 低分项目重测: {model_name}")
    print(f"{'='*80}")

    results = {}

    # 1. 文本理解 (100 cases) - 上次 37%
    print("\n  [1/3] 文本理解测试 (100 cases)...")
    print("        上次分数: 37.0%")
    try:
        results['text'] = run_text_test(BASE_URL, model_name)
        print(f"       本次通过: {results['text']['passed_tests']}/{results['text']['total_tests']} ({results['text']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['text'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0, 'duration_seconds': 0, 'tests': []}

    # 2. 逻辑推理 (100 cases) - 上次 60%
    print("\n  [2/3] 逻辑推理测试 (100 cases)...")
    print("        上次分数: 60.0%")
    try:
        results['logic'] = run_logic_test(BASE_URL, model_name)
        print(f"       本次通过: {results['logic']['passed_tests']}/{results['logic']['total_tests']} ({results['logic']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['logic'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0, 'duration_seconds': 0, 'tests': []}

    # 3. 推理规划 (100 cases) - 上次 60%
    print("\n  [3/3] 推理规划测试 (100 cases)...")
    print("        上次分数: 60.0%")
    try:
        results['reasoning'] = run_reasoning_test(BASE_URL, model_name)
        print(f"       本次通过: {results['reasoning']['passed_tests']}/{results['reasoning']['total_tests']} ({results['reasoning']['pass_rate']*100:.1f}%)")
    except Exception as e:
        print(f"       ❌ 测试失败: {e}")
        results['reasoning'] = {'passed_tests': 0, 'total_tests': 100, 'pass_rate': 0, 'duration_seconds': 0, 'tests': []}

    # 汇总
    total_tests = sum(r['total_tests'] for r in results.values())
    total_passed = sum(r['passed_tests'] for r in results.values())
    total_duration = sum(r.get('duration_seconds', 0) for r in results.values())

    summary = {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "endpoint": BASE_URL,
        "text": results['text'],
        "logic": results['logic'],
        "reasoning": results['reasoning'],
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
    print("📊 Stage 3 低分项目重测报告")
    print(f"{'='*80}")

    categories = [
        ('text', '文本理解', '📚', '37.0%'),
        ('logic', '逻辑推理', '🧠', '60.0%'),
        ('reasoning', '推理规划', '📐', '60.0%'),
    ]

    print(f"\n  ┌─────────────────────────────────────────────────────────────────┐")
    print(f"  │  测试类别      │   通过/总计   │   本次    │   上次    │ 变化  │")
    print(f"  ├─────────────────────────────────────────────────────────────────┤")

    for key, name, icon, last_score in categories:
        cat = result[key]
        passed = cat.get('passed_tests', 0)
        total = cat.get('total_tests', 100)
        rate = cat.get('pass_rate', 0) * 100
        last = float(last_score.replace('%', ''))
        change = rate - last
        change_str = f"+{change:.1f}%" if change >= 0 else f"{change:.1f}%"
        print(f"  │  {icon} {name:<8}  │   {passed:3d}/{total:3d}     │   {rate:5.1f}%  │   {last:5.1f}%  │ {change_str:>7} │")

    summary = result['summary']
    total_rate = summary['total_pass_rate'] * 100
    total_duration = summary.get('total_duration', 0)
    print(f"  ├─────────────────────────────────────────────────────────────────┤")
    print(f"  │  📊 总计        │   {summary['total_passed']:3d}/{summary['total_tests']:3d}     │   {total_rate:5.1f}%  │   52.3%   │       │")
    print(f"  └─────────────────────────────────────────────────────────────────┘")

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
    print(f"  ⏱️  总耗时: {total_duration:.1f} 秒")


def save_result(result: dict):
    """保存测试结果"""
    output_dir = "/mnt/volume3/llama_cpp/eval/eval_results/stage3"
    os.makedirs(output_dir, exist_ok=True)

    model_name = result['model']
    safe_name = model_name.replace('/', '_').replace(' ', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"{output_dir}/{safe_name}_{timestamp}_stage3_low_score.json"

    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n  💾 结果已保存: {output_file}")
    return output_file


def main():
    model_name = sys.argv[1] if len(sys.argv) > 1 else "Qwen3.5-35B-A3B-UD-Q4_K_XL"

    print("="*80)
    print("🧪 Qwen3.5 Stage 3 低分项目重测")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 测试端点: {BASE_URL}")
    print(f"📊 测试用例: 300 (文本100 + 逻辑100 + 推理100)")
    print(f"🎯 测试模型: {model_name}")
    print(f"⚙️  max_tokens: 4096")
    print("="*80)

    try:
        result = test_low_score_categories(model_name)
        save_result(result)

        # 返回码
        avg_rate = result['summary']['total_pass_rate']
        if avg_rate >= 0.6:
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
