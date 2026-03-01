#!/usr/bin/env python3
"""
Stage 1 吞吐量测试 - 批量运行脚本

自动运行所有测试（Prompt Processing、Token Generation、Context Scaling）
支持按后端批量测试多个模型。

Usage:
    # 测试单个模型
    python run_all_tests.py --backend vulkan --model-id minicpm-o-4_5

    # 测试多个模型
    python run_all_tests.py --backend cuda --models minicpm-o-4_5 glm-4-9b qwen2-5-7b

    # 生成报告
    python run_all_tests.py --backend cuda --generate-report
"""

import argparse
import sys
import subprocess
from pathlib import Path
from datetime import datetime

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = PROJECT_ROOT / "tests"

def run_test_script(test_name: str, backend: str, model_id: str, iterations: int = 3) -> bool:
    """运行单个测试脚本"""
    script_path = TESTS_DIR / f"test_{test_name}.py"

    if not script_path.exists():
        print(f"Error: Test script not found: {script_path}")
        return False

    cmd = [
        sys.executable,
        str(script_path),
        "--backend", backend,
        "--model-id", model_id,
        "--iterations", str(iterations)
    ]

    print(f"\n{'='*70}")
    print(f"Running: {test_name}")
    print(f"Model: {model_id} | Backend: {backend}")
    print('='*70)

    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    return result.returncode == 0


def run_all_tests(backend: str, model_id: str, iterations: int = 3) -> dict:
    """运行模型的所有测试"""
    results = {}

    tests = ["prompt_processing", "token_generation", "context_scaling"]

    for test in tests:
        success = run_test_script(test, backend, model_id, iterations)
        results[test] = "PASSED" if success else "FAILED"

    return results


def generate_report(backend: str, data_file: str = None):
    """生成测试报告"""
    from core.report_generator import ReportGenerator
    from core.data_logger import DataLogger

    results_dir = PROJECT_ROOT / "results" / "raw"

    # 如果没有指定数据文件，查找最新的
    if data_file is None:
        pattern = f"{backend}_*.jsonl"
        files = sorted(results_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

        if not files:
            print(f"No data files found for backend: {backend}")
            return

        data_file = files[0]

    print(f"\nGenerating report from: {data_file}")

    # 生成报告
    generator = ReportGenerator()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    device = "V100" if backend == "cuda" else "gfx1151"
    output_file = PROJECT_ROOT / "results" / f"{backend.upper()}_{device}_STAGE1_BENCHMARK_REPORT.md"

    report = generator.generate_report(
        data_file=str(data_file),
        output_file=str(output_file),
        title=f"{backend.upper()} {device} Stage 1 性能测试报告"
    )

    print(f"Report saved to: {output_file}")
    return output_file


def main():
    parser = argparse.ArgumentParser(
        description="Stage 1 Throughput Testing - Batch Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test single model
  python run_all_tests.py --backend vulkan --model-id minicpm-o-4_5

  # Test multiple models
  python run_all_tests.py --backend cuda --models minicpm-o-4_5 glm-4-9b qwen2-5-7b

  # Generate report from latest results
  python run_all_tests.py --backend cuda --generate-report
        """
    )

    parser.add_argument(
        "--backend",
        choices=['vulkan', 'cuda', 'rocm'],
        required=True,
        help="Backend to use"
    )

    parser.add_argument(
        "--model-id",
        help="Single model to test"
    )

    parser.add_argument(
        "--models",
        nargs='+',
        help="Multiple models to test"
    )

    parser.add_argument(
        "--iterations",
        type=int,
        default=3,
        help="Iterations per test (default: 3)"
    )

    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Generate report from results"
    )

    parser.add_argument(
        "--data-file",
        help="Specific data file for report generation"
    )

    args = parser.parse_args()

    # 生成报告模式
    if args.generate_report:
        generate_report(args.backend, args.data_file)
        return

    # 测试模式
    models = []
    if args.model_id:
        models.append(args.model_id)
    if args.models:
        models.extend(args.models)

    if not models:
        print("Error: Must specify --model-id or --models for testing")
        parser.print_help()
        return

    # 运行测试
    all_results = {}
    for model_id in models:
        results = run_all_tests(args.backend, model_id, args.iterations)
        all_results[model_id] = results

    # 打印汇总
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    for model_id, results in all_results.items():
        print(f"\n{model_id}:")
        for test, status in results.items():
            icon = "✓" if status == "PASSED" else "✗"
            print(f"  {icon} {test}: {status}")

    # 询问是否生成报告
    print(f"\n{'='*70}")
    response = input("Generate report from results? [Y/n]: ").strip().lower()
    if response in ['', 'y', 'yes']:
        generate_report(args.backend)


if __name__ == "__main__":
    main()
