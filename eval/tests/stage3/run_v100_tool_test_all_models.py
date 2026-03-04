#!/usr/bin/env python3
"""
所有模型工具使用能力测试
生成标准化汇总报告
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tests.stage2_basic.tool_eval import run_tool_test

# 所有要测试的模型
MODELS = [
    {"name": "Youtu-VL-4B-Instruct-Q8_0.gguf", "display": "Youtu-VL-4B-Instruct-Q8_0", "size": "4B"},
    {"name": "Step3-VL-10B-Q4_K_M.gguf", "display": "Step3-VL-10B-Q4_K_M", "size": "10B"},
    {"name": "Nanbeige.Nanbeige4.1-3B.Q8_0.gguf", "display": "Nanbeige4.1-3B-Q8_0", "size": "3B"},
    {"name": "Qwen3-Coder-Next-Q4_K_M.gguf", "display": "Qwen3-Coder-Next-Q4_K_M", "size": "15B"},
    {"name": "Qwen3VL-4B-Instruct-Q8_0.gguf", "display": "Qwen3VL-4B-Instruct-Q8_0", "size": "4B"},
    {"name": "Qwen3-VL-8B-Instruct-abliterated-v2.Q8_0.gguf", "display": "Qwen3-VL-8B", "size": "8B"},
    {"name": "GLM-4.7-Flash-Q4_K_M.gguf", "display": "GLM-4.7-Flash-Q4_K_M", "size": "4.7B"},
    {"name": "GLM-4.7-Flash-REAP-23B-A3B-IQ4_NL.gguf", "display": "GLM-4.7-Flash-REAP-23B", "size": "23B"},
    {"name": "Qwen3-4B-Instruct-2507-UD-Q4_K_XL.gguf", "display": "Qwen3-4B", "size": "4B"},
    {"name": "MiniCPM-o-4_5-Q4_K_M.gguf", "display": "MiniCPM-o-4_5", "size": "4.5B"},
    {"name": "JoyAI-LLM-Flash-Q4_K_M.gguf", "display": "JoyAI-LLM-Flash", "size": "8B"},
    {"name": "Alibaba-Apsara.DASD-4B-Thinking.Q8_0.gguf", "display": "DASD-4B-Thinking", "size": "4B"},
    {"name": "Qwen3-0.6B-Q4_0.gguf", "display": "Qwen3-0.6B", "size": "0.6B"},
]

BASE_URL = "http://localhost:8401"

def get_grade(rate):
    """获取评级"""
    if rate >= 0.8:
        return "⭐⭐⭐⭐⭐"
    elif rate >= 0.6:
        return "⭐⭐⭐⭐"
    elif rate >= 0.4:
        return "⭐⭐⭐"
    elif rate >= 0.2:
        return "⭐⭐"
    else:
        return "⭐"

def test_single_model(model_info):
    """测试单个模型"""
    model_name = model_info["name"]
    print(f"\n{'='*70}")
    print(f"🔧 工具使用测试: {model_info['display']}")
    print(f"{'='*70}")

    try:
        result = run_tool_test(BASE_URL, model_name)

        print(f"  通过: {result['passed_tests']}/{result['total_tests']}")
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
        print(f"  ❌ 测试失败: {e}")
        return {
            "model": model_info['display'],
            "size": model_info['size'],
            "passed": 0,
            "total": 20,
            "pass_rate": 0,
            "duration": 0,
            "categories": {},
            "tests": [],
            "error": str(e)
        }

def print_summary_report(results):
    """打印汇总报告"""
    print("\n\n" + "="*100)
    print("📊 工具使用能力测试汇总报告")
    print("="*100)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试端点: {BASE_URL}")
    print(f"测试用例: 20个 (工具理解/工具调用/工具选择)")
    print("="*100)

    # 排序
    valid_results = [r for r in results if 'error' not in r]
    sorted_results = sorted(valid_results, key=lambda x: x['pass_rate'], reverse=True)

    # 打印排名表
    print("\n" + "  📊 排名（工具使用能力）")
    print("  " + "─"*96)
    print(f"  │{'排名':^6}│{'模型':^28}│{'理解':^8}│{'调用':^8}│{'选择':^8}│{'总计':^10}│{'评级':^12}│")
    print("  " + "├" + "─"*6 + "┼" + "─"*28 + "┼" + "─"*8 + "┼" + "─"*8 + "┼" + "─"*8 + "┼" + "─"*10 + "┼" + "─"*12 + "┤")

    medals = ["🥇", "🥈", "🥉", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13"]

    for i, r in enumerate(sorted_results):
        medal = medals[i] if i < len(medals) else str(i+1)
        cats = r.get('categories', {})

        # 提取分类得分
        understand = cats.get('工具理解', {'passed': 0, 'total': 1})
        call = cats.get('工具调用', {'passed': 0, 'total': 1})
        select = cats.get('工具选择', {'passed': 0, 'total': 1})

        understand_rate = understand['passed'] / understand['total'] * 100 if understand['total'] > 0 else 0
        call_rate = call['passed'] / call['total'] * 100 if call['total'] > 0 else 0
        select_rate = select['passed'] / select['total'] * 100 if select['total'] > 0 else 0

        total_rate = r['pass_rate'] * 100
        grade = get_grade(r['pass_rate'])

        # 截断模型名
        name = r['model'][:26] + ".." if len(r['model']) > 28 else r['model']

        print(f"  │{medal:^6}│{name:^28}│{understand_rate:>6.0f}% │{call_rate:>6.0f}% │{select_rate:>6.0f}% │{total_rate:>8.1f}% │{grade:^12}│")

    print("  " + "─"*96)

    # 打印失败的模型
    failed_results = [r for r in results if 'error' in r]
    if failed_results:
        print("\n  ❌ 测试失败的模型:")
        for r in failed_results:
            print(f"    - {r['model']}: {r.get('error', 'Unknown error')}")

    # TOP 3 分析
    print("\n" + "="*100)
    print("  🏆 TOP 3 模型")
    print("="*100)

    for i, r in enumerate(sorted_results[:3], 1):
        print(f"\n  {i}. {r['model']} ({r['size']})")
        print(f"     工具使用通过率: {r['pass_rate']*100:.1f}%")
        print(f"     耗时: {r['duration']:.1f}秒")

        # 强项分析
        cats = r.get('categories', {})
        best_cat = max(cats.items(), key=lambda x: x[1]['passed']/x[1]['total'] if x[1]['total'] > 0 else 0)
        print(f"     最强项: {best_cat[0]} ({best_cat[1]['passed']}/{best_cat[1]['total']})")

    # 保存结果
    output_dir = "/mnt/volume3/llama_cpp/eval_results/stage2"
    os.makedirs(output_dir, exist_ok=True)
    output_file = f"{output_dir}/tool_use_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    with open(output_file, "w") as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "endpoint": BASE_URL,
            "total_models": len(results),
            "successful": len(valid_results),
            "failed": len(failed_results),
            "results": sorted_results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n  💾 结果已保存: {output_file}")
    print("="*100)

def main():
    print("="*100)
    print("🔧 所有模型工具使用能力测试")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 测试端点: {BASE_URL}")
    print(f"📊 测试用例: 20个")
    print("="*100)

    all_results = []

    for i, model_info in enumerate(MODELS, 1):
        print(f"\n\n{'#'*100}")
        print(f"# 模型 {i}/{len(MODELS)}: {model_info['display']}")
        print(f"{'#'*100}")

        result = test_single_model(model_info)
        all_results.append(result)

        # 保存单个结果
        output_dir = "/mnt/volume3/llama_cpp/eval_results/stage2"
        os.makedirs(output_dir, exist_ok=True)
        safe_name = model_info['display'].replace('/', '_').replace(' ', '_')
        with open(f"{output_dir}/{safe_name}_tool_test.json", "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

    # 打印汇总报告
    print_summary_report(all_results)

if __name__ == "__main__":
    main()
