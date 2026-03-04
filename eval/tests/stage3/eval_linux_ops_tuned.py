#!/usr/bin/env python3
"""
Linux/Shell 操作能力评估 - 专用调优版本

用途：探索特定模型的能力上限，使用针对该模型优化的配置

与通用测试的区别：
- 通用测试：标准化条件，用于横向对比不同模型
- 专用调优：最佳条件，用于了解模型能力上限
"""

import argparse
import json
import os
import sys

# 导入基础评估功能
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from eval_linux_ops import run_basic_test, run_deep_test, analyze_failures, BASIC_TEST_THRESHOLD
from eval_tools_capability import generate_report
from model_configs import get_tuning_config, list_available_configs


def main():
    parser = argparse.ArgumentParser(
        description="Linux/Shell 操作能力评估 - 专用调优版本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # JoyAI-LLM-Flash 专用调优测试
  python eval_linux_ops_tuned.py --model-url http://localhost:8401 --model-name JoyAI-LLM-Flash-Q4_K_M

  # 仅运行入门测试
  python eval_linux_ops_tuned.py --model-url http://localhost:8401 --model-name MODEL --basic-only

注意：
  本脚本使用针对特定模型优化的配置，结果不适用于横向对比。
  如需标准对比，请使用 eval_linux_ops.py
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
        "--basic-only",
        action="store_true",
        help="仅运行入门测试"
    )
    parser.add_argument(
        "--force-full",
        action="store_true",
        help="强制运行深度测试(忽略入门测试门槛)"
    )

    args = parser.parse_args()

    print("="*60)
    print("Linux/Shell 操作能力评估 - 专用调优版本")
    print("="*60)
    print(f"模型地址: {args.model_url}")
    print(f"模型名称: {args.model_name}")
    print(f"模式: 专用调优（探索能力上限）")
    print("="*60)

    # 检查是否有该模型的调优配置
    available_configs = list_available_configs()
    config = get_tuning_config(args.model_name)
    if config.tool_description_overrides or config.prompt_prefix:
        print(f"[INFO] 已加载 {args.model_name} 的调优配置")
        if config.prompt_prefix:
            print(f"       Prompt前缀: '{config.prompt_prefix[:30]}...'")
        if config.tool_description_overrides:
            print(f"       工具描述覆盖: {list(config.tool_description_overrides.keys())}")
    else:
        print(f"[INFO] {args.model_name} 无专用调优配置，使用默认")
        print(f"       可用配置: {', '.join(available_configs)}")

    # 阶段1: 入门测试（使用调优）
    basic_results, passed = run_basic_test(args.model_url, args.model_name, use_tuning=True)

    # 分析失败原因
    analyze_failures(basic_results)

    # 保存入门测试报告
    os.makedirs(args.output_dir, exist_ok=True)
    basic_report = generate_report(
        basic_results,
        f"{args.model_name}_Linux基础_调优",
        None
    )
    basic_report_file = os.path.join(
        args.output_dir,
        f"{args.model_name}_linux_basic_tuned_eval.md"
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
            print(f"\n[WARNING] 强制运行深度测试(入门测试未通过 {basic_results['accuracy']:.1%})")

        try:
            deep_results = run_deep_test(args.model_url, args.model_name)

            # 保存深度测试报告
            from linux_ops_test_cases import LINUX_OPS_TEST_CASES
            deep_report = generate_report(
                deep_results,
                f"{args.model_name}_Linux深度_调优",
                LINUX_OPS_TEST_CASES
            )
            deep_report_file = os.path.join(
                args.output_dir,
                f"{args.model_name}_linux_deep_tuned_eval.md"
            )
            with open(deep_report_file, 'w', encoding='utf-8') as f:
                f.write(deep_report)
            print(f"深度测试报告: {deep_report_file}")
        except Exception as e:
            print(f"\n[ERROR] 深度测试失败: {e}")
    else:
        print(f"\n[INFO] 入门测试未通过 ({basic_results['accuracy']:.1%} < {BASIC_TEST_THRESHOLD:.0%})，跳过深度测试")

    # 最终摘要
    print(f"\n{'='*60}")
    print("评估摘要 - 专用调优版本")
    print(f"{'='*60}")
    print(f"入门测试: {basic_results['passed']}/{basic_results['total']} ({basic_results['accuracy']:.1%})")
    if deep_results:
        print(f"深度测试: {deep_results['passed']}/{deep_results['total']} ({deep_results['accuracy']:.1%})")
    print(f"{'='*60}")
    print("\n注意：本结果为专用调优后的表现，不适用于与其他模型横向对比")
    print("如需标准对比，请使用: python eval_linux_ops.py")

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
