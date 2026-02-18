#!/usr/bin/env python3
"""
指标计算模块

提供标准化的指标计算和统计功能。
"""

from typing import List, Dict, Any
from dataclasses import dataclass
import statistics


@dataclass
class AggregatedMetrics:
    """聚合指标"""
    count: int = 0
    mean: float = 0.0
    median: float = 0.0
    min: float = 0.0
    max: float = 0.0
    std: float = 0.0
    p95: float = 0.0
    p99: float = 0.0


class MetricsCalculator:
    """
    指标计算器

    提供从原始数据计算统计指标的功能。
    """

    @staticmethod
    def calculate_aggregate(values: List[float]) -> AggregatedMetrics:
        """
        计算聚合指标

        Args:
            values: 数值列表

        Returns:
            AggregatedMetrics 包含统计指标
        """
        if not values:
            return AggregatedMetrics()

        sorted_values = sorted(values)
        count = len(sorted_values)

        return AggregatedMetrics(
            count=count,
            mean=statistics.mean(sorted_values),
            median=statistics.median(sorted_values),
            min=min(sorted_values),
            max=max(sorted_values),
            std=statistics.stdev(sorted_values) if count > 1 else 0.0,
            p95=sorted_values[int(count * 0.95)] if count >= 20 else sorted_values[-1],
            p99=sorted_values[int(count * 0.99)] if count >= 100 else sorted_values[-1]
        )

    @classmethod
    def aggregate_by_model(cls, results: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """
        按模型聚合指标

        Args:
            results: 原始结果列表

        Returns:
            按模型分组的聚合指标
        """
        by_model = {}

        for result in results:
            model_id = result.get('model_id', 'unknown')

            if model_id not in by_model:
                by_model[model_id] = {
                    'prompt_tps': [],
                    'generation_tps': [],
                    'total_tps': [],
                    'test_count': 0
                }

            metrics = result.get('metrics', {})
            by_model[model_id]['prompt_tps'].append(metrics.get('prompt_tokens_per_second', 0))
            by_model[model_id]['generation_tps'].append(metrics.get('generation_tokens_per_second', 0))
            by_model[model_id]['total_tps'].append(metrics.get('total_tokens_per_second', 0))
            by_model[model_id]['test_count'] += 1

        # 计算聚合统计
        aggregated = {}
        for model_id, data in by_model.items():
            aggregated[model_id] = {
                'test_count': data['test_count'],
                'prompt_tps': cls.calculate_aggregate(data['prompt_tps']),
                'generation_tps': cls.calculate_aggregate(data['generation_tps']),
                'total_tps': cls.calculate_aggregate(data['total_tps'])
            }

        return aggregated

    @staticmethod
    def format_tps(tps: float) -> str:
        """格式化 tokens/second 显示"""
        if tps >= 1000:
            return f"{tps/1000:.2f}K"
        return f"{tps:.1f}"
