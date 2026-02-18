#!/usr/bin/env python3
"""
Linux/Shell 操作能力两阶段评估

阶段1: 入门测试 (30案例)
- 只有通过 >=40% 的模型才进入阶段2
- 用于快速筛选基础能力

阶段2: 深度测试 (300案例)
- 全面评估系统运维能力
- 只有入门测试通过才执行
"""

import argparse
import json
import os
import sys
import requests
from typing import Dict, List, Optional, Tuple

# 导入工具定义
from eval_tools_capability import (
    AVAILABLE_TOOLS,
    test_tool_calling_native,
    run_tools_evaluation,
    generate_report
)

# 阈值配置
BASIC_TEST_THRESHOLD = 0.40  # 40% 通过率门槛


def run_basic_test(model_url: str, model_name: str, use_tuning: bool = False) -> Tuple[Dict, bool]:
    """
    运行入门测试 (30案例)

    Args:
        use_tuning: 是否使用模型专用调优配置

    Returns:
        (results, passed): 结果字典和是否通过门槛
    """
    from linux_ops_basic_cases import get_basic_test_cases

    test_cases = get_basic_test_cases()
    print(f"\n{'='*60}")
    print(f"阶段1: Linux/Shell 入门测试 ({len(test_cases)} 案例)")
    print(f"{'='*60}")
    print(f"模型: {model_name}")
    print(f"通过门槛: {BASIC_TEST_THRESHOLD:.0%}")
    if use_tuning:
        print(f"模式: 专用调优 (探索能力上限)")
    else:
        print(f"模式: 通用测试 (标准对比)")
    print(f"{'='*60}\n")

    # 如果启用调优，先应用调优配置
    if use_tuning:
        try:
            from model_configs import get_tuning_config
            config = get_tuning_config(model_name)
            # 调优测试用例的prompt
            for tc in test_cases:
                tc['prompt'] = config.apply_to_prompt(tc['prompt'])
            print(f"[INFO] 已应用 {model_name} 的专用调优配置")
            print(f"       Prompt前缀: '{config.prompt_prefix[:20]}...'\n")
        except ImportError as e:
            print(f"[WARNING] 调优配置不可用: {e}\n")

    results = run_tools_evaluation(model_url, test_cases=test_cases, model_name=model_name)

    passed = results['accuracy'] >= BASIC_TEST_THRESHOLD

    print(f"\n{'='*60}")
    print("入门测试完成!")
    print(f"  总计: {results['total']}")
    print(f"  通过: {results['passed']}")
    print(f"  失败: {results['failed']}")
    print(f"  准确率: {results['accuracy']:.1%}")
    print(f"{'='*60}")

    if passed:
        print(f"✅ 通过门槛 ({BASIC_TEST_THRESHOLD:.0%})，进入深度测试")
    else:
        print(f"❌ 未通过门槛 ({BASIC_TEST_THRESHOLD:.0%})，跳过深度测试")
        print("\n建议:")
        print("  1. 该模型可能未针对系统运维场景训练")
        print("  2. 尝试使用提示工程方式而非原生工具调用")
        print("  3. 考虑使用专门训练的 DevOps 模型")

    return results, passed


def run_deep_test(model_url: str, model_name: str) -> Dict:
    """
    运行深度测试 (300案例)
    """
    from linux_ops_test_cases import LINUX_OPS_TEST_CASES

    print(f"\n{'='*60}")
    print(f"阶段2: Linux/Shell 深度测试 ({len(LINUX_OPS_TEST_CASES)} 案例)")
    print(f"{'='*60}\n")

    results = run_tools_evaluation(
        model_url,
        test_cases=LINUX_OPS_TEST_CASES,
        model_name=model_name
    )

    print(f"\n{'='*60}")
    print("深度测试完成!")
    print(f"  总计: {results['total']}")
    print(f"  通过: {results['passed']}")
    print(f"  失败: {results['failed']}")
    print(f"  准确率: {results['accuracy']:.1%}")
    print(f"{'='*60}")

    return results


