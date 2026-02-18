#!/usr/bin/env python3
"""
llama.cpp 模型三层评估框架 - 统一入口

Usage:
    # 运行全部三层测试
    python3 eval_model.py --model-url http://localhost:8401 --model-name MODEL

    # 只运行指定阶段
    python3 eval_model.py --stage 1 --model-url http://localhost:8401

    # 跳过性能测试，从能力测试开始
    python3 eval_model.py --start-stage 2 --model-url http://localhost:8401

    # 同时测试CUDA和Vulkan
    python3 eval_model.py --test-both
"""

import argparse
import sys
import os

# 确保框架在路径中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from framework.runner import EvaluationRunner
from framework.report import ReportGenerator


def main():
    parser = argparse.ArgumentParser(
        description="llama.cpp 模型三层评估框架",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
阶段说明:
  Stage 1: 基础性能测试 (吞吐量/速度/Context)
  Stage 2: 基础能力测试 (Linux/代码/数学/文本)
  Stage 3: 深度能力测试 (复杂场景全面评估)

示例:
  python3 eval_model.py --model-url http://localhost:8401 --model-name Qwen3-4B
  python3 eval_model.py --stage 1 --model-url http://localhost:8400 --output-dir ./reports
        """
    )

    parser.add_argument("--model-url", type=str, required=True,
                        help="模型API地址 (如 http://localhost:8401)")
    parser.add_argument("--model-name", type=str, default="Unknown",
                        help="模型名称")
    parser.add_argument("--stage", type=int, choices=[1, 2, 3],
                        help="只运行指定阶段 (1, 2, 或 3)")
    parser.add_argument("--start-stage", type=int, default=1, choices=[1, 2, 3],
                        help="从哪个阶段开始运行 (默认: 1)")
    parser.add_argument("--output-dir", type=str, default="./reports",
                        help="报告输出目录 (默认: ./reports)")
    parser.add_argument("--test-both", action="store_true",
                        help="同时测试CUDA(8401)和Vulkan(8400)")

    args = parser.parse_args()

    if args.test_both:
        # 测试CUDA
        print("="*60)
        print("测试 CUDA (V100) 端口 8401")
        print("="*60)
        run_evaluation("http://localhost:8401", args.model_name + "-CUDA",
                       args.start_stage, args.output_dir)

        print("\n")

        # 测试Vulkan
        print("="*60)
        print("测试 Vulkan (gfx1151) 端口 8400")
        print("="*60)
        run_evaluation("http://localhost:8400", args.model_name + "-Vulkan",
                       args.start_stage, args.output_dir)
    else:
        run_evaluation(args.model_url, args.model_name,
                      args.stage or args.start_stage, args.output_dir)


def run_evaluation(model_url: str, model_name: str, start_stage: int, output_dir: str):
    """运行评估"""
    runner = EvaluationRunner(model_url, model_name, output_dir)

    # 注册评估器 (未来会添加更多)
    try:
        from tests.stage1_performance.evaluator import PerformanceEvaluator
        runner.register_evaluator(PerformanceEvaluator)
    except ImportError:
        print("[WARNING] 性能测试模块未加载")

    try:
        from tests.stage2_basic.linux_ops import LinuxOpsEvaluator
        runner.register_evaluator(LinuxOpsEvaluator)
    except ImportError:
        print("[WARNING] Linux运维测试模块未加载")

    # 运行测试
    if len(runner.evaluators) == 0:
        print("[ERROR] 没有可用的测试模块")
        return 1

    results = runner.run_all(start_stage=start_stage)

    # 生成报告
    if results:
        report_gen = ReportGenerator(output_dir)
        report_file = report_gen.generate(model_name, results)
        print(f"\n📄 报告已生成: {report_file}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
