#!/usr/bin/env python3
"""
评估报告生成入口脚本
支持Stage 1/2/3等不同阶段的测试结果汇总

用法:
  python3 generate_report.py --stage 2              # 生成Stage 2完整报告
  python3 generate_report.py --stage 2 --format csv # 生成CSV格式
  python3 generate_report.py --stage 3 -o report.md # 保存到文件
"""

import sys
import os

# 添加lib目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from lib.report_generator import ReportGenerator  # type: ignore


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='生成模型评估对比报告',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 生成Stage 2完整报告
  python3 generate_report.py -s 2

  # 生成Stage 3 CSV数据
  python3 generate_report.py -s 3 -f csv

  # 保存完整报告到文件
  python3 generate_report.py -s 2 -o eval_results/stage2/report.md

  # 仅显示对比表格
  python3 generate_report.py -s 2 -f table
        """
    )

    parser.add_argument('--stage', '-s', type=int, required=True,
                        choices=[1, 2, 3],
                        help='测试阶段 (1=基础能力, 2=入门能力, 3=综合能力)')

    parser.add_argument('--output', '-o', type=str,
                        help='输出文件路径 (默认输出到stdout)')

    parser.add_argument('--base-dir', '-b', type=str,
                        default='/mnt/volume3/llama_cpp',
                        help='基础目录 (默认: /mnt/volume3/llama_cpp)')

    parser.add_argument('--format', '-f', type=str,
                        choices=['markdown', 'md', 'csv', 'table'],
                        default='markdown',
                        help='输出格式 (默认: markdown)')

    args = parser.parse_args()

    generator = ReportGenerator(args.base_dir)

    try:
        # 自动生成默认输出文件名 (包含GFX1151标识)
        if not args.output and args.format == 'markdown':
            args.output = f"eval_results/stage{args.stage}/GFX1151_STAGE{args.stage}_BENCHMARK_REPORT.md"

        if args.format in ['csv']:
            generator.load_stage_results(args.stage)
            output = generator.generate_csv(args.stage)

        elif args.format in ['table']:
            generator.load_stage_results(args.stage)
            output = generator.generate_comparison_table(args.stage)

        else:  # markdown
            # 更新报告标题以包含GFX1151
            output = generator.generate_full_report(args.stage, args.output)

        # 如果没有保存到文件，输出到stdout
        if not args.output or args.format != 'markdown':
            print(output)

        # 如果需要保存但格式不是markdown
        if args.output and args.format != 'markdown':
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"\n报告已保存: {args.output}")

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
