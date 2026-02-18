#!/usr/bin/env python3
"""
报告生成器

从 JSONL 原始数据生成标准化的 Markdown 报告。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from .data_logger import DataLogger
from .metrics import MetricsCalculator


class ReportGenerator:
    """
    Stage 1 测试报告生成器

    从原始数据生成标准化的 Markdown 报告。

    Usage:
        generator = ReportGenerator()
        generator.generate_report(
            data_file="v100_cuda_20250218_120000.jsonl",
            output_file="V100_STAGE1_BENCHMARK_REPORT.md"
        )
    """

    def __init__(self, template_dir: str = None):
        """
        初始化报告生成器

        Args:
            template_dir: 模板目录（可选）
        """
        self.template_dir = template_dir

    def generate_report(self, data_file: str, output_file: str, title: str = "") -> str:
        """
        生成 Markdown 报告

        Args:
            data_file: JSONL 数据文件路径
            output_file: 输出 Markdown 文件路径
            title: 报告标题

        Returns:
            生成的报告内容
        """
        # 加载数据
        results = DataLogger.load_results(data_file)

        if not results:
            raise ValueError(f"No data found in {data_file}")

        # 提取元信息
        first_record = results[0]
        backend_type = first_record.get('backend_type', 'unknown')
        device = first_record.get('device', 'unknown')

        # 计算聚合指标
        aggregated = MetricsCalculator.aggregate_by_model(results)

        # 生成报告
        report_lines = []

        # 标题
        report_title = title or f"{backend_type.upper()}_{device} Stage 1 性能测试报告"
        report_lines.append(f"# {report_title}")
        report_lines.append("")
        report_lines.append(f"> **测试时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"> **后端类型**: {backend_type}")
        report_lines.append(f"> **设备**: {device}")
        report_lines.append(f"> **测试总数**: {len(results)}")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

        # 汇总表格
        report_lines.append("## 📊 模型性能排名")
        report_lines.append("")
        report_lines.append("| 排名 | 模型 | Prompt TPS | Generation TPS | 测试次数 |")
        report_lines.append("|:----:|------|:----------:|:--------------:|:--------:|")

        # 按平均总TPS排序
        sorted_models = sorted(
            aggregated.items(),
            key=lambda x: x[1]['total_tps'].mean,
            reverse=True
        )

        medals = ["🥇", "🥈", "🥉", "4", "5", "6", "7", "8", "9", "10"]

        for i, (model_id, metrics) in enumerate(sorted_models[:10]):
            medal = medals[i] if i < len(medals) else str(i + 1)
            prompt_tps = MetricsCalculator.format_tps(metrics['prompt_tps'].mean)
            gen_tps = MetricsCalculator.format_tps(metrics['generation_tps'].mean)
            test_count = metrics['test_count']

            report_lines.append(f"| {medal} | {model_id} | {prompt_tps} | {gen_tps} | {test_count} |")

        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

        # 详细数据
        report_lines.append("## 📈 详细指标")
        report_lines.append("")

        for model_id, metrics in sorted_models[:5]:
            report_lines.append(f"### {model_id}")
            report_lines.append("")
            report_lines.append(f"- **测试次数**: {metrics['test_count']}")
            report_lines.append(f"- **Prompt处理速度**: {metrics['prompt_tps'].mean:.1f} ± {metrics['prompt_tps'].std:.1f} tokens/s")
            report_lines.append(f"- **Token生成速度**: {metrics['generation_tps'].mean:.1f} ± {metrics['generation_tps'].std:.1f} tokens/s")
            report_lines.append(f"- **总吞吐量**: {metrics['total_tps'].mean:.1f} ± {metrics['total_tps'].std:.1f} tokens/s")
            report_lines.append("")

        report_lines.append("---")
        report_lines.append("")
        report_lines.append(f"*报告生成时间: {datetime.now().isoformat()}*")

        # 写入文件
        report_content = "\n".join(report_lines)
        Path(output_file).write_text(report_content, encoding='utf-8')

        return report_content

    def generate_comparison_report(self, data_files: List[str], output_file: str) -> str:
        """
        生成跨后端对比报告

        Args:
            data_files: 多个后端的 JSONL 文件路径列表
            output_file: 输出 Markdown 文件路径

        Returns:
            生成的报告内容
        """
        all_backends = []

        for data_file in data_files:
            results = DataLogger.load_results(data_file)
            if results:
                backend_type = results[0].get('backend_type', 'unknown')
                device = results[0].get('device', 'unknown')
                aggregated = MetricsCalculator.aggregate_by_model(results)
                all_backends.append({
                    'backend': f"{backend_type}_{device}",
                    'data': aggregated
                })

        # 生成对比报告
        report_lines = []
        report_lines.append("# 跨后端性能对比报告")
        report_lines.append("")
        report_lines.append(f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        report_lines.append("---")
        report_lines.append("")

        # 对比表格
        report_lines.append("## 📊 后端对比")
        report_lines.append("")

        # TODO: 实现更详细的对比逻辑

        report_content = "\n".join(report_lines)
        Path(output_file).write_text(report_content, encoding='utf-8')

        return report_content
