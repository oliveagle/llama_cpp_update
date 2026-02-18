#!/usr/bin/env python3
"""
Stage 2 批量测试 - 所有模型 (CUDA/V100)

测试所有8个模型的基础能力 (100 cases × 10 categories)，生成对比报告
"""

import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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
]

BASE_URL = "http://localhost:8401"  # CUDA/V100


def test_single_model(model_info):
    """测试单个模型"""
    model_name = model_info["name"]
    print(f"\n{'='*70}")
    print(f"🤖 测试模型: {model_name}")
    print(f"   参数量: {model_info['size']}")
    print(f"{'='*70}")

    # 运行10类测试
    print("\n  [1/10] 代码能力测试 (10 cases)...")
    code_result = run_code_test(BASE_URL, model_name)

    print("  [2/10] 数学推理测试 (10 cases)...")
    math_result = run_math_test(BASE_URL, model_name)

    print("  [3/10] 文本理解测试 (10 cases)...")
    text_result = run_text_test(BASE_URL, model_name)

    print("  [4/10] 工具使用测试 (10 cases)...")
    tool_result = run_tool_test(BASE_URL, model_name)

    print("  [5/10] 逻辑推理测试 (10 cases)...")
    reasoning_result = run_reasoning_test(BASE_URL, model_name)

    print("  [6/10] 知识问答测试 (10 cases)...")
    knowledge_result = run_knowledge_test(BASE_URL, model_name)

    print("  [7/10] 翻译能力测试 (10 cases)...")
    translation_result = run_translation_test(BASE_URL, model_name)

    print("  [8/10] 摘要总结测试 (10 cases)...")
    summarization_result = run_summarization_test(BASE_URL, model_name)

    print("  [9/10] 安全合规测试 (10 cases)...")
    safety_result = run_safety_test(BASE_URL, model_name)

    print("  [10/10] 多轮对话测试 (10 cases)...")
    multiturn_result = run_multiturn_test(BASE_URL, model_name)

    # 汇总
    results = [code_result, math_result, text_result, tool_result, reasoning_result,
               knowledge_result, translation_result, summarization_result, safety_result, multiturn_result]
    total_tests = sum(r['total_tests'] for r in results)
    total_passed = sum(r['passed_tests'] for r in results)
    total_time = sum(r['duration_seconds'] for r in results)

    result = {
        "model": model_name,
        "size": model_info["size"],
        "timestamp": datetime.now().isoformat(),
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

    # 打印模型报告
    print_model_report(result)

    return result


def print_model_report(result):
    """打印单个模型报告"""
    print(f"\n{'='*70}")
    print(f"📊 {result['model']} 测试报告")
    print(f"{'='*70}")

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


def print_comparison_report(all_results):
    """打印对比报告"""
    print(f"\n\n{'='*80}")
    print("📈 模型对比报告 - Stage 2 基础能力测试 (V100 CUDA)")
    print(f"{'='*80}")

    # 排序
    sorted_results = sorted(all_results, key=lambda x: x['summary']['total_pass_rate'], reverse=True)

    print(f"\n  🏅 排名")
    print(f"  {'='*76}")
    print(f"  {'排名':<4} {'模型名称':<40} {'参数量':<8} {'通过率':<8} {'评级':<8}")
    print(f"  {'-'*76}")

    for i, r in enumerate(sorted_results, 1):
        rate = r['summary']['total_pass_rate'] * 100
        grade = "⭐⭐⭐⭐⭐" if rate >= 80 else "⭐⭐⭐⭐" if rate >= 60 else "⭐⭐⭐" if rate >= 40 else "⭐⭐"
        short_name = r['model'][:38] + ".." if len(r['model']) > 40 else r['model']
        print(f"  {i:<4} {short_name:<40} {r['size']:<8} {rate:>6.1f}%  {grade:<8}")

    print(f"  {'='*76}")

    # 各类别排名
    print(f"\n  📊 各类别 TOP 3")
    print(f"  {'─'*76}")

    categories = [
        ('code', '💻 代码能力'),
        ('math', '🔢 数学推理'),
        ('text', '📚 文本理解'),
        ('tool', '🔧 工具使用'),
        ('reasoning', '🧠 逻辑推理'),
        ('knowledge', '🌍 知识问答'),
        ('translation', '🌐 翻译能力'),
        ('summarization', '📝 摘要总结'),
        ('safety', '🛡️ 安全合规'),
        ('multiturn', '💬 多轮对话'),
    ]

    for key, label in categories:
        print(f"\n  {label}:")
        cat_sorted = sorted(all_results, key=lambda x: x[key]['pass_rate'], reverse=True)[:3]
        for i, r in enumerate(cat_sorted, 1):
            rate = r[key]['pass_rate'] * 100
            print(f"    {i}. {r['model'][:35]:<35} {rate:>6.1f}%")

    # 速度对比
    print(f"\n  ⚡ 测试速度对比")
    print(f"  {'─'*76}")
    speed_sorted = sorted(all_results, key=lambda x: x['summary']['total_duration'])
    print(f"  最快完成:")
    for i, r in enumerate(speed_sorted[:3], 1):
        dur = r['summary']['total_duration']
        print(f"    {i}. {r['model'][:35]:<35} {dur:>6.1f}s")

    # 综合推荐
    print(f"\n  💡 综合推荐")
    print(f"  {'='*76}")

    best_overall = sorted_results[0]
    print(f"  🥇 综合能力最强: {best_overall['model']} ({best_overall['summary']['total_pass_rate']*100:.1f}%)")

    for key, label in categories:
        best = max(all_results, key=lambda x: x[key]['pass_rate'])
        print(f"  {label.split()[0]} {label.split()[1]}最强: {best['model']} ({best[key]['pass_rate']*100:.1f}%)")


def generate_markdown_report(all_results, timestamp):
    """生成 Markdown 报告"""
    output_dir = "/mnt/volume3/llama_cpp/eval_results/stage2"
    os.makedirs(output_dir, exist_ok=True)

    sorted_results = sorted(all_results, key=lambda x: x['summary']['total_pass_rate'], reverse=True)

    md_content = f"""# Stage 2 基础能力测试报告 - V100 CUDA

**测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**测试端点**: {BASE_URL}
**测试框架**: 10个类别 × 10个案例 = 100个测试/模型

## 模型综合排名

| 排名 | 模型 | 参数量 | 通过/总计 | 通过率 | 评级 |
|:----:|------|:------:|:---------:|:------:|:----:|
"""

    for i, r in enumerate(sorted_results, 1):
        rate = r['summary']['total_pass_rate']
        grade = "⭐⭐⭐⭐⭐" if rate >= 0.8 else "⭐⭐⭐⭐" if rate >= 0.6 else "⭐⭐⭐" if rate >= 0.4 else "⭐⭐"
        md_content += f"| {i} | {r['model']} | {r['size']} | {r['summary']['total_passed']}/{r['summary']['total_tests']} | {rate*100:.1f}% | {grade} |\n"

    md_content += """
## 分类排名详情

"""
    categories = [
        ('code', '💻 代码能力'),
        ('math', '🔢 数学推理'),
        ('text', '📚 文本理解'),
        ('tool', '🔧 工具使用'),
        ('reasoning', '🧠 逻辑推理'),
        ('knowledge', '🌍 知识问答'),
        ('translation', '🌐 翻译能力'),
        ('summarization', '📝 摘要总结'),
        ('safety', '🛡️ 安全合规'),
        ('multiturn', '💬 多轮对话'),
    ]

    for key, label in categories:
        md_content += f"""### {label}

| 排名 | 模型 | 通过率 |
|:----:|------|:------:|
"""
        cat_sorted = sorted(all_results, key=lambda x: x[key]['pass_rate'], reverse=True)[:5]
        for i, r in enumerate(cat_sorted, 1):
            rate = r[key]['pass_rate'] * 100
            md_content += f"| {i} | {r['model']} | {rate:.1f}% |\n"
        md_content += "\n"

    md_content += f"""
## 测试类别说明

1. 💻 **代码能力** (10 cases) - Python代码生成 (HumanEval风格)
2. 🔢 **数学推理** (10 cases) - 数学问题求解 (GSM8K风格)
3. 📚 **文本理解** (10 cases) - 知识和理解 (MMLU/CMMLU风格)
4. 🔧 **工具使用** (10 cases) - 函数调用和API使用
5. 🧠 **逻辑推理** (10 cases) - 逻辑和因果推理
6. 🌍 **知识问答** (10 cases) - 世界知识和常识
7. 🌐 **翻译能力** (10 cases) - 多语言翻译 (中英互译)
8. 📝 **摘要总结** (10 cases) - 文本摘要和信息提取
9. 🛡️ **安全合规** (10 cases) - 安全边界和合规性
10. 💬 **多轮对话** (10 cases) - 上下文理解和多轮交互

---
*报告生成时间: {datetime.now().isoformat()}*
"""

    md_file = f"{output_dir}/V100_STAGE2_BENCHMARK_REPORT_{timestamp}.md"
    with open(md_file, "w") as f:
        f.write(md_content)

    print(f"\n💾 Markdown报告已保存: {md_file}")


def main():
    print("="*80)
    print("🧪 llama.cpp Stage 2 批量测试 - V100 CUDA (100 cases × 10 categories)")
    print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📍 测试端点: {BASE_URL}")
    print(f"📊 测试用例: 100 (10类别 × 10案例)")
    print("="*80)

    all_results = []

    for i, model_info in enumerate(MODELS, 1):
        print(f"\n{'#'*80}")
        print(f"# 模型 {i}/{len(MODELS)}: {model_info['name']}")
        print(f"{'#'*80}")

        try:
            result = test_single_model(model_info)
            all_results.append(result)

            # 保存单个模型结果
            output_dir = "/mnt/volume3/llama_cpp/eval_results/stage2"
            os.makedirs(output_dir, exist_ok=True)
            safe_name = model_info['name'].replace('/', '_').replace(' ', '_')
            with open(f"{output_dir}/{safe_name}_stage2.json", "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"\n  ❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()

    # 保存所有结果
    output_dir = "/mnt/volume3/llama_cpp/eval_results/stage2"
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    with open(f"{output_dir}/all_models_stage2_{timestamp}.json", "w") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)

    # 生成对比报告
    print_comparison_report(all_results)

    # 生成 Markdown 报告
    generate_markdown_report(all_results, timestamp)

    print(f"\n\n{'='*80}")
    print("✅ 所有模型测试完成")
    print(f"💾 结果保存: {output_dir}/")
    print("="*80)


if __name__ == "__main__":
    main()
