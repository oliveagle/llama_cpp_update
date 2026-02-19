#!/usr/bin/env python3
"""
Stage 2 工具使用能力测试 - 所有模型
独立脚本，只测试工具使用能力 (20 cases)

用法:
  python3 run_stage2_tool_all_models.py              # 测试所有模型
  python3 run_stage2_tool_all_models.py <模型名>     # 测试单个模型
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.stage2_basic.tool_eval import run_tool_test

BASE_URL = "http://localhost:8400"

# 所有模型列表
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
    """测试单个模型的工具使用能力"""
    print(f"\n{'='*70}")
    print(f"🔧 工具使用测试: {model_name}")
    print(f"{'='*70}")

    result = run_tool_test(BASE_URL, model_name)

    # 打印结果
    print(f"\n  通过: {result['passed_tests']}/{result['total_tests']}")
    print(f"  通过率: {result['pass_rate']*100:.1f}%")
    print(f"  耗时: {result['duration_seconds']:.1f}秒")

    # 分类统计
    categories = {}
    for test in result['tests']:
        cat = test['category']
        if cat not in categories:
            categories[cat] = {'total': 0, 'passed': 0}
        categories[cat]['total'] += 1
        if test['passed']:
            categories[cat]['passed'] += 1

    print("\n  分类详情:")
    for cat, stats in categories.items():
        rate = stats['passed'] / stats['total'] * 100
        print(f"    {cat}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")

    # 失败的测试
    failed = [t for t in result['tests'] if not t['passed']]
    if failed:
        print(f"\n  ❌ 失败用例 ({len(failed)}个):")
        for t in failed:
            print(f"    - {t['name']}")

    return result


def save_result(model_name: str, result: dict):
    """保存测试结果"""
    output_dir = "/mnt/volume3/llama_cpp/eval_results/stage2"
    os.makedirs(output_dir, exist_ok=True)

    safe_name = model_name.replace('/', '_').replace(' ', '_')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f"{output_dir}/{safe_name}_{timestamp}_tool_result.json"

    # 添加元数据
    data = {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "test_type": "tool",
        "endpoint": BASE_URL,
        "tool": {
            "passed": result['passed_tests'],
            "total": result['total_tests'],
            "pass_rate": result['pass_rate'],
            "duration": result['duration_seconds'],
            "details": result['tests']
        }
    }

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n  💾 结果已保存: {output_file}")
    return output_file


def print_summary(all_results: list):
    """打印汇总报告"""
    print(f"\n\n{'='*80}")
    print("📊 Stage 2 工具使用能力测试 - 汇总报告")
    print(f"{'='*80}")

    # 按通过率排序
    sorted_results = sorted(all_results, key=lambda x: x['pass_rate'], reverse=True)

    print(f"\n  🏅 排名")
    print(f"  {'='*76}")
    print(f"  {'排名':<4} {'模型名称':<45} {'通过/总计':<10} {'通过率':<10}")
    print(f"  {'-'*76}")

    for i, r in enumerate(sorted_results, 1):
        print(f"  {i:<4} {r['model']:<45} {r['passed_tests']}/{r['total_tests']:<8} {r['pass_rate']*100:>6.1f}%")

    print(f"  {'='*76}")

    # 统计
    avg_rate = sum(r['pass_rate'] for r in all_results) / len(all_results) * 100
    print(f"\n  📈 平均通过率: {avg_rate:.1f}%")

    # 分类统计
    print(f"\n  📂 分类表现 (平均通过率)")
    print(f"  {'-'*76}")

    # 收集所有分类数据
    all_categories = {}
    for r in all_results:
        for test in r['tests']:
            cat = test['category']
            if cat not in all_categories:
                all_categories[cat] = {'total': 0, 'passed': 0}
            all_categories[cat]['total'] += 1
            if test['passed']:
                all_categories[cat]['passed'] += 1

    for cat, stats in sorted(all_categories.items()):
        rate = stats['passed'] / stats['total'] * 100
        print(f"    {cat}: {rate:.1f}% ({stats['passed']}/{stats['total']})")


def test_all_models():
    """测试所有模型"""
    print("="*80)
    print("🔧 GFX1151 Stage 2 工具使用能力测试 - 所有模型")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 测试端点: {BASE_URL}")
    print(f"📊 测试用例: 20个")
    print("="*80)

    all_results = []

    for i, model_info in enumerate(MODELS, 1):
        model_name = model_info['name']
        print(f"\n{'#'*80}")
        print(f"# [{i}/{len(MODELS)}] {model_name}")
        print(f"{'#'*80}")

        try:
            result = test_single_model(model_name)
            result['model'] = model_name
            result['size'] = model_info['size']
            all_results.append(result)

            # 保存结果
            save_result(model_name, result)

        except Exception as e:
            print(f"\n  ❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

    # 打印汇总
    print_summary(all_results)

    # 保存汇总
    output_dir = "/mnt/volume3/llama_cpp/eval_results/stage2"
    summary_file = f"{output_dir}/tool_test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    print(f"\n\n{'='*80}")
    print(f"✅ 所有模型工具测试完成")
    print(f"💾 汇总保存: {summary_file}")
    print("="*80)

    return all_results


def main():
    if len(sys.argv) > 1:
        # 测试单个模型
        model_name = sys.argv[1]
        result = test_single_model(model_name)
        save_result(model_name, result)
    else:
        # 测试所有模型
        test_all_models()


if __name__ == "__main__":
    main()