def analyze_failures(basic_results: Dict) -> None:
    """分析入门测试失败原因"""
    print(f"\n{'='*60}")
    print("失败原因分析")
    print(f"{'='*60}\n")

    failures = [r for r in basic_results['details'] if not r['success']]

    # 统计失败类型
    no_tool_call = [r for r in failures if 'No tool call detected' in str(r.get('error', ''))]
    wrong_tool = [r for r in failures if 'Tool call incorrect' in str(r.get('error', ''))]
    other_errors = [r for r in failures if r not in no_tool_call and r not in wrong_tool]

    print(f"1. 未识别到工具调用: {len(no_tool_call)} 个")
    if no_tool_call:
        print("   典型失败案例:")
        for r in no_tool_call[:3]:
            print(f"     - {r['test_name']}: 模型直接回答而非调用工具")

    print(f"\n2. 工具调用错误: {len(wrong_tool)} 个")
    if wrong_tool:
        print("   典型失败案例:")
        for r in wrong_tool[:3]:
            print(f"     - {r['test_name']}: 调用了错误的工具")

    print(f"\n3. 其他错误: {len(other_errors)} 个")

    # 按类别统计
    print(f"\n{'='*60}")
    print("分类表现:")
    print(f"{'='*60}")

    from collections import defaultdict
    from linux_ops_basic_cases import get_basic_test_cases

    test_cases = get_basic_test_cases()
    case_categories = {r['test_name']: tc['category'] for tc in test_cases for r in basic_results['details'] if r['test_name'] == tc['name']}

    category_stats = defaultdict(lambda: {'total': 0, 'passed': 0})
    for r in basic_results['details']:
        cat = case_categories.get(r['test_name'], '未知')
        category_stats[cat]['total'] += 1
        if r['success']:
            category_stats[cat]['passed'] += 1

    for cat, stats in sorted(category_stats.items()):
        acc = stats['passed'] / stats['total'] if stats['total'] > 0 else 0
        status = "✅" if acc >= BASIC_TEST_THRESHOLD else "❌"
        print(f"  {status} {cat}: {stats['passed']}/{stats['total']} ({acc:.0%})")

    print(f"\n{'='*60}")
    print("诊断结论:")
    print(f"{'='*60}")

    if len(no_tool_call) > len(failures) * 0.7:
        print("🔍 主要问题: 模型倾向直接回答问题，而非使用工具调用")
        print("   可能原因:")
        print("   - 模型训练数据以对话为主，缺少工具调用场景")
        print("   - 系统提示词没有强调必须使用工具")
        print("   - 工具描述不够吸引模型注意力")
        print("\n   建议改进:")
        print("   - 在prompt中明确要求'请使用工具执行'")
        print("   - 使用提示工程方式而非原生工具调用")
        print("   - 考虑微调模型增加工具调用能力")
    elif len(wrong_tool) > len(failures) * 0.3:
        print("🔍 主要问题: 模型能理解需要工具，但选择了错误的工具")
        print("   可能原因:")
        print("   - 工具描述不够清晰")
        print("   - 工具之间区分度不够")
    else:
        print("🔍 混合问题: 模型在多个方面表现不佳")
        print("   建议全面评估模型能力")


def main():
    parser = argparse.ArgumentParser(
        description="Linux/Shell 操作能力两阶段评估",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 仅运行入门测试
  python eval_linux_ops.py --model-url http://localhost:8401 --model-name MODEL

  # 强制运行完整测试(跳过门槛检查)
  python eval_linux_ops.py --model-url http://localhost:8401 --model-name MODEL --force-full
        """
    )
    parser.add_argument(
        "--model-url",
        type=str,
        required=True,
        help="模型API地址"
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default="Unknown",
        help="模型名称"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./eval_results",
        help="输出目录"
    )
    parser.add_argument(
        "--force-full",
        action="store_true",
        help="强制运行完整测试(忽略入门测试门槛)"
    )
    parser.add_argument(
        "--basic-only",
        action="store_true",
        help="仅运行入门测试"
    )
    parser.add_argument(
        "--tuned",
        action="store_true",
        help="使用模型专用调优配置（探索能力上限，非标准测试）"
    )

    args = parser.parse_args()

    print("="*60)
    print("Linux/Shell 操作能力评估")
    print("="*60)
    print(f"模型地址: {args.model_url}")
    print(f"模型名称: {args.model_name}")
    if args.tuned:
        print(f"模式: 专用调优（探索能力上限）")
    else:
        print(f"模式: 通用测试（标准对比）")
    print("="*60)

    # 阶段1: 入门测试
    basic_results, passed = run_basic_test(args.model_url, args.model_name, use_tuning=args.tuned)

    # 分析失败原因
    analyze_failures(basic_results)

    # 保存入门测试报告
    os.makedirs(args.output_dir, exist_ok=True)
    basic_report = generate_report(
        basic_results,
        f"{args.model_name}_Linux基础",
        None  # 使用默认test_cases
    )
    basic_report_file = os.path.join(
        args.output_dir,
        f"{args.model_name}_linux_basic_eval.md"
    )
    with open(basic_report_file, 'w', encoding='utf-8') as f:
        f.write(basic_report)
    print(f"\n入门测试报告: {basic_report_file}")

    # 阶段2: 深度测试 (条件执行)
    deep_results = None
    if args.basic_only:
        print("\n[INFO] 仅运行入门测试，跳过深度测试")
    elif passed or args.force_full:
        if args.force_full and not passed:
            print("\n[WARNING] 强制运行深度测试(入门测试未通过)")

        try:
            deep_results = run_deep_test(args.model_url, args.model_name)

            # 保存深度测试报告
            from linux_ops_test_cases import LINUX_OPS_TEST_CASES
            deep_report = generate_report(
                deep_results,
                f"{args.model_name}_Linux深度",
                LINUX_OPS_TEST_CASES
            )
            deep_report_file = os.path.join(
                args.output_dir,
                f"{args.model_name}_linux_deep_eval.md"
            )
            with open(deep_report_file, 'w', encoding='utf-8') as f:
                f.write(deep_report)
            print(f"深度测试报告: {deep_report_file}")
        except Exception as e:
            print(f"\n[ERROR] 深度测试失败: {e}")
    else:
        print("\n[INFO] 入门测试未通过，跳过深度测试")

    # 最终摘要
    print(f"\n{'='*60}")
    print("评估摘要")
    print(f"{'='*60}")
    print(f"入门测试: {basic_results['passed']}/{basic_results['total']} ({basic_results['accuracy']:.1%})")
    if deep_results:
        print(f"深度测试: {deep_results['passed']}/{deep_results['total']} ({deep_results['accuracy']:.1%})")
    print(f"{'='*60}")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
