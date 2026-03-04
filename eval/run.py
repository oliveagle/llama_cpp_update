#!/usr/bin/env python3
"""
统一评估入口 - llama.cpp 模型能力评估
"""

import argparse
import sys
import os

# 添加 eval 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
from typing import List, Optional


def cmd_stage1(args):
    """Stage 1 - 性能基准测试"""
    from tests.stage1.performance_test import run_performance_test

    print(f"{'='*70}")
    print(f"Stage 1 - 性能基准测试")
    print(f"{'='*70}")
    print(f"模型：{args.model}")
    print(f"API 地址：{args.url}")
    print(f"Context 大小：{args.ctx_size}")
    print()

    results = run_performance_test(
        model_name=args.model,
        base_url=args.url,
        ctx_size=args.ctx_size,
    )

    # 保存结果
    output_file = save_results(
        results,
        f"stage1_{args.model}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        args.output_dir
    )
    print(f"\n结果已保存：{output_file}")


def cmd_stage2(args):
    """Stage 2 - 基础能力测试"""
    import subprocess

    print(f"{'='*70}")
    print(f"Stage 2 - 基础能力测试 (10 大类 30 cases)")
    print(f"{'='*70}")
    print(f"模型：{args.model}")
    print(f"API 地址：{args.url}")
    print()

    # 调用 capability_test_v2.py
    script_path = os.path.join(os.path.dirname(__file__), 'tests', 'stage2', 'capability_test_v2.py')
    cmd = [sys.executable, script_path, '--model', args.model, '--url', args.url]

    if args.all:
        # 测试所有模型
        pass
    else:
        subprocess.run(cmd)


def cmd_stage3(args):
    """Stage 3 - 深度能力测试"""
    import subprocess

    print(f"{'='*70}")
    print(f"Stage 3 - 深度能力测试 (工具调用/复杂任务)")
    print(f"{'='*70}")
    print(f"模型：{args.model}")
    print(f"API 地址：{args.url}")
    print()

    # 调用 eval_tools_capability.py
    script_path = os.path.join(os.path.dirname(__file__), 'eval_tools_capability.py')
    cmd = [sys.executable, script_path, '--model', args.model, '--url', args.url]
    subprocess.run(cmd)


def cmd_all(args):
    """运行全部评估"""
    print(f"{'='*70}")
    print(f"完整评估流程 - 所有阶段")
    print(f"{'='*70}")
    print(f"模型：{args.model}")
    print(f"API 地址：{args.url}")
    print()

    # 依次运行各阶段
    args.model = args.model
    args.url = args.url

    print("\n>>> 开始 Stage 1 ...")
    cmd_stage1(args)

    print("\n>>> 开始 Stage 2 ...")
    cmd_stage2(args)

    print("\n>>> 开始 Stage 3 ...")
    cmd_stage3(args)

    print("\n" + "="*70)
    print("全部评估完成!")
    print("="*70)


def cmd_benchmark(args):
    """性能基准测试 (多模型对比)"""
    from tools.benchmark_all_models import benchmark_models

    print(f"{'='*70}")
    print(f"多模型性能基准对比")
    print(f"{'='*70}")

    benchmark_models(
        output_dir=args.output_dir,
        ctx_size=args.ctx_size,
    )


def cmd_leaderboard(args):
    """查看排行榜"""
    leaderboard_path = os.path.join(os.path.dirname(__file__), 'eval_results', 'MODEL_LEADERBOARD.md')

    if os.path.exists(leaderboard_path):
        with open(leaderboard_path, 'r') as f:
            print(f.read())
    else:
        print("排行榜文件不存在")


def save_results(results: dict, filename: str, output_dir: str) -> str:
    """保存结果到文件"""
    import json

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{filename}.json")

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="llama.cpp 模型能力评估系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # Stage 1 - 性能测试
  python run.py stage1 --model Qwen3-0.6B

  # Stage 2 - 基础能力
  python run.py stage2 --model JoyAI-LLM-Flash

  # Stage 3 - 深度能力
  python run.py stage3 --model GLM-4.7-Flash

  # 完整评估
  python run.py all --model Qwen3-4B

  # 多模型对比
  python run.py benchmark --ctx-size 8192
        """
    )

    parser.add_argument(
        '--url',
        type=str,
        default='http://localhost:8400',
        help='llama.cpp API 地址 (默认：http://localhost:8400)'
    )

    parser.add_argument(
        '--output-dir',
        type=str,
        default='./results',
        help='输出目录 (默认：./results)'
    )

    subparsers = parser.add_subparsers(dest='command', help='评估类型')

    # Stage 1 子命令
    p1 = subparsers.add_parser('stage1', help='Stage 1 - 性能基准测试')
    p1.add_argument('--model', type=str, required=True, help='模型名称')
    p1.add_argument('--ctx-size', type=int, default=8192, help='Context 大小')
    p1.set_defaults(func=cmd_stage1)

    # Stage 2 子命令
    p2 = subparsers.add_parser('stage2', help='Stage 2 - 基础能力测试')
    p2.add_argument('--model', type=str, required=True, help='模型名称')
    p2.add_argument('--all', action='store_true', help='测试所有预定义模型')
    p2.set_defaults(func=cmd_stage2)

    # Stage 3 子命令
    p3 = subparsers.add_parser('stage3', help='Stage 3 - 深度能力测试')
    p3.add_argument('--model', type=str, required=True, help='模型名称')
    p3.set_defaults(func=cmd_stage3)

    # All 子命令
    p_all = subparsers.add_parser('all', help='运行全部评估')
    p_all.add_argument('--model', type=str, required=True, help='模型名称')
    p_all.set_defaults(func=cmd_all)

    # Benchmark 子命令
    p_bench = subparsers.add_parser('benchmark', help='多模型性能对比')
    p_bench.add_argument('--ctx-size', type=int, default=8192, help='Context 大小')
    p_bench.set_defaults(func=cmd_benchmark)

    # Leaderboard 子命令
    p_lb = subparsers.add_parser('leaderboard', help='查看排行榜')
    p_lb.set_defaults(func=cmd_leaderboard)

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 1

    args.func(args)
    return 0


if __name__ == '__main__':
    sys.exit(main())
