#!/usr/bin/env python3
"""
通用评估报告生成器
支持Stage 1/2/3等不同阶段的测试结果汇总和对比
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ModelResult:
    """单个模型的测试结果"""
    name: str
    stage: int
    timestamp: str
    test_id: str
    categories: Dict[str, Dict] = field(default_factory=dict)  # code/math/text等
    summary: Dict = field(default_factory=dict)
    metadata: Dict = field(default_factory=dict)
    raw_data: Dict = field(default_factory=dict)

    @property
    def total_passed(self) -> int:
        return self.summary.get('total_passed', 0)

    @property
    def total_tests(self) -> int:
        return self.summary.get('total_tests', 0)

    @property
    def total_pass_rate(self) -> float:
        return self.summary.get('total_pass_rate', 0.0)

    def get_category_rate(self, category: str) -> float:
        """获取指定类别的通过率"""
        if category in self.categories:
            return self.categories[category].get('pass_rate', 0.0)
        return 0.0

    def get_category_score(self, category: str) -> Tuple[int, int]:
        """获取指定类别的通过数/总数"""
        if category in self.categories:
            cat = self.categories[category]
            return (cat.get('passed', 0), cat.get('total', 0))
        return (0, 0)


@dataclass
class StageConfig:
    """阶段配置"""
    stage: int
    name: str
    categories: List[str]  # 测试类别列表，如 ['code', 'math', 'text']
    category_names: Dict[str, str]  # 类别显示名称
    results_dir: str
    file_pattern: str  # 结果文件匹配模式


class ReportGenerator:
    """通用报告生成器"""

    # 预定义的阶段配置
    STAGE_CONFIGS = {
        1: StageConfig(
            stage=1,
            name="基础能力测试",
            categories=['functionality', 'context', 'performance'],
            category_names={
                'functionality': '功能测试',
                'context': '上下文',
                'performance': '性能'
            },
            results_dir="eval_results/stage1",
            file_pattern="*_stage1.json"
        ),
        2: StageConfig(
            stage=2,
            name="入门能力测试",
            categories=['code', 'math', 'text', 'tool'],
            category_names={
                'code': '代码能力',
                'math': '数学推理',
                'text': '文本理解',
                'tool': '工具使用'
            },
            results_dir="eval_results/stage2",
            file_pattern="*_result.json"  # 会匹配 *_result.json 但 exclude *_tool_result.json
        ),
        3: StageConfig(
            stage=3,
            name="综合能力测试",
            categories=['math', 'code', 'logic', 'commonsense', 'text', 'shell'],
            category_names={
                'math': '数学推理',
                'code': '代码生成',
                'logic': '逻辑推理',
                'commonsense': '常识问答',
                'text': '文本理解',
                'shell': 'Linux Shell'
            },
            results_dir="eval_results/stage3",
            file_pattern="*_stage3.json"
        )
    }

    def __init__(self, base_dir: str = "/mnt/volume3/llama_cpp"):
        self.base_dir = Path(base_dir)
        self.results: Dict[int, List[ModelResult]] = {}

    def load_stage_results(self, stage: int, custom_dir: Optional[str] = None) -> List[ModelResult]:
        """加载指定阶段的测试结果"""
        config = self.STAGE_CONFIGS.get(stage)
        if not config:
            raise ValueError(f"Unknown stage: {stage}")

        results_dir = custom_dir or config.results_dir
        results_path = self.base_dir / results_dir

        if not results_path.exists():
            print(f"Warning: Results directory not found: {results_path}")
            return []

        # 按模型分组，取每个模型最新的结果
        model_results: Dict[str, ModelResult] = {}

        for fname in results_path.glob(config.file_pattern):
            # 排除工具测试结果文件（避免与合并后的主结果文件冲突）
            if '_tool_result' in fname.name:
                continue
            try:
                with open(fname) as f:
                    data = json.load(f)

                model_name = self._extract_model_name(fname.name, config.file_pattern)
                if not model_name:
                    continue

                result = self._parse_result(model_name, stage, data, config)

                # 只保留最新的结果
                if model_name not in model_results:
                    model_results[model_name] = result
                else:
                    if result.timestamp > model_results[model_name].timestamp:
                        model_results[model_name] = result

            except Exception as e:
                print(f"Warning: Failed to load {fname}: {e}")
                continue

        self.results[stage] = list(model_results.values())
        return self.results[stage]

    def _extract_model_name(self, filename: str, pattern: str) -> Optional[str]:
        """从文件名提取模型名称"""
        # 移除后缀和pattern中的通配符部分
        suffix = pattern.replace("*", "").replace(".json", "")
        name = filename.replace(suffix, "").replace("_result", "").replace("_stage", "")

        # 找到时间戳位置 (格式: YYYYMMDD_HHMMSS)
        parts = name.split("_")
        for i, part in enumerate(parts):
            if len(part) == 8 and part.isdigit():
                return "_".join(parts[:i])

        # 如果没有时间戳，移除常见后缀
        for suffix in ['.json', '_result', '_stage1', '_stage2', '_stage3']:
            name = name.replace(suffix, "")
        return name if name else None

    def _parse_result(self, model_name: str, stage: int, data: Dict, config: StageConfig) -> ModelResult:
        """解析测试结果数据"""
        categories = {}

        for cat in config.categories:
            if cat in data:
                categories[cat] = data[cat]
            elif 'categories' in data and cat in data['categories']:
                cat_data = data['categories'][cat]
                # Stage 3格式: 有cases, score, passed_weight, total_weight
                if isinstance(cat_data, dict) and 'cases' in cat_data:
                    # 计算通过数
                    passed = sum(1 for c in cat_data['cases'] if c.get('passed', False))
                    total = len(cat_data['cases'])
                    categories[cat] = {
                        'passed': passed,
                        'total': total,
                        'pass_rate': passed / total if total > 0 else 0.0,
                        'score': cat_data.get('score', 0.0),
                        'weight': cat_data.get('weight', 1.0)
                    }
                else:
                    categories[cat] = cat_data

        # 计算summary
        if 'summary' in data:
            summary = data['summary']
        elif 'overall' in data:
            summary = data['overall']
        else:
            # 从categories计算summary
            total_passed = sum(c.get('passed', 0) for c in categories.values())
            total_tests = sum(c.get('total', 0) for c in categories.values())
            summary = {
                'total_passed': total_passed,
                'total_tests': total_tests,
                'total_pass_rate': total_passed / total_tests if total_tests > 0 else 0.0
            }

        return ModelResult(
            name=model_name,
            stage=stage,
            timestamp=data.get('timestamp', ''),
            test_id=data.get('test_id', data.get('model', '')),
            categories=categories,
            summary=summary,
            metadata={
                'endpoint': data.get('endpoint', ''),
                'filename': data.get('filename', ''),
                'config': data.get('config', '')
            },
            raw_data=data
        )

    def generate_comparison_table(self, stage: int, sort_by: str = 'total') -> str:
        """生成对比表格 (Markdown格式)"""
        if stage not in self.results:
            self.load_stage_results(stage)

        results = self.results.get(stage, [])
        if not results:
            return "No results found."

        config = self.STAGE_CONFIGS[stage]

        # 排序
        if sort_by == 'total':
            results = sorted(results, key=lambda x: x.total_pass_rate, reverse=True)
        else:
            results = sorted(results, key=lambda x: x.get_category_rate(sort_by), reverse=True)

        # 生成表格
        lines = []
        lines.append("| 排名 | 模型名称 | " + " | ".join(config.category_names.values()) + " | 总计 | 评级 |")
        lines.append("|:---:|:---|" + "|".join([":---:"] * len(config.categories)) + "|:---:|:---|")

        for rank, r in enumerate(results, 1):
            row = [f"{rank}", r.name[:40]]

            for cat in config.categories:
                passed, total = r.get_category_score(cat)
                rate = r.get_category_rate(cat) * 100
                row.append(f"{passed}/{total} ({rate:.1f}%)")

            total_rate = r.total_pass_rate * 100
            row.append(f"**{r.total_passed}/{r.total_tests} ({total_rate:.1f}%)**")
            row.append(self._get_grade(r.total_pass_rate))

            lines.append("| " + " | ".join(row) + " |")

        return "\n".join(lines)

    def generate_family_analysis(self, stage: int) -> str:
        """生成模型家族分析"""
        if stage not in self.results:
            self.load_stage_results(stage)

        results = self.results.get(stage, [])
        if not results:
            return "No results found."

        config = self.STAGE_CONFIGS[stage]

        # 按家族分组
        families: Dict[str, List[ModelResult]] = {}
        for r in results:
            family = self._detect_family(r.name)
            if family not in families:
                families[family] = []
            families[family].append(r)

        lines = []
        for family, models in sorted(families.items()):
            lines.append(f"\n### {family} 家族 ({len(models)}模型)")

            # 计算平均值
            avg_rates = {}
            for cat in config.categories:
                rates = [m.get_category_rate(cat) for m in models]
                avg_rates[cat] = sum(rates) / len(rates) * 100 if rates else 0

            avg_total = sum(m.total_pass_rate for m in models) / len(models) * 100

            cat_avgs = " | ".join([f"{config.category_names[cat]} {avg_rates[cat]:.1f}%" for cat in config.categories])
            lines.append(f"- **家族平均**: {cat_avgs} | 总计 {avg_total:.1f}%")
            lines.append("")

            # 排序显示
            for m in sorted(models, key=lambda x: x.total_pass_rate, reverse=True):
                lines.append(f"  • {m.name:<40} 总计 {m.total_pass_rate*100:5.1f}%")

        return "\n".join(lines)

    def generate_csv(self, stage: int) -> str:
        """生成CSV格式数据"""
        if stage not in self.results:
            self.load_stage_results(stage)

        results = self.results.get(stage, [])
        if not results:
            return ""

        config = self.STAGE_CONFIGS[stage]

        lines = []
        headers = ["模型名称"] + [f"{name}通过,{name}总数,{name}率" for name in config.category_names.values()] + ["总计通过", "总计总数", "总通过率"]
        lines.append(",".join(headers))

        for r in sorted(results, key=lambda x: x.total_pass_rate, reverse=True):
            row = [r.name]
            for cat in config.categories:
                passed, total = r.get_category_score(cat)
                rate = r.get_category_rate(cat)
                row.extend([str(passed), str(total), f"{rate:.4f}"])
            row.extend([str(r.total_passed), str(r.total_tests), f"{r.total_pass_rate:.4f}"])
            lines.append(",".join(row))

        return "\n".join(lines)

    def generate_full_report(self, stage: int, output_file: Optional[str] = None) -> str:
        """生成完整报告"""
        if stage not in self.STAGE_CONFIGS:
            return f"Error: Stage {stage} not configured"

        if stage not in self.results:
            self.load_stage_results(stage)

        results = self.results.get(stage, [])
        if not results:
            return "No results found."

        config = self.STAGE_CONFIGS[stage]

        lines = [
            f"# GFX1151 - Stage {stage} {config.name} - 全模型基准报告",
            "",
            f"> **后端**: AMD gfx1151 (Strix Halo) Vulkan",
            f"> **测试时间**: {datetime.now().strftime('%Y-%m-%d')}",
            f"> **测试框架**: {self._get_framework_desc(stage)}",
            f"> **模型数量**: {len(results)}个",
            "",
            "---",
            "",
            "## 📊 综合排名",
            "",
            self.generate_comparison_table(stage),
            "",
            "---",
            "",
            "## 📈 模型家族对比",
            self.generate_family_analysis(stage),
            "",
            "---",
            "",
            "## 📋 原始数据 (CSV)",
            "",
            "```csv",
            self.generate_csv(stage),
            "```",
            "",
            "---",
            "",
            f"*报告生成时间: {datetime.now().strftime('%Y-%m-%d')}*",
        ]

        report = "\n".join(lines)

        if output_file:
            output_path = self.base_dir / output_file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(report)
            print(f"Report saved to: {output_path}")

        return report

    def _detect_family(self, model_name: str) -> str:
        """检测模型家族"""
        families = {
            'Qwen3': ['Qwen3'],
            'Qwen2.5': ['Qwen2.5', 'Qwen2-5'],
            'GLM-4': ['GLM-4', 'GLM4'],
            'GLM-4.7': ['GLM-4.7', 'GLM4.7'],
            'MiniCPM': ['MiniCPM'],
            'Llama': ['Llama', 'LLaMA'],
            'Mistral': ['Mistral'],
            'MiroThinker': ['MiroThinker'],
            'JoyAI': ['JoyAI'],
            'DeepSeek': ['DeepSeek'],
        }

        for family, keywords in families.items():
            for kw in keywords:
                if kw in model_name:
                    return family

        return "Other"

    def _get_grade(self, pass_rate: float) -> str:
        """获取评级"""
        if pass_rate >= 0.8:
            return "⭐⭐⭐⭐⭐ 优秀"
        elif pass_rate >= 0.6:
            return "⭐⭐⭐⭐ 良好"
        elif pass_rate >= 0.4:
            return "⭐⭐⭐ 及格"
        else:
            return "⭐⭐ 需改进"

    def _get_framework_desc(self, stage: int) -> str:
        """获取测试框架描述"""
        descriptions = {
            1: "基础能力 (功能/上下文/性能)",
            2: "50-case (代码9 + 数学11 + 文本10 + 工具20)",
            3: "65-case (数学/代码/逻辑/常识/文本/Linux)"
        }
        return descriptions.get(stage, f"Stage {stage}")


def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(description='Generate evaluation reports')
    parser.add_argument('--stage', '-s', type=int, required=True, help='Stage number (1/2/3)')
    parser.add_argument('--output', '-o', type=str, help='Output file path')
    parser.add_argument('--base-dir', '-b', type=str, default='/mnt/volume3/llama_cpp', help='Base directory')
    parser.add_argument('--format', '-f', type=str, choices=['markdown', 'csv', 'table'], default='markdown', help='Output format')

    args = parser.parse_args()

    generator = ReportGenerator(args.base_dir)

    if args.format == 'csv':
        generator.load_stage_results(args.stage)
        print(generator.generate_csv(args.stage))
    elif args.format == 'table':
        generator.load_stage_results(args.stage)
        print(generator.generate_comparison_table(args.stage))
    else:
        print(generator.generate_full_report(args.stage, args.output))


if __name__ == '__main__':
    main()
