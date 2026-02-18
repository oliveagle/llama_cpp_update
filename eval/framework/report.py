#!/usr/bin/env python3
"""
报告生成器
"""

import os
import json
from datetime import datetime
from typing import List
from .base import StageResult


class ReportGenerator:
    """生成评估报告"""

    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate(self, model_name: str, results: List[StageResult]) -> str:
        """生成完整报告"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(
            self.output_dir,
            f"{model_name}_evaluation_{timestamp}.md"
        )

        content = self._generate_markdown(model_name, results)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # 同时生成JSON便于程序处理
        json_file = report_file.replace('.md', '.json')
        self._generate_json(model_name, results, json_file)

        return report_file

    def _generate_markdown(self, model_name: str, results: List[StageResult]) -> str:
        """生成Markdown报告"""
        lines = [
            f"# {model_name} 模型评估报告",
            f"",
            f"**评估时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"",
            "---",
            f"",
            "## 总体概况",
            f"",
        ]

        # 汇总表
        lines.extend([
            "| 阶段 | 名称 | 测试数 | 通过 | 准确率 | 状态 |",
            "|------|------|--------|------|--------|------|",
        ])

        for r in results:
            status = "✅" if r.passed_threshold else "❌"
            lines.append(
                f"| {r.stage_number} | {r.stage_name} | {r.total_tests} | "
                f"{r.passed_tests} | {r.pass_rate:.1%} | {status} |"
            )

        lines.append("")

        # 详细结果
        for r in results:
            lines.extend([
                f"---",
                f"",
                f"## 阶段 {r.stage_number}: {r.stage_name}",
                f"",
                f"- **测试总数**: {r.total_tests}",
                f"- **通过**: {r.passed_tests}",
                f"- **失败**: {r.failed_tests}",
                f"- **准确率**: {r.pass_rate:.1%}",
                f"- **门槛**: {r.threshold_percentage:.0%}",
                f"- **状态**: {'✅ 通过' if r.passed_threshold else '❌ 未通过'}",
                f"",
            ])

            if r.metadata:
                lines.append("### 元数据")
                lines.append("")
                for key, value in r.metadata.items():
                    lines.append(f"- **{key}**: {value}")
                lines.append("")

            # 失败的测试项
            failed_tests = [t for t in r.test_results if not t.passed]
            if failed_tests:
                lines.extend([
                    "### 失败项详情",
                    "",
                    "| 测试名称 | 类别 | 错误信息 |",
                    "|----------|------|----------|",
                ])
                for t in failed_tests[:10]:  # 只显示前10个
                    error = t.error_message or "-"
                    lines.append(f"| {t.name} | {t.category} | {error[:50]}... |")
                lines.append("")

        return "\n".join(lines)

    def _generate_json(self, model_name: str, results: List[StageResult], filepath: str):
        """生成JSON报告"""
        data = {
            "model_name": model_name,
            "timestamp": datetime.now().isoformat(),
            "stages": []
        }

        for r in results:
            data["stages"].append({
                "stage_number": r.stage_number,
                "stage_name": r.stage_name,
                "total_tests": r.total_tests,
                "passed_tests": r.passed_tests,
                "failed_tests": r.failed_tests,
                "pass_rate": r.pass_rate,
                "threshold": r.threshold_percentage,
                "passed": r.passed_threshold,
                "duration_seconds": r.duration_seconds,
                "metadata": r.metadata,
                "test_results": [
                    {
                        "name": t.name,
                        "category": t.category,
                        "passed": t.passed,
                        "duration_ms": t.duration_ms,
                        "error_message": t.error_message
                    }
                    for t in r.test_results
                ]
            })

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
