#!/usr/bin/env python3
"""
Stage 1 测试报告生成脚本

从 JSONL 原始数据生成标准化的 Markdown 报告。

Usage:
    # 从最新数据文件生成报告
    python generate_report.py --backend cuda

    # 从指定文件生成
    python generate_report.py --data-file /path/to/results.jsonl

    # 跨后端对比报告
    python generate_report.py --compare vulkan cuda --data-files vulkan_*.jsonl cuda_*.jsonl
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime
from glob import glob

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.report_generator import ReportGenerator
from core.data_logger import DataLogger


def find_latest_data_file(backend: str, results_dir: Path = None) -> Path:
    """查找最新的数据文件"""
    if results_dir is None:
        results_dir = PROJECT_ROOT / "results" / "raw"

    pattern = f"{backend}_*.jsonl"
    files = list(results_dir.glob(pattern))

    if not files:
        raise FileNotFoundError(f"No data files found for backend: {backend}")

    return max(files, key=lambda p: p.stat().st_mtime)


def generate_single_report(backend: str, data_file: Path = None, output_file: Path = None):
    """生成单个后端报告"""
    if data_file is None:
        data_file = find_latest_data_file(backend)

    print(f"Using data file: {data_file}")

    # 自动推断设备名称
    device = "V100" if backend == "cuda" else "gfx1151"

    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = PROJECT_ROOT / "results" / f"{backend.upper()}_{device}_STAGE1_BENCHMARK_REPORT.md"

    generator = ReportGenerator()
    report = generator.generate_report(
        data_file=str(data_file),
        output_file=str(output_file),
        title=f"{backend.upper()} {device} Stage 1 性能测试报告"
    )

    print(f"\nReport generated: {output_file}")

    # 打印汇总
    print("\n" + "="*60)
    print("QUICK SUMMARY")
    print("="*60)

    results = DataLogger.load_results(str(data_file))
    if results:
        from core.metrics import MetricsCalculator
        aggregated = MetricsCalculator.aggregate_by_model(results)

        print(f"\nTotal models tested: {len(aggregated)}")
        print(f"Total test runs: {len(results)}")

        print("\nTop 5 by Total TPS:")
        sorted_models = sorted(
            aggregated.items(),
            key=lambda x: x[1]['total_tps'].mean,
            reverse=True
        )
        for i, (model_id, metrics) in enumerate(sorted_models[:5], 1):
            tps = metrics['total_tps'].mean
            print(f"  {i}. {model_id}: {tps:.1f} t/s")


def generate_comparison_report(backends: list, data_files: list, output_file: Path = None):
    """生成跨后端对比报告"""
    if len(backends) != len(data_files):
        print("Error: Number of backends must match number of data files")
        return

    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = PROJECT_ROOT / "results" / f"COMPARISON_{timestamp}_STAGE1_REPORT.md"

    generator = ReportGenerator()
    report = generator.generate_comparison_report(
        data_files=data_files,
        output_file=str(output_file)
    )

    print(f"\nComparison report generated: {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate Stage 1 Benchmark Reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate report from latest CUDA results
  python generate_report.py --backend cuda

  # Generate report from specific file
  python generate_report.py --data-file results/raw/cuda_V100_20250218_120000.jsonl

  # Generate comparison report
  python generate_report.py --compare vulkan cuda --data-files vulkan_*.jsonl cuda_*.jsonl
        """
    )

    parser.add_argument(
        "--backend",
        choices=['vulkan', 'cuda', 'rocm'],
        help="Backend to generate report for"
    )

    parser.add_argument(
        "--data-file",
        help="Specific data file to use"
    )

    parser.add_argument(
        "--output",
        help="Output file path"
    )

    parser.add_argument(
        "--compare",
        nargs='+',
        help="Backends to compare"
    )

    parser.add_argument(
        "--data-files",
        nargs='+',
        help="Data files for comparison"
    )

    args = parser.parse_args()

    # 对比报告
    if args.compare:
        if not args.data_files:
            print("Error: --data-files required for comparison")
            return

        output = Path(args.output) if args.output else None
        generate_comparison_report(args.compare, args.data_files, output)
        return

    # 单后端报告
    if not args.backend and not args.data_file:
        print("Error: Must specify --backend or --data-file")
        parser.print_help()
        return

    data_file = Path(args.data_file) if args.data_file else None
    output = Path(args.output) if args.output else None
    backend = args.backend or "unknown"

    generate_single_report(backend, data_file, output)


if __name__ == "__main__":
    main()
